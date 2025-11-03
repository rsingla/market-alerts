"""
Configuration Settings
Loads environment variables from .env file
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print(f"✓ Loaded configuration from {env_path}")
else:
    print(f"⚠️  No .env file found at {env_path}")
    print("   Using environment variables or defaults")

# ===== EMAIL NOTIFICATIONS (Brevo/Sendinblue) =====
BREVO_API_KEY = os.getenv('BREVO_API_KEY')
SENDER_EMAIL = os.getenv('SENDER_EMAIL', 'alerts@marketalerts.com')
SENDER_NAME = os.getenv('SENDER_NAME', 'Market Alerts')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')

# ===== TELEGRAM SETTINGS =====
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# ===== SIGNAL SETTINGS =====
SIGNAL_SENDER_NUMBER = os.getenv('SIGNAL_SENDER_NUMBER')
SIGNAL_RECIPIENT_NUMBER = os.getenv('SIGNAL_RECIPIENT_NUMBER')
SIGNAL_CLI_PATH = os.getenv('SIGNAL_CLI_PATH', 'signal-cli')

# ===== TWILIO (WhatsApp) SETTINGS =====
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_FROM = os.getenv('TWILIO_WHATSAPP_FROM', 'whatsapp:+14155238886')
TWILIO_WHATSAPP_TO = os.getenv('TWILIO_WHATSAPP_TO')

# ===== WHATSAPP WEB SETTINGS =====
WHATSAPP_WEB_RECIPIENT = os.getenv('WHATSAPP_WEB_RECIPIENT')
WHATSAPP_WEB_WAIT_TIME = int(os.getenv('WHATSAPP_WEB_WAIT_TIME', '15'))
WHATSAPP_WEB_CLOSE_TAB = os.getenv('WHATSAPP_WEB_CLOSE_TAB', 'true').lower() == 'true'

# ===== FINANCIAL DATA API KEYS =====
ALPACA_API_KEY = os.getenv('ALPACA_API_KEY')  # Alpaca Markets (FREE unlimited data)
ALPACA_SECRET_KEY = os.getenv('ALPACA_SECRET_KEY')
ALPACA_BASE_URL = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')
POLYGON_API_KEY = os.getenv('POLYGON_API_KEY')  # Polygon.io (massive.com)
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
NEWS_API_KEY = os.getenv('NEWS_API_KEY')
FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY')
USE_YFINANCE = os.getenv('USE_YFINANCE', 'true').lower() == 'true'

# ===== WATCHLIST =====
WATCHLIST_STR = os.getenv('WATCHLIST', 'AAPL,GOOGL,MSFT,TSLA,SPY,QQQ')
WATCHLIST = [s.strip().upper() for s in WATCHLIST_STR.split(',') if s.strip()]

# Categorize watchlist
STOCKS = [s for s in WATCHLIST if not s in ['SPY', 'QQQ', 'DIA', 'IWM']]
INDICES = [s for s in WATCHLIST if s in ['SPY', 'QQQ', 'DIA', 'IWM']]

# ===== ALERT THRESHOLDS =====
SMALL_MOVE_THRESHOLD = float(os.getenv('SMALL_MOVE_THRESHOLD', '1.0'))
MEDIUM_MOVE_THRESHOLD = float(os.getenv('MEDIUM_MOVE_THRESHOLD', '3.0'))
LARGE_MOVE_THRESHOLD = float(os.getenv('LARGE_MOVE_THRESHOLD', '5.0'))
VOLUME_SPIKE_THRESHOLD = float(os.getenv('VOLUME_SPIKE_THRESHOLD', '2.0'))

# ===== SCHEDULER SETTINGS =====
CHECK_INTERVAL_MINUTES = int(os.getenv('CHECK_INTERVAL_MINUTES', '60'))
MARKET_HOURS_ONLY = os.getenv('MARKET_HOURS_ONLY', 'true').lower() == 'true'

# Market hours (EST/EDT)
MARKET_OPEN_HOUR = int(os.getenv('MARKET_OPEN_HOUR', '9'))
MARKET_OPEN_MINUTE = int(os.getenv('MARKET_OPEN_MINUTE', '30'))
MARKET_CLOSE_HOUR = int(os.getenv('MARKET_CLOSE_HOUR', '16'))
MARKET_CLOSE_MINUTE = int(os.getenv('MARKET_CLOSE_MINUTE', '0'))

# ===== NEWS SETTINGS =====
NEWS_KEYWORDS_STR = os.getenv('NEWS_KEYWORDS', 'earnings,fed,rate,gdp,jobs,inflation')
NEWS_KEYWORDS = [k.strip().lower() for k in NEWS_KEYWORDS_STR.split(',') if k.strip()]
MAX_NEWS_ITEMS = int(os.getenv('MAX_NEWS_ITEMS', '3'))

# ===== CACHE SETTINGS =====
CACHE_DURATION = int(os.getenv('CACHE_DURATION', '300'))  # 5 minutes

# ===== LOGGING =====
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'logs/market_alerts.log')

# ===== AI ANALYSIS (DeepSeek) =====
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_API_URL = os.getenv('DEEPSEEK_API_URL', 'https://api.deepseek.com/v1/chat/completions')
DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')

# ===== VALIDATION =====
def validate_config():
    """Validate critical configuration"""
    errors = []
    warnings = []

    # Check Twilio credentials
    if not TWILIO_ACCOUNT_SID:
        warnings.append("TWILIO_ACCOUNT_SID not set - WhatsApp alerts will not work")
    if not TWILIO_AUTH_TOKEN:
        warnings.append("TWILIO_AUTH_TOKEN not set - WhatsApp alerts will not work")
    if not TWILIO_WHATSAPP_TO:
        warnings.append("TWILIO_WHATSAPP_TO not set - No recipient for alerts")

    # Check at least one data source
    if not USE_YFINANCE and not ALPHA_VANTAGE_API_KEY and not FINNHUB_API_KEY:
        errors.append("No data source configured! Enable USE_YFINANCE or add API keys")

    # Check watchlist
    if not WATCHLIST:
        errors.append("WATCHLIST is empty - no stocks to monitor")

    # Check news API
    if not NEWS_API_KEY:
        warnings.append("NEWS_API_KEY not set - news alerts will not work")

    return errors, warnings

def print_config_summary():
    """Print configuration summary"""
    print("\n" + "="*60)
    print("MARKET ALERTS - CONFIGURATION SUMMARY")
    print("="*60)

    print(f"\n📊 WATCHLIST ({len(WATCHLIST)} symbols):")
    print(f"   Stocks: {', '.join(STOCKS[:5])}{' ...' if len(STOCKS) > 5 else ''}")
    print(f"   Indices: {', '.join(INDICES)}")

    print(f"\n🔔 ALERT THRESHOLDS:")
    print(f"   Small move:   ±{SMALL_MOVE_THRESHOLD}%")
    print(f"   Medium move:  ±{MEDIUM_MOVE_THRESHOLD}%")
    print(f"   Large move:   ±{LARGE_MOVE_THRESHOLD}%")
    print(f"   Volume spike: {VOLUME_SPIKE_THRESHOLD}x average")

    print(f"\n⏰ SCHEDULE:")
    print(f"   Check interval: Every {CHECK_INTERVAL_MINUTES} minutes")
    print(f"   Market hours only: {MARKET_HOURS_ONLY}")
    if MARKET_HOURS_ONLY:
        print(f"   Trading hours: {MARKET_OPEN_HOUR}:{MARKET_OPEN_MINUTE:02d} - {MARKET_CLOSE_HOUR}:{MARKET_CLOSE_MINUTE:02d} EST")

    print(f"\n📰 NEWS:")
    print(f"   Keywords: {', '.join(NEWS_KEYWORDS[:5])}{' ...' if len(NEWS_KEYWORDS) > 5 else ''}")
    print(f"   Max items: {MAX_NEWS_ITEMS}")

    print(f"\n🔌 DATA SOURCES:")
    print(f"   Alpaca Markets: {'✓' if ALPACA_API_KEY and ALPACA_SECRET_KEY else '✗'}")
    print(f"   Polygon.io: {'✓' if POLYGON_API_KEY else '✗'}")
    print(f"   Yahoo Finance: {'✓' if USE_YFINANCE else '✗'}")
    print(f"   Alpha Vantage: {'✓' if ALPHA_VANTAGE_API_KEY else '✗'}")
    print(f"   Finnhub: {'✓' if FINNHUB_API_KEY else '✗'}")
    print(f"   News API: {'✓' if NEWS_API_KEY else '✗'}")

    print(f"\n📱 NOTIFICATIONS:")
    print(f"   Email (Brevo): {'✓' if BREVO_API_KEY else '✗'}")
    if RECIPIENT_EMAIL:
        print(f"   Email to: {RECIPIENT_EMAIL}")
    print(f"   Telegram: {'✓' if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID else '✗'}")
    if TELEGRAM_CHAT_ID:
        print(f"   Telegram chat: {TELEGRAM_CHAT_ID}")
    print(f"   Signal: {'✓' if SIGNAL_SENDER_NUMBER and SIGNAL_RECIPIENT_NUMBER else '✗'}")
    if SIGNAL_RECIPIENT_NUMBER:
        print(f"   Signal to: {SIGNAL_RECIPIENT_NUMBER}")
    print(f"   WhatsApp (Twilio): {'✓' if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN else '✗'}")
    if TWILIO_WHATSAPP_TO:
        print(f"   WhatsApp to: {TWILIO_WHATSAPP_TO}")
    print(f"   WhatsApp Web: {'✓' if WHATSAPP_WEB_RECIPIENT else '✗'}")
    if WHATSAPP_WEB_RECIPIENT:
        print(f"   WhatsApp Web to: {WHATSAPP_WEB_RECIPIENT}")

    # Validation
    errors, warnings = validate_config()

    if warnings:
        print(f"\n⚠️  WARNINGS:")
        for warning in warnings:
            print(f"   • {warning}")

    if errors:
        print(f"\n❌ ERRORS:")
        for error in errors:
            print(f"   • {error}")
        print("\n   Fix these errors before running the application!")
    else:
        print(f"\n✅ Configuration is valid!")

    print("="*60 + "\n")

    return len(errors) == 0

if __name__ == '__main__':
    # Test configuration
    print_config_summary()
