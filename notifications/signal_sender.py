"""
Signal Sender
Sends market alerts via Signal using signal-cli
Note: Requires signal-cli to be installed on the system
"""

from typing import Optional, List
from datetime import datetime
import subprocess
import json
from config import settings
from utils.logger import logger
from alerts.alert_engine import Alert


class SignalSender:
    """Signal message sender using signal-cli"""

    def __init__(self):
        """Initialize Signal sender"""
        self.sender_number = getattr(settings, 'SIGNAL_SENDER_NUMBER', None)
        self.recipient_number = getattr(settings, 'SIGNAL_RECIPIENT_NUMBER', None)
        self.signal_cli_path = getattr(settings, 'SIGNAL_CLI_PATH', 'signal-cli')

        # Check if signal-cli is available
        self.available = self._check_signal_cli()

        if not self.sender_number:
            logger.warning("Signal sender number not configured")

        if not self.recipient_number:
            logger.warning("Signal recipient number not configured")

        if self.available and self.sender_number and self.recipient_number:
            logger.info("Signal sender initialized")

        self.messages_sent = 0
        self.last_sent = None

    def _check_signal_cli(self) -> bool:
        """
        Check if signal-cli is installed and accessible

        Returns:
            True if signal-cli is available
        """
        try:
            result = subprocess.run(
                [self.signal_cli_path, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info(f"signal-cli found: {result.stdout.strip()}")
                return True
            else:
                logger.warning("signal-cli not working properly")
                return False
        except FileNotFoundError:
            logger.warning("signal-cli not found. Install from: https://github.com/AsamK/signal-cli")
            return False
        except Exception as e:
            logger.warning(f"Error checking signal-cli: {e}")
            return False

    def send_message(self, message: str, to: Optional[str] = None) -> bool:
        """
        Send a Signal message

        Args:
            message: Message text to send
            to: Recipient phone number (uses settings.SIGNAL_RECIPIENT_NUMBER if None)

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.available:
            logger.error("signal-cli not available")
            return False

        if not self.sender_number:
            logger.error("Signal sender number not configured")
            return False

        if to is None:
            to = self.recipient_number

        if not to:
            logger.error("No Signal recipient number configured")
            return False

        try:
            # Send message via signal-cli
            cmd = [
                self.signal_cli_path,
                '-a', self.sender_number,
                'send',
                '-m', message,
                to
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                logger.info(f"Signal message sent to {to}")
                self.messages_sent += 1
                self.last_sent = datetime.now()
                return True
            else:
                logger.error(f"signal-cli error: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error("Signal send timeout")
            return False

        except Exception as e:
            logger.error(f"Error sending Signal message: {e}", exc_info=True)
            return False

    def send_alert(self, alert: Alert) -> bool:
        """
        Send a single alert via Signal

        Args:
            alert: Alert object

        Returns:
            True if sent successfully
        """
        logger.info(f"Sending Signal alert for {alert.symbol}")

        # Format message for Signal
        message = f"🔔 Market Alert\n\n"
        message += alert.message

        return self.send_message(message)

    def send_alerts(self, alerts: List[Alert], combine: bool = True) -> bool:
        """
        Send multiple alerts via Signal

        Args:
            alerts: List of Alert objects
            combine: If True, combine into single message; if False, send separately

        Returns:
            True if all sent successfully
        """
        if not alerts:
            logger.info("No alerts to send")
            return True

        if combine:
            # Combine alerts into single message
            message = f"🔔 Market Alerts - {len(alerts)} Alert{'s' if len(alerts) > 1 else ''}\n"
            message += f"{datetime.now().strftime('%B %d, %Y at %I:%M %p ET')}\n\n"

            for i, alert in enumerate(alerts, 1):
                message += f"{'='*30}\n"
                message += f"Alert #{i}\n"
                message += f"{'='*30}\n\n"
                message += alert.message + "\n\n"

            return self.send_message(message)

        else:
            # Send each alert separately
            success = True
            for alert in alerts:
                if not self.send_alert(alert):
                    success = False

            return success

    def test_connection(self) -> bool:
        """
        Test Signal connection by sending a test message

        Returns:
            True if test successful
        """
        logger.info("Testing Signal connection...")

        test_message = "✅ Market Alerts - Test Message\n\n"
        test_message += "This is a test message to verify your Signal integration.\n\n"
        test_message += f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        test_message += f"Status: Connection successful!\n\n"
        test_message += "If you received this message, your Market Alerts system is properly configured."

        return self.send_message(test_message)

    def get_stats(self) -> dict:
        """
        Get sender statistics

        Returns:
            Dictionary with statistics
        """
        return {
            'messages_sent': self.messages_sent,
            'last_sent': self.last_sent.isoformat() if self.last_sent else None,
            'configured': self.available and self.sender_number is not None and self.recipient_number is not None,
            'signal_cli_available': self.available,
            'sender_number': self.sender_number,
            'recipient_number': self.recipient_number
        }


# Global sender instance
_sender = None


def get_sender() -> SignalSender:
    """Get global Signal sender instance"""
    global _sender
    if _sender is None:
        _sender = SignalSender()
    return _sender


def send_message(message: str, to: Optional[str] = None) -> bool:
    """
    Send a Signal message (convenience function)

    Args:
        message: Message text
        to: Optional recipient

    Returns:
        True if sent successfully
    """
    sender = get_sender()
    return sender.send_message(message, to)


def send_alert(alert: Alert) -> bool:
    """
    Send a single alert (convenience function)

    Args:
        alert: Alert object

    Returns:
        True if sent successfully
    """
    sender = get_sender()
    return sender.send_alert(alert)


def send_alerts(alerts: List[Alert], combine: bool = True) -> bool:
    """
    Send multiple alerts (convenience function)

    Args:
        alerts: List of Alert objects
        combine: Combine into single message

    Returns:
        True if all sent successfully
    """
    sender = get_sender()
    return sender.send_alerts(alerts, combine)


if __name__ == '__main__':
    # Test Signal sender
    print("\n" + "="*60)
    print("SIGNAL SENDER TEST")
    print("="*60)

    sender = SignalSender()

    # Check configuration
    if not sender.available:
        print("\n❌ signal-cli not available")
        print("   Install from: https://github.com/AsamK/signal-cli")
        print("\n   macOS: brew install signal-cli")
        print("   Linux: See GitHub for installation instructions")
    elif not sender.sender_number or not sender.recipient_number:
        print("\n❌ Signal not configured")
        print("   Please set SIGNAL_SENDER_NUMBER and SIGNAL_RECIPIENT_NUMBER in .env")
    else:
        print("\n✓ Signal sender initialized")
        print(f"  Sender: {sender.sender_number}")
        print(f"  Recipient: {sender.recipient_number}")

        # Test connection
        print("\nTesting Signal connection...")
        print("(This will send a test message to the configured number)")

        user_input = input("\nSend test message? (y/n): ")
        if user_input.lower() == 'y':
            success = sender.test_connection()
            if success:
                print("✓ Test message sent successfully!")
            else:
                print("❌ Failed to send test message")
                print("  Check logs for details")

    # Show stats
    print("\nSender Statistics:")
    stats = sender.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("="*60 + "\n")
