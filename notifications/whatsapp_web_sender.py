"""
WhatsApp Web Sender
Sends market alerts via WhatsApp Web using pywhatkit
Note: Requires WhatsApp Web to be logged in on the browser
"""

from typing import Optional, List
from datetime import datetime
import pywhatkit as kit
from config import settings
from utils.logger import logger
from alerts.alert_engine import Alert


class WhatsAppWebSender:
    """WhatsApp message sender using pywhatkit (WhatsApp Web automation)"""

    def __init__(self):
        """Initialize WhatsApp Web sender"""
        self.recipient_phone = getattr(settings, 'WHATSAPP_WEB_RECIPIENT', None)
        self.wait_time = getattr(settings, 'WHATSAPP_WEB_WAIT_TIME', 15)  # Wait time in seconds
        self.close_tab = getattr(settings, 'WHATSAPP_WEB_CLOSE_TAB', True)  # Close tab after sending

        if not self.recipient_phone:
            logger.warning("WhatsApp Web recipient number not configured")
        else:
            logger.info("WhatsApp Web sender initialized")

        self.messages_sent = 0
        self.last_sent = None

    def send_message(self, message: str, to: Optional[str] = None) -> bool:
        """
        Send a WhatsApp message via WhatsApp Web

        Args:
            message: Message text to send
            to: Recipient phone number with country code (e.g., +1234567890)
                Uses settings.WHATSAPP_WEB_RECIPIENT if None

        Returns:
            True if sent successfully, False otherwise
        """
        if to is None:
            to = self.recipient_phone

        if not to:
            logger.error("No WhatsApp Web recipient phone number configured")
            return False

        try:
            # Get current time and add 2 minutes for scheduling
            now = datetime.now()
            hour = now.hour
            minute = now.minute + 2

            # Handle minute overflow
            if minute >= 60:
                hour = (hour + 1) % 24
                minute = minute - 60

            logger.info(f"Scheduling WhatsApp message to {to} at {hour:02d}:{minute:02d}")

            # Send message using pywhatkit
            # This will open WhatsApp Web in browser and send the message
            kit.sendwhatmsg(
                phone_no=to,
                message=message,
                time_hour=hour,
                time_min=minute,
                wait_time=self.wait_time,
                tab_close=self.close_tab
            )

            logger.info(f"WhatsApp Web message sent to {to}")
            self.messages_sent += 1
            self.last_sent = datetime.now()

            return True

        except Exception as e:
            logger.error(f"Error sending WhatsApp Web message: {e}", exc_info=True)
            return False

    def send_instant(self, message: str, to: Optional[str] = None) -> bool:
        """
        Send an instant WhatsApp message (opens WhatsApp Web but doesn't auto-send)

        Args:
            message: Message text to send
            to: Recipient phone number with country code

        Returns:
            True if WhatsApp Web opened successfully
        """
        if to is None:
            to = self.recipient_phone

        if not to:
            logger.error("No WhatsApp Web recipient phone number configured")
            return False

        try:
            logger.info(f"Opening WhatsApp Web for instant message to {to}")

            # Open WhatsApp Web with message ready (user needs to click send)
            kit.sendwhatmsg_instantly(
                phone_no=to,
                message=message,
                wait_time=self.wait_time,
                tab_close=False  # Keep tab open for manual sending
            )

            logger.info(f"WhatsApp Web opened for {to}")
            self.messages_sent += 1
            self.last_sent = datetime.now()

            return True

        except Exception as e:
            logger.error(f"Error opening WhatsApp Web: {e}", exc_info=True)
            return False

    def send_alert(self, alert: Alert) -> bool:
        """
        Send a single alert via WhatsApp Web

        Args:
            alert: Alert object

        Returns:
            True if sent successfully
        """
        logger.info(f"Sending WhatsApp Web alert for {alert.symbol}")

        # Format message for WhatsApp
        message = f"🔔 *Market Alert*\n\n"
        message += alert.message

        return self.send_message(message)

    def send_alerts(self, alerts: List[Alert], combine: bool = True) -> bool:
        """
        Send multiple alerts via WhatsApp Web

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
            message = f"🔔 *Market Alerts - {len(alerts)} Alert{'s' if len(alerts) > 1 else ''}*\n"
            message += f"_{datetime.now().strftime('%B %d, %Y at %I:%M %p ET')}_\n\n"

            for i, alert in enumerate(alerts, 1):
                message += f"━━━━━━━━━━━━━━━━━\n"
                message += f"*Alert #{i}*\n"
                message += f"━━━━━━━━━━━━━━━━━\n\n"
                message += alert.message + "\n\n"

            return self.send_message(message)

        else:
            # Send each alert separately
            # Note: This will open multiple browser tabs with delays
            success = True
            for i, alert in enumerate(alerts):
                if i > 0:
                    # Add delay between messages to avoid conflicts
                    import time
                    time.sleep(5)
                if not self.send_alert(alert):
                    success = False

            return success

    def test_connection(self) -> bool:
        """
        Test WhatsApp Web connection by sending a test message

        Returns:
            True if test successful
        """
        logger.info("Testing WhatsApp Web connection...")

        test_message = "✅ *Market Alerts - Test Message*\n\n"
        test_message += "This is a test message to verify your WhatsApp Web integration.\n\n"
        test_message += f"*Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        test_message += f"*Status:* Connection successful!\n\n"
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
            'configured': self.recipient_phone is not None,
            'recipient_phone': self.recipient_phone,
            'wait_time': self.wait_time,
            'close_tab': self.close_tab
        }


# Global sender instance
_sender = None


def get_sender() -> WhatsAppWebSender:
    """Get global WhatsApp Web sender instance"""
    global _sender
    if _sender is None:
        _sender = WhatsAppWebSender()
    return _sender


def send_message(message: str, to: Optional[str] = None) -> bool:
    """
    Send a WhatsApp Web message (convenience function)

    Args:
        message: Message text
        to: Optional recipient

    Returns:
        True if sent successfully
    """
    sender = get_sender()
    return sender.send_message(message, to)


def send_instant(message: str, to: Optional[str] = None) -> bool:
    """
    Send an instant WhatsApp Web message (convenience function)

    Args:
        message: Message text
        to: Optional recipient

    Returns:
        True if WhatsApp Web opened successfully
    """
    sender = get_sender()
    return sender.send_instant(message, to)


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
    # Test WhatsApp Web sender
    print("\n" + "="*60)
    print("WHATSAPP WEB SENDER TEST")
    print("="*60)
    print("\n⚠️  IMPORTANT:")
    print("   1. Make sure WhatsApp Web is logged in on your default browser")
    print("   2. This will open a browser tab and send the message automatically")
    print("   3. Do not use your mouse/keyboard until the message is sent")
    print()

    sender = WhatsAppWebSender()

    # Check configuration
    if not sender.recipient_phone:
        print("\n❌ WhatsApp Web not configured")
        print("   Please set WHATSAPP_WEB_RECIPIENT in .env")
        print("   Format: +1234567890 (with country code)")
    else:
        print("\n✓ WhatsApp Web sender initialized")
        print(f"  Recipient: {sender.recipient_phone}")
        print(f"  Wait time: {sender.wait_time} seconds")

        # Test connection
        print("\nTesting WhatsApp Web connection...")
        print("(This will open WhatsApp Web and send a test message)")

        user_input = input("\nSend test message? (y/n): ")
        if user_input.lower() == 'y':
            print("\n⏳ Opening WhatsApp Web in 2 minutes...")
            print("   Please do not use your computer until the message is sent!")

            success = sender.test_connection()
            if success:
                print("\n✓ Test message scheduled successfully!")
                print("  The message will be sent automatically")
            else:
                print("\n❌ Failed to send test message")
                print("  Check logs for details")

    # Show stats
    print("\nSender Statistics:")
    stats = sender.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("="*60 + "\n")
