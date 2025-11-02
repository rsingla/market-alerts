# Messaging Setup Guide

Complete guide for setting up all 5 notification channels for Market Alerts.

## Priority & Recommendations

The system automatically chooses the first configured channel in this order:

1. **Email (Brevo)** - ⭐ **RECOMMENDED** - Easiest, most reliable
2. **Telegram** - ⭐ **HIGHLY RECOMMENDED** - Super easy, just need bot token
3. **Signal** - Requires signal-cli installation
4. **WhatsApp (Twilio)** - Complex setup with sandbox
5. **WhatsApp Web** - Browser automation (least reliable)

---

## Option 1: Email via Brevo (Sendinblue) ⭐

**Difficulty:** ⭐☆☆☆☆ (Easiest)
**Setup Time:** 5 minutes
**Reliability:** ⭐⭐⭐⭐⭐

### Why Choose This?
- ✅ FREE: 300 emails/day forever
- ✅ No phone required
- ✅ Beautiful HTML formatted alerts
- ✅ Works immediately
- ✅ Most reliable option

### Setup Steps

1. **Create Brevo Account** (2 minutes)
   - Go to https://app.brevo.com/account/register
   - Sign up with your email
   - Verify your email address

2. **Get API Key** (1 minute)
   - Once logged in, click your name (top right)
   - Go to **SMTP & API** → **API Keys**
   - Click **Generate a new API key**
   - Name it: "Market Alerts"
   - Copy the API key (starts with `xkeysib-...`)
   - ⚠️ SAVE IT - you can't see it again!

3. **Configure .env File**
   ```env
   BREVO_API_KEY=xkeysib-your-actual-api-key-here
   SENDER_EMAIL=alerts@marketalerts.com
   SENDER_NAME=Market Alerts
   RECIPIENT_EMAIL=your.email@gmail.com
   ```

4. **Test It**
   ```bash
   python3 -m notifications.email_sender
   # Type 'y' when prompted
   ```

See [BREVO_SETUP.md](BREVO_SETUP.md) for detailed guide.

---

## Option 2: Telegram ⭐

**Difficulty:** ⭐⭐☆☆☆ (Very Easy)
**Setup Time:** 3 minutes
**Reliability:** ⭐⭐⭐⭐⭐

### Why Choose This?
- ✅ FREE: Unlimited messages
- ✅ Super easy setup (just need bot token)
- ✅ Instant delivery
- ✅ Rich formatting with Markdown
- ✅ Works on all devices

### Setup Steps

1. **Create Telegram Bot** (2 minutes)
   - Open Telegram and search for `@BotFather`
   - Send `/newbot` command
   - Follow prompts to:
     - Choose a name (e.g., "Market Alerts")
     - Choose a username (e.g., "my_market_alerts_bot")
   - Copy the bot token (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

2. **Get Your Chat ID** (1 minute)
   - Search for `@userinfobot` on Telegram
   - Start a chat with it
   - It will send you your chat ID (a number)
   - Copy this number

3. **Configure .env File**
   ```env
   TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   TELEGRAM_CHAT_ID=123456789
   ```

4. **Start Your Bot**
   - Search for your bot username on Telegram
   - Click START button
   - This allows the bot to send you messages

5. **Test It**
   ```bash
   python3 -m notifications.telegram_sender
   # Type 'y' when prompted
   ```

### Troubleshooting

**"Forbidden: bot can't initiate conversation"**
- Solution: You must click START on your bot first

**"Chat not found"**
- Solution: Double-check your chat ID with @userinfobot

---

## Option 3: Signal

**Difficulty:** ⭐⭐⭐☆☆ (Moderate)
**Setup Time:** 15 minutes
**Reliability:** ⭐⭐⭐⭐☆

### Why Choose This?
- ✅ FREE: Unlimited messages
- ✅ Very private and secure
- ✅ No central service required
- ⚠️ Requires signal-cli installation
- ⚠️ More complex setup

### Setup Steps

1. **Install signal-cli**

   **macOS:**
   ```bash
   brew install signal-cli
   ```

   **Linux (Ubuntu/Debian):**
   ```bash
   # Install Java first
   sudo apt install default-jre

   # Download signal-cli
   wget https://github.com/AsamK/signal-cli/releases/latest/download/signal-cli.tar.gz
   tar xf signal-cli.tar.gz -C /opt
   sudo ln -sf /opt/signal-cli/bin/signal-cli /usr/local/bin/
   ```

2. **Register Your Phone Number**
   ```bash
   # Request verification code
   signal-cli -a +1234567890 register

   # You'll receive an SMS with a code
   # Verify with the code
   signal-cli -a +1234567890 verify CODE-FROM-SMS
   ```

3. **Configure .env File**
   ```env
   SIGNAL_SENDER_NUMBER=+1234567890
   SIGNAL_RECIPIENT_NUMBER=+1234567890
   SIGNAL_CLI_PATH=signal-cli
   ```

4. **Test It**
   ```bash
   python3 -m notifications.signal_sender
   # Type 'y' when prompted
   ```

### Troubleshooting

**"signal-cli not found"**
- Solution: Make sure signal-cli is in your PATH
- Try: `which signal-cli`

**"Not registered"**
- Solution: Complete the registration steps above

**"Untrusted identity"**
- Solution: Send a manual message first to establish trust
- `signal-cli -a +sender send -m "test" +recipient`

---

## Option 4: WhatsApp Web (pywhatkit)

**Difficulty:** ⭐⭐☆☆☆ (Easy but quirky)
**Setup Time:** 2 minutes
**Reliability:** ⭐⭐⭐☆☆

### Why Choose This?
- ✅ FREE: Unlimited messages
- ✅ No API keys needed
- ✅ Direct WhatsApp messages
- ⚠️ Requires WhatsApp Web to be logged in
- ⚠️ Opens browser tabs
- ⚠️ Computer must be running

### How It Works
- Uses browser automation to open WhatsApp Web
- Automatically types and sends messages
- Requires you to be logged into WhatsApp Web

### Setup Steps

1. **Login to WhatsApp Web**
   - Go to https://web.whatsapp.com
   - Scan QR code with your phone
   - Keep "Keep me signed in" checked

2. **Configure .env File**
   ```env
   WHATSAPP_WEB_RECIPIENT=+1234567890
   WHATSAPP_WEB_WAIT_TIME=15
   WHATSAPP_WEB_CLOSE_TAB=true
   ```

   **Phone Number Format:** Must include country code with +, no spaces
   - ✅ Correct: `+1234567890`
   - ❌ Wrong: `1234567890` (missing +)
   - ❌ Wrong: `+1 234 567 890` (spaces)

3. **Test It**
   ```bash
   python3 -m notifications.whatsapp_web_sender
   # Type 'y' when prompted
   ```

   ⚠️ **IMPORTANT:**
   - Do NOT use your mouse/keyboard while the message is being sent
   - The browser will open automatically and send the message
   - Takes about 15-20 seconds total

### Troubleshooting

**"Not logged into WhatsApp Web"**
- Solution: Open https://web.whatsapp.com and log in

**"Browser opens but message doesn't send"**
- Solution: Increase WHATSAPP_WEB_WAIT_TIME to 20 or 25

**"Invalid phone number"**
- Solution: Make sure format is +1234567890 (with + and country code)

---

## Option 5: WhatsApp via Twilio (Original)

**Difficulty:** ⭐⭐⭐⭐☆ (Complex)
**Setup Time:** 20 minutes
**Reliability:** ⭐⭐⭐☆☆

See [WHATSAPP_SETUP.md](WHATSAPP_SETUP.md) for full details.

This option requires:
- Twilio account setup
- Sandbox configuration
- Phone number verification
- Special join code

**We recommend using Email or Telegram instead.**

---

## Comparison Table

| Feature | Email | Telegram | Signal | WhatsApp Web | WhatsApp (Twilio) |
|---------|-------|----------|--------|--------------|-------------------|
| Setup Time | 5 min | 3 min | 15 min | 2 min | 20 min |
| Difficulty | ⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| Reliability | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| Free Tier | 300/day | Unlimited | Unlimited | Unlimited | Complex |
| Phone Required | ❌ | ❌ | ✅ | ✅ | ✅ |
| Special Setup | API Key | Bot Token | signal-cli | WhatsApp Web | Sandbox |
| Rich Formatting | ✅ HTML | ✅ Markdown | ❌ Text | ✅ | ❌ Text |
| Needs Running PC | ❌ | ❌ | ❌ | ✅ | ❌ |

---

## Testing Your Setup

After configuring any channel, test it:

### Email
```bash
python3 -m notifications.email_sender
```

### Telegram
```bash
python3 -m notifications.telegram_sender
```

### Signal
```bash
python3 -m notifications.signal_sender
```

### WhatsApp Web
```bash
python3 -m notifications.whatsapp_web_sender
```

### Check Configuration
```bash
python3 -m config.settings
```

This will show which channels are configured.

---

## Using Multiple Channels

You can configure multiple channels! The system will use the first available one in priority order:

1. Email (if BREVO_API_KEY is set)
2. Telegram (if TELEGRAM_BOT_TOKEN is set)
3. Signal (if SIGNAL_SENDER_NUMBER is set)
4. WhatsApp Twilio (if TWILIO_ACCOUNT_SID is set)
5. WhatsApp Web (if WHATSAPP_WEB_RECIPIENT is set)

This provides automatic fallback if one channel fails.

---

## Recommendations by Use Case

### Best for Most Users
→ **Email (Brevo)** - Most reliable, easy setup, works anywhere

### Best for Mobile-First Users
→ **Telegram** - Instant notifications on phone, very easy setup

### Best for Privacy
→ **Signal** - Most secure, but requires more setup

### Best for Quick Testing
→ **Telegram** - Fastest to set up and test

### NOT Recommended
→ **WhatsApp Web** - Too unreliable for production use
→ **WhatsApp Twilio** - Too complex with sandbox limitations

---

## Getting Help

If you have issues:

1. Check the troubleshooting section for your channel
2. Run `python3 -m config.settings` to verify configuration
3. Check `logs/market_alerts.log` for errors
4. Test the channel with the test scripts above

---

## Ready to Start!

Once you've configured at least one channel:

```bash
# Start the dashboard
python3 -m streamlit run app_dashboard.py

# Or run the scheduler directly
python3 main.py
```

Your market alerts will now be sent to your configured channel! 🎉
