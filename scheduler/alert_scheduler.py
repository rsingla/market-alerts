"""
Alert Scheduler
Schedules periodic alert checks during market hours
"""

from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from alerts.alert_engine import AlertEngine
from alerts.advanced_alert_engine import get_advanced_engine
from notifications import send_alerts, send_message
from config import settings
from utils.logger import logger
from utils.market_hours import should_check_now, get_market_status


class AlertScheduler:
    """Scheduler for periodic alert checks"""

    def __init__(self):
        """Initialize scheduler"""
        self.scheduler = BackgroundScheduler()
        self.alert_engine = AlertEngine()
        self.advanced_engine = get_advanced_engine()  # New advanced engine with custom rules
        self.is_running = False
        self.last_check = None
        self.check_count = 0

    def check_and_alert(self):
        """Main job: Check markets and send alerts (Event-Driven - Every 30 min)"""
        try:
            logger.info("="*60)
            logger.info("SCHEDULED ALERT CHECK (EVENT-DRIVEN)")
            logger.info("="*60)

            # Check if we should run now
            if not should_check_now():
                logger.info("Outside of configured check hours, skipping...")
                return

            # Get market status
            status = get_market_status()
            logger.info(f"Market Status: Trading={status['is_trading_day']}, Hours={status['is_market_hours']}")

            self.last_check = datetime.now()
            self.check_count += 1

            # FIRST: Check custom alert rules (advanced engine)
            logger.info("Evaluating custom alert rules...")
            custom_alerts = self.advanced_engine.evaluate_all_rules()

            if custom_alerts:
                logger.info(f"Found {len(custom_alerts)} custom rule alerts!")

                # Send each custom alert
                for alert_data in custom_alerts:
                    logger.info(f"  - {alert_data['symbol']}: {alert_data['rule_type']}")

                    # Send WhatsApp/Telegram message
                    message = alert_data['messages']['whatsapp']
                    success = send_message(message)

                    if success:
                        logger.info(f"✓ Sent alert for {alert_data['symbol']}")
                    else:
                        logger.error(f"✗ Failed to send alert for {alert_data['symbol']}")

            # SECOND: Check standard alerts (original engine for backwards compatibility)
            logger.info("Checking standard market alerts...")
            standard_alerts = self.alert_engine.check_markets()

            if standard_alerts:
                logger.info(f"Found {len(standard_alerts)} standard alerts!")

                # Log alert details
                for alert in standard_alerts:
                    logger.info(f"  - {alert.symbol}: {alert.alert_type.value} ({alert.alert_level.value})")

                # Send alerts via WhatsApp
                logger.info("Sending standard alerts...")
                success = send_alerts(standard_alerts, combine=True)

                if success:
                    logger.info("✓ Standard alerts sent successfully!")
                else:
                    logger.error("✗ Failed to send standard alerts")

            # Summary
            total_alerts = len(custom_alerts) + len(standard_alerts)
            if total_alerts == 0:
                logger.info("No alerts triggered this check")
            else:
                logger.info(f"Total alerts processed: {total_alerts} ({len(custom_alerts)} custom + {len(standard_alerts)} standard)")

        except Exception as e:
            logger.error(f"Error in scheduled check: {e}", exc_info=True)

    def send_market_summary(self):
        """Send market summary at specific times"""
        try:
            logger.info("Generating market summary...")

            # Get market summary
            summary = self.alert_engine.get_market_summary_alert()

            if not summary:
                logger.warning("No summary to send")
                return

            # Send via WhatsApp
            from notifications import send_message
            success = send_message(summary)

            if success:
                logger.info("✓ Market summary sent!")
            else:
                logger.error("✗ Failed to send summary")

        except Exception as e:
            logger.error(f"Error sending summary: {e}", exc_info=True)

    def send_news_digest(self):
        """Send news digest"""
        try:
            logger.info("Generating news digest...")

            # Get news alert
            news = self.alert_engine.get_news_alert()

            if not news:
                logger.info("No news to send")
                return

            # Send via WhatsApp
            success = send_message(news)

            if success:
                logger.info("✓ News digest sent!")
            else:
                logger.error("✗ Failed to send news")

        except Exception as e:
            logger.error(f"Error sending news: {e}", exc_info=True)

    def send_hourly_summary(self):
        """Send hourly watchlist summary (Time-Based Alert)"""
        try:
            logger.info("Generating hourly watchlist summary...")

            # Get hourly summary from advanced engine
            summary_data = self.advanced_engine.generate_hourly_summary()

            if not summary_data:
                logger.warning("No summary data available")
                return

            # Send via WhatsApp/Telegram
            message = summary_data['messages']['whatsapp']
            success = send_message(message)

            if success:
                logger.info("✓ Hourly summary sent!")
            else:
                logger.error("✗ Failed to send hourly summary")

        except Exception as e:
            logger.error(f"Error sending hourly summary: {e}", exc_info=True)

    def start(self):
        """Start the scheduler"""
        if self.is_running:
            logger.warning("Scheduler already running")
            return

        logger.info("="*60)
        logger.info("STARTING ALERT SCHEDULER")
        logger.info("="*60)

        # Add periodic check job (every CHECK_INTERVAL_MINUTES)
        self.scheduler.add_job(
            self.check_and_alert,
            trigger=IntervalTrigger(minutes=settings.CHECK_INTERVAL_MINUTES),
            id='periodic_check',
            name='Periodic Market Check',
            replace_existing=True
        )
        logger.info(f"✓ Added periodic check (every {settings.CHECK_INTERVAL_MINUTES} minutes)")

        # Add market open summary (9:30 AM ET)
        self.scheduler.add_job(
            self.send_market_summary,
            trigger=CronTrigger(hour=9, minute=35, timezone='US/Eastern'),
            id='market_open_summary',
            name='Market Open Summary',
            replace_existing=True
        )
        logger.info("✓ Added market open summary (9:35 AM ET)")

        # Add midday summary (12:00 PM ET)
        self.scheduler.add_job(
            self.send_market_summary,
            trigger=CronTrigger(hour=12, minute=0, timezone='US/Eastern'),
            id='midday_summary',
            name='Midday Summary',
            replace_existing=True
        )
        logger.info("✓ Added midday summary (12:00 PM ET)")

        # Add market close summary (4:05 PM ET)
        self.scheduler.add_job(
            self.send_market_summary,
            trigger=CronTrigger(hour=16, minute=5, timezone='US/Eastern'),
            id='market_close_summary',
            name='Market Close Summary',
            replace_existing=True
        )
        logger.info("✓ Added market close summary (4:05 PM ET)")

        # Add morning news digest (8:00 AM ET)
        self.scheduler.add_job(
            self.send_news_digest,
            trigger=CronTrigger(hour=8, minute=0, timezone='US/Eastern'),
            id='morning_news',
            name='Morning News Digest',
            replace_existing=True
        )
        logger.info("✓ Added morning news digest (8:00 AM ET)")

        # Add hourly summaries during market hours (10 AM, 11 AM, 1 PM, 2 PM, 3 PM ET)
        hourly_times = [
            (10, 0, 'hourly_10am', '10:00 AM'),
            (11, 0, 'hourly_11am', '11:00 AM'),
            (13, 0, 'hourly_1pm', '1:00 PM'),
            (14, 0, 'hourly_2pm', '2:00 PM'),
            (15, 0, 'hourly_3pm', '3:00 PM'),
        ]

        for hour, minute, job_id, time_str in hourly_times:
            self.scheduler.add_job(
                self.send_hourly_summary,
                trigger=CronTrigger(hour=hour, minute=minute, timezone='US/Eastern'),
                id=job_id,
                name=f'Hourly Summary ({time_str} ET)',
                replace_existing=True
            )
            logger.info(f"✓ Added hourly summary ({time_str} ET)")

        # Start scheduler
        self.scheduler.start()
        self.is_running = True

        logger.info("="*60)
        logger.info("SCHEDULER STARTED SUCCESSFULLY")
        logger.info("="*60)

        # Print schedule
        self.print_schedule()

    def stop(self):
        """Stop the scheduler"""
        if not self.is_running:
            logger.warning("Scheduler not running")
            return

        logger.info("Stopping scheduler...")
        self.scheduler.shutdown()
        self.is_running = False
        logger.info("✓ Scheduler stopped")

    def print_schedule(self):
        """Print current schedule"""
        logger.info("\nScheduled Jobs:")
        logger.info("-" * 60)

        jobs = self.scheduler.get_jobs()
        for job in jobs:
            logger.info(f"  {job.name} (ID: {job.id})")
            logger.info(f"    Next run: {job.next_run_time}")

        logger.info("-" * 60)
        logger.info(f"Total jobs: {len(jobs)}")
        logger.info("")

    def get_stats(self) -> dict:
        """Get scheduler statistics"""
        return {
            'is_running': self.is_running,
            'last_check': self.last_check.isoformat() if self.last_check else None,
            'check_count': self.check_count,
            'jobs_count': len(self.scheduler.get_jobs()) if self.is_running else 0
        }


# Global scheduler instance
_scheduler = None


def get_scheduler() -> AlertScheduler:
    """Get global scheduler instance"""
    global _scheduler
    if _scheduler is None:
        _scheduler = AlertScheduler()
    return _scheduler


def start_scheduler():
    """Start the global scheduler (convenience function)"""
    scheduler = get_scheduler()
    scheduler.start()


def stop_scheduler():
    """Stop the global scheduler (convenience function)"""
    scheduler = get_scheduler()
    scheduler.stop()


if __name__ == '__main__':
    import time
    import signal
    import sys

    # Test scheduler
    print("\n" + "="*60)
    print("ALERT SCHEDULER TEST")
    print("="*60)

    scheduler = AlertScheduler()

    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        print("\n\nStopping scheduler...")
        scheduler.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    # Start scheduler
    scheduler.start()

    print("\nScheduler is running. Press Ctrl+C to stop.")
    print("Waiting for scheduled jobs...\n")

    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        scheduler.stop()
