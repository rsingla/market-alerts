"""
Email Sender via Brevo (Sendinblue)
Sends market alerts via email
"""

from typing import Optional, List
from datetime import datetime
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from config import settings
from utils.logger import logger
from alerts.alert_engine import Alert


class EmailSender:
    """Email sender using Brevo (Sendinblue) API"""

    def __init__(self):
        """Initialize Brevo client"""
        # Get API key from environment
        self.api_key = getattr(settings, 'BREVO_API_KEY', None)
        self.sender_email = getattr(settings, 'SENDER_EMAIL', 'alerts@marketalerts.com')
        self.sender_name = getattr(settings, 'SENDER_NAME', 'Market Alerts')
        self.recipient_email = getattr(settings, 'RECIPIENT_EMAIL', None)

        if not self.api_key:
            logger.warning("Brevo API key not configured")
            self.client = None
        else:
            # Configure API client
            configuration = sib_api_v3_sdk.Configuration()
            configuration.api_key['api-key'] = self.api_key
            self.client = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
            logger.info("Brevo email client initialized")

        self.emails_sent = 0
        self.last_sent = None

    def send_email(self, subject: str, content: str, to_email: Optional[str] = None) -> bool:
        """
        Send an email

        Args:
            subject: Email subject
            content: Email content (HTML or text)
            to_email: Recipient email (uses RECIPIENT_EMAIL if None)

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.client:
            logger.error("Brevo client not initialized - check API key")
            return False

        if to_email is None:
            to_email = self.recipient_email

        if not to_email:
            logger.error("No recipient email configured")
            return False

        try:
            # Create email object
            sender = {"name": self.sender_name, "email": self.sender_email}
            to = [{"email": to_email}]

            # Convert markdown-style formatting to HTML
            html_content = self._format_html(content)

            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=to,
                sender=sender,
                subject=subject,
                html_content=html_content,
                text_content=content  # Fallback to plain text
            )

            # Send email
            api_response = self.client.send_transac_email(send_smtp_email)

            logger.info(f"Email sent successfully: {api_response.message_id}")
            self.emails_sent += 1
            self.last_sent = datetime.now()

            return True

        except ApiException as e:
            logger.error(f"Brevo API error: {e}")
            return False

        except Exception as e:
            logger.error(f"Error sending email: {e}", exc_info=True)
            return False

    def _format_html(self, text: str) -> str:
        """
        Convert markdown-style text to HTML

        Args:
            text: Text with markdown formatting

        Returns:
            HTML formatted text
        """
        html = text

        # Convert bold (**text** or *text*) to <strong>
        import re
        html = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*([^*]+)\*', r'<strong>\1</strong>', html)

        # Convert newlines to <br>
        html = html.replace('\n', '<br>')

        # Add basic styling
        html = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 20px;
                    border-radius: 10px 10px 0 0;
                    text-align: center;
                }}
                .content {{
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 0 0 10px 10px;
                }}
                .alert-box {{
                    background: white;
                    padding: 15px;
                    margin: 10px 0;
                    border-left: 4px solid #667eea;
                    border-radius: 5px;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 20px;
                    font-size: 12px;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 Market Alerts</h1>
            </div>
            <div class="content">
                <div class="alert-box">
                    {html}
                </div>
            </div>
            <div class="footer">
                <p>Sent by Market Alerts System | {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}</p>
            </div>
        </body>
        </html>
        """

        return html

    def send_alert(self, alert: Alert) -> bool:
        """
        Send a single alert via email

        Args:
            alert: Alert object

        Returns:
            True if sent successfully
        """
        subject = f"🔔 Market Alert: {alert.symbol} {alert.alert_type.value}"
        logger.info(f"Sending email alert for {alert.symbol}")
        return self.send_email(subject, alert.message)

    def send_alerts(self, alerts: List[Alert], combine: bool = True) -> bool:
        """
        Send multiple alerts via email

        Args:
            alerts: List of Alert objects
            combine: If True, combine into single email; if False, send separately

        Returns:
            True if all sent successfully
        """
        if not alerts:
            logger.info("No alerts to send")
            return True

        if combine:
            # Combine alerts into single email
            subject = f"🔔 Market Alerts - {len(alerts)} Alert{'s' if len(alerts) > 1 else ''}"

            content = f"Market Alerts Summary\n"
            content += f"{datetime.now().strftime('%B %d, %Y at %I:%M %p ET')}\n\n"
            content += f"You have {len(alerts)} alert{'s' if len(alerts) > 1 else ''}:\n\n"

            for i, alert in enumerate(alerts, 1):
                content += f"\n{'='*50}\n"
                content += f"Alert #{i}\n"
                content += f"{'='*50}\n\n"
                content += alert.message
                content += "\n"

            return self.send_email(subject, content)

        else:
            # Send each alert separately
            success = True
            for alert in alerts:
                if not self.send_alert(alert):
                    success = False

            return success

    def test_connection(self) -> bool:
        """
        Test email connection by sending a test message

        Returns:
            True if test successful
        """
        logger.info("Testing email connection...")

        subject = "✅ Market Alerts - Test Email"
        content = """
**Market Alerts - Test Message**

This is a test email to verify your email integration.

**Configuration:**
• Sender: {sender}
• API: Brevo (Sendinblue)
• Status: Connection successful!

**Time:** {time}

If you received this email, your Market Alerts system is properly configured and ready to send notifications.

---

You can now start receiving real-time market alerts via email!
        """.format(
            sender=self.sender_email,
            time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )

        return self.send_email(subject, content)

    def get_stats(self) -> dict:
        """
        Get sender statistics

        Returns:
            Dictionary with statistics
        """
        return {
            'emails_sent': self.emails_sent,
            'last_sent': self.last_sent.isoformat() if self.last_sent else None,
            'configured': self.client is not None,
            'sender_email': self.sender_email,
            'recipient_email': self.recipient_email
        }


# Global sender instance
_sender = None


def get_sender() -> EmailSender:
    """Get global email sender instance"""
    global _sender
    if _sender is None:
        _sender = EmailSender()
    return _sender


def send_email(subject: str, content: str, to_email: Optional[str] = None) -> bool:
    """
    Send an email (convenience function)

    Args:
        subject: Email subject
        content: Email content
        to_email: Optional recipient

    Returns:
        True if sent successfully
    """
    sender = get_sender()
    return sender.send_email(subject, content, to_email)


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
        combine: Combine into single email

    Returns:
        True if all sent successfully
    """
    sender = get_sender()
    return sender.send_alerts(alerts, combine)


if __name__ == '__main__':
    # Test email sender
    print("\n" + "="*60)
    print("EMAIL SENDER TEST")
    print("="*60)

    sender = EmailSender()

    # Check configuration
    if not sender.client:
        print("\n❌ Brevo not configured")
        print("   Please set BREVO_API_KEY and RECIPIENT_EMAIL in .env")
    else:
        print("\n✓ Brevo client initialized")
        print(f"  Sender: {sender.sender_email}")
        print(f"  Recipient: {sender.recipient_email}")

        # Test connection
        print("\nTesting email connection...")
        print("(This will send a test email to the configured address)")

        user_input = input("\nSend test email? (y/n): ")
        if user_input.lower() == 'y':
            success = sender.test_connection()
            if success:
                print("✓ Test email sent successfully!")
                print("  Check your inbox")
            else:
                print("❌ Failed to send test email")
                print("  Check logs for details")

    # Show stats
    print("\nSender Statistics:")
    stats = sender.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("="*60 + "\n")
