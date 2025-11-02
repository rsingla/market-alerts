"""
Notifications Module
Handles sending alerts via multiple channels: Email, Telegram, Signal, WhatsApp (Twilio), and WhatsApp Web
"""

from .whatsapp_sender import WhatsAppSender
from .email_sender import EmailSender
from .telegram_sender import TelegramSender
from .signal_sender import SignalSender
from .whatsapp_web_sender import WhatsAppWebSender
import os

# Priority order for notification channels (first available is used)
CHANNEL_PRIORITY = [
    'email',      # Brevo (easiest, most reliable)
    'telegram',   # Second easiest (just need bot token)
    'signal',     # Requires signal-cli installation
    'whatsapp',   # Twilio (requires credentials and sandbox setup)
    'whatsapp_web'  # Browser automation (least reliable, requires logged-in browser)
]


def get_notification_sender():
    """
    Get the appropriate notification sender based on configuration
    Checks channels in priority order and returns the first available
    """
    from config import settings

    # 1. Check Email (Brevo) - Highest priority
    if hasattr(settings, 'BREVO_API_KEY'):
        api_key = getattr(settings, 'BREVO_API_KEY', None)
        recipient = getattr(settings, 'RECIPIENT_EMAIL', None)
        if api_key and api_key != 'your_brevo_api_key' and recipient:
            from .email_sender import get_sender
            from utils.logger import logger
            logger.info("Using Email (Brevo) for notifications")
            return get_sender()

    # 2. Check Telegram - Second priority
    if hasattr(settings, 'TELEGRAM_BOT_TOKEN'):
        bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', None)
        if bot_token and chat_id:
            from .telegram_sender import get_sender
            from utils.logger import logger
            logger.info("Using Telegram for notifications")
            return get_sender()

    # 3. Check Signal - Third priority
    if hasattr(settings, 'SIGNAL_SENDER_NUMBER'):
        sender_num = getattr(settings, 'SIGNAL_SENDER_NUMBER', None)
        recipient_num = getattr(settings, 'SIGNAL_RECIPIENT_NUMBER', None)
        if sender_num and recipient_num:
            from .signal_sender import get_sender
            sender = get_sender()
            if sender.available:
                from utils.logger import logger
                logger.info("Using Signal for notifications")
                return sender

    # 4. Check WhatsApp (Twilio) - Fourth priority
    if hasattr(settings, 'TWILIO_ACCOUNT_SID'):
        account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
        auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
        to_number = getattr(settings, 'TWILIO_WHATSAPP_TO', None)
        if account_sid and auth_token and to_number:
            from .whatsapp_sender import WhatsAppSender
            from utils.logger import logger
            logger.info("Using WhatsApp (Twilio) for notifications")
            return WhatsAppSender()

    # 5. Check WhatsApp Web - Lowest priority
    if hasattr(settings, 'WHATSAPP_WEB_RECIPIENT'):
        recipient = getattr(settings, 'WHATSAPP_WEB_RECIPIENT', None)
        if recipient:
            from .whatsapp_web_sender import get_sender
            from utils.logger import logger
            logger.info("Using WhatsApp Web for notifications")
            return get_sender()

    # No notification channel configured
    from utils.logger import logger
    logger.warning("No notification channel configured! Please configure at least one notification method.")
    return None


def send_alert(alert):
    """Send a single alert using configured method"""
    sender = get_notification_sender()
    if sender is None:
        return False
    return sender.send_alert(alert)


def send_alerts(alerts, combine=True):
    """Send multiple alerts using configured method"""
    sender = get_notification_sender()
    if sender is None:
        return False
    return sender.send_alerts(alerts, combine)


def send_message(message, to=None):
    """Send a message using configured method"""
    sender = get_notification_sender()
    if sender is None:
        return False

    # Handle different sender types
    if hasattr(sender, 'send_email'):
        return sender.send_email("Market Alert", message, to)
    else:
        return sender.send_message(message, to)


def get_available_channels():
    """
    Get list of available notification channels

    Returns:
        List of tuples: (channel_name, is_configured, details)
    """
    from config import settings
    channels = []

    # Email (Brevo)
    brevo_key = getattr(settings, 'BREVO_API_KEY', None)
    recipient_email = getattr(settings, 'RECIPIENT_EMAIL', None)
    channels.append((
        'email',
        bool(brevo_key and brevo_key != 'your_brevo_api_key' and recipient_email),
        f"Email to {recipient_email}" if recipient_email else "Not configured"
    ))

    # Telegram
    telegram_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    telegram_chat = getattr(settings, 'TELEGRAM_CHAT_ID', None)
    channels.append((
        'telegram',
        bool(telegram_token and telegram_chat),
        f"Telegram chat {telegram_chat}" if telegram_chat else "Not configured"
    ))

    # Signal
    signal_sender = getattr(settings, 'SIGNAL_SENDER_NUMBER', None)
    signal_recipient = getattr(settings, 'SIGNAL_RECIPIENT_NUMBER', None)
    signal_configured = bool(signal_sender and signal_recipient)
    if signal_configured:
        from .signal_sender import SignalSender
        signal_obj = SignalSender()
        signal_configured = signal_obj.available
    channels.append((
        'signal',
        signal_configured,
        f"Signal to {signal_recipient}" if signal_recipient else "Not configured"
    ))

    # WhatsApp (Twilio)
    twilio_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
    twilio_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
    twilio_to = getattr(settings, 'TWILIO_WHATSAPP_TO', None)
    channels.append((
        'whatsapp',
        bool(twilio_sid and twilio_token and twilio_to),
        f"WhatsApp to {twilio_to}" if twilio_to else "Not configured"
    ))

    # WhatsApp Web
    whatsapp_web_recipient = getattr(settings, 'WHATSAPP_WEB_RECIPIENT', None)
    channels.append((
        'whatsapp_web',
        bool(whatsapp_web_recipient),
        f"WhatsApp Web to {whatsapp_web_recipient}" if whatsapp_web_recipient else "Not configured"
    ))

    return channels


__all__ = [
    'WhatsAppSender',
    'EmailSender',
    'TelegramSender',
    'SignalSender',
    'WhatsAppWebSender',
    'get_notification_sender',
    'send_alert',
    'send_alerts',
    'send_message',
    'get_available_channels',
    'CHANNEL_PRIORITY'
]
