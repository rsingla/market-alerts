"""
WhatsApp Sender
Sends alerts via WhatsApp using Twilio API
"""

from typing import Optional, List
from datetime import datetime
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from config import settings
from utils.logger import logger
from alerts.alert_engine import Alert


class WhatsAppSender:
    """WhatsApp message sender using Twilio"""

    def __init__(self):
        """Initialize Twilio client"""
        if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
            logger.warning("Twilio credentials not configured")
            self.client = None
        else:
            self.client = Client(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )
            logger.info("Twilio WhatsApp client initialized")

        self.messages_sent = 0
        self.last_sent = None

    def send_message(self, message: str, to: Optional[str] = None) -> bool:
        """
        Send a WhatsApp message

        Args:
            message: Message text to send
            to: Recipient phone number (uses settings.TWILIO_WHATSAPP_TO if None)

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.client:
            logger.error("Twilio client not initialized - check credentials")
            return False

        if to is None:
            to = settings.TWILIO_WHATSAPP_TO

        if not to:
            logger.error("No recipient phone number configured")
            return False

        try:
            # Send message via Twilio
            tw_message = self.client.messages.create(
                from_=settings.TWILIO_WHATSAPP_FROM,
                body=message,
                to=to
            )

            logger.info(f"WhatsApp message sent: SID={tw_message.sid}, Status={tw_message.status}")
            self.messages_sent += 1
            self.last_sent = datetime.now()

            return True

        except TwilioRestException as e:
            logger.error(f"Twilio API error: {e.code} - {e.msg}")
            return False

        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {e}", exc_info=True)
            return False

    def send_alert(self, alert: Alert) -> bool:
        """
        Send a single alert

        Args:
            alert: Alert object

        Returns:
            True if sent successfully
        """
        logger.info(f"Sending alert for {alert.symbol}")
        return self.send_message(alert.message)

    def send_alerts(self, alerts: List[Alert], combine: bool = True) -> bool:
        """
        Send multiple alerts

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
            message = "🔔 *Market Alerts*\n"
            message += f"_{datetime.now().strftime('%B %d, %Y at %I:%M %p ET')}_\n\n"

            for alert in alerts:
                message += f"{alert.message}\n\n"
                message += "-" * 30 + "\n\n"

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
        Test WhatsApp connection by sending a test message

        Returns:
            True if test successful
        """
        logger.info("Testing WhatsApp connection...")

        test_message = "✅ *Market Alerts - Test Message*\n\n"
        test_message += "This is a test message to verify WhatsApp integration.\n\n"
        test_message += f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        test_message += f"Status: Connection successful!"

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
            'configured': self.client is not None
        }


# Global sender instance
_sender = None


def get_sender() -> WhatsAppSender:
    """Get global WhatsApp sender instance"""
    global _sender
    if _sender is None:
        _sender = WhatsAppSender()
    return _sender


def send_message(message: str, to: Optional[str] = None) -> bool:
    """
    Send a WhatsApp message (convenience function)

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
    # Test WhatsApp sender
    print("\n" + "="*60)
    print("WHATSAPP SENDER TEST")
    print("="*60)

    sender = WhatsAppSender()

    # Check configuration
    if not sender.client:
        print("\n❌ Twilio not configured")
        print("   Please set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN in .env")
    else:
        print("\n✓ Twilio client initialized")

        # Test connection
        print("\nTesting WhatsApp connection...")
        print("(This will send a test message to the configured phone number)")

        user_input = input("\nSend test message? (y/n): ")
        if user_input.lower() == 'y':
            success = sender.test_connection()
            if success:
                print("✓ Test message sent successfully!")
            else:
                print("❌ Failed to send test message")

    # Show stats
    print("\nSender Statistics:")
    stats = sender.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("="*60 + "\n")
