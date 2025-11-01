# Market Alerts Application - Detailed Implementation Plan

## 📋 Project Overview

**Goal**: Build a Python application that monitors financial markets and sends real-time alerts to WhatsApp

**Key Features**:
- Monitor stock prices, indices, and cryptocurrencies
- Aggregate financial news from multiple sources
- Send WhatsApp notifications via Twilio
- Run on hourly schedule during market hours
- Filter important events (price moves, breaking news, earnings)

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    MARKET ALERTS SYSTEM                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  Data Layer  │    │ Logic Layer  │    │ Output Layer │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                    │                    │          │
│         ▼                    ▼                    ▼          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │ Market Data  │───▶│ Alert Engine │───▶│   WhatsApp   │  │
│  │  APIs        │    │  Processor   │    │   Sender     │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                    │                               │
│  ┌──────────────┐    ┌──────────────┐                      │
│  │  News APIs   │───▶│   Filters    │                      │
│  │              │    │   & Rules    │                      │
│  └──────────────┘    └──────────────┘                      │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Scheduler (Hourly Triggers)             │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 📝 PHASE 1: Project Setup (15 minutes)

### Step 1.1: Create Project Structure

```bash
market_alerts/
├── config/
│   ├── __init__.py
│   ├── settings.py          # Configuration constants
│   └── watchlist.py          # Stock watchlists
├── data/
│   ├── __init__.py
│   ├── market_data.py        # Fetch stock prices
│   ├── news_fetcher.py       # Fetch news
│   └── cache.py              # Cache API responses
├── alerts/
│   ├── __init__.py
│   ├── alert_engine.py       # Main alert logic
│   ├── filters.py            # Alert filtering rules
│   └── formatters.py         # Message formatting
├── notifications/
│   ├── __init__.py
│   ├── whatsapp_sender.py    # Twilio WhatsApp
│   ├── telegram_sender.py    # (Optional) Telegram
│   └── email_sender.py       # (Optional) Email
├── scheduler/
│   ├── __init__.py
│   ├── cron_scheduler.py     # Hourly triggers
│   └── market_hours.py       # Market hours checker
├── utils/
│   ├── __init__.py
│   ├── logger.py             # Logging setup
│   └── helpers.py            # Utility functions
├── tests/
│   ├── test_market_data.py
│   ├── test_alerts.py
│   └── test_notifications.py
├── .env                      # API keys (DO NOT COMMIT)
├── .env.example              # Template for .env
├── requirements.txt          # Python dependencies
├── main.py                   # Main entry point
├── README.md                 # Documentation
└── IMPLEMENTATION_PLAN.md    # This file
```

**Action Items**:
- [x] Create directory structure
- [ ] Initialize git repository
- [ ] Create .gitignore (exclude .env, __pycache__, *.pyc)
- [ ] Create requirements.txt
- [ ] Create .env.example template

---

## 📝 PHASE 2: Configuration & Environment (20 minutes)

### Step 2.1: Create `.env.example` Template

```env
# ===== TWILIO (WhatsApp) =====
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
TWILIO_WHATSAPP_TO=whatsapp:+1234567890

# ===== FINANCIAL DATA APIs =====
# Alpha Vantage (FREE - 500 calls/day)
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key

# News API (FREE - 1000 requests/day)
NEWS_API_KEY=your_news_api_key

# Finnhub (FREE - 60 calls/minute)
FINNHUB_API_KEY=your_finnhub_key

# Yahoo Finance (no key needed)
USE_YFINANCE=true

# ===== ALERT SETTINGS =====
# Stocks to monitor (comma-separated)
WATCHLIST=AAPL,GOOGL,MSFT,TSLA,NVDA,SPY,QQQ

# Price change thresholds (%)
SMALL_MOVE_THRESHOLD=1.0
MEDIUM_MOVE_THRESHOLD=3.0
LARGE_MOVE_THRESHOLD=5.0

# Volume spike threshold (multiple of average)
VOLUME_SPIKE_THRESHOLD=2.0

# ===== SCHEDULER SETTINGS =====
# Check interval in minutes (during market hours)
CHECK_INTERVAL_MINUTES=60

# Only send alerts during market hours
MARKET_HOURS_ONLY=true

# Market hours (EST)
MARKET_OPEN_HOUR=9
MARKET_OPEN_MINUTE=30
MARKET_CLOSE_HOUR=16
MARKET_CLOSE_MINUTE=0

# ===== NEWS SETTINGS =====
# Keywords for important news
NEWS_KEYWORDS=earnings,fed,rate,gdp,jobs,inflation,unemployment

# Maximum news items per alert
MAX_NEWS_ITEMS=3

# ===== CACHE SETTINGS =====
# Cache duration in seconds
CACHE_DURATION=300

# ===== LOGGING =====
LOG_LEVEL=INFO
LOG_FILE=market_alerts.log
```

### Step 2.2: Create `requirements.txt`

```txt
# Core
python-dotenv==1.0.0
requests==2.31.0
schedule==1.2.0

# Financial Data
yfinance==0.2.33
alpha-vantage==2.3.1

# News
feedparser==6.0.10

# WhatsApp/Notifications
twilio==8.10.0

# Data Processing
pandas==2.1.4
numpy==1.26.2

# Utilities
pytz==2023.3
python-dateutil==2.8.2

# Optional
# telegram-send==0.34  # For Telegram notifications
# sendgrid==6.11.0     # For email notifications
```

### Step 2.3: Create Configuration Module (`config/settings.py`)

```python
"""
Configuration settings loaded from .env file
"""
import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env file
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# ===== TWILIO SETTINGS =====
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_FROM = os.getenv('TWILIO_WHATSAPP_FROM', 'whatsapp:+14155238886')
TWILIO_WHATSAPP_TO = os.getenv('TWILIO_WHATSAPP_TO')

# ===== API KEYS =====
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
NEWS_API_KEY = os.getenv('NEWS_API_KEY')
FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY')
USE_YFINANCE = os.getenv('USE_YFINANCE', 'true').lower() == 'true'

# ===== WATCHLIST =====
WATCHLIST = os.getenv('WATCHLIST', 'AAPL,GOOGL,MSFT,SPY').split(',')
WATCHLIST = [s.strip() for s in WATCHLIST]

# ===== THRESHOLDS =====
SMALL_MOVE_THRESHOLD = float(os.getenv('SMALL_MOVE_THRESHOLD', '1.0'))
MEDIUM_MOVE_THRESHOLD = float(os.getenv('MEDIUM_MOVE_THRESHOLD', '3.0'))
LARGE_MOVE_THRESHOLD = float(os.getenv('LARGE_MOVE_THRESHOLD', '5.0'))
VOLUME_SPIKE_THRESHOLD = float(os.getenv('VOLUME_SPIKE_THRESHOLD', '2.0'))

# ===== SCHEDULER =====
CHECK_INTERVAL_MINUTES = int(os.getenv('CHECK_INTERVAL_MINUTES', '60'))
MARKET_HOURS_ONLY = os.getenv('MARKET_HOURS_ONLY', 'true').lower() == 'true'

MARKET_OPEN_HOUR = int(os.getenv('MARKET_OPEN_HOUR', '9'))
MARKET_OPEN_MINUTE = int(os.getenv('MARKET_OPEN_MINUTE', '30'))
MARKET_CLOSE_HOUR = int(os.getenv('MARKET_CLOSE_HOUR', '16'))
MARKET_CLOSE_MINUTE = int(os.getenv('MARKET_CLOSE_MINUTE', '0'))

# ===== NEWS =====
NEWS_KEYWORDS = os.getenv('NEWS_KEYWORDS', 'earnings,fed,rate').split(',')
NEWS_KEYWORDS = [k.strip() for k in NEWS_KEYWORDS]
MAX_NEWS_ITEMS = int(os.getenv('MAX_NEWS_ITEMS', '3'))

# ===== CACHE =====
CACHE_DURATION = int(os.getenv('CACHE_DURATION', '300'))

# ===== LOGGING =====
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'market_alerts.log')
```

**Action Items**:
- [ ] Create .env file with your actual API keys
- [ ] Test configuration loading
- [ ] Verify all required keys are present

---

## 📝 PHASE 3: Data Layer - Market Data APIs (45 minutes)

### Step 3.1: Market Data Fetcher (`data/market_data.py`)

**Features**:
- Fetch real-time stock prices
- Get historical data for comparison
- Calculate price changes and volume
- Support multiple data sources (yfinance, Alpha Vantage, Finnhub)
- Cache results to reduce API calls

**Key Functions**:
```python
def get_stock_price(symbol: str) -> dict
def get_price_change(symbol: str, period: str = '1d') -> float
def get_volume_data(symbol: str) -> dict
def get_market_indices() -> dict
def is_market_open() -> bool
```

**Data Structure**:
```python
{
    'symbol': 'AAPL',
    'price': 185.50,
    'change': 3.75,
    'change_pct': 2.06,
    'volume': 89234567,
    'avg_volume': 65000000,
    'volume_ratio': 1.37,
    'high': 186.00,
    'low': 182.50,
    'open': 183.00,
    'timestamp': '2024-01-15 15:30:00'
}
```

### Step 3.2: News Fetcher (`data/news_fetcher.py`)

**Features**:
- Aggregate news from RSS feeds
- Fetch news from News API
- Filter by keywords
- Rank by importance

**Key Functions**:
```python
def get_market_news(limit: int = 10) -> list
def get_stock_news(symbol: str, limit: int = 5) -> list
def filter_breaking_news(news_items: list, keywords: list) -> list
def rank_news_by_importance(news_items: list) -> list
```

**Data Structure**:
```python
{
    'title': 'Fed Announces Rate Decision',
    'description': 'Federal Reserve raises rates by 0.25%...',
    'url': 'https://reuters.com/article/...',
    'source': 'Reuters',
    'published': '2024-01-15T14:30:00Z',
    'relevance_score': 0.95,
    'keywords': ['fed', 'rate', 'inflation']
}
```

### Step 3.3: Caching Layer (`data/cache.py`)

**Purpose**: Reduce API calls by caching responses

```python
class DataCache:
    def get(key: str) -> Any
    def set(key: str, value: Any, ttl: int)
    def clear()
    def is_valid(key: str) -> bool
```

**Action Items**:
- [ ] Implement yfinance integration (no API key needed)
- [ ] Add Alpha Vantage fallback
- [ ] Create RSS news aggregator
- [ ] Implement caching with expiration
- [ ] Test data fetching functions

---

## 📝 PHASE 4: Alert Engine (60 minutes)

### Step 4.1: Alert Logic (`alerts/alert_engine.py`)

**Core Responsibilities**:
1. Check watchlist stocks for significant moves
2. Scan news for breaking stories
3. Apply filtering rules
4. Format alert messages
5. Trigger notifications

**Key Functions**:
```python
def check_watchlist() -> list[Alert]
def check_price_movements() -> list[Alert]
def check_breaking_news() -> list[Alert]
def process_alerts(alerts: list[Alert]) -> list[Alert]
```

**Alert Types**:
1. **Price Movement Alerts**
   - Small move (1-3%)
   - Medium move (3-5%)
   - Large move (>5%)
   - Volume spike (>2x average)

2. **News Alerts**
   - Breaking news (keywords match)
   - Stock-specific news
   - Market-wide events

3. **Market Summary**
   - Hourly update with indices
   - Top movers
   - Market sentiment

### Step 4.2: Filters (`alerts/filters.py`)

**Purpose**: Prevent alert fatigue by filtering noise

```python
def filter_by_market_hours(alert: Alert) -> bool
def filter_by_threshold(alert: Alert, threshold: float) -> bool
def filter_duplicates(alerts: list[Alert]) -> list[Alert]
def prioritize_alerts(alerts: list[Alert]) -> list[Alert]
```

**Filtering Rules**:
- Only send during market hours (if enabled)
- Deduplicate alerts within 15 minutes
- Prioritize large moves over small moves
- Limit to top 5 most important alerts per cycle

### Step 4.3: Message Formatting (`alerts/formatters.py`)

**Purpose**: Create clean, readable WhatsApp messages

**Message Templates**:

```python
# Price Movement Alert
"""
🔥 PRICE ALERT 🔥
{symbol} {direction} {change_pct}% → ${price}
Previous: ${prev_price}
Volume: {volume} ({volume_ratio}x avg)
⏰ {time}
"""

# Market Summary
"""
📊 MARKET UPDATE 📊
S&P 500: {spy_change}% ({spy_price})
Nasdaq: {qqq_change}% ({qqq_price})
Dow: {dia_change}% ({dia_price})
VIX: {vix} ({vix_change}%)

Top Movers:
{top_gainers}

⏰ {time}
"""

# Breaking News
"""
📰 BREAKING NEWS 📰
{headline}

{summary}

🔗 {url}
⏰ {time}
```

**Action Items**:
- [ ] Implement alert detection logic
- [ ] Create filtering system
- [ ] Design message templates
- [ ] Test alert generation

---

## 📝 PHASE 5: WhatsApp Integration (30 minutes)

### Step 5.1: Twilio Setup

**Prerequisites**:
1. Twilio Account (free trial available)
2. WhatsApp Sandbox OR WhatsApp Business API

**Sandbox Setup**:
```
1. Go to Twilio Console
2. Navigate to Messaging → Try it out → Send a WhatsApp message
3. Join sandbox by texting: "join <code>" to +1-415-523-8886
4. Note your Twilio number: whatsapp:+14155238886
5. Your number format: whatsapp:+1234567890
```

### Step 5.2: WhatsApp Sender (`notifications/whatsapp_sender.py`)

```python
from twilio.rest import Client

class WhatsAppSender:
    def __init__(self):
        self.client = Client(account_sid, auth_token)

    def send_message(self, message: str, to: str = None) -> bool
    def send_alert(self, alert: Alert) -> bool
    def send_batch(self, alerts: list[Alert]) -> int
    def test_connection() -> bool
```

**Features**:
- Send individual messages
- Batch sending for multiple alerts
- Error handling and retries
- Delivery status tracking
- Rate limiting (Twilio allows 1 msg/sec)

**Action Items**:
- [ ] Set up Twilio account
- [ ] Join WhatsApp sandbox
- [ ] Implement sender class
- [ ] Test message delivery
- [ ] Handle errors gracefully

---

## 📝 PHASE 6: Scheduler (30 minutes)

### Step 6.1: Cron Scheduler (`scheduler/cron_scheduler.py`)

**Features**:
- Run checks every N minutes
- Respect market hours
- Handle timezone (convert to EST/EDT)
- Skip weekends
- Graceful shutdown

```python
def run_hourly_check():
    """Main function that runs every hour"""
    if not is_market_open_today():
        return

    if MARKET_HOURS_ONLY and not is_market_open_now():
        return

    # Fetch data
    market_data = get_market_data()
    news = get_breaking_news()

    # Generate alerts
    alerts = generate_alerts(market_data, news)

    # Send notifications
    send_alerts_to_whatsapp(alerts)
```

### Step 6.2: Market Hours Checker (`scheduler/market_hours.py`)

```python
def is_market_open_now() -> bool
def is_market_open_today() -> bool
def time_until_market_open() -> timedelta
def time_until_market_close() -> timedelta
def is_trading_day(date: datetime) -> bool  # Skip holidays
```

**Action Items**:
- [ ] Implement schedule library integration
- [ ] Add market hours logic
- [ ] Handle timezones correctly
- [ ] Test hourly triggers

---

## 📝 PHASE 7: Main Application (20 minutes)

### Step 7.1: Entry Point (`main.py`)

```python
"""
Market Alerts - Main Entry Point

Usage:
    python main.py --mode once     # Run once and exit
    python main.py --mode schedule # Run continuously with scheduler
    python main.py --test          # Test mode (no alerts sent)
"""

import argparse
from scheduler import start_scheduler
from alerts import check_and_send_alerts

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['once', 'schedule'], default='once')
    parser.add_argument('--test', action='store_true')
    args = parser.parse_args()

    if args.mode == 'once':
        check_and_send_alerts(test_mode=args.test)
    else:
        start_scheduler(test_mode=args.test)

if __name__ == '__main__':
    main()
```

**Action Items**:
- [ ] Create main entry point
- [ ] Add command-line arguments
- [ ] Implement test mode
- [ ] Add logging

---

## 📝 PHASE 8: Testing & Validation (30 minutes)

### Test Cases:

1. **Unit Tests**
   - [ ] Test market data fetching
   - [ ] Test news fetching
   - [ ] Test alert generation
   - [ ] Test message formatting

2. **Integration Tests**
   - [ ] Test WhatsApp delivery
   - [ ] Test scheduler triggers
   - [ ] Test error handling

3. **End-to-End Tests**
   - [ ] Run full cycle in test mode
   - [ ] Verify alert accuracy
   - [ ] Check message formatting

**Test Commands**:
```bash
# Test market data
python -m pytest tests/test_market_data.py

# Test WhatsApp (sends test message)
python -c "from notifications import test_whatsapp; test_whatsapp()"

# Test full cycle (no messages sent)
python main.py --test

# Run once for real
python main.py --mode once
```

---

## 📝 PHASE 9: Deployment (30 minutes)

### Option 1: Local Machine (Easiest)

```bash
# Install as service (runs continuously)
python main.py --mode schedule &

# Or use screen/tmux
screen -S market_alerts
python main.py --mode schedule
# Detach: Ctrl+A, D
```

### Option 2: Cloud (Recommended)

**AWS EC2 / Google Cloud / DigitalOcean**:
```bash
# 1. SSH into server
ssh user@your-server

# 2. Clone repository
git clone <your-repo>
cd market_alerts

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure .env
nano .env

# 5. Run as systemd service
sudo nano /etc/systemd/system/market-alerts.service
sudo systemctl enable market-alerts
sudo systemctl start market-alerts
```

**Docker**:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py", "--mode", "schedule"]
```

---

## 📊 Timeline Summary

| Phase | Task | Duration | Status |
|-------|------|----------|--------|
| 1 | Project Setup | 15 min | ⏳ In Progress |
| 2 | Configuration | 20 min | ⏳ Pending |
| 3 | Data Layer | 45 min | ⏳ Pending |
| 4 | Alert Engine | 60 min | ⏳ Pending |
| 5 | WhatsApp | 30 min | ⏳ Pending |
| 6 | Scheduler | 30 min | ⏳ Pending |
| 7 | Main App | 20 min | ⏳ Pending |
| 8 | Testing | 30 min | ⏳ Pending |
| 9 | Deployment | 30 min | ⏳ Pending |
| **TOTAL** | | **~4-5 hours** | |

---

## 🎯 Next Steps

1. **Immediate**: Create .env file with API keys
2. **Phase 1**: Complete project structure
3. **Phase 2**: Set up configuration
4. **Phase 3**: Build data layer (start with yfinance)
5. **Phase 4**: Implement alert logic
6. **Phase 5**: Set up WhatsApp (Twilio)
7. **Test**: Send first alert!

---

## 📚 Resources

**API Documentation**:
- Twilio WhatsApp: https://www.twilio.com/docs/whatsapp
- Alpha Vantage: https://www.alphavantage.co/documentation/
- News API: https://newsapi.org/docs
- yfinance: https://pypi.org/project/yfinance/

**Tutorials**:
- Python Schedule: https://schedule.readthedocs.io/
- Twilio Python: https://www.twilio.com/docs/libraries/python

---

Ready to start? Let me know which phase you'd like to begin with! 🚀
