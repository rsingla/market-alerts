"""
Alpaca Trading Integration
Fetches data from Alpaca and runs AI Trading Analysis with 12-hour caching
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Optional
import json
from pathlib import Path
from utils.logger import logger
from utils.cache import get_cache
from config import settings
from ai.trading_analysis_engine import get_trading_engine


class AlpacaTradingIntegration:
    """
    Integration layer between Alpaca data source and AI Trading Analysis Engine
    Includes 12-hour caching with end-of-day expiration
    """

    def __init__(self):
        """Initialize Alpaca trading integration"""
        self.engine = get_trading_engine()
        self.cache = get_cache()
        self.cache_ttl_hours = 12
        logger.info("Alpaca Trading Integration initialized")

    def get_ai_evaluation(self, ticker: str, timeframe: str = "1D", force_refresh: bool = False) -> Dict:
        """
        Get AI evaluation for a ticker with intelligent caching

        Args:
            ticker: Stock ticker symbol
            timeframe: Data timeframe (1D, 1H, 15m, etc.)
            force_refresh: Force fresh analysis bypassing cache

        Returns:
            Dictionary with complete AI analysis
        """
        try:
            # Check cache first (unless force refresh)
            if not force_refresh:
                cached_analysis = self._get_cached_analysis(ticker, timeframe)
                if cached_analysis:
                    logger.info(f"Using cached AI analysis for {ticker} ({timeframe})")
                    return cached_analysis

            # Fetch fresh data from Alpaca
            logger.info(f"Fetching fresh data from Alpaca for {ticker} ({timeframe})")
            df = self._fetch_alpaca_data(ticker, timeframe)

            if df is None or df.empty:
                logger.warning(f"No data available for {ticker}")
                return self._get_empty_analysis(ticker, timeframe, "No data available from Alpaca")

            # Run AI analysis
            logger.info(f"Running AI analysis for {ticker}")
            analysis = self.engine.analyze(ticker, df, timeframe)

            # Cache the result
            self._cache_analysis(ticker, timeframe, analysis)

            return analysis

        except Exception as e:
            logger.error(f"Error getting AI evaluation for {ticker}: {e}", exc_info=True)
            return self._get_empty_analysis(ticker, timeframe, f"Error: {str(e)}")

    def _fetch_alpaca_data(self, ticker: str, timeframe: str = "1D") -> Optional[pd.DataFrame]:
        """
        Fetch historical data from Alpaca

        Args:
            ticker: Stock ticker symbol
            timeframe: Bar timeframe

        Returns:
            DataFrame with OHLCV data or None
        """
        try:
            # Check if Alpaca is configured
            if not hasattr(settings, 'ALPACA_API_KEY') or not settings.ALPACA_API_KEY:
                logger.warning("Alpaca API not configured")
                return None

            from alpaca.data.historical import StockHistoricalDataClient
            from alpaca.data.requests import StockBarsRequest
            from alpaca.data.timeframe import TimeFrame, TimeFrameUnit

            # Initialize client
            client = StockHistoricalDataClient(
                api_key=settings.ALPACA_API_KEY,
                secret_key=settings.ALPACA_SECRET_KEY
            )

            # Map timeframe string to Alpaca TimeFrame
            timeframe_map = {
                "1m": TimeFrame(1, TimeFrameUnit.Minute),
                "5m": TimeFrame(5, TimeFrameUnit.Minute),
                "15m": TimeFrame(15, TimeFrameUnit.Minute),
                "1H": TimeFrame(1, TimeFrameUnit.Hour),
                "1D": TimeFrame(1, TimeFrameUnit.Day),
                "30D": TimeFrame(1, TimeFrameUnit.Day),
                "200D": TimeFrame(1, TimeFrameUnit.Day),
                "365D": TimeFrame(1, TimeFrameUnit.Day),
            }

            alpaca_timeframe = timeframe_map.get(timeframe, TimeFrame(1, TimeFrameUnit.Day))

            # Calculate date range (need at least 200 bars for full analysis)
            end_date = datetime.now()

            if timeframe == "365D":
                start_date = end_date - timedelta(days=365)  # 1 year
            elif timeframe == "200D":
                start_date = end_date - timedelta(days=200)  # 200 days
            elif timeframe == "30D":
                start_date = end_date - timedelta(days=30)  # 30 days
            elif timeframe == "1D":
                start_date = end_date - timedelta(days=400)  # ~200 trading days
            elif timeframe == "1H":
                start_date = end_date - timedelta(days=60)  # ~200 hours of trading
            elif timeframe == "15m":
                start_date = end_date - timedelta(days=15)  # ~200 15-min bars
            else:
                start_date = end_date - timedelta(days=200)

            # Create request
            request = StockBarsRequest(
                symbol_or_symbols=ticker,
                timeframe=alpaca_timeframe,
                start=start_date,
                end=end_date
            )

            # Fetch data
            bars = client.get_stock_bars(request)

            if not bars or ticker not in bars.df.index.get_level_values('symbol').unique():
                logger.warning(f"No bars returned for {ticker}")
                return None

            # Convert to DataFrame
            df = bars.df

            # If multi-index, select the ticker
            if isinstance(df.index, pd.MultiIndex):
                df = df.xs(ticker, level='symbol')

            # Rename columns to match expected format
            df = df.rename(columns={
                'open': 'Open',
                'high': 'High',
                'low': 'Low',
                'close': 'Close',
                'volume': 'Volume'
            })

            # Ensure we have required columns
            required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
            if not all(col in df.columns for col in required_cols):
                logger.error(f"Missing required columns in Alpaca data for {ticker}")
                return None

            logger.debug(f"Fetched {len(df)} bars for {ticker}")
            return df

        except Exception as e:
            logger.error(f"Error fetching Alpaca data for {ticker}: {e}", exc_info=True)
            return None

    def _get_cached_analysis(self, ticker: str, timeframe: str) -> Optional[Dict]:
        """Get cached analysis if valid"""
        try:
            # Check if cache has expired (12 hours or end of trading day)
            cache_key = f"ai_eval_{ticker}_{timeframe}"
            cached_data = self.cache.get('ai_evaluation', ticker, timeframe=timeframe)

            if cached_data:
                # Check if still valid
                cached_time = datetime.fromisoformat(cached_data['analysis_timestamp_utc'].rstrip('Z'))
                now = datetime.utcnow()

                # Check if cache is older than 12 hours
                if (now - cached_time).total_seconds() > (self.cache_ttl_hours * 3600):
                    logger.debug(f"Cache expired for {ticker} (>12 hours old)")
                    return None

                # Check if we've passed end of trading day (4 PM ET = 9 PM UTC)
                if now.hour >= 21 and cached_time.hour < 21:
                    logger.debug(f"Cache expired for {ticker} (trading day ended)")
                    return None

                return cached_data

            return None

        except Exception as e:
            logger.warning(f"Error reading cache for {ticker}: {e}")
            return None

    def _cache_analysis(self, ticker: str, timeframe: str, analysis: Dict):
        """Cache analysis result with 12-hour TTL"""
        try:
            self.cache.set(
                'ai_evaluation',
                ticker,
                analysis,
                timeframe=timeframe
            )
            logger.debug(f"Cached AI evaluation for {ticker} ({timeframe})")
        except Exception as e:
            logger.warning(f"Error caching analysis for {ticker}: {e}")

    def _get_empty_analysis(self, ticker: str, timeframe: str, reason: str) -> Dict:
        """Return empty analysis when data is unavailable"""
        return {
            "analysis_timestamp_utc": datetime.utcnow().isoformat() + "Z",
            "data_source": "alpaca_data_cache",
            "asset_analyzed": ticker,
            "data_timeframe": timeframe,
            "overall_sentiment": "Unknown",
            "key_levels": {"support": [], "resistance": []},
            "analysis_summary": f"Analysis unavailable: {reason}",
            "indicator_details": {},
            "error": reason
        }

    def export_to_json(self, analysis: Dict, filepath: Optional[str] = None) -> str:
        """
        Export analysis to JSON file

        Args:
            analysis: Analysis dictionary
            filepath: Optional file path (auto-generated if None)

        Returns:
            Path to saved JSON file
        """
        try:
            if filepath is None:
                ticker = analysis['asset_analyzed']
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filepath = f"ai_analysis_{ticker}_{timestamp}.json"

            with open(filepath, 'w') as f:
                json.dump(analysis, f, indent=2)

            logger.info(f"Exported analysis to {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Error exporting analysis: {e}")
            return ""


# Global integration instance
_integration = None


def get_alpaca_integration() -> AlpacaTradingIntegration:
    """Get global Alpaca trading integration instance"""
    global _integration
    if _integration is None:
        _integration = AlpacaTradingIntegration()
    return _integration


if __name__ == '__main__':
    # Test Alpaca integration
    print("\n" + "="*60)
    print("ALPACA TRADING INTEGRATION TEST")
    print("="*60)

    integration = AlpacaTradingIntegration()
    print("\n✓ Integration initialized")

    ticker = "AAPL"
    timeframe = "1D"

    print(f"\nFetching AI evaluation for {ticker} ({timeframe})...")
    analysis = integration.get_ai_evaluation(ticker, timeframe)

    if "error" not in analysis:
        print(f"\n✓ Analysis complete!")
        print(f"\n📊 Results:")
        print(f"   Sentiment: {analysis['overall_sentiment']}")
        print(f"   Data Points: {analysis.get('data_points_analyzed', 0)}")
        print(f"   Summary: {analysis['analysis_summary'][:100]}...")

        print(f"\n💾 Exporting to JSON...")
        json_file = integration.export_to_json(analysis)
        if json_file:
            print(f"   Saved to: {json_file}")
    else:
        print(f"\n✗ Analysis failed: {analysis['error']}")

    print("\n" + "="*60 + "\n")
