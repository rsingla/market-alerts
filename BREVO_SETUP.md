# Brevo (Sendinblue) Email Setup Guide

Quick guide to set up email notifications via Brevo.

## Why Brevo?

- ✅ **FREE**: 300 emails/day forever
- ✅ **Easy setup**: 5 minutes
- ✅ **No phone required**: Unlike WhatsApp
- ✅ **Reliable**: Professional email service
- ✅ **No sandbox**: Works immediately
- ✅ **Beautiful emails**: HTML formatted alerts

## Step 1: Create Brevo Account (2 minutes)

1. Go to https://app.brevo.com/account/register
2. Sign up with your email
3. Verify your email address
4. Complete the quick profile setup

## Step 2: Get API Key (1 minute)

1. Once logged in, click your name (top right)
2. Go to **SMTP & API** → **API Keys**
3. Click **Generate a new API key**
4. Give it a name: "Market Alerts"
5. Copy the API key (starts with `xkeysib-...`)

**IMPORTANT:** Save this key immediately - you can't see it again!

## Step 3: Configure .env File (1 minute)

Open your `.env` file and add:

```env
# ===== EMAIL NOTIFICATIONS (Brevo) =====
BREVO_API_KEY=xkeysib-your-actual-api-key-here
SENDER_EMAIL=alerts@marketalerts.com
SENDER_NAME=Market Alerts
RECIPIENT_EMAIL=your.email@gmail.com    # YOUR actual email
```

**Replace:**
- `BREVO_API_KEY`: Your actual API key from step 2
- `RECIPIENT_EMAIL`: Your email where you want to receive alerts

## Step 4: Test It! (1 minute)

```bash
# Test email sending
python3 -m notifications.email_sender
# When prompted, type 'y' to send test email
```

Check your inbox (and spam folder) for the test email!

## Complete .env Example

```env
# Email (Brevo) - Recommended
BREVO_API_KEY=xkeysib-a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
SENDER_EMAIL=alerts@marketalerts.com
SENDER_NAME=Market Alerts
RECIPIENT_EMAIL=john.doe@gmail.com

# Other APIs
NEWS_API_KEY=6fe02601d916407c80aaf3f15bc9d5f8
FINNHUB_API_KEY=d439cbpr01qvk0jargsgd439cbpr01qvk0jargt0

# Watchlist
WATCHLIST=AAPL,GOOGL,MSFT,TSLA,NVDA,SPY,QQQ,DIA

# Thresholds
SMALL_MOVE_THRESHOLD=1.0
MEDIUM_MOVE_THRESHOLD=3.0
LARGE_MOVE_THRESHOLD=5.0
VOLUME_SPIKE_THRESHOLD=2.0

# Schedule
CHECK_INTERVAL_MINUTES=60
MARKET_HOURS_ONLY=true
```

## What You'll Receive

### Alert Email Example

```
Subject: 🔔 Market Alert: AAPL large_move

📊 Market Alerts
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚨 AAPL 📈

Price: $185.50
Change: +5.2% (+$9.25)
Range: $178.00 - $186.00

Updated: 2:30 PM ET

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Sent by Market Alerts System
2025-11-01 14:30:00 ET
```

### Summary Email Example

```
Subject: 🔔 Market Alerts - 3 Alerts

Market Alerts Summary
November 1, 2025 at 2:30 PM ET

You have 3 alerts:

══════════════════════════════
Alert #1
══════════════════════════════

🚨 AAPL 📈
Price: $185.50
Change: +5.2% (+$9.25)

══════════════════════════════
Alert #2
══════════════════════════════

⚠️ TSLA 📉
Price: $245.30
Change: -3.8% (-$9.70)
```

## Benefits vs WhatsApp

| Feature | Email (Brevo) | WhatsApp (Twilio) |
|---------|---------------|-------------------|
| Setup Time | 5 minutes | 15-20 minutes |
| Verification | Email only | Phone + Sandbox join |
| Free Tier | 300/day | Complex pricing |
| Reliability | High | Medium (sandbox issues) |
| Formatting | HTML + Text | Text only |
| Links | Clickable | Plain text |
| History | Full email history | Disappears |

## Troubleshooting

### "API key not configured"

**Problem:** API key missing or invalid
**Solution:**
1. Check .env file has `BREVO_API_KEY=xkeysib-...`
2. Restart the application
3. Run `python3 -m config.settings` to verify

### "No recipient email configured"

**Problem:** RECIPIENT_EMAIL not set
**Solution:**
1. Add `RECIPIENT_EMAIL=your.email@gmail.com` to .env
2. Restart the application

### "Email not received"

**Problem:** Email in spam or wrong address
**Solution:**
1. Check spam folder
2. Verify `RECIPIENT_EMAIL` is correct
3. Add `alerts@marketalerts.com` to contacts
4. Check Brevo dashboard for delivery status

### "API error 401"

**Problem:** Invalid API key
**Solution:**
1. Generate new API key in Brevo
2. Copy it carefully (no spaces)
3. Update in .env

## Free Tier Limits

- **300 emails/day** forever
- **Unlimited contacts**
- **Email support**
- **API access**

Perfect for personal market alerts!

## Upgrade (Optional)

If you need more than 300 emails/day:
- **Lite Plan**: $25/month for 20,000 emails
- **Premium**: $65/month for 40,000 emails

But 300/day = 9,000/month is plenty for most users!

## System Integration

The Market Alerts system **automatically** uses email if Brevo is configured:

```python
# The system automatically chooses the best method:
# 1. If BREVO_API_KEY is set → uses Email
# 2. Otherwise → tries WhatsApp
```

**No code changes needed!** Just configure `.env` and it works.

## Ready!

Once you have:
- ✅ Brevo account created
- ✅ API key added to .env
- ✅ Recipient email configured
- ✅ Test email sent successfully

You're ready to receive market alerts via email! 🎉

Start the system:
```bash
python3 main.py
```

Or use the dashboard:
```bash
python3 -m streamlit run app_dashboard.py
```

---

**Questions?** Check the logs:
```bash
tail -f logs/market_alerts.log
```
