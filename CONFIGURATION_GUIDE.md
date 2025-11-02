# Configuration Guide - Market Alerts

Complete guide to configuring your Market Alerts system.

## 📋 Quick Configuration Checklist

- [ ] Copy .env.example to .env
- [ ] Set up Twilio WhatsApp (REQUIRED for notifications)
- [ ] Configure at least one data source (yfinance is free and enabled by default)
- [ ] Add News API key (optional but recommended)
- [ ] Customize your watchlist
- [ ] Set alert thresholds
- [ ] Test the configuration

---

## 1. Create Your .env File

```bash
# Copy the example file
cp .env.example .env

# Edit it
nano .env    # or use your preferred editor
```

---

## 2. 🔴 REQUIRED: Twilio WhatsApp Setup

**This is REQUIRED for receiving alerts on WhatsApp.**

### Step 1: Get Twilio Account

1. Go to https://www.twilio.com/try-twilio
2. Sign up for a free account
3. Complete phone verification

### Step 2: Get WhatsApp Sandbox Access

1. In Twilio Console, go to **Messaging** → **Try it out** → **Send a WhatsApp message**
2. You'll see a WhatsApp number (like `+1 415 523 8886`)
3. You'll see a sandbox code (like `join abc-xyz`)
4. On your phone, send that message to the Twilio number:
   ```
   join abc-xyz
   ```
5. Wait for confirmation message

### Step 3: Get Your Credentials

1. Go to Twilio Console home page
2. Copy your **Account SID** (starts with AC...)
3. Copy your **Auth Token** (click to reveal)

### Step 4: Update .env File

```env
# Twilio WhatsApp Configuration
TWILIO_ACCOUNT_SID=your_account_sid_here    # Your Account SID (starts with AC)
TWILIO_AUTH_TOKEN=your_auth_token_here      # Your Auth Token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886  # Twilio's WhatsApp number
TWILIO_WHATSAPP_TO=whatsapp:+1234567890     # YOUR phone number (with country code)
```

**Important Notes:**
- `TWILIO_WHATSAPP_FROM`: Use the number from the sandbox (usually +1 415 523 8886)
- `TWILIO_WHATSAPP_TO`: Your personal phone number in format `whatsapp:+[country code][number]`
  - Example US: `whatsapp:+12025551234`
  - Example India: `whatsapp:+919876543210`
  - Example UK: `whatsapp:+447700900123`

---

## 3. 🟢 RECOMMENDED: News API Setup

**Get breaking financial news (1000 requests/day free).**

### Step 1: Get API Key

1. Go to https://newsapi.org/register
2. Fill in your details (name, email)
3. Confirm email
4. Copy your API key

### Step 2: Update .env File

```env
NEWS_API_KEY=your_news_api_key_here
```

**Benefits:**
- Breaking financial news
- Company-specific news
- Keyword filtering (earnings, fed, GDP, etc.)

---

## 4. 🟡 OPTIONAL: Additional Data Sources

### Alpha Vantage (FREE - 500 calls/day)

**Use as fallback or for more detailed data.**

1. Go to https://www.alphavantage.co/support/#api-key
2. Fill in your email
3. Copy your API key
4. Update .env:
   ```env
   ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
   ```

### Finnhub (FREE - 60 calls/minute)

**Good for company news and real-time data.**

1. Go to https://finnhub.io/register
2. Sign up
3. Copy your API key from dashboard
4. Update .env:
   ```env
   FINNHUB_API_KEY=your_finnhub_key
   ```

---

## 5. ⚙️ Customize Your Settings

### Watchlist (Which stocks to monitor)

```env
# Add your favorite stocks (comma-separated)
WATCHLIST=AAPL,GOOGL,MSFT,TSLA,NVDA,SPY,QQQ,DIA

# Examples:
# Tech heavy: AAPL,GOOGL,MSFT,AMZN,META,NVDA,TSM
# Index funds: SPY,QQQ,DIA,IWM,VTI
# Crypto-related: COIN,MSTR,RIOT,MARA
# Mix: AAPL,TSLA,SPY,QQQ,BTC-USD,ETH-USD
```

**Tips:**
- Start with 5-10 stocks to avoid overwhelming alerts
- Include at least one index (SPY, QQQ, or DIA) for market overview
- Use official Yahoo Finance symbols

### Alert Thresholds (How sensitive)

```env
# Price movement alerts
SMALL_MOVE_THRESHOLD=1.0    # Alert on ±1% moves
MEDIUM_MOVE_THRESHOLD=3.0   # Alert on ±3% moves (recommended)
LARGE_MOVE_THRESHOLD=5.0    # Alert on ±5% moves (critical)

# Volume alerts
VOLUME_SPIKE_THRESHOLD=2.0  # Alert when volume is 2x normal
```

**Recommendations:**
- **Conservative** (fewer alerts): 3%, 5%, 7%, 2.5x
- **Moderate** (balanced): 1%, 3%, 5%, 2x ← **Default**
- **Aggressive** (many alerts): 0.5%, 2%, 4%, 1.5x

### Schedule Settings

```env
# How often to check (in minutes)
CHECK_INTERVAL_MINUTES=60    # Check every hour

# Only during market hours?
MARKET_HOURS_ONLY=true       # true = only 9:30 AM - 4:00 PM ET
                             # false = check 24/7

# Market hours (EST)
MARKET_OPEN_HOUR=9
MARKET_OPEN_MINUTE=30
MARKET_CLOSE_HOUR=16
MARKET_CLOSE_MINUTE=0
```

**Tips:**
- `CHECK_INTERVAL_MINUTES=60` is good for most users
- Use 30 minutes for more active monitoring
- Use 15 minutes if you're a day trader (may hit rate limits)
- Keep `MARKET_HOURS_ONLY=true` to avoid off-hours noise

### News Settings

```env
# Which keywords trigger news alerts
NEWS_KEYWORDS=earnings,fed,rate,gdp,jobs,inflation,unemployment,fomc

# How many news items per alert
MAX_NEWS_ITEMS=3    # Keep it short for WhatsApp
```

---

## 6. 📝 Complete .env Example

Here's a fully configured example:

```env
# ===== TWILIO (WhatsApp) =====
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_actual_auth_token_here
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
TWILIO_WHATSAPP_TO=whatsapp:+12025551234

# ===== FINANCIAL DATA APIs =====
ALPHA_VANTAGE_API_KEY=YOUR_KEY_HERE
NEWS_API_KEY=YOUR_NEWS_KEY_HERE
FINNHUB_API_KEY=YOUR_FINNHUB_KEY
USE_YFINANCE=true

# ===== ALERT SETTINGS =====
WATCHLIST=AAPL,GOOGL,MSFT,TSLA,NVDA,SPY,QQQ
SMALL_MOVE_THRESHOLD=1.0
MEDIUM_MOVE_THRESHOLD=3.0
LARGE_MOVE_THRESHOLD=5.0
VOLUME_SPIKE_THRESHOLD=2.0

# ===== SCHEDULER SETTINGS =====
CHECK_INTERVAL_MINUTES=60
MARKET_HOURS_ONLY=true
MARKET_OPEN_HOUR=9
MARKET_OPEN_MINUTE=30
MARKET_CLOSE_HOUR=16
MARKET_CLOSE_MINUTE=0

# ===== NEWS SETTINGS =====
NEWS_KEYWORDS=earnings,fed,rate,gdp,jobs,inflation
MAX_NEWS_ITEMS=3

# ===== CACHE SETTINGS =====
CACHE_DURATION=300

# ===== LOGGING =====
LOG_LEVEL=INFO
LOG_FILE=logs/market_alerts.log
```

---

## 7. 🧪 Test Your Configuration

### Test 1: Validate Configuration

```bash
python3 -m config.settings
```

**Expected output:**
```
✓ Configuration loaded
✓ All required settings present
✓ WhatsApp configured
✓ Data sources available
```

### Test 2: Test Market Hours

```bash
python3 -m utils.market_hours
```

**Expected output:**
```
Current Time (ET): 2025-11-01 16:00:00 EDT
Trading Day: Yes ✓
Market Hours: No ✗ (after hours)
```

### Test 3: Test WhatsApp

```bash
python3 -m notifications.whatsapp_sender
```

Then follow prompts to send a test message.

### Test 4: Run Full System Test

```bash
python3 test_system.py
```

This runs all 7 tests including WhatsApp.

---

## 8. 🔍 Troubleshooting

### "TWILIO_ACCOUNT_SID not set"

**Problem:** Twilio credentials missing
**Solution:**
1. Copy credentials from Twilio console
2. Update .env file
3. Restart application

### "WhatsApp message failed"

**Problem:** Phone number not joined to sandbox
**Solution:**
1. Send `join [code]` to Twilio WhatsApp number
2. Wait for confirmation
3. Try again

### "No data available"

**Problem:** Markets closed or rate limited
**Solution:**
1. Check if markets are open (9:30 AM - 4:00 PM ET)
2. Wait if rate limited (15-30 minutes)
3. Try with `MARKET_HOURS_ONLY=false` for testing

### "News API error"

**Problem:** Invalid or missing API key
**Solution:**
1. Get new key from newsapi.org
2. Update NEWS_API_KEY in .env
3. Restart

---

## 9. 🎯 Recommended Configurations

### For Day Traders

```env
WATCHLIST=AAPL,TSLA,NVDA,SPY,QQQ
SMALL_MOVE_THRESHOLD=0.5
MEDIUM_MOVE_THRESHOLD=2.0
LARGE_MOVE_THRESHOLD=4.0
CHECK_INTERVAL_MINUTES=15
MARKET_HOURS_ONLY=true
```

### For Long-term Investors

```env
WATCHLIST=SPY,QQQ,VTI,VEA,VWO
SMALL_MOVE_THRESHOLD=2.0
MEDIUM_MOVE_THRESHOLD=5.0
LARGE_MOVE_THRESHOLD=10.0
CHECK_INTERVAL_MINUTES=120
MARKET_HOURS_ONLY=true
```

### For News Junkies

```env
NEWS_KEYWORDS=earnings,fed,rate,gdp,jobs,inflation,fomc,powell,yellen,treasury,crisis,rally,sell-off
MAX_NEWS_ITEMS=5
CHECK_INTERVAL_MINUTES=30
```

---

## 10. 🔒 Security Best Practices

1. **Never commit .env to git** (already in .gitignore)
2. **Keep API keys private** - don't share screenshots
3. **Use environment variables** in production
4. **Rotate keys** if accidentally exposed
5. **Use Twilio's test credentials** for development

---

## 11. ✅ Configuration Checklist

Before running the system, verify:

- [ ] `.env` file created and populated
- [ ] Twilio WhatsApp credentials added
- [ ] Sent `join` message to Twilio sandbox
- [ ] At least one data source configured (yfinance is default)
- [ ] Watchlist has 5+ symbols
- [ ] Alert thresholds set appropriately
- [ ] Ran `python3 -m config.settings` successfully
- [ ] Tested WhatsApp with test message
- [ ] Dashboard accessible at http://localhost:8502

---

## 12. 🚀 Ready to Start!

Once configured, start the system:

```bash
# Option 1: Background scheduler (recommended)
python3 main.py

# Option 2: Web dashboard
python3 -m streamlit run app_dashboard.py

# Option 3: One-time check
python3 -m alerts.alert_engine
```

---

## Need Help?

- Check logs: `tail -f logs/market_alerts.log`
- Run tests: `python3 test_system.py`
- View this guide: `CONFIGURATION_GUIDE.md`
- Check README: `README.md`
- Quick start: `QUICKSTART.md`
