# Alpaca Markets Integration - FREE Unlimited Market Data!

## Why Alpaca?

Alpaca provides **completely FREE, unlimited real-time and historical market data** with no rate limits!

### Benefits:
- ✅ **100% FREE** - No credit card required
- ✅ **Unlimited API calls** - No rate limiting
- ✅ **Real-time data** - Latest quotes and trades
- ✅ **Historical data** - For technical indicators
- ✅ **Reliable** - Professional-grade infrastructure
- ✅ **No trading required** - Data-only access

### Comparison:

| Provider | Cost | Rate Limit | Data Quality |
|----------|------|------------|--------------|
| **Alpaca** | **FREE** | **Unlimited** | **Excellent** |
| Polygon.io | $29/mo | 5/min (free) | Excellent |
| Yahoo Finance | Free | Frequent 429 | Poor |
| Alpha Vantage | Free | 25/day | Good |

---

## Quick Setup (5 Minutes)

### Step 1: Create FREE Alpaca Account

1. Visit: **https://alpaca.markets/data**
2. Click "Sign Up" (top right)
3. Fill in:
   - Email address
   - Password
   - Name
4. Click "Create Account"
5. Verify your email (check inbox)

**Note:** You do NOT need to link a bank account or add payment info. Data is completely free!

### Step 2: Get Your API Keys

1. Log in to Alpaca dashboard
2. Click "Generate API Keys" or go to: https://app.alpaca.markets/paper/dashboard/overview
3. You'll see two keys:
   - **API Key ID** (starts with `PK...`)
   - **Secret Key** (starts with `...`)
4. Copy both keys (you'll need them in Step 3)

**Important:** Use the **Paper Trading** keys (not Live Trading). Paper keys give you free data access without any risk.

### Step 3: Add Keys to .env File

Open your `.env` file and update these lines:

```env
# Alpaca (FREE - Unlimited market data, no credit card required)
ALPACA_API_KEY=PKxxxxxxxxxxxxxxxxxxx
ALPACA_SECRET_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ALPACA_BASE_URL=https://paper-api.alpaca.markets
```

**Example:**
```env
ALPACA_API_KEY=PKABCDEF123456789
ALPACA_SECRET_KEY=abc123def456ghi789jkl012mno345pqr678stu901vwx234
ALPACA_BASE_URL=https://paper-api.alpaca.markets
```

### Step 4: Restart the Application

```bash
# Stop everything
pkill -f streamlit
pkill -f main.py

# Start dashboard
python3 -m streamlit run app_dashboard.py --server.port=8502 &

# Start alerts
python3 main.py &
```

### Step 5: Verify It's Working

Check the logs:

```bash
tail -f logs/market_alerts.log
```

**Look for:**
```
INFO | Trying Alpaca for AAPL...
INFO | ✓ Alpaca success for AAPL
INFO | Successfully fetched 8/8 quotes
```

✅ **Done!** Your system now has unlimited free market data!

---

## How It Works

### Automatic Fallback Chain

The system tries data sources in this order:

1. **Alpaca** (FREE unlimited) ← **Tries first!**
2. **Polygon.io** (paid or 5/min free)
3. **Yahoo Finance** (free but rate-limited)
4. **Alpha Vantage** (25/day free)

### What Alpaca Provides

- **Current Prices** - Real-time stock quotes
- **Daily Bars** - Open, High, Low, Close, Volume
- **Historical Data** - For technical indicators (RSI, MACD, etc.)
- **Trade Data** - Latest executed trades
- **Quote Data** - Bid/ask spreads

---

## Troubleshooting

### "No Alpaca data for AAPL"

**Possible reasons:**
1. API keys not added to .env
2. Application not restarted
3. Invalid API keys
4. Market is closed (some data unavailable)

**Solution:**
```bash
# Verify API keys are set
cat .env | grep ALPACA

# Should show:
# ALPACA_API_KEY=PKxxxxxxxxx
# ALPACA_SECRET_KEY=xxxxxxxxx
# NOT: ALPACA_API_KEY=your_alpaca_api_key

# Restart application
pkill -f streamlit && pkill -f main.py
python3 -m streamlit run app_dashboard.py --server.port=8502 &
python3 main.py &
```

### "Authentication error"

**Problem:** Invalid API keys

**Solution:**
- Check for typos in .env
- Make sure you copied the full keys (they're long!)
- Verify keys are active in Alpaca dashboard
- Make sure you're using **Paper Trading** keys (not Live)

### "Symbol not found"

**Problem:** Invalid stock symbol

**Solution:**
- Check the symbol is correct (e.g., AAPL not APPLE)
- Some stocks may not be available in Alpaca's database
- Try a different symbol to verify integration is working

---

## API Key Security

### Important Security Notes:

1. **Never commit .env to git**
   - Already in `.gitignore`
   - Double check: `git status` should not show .env

2. **Paper Trading Only**
   - We're using paper trading keys
   - No real money at risk
   - Can't execute actual trades

3. **Regenerate if Exposed**
   - If you accidentally expose your keys, regenerate them
   - Go to Alpaca dashboard → Regenerate API Keys

---

## FAQs

### Q: Do I need to deposit money?
**A:** No! Data access is completely free, no deposit required.

### Q: Can Alpaca execute trades through this integration?
**A:** No. We're only using the data API, not the trading API. Your account is safe.

### Q: What's the difference between Paper and Live keys?
**A:** Paper keys access simulated trading with fake money. Live keys access real trading. We use Paper keys for safety, and they provide the same data.

### Q: Is there a rate limit?
**A:** No! Alpaca provides unlimited API calls for market data.

### Q: What markets does Alpaca cover?
**A:** US stocks (NYSE, NASDAQ) and some crypto. Perfect for stocks like AAPL, GOOGL, TSLA, SPY, QQQ, etc.

### Q: How recent is the data?
**A:** Real-time! Typically updated within seconds.

---

## Next Steps

### Immediate
1. ✅ Get Alpaca API keys
2. ✅ Add to .env file
3. ✅ Restart application
4. ✅ Verify data is flowing

### Optional Enhancements
- Add more stocks to watchlist
- Increase check frequency (no rate limits!)
- Enable historical data analysis
- Set up real-time streaming (advanced)

---

## Support

### Need Help?

1. **Check logs first:**
   ```bash
   tail -100 logs/market_alerts.log
   ```

2. **Alpaca Documentation:**
   - Data API: https://alpaca.markets/docs/api-references/market-data-api/
   - Getting Started: https://alpaca.markets/learn/

3. **Alpaca Support:**
   - Email: support@alpaca.markets
   - Slack: alpaca-community.slack.com

---

## Summary

✅ **Alpaca integrated** - FREE unlimited market data
✅ **Primary data source** - Tries first in fallback chain
✅ **No rate limiting** - Make as many calls as you want
✅ **Easy setup** - Just 5 minutes to configure
✅ **Safe** - Paper trading keys, no risk

**Your Action:** Sign up at alpaca.markets/data and add keys to .env!

**Time required:** 5 minutes
**Cost:** $0 (completely free forever)
**Result:** Unlimited reliable market data 24/7

---

Your Market Alerts system is now future-proof with FREE unlimited data! 🚀
