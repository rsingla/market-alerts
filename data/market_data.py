"""
Market Data Fetcher
Fetches stock prices and market data from multiple sources
"""

from typing import Dict, Optional, List
import yfinance as yf
from datetime import datetime, timedelta
from config import settings
from utils.logger import logger


class StockQuote:
    """Stock quote data structure"""
    def __init__(self, symbol: str, data: dict):
        self.symbol = symbol
        self.price = data.get('regularMarketPrice', 0)
        self.change = data.get('regularMarketChange', 0)
        self.change_percent = data.get('regularMarketChangePercent', 0)
        self.volume = data.get('regularMarketVolume', 0)
        self.avg_volume = data.get('averageDailyVolume10Day', 0)
        self.day_high = data.get('regularMarketDayHigh', 0)
        self.day_low = data.get('regularMarketDayLow', 0)
        self.prev_close = data.get('regularMarketPreviousClose', 0)
        self.market_cap = data.get('marketCap', 0)
        self.timestamp = datetime.now()

    @property
    def volume_ratio(self) -> float:
        """Volume compared to average"""
        if self.avg_volume and self.avg_volume > 0:
            return self.volume / self.avg_volume
        return 0

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'symbol': self.symbol,
            'price': self.price,
            'change': self.change,
            'change_percent': self.change_percent,
            'volume': self.volume,
            'avg_volume': self.avg_volume,
            'volume_ratio': self.volume_ratio,
            'day_high': self.day_high,
            'day_low': self.day_low,
            'prev_close': self.prev_close,
            'market_cap': self.market_cap,
            'timestamp': self.timestamp.isoformat()
        }


def get_stock_quote(symbol: str) -> Optional[StockQuote]:
    """
    Get current stock quote with intelligent fallback

    Args:
        symbol: Stock ticker symbol

    Returns:
        StockQuote object or None if failed
    """
    try:
        # Try yfinance first if enabled
        if settings.USE_YFINANCE:
            quote = _get_yfinance_quote(symbol)
            if quote:
                return quote
            # If yfinance fails, try Alpha Vantage as fallback
            elif hasattr(settings, 'ALPHA_VANTAGE_API_KEY') and settings.ALPHA_VANTAGE_API_KEY and settings.ALPHA_VANTAGE_API_KEY != 'your_alpha_vantage_key':
                logger.info(f"yfinance failed for {symbol}, trying Alpha Vantage fallback...")
                return _get_alpha_vantage_quote(symbol)

        # If yfinance not enabled, try Alpha Vantage
        elif hasattr(settings, 'ALPHA_VANTAGE_API_KEY') and settings.ALPHA_VANTAGE_API_KEY and settings.ALPHA_VANTAGE_API_KEY != 'your_alpha_vantage_key':
            return _get_alpha_vantage_quote(symbol)
        else:
            logger.error("No data source configured")
            return None
    except Exception as e:
        logger.error(f"Error fetching quote for {symbol}: {e}")
        return None


def _get_yfinance_quote(symbol: str) -> Optional[StockQuote]:
    """Fetch quote using yfinance"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        # Get current price data
        if not info:
            logger.warning(f"No data returned for {symbol}")
            return None

        return StockQuote(symbol, info)

    except Exception as e:
        logger.error(f"yfinance error for {symbol}: {e}")
        return None


def _get_alpha_vantage_quote(symbol: str) -> Optional[StockQuote]:
    """Fetch quote using Alpha Vantage"""
    try:
        from alpha_vantage.timeseries import TimeSeries

        ts = TimeSeries(key=settings.ALPHA_VANTAGE_API_KEY, output_format='json')
        data, meta = ts.get_quote_endpoint(symbol=symbol)

        # Convert Alpha Vantage format to our format
        quote_data = {
            'regularMarketPrice': float(data['05. price']),
            'regularMarketChange': float(data['09. change']),
            'regularMarketChangePercent': float(data['10. change percent'].rstrip('%')),
            'regularMarketVolume': int(data['06. volume']),
            'regularMarketDayHigh': float(data['03. high']),
            'regularMarketDayLow': float(data['04. low']),
            'regularMarketPreviousClose': float(data['08. previous close']),
        }

        return StockQuote(symbol, quote_data)

    except Exception as e:
        logger.error(f"Alpha Vantage error for {symbol}: {e}")
        return None


def get_market_summary(symbols: Optional[List[str]] = None) -> Dict[str, StockQuote]:
    """
    Get quotes for multiple symbols

    Args:
        symbols: List of ticker symbols (uses WATCHLIST if None)

    Returns:
        Dictionary mapping symbol to StockQuote
    """
    if symbols is None:
        symbols = settings.WATCHLIST

    logger.info(f"Fetching quotes for {len(symbols)} symbols")

    quotes = {}
    for symbol in symbols:
        quote = get_stock_quote(symbol)
        if quote:
            quotes[symbol] = quote
        else:
            logger.warning(f"Failed to fetch {symbol}")

    logger.info(f"Successfully fetched {len(quotes)}/{len(symbols)} quotes")
    return quotes


def get_historical_data(symbol: str, period: str = "1mo") -> Optional[dict]:
    """
    Get historical price data

    Args:
        symbol: Stock ticker symbol
        period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)

    Returns:
        Dictionary with OHLCV data or None
    """
    try:
        if not settings.USE_YFINANCE:
            logger.warning("Historical data only available with yfinance")
            return None

        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)

        if hist.empty:
            logger.warning(f"No historical data for {symbol}")
            return None

        return {
            'dates': hist.index.tolist(),
            'open': hist['Open'].tolist(),
            'high': hist['High'].tolist(),
            'low': hist['Low'].tolist(),
            'close': hist['Close'].tolist(),
            'volume': hist['Volume'].tolist()
        }

    except Exception as e:
        logger.error(f"Error fetching historical data for {symbol}: {e}")
        return None


def calculate_price_stats(symbol: str, days: int = 30) -> Optional[dict]:
    """
    Calculate price statistics over period

    Args:
        symbol: Stock ticker symbol
        days: Number of days to analyze

    Returns:
        Dictionary with statistics or None
    """
    try:
        if not settings.USE_YFINANCE:
            return None

        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=f"{days}d")

        if hist.empty:
            return None

        closes = hist['Close']
        volumes = hist['Volume']

        return {
            'avg_price': float(closes.mean()),
            'max_price': float(closes.max()),
            'min_price': float(closes.min()),
            'volatility': float(closes.std()),
            'avg_volume': float(volumes.mean()),
            'total_change_percent': float(((closes.iloc[-1] - closes.iloc[0]) / closes.iloc[0]) * 100),
            'days_analyzed': len(closes)
        }

    except Exception as e:
        logger.error(f"Error calculating stats for {symbol}: {e}")
        return None


if __name__ == '__main__':
    # Test market data
    print("\n" + "="*60)
    print("MARKET DATA TEST")
    print("="*60)

    # Test single quote
    print("\nFetching AAPL quote...")
    quote = get_stock_quote('AAPL')
    if quote:
        print(f"✓ {quote.symbol}: ${quote.price:.2f} ({quote.change_percent:+.2f}%)")
        print(f"  Volume: {quote.volume:,} (Ratio: {quote.volume_ratio:.2f}x)")

    # Test market summary
    print(f"\nFetching market summary for {len(settings.WATCHLIST)} symbols...")
    quotes = get_market_summary()
    print(f"✓ Fetched {len(quotes)} quotes")

    for symbol, quote in list(quotes.items())[:3]:
        print(f"  {symbol}: ${quote.price:.2f} ({quote.change_percent:+.2f}%)")

    # Test historical data
    print("\nFetching 1-month historical data for SPY...")
    hist = get_historical_data('SPY', '1mo')
    if hist:
        print(f"✓ Retrieved {len(hist['dates'])} days of data")

    print("="*60 + "\n")
