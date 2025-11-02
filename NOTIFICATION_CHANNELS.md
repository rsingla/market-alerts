# Notification Channels - Quick Reference

Market Alerts now supports **5 different notification channels**! Choose the one that works best for you.

## Quick Comparison

| Channel | Setup Time | Difficulty | Reliability | Free Tier | Recommended? |
|---------|------------|------------|-------------|-----------|--------------|
| **Email (Brevo)** | 5 min | ⭐ | ⭐⭐⭐⭐⭐ | 300/day | ⭐ **YES** |
| **Telegram** | 3 min | ⭐⭐ | ⭐⭐⭐⭐⭐ | Unlimited | ⭐ **YES** |
| **Signal** | 15 min | ⭐⭐⭐ | ⭐⭐⭐⭐ | Unlimited | Maybe |
| **WhatsApp Web** | 2 min | ⭐⭐ | ⭐⭐⭐ | Unlimited | Testing only |
| **WhatsApp (Twilio)** | 20 min | ⭐⭐⭐⭐ | ⭐⭐⭐ | Complex | No |

## Top Recommendations

### 🏆 Best Overall: Email (Brevo)
- **Perfect for:** Everyone
- **Why:** Most reliable, beautiful HTML emails, works anywhere
- **Setup:** [BREVO_SETUP.md](BREVO_SETUP.md)

### 🥈 Best for Mobile: Telegram
- **Perfect for:** Users who want instant mobile notifications
- **Why:** Super easy setup, reliable, works great on phones
- **Setup:** [MESSAGING_SETUP_GUIDE.md](MESSAGING_SETUP_GUIDE.md#option-2-telegram-)

## Auto-Selection Priority

The system automatically chooses the first configured channel:

```
1. Email (Brevo)         → If BREVO_API_KEY is set
2. Telegram              → If TELEGRAM_BOT_TOKEN is set
3. Signal                → If SIGNAL_SENDER_NUMBER is set
4. WhatsApp (Twilio)     → If TWILIO_ACCOUNT_SID is set
5. WhatsApp Web          → If WHATSAPP_WEB_RECIPIENT is set
```

You can configure multiple channels for automatic fallback!

## Quick Setup Links

### Email (Brevo) - 5 minutes ⭐ RECOMMENDED
```env
BREVO_API_KEY=xkeysib-your-key
RECIPIENT_EMAIL=you@email.com
```
**Guide:** [BREVO_SETUP.md](BREVO_SETUP.md)

### Telegram - 3 minutes ⭐ EASY
```env
TELEGRAM_BOT_TOKEN=123456:ABC-DEF
TELEGRAM_CHAT_ID=123456789
```
**Guide:** [MESSAGING_SETUP_GUIDE.md](MESSAGING_SETUP_GUIDE.md#option-2-telegram-)

### Signal - 15 minutes
```env
SIGNAL_SENDER_NUMBER=+1234567890
SIGNAL_RECIPIENT_NUMBER=+1234567890
```
**Guide:** [MESSAGING_SETUP_GUIDE.md](MESSAGING_SETUP_GUIDE.md#option-3-signal)

### WhatsApp Web - 2 minutes (NOT for production)
```env
WHATSAPP_WEB_RECIPIENT=+1234567890
```
**Guide:** [MESSAGING_SETUP_GUIDE.md](MESSAGING_SETUP_GUIDE.md#option-4-whatsapp-web-pywhatkit)

### WhatsApp (Twilio) - 20 minutes (NOT recommended)
```env
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_WHATSAPP_TO=whatsapp:+1234567890
```
**Guide:** [WHATSAPP_SETUP.md](WHATSAPP_SETUP.md)

## Testing Your Setup

After configuration, test each channel:

```bash
# Email
python3 -m notifications.email_sender

# Telegram
python3 -m notifications.telegram_sender

# Signal
python3 -m notifications.signal_sender

# WhatsApp Web
python3 -m notifications.whatsapp_web_sender

# Check which channel is active
python3 -m config.settings
```

## Features by Channel

| Feature | Email | Telegram | Signal | WhatsApp Web | Twilio |
|---------|-------|----------|--------|--------------|---------|
| Rich Formatting | ✅ HTML | ✅ Markdown | ❌ | ✅ | ❌ |
| Clickable Links | ✅ | ✅ | ✅ | ✅ | ✅ |
| Message History | ✅ | ✅ | ✅ | ✅ | ❌ |
| Multi-Device | ✅ | ✅ | ✅ | ❌ | ✅ |
| Offline Delivery | ✅ | ✅ | ✅ | ❌ | ✅ |
| Needs Running PC | ❌ | ❌ | ❌ | ✅ | ❌ |

## Common Questions

### Q: Can I use multiple channels at once?
**A:** Yes! Configure as many as you want. The system uses the first one that's configured (in priority order).

### Q: Which is the easiest?
**A:** Email (Brevo) - just need an API key, no phone required.

### Q: Which is fastest to set up?
**A:** Telegram - takes about 3 minutes from start to finish.

### Q: Can I switch channels without changing code?
**A:** Yes! Just update your `.env` file and restart the application.

### Q: Do I need a phone number?
**A:**
- Email: ❌ No
- Telegram: ❌ No
- Signal: ✅ Yes
- WhatsApp Web: ✅ Yes
- Twilio: ✅ Yes

### Q: Which works best on mobile?
**A:** Telegram - designed for mobile-first notifications.

### Q: Which is most reliable?
**A:** Email (Brevo) - enterprise-grade email service with 99.9% uptime.

## Troubleshooting

### No notifications received?
1. Check configuration: `python3 -m config.settings`
2. Test the channel: `python3 -m notifications.{channel}_sender`
3. Check logs: `tail -f logs/market_alerts.log`

### "No notification channel configured"?
- Make sure you've added at least one channel to your `.env` file
- Restart the application after making changes

### Channel not being used?
- Remember priority order (Email > Telegram > Signal > WhatsApp Twilio > WhatsApp Web)
- The first configured channel is used
- To use a lower-priority channel, remove/comment out higher-priority ones

## Full Documentation

- [Complete Setup Guide](MESSAGING_SETUP_GUIDE.md) - All channels in detail
- [Email Setup](BREVO_SETUP.md) - Detailed Brevo guide
- [Configuration Guide](CONFIGURATION_GUIDE.md) - All settings explained

## Need Help?

1. Check the guides above
2. Run test scripts to diagnose issues
3. Check `logs/market_alerts.log` for errors
4. Verify your `.env` configuration

---

**Ready to get started?** We recommend **Email (Brevo)** for most users - it's the easiest and most reliable option! 🎉
