"""
Alert Engine
Main engine for detecting and managing market alerts
"""

from typing import List, Dict, Optional
from datetime import datetime
from dataclasses import dataclass
from data.market_data import get_market_summary, StockQuote
from data.news_fetcher import get_market_news
from .filters import filter_quotes_for_alerts, prioritize_alerts, AlertType, AlertLevel, should_send_summary
from .formatters import format_alert_message, format_market_summary, format_combined_alert, format_news_alert
from config import settings
from utils.logger import logger


@dataclass
class Alert:
    """Alert data structure"""
    symbol: str
    alert_type: AlertType
    alert_level: AlertLevel
    quote: StockQuote
    message: str
    timestamp: datetime

    def __repr__(self):
        return f"Alert({self.symbol}, {self.alert_type.value}, {self.alert_level.value})"


class AlertEngine:
    """Main alert engine"""

    def __init__(self):
        self.last_check = None
        self.alerts_history = []

    def check_markets(self) -> List[Alert]:
        """
        Check markets and generate alerts

        Returns:
            List of Alert objects
        """
        logger.info("Checking markets for alerts...")
        self.last_check = datetime.now()

        alerts = []

        try:
            # Fetch market data
            logger.info(f"Fetching quotes for {len(settings.WATCHLIST)} symbols")
            quotes = get_market_summary()

            if not quotes:
                logger.warning("No quotes fetched, skipping alert check")
                return alerts

            logger.info(f"Received {len(quotes)} quotes")

            # Filter for alerts
            alert_triggers = filter_quotes_for_alerts(quotes)

            if not alert_triggers:
                logger.info("No alerts triggered")
                return alerts

            # Create Alert objects
            for symbol, (alert_type, alert_level) in alert_triggers.items():
                quote = quotes[symbol]

                # Format message
                message = format_alert_message(symbol, quote, alert_type, alert_level)

                alert = Alert(
                    symbol=symbol,
                    alert_type=alert_type,
                    alert_level=alert_level,
                    quote=quote,
                    message=message,
                    timestamp=datetime.now()
                )

                alerts.append(alert)
                self.alerts_history.append(alert)

            logger.info(f"Generated {len(alerts)} alerts")

        except Exception as e:
            logger.error(f"Error checking markets: {e}", exc_info=True)

        return alerts

    def get_market_summary_alert(self) -> Optional[str]:
        """
        Generate a market summary message

        Returns:
            Formatted market summary or None
        """
        try:
            logger.info("Generating market summary")

            quotes = get_market_summary()

            if not quotes:
                logger.warning("No quotes available for summary")
                return None

            message = format_market_summary(quotes)
            return message

        except Exception as e:
            logger.error(f"Error generating market summary: {e}")
            return None

    def get_news_alert(self) -> Optional[str]:
        """
        Generate a news alert message

        Returns:
            Formatted news alert or None
        """
        try:
            logger.info("Fetching market news")

            articles = get_market_news()

            if not articles:
                logger.info("No news articles found")
                return None

            message = format_news_alert(articles)
            return message

        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            return None

    def get_combined_alert(self) -> Optional[str]:
        """
        Generate a combined alert with stocks and news

        Returns:
            Formatted combined alert or None
        """
        try:
            logger.info("Generating combined alert")

            # Get market data
            quotes = get_market_summary()
            if not quotes:
                return None

            # Filter for alerts
            alert_triggers = filter_quotes_for_alerts(quotes)

            if not alert_triggers:
                logger.info("No alerts for combined message")
                return None

            # Get news
            news = get_market_news(max_items=3)

            # Format message
            message = format_combined_alert(quotes, alert_triggers, news)
            return message

        except Exception as e:
            logger.error(f"Error generating combined alert: {e}")
            return None

    def get_priority_alerts(self, max_alerts: int = 5) -> List[Alert]:
        """
        Get top priority alerts

        Args:
            max_alerts: Maximum number of alerts to return

        Returns:
            List of Alert objects sorted by priority
        """
        alerts = self.check_markets()

        if not alerts:
            return []

        # Extract alert info for prioritization
        alert_dict = {alert.symbol: (alert.alert_type, alert.alert_level) for alert in alerts}

        # Prioritize
        prioritized = prioritize_alerts(alert_dict)

        # Return alerts in priority order
        result = []
        for symbol, _, _ in prioritized[:max_alerts]:
            alert = next(a for a in alerts if a.symbol == symbol)
            result.append(alert)

        return result

    def should_check_now(self) -> bool:
        """
        Determine if we should check markets now

        Returns:
            True if should check
        """
        from utils.market_hours import should_check_now
        return should_check_now()

    def get_alerts_since(self, since: datetime) -> List[Alert]:
        """
        Get alerts since a specific time

        Args:
            since: Datetime to filter from

        Returns:
            List of Alert objects
        """
        return [alert for alert in self.alerts_history if alert.timestamp > since]

    def get_stats(self) -> dict:
        """
        Get engine statistics

        Returns:
            Dictionary with statistics
        """
        return {
            'last_check': self.last_check.isoformat() if self.last_check else None,
            'total_alerts': len(self.alerts_history),
            'critical_alerts': len([a for a in self.alerts_history if a.alert_level == AlertLevel.CRITICAL]),
            'warning_alerts': len([a for a in self.alerts_history if a.alert_level == AlertLevel.WARNING]),
            'info_alerts': len([a for a in self.alerts_history if a.alert_level == AlertLevel.INFO])
        }

    def clear_history(self):
        """Clear alert history"""
        self.alerts_history.clear()
        logger.info("Cleared alert history")


if __name__ == '__main__':
    # Test alert engine
    print("\n" + "="*60)
    print("ALERT ENGINE TEST")
    print("="*60)

    engine = AlertEngine()

    # Test market check
    print("\nChecking markets...")
    alerts = engine.check_markets()
    print(f"✓ Generated {len(alerts)} alerts")

    if alerts:
        print("\nAlerts:")
        for alert in alerts[:3]:
            print(f"\n{alert}")
            print("-" * 40)
            print(alert.message)

    # Test market summary
    print("\n" + "="*60)
    print("Market Summary:")
    print("-" * 60)
    summary = engine.get_market_summary_alert()
    if summary:
        print(summary)

    # Test stats
    print("\n" + "="*60)
    print("Engine Statistics:")
    stats = engine.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("="*60 + "\n")
