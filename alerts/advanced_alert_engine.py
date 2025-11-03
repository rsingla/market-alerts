"""
Advanced Alert Rules Engine
Evaluates custom per-stock alert rules and generates beautiful alert messages
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime
from data.market_data import get_stock_quote, get_market_summary, StockQuote
from data.technical_indicators import get_technical_analysis
from data.news_fetcher import get_market_news
from alerts.alert_rules import AlertRule, RuleType, get_rules_manager
from alerts.alert_templates import AlertTemplates
from utils.logger import logger


class AdvancedAlertEngine:
    """Advanced alert engine with custom rule evaluation"""

    def __init__(self):
        """Initialize advanced alert engine"""
        self.rules_manager = get_rules_manager()
        self.alert_cache = {}  # Cache to prevent duplicate alerts
        logger.info("Advanced Alert Engine initialized")

    def evaluate_all_rules(self) -> List[Dict]:
        """
        Evaluate all enabled rules and generate alerts

        Returns:
            List of alert dictionaries with messages
        """
        alerts = []

        try:
            # Get all enabled rules
            rules = self.rules_manager.get_enabled_rules()

            if not rules:
                logger.info("No enabled rules to evaluate")
                return alerts

            logger.info(f"Evaluating {len(rules)} enabled rules")

            # Group rules by symbol for efficient data fetching
            rules_by_symbol = {}
            for rule in rules:
                if rule.symbol not in rules_by_symbol:
                    rules_by_symbol[rule.symbol] = []
                rules_by_symbol[rule.symbol].append(rule)

            # Evaluate rules for each symbol
            for symbol, symbol_rules in rules_by_symbol.items():
                try:
                    symbol_alerts = self._evaluate_symbol_rules(symbol, symbol_rules)
                    alerts.extend(symbol_alerts)
                except Exception as e:
                    logger.error(f"Error evaluating rules for {symbol}: {e}", exc_info=True)

            logger.info(f"Generated {len(alerts)} alerts from rule evaluation")

        except Exception as e:
            logger.error(f"Error in evaluate_all_rules: {e}", exc_info=True)

        return alerts

    def _evaluate_symbol_rules(self, symbol: str, rules: List[AlertRule]) -> List[Dict]:
        """
        Evaluate all rules for a specific symbol

        Args:
            symbol: Stock ticker
            rules: List of rules for this symbol

        Returns:
            List of alert dictionaries
        """
        alerts = []

        try:
            # Fetch data needed for this symbol
            quote = get_stock_quote(symbol)
            if not quote:
                logger.warning(f"No quote data for {symbol}, skipping rules")
                return alerts

            # Fetch technical indicators (for RSI, MA, Bollinger, MACD rules)
            technical_data = None
            needs_technical = any(r.rule_type in [
                RuleType.RSI_LEVEL,
                RuleType.MA_CROSSOVER,
                RuleType.BOLLINGER_BREAKOUT,
                RuleType.MACD_SIGNAL
            ] for r in rules)

            if needs_technical:
                technical_data = get_technical_analysis(symbol, period='3mo')

            # Evaluate each rule
            for rule in rules:
                try:
                    alert = self._evaluate_rule(rule, quote, technical_data)
                    if alert:
                        alerts.append(alert)
                        # Record that rule was triggered
                        rule.record_trigger()
                        self.rules_manager.add_rule(rule)  # Save updated trigger count

                except Exception as e:
                    logger.error(f"Error evaluating rule {rule.rule_id}: {e}")

        except Exception as e:
            logger.error(f"Error evaluating symbol {symbol}: {e}", exc_info=True)

        return alerts

    def _evaluate_rule(self, rule: AlertRule, quote: StockQuote, technical_data: Optional[Dict]) -> Optional[Dict]:
        """
        Evaluate a single rule

        Args:
            rule: AlertRule to evaluate
            quote: Stock quote data
            technical_data: Technical indicators data (optional)

        Returns:
            Alert dictionary if rule triggered, None otherwise
        """
        try:
            # Check cache to avoid duplicate alerts within same session
            cache_key = f"{rule.rule_id}_{datetime.now().strftime('%Y%m%d_%H')}"
            if cache_key in self.alert_cache:
                return None

            triggered = False
            alert_message = None

            # Evaluate based on rule type
            if rule.rule_type == RuleType.PRICE_THRESHOLD:
                triggered, alert_message = self._check_price_threshold(rule, quote)

            elif rule.rule_type == RuleType.PRICE_CHANGE_PERCENT:
                triggered, alert_message = self._check_price_change_percent(rule, quote)

            elif rule.rule_type == RuleType.VOLUME_SPIKE:
                triggered, alert_message = self._check_volume_spike(rule, quote)

            elif rule.rule_type == RuleType.RSI_LEVEL:
                triggered, alert_message = self._check_rsi_level(rule, quote, technical_data)

            elif rule.rule_type == RuleType.MA_CROSSOVER:
                triggered, alert_message = self._check_ma_crossover(rule, quote, technical_data)

            elif rule.rule_type == RuleType.BOLLINGER_BREAKOUT:
                triggered, alert_message = self._check_bollinger_breakout(rule, quote, technical_data)

            elif rule.rule_type == RuleType.MACD_SIGNAL:
                triggered, alert_message = self._check_macd_signal(rule, quote, technical_data)

            elif rule.rule_type == RuleType.BREAKING_NEWS:
                triggered, alert_message = self._check_breaking_news(rule, quote)

            if triggered and alert_message:
                # Cache this alert
                self.alert_cache[cache_key] = True

                return {
                    'rule_id': rule.rule_id,
                    'symbol': rule.symbol,
                    'rule_type': rule.rule_type.value,
                    'messages': alert_message,
                    'timestamp': datetime.now().isoformat()
                }

            return None

        except Exception as e:
            logger.error(f"Error in _evaluate_rule for {rule.rule_id}: {e}")
            return None

    def _check_price_threshold(self, rule: AlertRule, quote: StockQuote) -> Tuple[bool, Optional[Dict]]:
        """Check price threshold rule"""
        current_price = quote.price

        if rule.check_condition(current_price):
            direction = "above" if rule.condition.value in ["above", "crosses_above", "greater_than"] else "below"
            messages = AlertTemplates.price_threshold_alert(
                rule.symbol,
                current_price,
                rule.threshold,
                direction
            )
            return True, messages

        return False, None

    def _check_price_change_percent(self, rule: AlertRule, quote: StockQuote) -> Tuple[bool, Optional[Dict]]:
        """Check price change percent rule"""
        change_percent = abs(quote.change_percent)

        if rule.check_condition(change_percent):
            messages = AlertTemplates.price_change_percent_alert(
                rule.symbol,
                quote.price,
                quote.change_percent,
                "30-minute"
            )
            return True, messages

        return False, None

    def _check_volume_spike(self, rule: AlertRule, quote: StockQuote) -> Tuple[bool, Optional[Dict]]:
        """Check volume spike rule"""
        volume_ratio = quote.volume_ratio

        if rule.check_condition(volume_ratio):
            messages = AlertTemplates.volume_spike_alert(
                rule.symbol,
                quote.price,
                quote.volume,
                quote.avg_volume,
                volume_ratio
            )
            return True, messages

        return False, None

    def _check_rsi_level(self, rule: AlertRule, quote: StockQuote, technical_data: Optional[Dict]) -> Tuple[bool, Optional[Dict]]:
        """Check RSI level rule"""
        if not technical_data or 'latest' not in technical_data:
            return False, None

        rsi = technical_data['latest'].get('rsi')
        if rsi is None:
            return False, None

        if rule.check_condition(rsi):
            condition = "oversold" if rsi < 30 else "overbought" if rsi > 70 else "neutral"
            messages = AlertTemplates.rsi_alert(
                rule.symbol,
                quote.price,
                rsi,
                condition
            )
            return True, messages

        return False, None

    def _check_ma_crossover(self, rule: AlertRule, quote: StockQuote, technical_data: Optional[Dict]) -> Tuple[bool, Optional[Dict]]:
        """Check moving average crossover rule"""
        if not technical_data or 'latest' not in technical_data:
            return False, None

        # Determine which MA to check based on threshold (50 or 200)
        ma_period = int(rule.threshold)
        if ma_period == 50:
            ma_value = technical_data['latest'].get('sma_50')
        elif ma_period == 200:
            ma_value = technical_data['latest'].get('sma_200')
        else:
            return False, None

        if ma_value is None:
            return False, None

        current_price = quote.price

        # Simple check: is price above or below MA?
        if rule.condition.value in ["above", "crosses_above"]:
            if current_price > ma_value:
                messages = AlertTemplates.ma_crossover_alert(
                    rule.symbol,
                    current_price,
                    "SMA",
                    ma_period,
                    "above"
                )
                return True, messages
        elif rule.condition.value in ["below", "crosses_below"]:
            if current_price < ma_value:
                messages = AlertTemplates.ma_crossover_alert(
                    rule.symbol,
                    current_price,
                    "SMA",
                    ma_period,
                    "below"
                )
                return True, messages

        return False, None

    def _check_bollinger_breakout(self, rule: AlertRule, quote: StockQuote, technical_data: Optional[Dict]) -> Tuple[bool, Optional[Dict]]:
        """Check Bollinger Band breakout rule"""
        if not technical_data or 'latest' not in technical_data:
            return False, None

        bb_upper = technical_data['latest'].get('bb_upper')
        bb_lower = technical_data['latest'].get('bb_lower')
        current_price = quote.price

        if bb_upper is None or bb_lower is None:
            return False, None

        # Check upper band breakout
        if current_price > bb_upper:
            messages = AlertTemplates.bollinger_breakout_alert(
                rule.symbol,
                current_price,
                "upper",
                bb_upper
            )
            return True, messages

        # Check lower band breakout
        if current_price < bb_lower:
            messages = AlertTemplates.bollinger_breakout_alert(
                rule.symbol,
                current_price,
                "lower",
                bb_lower
            )
            return True, messages

        return False, None

    def _check_macd_signal(self, rule: AlertRule, quote: StockQuote, technical_data: Optional[Dict]) -> Tuple[bool, Optional[Dict]]:
        """Check MACD signal rule"""
        if not technical_data or 'latest' not in technical_data:
            return False, None

        macd_line = technical_data['latest'].get('macd')
        signal_line = technical_data['latest'].get('macd_signal')

        if macd_line is None or signal_line is None:
            return False, None

        # Bullish crossover: MACD > Signal
        if macd_line > signal_line and rule.condition.value in ["above", "crosses_above"]:
            messages = AlertTemplates.macd_signal_alert(
                rule.symbol,
                quote.price,
                macd_line,
                signal_line,
                "bullish"
            )
            return True, messages

        # Bearish crossover: MACD < Signal
        if macd_line < signal_line and rule.condition.value in ["below", "crosses_below"]:
            messages = AlertTemplates.macd_signal_alert(
                rule.symbol,
                quote.price,
                macd_line,
                signal_line,
                "bearish"
            )
            return True, messages

        return False, None

    def _check_breaking_news(self, rule: AlertRule, quote: StockQuote) -> Tuple[bool, Optional[Dict]]:
        """Check breaking news rule"""
        try:
            # Fetch recent news for symbol
            news = get_market_news(query=rule.symbol, max_items=5)

            if not news:
                return False, None

            # Check for high-impact keywords
            important_keywords = ['earnings', 'fed', 'acquisition', 'merger', 'bankruptcy', 'lawsuit', 'fda', 'approval']

            for article in news:
                title = article.get('title', '').lower()
                description = article.get('description', '').lower()
                content = f"{title} {description}"

                # Check if any important keyword is in the content
                matched_keywords = [kw for kw in important_keywords if kw in content]

                if matched_keywords:
                    messages = AlertTemplates.breaking_news_alert(
                        rule.symbol,
                        article['title'],
                        article.get('source', {}).get('name', 'Unknown'),
                        matched_keywords
                    )
                    return True, messages

            return False, None

        except Exception as e:
            logger.error(f"Error checking breaking news for {rule.symbol}: {e}")
            return False, None

    def generate_hourly_summary(self) -> Optional[Dict]:
        """
        Generate hourly watchlist summary

        Returns:
            Dictionary with summary messages
        """
        try:
            quotes = get_market_summary()

            if not quotes:
                return None

            # Calculate top gainers and losers
            sorted_quotes = sorted(quotes.values(), key=lambda q: q.change_percent, reverse=True)

            top_gainers = [
                {
                    'symbol': q.symbol,
                    'price': q.price,
                    'change_pct': q.change_percent
                }
                for q in sorted_quotes[:3] if q.change_percent > 0
            ]

            top_losers = [
                {
                    'symbol': q.symbol,
                    'price': q.price,
                    'change_pct': q.change_percent
                }
                for q in sorted_quotes[-3:] if q.change_percent < 0
            ]
            top_losers.reverse()  # Show worst first

            from utils.market_hours import get_market_status
            market_status_data = get_market_status()
            market_status = "Open" if market_status_data.get('is_market_hours') else "Closed"

            stats = {
                'top_gainers': top_gainers,
                'top_losers': top_losers,
                'total_symbols': len(quotes),
                'market_status': market_status
            }

            messages = AlertTemplates.hourly_summary(stats)

            return {
                'type': 'hourly_summary',
                'messages': messages,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error generating hourly summary: {e}", exc_info=True)
            return None

    def clear_alert_cache(self):
        """Clear the alert cache (call this at start of new day)"""
        self.alert_cache.clear()
        logger.info("Alert cache cleared")

    def get_stats(self) -> Dict:
        """Get engine statistics"""
        return {
            'enabled_rules': len(self.rules_manager.get_enabled_rules()),
            'symbols_with_rules': len(self.rules_manager.get_symbols_with_rules()),
            'cached_alerts': len(self.alert_cache),
            'rules_stats': self.rules_manager.get_stats()
        }


# Global engine instance
_advanced_engine = None


def get_advanced_engine() -> AdvancedAlertEngine:
    """Get global advanced engine instance"""
    global _advanced_engine
    if _advanced_engine is None:
        _advanced_engine = AdvancedAlertEngine()
    return _advanced_engine


if __name__ == '__main__':
    # Test advanced alert engine
    print("\n" + "="*60)
    print("ADVANCED ALERT ENGINE TEST")
    print("="*60)

    engine = AdvancedAlertEngine()

    # Create some test rules
    print("\nCreating test rules...")
    from alerts.alert_rules import AlertRule, RuleType, RuleCondition

    # Price threshold rule for AAPL
    rule = AlertRule(
        rule_id="test_aapl_price",
        symbol="AAPL",
        rule_type=RuleType.PRICE_THRESHOLD,
        condition=RuleCondition.ABOVE,
        threshold=250.0,  # Set low threshold for testing
        description="Test: AAPL above $250"
    )
    engine.rules_manager.add_rule(rule)

    # Evaluate all rules
    print("\nEvaluating all rules...")
    alerts = engine.evaluate_all_rules()

    if alerts:
        print(f"\n✓ Generated {len(alerts)} alerts:")
        for alert in alerts:
            print(f"\n{'-'*60}")
            print(f"Symbol: {alert['symbol']}")
            print(f"Type: {alert['rule_type']}")
            print(f"\nWhatsApp Message:")
            print(alert['messages']['whatsapp'])
    else:
        print("\nNo alerts triggered")

    # Show stats
    print("\n" + "="*60)
    print("Engine Statistics:")
    stats = engine.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n" + "="*60 + "\n")
