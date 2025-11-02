"""
Technical Indicators Module
Calculates various technical indicators: MACD, Bollinger Bands, RSI, SMA, EMA, etc.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
from utils.logger import logger


class TechnicalIndicators:
    """Calculate technical indicators for stock data"""

    @staticmethod
    def calculate_sma(data: pd.Series, period: int = 20) -> pd.Series:
        """
        Calculate Simple Moving Average

        Args:
            data: Price data series
            period: Number of periods for SMA

        Returns:
            SMA series
        """
        return data.rolling(window=period).mean()

    @staticmethod
    def calculate_ema(data: pd.Series, period: int = 12) -> pd.Series:
        """
        Calculate Exponential Moving Average

        Args:
            data: Price data series
            period: Number of periods for EMA

        Returns:
            EMA series
        """
        return data.ewm(span=period, adjust=False).mean()

    @staticmethod
    def calculate_macd(
        data: pd.Series,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> Dict[str, pd.Series]:
        """
        Calculate MACD (Moving Average Convergence Divergence)

        Args:
            data: Price data series (typically close prices)
            fast_period: Fast EMA period (default 12)
            slow_period: Slow EMA period (default 26)
            signal_period: Signal line period (default 9)

        Returns:
            Dictionary with 'macd', 'signal', and 'histogram' series
        """
        ema_fast = data.ewm(span=fast_period, adjust=False).mean()
        ema_slow = data.ewm(span=slow_period, adjust=False).mean()

        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
        histogram = macd_line - signal_line

        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }

    @staticmethod
    def calculate_bollinger_bands(
        data: pd.Series,
        period: int = 20,
        num_std: float = 2.0
    ) -> Dict[str, pd.Series]:
        """
        Calculate Bollinger Bands

        Args:
            data: Price data series
            period: Moving average period (default 20)
            num_std: Number of standard deviations (default 2.0)

        Returns:
            Dictionary with 'upper', 'middle', 'lower' bands and 'bandwidth'
        """
        middle_band = data.rolling(window=period).mean()
        std = data.rolling(window=period).std()

        upper_band = middle_band + (std * num_std)
        lower_band = middle_band - (std * num_std)
        bandwidth = (upper_band - lower_band) / middle_band

        return {
            'upper': upper_band,
            'middle': middle_band,
            'lower': lower_band,
            'bandwidth': bandwidth
        }

    @staticmethod
    def calculate_rsi(data: pd.Series, period: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index (RSI)

        Args:
            data: Price data series
            period: RSI period (default 14)

        Returns:
            RSI series (0-100)
        """
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    @staticmethod
    def calculate_stochastic(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        k_period: int = 14,
        d_period: int = 3
    ) -> Dict[str, pd.Series]:
        """
        Calculate Stochastic Oscillator

        Args:
            high: High price series
            low: Low price series
            close: Close price series
            k_period: %K period (default 14)
            d_period: %D period (default 3)

        Returns:
            Dictionary with '%K' and '%D' series
        """
        lowest_low = low.rolling(window=k_period).min()
        highest_high = high.rolling(window=k_period).max()

        k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d_percent = k_percent.rolling(window=d_period).mean()

        return {
            'k': k_percent,
            'd': d_percent
        }

    @staticmethod
    def calculate_atr(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period: int = 14
    ) -> pd.Series:
        """
        Calculate Average True Range (ATR)

        Args:
            high: High price series
            low: Low price series
            close: Close price series
            period: ATR period (default 14)

        Returns:
            ATR series
        """
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())

        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()

        return atr

    @staticmethod
    def calculate_obv(close: pd.Series, volume: pd.Series) -> pd.Series:
        """
        Calculate On-Balance Volume (OBV)

        Args:
            close: Close price series
            volume: Volume series

        Returns:
            OBV series
        """
        obv = (np.sign(close.diff()) * volume).fillna(0).cumsum()
        return obv

    @staticmethod
    def calculate_all_indicators(df: pd.DataFrame) -> Dict[str, any]:
        """
        Calculate all technical indicators for a stock

        Args:
            df: DataFrame with OHLCV data (columns: Open, High, Low, Close, Volume)

        Returns:
            Dictionary with all calculated indicators
        """
        try:
            indicators = {}

            # Moving Averages
            indicators['sma_20'] = TechnicalIndicators.calculate_sma(df['Close'], 20)
            indicators['sma_50'] = TechnicalIndicators.calculate_sma(df['Close'], 50)
            indicators['sma_200'] = TechnicalIndicators.calculate_sma(df['Close'], 200)
            indicators['ema_12'] = TechnicalIndicators.calculate_ema(df['Close'], 12)
            indicators['ema_26'] = TechnicalIndicators.calculate_ema(df['Close'], 26)

            # MACD
            macd = TechnicalIndicators.calculate_macd(df['Close'])
            indicators['macd'] = macd['macd']
            indicators['macd_signal'] = macd['signal']
            indicators['macd_histogram'] = macd['histogram']

            # Bollinger Bands
            bb = TechnicalIndicators.calculate_bollinger_bands(df['Close'])
            indicators['bb_upper'] = bb['upper']
            indicators['bb_middle'] = bb['middle']
            indicators['bb_lower'] = bb['lower']
            indicators['bb_bandwidth'] = bb['bandwidth']

            # RSI
            indicators['rsi'] = TechnicalIndicators.calculate_rsi(df['Close'])

            # Stochastic
            stoch = TechnicalIndicators.calculate_stochastic(
                df['High'], df['Low'], df['Close']
            )
            indicators['stoch_k'] = stoch['k']
            indicators['stoch_d'] = stoch['d']

            # ATR
            indicators['atr'] = TechnicalIndicators.calculate_atr(
                df['High'], df['Low'], df['Close']
            )

            # OBV
            if 'Volume' in df.columns:
                indicators['obv'] = TechnicalIndicators.calculate_obv(df['Close'], df['Volume'])

            # Get latest values
            latest = {
                'sma_20': indicators['sma_20'].iloc[-1] if len(indicators['sma_20']) > 0 else None,
                'sma_50': indicators['sma_50'].iloc[-1] if len(indicators['sma_50']) > 0 else None,
                'sma_200': indicators['sma_200'].iloc[-1] if len(indicators['sma_200']) > 0 else None,
                'ema_12': indicators['ema_12'].iloc[-1] if len(indicators['ema_12']) > 0 else None,
                'ema_26': indicators['ema_26'].iloc[-1] if len(indicators['ema_26']) > 0 else None,
                'macd': indicators['macd'].iloc[-1] if len(indicators['macd']) > 0 else None,
                'macd_signal': indicators['macd_signal'].iloc[-1] if len(indicators['macd_signal']) > 0 else None,
                'macd_histogram': indicators['macd_histogram'].iloc[-1] if len(indicators['macd_histogram']) > 0 else None,
                'bb_upper': indicators['bb_upper'].iloc[-1] if len(indicators['bb_upper']) > 0 else None,
                'bb_middle': indicators['bb_middle'].iloc[-1] if len(indicators['bb_middle']) > 0 else None,
                'bb_lower': indicators['bb_lower'].iloc[-1] if len(indicators['bb_lower']) > 0 else None,
                'rsi': indicators['rsi'].iloc[-1] if len(indicators['rsi']) > 0 else None,
                'stoch_k': indicators['stoch_k'].iloc[-1] if len(indicators['stoch_k']) > 0 else None,
                'stoch_d': indicators['stoch_d'].iloc[-1] if len(indicators['stoch_d']) > 0 else None,
                'atr': indicators['atr'].iloc[-1] if len(indicators['atr']) > 0 else None,
            }

            if 'obv' in indicators:
                latest['obv'] = indicators['obv'].iloc[-1] if len(indicators['obv']) > 0 else None

            return {
                'series': indicators,
                'latest': latest,
                'signals': TechnicalIndicators.generate_signals(latest, df['Close'].iloc[-1])
            }

        except Exception as e:
            logger.error(f"Error calculating indicators: {e}", exc_info=True)
            return {'series': {}, 'latest': {}, 'signals': {}}

    @staticmethod
    def generate_signals(indicators: Dict, current_price: float) -> Dict[str, str]:
        """
        Generate trading signals from indicators

        Args:
            indicators: Dictionary of indicator values
            current_price: Current stock price

        Returns:
            Dictionary of signals (buy/sell/neutral)
        """
        signals = {}

        try:
            # RSI Signal
            rsi = indicators.get('rsi')
            if rsi:
                if rsi < 30:
                    signals['rsi'] = 'oversold'
                elif rsi > 70:
                    signals['rsi'] = 'overbought'
                else:
                    signals['rsi'] = 'neutral'

            # MACD Signal
            macd = indicators.get('macd')
            macd_signal = indicators.get('macd_signal')
            if macd and macd_signal:
                if macd > macd_signal:
                    signals['macd'] = 'bullish'
                else:
                    signals['macd'] = 'bearish'

            # Bollinger Bands Signal
            bb_upper = indicators.get('bb_upper')
            bb_lower = indicators.get('bb_lower')
            if bb_upper and bb_lower:
                if current_price > bb_upper:
                    signals['bollinger'] = 'overbought'
                elif current_price < bb_lower:
                    signals['bollinger'] = 'oversold'
                else:
                    signals['bollinger'] = 'neutral'

            # Stochastic Signal
            stoch_k = indicators.get('stoch_k')
            stoch_d = indicators.get('stoch_d')
            if stoch_k and stoch_d:
                if stoch_k < 20:
                    signals['stochastic'] = 'oversold'
                elif stoch_k > 80:
                    signals['stochastic'] = 'overbought'
                else:
                    signals['stochastic'] = 'neutral'

            # Moving Average Trend
            sma_20 = indicators.get('sma_20')
            sma_50 = indicators.get('sma_50')
            sma_200 = indicators.get('sma_200')

            if sma_20 and sma_50:
                if sma_20 > sma_50:
                    signals['trend_short'] = 'bullish'
                else:
                    signals['trend_short'] = 'bearish'

            if sma_50 and sma_200:
                if sma_50 > sma_200:
                    signals['trend_long'] = 'bullish'
                else:
                    signals['trend_long'] = 'bearish'

        except Exception as e:
            logger.error(f"Error generating signals: {e}")

        return signals


def get_technical_analysis(symbol: str, period: str = '3mo') -> Dict:
    """
    Get complete technical analysis for a symbol

    Args:
        symbol: Stock symbol
        period: Data period (1mo, 3mo, 6mo, 1y, etc.)

    Returns:
        Dictionary with indicators and analysis
    """
    try:
        import yfinance as yf

        # Fetch historical data
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)

        if df.empty:
            logger.warning(f"No data available for {symbol}")
            return {}

        # Calculate all indicators
        analysis = TechnicalIndicators.calculate_all_indicators(df)

        # Add symbol and current price
        analysis['symbol'] = symbol
        analysis['current_price'] = df['Close'].iloc[-1]
        analysis['data_points'] = len(df)

        return analysis

    except Exception as e:
        logger.error(f"Error fetching technical analysis for {symbol}: {e}")
        return {}


if __name__ == '__main__':
    # Test technical indicators
    print("\n" + "="*60)
    print("TECHNICAL INDICATORS TEST")
    print("="*60)

    symbol = "AAPL"
    print(f"\nTesting indicators for {symbol}...")

    analysis = get_technical_analysis(symbol)

    if analysis:
        print(f"\n✓ Analysis complete for {symbol}")
        print(f"  Current Price: ${analysis['current_price']:.2f}")
        print(f"  Data Points: {analysis['data_points']}")

        print("\n📊 Latest Indicators:")
        for key, value in analysis['latest'].items():
            if value is not None:
                print(f"  {key}: {value:.2f}")

        print("\n🎯 Trading Signals:")
        for key, value in analysis['signals'].items():
            print(f"  {key}: {value}")
    else:
        print(f"\n❌ Failed to get analysis for {symbol}")

    print("\n" + "="*60 + "\n")
