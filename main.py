"""Main entry point for kdx-pi-cam.

This script initializes the application and runs the Telegram bot.
"""

import asyncio
import logging
import logging.handlers
import os
import sys

from bot_handler import BotHandler
from cache_manager import get_cache_manager
from config import load_config


def setup_logging():
    """Set up logging configuration."""
    config = load_config()
    level = getattr(logging, config.log_level.upper(), logging.INFO)
    handlers = [logging.StreamHandler(sys.stdout)]

    if config.log_to_file:
        os.makedirs(os.path.dirname(config.log_file_path), exist_ok=True)
        if config.log_rotation_enabled:
            handler = logging.handlers.RotatingFileHandler(
                config.log_file_path,
                maxBytes=config.log_max_file_size_mb * 1024 * 1024,
                backupCount=config.log_backup_count
            )
        else:
            handler = logging.FileHandler(config.log_file_path)
        handlers.append(handler)

    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )


async def main():
    """Main application entry point."""
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        # Load configuration
        config = load_config()
        logger.info("Configuration loaded successfully")

        # Initialize cache manager
        cache_manager = get_cache_manager()
        await cache_manager.start_cleanup()
        logger.info("Cache manager started")

        # Initialize bot handler
        bot_handler = BotHandler()

        # Run the bot
        logger.info("Starting Telegram bot...")
        await bot_handler.run()

    except Exception as e:
        logger.error(f"Application error: {e}")
        await cache_manager.stop_cleanup()
        sys.exit(1)
    finally:
        await cache_manager.stop_cleanup()


if __name__ == "__main__":
    asyncio.run(main())