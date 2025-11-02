#!/usr/bin/env python3
"""
Market Alerts - Main Entry Point
Starts the scheduled alert system
"""

import sys
import signal
import time
from config import settings
from scheduler import start_scheduler, stop_scheduler
from utils.logger import logger


def main():
    """Main entry point"""

    # Print configuration summary
    if not settings.print_config_summary():
        logger.error("Configuration validation failed! Please fix errors in .env file")
        sys.exit(1)

    # Initialize scheduler
    logger.info("\n" + "="*60)
    logger.info("MARKET ALERTS - STARTING")
    logger.info("="*60 + "\n")

    # Handle shutdown gracefully
    def signal_handler(sig, frame):
        logger.info("\n\nReceived shutdown signal...")
        stop_scheduler()
        logger.info("Goodbye!")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Start scheduler
    try:
        start_scheduler()

        logger.info("\n" + "="*60)
        logger.info("MARKET ALERTS IS RUNNING")
        logger.info("="*60)
        logger.info("Press Ctrl+C to stop\n")

        # Keep running
        while True:
            time.sleep(1)

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        stop_scheduler()
        sys.exit(1)


if __name__ == '__main__':
    main()
