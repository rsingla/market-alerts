"""
Market Hours Checker
Determines if markets are open for trading
"""

from datetime import datetime, time
import pytz
from config import settings

# US market timezone
ET = pytz.timezone('US/Eastern')

# US market holidays (2024-2025)
MARKET_HOLIDAYS = [
    '2024-01-01',  # New Year's Day
    '2024-01-15',  # MLK Day
    '2024-02-19',  # Presidents Day
    '2024-03-29',  # Good Friday
    '2024-05-27',  # Memorial Day
    '2024-06-19',  # Juneteenth
    '2024-07-04',  # Independence Day
    '2024-09-02',  # Labor Day
    '2024-11-28',  # Thanksgiving
    '2024-12-25',  # Christmas
    '2025-01-01',  # New Year's Day
    '2025-01-20',  # MLK Day
    '2025-02-17',  # Presidents Day
    '2025-04-18',  # Good Friday
    '2025-05-26',  # Memorial Day
    '2025-06-19',  # Juneteenth
    '2025-07-04',  # Independence Day
    '2025-09-01',  # Labor Day
    '2025-11-27',  # Thanksgiving
    '2025-12-25',  # Christmas
]


def get_current_et_time():
    """Get current time in Eastern Time"""
    return datetime.now(ET)


def is_weekend(dt=None):
    """Check if given date is weekend"""
    if dt is None:
        dt = get_current_et_time()
    return dt.weekday() >= 5  # Saturday = 5, Sunday = 6


def is_holiday(dt=None):
    """Check if given date is a market holiday"""
    if dt is None:
        dt = get_current_et_time()
    date_str = dt.strftime('%Y-%m-%d')
    return date_str in MARKET_HOLIDAYS


def is_trading_day(dt=None):
    """Check if given date is a trading day"""
    return not (is_weekend(dt) or is_holiday(dt))


def is_market_hours(dt=None):
    """Check if current time is within market trading hours"""
    if dt is None:
        dt = get_current_et_time()

    # Check if it's a trading day
    if not is_trading_day(dt):
        return False

    # Market hours (9:30 AM - 4:00 PM ET)
    market_open = time(
        settings.MARKET_OPEN_HOUR,
        settings.MARKET_OPEN_MINUTE
    )
    market_close = time(
        settings.MARKET_CLOSE_HOUR,
        settings.MARKET_CLOSE_MINUTE
    )

    current_time = dt.time()
    return market_open <= current_time <= market_close


def time_until_market_open():
    """Calculate time until market opens"""
    now = get_current_et_time()

    # If it's weekend, calculate to Monday
    if now.weekday() == 5:  # Saturday
        days_to_add = 2
    elif now.weekday() == 6:  # Sunday
        days_to_add = 1
    else:
        days_to_add = 0

    # Next market open time
    next_open = now.replace(
        hour=settings.MARKET_OPEN_HOUR,
        minute=settings.MARKET_OPEN_MINUTE,
        second=0,
        microsecond=0
    )

    # If market already opened today, move to tomorrow
    if now.time() > next_open.time() and days_to_add == 0:
        days_to_add = 1

    from datetime import timedelta
    next_open += timedelta(days=days_to_add)

    # Skip holidays
    while is_holiday(next_open):
        next_open += timedelta(days=1)

    return next_open - now


def time_until_market_close():
    """Calculate time until market closes"""
    now = get_current_et_time()

    if not is_trading_day():
        return None

    market_close = now.replace(
        hour=settings.MARKET_CLOSE_HOUR,
        minute=settings.MARKET_CLOSE_MINUTE,
        second=0,
        microsecond=0
    )

    if now.time() > market_close.time():
        return None

    return market_close - now


def should_check_now():
    """Determine if we should check markets now"""
    if settings.MARKET_HOURS_ONLY:
        return is_market_hours()
    return is_trading_day()


def get_market_status():
    """Get detailed market status"""
    now = get_current_et_time()

    status = {
        'current_time': now.strftime('%Y-%m-%d %H:%M:%S %Z'),
        'is_trading_day': is_trading_day(),
        'is_market_hours': is_market_hours(),
        'is_weekend': is_weekend(),
        'is_holiday': is_holiday(),
        'should_check': should_check_now()
    }

    if not status['is_market_hours'] and status['is_trading_day']:
        time_to_open = time_until_market_open()
        if time_to_open:
            hours = int(time_to_open.total_seconds() // 3600)
            minutes = int((time_to_open.total_seconds() % 3600) // 60)
            status['time_to_open'] = f"{hours}h {minutes}m"

    if status['is_market_hours']:
        time_to_close = time_until_market_close()
        if time_to_close:
            hours = int(time_to_close.total_seconds() // 3600)
            minutes = int((time_to_close.total_seconds() % 3600) // 60)
            status['time_to_close'] = f"{hours}h {minutes}m"

    return status


if __name__ == '__main__':
    # Test market hours
    status = get_market_status()

    print("\n" + "="*50)
    print("MARKET STATUS")
    print("="*50)
    print(f"Current Time (ET): {status['current_time']}")
    print(f"Trading Day: {' ✓' if status['is_trading_day'] else '✗'}")
    print(f"Market Hours: {'✓' if status['is_market_hours'] else '✗'}")

    if 'time_to_open' in status:
        print(f"Time to Open: {status['time_to_open']}")
    if 'time_to_close' in status:
        print(f"Time to Close: {status['time_to_close']}")

    print(f"\nShould Check Now: {'✓ YES' if status['should_check'] else '✗ NO'}")
    print("="*50 + "\n")
