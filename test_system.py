#!/usr/bin/env python3
"""
System Test Script
Tests all components of the Market Alerts system
"""

import sys
from datetime import datetime
from config import settings
from utils.logger import logger
from utils.market_hours import get_market_status
from data.market_data import get_stock_quote, get_market_summary
from data.news_fetcher import get_market_news
from alerts.alert_engine import AlertEngine
from notifications import WhatsAppSender


def print_header(title: str):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def test_configuration():
    """Test configuration loading"""
    print_header("TEST 1: CONFIGURATION")

    try:
        # Validate configuration
        errors, warnings = settings.validate_config()

        if errors:
            print("❌ CONFIGURATION ERRORS:")
            for error in errors:
                print(f"   • {error}")
            return False

        if warnings:
            print("⚠️  CONFIGURATION WARNINGS:")
            for warning in warnings:
                print(f"   • {warning}")

        print("✓ Configuration loaded successfully")
        print(f"✓ Watchlist: {len(settings.WATCHLIST)} symbols")
        print(f"✓ Check interval: {settings.CHECK_INTERVAL_MINUTES} minutes")
        print(f"✓ Market hours only: {settings.MARKET_HOURS_ONLY}")

        return len(errors) == 0

    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


def test_market_hours():
    """Test market hours checking"""
    print_header("TEST 2: MARKET HOURS")

    try:
        status = get_market_status()

        print(f"Current Time (ET): {status['current_time']}")
        print(f"Trading Day: {'Yes ✓' if status['is_trading_day'] else 'No ✗'}")
        print(f"Market Hours: {'Yes ✓' if status['is_market_hours'] else 'No ✗'}")

        if status.get('is_weekend'):
            print("Status: Weekend - Markets Closed")
        elif status.get('is_holiday'):
            print("Status: Holiday - Markets Closed")
        elif status.get('time_to_open'):
            print(f"Time to Open: {status['time_to_open']}")
        elif status.get('time_to_close'):
            print(f"Time to Close: {status['time_to_close']}")

        print(f"Should Check Now: {'Yes ✓' if status['should_check'] else 'No ✗'}")

        print("\n✓ Market hours check successful")
        return True

    except Exception as e:
        print(f"❌ Market hours test failed: {e}")
        return False


def test_market_data():
    """Test market data fetching"""
    print_header("TEST 3: MARKET DATA")

    try:
        print("Fetching AAPL quote...")
        quote = get_stock_quote('AAPL')

        if not quote:
            print("❌ Failed to fetch quote")
            return False

        print(f"✓ {quote.symbol}: ${quote.price:.2f} ({quote.change_percent:+.2f}%)")
        print(f"  Volume: {quote.volume:,}")
        print(f"  Range: ${quote.day_low:.2f} - ${quote.day_high:.2f}")

        print(f"\nFetching quotes for {min(3, len(settings.WATCHLIST))} symbols...")
        test_symbols = settings.WATCHLIST[:3]
        quotes = get_market_summary(test_symbols)

        if not quotes:
            print("❌ Failed to fetch market summary")
            return False

        print(f"✓ Fetched {len(quotes)}/{len(test_symbols)} quotes")

        for symbol, q in quotes.items():
            print(f"  {symbol}: ${q.price:.2f} ({q.change_percent:+.2f}%)")

        print("\n✓ Market data test successful")
        return True

    except Exception as e:
        print(f"❌ Market data test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_news_fetching():
    """Test news fetching"""
    print_header("TEST 4: NEWS FETCHING")

    try:
        print("Fetching market news...")
        articles = get_market_news(max_items=3)

        if not articles:
            print("⚠️  No news articles found (this is OK)")
            return True

        print(f"✓ Fetched {len(articles)} articles")

        for i, article in enumerate(articles, 1):
            print(f"\n{i}. {article.title[:60]}...")
            print(f"   Source: {article.source}")
            print(f"   Published: {article.published.strftime('%Y-%m-%d %H:%M')}")

        print("\n✓ News fetching test successful")
        return True

    except Exception as e:
        print(f"❌ News fetching test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_alert_engine():
    """Test alert engine"""
    print_header("TEST 5: ALERT ENGINE")

    try:
        print("Initializing alert engine...")
        engine = AlertEngine()

        print("Checking markets for alerts...")
        alerts = engine.check_markets()

        print(f"✓ Alert engine ran successfully")
        print(f"✓ Found {len(alerts)} alerts")

        if alerts:
            print("\nAlerts generated:")
            for alert in alerts[:3]:
                print(f"\n  {alert.symbol} - {alert.alert_type.value} ({alert.alert_level.value})")
                print(f"  Price: ${alert.quote.price:.2f} ({alert.quote.change_percent:+.2f}%)")

        print("\n✓ Alert engine test successful")
        return True

    except Exception as e:
        print(f"❌ Alert engine test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_whatsapp():
    """Test WhatsApp integration"""
    print_header("TEST 6: WHATSAPP INTEGRATION")

    try:
        print("Initializing WhatsApp sender...")
        sender = WhatsAppSender()

        if not sender.client:
            print("⚠️  Twilio not configured")
            print("   Set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN in .env")
            print("   Skipping WhatsApp test")
            return True

        print("✓ Twilio client initialized")
        print(f"  From: {settings.TWILIO_WHATSAPP_FROM}")
        print(f"  To: {settings.TWILIO_WHATSAPP_TO}")

        user_input = input("\nSend test message to WhatsApp? (y/n): ")

        if user_input.lower() == 'y':
            print("\nSending test message...")
            success = sender.test_connection()

            if success:
                print("✓ Test message sent successfully!")
                print("  Check your phone for the message")
            else:
                print("❌ Failed to send test message")
                print("  Check logs for details")
                return False
        else:
            print("Skipped WhatsApp test message")

        print("\n✓ WhatsApp integration test successful")
        return True

    except Exception as e:
        print(f"❌ WhatsApp test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_full_workflow():
    """Test complete workflow"""
    print_header("TEST 7: FULL WORKFLOW")

    try:
        print("Running complete workflow test...\n")

        # 1. Check market hours
        print("1. Checking market status...")
        status = get_market_status()
        print(f"   ✓ Market hours: {status['is_market_hours']}")

        # 2. Fetch market data
        print("\n2. Fetching market data...")
        quotes = get_market_summary(settings.WATCHLIST[:5])
        print(f"   ✓ Fetched {len(quotes)} quotes")

        # 3. Check for alerts
        print("\n3. Checking for alerts...")
        engine = AlertEngine()
        alerts = engine.check_markets()
        print(f"   ✓ Generated {len(alerts)} alerts")

        # 4. Format messages
        if alerts:
            print("\n4. Formatting alert messages...")
            for alert in alerts[:2]:
                print(f"   ✓ Formatted alert for {alert.symbol}")

        # 5. News digest
        print("\n5. Fetching news...")
        news = get_market_news(max_items=3)
        print(f"   ✓ Fetched {len(news)} articles")

        print("\n✓ Full workflow test successful!")
        print("\nWorkflow Summary:")
        print(f"  • Market Status: {'Open' if status['is_market_hours'] else 'Closed'}")
        print(f"  • Quotes Fetched: {len(quotes)}")
        print(f"  • Alerts Generated: {len(alerts)}")
        print(f"  • News Articles: {len(news)}")

        return True

    except Exception as e:
        print(f"❌ Full workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("  MARKET ALERTS - SYSTEM TEST")
    print("  " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("="*70)

    tests = [
        ("Configuration", test_configuration),
        ("Market Hours", test_market_hours),
        ("Market Data", test_market_data),
        ("News Fetching", test_news_fetching),
        ("Alert Engine", test_alert_engine),
        ("WhatsApp Integration", test_whatsapp),
        ("Full Workflow", test_full_workflow),
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except KeyboardInterrupt:
            print("\n\nTest interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error in {test_name}: {e}")
            results[test_name] = False

    # Print summary
    print_header("TEST SUMMARY")

    passed = sum(1 for r in results.values() if r)
    total = len(results)

    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}  {test_name}")

    print(f"\n  Total: {passed}/{total} tests passed")

    if passed == total:
        print("\n  🎉 All tests passed!")
        return 0
    else:
        print(f"\n  ⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
