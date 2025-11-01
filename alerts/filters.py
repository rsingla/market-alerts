"""
Alert Filters
Determines which market movements warrant alerts
"""

from enum import Enum
from typing import Optional
from data.market_data import StockQuote
from config import settings
from utils.logger import logger


class AlertType(Enum):
    """Types of alerts"""
    SMALL_MOVE = "small_move"
    MEDIUM_MOVE = "medium_move"
    LARGE_MOVE = "large_move"
    VOLUME_SPIKE = "volume_spike"
    NEWS = "news"
    MARKET_SUMMARY = "market_summary"


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


def should_alert(quote: StockQuote) -> Optional[tuple[AlertType, AlertLevel]]:
    """
    Determine if a stock quote warrants an alert

    Args:
        quote: StockQuote object

    Returns:
        Tuple of (AlertType, AlertLevel) or None if no alert needed
    """
    if not quote:
        return None

    # Check for large price movements first (most critical)
    if abs(quote.change_percent) >= settings.LARGE_MOVE_THRESHOLD:
        logger.info(f"LARGE move detected: {quote.symbol} {quote.change_percent:+.2f}%")
        return (AlertType.LARGE_MOVE, AlertLevel.CRITICAL)

    # Check for medium price movements
    if abs(quote.change_percent) >= settings.MEDIUM_MOVE_THRESHOLD:
        logger.info(f"MEDIUM move detected: {quote.symbol} {quote.change_percent:+.2f}%")
        return (AlertType.MEDIUM_MOVE, AlertLevel.WARNING)

    # Check for volume spikes
    if quote.volume_ratio >= settings.VOLUME_SPIKE_THRESHOLD:
        logger.info(f"VOLUME spike detected: {quote.symbol} {quote.volume_ratio:.2f}x")
        return (AlertType.VOLUME_SPIKE, AlertLevel.WARNING)

    # Check for small movements (info only)
    if abs(quote.change_percent) >= settings.SMALL_MOVE_THRESHOLD:
        logger.debug(f"Small move detected: {quote.symbol} {quote.change_percent:+.2f}%")
        return (AlertType.SMALL_MOVE, AlertLevel.INFO)

    return None


def filter_quotes_for_alerts(quotes: dict[str, StockQuote]) -> dict[str, tuple[AlertType, AlertLevel]]:
    """
    Filter multiple quotes and return those that need alerts

    Args:
        quotes: Dictionary mapping symbol to StockQuote

    Returns:
        Dictionary mapping symbol to (AlertType, AlertLevel)
    """
    alerts = {}

    for symbol, quote in quotes.items():
        alert_info = should_alert(quote)
        if alert_info:
            alerts[symbol] = alert_info

    logger.info(f"Found {len(alerts)} alerts from {len(quotes)} quotes")
    return alerts


def prioritize_alerts(alerts: dict[str, tuple[AlertType, AlertLevel]]) -> list[tuple[str, AlertType, AlertLevel]]:
    """
    Sort alerts by priority (critical first, then by alert type)

    Args:
        alerts: Dictionary mapping symbol to (AlertType, AlertLevel)

    Returns:
        List of (symbol, AlertType, AlertLevel) tuples sorted by priority
    """
    # Define priority order
    level_priority = {
        AlertLevel.CRITICAL: 3,
        AlertLevel.WARNING: 2,
        AlertLevel.INFO: 1
    }

    type_priority = {
        AlertType.LARGE_MOVE: 5,
        AlertType.MEDIUM_MOVE: 4,
        AlertType.VOLUME_SPIKE: 3,
        AlertType.SMALL_MOVE: 2,
        AlertType.NEWS: 1,
        AlertType.MARKET_SUMMARY: 0
    }

    # Convert to list with priorities
    alert_list = []
    for symbol, (alert_type, alert_level) in alerts.items():
        priority = (level_priority[alert_level], type_priority[alert_type])
        alert_list.append((symbol, alert_type, alert_level, priority))

    # Sort by priority (descending)
    alert_list.sort(key=lambda x: x[3], reverse=True)

    # Remove priority from result
    return [(symbol, alert_type, alert_level) for symbol, alert_type, alert_level, _ in alert_list]


def should_send_summary() -> bool:
    """
    Determine if we should send a market summary alert

    Returns:
        True if summary should be sent
    """
    from utils.market_hours import is_market_hours, get_current_et_time

    now = get_current_et_time()
    hour = now.hour
    minute = now.minute

    # Send summary at market open (9:30 AM)
    if is_market_hours() and hour == 9 and minute >= 30 and minute < 35:
        return True

    # Send summary at market close (4:00 PM)
    if hour == 16 and minute < 5:
        return True

    # Send summary at midday (12:00 PM)
    if is_market_hours() and hour == 12 and minute < 5:
        return True

    return False


def get_alert_emoji(alert_type: AlertType, alert_level: AlertLevel) -> str:
    """
    Get emoji for alert type and level

    Args:
        alert_type: Type of alert
        alert_level: Severity level

    Returns:
        Emoji string
    """
    if alert_level == AlertLevel.CRITICAL:
        return "🚨"
    elif alert_level == AlertLevel.WARNING:
        if alert_type == AlertType.VOLUME_SPIKE:
            return "📊"
        return "⚠️"
    else:
        return "ℹ️"


if __name__ == '__main__':
    # Test filtering logic
    from data.market_data import StockQuote

    print("\n" + "="*60)
    print("ALERT FILTERS TEST")
    print("="*60)

    # Create test quotes
    test_data = [
        {'symbol': 'TEST1', 'regularMarketPrice': 100, 'regularMarketChangePercent': 0.5},  # No alert
        {'symbol': 'TEST2', 'regularMarketPrice': 100, 'regularMarketChangePercent': 1.5},  # Small
        {'symbol': 'TEST3', 'regularMarketPrice': 100, 'regularMarketChangePercent': 3.5},  # Medium
        {'symbol': 'TEST4', 'regularMarketPrice': 100, 'regularMarketChangePercent': 6.0},  # Large
        {'symbol': 'TEST5', 'regularMarketPrice': 100, 'regularMarketChangePercent': -4.5},  # Medium (negative)
    ]

    quotes = {}
    for data in test_data:
        quote = StockQuote(data['symbol'], {
            'regularMarketPrice': data['regularMarketPrice'],
            'regularMarketChangePercent': data['regularMarketChangePercent'],
            'regularMarketChange': data['regularMarketChangePercent'],
            'regularMarketVolume': 1000000,
            'averageDailyVolume10Day': 1000000,
            'regularMarketDayHigh': 105,
            'regularMarketDayLow': 95,
            'regularMarketPreviousClose': 100,
        })
        quotes[data['symbol']] = quote

    # Test filtering
    alerts = filter_quotes_for_alerts(quotes)
    print(f"\n✓ Found {len(alerts)} alerts from {len(quotes)} quotes")

    # Test prioritization
    prioritized = prioritize_alerts(alerts)
    print("\nPrioritized alerts:")
    for symbol, alert_type, alert_level in prioritized:
        emoji = get_alert_emoji(alert_type, alert_level)
        print(f"  {emoji} {symbol}: {alert_type.value} ({alert_level.value})")

    print("="*60 + "\n")
