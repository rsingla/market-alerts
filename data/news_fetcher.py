"""
News Fetcher
Aggregates financial news from multiple sources
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
import feedparser
import requests
from config import settings
from utils.logger import logger


class NewsArticle:
    """News article data structure"""
    def __init__(self, title: str, source: str, url: str, published: datetime, summary: str = ""):
        self.title = title
        self.source = source
        self.url = url
        self.published = published
        self.summary = summary

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'title': self.title,
            'source': self.source,
            'url': self.url,
            'published': self.published.isoformat() if self.published else None,
            'summary': self.summary
        }

    def __repr__(self):
        return f"NewsArticle(title='{self.title[:50]}...', source='{self.source}')"


# RSS Feed sources (free, no API key needed)
RSS_FEEDS = {
    'CNBC': 'https://www.cnbc.com/id/100003114/device/rss/rss.html',
    'Reuters Business': 'https://www.reuters.com/business/',
    'MarketWatch': 'https://feeds.marketwatch.com/marketwatch/topstories/',
    'Seeking Alpha': 'https://seekingalpha.com/feed.xml',
    'Yahoo Finance': 'https://finance.yahoo.com/news/rssindex',
}


def get_market_news(max_items: Optional[int] = None) -> List[NewsArticle]:
    """
    Get general market news from multiple sources

    Args:
        max_items: Maximum number of articles (uses settings.MAX_NEWS_ITEMS if None)

    Returns:
        List of NewsArticle objects
    """
    if max_items is None:
        max_items = settings.MAX_NEWS_ITEMS

    articles = []

    # Try News API first (if available)
    if settings.NEWS_API_KEY:
        articles.extend(_get_newsapi_articles())

    # Fallback to RSS feeds
    if len(articles) < max_items:
        articles.extend(_get_rss_articles())

    # Sort by published date (newest first)
    articles.sort(key=lambda x: x.published if x.published else datetime.min, reverse=True)

    # Filter by keywords if configured
    if settings.NEWS_KEYWORDS:
        articles = _filter_by_keywords(articles, settings.NEWS_KEYWORDS)

    return articles[:max_items]


def get_stock_news(symbol: str, max_items: int = 5) -> List[NewsArticle]:
    """
    Get news specific to a stock symbol

    Args:
        symbol: Stock ticker symbol
        max_items: Maximum number of articles

    Returns:
        List of NewsArticle objects
    """
    articles = []

    # Try News API
    if settings.NEWS_API_KEY:
        articles.extend(_get_newsapi_articles(query=symbol))

    # Try Finnhub
    if settings.FINNHUB_API_KEY and len(articles) < max_items:
        articles.extend(_get_finnhub_news(symbol))

    # Sort by published date
    articles.sort(key=lambda x: x.published if x.published else datetime.min, reverse=True)

    return articles[:max_items]


def _get_newsapi_articles(query: Optional[str] = None) -> List[NewsArticle]:
    """Fetch articles from News API"""
    try:
        url = "https://newsapi.org/v2/top-headlines" if not query else "https://newsapi.org/v2/everything"

        params = {
            'apiKey': settings.NEWS_API_KEY,
            'language': 'en',
            'pageSize': 10
        }

        if query:
            params['q'] = query
            params['sortBy'] = 'publishedAt'
        else:
            params['category'] = 'business'
            params['country'] = 'us'

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        articles = []
        for item in data.get('articles', []):
            try:
                published = datetime.fromisoformat(item['publishedAt'].replace('Z', '+00:00'))
            except:
                published = datetime.now()

            article = NewsArticle(
                title=item.get('title', 'No title'),
                source=item.get('source', {}).get('name', 'News API'),
                url=item.get('url', ''),
                published=published,
                summary=item.get('description', '')
            )
            articles.append(article)

        logger.info(f"Fetched {len(articles)} articles from News API")
        return articles

    except Exception as e:
        logger.error(f"Error fetching from News API: {e}")
        return []


def _get_finnhub_news(symbol: str) -> List[NewsArticle]:
    """Fetch news from Finnhub"""
    try:
        # Get news from last 7 days
        from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        to_date = datetime.now().strftime('%Y-%m-%d')

        url = "https://finnhub.io/api/v1/company-news"
        params = {
            'symbol': symbol,
            'from': from_date,
            'to': to_date,
            'token': settings.FINNHUB_API_KEY
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        articles = []
        for item in data:
            published = datetime.fromtimestamp(item['datetime'])

            article = NewsArticle(
                title=item.get('headline', 'No title'),
                source=item.get('source', 'Finnhub'),
                url=item.get('url', ''),
                published=published,
                summary=item.get('summary', '')
            )
            articles.append(article)

        logger.info(f"Fetched {len(articles)} articles from Finnhub for {symbol}")
        return articles

    except Exception as e:
        logger.error(f"Error fetching from Finnhub for {symbol}: {e}")
        return []


def _get_rss_articles() -> List[NewsArticle]:
    """Fetch articles from RSS feeds"""
    articles = []

    for source_name, feed_url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(feed_url)

            for entry in feed.entries[:5]:  # Get 5 from each source
                try:
                    # Parse published date
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        from time import mktime
                        published = datetime.fromtimestamp(mktime(entry.published_parsed))
                    else:
                        published = datetime.now()

                    article = NewsArticle(
                        title=entry.get('title', 'No title'),
                        source=source_name,
                        url=entry.get('link', ''),
                        published=published,
                        summary=entry.get('summary', '')[:200]  # Truncate summary
                    )
                    articles.append(article)

                except Exception as e:
                    logger.debug(f"Error parsing RSS entry from {source_name}: {e}")
                    continue

            logger.debug(f"Fetched articles from {source_name}")

        except Exception as e:
            logger.warning(f"Error fetching RSS feed {source_name}: {e}")
            continue

    logger.info(f"Fetched {len(articles)} articles from RSS feeds")
    return articles


def _filter_by_keywords(articles: List[NewsArticle], keywords: List[str]) -> List[NewsArticle]:
    """Filter articles by keywords"""
    filtered = []

    for article in articles:
        text = f"{article.title} {article.summary}".lower()

        # Check if any keyword appears in title or summary
        if any(keyword.lower() in text for keyword in keywords):
            filtered.append(article)

    logger.info(f"Filtered {len(filtered)}/{len(articles)} articles by keywords")
    return filtered


def get_trending_topics(articles: List[NewsArticle]) -> Dict[str, int]:
    """
    Extract trending topics from articles

    Args:
        articles: List of NewsArticle objects

    Returns:
        Dictionary mapping topic to frequency
    """
    topics = {}

    for article in articles:
        text = f"{article.title} {article.summary}".lower()

        # Count keyword occurrences
        for keyword in settings.NEWS_KEYWORDS:
            if keyword.lower() in text:
                topics[keyword] = topics.get(keyword, 0) + 1

    # Sort by frequency
    return dict(sorted(topics.items(), key=lambda x: x[1], reverse=True))


if __name__ == '__main__':
    # Test news fetching
    print("\n" + "="*60)
    print("NEWS FETCHER TEST")
    print("="*60)

    # Test market news
    print("\nFetching general market news...")
    news = get_market_news(max_items=5)
    print(f"✓ Fetched {len(news)} articles")

    for i, article in enumerate(news[:3], 1):
        print(f"\n{i}. {article.title[:60]}...")
        print(f"   Source: {article.source}")
        print(f"   Published: {article.published.strftime('%Y-%m-%d %H:%M')}")

    # Test stock-specific news
    print("\n" + "-"*60)
    print("Fetching AAPL-specific news...")
    aapl_news = get_stock_news('AAPL', max_items=3)
    print(f"✓ Fetched {len(aapl_news)} articles")

    for i, article in enumerate(aapl_news, 1):
        print(f"\n{i}. {article.title[:60]}...")
        print(f"   Source: {article.source}")

    # Test trending topics
    if news:
        print("\n" + "-"*60)
        print("Trending topics:")
        topics = get_trending_topics(news)
        for topic, count in list(topics.items())[:5]:
            print(f"  {topic}: {count} mentions")

    print("="*60 + "\n")
