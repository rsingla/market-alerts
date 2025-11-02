# Polygon.io (massive.com) Setup Guide

## Why Polygon.io?

Polygon.io (now called massive.com) is the **most reliable** market data provider with:

### Advantages over Yahoo Finance:
- ✅ **No rate limiting issues** on paid plans
- ✅ **Official API** with guaranteed uptime
- ✅ **Real-time data** available
- ✅ **Better documentation** and support
- ✅ **Professional-grade** data quality
- ✅ **Websocket support** for live streaming

### Pricing:
- **FREE Tier:** 5 API calls/minute
- **BASIC Plan:** $29/month - Unlimited API calls
- **STARTER Plan:** $99/month - Real-time data + websockets
- **DEVELOPER Plan:** $249/month - All features

**Recommendation:** Start with FREE tier for testing, upgrade to BASIC ($29/mo) for production.

---

## Step 1: Get Your API Key

### Option A: polygon.io (Original Site)

1. Visit: https://polygon.io
2. Click "**Get Started**" or "**Sign Up**"
3. Create account with email
4. Verify your email
5. Go to Dashboard → **API Keys**
6. Copy your API key (starts with: `pk_`)

### Option B: massive.com (New Branding)

1. Visit: https://massive.com
2. Sign up for account
3. Navigate to API section
4. Generate API key

**Note:** Both sites are the same service, just different branding.

---

## Step 2: Add API Key to .env

Open your `.env` file and add:

```env
# Polygon.io / massive.com
POLYGON_API_KEY=pk_your_actual_api_key_here
```

**Example:**
```env
POLYGON_API_KEY=pk_1234567890abcdefghijklmnopqrst
```

---

## Step 3: Restart the Application

```bash
# Stop all processes
pkill -f streamlit
pkill -f main.py

# Start dashboard
python3 -m streamlit run app_dashboard.py --server.port=8502 &

# Start alert scheduler
python3 main.py &
```

---

## Step 4: Verify It's Working

### Check Logs

```bash
tail -f logs/market_alerts.log
```

**Look for:**
```
INFO | Trying Polygon.io for AAPL...
INFO | ✓ Polygon.io success for AAPL
INFO | Successfully fetched 8/8 quotes
```

### Test Data Fetching

```bash
python3 -c "from data.market_data import get_stock_quote; quote = get_stock_quote('AAPL'); print(f'Success: {quote is not None}') if quote else print('Failed')"
```

**Expected Output:**
```
Success: True
```

### Check Dashboard

1. Open: http://localhost:8502
2. You should see market data loading
3. All 8 stocks should have prices

---

## How It Works

### Data Source Priority

The system now uses this priority order:

1. **Polygon.io** (if API key configured) ← **PRIMARY**
2. **Yahoo Finance** (if enabled) ← Fallback
3. **Alpha Vantage** (if API key configured) ← Last resort

### Intelligent Fallback

```python
# Polygon tries first
if POLYGON_API_KEY configured:
    try Polygon.io
    if success: return data ✓

# Falls back to yfinance if Polygon fails
if USE_YFINANCE=true:
    try Yahoo Finance
    if success: return data ✓

# Last resort: Alpha Vantage
if ALPHA_VANTAGE_API_KEY configured:
    try Alpha Vantage
    if success: return data ✓
```

### What Data Polygon Provides

- ✅ Current price
- ✅ Price change ($)
- ✅ Price change (%)
- ✅ Daily volume
- ✅ Day high/low
- ✅ Previous close
- ✅ Previous day volume (as avg volume approximation)
- ❌ Market cap (not provided in snapshot API)

---

## Free Tier Limits

### What You Get:
- **5 API calls per minute**
- **100 API calls per day** (approximately)
- Delayed data (15 minutes)

### For 8 Stocks Every Hour:
- 8 API calls per check
- 24 checks per day (hourly)
- **192 API calls/day** needed

**Result:** Free tier is **NOT sufficient** for hourly monitoring of 8 stocks.

### Solutions:

#### Option 1: Reduce Frequency ✅
```env
# Check every 2 hours instead of 1
CHECK_INTERVAL_MINUTES=120
```
- 12 checks per day
- 96 API calls/day
- ✓ Stays within free tier

#### Option 2: Reduce Watchlist ✅
```env
# Monitor only 5 stocks instead of 8
WATCHLIST=AAPL,GOOGL,MSFT,TSLA,SPY
```
- 5 API calls per check
- 24 checks per day (hourly)
- 120 API calls/day
- ⚠️ Slightly over limit, but might work

#### Option 3: Upgrade to BASIC Plan ($29/mo) ✅ **RECOMMENDED**
- **Unlimited API calls**
- No rate limiting
- Monitor as many stocks as you want
- Check as frequently as you want
- **Best for production use**

---

## Comparison: Polygon vs Others

| Feature | Polygon Free | Polygon Basic | Yahoo Finance | Alpha Vantage |
|---------|--------------|---------------|---------------|---------------|
| **Cost** | Free | $29/month | Free | Free |
| **Rate Limit** | 5/min | Unlimited | Unstable | 500/day |
| **API Calls/Day** | ~100 | Unlimited | Unknown | 500 |
| **Data Quality** | ✓ | ✓✓✓ | ✓ | ✓✓ |
| **Reliability** | ✓✓ | ✓✓✓ | ✗ | ✓✓ |
| **Documentation** | ✓✓✓ | ✓✓✓ | ✗ | ✓✓ |
| **Support** | Email | Priority | None | Email |
| **Real-time** | ✗ | ✗ | ✗ | ✗ |
| **Historical** | ✓ | ✓ | ✓ | Limited |
| **Production Ready** | ✗ | ✓✓✓ | ✗ | ✓ |

---

## Troubleshooting

### Error: "Authentication error"

**Problem:** Invalid API key

**Solutions:**
1. Check API key is correct (starts with `pk_`)
2. Ensure no extra spaces in .env file
3. Verify API key is active in Polygon dashboard
4. Make sure you didn't copy example key

```env
# ✗ Wrong (example key)
POLYGON_API_KEY=your_polygon_api_key

# ✓ Correct (real key)
POLYGON_API_KEY=pk_1234567890abcdefghijklmnopqrst
```

### Error: "Rate limit exceeded"

**Problem:** Using free tier with too many requests

**Solutions:**
1. Reduce check frequency to every 2+ hours
2. Reduce number of stocks in watchlist
3. Upgrade to BASIC plan ($29/mo)

```env
# Option 1: Reduce frequency
CHECK_INTERVAL_MINUTES=120  # Every 2 hours

# Option 2: Smaller watchlist
WATCHLIST=AAPL,SPY  # Just 2 stocks
```

### Error: "No data available"

**Problem:** Market closed or weekend

**Solution:** Polygon returns previous day's close when market is closed. This is expected behavior.

### Error: "Ticker not found"

**Problem:** Invalid stock symbol

**Solutions:**
1. Verify symbol is correct (AAPL not APPL)
2. Check if stock is listed on US exchanges
3. Some ETFs might not be available

---

## Advanced Configuration

### Disable Fallbacks (Polygon Only)

If you want to use **only** Polygon.io:

```env
# Disable other data sources
USE_YFINANCE=false
POLYGON_API_KEY=pk_your_key_here
# Don't set ALPHA_VANTAGE_API_KEY
```

### Use Polygon with Fallbacks (Recommended)

For maximum reliability:

```env
# Primary source
POLYGON_API_KEY=pk_your_key_here

# Fallbacks
USE_YFINANCE=true
ALPHA_VANTAGE_API_KEY=your_av_key

# System tries Polygon first, then yfinance, then Alpha Vantage
```

---

## API Key Security

### Best Practices:

1. **Never commit .env file to git**
   ```bash
   # Already in .gitignore
   .env
   ```

2. **Use environment variables in production**
   ```bash
   export POLYGON_API_KEY=pk_your_key
   ```

3. **Rotate keys regularly**
   - Generate new key every 6 months
   - Delete old keys from Polygon dashboard

4. **Use different keys for dev/prod**
   - Development: Free tier key
   - Production: Paid plan key

---

## Monitoring Usage

### Check API Usage

1. Login to Polygon.io dashboard
2. Go to **Usage** section
3. View API call statistics

### Set Up Alerts

In Polygon dashboard:
1. Go to **Settings**
2. Enable usage alerts
3. Get notified at 80% of limit

---

## Migration from Yahoo Finance

### Before (Yahoo Finance Only)

```env
USE_YFINANCE=true
# Getting rate limited frequently
```

**Problems:**
- 429 errors during development
- Unreliable data fetching
- No official support
- Unknown rate limits

### After (Polygon + Fallbacks)

```env
POLYGON_API_KEY=pk_your_key
USE_YFINANCE=true
ALPHA_VANTAGE_API_KEY=your_av_key
```

**Benefits:**
- ✓ Reliable data from Polygon
- ✓ Automatic fallback if Polygon fails
- ✓ No more rate limiting (on paid plan)
- ✓ Production-ready setup

---

## Testing Polygon Integration

### Test Script

Create `test_polygon.py`:

```python
from data.market_data import get_stock_quote, get_market_summary
from config import settings

print("\n" + "="*60)
print("POLYGON.IO TEST")
print("="*60)

# Check if API key is configured
if not settings.POLYGON_API_KEY:
    print("\n❌ POLYGON_API_KEY not configured in .env")
    print("   Add your API key to proceed")
    exit(1)

print(f"\n✓ API Key configured: {settings.POLYGON_API_KEY[:10]}...")

# Test single stock
print("\nTesting single stock (AAPL)...")
quote = get_stock_quote('AAPL')

if quote:
    print(f"✓ Success!")
    print(f"  Price: ${quote.price:.2f}")
    print(f"  Change: {quote.change_percent:+.2f}%")
    print(f"  Volume: {quote.volume:,}")
else:
    print("✗ Failed to fetch data")

# Test full watchlist
print(f"\nTesting full watchlist ({len(settings.WATCHLIST)} stocks)...")
quotes = get_market_summary()

print(f"✓ Fetched {len(quotes)}/{len(settings.WATCHLIST)} stocks")

for symbol, quote in list(quotes.items())[:3]:
    print(f"  {symbol}: ${quote.price:.2f} ({quote.change_percent:+.2f}%)")

if len(quotes) == len(settings.WATCHLIST):
    print("\n✅ All stocks fetched successfully!")
else:
    print(f"\n⚠️  Only fetched {len(quotes)}/{len(settings.WATCHLIST)} stocks")

print("="*60 + "\n")
```

Run test:
```bash
python3 test_polygon.py
```

---

## Getting Help

### Polygon.io Support
- **Documentation:** https://polygon.io/docs
- **API Reference:** https://polygon.io/docs/stocks/get_v2_aggs_ticker__stocksticker__prev
- **Support Email:** support@polygon.io
- **Discord Community:** https://polygon.io/discord

### Market Alerts Issues
- Check logs: `tail -f logs/market_alerts.log`
- View GitHub issues: https://github.com/rsingla/market-alerts/issues

---

## Summary

### Quick Setup (5 minutes):

1. **Get API key:** https://polygon.io → Sign up → Copy key
2. **Add to .env:** `POLYGON_API_KEY=pk_your_key`
3. **Restart app:** `pkill -f streamlit && python3 -m streamlit run app_dashboard.py &`
4. **Verify:** Check logs for "✓ Polygon.io success"

### For Production:

- **Upgrade to BASIC plan:** $29/month unlimited calls
- **Keep fallbacks enabled:** USE_YFINANCE=true
- **Monitor usage:** Check Polygon dashboard
- **Set up alerts:** Get notified before hitting limits

### Next Steps:

- ✅ Polygon.io integration complete
- ✅ Intelligent fallback system ready
- ✅ No more Yahoo Finance rate limiting
- ✅ Production-ready data pipeline

Your Market Alerts system is now using professional-grade market data! 🚀

---

## Changelog

- **2025-01-02:** Added Polygon.io integration
- **2025-01-02:** Implemented intelligent fallback system
- **2025-01-02:** Updated priority: Polygon > yfinance > Alpha Vantage
