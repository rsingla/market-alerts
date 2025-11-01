"""
Alert Formatters
Formats alerts into readable WhatsApp messages
"""

from typing import List
from datetime import datetime
from data.market_data import StockQuote
from data.news_fetcher import NewsArticle
from .filters import AlertType, AlertLevel, get_alert_emoji
from config import settings


def format_alert_message(symbol: str, quote: StockQuote, alert_type: AlertType, alert_level: AlertLevel) -> str:
    """
    Format a single stock alert message

    Args:
        symbol: Stock ticker symbol
        quote: StockQuote object
        alert_type: Type of alert
        alert_level: Severity level

    Returns:
        Formatted message string
    """
    emoji = get_alert_emoji(alert_type, alert_level)

    # Direction indicator
    direction = "📈" if quote.change_percent > 0 else "📉"

    message = f"{emoji} *{symbol}* {direction}\n"
    message += f"\n"
    message += f"Price: ${quote.price:.2f}\n"
    message += f"Change: {quote.change_percent:+.2f}% (${quote.change:+.2f})\n"

    # Add volume info for volume spikes
    if alert_type == AlertType.VOLUME_SPIKE:
        message += f"Volume: {quote.volume:,} ({quote.volume_ratio:.1f}x avg)\n"

    # Add day range
    message += f"Range: ${quote.day_low:.2f} - ${quote.day_high:.2f}\n"

    # Add timestamp
    message += f"\n_Updated: {quote.timestamp.strftime('%I:%M %p ET')}_"

    return message


def format_market_summary(quotes: dict[str, StockQuote]) -> str:
    """
    Format a market summary message

    Args:
        quotes: Dictionary mapping symbol to StockQuote

    Returns:
        Formatted summary message
    """
    if not quotes:
        return "📊 *Market Summary*\n\nNo data available"

    # Separate stocks and indices
    indices = {k: v for k, v in quotes.items() if k in settings.INDICES}
    stocks = {k: v for k, v in quotes.items() if k in settings.STOCKS}

    message = "📊 *Market Summary*\n"
    message += f"_{datetime.now().strftime('%B %d, %Y at %I:%M %p ET')}_\n\n"

    # Format indices
    if indices:
        message += "*Indices:*\n"
        for symbol in sorted(indices.keys()):
            quote = indices[symbol]
            direction = "📈" if quote.change_percent > 0 else "📉"
            message += f"{direction} {symbol}: ${quote.price:.2f} ({quote.change_percent:+.2f}%)\n"
        message += "\n"

    # Format stocks (show top movers)
    if stocks:
        # Sort by absolute change percentage
        sorted_stocks = sorted(stocks.items(), key=lambda x: abs(x[1].change_percent), reverse=True)

        message += "*Top Movers:*\n"
        for symbol, quote in sorted_stocks[:10]:  # Top 10 movers
            direction = "📈" if quote.change_percent > 0 else "📉"
            message += f"{direction} {symbol}: ${quote.price:.2f} ({quote.change_percent:+.2f}%)\n"

        # Add summary stats
        if len(stocks) > 10:
            message += f"\n_... and {len(stocks) - 10} more stocks_\n"

    return message


def format_news_alert(articles: List[NewsArticle]) -> str:
    """
    Format news articles into an alert message

    Args:
        articles: List of NewsArticle objects

    Returns:
        Formatted news message
    """
    if not articles:
        return "📰 *Market News*\n\nNo news available"

    message = "📰 *Market News*\n\n"

    for i, article in enumerate(articles[:settings.MAX_NEWS_ITEMS], 1):
        message += f"*{i}. {article.title}*\n"
        message += f"_{article.source}_\n"

        if article.summary:
            # Truncate summary to 150 characters
            summary = article.summary[:150]
            if len(article.summary) > 150:
                summary += "..."
            message += f"{summary}\n"

        message += f"{article.url}\n\n"

    return message


def format_combined_alert(quotes: dict[str, StockQuote],
                         alerts: dict[str, tuple[AlertType, AlertLevel]],
                         news: List[NewsArticle] = None) -> str:
    """
    Format a combined alert with multiple stocks and news

    Args:
        quotes: Dictionary mapping symbol to StockQuote
        alerts: Dictionary mapping symbol to (AlertType, AlertLevel)
        news: Optional list of NewsArticle objects

    Returns:
        Formatted combined message
    """
    message = "🔔 *Market Alerts*\n"
    message += f"_{datetime.now().strftime('%B %d, %Y at %I:%M %p ET')}_\n\n"

    # Add stock alerts
    if alerts:
        message += f"*{len(alerts)} Alert{'s' if len(alerts) > 1 else ''}:*\n\n"

        for symbol, (alert_type, alert_level) in alerts.items():
            quote = quotes.get(symbol)
            if quote:
                emoji = get_alert_emoji(alert_type, alert_level)
                direction = "📈" if quote.change_percent > 0 else "📉"
                message += f"{emoji} {direction} *{symbol}*: ${quote.price:.2f} ({quote.change_percent:+.2f}%)\n"

                if alert_type == AlertType.VOLUME_SPIKE:
                    message += f"   Volume: {quote.volume_ratio:.1f}x average\n"

        message += "\n"

    # Add news if provided
    if news:
        message += f"*Breaking News ({len(news)}):*\n\n"
        for i, article in enumerate(news[:3], 1):
            message += f"{i}. {article.title}\n"
            message += f"   _{article.source}_\n\n"

    return message


def format_error_message(error: str) -> str:
    """
    Format an error message

    Args:
        error: Error description

    Returns:
        Formatted error message
    """
    message = "❌ *Alert Error*\n\n"
    message += f"An error occurred while processing market alerts:\n\n"
    message += f"_{error}_\n\n"
    message += f"Please check the logs for more details."

    return message


def format_status_message(status: dict) -> str:
    """
    Format a market status message

    Args:
        status: Market status dictionary from market_hours.get_market_status()

    Returns:
        Formatted status message
    """
    message = "⏰ *Market Status*\n\n"
    message += f"Current Time: {status['current_time']}\n"
    message += f"Trading Day: {'Yes ✓' if status['is_trading_day'] else 'No ✗'}\n"
    message += f"Market Hours: {'Yes ✓' if status['is_market_hours'] else 'No ✗'}\n"

    if status.get('is_weekend'):
        message += f"\n🏖️ _Markets closed for the weekend_"
    elif status.get('is_holiday'):
        message += f"\n🎉 _Markets closed for holiday_"
    elif status.get('time_to_open'):
        message += f"\n⏳ Market opens in: {status['time_to_open']}"
    elif status.get('time_to_close'):
        message += f"\n⏳ Market closes in: {status['time_to_close']}"

    return message


if __name__ == '__main__':
    # Test formatters
    from data.market_data import StockQuote

    print("\n" + "="*60)
    print("ALERT FORMATTERS TEST")
    print("="*60)

    # Create test quote
    test_quote = StockQuote('AAPL', {
        'regularMarketPrice': 175.50,
        'regularMarketChange': 8.75,
        'regularMarketChangePercent': 5.25,
        'regularMarketVolume': 150000000,
        'averageDailyVolume10Day': 50000000,
        'regularMarketDayHigh': 176.00,
        'regularMarketDayLow': 170.00,
        'regularMarketPreviousClose': 166.75,
    })

    # Test single alert
    print("\nSingle Alert:")
    print("-" * 60)
    msg = format_alert_message('AAPL', test_quote, AlertType.LARGE_MOVE, AlertLevel.CRITICAL)
    print(msg)

    # Test market summary
    print("\n\nMarket Summary:")
    print("-" * 60)
    quotes = {
        'SPY': test_quote,
        'AAPL': test_quote
    }
    msg = format_market_summary(quotes)
    print(msg)

    print("="*60 + "\n")
