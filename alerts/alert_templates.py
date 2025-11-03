"""
Alert Templates
Beautiful message templates for WhatsApp, Telegram, and Email alerts
"""

from typing import Dict, Any
from datetime import datetime


class AlertTemplates:
    """Message templates for different alert types"""

    @staticmethod
    def price_threshold_alert(symbol: str, price: float, trigger_price: float, direction: str) -> Dict[str, str]:
        """
        Price Threshold Alert
        Trigger: Price crosses ABOVE or BELOW a set trigger price

        Args:
            symbol: Stock ticker
            price: Current price
            trigger_price: The trigger price
            direction: "above" or "below"

        Returns:
            Dict with 'whatsapp', 'telegram', and 'email' formatted messages
        """
        emoji = "🚀" if direction == "above" else "📉"
        action = "crossed above" if direction == "above" else "fell below"

        # WhatsApp/Telegram (concise, emoji-led)
        short_msg = f"""
{emoji} **Price Alert: {symbol}**

${price:.2f} {action} ${trigger_price:.2f}

_Time: {datetime.now().strftime('%I:%M %p ET')}_
        """.strip()

        # Email (more formal)
        email_subject = f"Price Alert for {symbol}: Crossed ${trigger_price:.2f}"
        email_body = f"""
{emoji} Price Alert for {symbol}

Current Price: ${price:.2f}
Trigger Price: ${trigger_price:.2f}
Action: {action.title()}
Time: {datetime.now().strftime('%I:%M %p ET on %B %d, %Y')}

---
Market Alerts System
        """.strip()

        return {
            'whatsapp': short_msg,
            'telegram': short_msg,
            'email_subject': email_subject,
            'email_body': email_body
        }

    @staticmethod
    def price_change_percent_alert(symbol: str, price: float, change_percent: float, timeframe: str = "30-minute") -> Dict[str, str]:
        """
        Significant % Change Alert
        Trigger: Price moves more than X% in the last check period

        Args:
            symbol: Stock ticker
            price: Current price
            change_percent: Percentage change
            timeframe: Time period (default: "30-minute")

        Returns:
            Dict with formatted messages
        """
        direction = "UP" if change_percent > 0 else "DOWN"
        emoji = "📈" if change_percent > 0 else "📉"

        short_msg = f"""
{emoji} **{symbol} {direction} {abs(change_percent):.2f}%**

Current: ${price:.2f}
Timeframe: {timeframe}

_Time: {datetime.now().strftime('%I:%M %p ET')}_
        """.strip()

        email_subject = f"{symbol} Moved {abs(change_percent):.1f}% in {timeframe}"
        email_body = f"""
{emoji} Significant Price Movement Alert

Symbol: {symbol}
Direction: {direction}
Change: {change_percent:+.2f}%
Current Price: ${price:.2f}
Timeframe: {timeframe}
Time: {datetime.now().strftime('%I:%M %p ET on %B %d, %Y')}

---
Market Alerts System
        """.strip()

        return {
            'whatsapp': short_msg,
            'telegram': short_msg,
            'email_subject': email_subject,
            'email_body': email_body
        }

    @staticmethod
    def volume_spike_alert(symbol: str, price: float, volume: int, avg_volume: int, multiplier: float) -> Dict[str, str]:
        """
        Volume Spike Alert
        Trigger: Volume is X% above average

        Args:
            symbol: Stock ticker
            price: Current price
            volume: Current volume
            avg_volume: Average volume
            multiplier: Volume multiplier (e.g., 2.5x)

        Returns:
            Dict with formatted messages
        """
        short_msg = f"""
🔊 **Volume Spike: {symbol}**

{multiplier:.1f}x Average Volume!

Price: ${price:.2f}
Volume: {volume:,} vs Avg {avg_volume:,}

_Time: {datetime.now().strftime('%I:%M %p ET')}_
        """.strip()

        email_subject = f"Volume Spike Alert: {symbol} ({multiplier:.1f}x Average)"
        email_body = f"""
🔊 Volume Spike Detected

Symbol: {symbol}
Current Price: ${price:.2f}
Current Volume: {volume:,}
Average Volume: {avg_volume:,}
Multiplier: {multiplier:.1f}x

This indicates unusual trading activity.

Time: {datetime.now().strftime('%I:%M %p ET on %B %d, %Y')}

---
Market Alerts System
        """.strip()

        return {
            'whatsapp': short_msg,
            'telegram': short_msg,
            'email_subject': email_subject,
            'email_body': email_body
        }

    @staticmethod
    def rsi_alert(symbol: str, price: float, rsi: float, condition: str) -> Dict[str, str]:
        """
        RSI Level Alert
        Trigger: RSI crosses BELOW 30 (Oversold) or ABOVE 70 (Overbought)

        Args:
            symbol: Stock ticker
            price: Current price
            rsi: RSI value
            condition: "oversold" or "overbought"

        Returns:
            Dict with formatted messages
        """
        if condition == "oversold":
            emoji = "🟢"
            signal = "OVERSOLD"
            desc = "Potential buying opportunity"
        else:
            emoji = "🔴"
            signal = "OVERBOUGHT"
            desc = "Potential selling signal"

        short_msg = f"""
{emoji} **RSI Alert: {symbol}**

RSI: {rsi:.1f} - {signal}
Price: ${price:.2f}

_{desc}_
_Time: {datetime.now().strftime('%I:%M %p ET')}_
        """.strip()

        email_subject = f"RSI Alert for {symbol}: {signal} at {rsi:.1f}"
        email_body = f"""
{emoji} RSI Technical Indicator Alert

Symbol: {symbol}
Current Price: ${price:.2f}
RSI Value: {rsi:.1f}
Signal: {signal}
Interpretation: {desc}

Time: {datetime.now().strftime('%I:%M %p ET on %B %d, %Y')}

---
Market Alerts System
        """.strip()

        return {
            'whatsapp': short_msg,
            'telegram': short_msg,
            'email_subject': email_subject,
            'email_body': email_body
        }

    @staticmethod
    def ma_crossover_alert(symbol: str, price: float, ma_type: str, ma_period: int, direction: str) -> Dict[str, str]:
        """
        Moving Average Crossover Alert
        Trigger: Price crosses ABOVE or BELOW a key MA

        Args:
            symbol: Stock ticker
            price: Current price
            ma_type: Type of MA (e.g., "SMA", "EMA")
            ma_period: MA period (e.g., 50, 200)
            direction: "above" or "below"

        Returns:
            Dict with formatted messages
        """
        emoji = "✅" if direction == "above" else "⚠️"
        signal = "BULLISH" if direction == "above" else "BEARISH"
        action = "crossed above" if direction == "above" else "fell below"

        short_msg = f"""
{emoji} **MA Crossover: {symbol}**

Price {action} {ma_type}-{ma_period}
Signal: {signal}

Current: ${price:.2f}

_Time: {datetime.now().strftime('%I:%M %p ET')}_
        """.strip()

        email_subject = f"MA Crossover Alert: {symbol} {action} {ma_type}-{ma_period}"
        email_body = f"""
{emoji} Moving Average Crossover Alert

Symbol: {symbol}
Current Price: ${price:.2f}
Moving Average: {ma_type}-{ma_period}
Action: {action.title()}
Signal: {signal}

This is a potentially significant technical signal.

Time: {datetime.now().strftime('%I:%M %p ET on %B %d, %Y')}

---
Market Alerts System
        """.strip()

        return {
            'whatsapp': short_msg,
            'telegram': short_msg,
            'email_subject': email_subject,
            'email_body': email_body
        }

    @staticmethod
    def breaking_news_alert(symbol: str, headline: str, source: str, keywords: list) -> Dict[str, str]:
        """
        Breaking News / Economic Data Alert
        Trigger: High-impact news keyword published

        Args:
            symbol: Stock ticker (or "MARKET" for general news)
            headline: News headline
            source: News source
            keywords: Matched keywords

        Returns:
            Dict with formatted messages
        """
        keywords_str = ", ".join(keywords)

        short_msg = f"""
📰 **Breaking News: {symbol}**

{headline}

Keywords: {keywords_str}
Source: {source}

_Time: {datetime.now().strftime('%I:%M %p ET')}_
        """.strip()

        email_subject = f"Breaking News Alert: {symbol} - {keywords[0] if keywords else 'Important'}"
        email_body = f"""
📰 Breaking News Alert

Symbol: {symbol}
Headline: {headline}
Source: {source}
Keywords Matched: {keywords_str}

Time: {datetime.now().strftime('%I:%M %p ET on %B %d, %Y')}

---
Market Alerts System
        """.strip()

        return {
            'whatsapp': short_msg,
            'telegram': short_msg,
            'email_subject': email_subject,
            'email_body': email_body
        }

    @staticmethod
    def hourly_summary(stats: Dict[str, Any]) -> Dict[str, str]:
        """
        Hourly Watchlist Summary
        Time-based alert sent every hour

        Args:
            stats: Dictionary with market statistics

        Returns:
            Dict with formatted messages
        """
        gainers = stats.get('top_gainers', [])
        losers = stats.get('top_losers', [])
        total_symbols = stats.get('total_symbols', 0)
        market_status = stats.get('market_status', 'Closed')

        gainers_text = "\n".join([f"  • {g['symbol']}: {g['price']:.2f} (+{g['change_pct']:.2f}%)" for g in gainers[:3]])
        losers_text = "\n".join([f"  • {l['symbol']}: {l['price']:.2f} ({l['change_pct']:.2f}%)" for l in losers[:3]])

        short_msg = f"""
📊 **Hourly Market Summary**

_Market: {market_status}_
_Watching: {total_symbols} symbols_

**Top Gainers:**
{gainers_text or "  None"}

**Top Losers:**
{losers_text or "  None"}

_Time: {datetime.now().strftime('%I:%M %p ET')}_
        """.strip()

        email_subject = f"Hourly Market Summary - {datetime.now().strftime('%I %p ET')}"
        email_body = f"""
📊 Hourly Watchlist Summary

Market Status: {market_status}
Total Symbols: {total_symbols}

Top Gainers:
{gainers_text or "None"}

Top Losers:
{losers_text or "None"}

Time: {datetime.now().strftime('%I:%M %p ET on %B %d, %Y')}

---
Market Alerts System
        """.strip()

        return {
            'whatsapp': short_msg,
            'telegram': short_msg,
            'email_subject': email_subject,
            'email_body': email_body
        }

    @staticmethod
    def bollinger_breakout_alert(symbol: str, price: float, band_type: str, band_value: float) -> Dict[str, str]:
        """
        Bollinger Band Breakout Alert
        Trigger: Price breaks above upper or below lower Bollinger Band

        Args:
            symbol: Stock ticker
            price: Current price
            band_type: "upper" or "lower"
            band_value: Band value

        Returns:
            Dict with formatted messages
        """
        if band_type == "upper":
            emoji = "⬆️"
            signal = "BREAKOUT"
            desc = "Price broke above upper band"
        else:
            emoji = "⬇️"
            signal = "BREAKDOWN"
            desc = "Price broke below lower band"

        short_msg = f"""
{emoji} **Bollinger {signal}: {symbol}**

Price: ${price:.2f}
Band: ${band_value:.2f}

_{desc}_
_Time: {datetime.now().strftime('%I:%M %p ET')}_
        """.strip()

        email_subject = f"Bollinger Band Alert: {symbol} {signal}"
        email_body = f"""
{emoji} Bollinger Band Alert

Symbol: {symbol}
Current Price: ${price:.2f}
{band_type.title()} Band: ${band_value:.2f}
Signal: {signal}
Description: {desc}

This indicates potential volatility expansion.

Time: {datetime.now().strftime('%I:%M %p ET on %B %d, %Y')}

---
Market Alerts System
        """.strip()

        return {
            'whatsapp': short_msg,
            'telegram': short_msg,
            'email_subject': email_subject,
            'email_body': email_body
        }

    @staticmethod
    def macd_signal_alert(symbol: str, price: float, macd_line: float, signal_line: float, crossover: str) -> Dict[str, str]:
        """
        MACD Crossover Alert
        Trigger: MACD line crosses signal line

        Args:
            symbol: Stock ticker
            price: Current price
            macd_line: MACD line value
            signal_line: Signal line value
            crossover: "bullish" or "bearish"

        Returns:
            Dict with formatted messages
        """
        emoji = "🟢" if crossover == "bullish" else "🔴"
        signal = "BULLISH CROSSOVER" if crossover == "bullish" else "BEARISH CROSSOVER"

        short_msg = f"""
{emoji} **MACD Alert: {symbol}**

{signal}
Price: ${price:.2f}

MACD: {macd_line:.2f}
Signal: {signal_line:.2f}

_Time: {datetime.now().strftime('%I:%M %p ET')}_
        """.strip()

        email_subject = f"MACD Alert: {symbol} - {signal}"
        email_body = f"""
{emoji} MACD Crossover Alert

Symbol: {symbol}
Current Price: ${price:.2f}
MACD Line: {macd_line:.2f}
Signal Line: {signal_line:.2f}
Crossover Type: {signal}

This is a momentum indicator signal.

Time: {datetime.now().strftime('%I:%M %p ET on %B %d, %Y')}

---
Market Alerts System
        """.strip()

        return {
            'whatsapp': short_msg,
            'telegram': short_msg,
            'email_subject': email_subject,
            'email_body': email_body
        }


if __name__ == '__main__':
    # Test templates
    print("\n" + "="*60)
    print("ALERT TEMPLATES TEST")
    print("="*60)

    # Test price threshold alert
    print("\n1. PRICE THRESHOLD ALERT:")
    print("-" * 60)
    msg = AlertTemplates.price_threshold_alert("AAPL", 305.50, 300.00, "above")
    print(msg['whatsapp'])

    # Test volume spike alert
    print("\n2. VOLUME SPIKE ALERT:")
    print("-" * 60)
    msg = AlertTemplates.volume_spike_alert("TSLA", 250.75, 150000000, 50000000, 3.0)
    print(msg['whatsapp'])

    # Test RSI alert
    print("\n3. RSI ALERT:")
    print("-" * 60)
    msg = AlertTemplates.rsi_alert("MSFT", 420.30, 28.5, "oversold")
    print(msg['whatsapp'])

    # Test MA crossover
    print("\n4. MA CROSSOVER ALERT:")
    print("-" * 60)
    msg = AlertTemplates.ma_crossover_alert("SPY", 580.25, "SMA", 200, "above")
    print(msg['whatsapp'])

    # Test breaking news
    print("\n5. BREAKING NEWS ALERT:")
    print("-" * 60)
    msg = AlertTemplates.breaking_news_alert("AAPL", "Apple announces major acquisition", "Reuters", ["acquisition", "earnings"])
    print(msg['whatsapp'])

    print("\n" + "="*60 + "\n")
