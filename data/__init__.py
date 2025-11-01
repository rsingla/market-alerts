"""
Data Layer
Handles market data and news fetching
"""

from .market_data import get_stock_quote, get_market_summary, StockQuote
from .news_fetcher import get_market_news, get_stock_news, NewsArticle
from .cache import cached, get_cache, clear_cache

__all__ = [
    'get_stock_quote',
    'get_market_summary',
    'get_market_news',
    'get_stock_news',
    'StockQuote',
    'NewsArticle',
    'cached',
    'get_cache',
    'clear_cache'
]
