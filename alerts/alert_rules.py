"""
Alert Rules System
Per-stock customizable alert rules with JSON storage
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import json
from pathlib import Path
from utils.logger import logger


class RuleType(Enum):
    """Types of alert rules"""
    PRICE_THRESHOLD = "price_threshold"          # Price crosses above/below value
    PRICE_CHANGE_PERCENT = "price_change_percent"  # % change in 30 min
    VOLUME_SPIKE = "volume_spike"                # Volume spike vs average
    RSI_LEVEL = "rsi_level"                      # RSI oversold/overbought
    MA_CROSSOVER = "ma_crossover"                # MA crossover
    BREAKING_NEWS = "breaking_news"              # News with keywords
    BOLLINGER_BREAKOUT = "bollinger_breakout"    # Price breaks Bollinger Band
    MACD_SIGNAL = "macd_signal"                  # MACD crossover


class RuleCondition(Enum):
    """Rule condition types"""
    ABOVE = "above"
    BELOW = "below"
    CROSSES_ABOVE = "crosses_above"
    CROSSES_BELOW = "crosses_below"
    EQUALS = "equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"


@dataclass
class AlertRule:
    """Individual alert rule"""
    rule_id: str
    symbol: str
    rule_type: RuleType
    condition: RuleCondition
    threshold: float
    enabled: bool = True
    created_at: str = None
    last_triggered: Optional[str] = None
    trigger_count: int = 0
    description: str = ""

    def __post_init__(self):
        """Post initialization"""
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat() + "Z"

        # Convert enum strings back to enums if needed
        if isinstance(self.rule_type, str):
            self.rule_type = RuleType(self.rule_type)
        if isinstance(self.condition, str):
            self.condition = RuleCondition(self.condition)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        d = asdict(self)
        d['rule_type'] = self.rule_type.value
        d['condition'] = self.condition.value
        return d

    @classmethod
    def from_dict(cls, data: Dict) -> 'AlertRule':
        """Create from dictionary"""
        return cls(**data)

    def check_condition(self, current_value: float, previous_value: Optional[float] = None) -> bool:
        """
        Check if rule condition is met

        Args:
            current_value: Current value to check
            previous_value: Previous value (for crossover detection)

        Returns:
            True if condition is met
        """
        try:
            if self.condition == RuleCondition.ABOVE:
                return current_value > self.threshold

            elif self.condition == RuleCondition.BELOW:
                return current_value < self.threshold

            elif self.condition == RuleCondition.CROSSES_ABOVE:
                if previous_value is None:
                    return False
                return previous_value <= self.threshold and current_value > self.threshold

            elif self.condition == RuleCondition.CROSSES_BELOW:
                if previous_value is None:
                    return False
                return previous_value >= self.threshold and current_value < self.threshold

            elif self.condition == RuleCondition.EQUALS:
                # Allow 0.1% tolerance for floating point comparison
                tolerance = abs(self.threshold * 0.001)
                return abs(current_value - self.threshold) <= tolerance

            elif self.condition == RuleCondition.GREATER_THAN:
                return current_value > self.threshold

            elif self.condition == RuleCondition.LESS_THAN:
                return current_value < self.threshold

            return False

        except Exception as e:
            logger.error(f"Error checking condition for rule {self.rule_id}: {e}")
            return False

    def record_trigger(self):
        """Record that this rule was triggered"""
        self.last_triggered = datetime.utcnow().isoformat() + "Z"
        self.trigger_count += 1


class AlertRulesManager:
    """Manage alert rules with JSON storage"""

    def __init__(self, rules_file: str = "config/alert_rules.json"):
        """Initialize rules manager"""
        self.rules_file = Path(rules_file)
        self.rules: Dict[str, AlertRule] = {}
        self._load_rules()

    def _load_rules(self):
        """Load rules from JSON file"""
        try:
            if self.rules_file.exists():
                with open(self.rules_file, 'r') as f:
                    data = json.load(f)

                for rule_data in data.get('rules', []):
                    rule = AlertRule.from_dict(rule_data)
                    self.rules[rule.rule_id] = rule

                logger.info(f"Loaded {len(self.rules)} alert rules from {self.rules_file}")
            else:
                logger.info(f"No rules file found at {self.rules_file}, starting fresh")
                self._save_rules()  # Create empty file

        except Exception as e:
            logger.error(f"Error loading rules: {e}", exc_info=True)
            self.rules = {}

    def _save_rules(self):
        """Save rules to JSON file"""
        try:
            # Ensure directory exists
            self.rules_file.parent.mkdir(parents=True, exist_ok=True)

            # Convert rules to dict
            data = {
                'last_updated': datetime.utcnow().isoformat() + "Z",
                'rules': [rule.to_dict() for rule in self.rules.values()]
            }

            with open(self.rules_file, 'w') as f:
                json.dump(data, f, indent=2)

            logger.debug(f"Saved {len(self.rules)} rules to {self.rules_file}")

        except Exception as e:
            logger.error(f"Error saving rules: {e}", exc_info=True)

    def add_rule(self, rule: AlertRule) -> bool:
        """Add or update a rule"""
        try:
            self.rules[rule.rule_id] = rule
            self._save_rules()
            logger.info(f"Added rule: {rule.rule_id} for {rule.symbol}")
            return True
        except Exception as e:
            logger.error(f"Error adding rule: {e}")
            return False

    def remove_rule(self, rule_id: str) -> bool:
        """Remove a rule"""
        try:
            if rule_id in self.rules:
                rule = self.rules.pop(rule_id)
                self._save_rules()
                logger.info(f"Removed rule: {rule_id} for {rule.symbol}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error removing rule: {e}")
            return False

    def get_rule(self, rule_id: str) -> Optional[AlertRule]:
        """Get a specific rule"""
        return self.rules.get(rule_id)

    def get_rules_for_symbol(self, symbol: str) -> List[AlertRule]:
        """Get all rules for a symbol"""
        return [rule for rule in self.rules.values() if rule.symbol == symbol and rule.enabled]

    def get_all_rules(self) -> List[AlertRule]:
        """Get all rules"""
        return list(self.rules.values())

    def get_enabled_rules(self) -> List[AlertRule]:
        """Get all enabled rules"""
        return [rule for rule in self.rules.values() if rule.enabled]

    def enable_rule(self, rule_id: str) -> bool:
        """Enable a rule"""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = True
            self._save_rules()
            return True
        return False

    def disable_rule(self, rule_id: str) -> bool:
        """Disable a rule"""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = False
            self._save_rules()
            return True
        return False

    def get_rules_by_type(self, rule_type: RuleType) -> List[AlertRule]:
        """Get all rules of a specific type"""
        return [rule for rule in self.rules.values() if rule.rule_type == rule_type and rule.enabled]

    def get_symbols_with_rules(self) -> List[str]:
        """Get list of symbols that have rules"""
        return list(set(rule.symbol for rule in self.rules.values() if rule.enabled))

    def clear_all_rules(self) -> bool:
        """Clear all rules (use with caution!)"""
        try:
            self.rules = {}
            self._save_rules()
            logger.warning("Cleared all alert rules")
            return True
        except Exception as e:
            logger.error(f"Error clearing rules: {e}")
            return False

    def create_default_rules(self, symbols: List[str]) -> int:
        """
        Create default rules for a list of symbols

        Args:
            symbols: List of stock symbols

        Returns:
            Number of rules created
        """
        count = 0

        for symbol in symbols:
            # Price change alert (3% in 30 minutes)
            rule_id = f"{symbol}_price_change_3pct"
            if rule_id not in self.rules:
                rule = AlertRule(
                    rule_id=rule_id,
                    symbol=symbol,
                    rule_type=RuleType.PRICE_CHANGE_PERCENT,
                    condition=RuleCondition.GREATER_THAN,
                    threshold=3.0,
                    description=f"{symbol}: Alert if price moves >3% in 30 minutes"
                )
                self.add_rule(rule)
                count += 1

            # Volume spike alert (2x average)
            rule_id = f"{symbol}_volume_spike_2x"
            if rule_id not in self.rules:
                rule = AlertRule(
                    rule_id=rule_id,
                    symbol=symbol,
                    rule_type=RuleType.VOLUME_SPIKE,
                    condition=RuleCondition.GREATER_THAN,
                    threshold=2.0,
                    description=f"{symbol}: Alert if volume >2x average"
                )
                self.add_rule(rule)
                count += 1

            # RSI oversold alert (below 30)
            rule_id = f"{symbol}_rsi_oversold"
            if rule_id not in self.rules:
                rule = AlertRule(
                    rule_id=rule_id,
                    symbol=symbol,
                    rule_type=RuleType.RSI_LEVEL,
                    condition=RuleCondition.BELOW,
                    threshold=30.0,
                    description=f"{symbol}: Alert if RSI <30 (oversold)"
                )
                self.add_rule(rule)
                count += 1

            # RSI overbought alert (above 70)
            rule_id = f"{symbol}_rsi_overbought"
            if rule_id not in self.rules:
                rule = AlertRule(
                    rule_id=rule_id,
                    symbol=symbol,
                    rule_type=RuleType.RSI_LEVEL,
                    condition=RuleCondition.ABOVE,
                    threshold=70.0,
                    description=f"{symbol}: Alert if RSI >70 (overbought)"
                )
                self.add_rule(rule)
                count += 1

        logger.info(f"Created {count} default rules for {len(symbols)} symbols")
        return count

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about rules"""
        enabled_rules = self.get_enabled_rules()

        stats = {
            'total_rules': len(self.rules),
            'enabled_rules': len(enabled_rules),
            'disabled_rules': len(self.rules) - len(enabled_rules),
            'symbols_with_rules': len(self.get_symbols_with_rules()),
            'rules_by_type': {}
        }

        # Count by type
        for rule_type in RuleType:
            count = len([r for r in enabled_rules if r.rule_type == rule_type])
            if count > 0:
                stats['rules_by_type'][rule_type.value] = count

        return stats


# Global rules manager instance
_rules_manager = None


def get_rules_manager() -> AlertRulesManager:
    """Get global rules manager instance"""
    global _rules_manager
    if _rules_manager is None:
        _rules_manager = AlertRulesManager()
    return _rules_manager


if __name__ == '__main__':
    # Test alert rules system
    print("\n" + "="*60)
    print("ALERT RULES SYSTEM TEST")
    print("="*60)

    manager = AlertRulesManager()

    # Create test rules
    print("\nCreating test rules...")

    rule1 = AlertRule(
        rule_id="AAPL_price_above_300",
        symbol="AAPL",
        rule_type=RuleType.PRICE_THRESHOLD,
        condition=RuleCondition.ABOVE,
        threshold=300.0,
        description="Alert when AAPL crosses above $300"
    )
    manager.add_rule(rule1)

    rule2 = AlertRule(
        rule_id="AAPL_rsi_oversold",
        symbol="AAPL",
        rule_type=RuleType.RSI_LEVEL,
        condition=RuleCondition.BELOW,
        threshold=30.0,
        description="Alert when AAPL RSI <30"
    )
    manager.add_rule(rule2)

    print(f"✓ Created {len(manager.rules)} rules")

    # Test condition checking
    print("\nTesting conditions:")
    print(f"  AAPL at $305 (threshold $300, ABOVE): {rule1.check_condition(305.0)}")
    print(f"  AAPL at $295 (threshold $300, ABOVE): {rule1.check_condition(295.0)}")
    print(f"  RSI at 25 (threshold 30, BELOW): {rule2.check_condition(25.0)}")
    print(f"  RSI at 35 (threshold 30, BELOW): {rule2.check_condition(35.0)}")

    # Get stats
    print("\nRule Statistics:")
    stats = manager.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n" + "="*60 + "\n")
