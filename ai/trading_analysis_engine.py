"""
AI Trading Analysis Engine
Comprehensive technical analysis with 11 key indicators
Outputs structured JSON for caching and UI display
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
from utils.logger import logger
from data.technical_indicators import TechnicalIndicators


class TradingAnalysisEngine:
    """
    Advanced technical analysis engine that calculates 11 key indicators
    and produces structured JSON output for AI evaluation
    """

    def __init__(self):
        """Initialize the trading analysis engine"""
        self.indicators_calculator = TechnicalIndicators()
        logger.info("Trading Analysis Engine initialized")

    def analyze(self, ticker: str, df: pd.DataFrame, timeframe: str = "1D") -> Dict:
        """
        Perform comprehensive technical analysis on OHLCV data

        Args:
            ticker: Stock ticker symbol
            df: DataFrame with OHLCV data (columns: Open, High, Low, Close, Volume)
            timeframe: Timeframe of the data (e.g., "1D", "1H", "15m")

        Returns:
            Dictionary with complete analysis in JSON-serializable format
        """
        try:
            if df.empty or len(df) < 200:
                logger.warning(f"Insufficient data for {ticker}: {len(df)} bars")
                return self._get_empty_analysis(ticker, timeframe, "Insufficient data")

            # Calculate all indicators
            analysis = {
                "analysis_timestamp_utc": datetime.utcnow().isoformat() + "Z",
                "data_source": "alpaca_data_cache",
                "asset_analyzed": ticker,
                "data_timeframe": timeframe,
                "data_points_analyzed": len(df),
                "overall_sentiment": "Neutral",
                "key_levels": {
                    "support": [],
                    "resistance": []
                },
                "analysis_summary": "",
                "indicator_details": {}
            }

            # Get current price
            current_price = float(df['Close'].iloc[-1])

            # Calculate each indicator
            analysis["indicator_details"]["sma"] = self._calculate_sma(df, current_price)
            analysis["indicator_details"]["ema"] = self._calculate_ema(df, current_price)
            analysis["indicator_details"]["macd"] = self._calculate_macd_indicator(df)
            analysis["indicator_details"]["rsi"] = self._calculate_rsi_indicator(df)
            analysis["indicator_details"]["bollinger_bands"] = self._calculate_bollinger(df, current_price)
            analysis["indicator_details"]["stochastic"] = self._calculate_stochastic_indicator(df)
            analysis["indicator_details"]["obv"] = self._calculate_obv_indicator(df)
            analysis["indicator_details"]["adx"] = self._calculate_adx_indicator(df)
            analysis["indicator_details"]["ichimoku"] = self._calculate_ichimoku(df, current_price)
            analysis["indicator_details"]["vwap"] = self._calculate_vwap(df, current_price)
            analysis["indicator_details"]["fibonacci"] = self._calculate_fibonacci(df, current_price)

            # Determine support/resistance levels
            analysis["key_levels"] = self._find_key_levels(df, analysis["indicator_details"])

            # Calculate overall sentiment
            analysis["overall_sentiment"] = self._calculate_overall_sentiment(analysis["indicator_details"])

            # Generate analysis summary
            analysis["analysis_summary"] = self._generate_summary(
                ticker,
                current_price,
                analysis["indicator_details"],
                analysis["overall_sentiment"]
            )

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing {ticker}: {e}", exc_info=True)
            return self._get_empty_analysis(ticker, timeframe, f"Analysis error: {str(e)}")

    def _calculate_sma(self, df: pd.DataFrame, current_price: float) -> Dict:
        """Calculate Simple Moving Average analysis"""
        sma_50 = self.indicators_calculator.calculate_sma(df['Close'], 50).iloc[-1]
        sma_200 = self.indicators_calculator.calculate_sma(df['Close'], 200).iloc[-1]

        # Determine signal
        if current_price > sma_50 > sma_200:
            signal = "Bullish"
        elif current_price < sma_50 < sma_200:
            signal = "Bearish"
        else:
            # Check for crossovers
            sma_50_prev = self.indicators_calculator.calculate_sma(df['Close'], 50).iloc[-5]
            sma_200_prev = self.indicators_calculator.calculate_sma(df['Close'], 200).iloc[-5]

            if sma_50_prev < sma_200_prev and sma_50 > sma_200:
                signal = "Potential Golden Cross"
            elif sma_50_prev > sma_200_prev and sma_50 < sma_200:
                signal = "Potential Death Cross"
            else:
                signal = "Neutral"

        return {
            "sma_50": round(float(sma_50), 2),
            "sma_200": round(float(sma_200), 2),
            "current_price": round(current_price, 2),
            "signal": signal
        }

    def _calculate_ema(self, df: pd.DataFrame, current_price: float) -> Dict:
        """Calculate Exponential Moving Average analysis"""
        ema_12 = self.indicators_calculator.calculate_ema(df['Close'], 12).iloc[-1]
        ema_26 = self.indicators_calculator.calculate_ema(df['Close'], 26).iloc[-1]

        signal = "Bullish" if ema_12 > ema_26 else "Bearish" if ema_12 < ema_26 else "Neutral"

        return {
            "ema_12": round(float(ema_12), 2),
            "ema_26": round(float(ema_26), 2),
            "signal": signal
        }

    def _calculate_macd_indicator(self, df: pd.DataFrame) -> Dict:
        """Calculate MACD analysis"""
        macd_data = self.indicators_calculator.calculate_macd(df['Close'])

        macd_line = macd_data['macd'].iloc[-1]
        signal_line = macd_data['signal'].iloc[-1]
        histogram = macd_data['histogram'].iloc[-1]

        # Determine signal
        if macd_line > signal_line:
            if macd_data['macd'].iloc[-2] <= macd_data['signal'].iloc[-2]:
                signal = "Bullish Crossover"
            else:
                signal = "Bullish"
        elif macd_line < signal_line:
            if macd_data['macd'].iloc[-2] >= macd_data['signal'].iloc[-2]:
                signal = "Bearish Crossover"
            else:
                signal = "Bearish"
        else:
            signal = "Neutral"

        return {
            "macd_line": round(float(macd_line), 4),
            "signal_line": round(float(signal_line), 4),
            "histogram": round(float(histogram), 4),
            "signal": signal
        }

    def _calculate_rsi_indicator(self, df: pd.DataFrame) -> Dict:
        """Calculate RSI analysis"""
        rsi = self.indicators_calculator.calculate_rsi(df['Close']).iloc[-1]

        if rsi > 70:
            signal = "Overbought"
        elif rsi < 30:
            signal = "Oversold"
        else:
            signal = "Neutral"

        return {
            "value": round(float(rsi), 2),
            "signal": signal
        }

    def _calculate_bollinger(self, df: pd.DataFrame, current_price: float) -> Dict:
        """Calculate Bollinger Bands analysis"""
        bb = self.indicators_calculator.calculate_bollinger_bands(df['Close'])

        upper = bb['upper'].iloc[-1]
        middle = bb['middle'].iloc[-1]
        lower = bb['lower'].iloc[-1]
        bandwidth = bb['bandwidth'].iloc[-1]

        # Determine signal
        if current_price > upper:
            signal = "Price broke Upper"
        elif current_price < lower:
            signal = "Price broke Lower"
        elif bandwidth < 0.05:  # Narrow bands
            signal = "Squeeze"
        else:
            signal = "Neutral"

        return {
            "upper_band": round(float(upper), 2),
            "middle_band": round(float(middle), 2),
            "lower_band": round(float(lower), 2),
            "bandwidth": round(float(bandwidth), 4),
            "signal": signal
        }

    def _calculate_stochastic_indicator(self, df: pd.DataFrame) -> Dict:
        """Calculate Stochastic Oscillator analysis"""
        stoch = self.indicators_calculator.calculate_stochastic(
            df['High'], df['Low'], df['Close']
        )

        k = stoch['k'].iloc[-1]
        d = stoch['d'].iloc[-1]

        if k > 80 or d > 80:
            signal = "Overbought"
        elif k < 20 or d < 20:
            signal = "Oversold"
        else:
            signal = "Neutral"

        return {
            "percent_k": round(float(k), 2),
            "percent_d": round(float(d), 2),
            "signal": signal
        }

    def _calculate_obv_indicator(self, df: pd.DataFrame) -> Dict:
        """Calculate On-Balance Volume analysis"""
        obv = self.indicators_calculator.calculate_obv(df['Close'], df['Volume'])

        # Calculate OBV trend
        obv_sma = obv.rolling(window=20).mean()
        current_obv = obv.iloc[-1]
        current_sma = obv_sma.iloc[-1]

        # Check for divergence with price
        price_trend = (df['Close'].iloc[-1] - df['Close'].iloc[-20]) / df['Close'].iloc[-20]
        obv_trend = (current_obv - obv.iloc[-20]) / abs(obv.iloc[-20])

        if obv_trend > 0 and price_trend > 0:
            trend = "Rising"
        elif obv_trend < 0 and price_trend < 0:
            trend = "Falling"
        elif (obv_trend > 0 and price_trend < 0) or (obv_trend < 0 and price_trend > 0):
            trend = "Divergence"
        else:
            trend = "Neutral"

        return {
            "current_value": int(current_obv),
            "trend": trend
        }

    def _calculate_adx_indicator(self, df: pd.DataFrame) -> Dict:
        """Calculate Average Directional Index"""
        # Calculate ADX using ATR and directional movement
        tr = self.indicators_calculator.calculate_atr(df['High'], df['Low'], df['Close'])

        # Simplified ADX calculation
        high_diff = df['High'].diff()
        low_diff = -df['Low'].diff()

        pos_dm = high_diff.where((high_diff > low_diff) & (high_diff > 0), 0)
        neg_dm = low_diff.where((low_diff > high_diff) & (low_diff > 0), 0)

        atr_14 = tr.rolling(window=14).mean()
        pos_di = 100 * (pos_dm.rolling(window=14).mean() / atr_14)
        neg_di = 100 * (neg_dm.rolling(window=14).mean() / atr_14)

        dx = 100 * abs(pos_di - neg_di) / (pos_di + neg_di)
        adx = dx.rolling(window=14).mean().iloc[-1]

        if adx > 25:
            signal = "Strong Trend"
        elif adx < 20:
            signal = "Weak Trend"
        else:
            signal = "No Trend"

        return {
            "value": round(float(adx), 2) if not np.isnan(adx) else 0,
            "signal": signal
        }

    def _calculate_ichimoku(self, df: pd.DataFrame, current_price: float) -> Dict:
        """Calculate Ichimoku Cloud analysis"""
        # Tenkan-sen (Conversion Line): (9-period high + 9-period low)/2
        period9_high = df['High'].rolling(window=9).max()
        period9_low = df['Low'].rolling(window=9).min()
        tenkan_sen = (period9_high + period9_low) / 2

        # Kijun-sen (Base Line): (26-period high + 26-period low)/2
        period26_high = df['High'].rolling(window=26).max()
        period26_low = df['Low'].rolling(window=26).min()
        kijun_sen = (period26_high + period26_low) / 2

        # Senkou Span A (Leading Span A): (Tenkan-sen + Kijun-sen)/2
        senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(26)

        # Senkou Span B (Leading Span B): (52-period high + 52-period low)/2
        period52_high = df['High'].rolling(window=52).max()
        period52_low = df['Low'].rolling(window=52).min()
        senkou_span_b = ((period52_high + period52_low) / 2).shift(26)

        # Get current values
        tenkan = tenkan_sen.iloc[-1]
        kijun = kijun_sen.iloc[-1]
        span_a = senkou_span_a.iloc[-1]
        span_b = senkou_span_b.iloc[-1]

        # Determine signal
        cloud_top = max(span_a, span_b)
        cloud_bottom = min(span_a, span_b)

        if current_price > cloud_top and span_a > span_b:
            signal = "Bullish"
        elif current_price < cloud_bottom and span_a < span_b:
            signal = "Bearish"
        else:
            signal = "Neutral"

        return {
            "tenkan_sen": round(float(tenkan), 2) if not np.isnan(tenkan) else 0,
            "kijun_sen": round(float(kijun), 2) if not np.isnan(kijun) else 0,
            "senkou_span_a": round(float(span_a), 2) if not np.isnan(span_a) else 0,
            "senkou_span_b": round(float(span_b), 2) if not np.isnan(span_b) else 0,
            "signal": signal
        }

    def _calculate_vwap(self, df: pd.DataFrame, current_price: float) -> Dict:
        """Calculate Volume Weighted Average Price"""
        # VWAP = Cumulative(Price * Volume) / Cumulative(Volume)
        typical_price = (df['High'] + df['Low'] + df['Close']) / 3
        vwap = (typical_price * df['Volume']).cumsum() / df['Volume'].cumsum()

        current_vwap = vwap.iloc[-1]

        signal = "Bullish" if current_price > current_vwap else "Bearish"

        return {
            "value": round(float(current_vwap), 2),
            "signal": signal
        }

    def _calculate_fibonacci(self, df: pd.DataFrame, current_price: float) -> Dict:
        """Calculate Fibonacci Retracement levels"""
        # Find recent significant high and low (last 50 periods)
        recent_data = df.tail(50)
        high = recent_data['High'].max()
        low = recent_data['Low'].min()

        diff = high - low

        levels = {
            "0.000": round(high, 2),
            "0.236": round(high - 0.236 * diff, 2),
            "0.382": round(high - 0.382 * diff, 2),
            "0.500": round(high - 0.500 * diff, 2),
            "0.618": round(high - 0.618 * diff, 2),
            "0.786": round(high - 0.786 * diff, 2),
            "1.000": round(low, 2)
        }

        # Determine which level price is near
        tolerance = diff * 0.02  # 2% tolerance
        signal = "Neutral"

        for level_name, level_value in levels.items():
            if abs(current_price - level_value) < tolerance:
                if current_price < levels["0.500"]:
                    signal = f"Testing Support {level_name}"
                else:
                    signal = f"Testing Resistance {level_name}"
                break

        return {
            "recent_high": round(high, 2),
            "recent_low": round(low, 2),
            "levels": levels,
            "signal": signal
        }

    def _find_key_levels(self, df: pd.DataFrame, indicators: Dict) -> Dict:
        """Identify key support and resistance levels"""
        support = []
        resistance = []

        # Add Fibonacci levels
        fib = indicators["fibonacci"]
        support.append(fib["levels"]["0.618"])
        support.append(fib["levels"]["0.786"])
        resistance.append(fib["levels"]["0.236"])
        resistance.append(fib["levels"]["0.382"])

        # Add Bollinger bands
        bb = indicators["bollinger_bands"]
        support.append(bb["lower_band"])
        resistance.append(bb["upper_band"])

        # Add moving averages
        sma = indicators["sma"]
        support.append(sma["sma_200"])
        resistance.append(sma["sma_50"])

        return {
            "support": sorted(list(set(support)))[:3],  # Top 3 unique support levels
            "resistance": sorted(list(set(resistance)), reverse=True)[:3]  # Top 3 unique resistance levels
        }

    def _calculate_overall_sentiment(self, indicators: Dict) -> str:
        """Calculate overall market sentiment from all indicators"""
        bullish_count = 0
        bearish_count = 0
        total_indicators = 0

        # Score each indicator
        for indicator_name, indicator_data in indicators.items():
            signal = indicator_data.get("signal", "")
            total_indicators += 1

            if any(word in signal.lower() for word in ["bullish", "oversold", "rising"]):
                bullish_count += 1
            elif any(word in signal.lower() for word in ["bearish", "overbought", "falling"]):
                bearish_count += 1

        # Calculate sentiment
        if bullish_count >= total_indicators * 0.7:
            return "Strong Bullish"
        elif bullish_count >= total_indicators * 0.5:
            return "Bullish"
        elif bearish_count >= total_indicators * 0.7:
            return "Strong Bearish"
        elif bearish_count >= total_indicators * 0.5:
            return "Bearish"
        else:
            return "Neutral"

    def _generate_summary(self, ticker: str, price: float, indicators: Dict, sentiment: str) -> str:
        """Generate human-readable analysis summary"""
        # Get key signals
        macd_signal = indicators["macd"]["signal"]
        rsi_signal = indicators["rsi"]["signal"]
        sma_signal = indicators["sma"]["signal"]

        summary = f"{ticker} at ${price:.2f} shows {sentiment.lower()} momentum. "

        # Add MACD info
        if "Crossover" in macd_signal:
            summary += f"{macd_signal} detected. "

        # Add trend info
        if sma_signal in ["Bullish", "Bearish"]:
            summary += f"Price is {sma_signal.lower()} relative to key moving averages. "

        # Add RSI warning
        if rsi_signal != "Neutral":
            summary += f"RSI indicates {rsi_signal.lower()} conditions. "

        return summary.strip()

    def _get_empty_analysis(self, ticker: str, timeframe: str, reason: str) -> Dict:
        """Return empty analysis structure when data is insufficient"""
        return {
            "analysis_timestamp_utc": datetime.utcnow().isoformat() + "Z",
            "data_source": "alpaca_data_cache",
            "asset_analyzed": ticker,
            "data_timeframe": timeframe,
            "overall_sentiment": "Unknown",
            "key_levels": {"support": [], "resistance": []},
            "analysis_summary": f"Analysis unavailable: {reason}",
            "indicator_details": {}
        }

    def to_json(self, analysis: Dict) -> str:
        """Convert analysis to JSON string"""
        return json.dumps(analysis, indent=2)


# Global engine instance
_engine = None


def get_trading_engine() -> TradingAnalysisEngine:
    """Get global trading analysis engine instance"""
    global _engine
    if _engine is None:
        _engine = TradingAnalysisEngine()
    return _engine


if __name__ == '__main__':
    # Test the trading analysis engine
    print("\n" + "="*60)
    print("TRADING ANALYSIS ENGINE TEST")
    print("="*60)

    engine = TradingAnalysisEngine()
    print("\n✓ Engine initialized")

    # Test with sample data
    import yfinance as yf

    ticker = "AAPL"
    print(f"\nFetching data for {ticker}...")

    stock = yf.Ticker(ticker)
    df = stock.history(period="1y")

    if not df.empty:
        print(f"✓ Fetched {len(df)} days of data")

        print(f"\nPerforming analysis...")
        analysis = engine.analyze(ticker, df, "1D")

        print(f"\n📊 ANALYSIS RESULTS:")
        print(f"   Overall Sentiment: {analysis['overall_sentiment']}")
        print(f"   Summary: {analysis['analysis_summary']}")

        print(f"\n📈 Key Indicators:")
        for name, data in list(analysis['indicator_details'].items())[:5]:
            print(f"   {name}: {data.get('signal', 'N/A')}")

        print(f"\n💾 JSON Output (first 500 chars):")
        json_output = engine.to_json(analysis)
        print(json_output[:500] + "...")
    else:
        print("✗ No data available")

    print("\n" + "="*60 + "\n")
