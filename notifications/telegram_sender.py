"""
Telegram Sender
Sends market alerts via Telegram using python-telegram-bot
"""

from typing import Optional, List
from datetime import datetime
import asyncio
from telegram import Bot
from telegram.error import TelegramError
from config import settings
from utils.logger import logger
from alerts.alert_engine import Alert


class TelegramSender:
    """Telegram message sender using python-telegram-bot"""

    def __init__(self):
        """Initialize Telegram bot"""
        self.bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        self.chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', None)

        if not self.bot_token:
            logger.warning("Telegram bot token not configured")
            self.bot = None
        else:
            self.bot = Bot(token=self.bot_token)
            logger.info("Telegram bot initialized")

        self.messages_sent = 0
        self.last_sent = None

    async def _send_message_async(self, message: str, chat_id: Optional[str] = None) -> bool:
        """
        Send a Telegram message asynchronously

        Args:
            message: Message text to send
            chat_id: Recipient chat ID (uses settings.TELEGRAM_CHAT_ID if None)

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.bot:
            logger.error("Telegram bot not initialized - check bot token")
            return False

        if chat_id is None:
            chat_id = self.chat_id

        if not chat_id:
            logger.error("No Telegram chat ID configured")
            return False

        try:
            # Send message via Telegram
            msg = await self.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode='Markdown'
            )

            logger.info(f"Telegram message sent: message_id={msg.message_id}")
            self.messages_sent += 1
            self.last_sent = datetime.now()

            return True

        except TelegramError as e:
            logger.error(f"Telegram API error: {e}")
            return False

        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}", exc_info=True)
            return False

    def send_message(self, message: str, chat_id: Optional[str] = None) -> bool:
        """
        Send a Telegram message (synchronous wrapper)

        Args:
            message: Message text to send
            chat_id: Recipient chat ID (uses settings.TELEGRAM_CHAT_ID if None)

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Run async function in event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self._send_message_async(message, chat_id))
            loop.close()
            return result
        except Exception as e:
            logger.error(f"Error in send_message: {e}", exc_info=True)
            return False

    def send_alert(self, alert: Alert) -> bool:
        """
        Send a single alert via Telegram

        Args:
            alert: Alert object

        Returns:
            True if sent successfully
        """
        logger.info(f"Sending Telegram alert for {alert.symbol}")

        # Format message with Telegram markdown
        message = f"🔔 *Market Alert*\n\n"
        message += alert.message.replace('**', '*')  # Convert double asterisks to single for Telegram

        return self.send_message(message)

    def send_alerts(self, alerts: List[Alert], combine: bool = True) -> bool:
        """
        Send multiple alerts via Telegram

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
                # Convert alert message formatting
                alert_msg = alert.message.replace('**', '*')
                message += alert_msg + "\n\n"

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
        Test Telegram connection by sending a test message

        Returns:
            True if test successful
        """
        logger.info("Testing Telegram connection...")

        test_message = "✅ *Market Alerts - Test Message*\n\n"
        test_message += "This is a test message to verify your Telegram integration.\n\n"
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
            'configured': self.bot is not None,
            'chat_id': self.chat_id
        }


# Global sender instance
_sender = None


def get_sender() -> TelegramSender:
    """Get global Telegram sender instance"""
    global _sender
    if _sender is None:
        _sender = TelegramSender()
    return _sender


def send_message(message: str, chat_id: Optional[str] = None) -> bool:
    """
    Send a Telegram message (convenience function)

    Args:
        message: Message text
        chat_id: Optional recipient

    Returns:
        True if sent successfully
    """
    sender = get_sender()
    return sender.send_message(message, chat_id)


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
    # Test Telegram sender
    print("\n" + "="*60)
    print("TELEGRAM SENDER TEST")
    print("="*60)

    sender = TelegramSender()

    # Check configuration
    if not sender.bot:
        print("\n❌ Telegram not configured")
        print("   Please set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env")
    else:
        print("\n✓ Telegram bot initialized")
        print(f"  Chat ID: {sender.chat_id}")

        # Test connection
        print("\nTesting Telegram connection...")
        print("(This will send a test message to the configured chat)")

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
