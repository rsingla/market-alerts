# Yahoo Finance Rate Limiting - Solutions Guide

## The Problem

**Symptom:** Dashboard shows "No market data available"

**Root Cause:** Yahoo Finance API is rate limiting requests with `429 Too Many Requests` errors

```
ERROR | yfinance error for AAPL: 429 Client Error: Too Many Requests
INFO  | Successfully fetched 0/8 quotes
```

This happens when you make too many requests to Yahoo Finance in a short period. Common causes:
- Testing/development with frequent refreshes
- Running multiple instances of the app
- High-frequency data fetching during development

---

## Solution 1: Wait for Rate Limit Reset ⏳

**Difficulty:** Easy
**Cost:** Free
**Time:** 15-60 minutes

Yahoo Finance rate limits typically reset within:
- **15-30 minutes** for light rate limiting
- **30-60 minutes** for heavy rate limiting
- **Up to 24 hours** in extreme cases (rare)

**No action required** - just wait and the data will start working again.

---

## Solution 2: Use Alpha Vantage API Fallback ✅ **RECOMMENDED**

**Difficulty:** Easy
**Cost:** Free (500 calls/day)
**Time:** 5 minutes

### Step 1: Get Alpha Vantage API Key

1. Visit: https://www.alphavantage.co/support/#api-key
2. Enter your email
3. Click "GET FREE API KEY"
4. Copy the API key (looks like: `ABCD1234EFGH5678`)

### Step 2: Update .env File

```env
# Replace the placeholder with your real API key
ALPHA_VANTAGE_API_KEY=ABCD1234EFGH5678
```

### Step 3: Restart Application

```bash
# Stop all processes
pkill -f "python3 main.py"
pkill -f "streamlit"

# Start dashboard
python3 -m streamlit run app_dashboard.py --server.port=8502 &

# Start alert scheduler
python3 main.py &
```

### How It Works

The system now has **intelligent fallback**:
1. First tries Yahoo Finance (yfinance)
2. If yfinance fails (429 error), automatically tries Alpha Vantage
3. If both fail, returns no data

You'll see this in logs:
```
ERROR | yfinance error for AAPL: 429 Client Error: Too Many Requests
INFO  | yfinance failed for AAPL, trying Alpha Vantage fallback...
INFO  | Successfully fetched 8/8 quotes  # ✓ Success via Alpha Vantage!
```

### Alpha Vantage Limits

- **Free Tier:** 500 API calls/day
- **Rate:** 5 calls/minute
- **Good for:** 8 stocks × 60 checks/day = 480 calls/day ✓

---

## Solution 3: Switch Permanently to Alpha Vantage

**When:** If Yahoo Finance is consistently unreliable

### Update .env

```env
# Disable yfinance
USE_YFINANCE=false

# Use Alpha Vantage as primary
ALPHA_VANTAGE_API_KEY=your_real_api_key_here
```

**Pros:**
- More reliable rate limits
- Official API with documented limits
- Better for production use

**Cons:**
- Limited to 500 calls/day
- Slower response times
- No historical data beyond basics

---

## Solution 4: Add Time Delays Between Requests

**For development/testing to avoid rate limits**

### Current Issue
When testing, the app might fetch data too frequently:
- Dashboard refresh: every page load
- Scheduler: every 60 minutes
- Manual testing: multiple rapid refreshes

### Solution

Modify `config/settings.py`:

```python
# Add rate limiting
CACHE_DURATION = 600  # 10 minutes (increased from 5)
CHECK_INTERVAL_MINUTES = 60  # Keep at 60 for production
```

This ensures the same data is cached and not refetched too quickly.

---

## Solution 5: Use Request Throttling

**For advanced users**

Install `ratelimit` package:

```bash
pip install ratelimit
```

Modify `data/market_data.py`:

```python
from ratelimit import limits, sleep_and_retry

# Allow 5 calls per minute
@sleep_and_retry
@limits(calls=5, period=60)
def _get_yfinance_quote(symbol: str) -> Optional[StockQuote]:
    # ... existing code ...
```

This automatically throttles requests to stay within limits.

---

## Quick Reference: Which Solution to Use?

| Situation | Best Solution | Time to Fix |
|-----------|---------------|-------------|
| Testing right now, need data ASAP | Get Alpha Vantage API key | 5 minutes |
| Occasional rate limiting | Wait + use cache | 15-30 min |
| Frequent development | Alpha Vantage fallback | 5 minutes |
| Production deployment | Alpha Vantage primary | 5 minutes |
| Heavy usage (>500 stocks/day) | Paid API tier or Finnhub | Varies |

---

## Checking Current Status

### View Logs

```bash
# Check dashboard logs
tail -f logs/market_alerts.log

# Check for rate limit errors
grep "429" logs/market_alerts.log | tail -20
```

### Test Data Fetching

```bash
# Test single stock
python3 -c "from data.market_data import get_stock_quote; quote = get_stock_quote('AAPL'); print(f'Success: {quote is not None}')"

# Test full watchlist
python3 -c "from data.market_data import get_market_summary; quotes = get_market_summary(); print(f'Fetched: {len(quotes)}/8 stocks')"
```

**Expected Output:**
- **Before fix:** `Fetched: 0/8 stocks`
- **After fix:** `Fetched: 8/8 stocks`

---

## Preventing Future Rate Limiting

### Best Practices

1. **Cache Aggressively**
   - Use longer cache durations during development
   - Only refresh when necessary

2. **Limit Concurrent Requests**
   - Don't run multiple instances simultaneously
   - Avoid rapid dashboard refreshes

3. **Use Fallback APIs**
   - Always have Alpha Vantage configured as backup
   - Consider Finnhub as tertiary fallback

4. **Monitor Usage**
   - Check logs for frequent API errors
   - Track number of daily API calls

5. **Production Settings**
   ```env
   # Recommended for production
   CACHE_DURATION=600          # 10 minutes
   CHECK_INTERVAL_MINUTES=60   # 1 hour
   USE_YFINANCE=true          # Primary source
   ALPHA_VANTAGE_API_KEY=xxx  # Fallback configured
   ```

---

## Alternative Data Sources

If both Yahoo Finance and Alpha Vantage are insufficient:

### Finnhub (FREE - 60 calls/minute)
```env
FINNHUB_API_KEY=your_finnhub_key
```
Get key: https://finnhub.io

### Polygon.io (FREE - 5 calls/minute)
Get key: https://polygon.io

### IEX Cloud (FREE tier available)
Get key: https://iexcloud.io

---

## Current Implementation Status

✅ **Implemented:** Intelligent fallback system
✅ **Implemented:** Alpha Vantage integration
✅ **Implemented:** Error handling and logging
⏳ **Available:** Waiting for your Alpha Vantage API key

**Next Steps:**
1. Get Alpha Vantage API key (5 minutes)
2. Add to `.env` file
3. Restart application
4. Data will start flowing via Alpha Vantage fallback

---

## Testing the Fix

### Before Adding API Key

```bash
# Attempt to fetch data - should fail with 429 errors
python3 -m data.market_data
```

**Expected:** `0/8 quotes fetched`

### After Adding API Key

```bash
# Should succeed via Alpha Vantage fallback
python3 -m data.market_data
```

**Expected:** `8/8 quotes fetched`

---

## Support

- **Yahoo Finance Status:** https://status.yahoo.com
- **Alpha Vantage Support:** https://www.alphavantage.co/support/
- **Rate Limit Info:** See logs at `logs/market_alerts.log`

---

## Summary

**The problem:** Yahoo Finance rate limiting (429 errors)
**The fix:** Intelligent fallback to Alpha Vantage API
**Your action:** Get free API key and add to `.env`
**Time required:** 5 minutes
**Cost:** Free (500 calls/day)

Once configured, your Market Alerts system will:
1. Try Yahoo Finance first (fast, no API key needed)
2. Fall back to Alpha Vantage on failures (reliable, rate-limited)
3. Continue working even during heavy Yahoo Finance rate limiting

The system is now more resilient and production-ready! 🎉
