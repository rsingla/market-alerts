# Quick Start Guide - Market Alerts

Get up and running in 5 minutes!

## Step 1: Install Dependencies (1 min)

```bash
cd market_alerts
pip install -r requirements.txt
```

## Step 2: Create Configuration File (2 min)

```bash
# Copy example to .env
cp .env.example .env

# Edit with your credentials
nano .env  # or use your favorite editor
```

**Minimum required settings:**
```env
# Get from https://www.twilio.com
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_WHATSAPP_TO=whatsapp:+1234567890

# Optional: Add your API keys for more features
NEWS_API_KEY=your_news_api_key  # Get from https://newsapi.org
```

## Step 3: Test the System (1 min)

```bash
# Run system tests
python3 test_system.py
```

This will test:
- ✓ Configuration loading
- ✓ Market hours checking
- ✓ Market data fetching
- ✓ News fetching
- ✓ Alert engine
- ✓ WhatsApp integration
- ✓ Full workflow

## Step 4: Choose How to Run (1 min)

### Option A: Scheduled Alerts (Recommended)

Runs automatically with hourly checks:

```bash
python3 main.py
```

This will:
- Check markets every 60 minutes during trading hours
- Send morning news digest at 8:00 AM ET
- Send market open summary at 9:35 AM ET
- Send midday summary at 12:00 PM ET
- Send market close summary at 4:05 PM ET
- Send WhatsApp alerts for significant movements

Press `Ctrl+C` to stop.

### Option B: Web Dashboard

Interactive dashboard to monitor markets:

```bash
streamlit run app_dashboard.py
```

Opens at: http://localhost:8501

Features:
- 📊 Live watchlist with prices
- 🔔 Active alerts
- 📰 Latest market news
- 📈 Price charts
- ⚙️ Settings
- 🧪 Test panel

## What You'll Receive on WhatsApp

### Price Movement Alerts
```
🚨 AAPL 📈

Price: $185.50
Change: +5.2% (+$9.25)
Range: $178.00 - $186.00

Updated: 2:30 PM ET
```

### Market Summaries
```
📊 Market Summary
November 1, 2025 at 9:35 AM ET

Indices:
📈 SPY: $450.25 (+0.8%)
📈 QQQ: $380.50 (+1.2%)
📉 DIA: $350.75 (-0.3%)

Top Movers:
📈 AAPL: $185.50 (+5.2%)
📉 TSLA: $245.30 (-3.8%)
```

### News Digest
```
📰 Market News

1. Fed Announces Rate Decision
   Reuters
   Federal Reserve raises rates by 0.25%...
   https://reuters.com/...

2. Tech Stocks Rally on Earnings
   CNBC
   Major tech companies beat expectations...
```

## Customization

### Change Watchlist

Edit `.env`:
```env
WATCHLIST=AAPL,GOOGL,MSFT,TSLA,NVDA,SPY,QQQ
```

### Adjust Alert Thresholds

Edit `.env`:
```env
SMALL_MOVE_THRESHOLD=1.0   # Alert on ±1% moves
MEDIUM_MOVE_THRESHOLD=3.0  # Alert on ±3% moves
LARGE_MOVE_THRESHOLD=5.0   # Alert on ±5% moves
VOLUME_SPIKE_THRESHOLD=2.0 # Alert on 2x volume
```

### Change Check Frequency

Edit `.env`:
```env
CHECK_INTERVAL_MINUTES=30  # Check every 30 minutes
```

## Troubleshooting

### "No data available"
- Markets may be closed (check market hours)
- Set `MARKET_HOURS_ONLY=false` to test anytime
- Try using yfinance: `USE_YFINANCE=true`

### "WhatsApp not configured"
1. Get Twilio account at https://www.twilio.com
2. Enable WhatsApp sandbox
3. Join sandbox by texting: `join <code>` to Twilio number
4. Set credentials in `.env`

### "Rate limit exceeded"
- Increase `CHECK_INTERVAL_MINUTES`
- Enable caching: `CACHE_DURATION=300` (5 minutes)
- Get additional API keys

## Testing Individual Components

```bash
# Test configuration
python3 -m config.settings

# Test market data
python3 -m data.market_data

# Test news fetching
python3 -m data.news_fetcher

# Test alerts
python3 -m alerts.alert_engine

# Test WhatsApp
python3 -m notifications.whatsapp_sender
```

## Next Steps

1. **Monitor for a day** - Let it run and see what alerts you get
2. **Adjust thresholds** - Too many alerts? Increase thresholds
3. **Add more stocks** - Edit WATCHLIST in `.env`
4. **Explore dashboard** - Run `streamlit run app_dashboard.py`
5. **Check logs** - View `logs/market_alerts.log` for details

## Support

Need help?
- Check logs in `logs/market_alerts.log`
- Run `python3 test_system.py` to diagnose issues
- Review README.md for detailed documentation

## Tips for Best Results

1. **Start small**: Monitor 5-10 stocks initially
2. **Tune thresholds**: Adjust based on volatility
3. **Check logs**: Review what's happening
4. **Test WhatsApp**: Send test message first
5. **Market hours**: Enable MARKET_HOURS_ONLY for less noise

---

**You're all set!** Run `python3 main.py` and start receiving market alerts! 🚀
