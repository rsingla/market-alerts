"""
Logging Configuration
Uses loguru for better logging
"""

import sys
from pathlib import Path
from loguru import logger
from config import settings

# Remove default handler
logger.remove()

# Create logs directory if needed
log_file = Path(settings.LOG_FILE)
log_file.parent.mkdir(parents=True, exist_ok=True)

# Add console handler with colors
logger.add(
    sys.stdout,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> | <level>{message}</level>",
    level=settings.LOG_LEVEL,
    colorize=True
)

# Add file handler
logger.add(
    settings.LOG_FILE,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
    level=settings.LOG_LEVEL,
    rotation="1 day",  # Rotate daily
    retention="7 days",  # Keep logs for 7 days
    compression="zip"  # Compress old logs
)

# Export logger
__all__ = ['logger']
