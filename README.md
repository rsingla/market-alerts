# Market Alerts - Real-time Financial Notifications to WhatsApp

A Python-based market monitoring system that sends real-time alerts about:
- Stock price movements
- Market news and events
- Economic indicators
- Earnings reports
- Custom watchlists

Delivers alerts directly to WhatsApp using Twilio API with hourly scheduled checks.

## Features

- 📊 **Real-time Market Data** - Track stocks, indices, and cryptocurrencies
- 📰 **News Aggregation** - Financial news from multiple sources
- 📱 **WhatsApp Integration** - Instant alerts to your phone
- ⏰ **Scheduled Monitoring** - Hourly checks during market hours
- 🎯 **Custom Watchlists** - Monitor your favorite stocks
- 📈 **Price Alerts** - Trigger on price movements (±3%, ±5%, etc.)
- 🔔 **Breaking News** - Filter important market events

## Quick Start

### 1. Install Dependencies

```bash
pip install twilio requests schedule python-dotenv yfinance feedparser
```

### 2. Get API Keys

**Twilio (WhatsApp):**
1. Sign up at https://www.twilio.com
2. Get WhatsApp Sandbox or WhatsApp Business API
3. Note your Account SID and Auth Token

**Financial Data (Choose one or more):**
- Alpha Vantage: https://www.alphavantage.co/support/#api-key (FREE)
- News API: https://newsapi.org/register (FREE 1000 requests/day)
- Finnhub: https://finnhub.io (FREE 60 calls/minute)

### 3. Configure `.env`

```env
# Twilio WhatsApp
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
TWILIO_WHATSAPP_TO=whatsapp:+1234567890

# Financial APIs
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
NEWS_API_KEY=your_news_api_key
FINNHUB_API_KEY=your_finnhub_key

# Alert Settings
WATCHLIST=AAPL,GOOGL,MSFT,TSLA,SPY
PRICE_ALERT_THRESHOLD=3.0
CHECK_INTERVAL_MINUTES=60
MARKET_HOURS_ONLY=true
```

### 4. Run the Application

```bash
# Start the scheduled alert system (recommended)
python3 main.py

# Or run the web dashboard
streamlit run app_dashboard.py

# Or test individual modules
python3 -m config.settings           # Test configuration
python3 -m data.market_data          # Test market data fetching
python3 -m data.news_fetcher         # Test news fetching
python3 -m alerts.alert_engine       # Test alert engine
python3 -m notifications.whatsapp_sender  # Test WhatsApp
```

## Architecture

```
market_alerts/
├── main.py                    # Main entry point with scheduler
├── app_dashboard.py           # Streamlit web dashboard
├── config/
│   └── settings.py           # Configuration loader
├── data/
│   ├── market_data.py        # Stock price fetching (yfinance/Alpha Vantage)
│   ├── news_fetcher.py       # News aggregation (News API/RSS)
│   └── cache.py              # Caching layer
├── alerts/
│   ├── alert_engine.py       # Alert detection engine
│   ├── filters.py            # Alert filtering logic
│   └── formatters.py         # Message formatting
├── notifications/
│   └── whatsapp_sender.py    # WhatsApp integration (Twilio)
├── scheduler/
│   └── alert_scheduler.py    # APScheduler background jobs
├── utils/
│   ├── logger.py             # Logging configuration
│   └── market_hours.py       # Market hours checking
├── .env                      # API keys (not in git)
├── .env.example              # Example configuration
└── requirements.txt          # Python dependencies
```

## Usage Examples

### Monitor Specific Stocks

```python
from market_alerts import MarketAlerts

alerts = MarketAlerts()

# Check single stock
alerts.check_stock('AAPL')

# Check watchlist
alerts.check_watchlist(['AAPL', 'GOOGL', 'MSFT'])

# Get market summary
alerts.send_market_summary()
```

### Custom Price Alerts

```python
# Alert if price moves > 5%
alerts.check_price_movement('TSLA', threshold=5.0)

# Alert on specific price
alerts.set_price_target('AAPL', target_price=180.00)
```

### News Monitoring

```python
from news_fetcher import NewsFetcher

news = NewsFetcher()

# Get breaking news
news.get_breaking_news(keywords=['earnings', 'fed', 'rate'])

# Stock-specific news
news.get_stock_news('AAPL')
```

## Alert Types

### 1. Price Movement Alerts
```
🔥 PRICE ALERT 🔥
AAPL +4.2% → $185.50
Previous: $177.90
Volume: 89.2M (↑32%)
Time: 2:30 PM EST
```

### 2. Market Summary (Hourly)
```
📊 MARKET UPDATE 📊
S&P 500: +0.8% (4,589)
Nasdaq: +1.2% (14,203)
Dow: +0.5% (35,421)
VIX: 14.2 (-3%)
⏰ 3:00 PM EST
```

### 3. Breaking News
```
📰 BREAKING NEWS 📰
Fed Announces Rate Decision
• Raises rates by 0.25%
• Projects 2 more hikes in 2024
• Market reaction: Mixed
🔗 reuters.com/article/...
```

### 4. Earnings Alerts
```
💰 EARNINGS ALERT 💰
GOOGL Q4 2024
EPS: $1.64 (beat by $0.08)
Revenue: $86.3B (↑13%)
Reaction: +5.2% after hours
```

## Configuration

### Watchlist Settings

```python
# config.py
WATCHLIST = {
    'stocks': ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA'],
    'indices': ['SPY', 'QQQ', 'DIA'],
    'crypto': ['BTC-USD', 'ETH-USD']
}

# Alert thresholds
THRESHOLDS = {
    'small_move': 1.0,   # 1% movement
    'medium_move': 3.0,  # 3% movement
    'large_move': 5.0,   # 5% movement
    'volume_spike': 2.0  # 2x average volume
}
```

### Schedule Settings

```python
# Hourly during market hours (9:30 AM - 4:00 PM EST)
SCHEDULE = {
    'market_summary': '0 * 9-16 * * *',  # Every hour
    'news_check': '*/30 * * * * *',       # Every 30 minutes
    'watchlist_check': '*/15 * 9-16 * * *' # Every 15 min during market hours
}
```

## API Rate Limits

| Service | Free Tier | Recommendation |
|---------|-----------|----------------|
| Alpha Vantage | 5 calls/min, 500/day | Use for EOD data |
| News API | 1000 requests/day | Use for news only |
| Finnhub | 60 calls/minute | Use for real-time |
| Twilio WhatsApp | Pay-as-you-go | ~$0.005/message |

## Advanced Features

### Custom Filters

```python
# Only alert on significant moves
def filter_alerts(data):
    return (
        data['price_change_pct'] > 3.0 or
        data['volume_ratio'] > 2.0 or
        'earnings' in data.get('news', '').lower()
    )
```

### Multi-Channel Alerts

```python
# Send to multiple recipients
RECIPIENTS = [
    'whatsapp:+1234567890',  # Your number
    'whatsapp:+0987654321',  # Partner's number
]
```

### Historical Tracking

```python
# Track alert history
alerts.save_to_database()
alerts.generate_daily_report()
```

## Troubleshooting

### WhatsApp Not Receiving Messages

1. Check Twilio WhatsApp Sandbox is active
2. Verify phone number format: `whatsapp:+1234567890`
3. Join sandbox by sending "join <code>" to Twilio number
4. Check Twilio console for delivery status

### API Rate Limit Errors

1. Reduce check frequency
2. Use caching for repeated requests
3. Upgrade to paid API tier
4. Use multiple API providers

### No Alerts Firing

1. Check if watchlist stocks are valid
2. Verify market is open (if MARKET_HOURS_ONLY=true)
3. Lower threshold percentages
4. Check logs for errors

## Best Practices

1. **Start Small**: Test with 2-3 stocks first
2. **Use Caching**: Cache data for 5-15 minutes to reduce API calls
3. **Market Hours**: Only send alerts during trading hours
4. **Filter Noise**: Set appropriate thresholds (3-5% for price moves)
5. **Test Mode**: Use demo mode before going live

## Example Daily Workflow

```
9:30 AM  - Market Open Alert
10:00 AM - Hourly Summary
11:00 AM - Hourly Summary
12:00 PM - Hourly Summary + News Check
1:00 PM  - Hourly Summary
2:00 PM  - Earnings Alerts (if any)
3:00 PM  - Hourly Summary
4:00 PM  - Market Close Summary
```

## Future Enhancements

- [ ] Technical indicator alerts (RSI, MACD)
- [ ] Sentiment analysis from news
- [ ] Portfolio tracking integration
- [ ] Telegram/Discord support
- [ ] Web dashboard for alert history
- [ ] ML-based alert prioritization

## License

MIT License - Use freely

## Support

For issues or questions, create an issue in the GitHub repository.

---

**Built with**: Python, Twilio, Alpha Vantage, News API, YFinance
