"""Main entry point for kdx-pi-cam.

This script initializes the application and runs the Telegram bot.
"""

import asyncio
import logging
import logging.handlers
import os
import sys
import threading

from bot_handler import BotHandler
from cache_manager import get_cache_manager
from config import load_config

PID_FILE = "bot.pid"


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


def check_existing_instance():
    """Check if another instance is already running."""
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE, 'r') as f:
                old_pid = int(f.read().strip())
            # Check if process is still running
            try:
                os.kill(old_pid, 0)  # Signal 0 just checks if process exists
                return True  # Process is still running
            except OSError:
                # Process is not running, remove stale PID file
                os.remove(PID_FILE)
        except (ValueError, FileNotFoundError):
            # Invalid PID file, remove it
            if os.path.exists(PID_FILE):
                os.remove(PID_FILE)
    return False


def create_pid_file():
    """Create PID file for this instance."""
    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))


def remove_pid_file():
    """Remove PID file."""
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)


def run_bot_sync(bot_handler: BotHandler):
    """Run the bot synchronously in a thread."""
    asyncio.set_event_loop(asyncio.new_event_loop())
    bot_handler.setup_application()
    bot_handler.application.run_polling()


async def main():
    """Main application entry point."""
    setup_logging()
    logger = logging.getLogger(__name__)

    # Check for existing instance
    if check_existing_instance():
        logger.error("Another instance of the bot is already running. Exiting.")
        sys.exit(1)

    # Create PID file
    create_pid_file()

    try:
        # Load configuration
        config = load_config()
        logger.info(f"Configuration loaded successfully. Process PID: {os.getpid()}")
        logger.info(f"Starting bot instance with token ending in ...{config.bot_token[-10:]}")

        # Initialize cache manager
        cache_manager = get_cache_manager()
        await cache_manager.start_cleanup()
        logger.info("Cache manager started")

        # Initialize bot handler
        bot_handler = BotHandler()

        # Run the bot in a thread
        logger.info("Starting Telegram bot...")
        bot_thread = threading.Thread(target=run_bot_sync, args=(bot_handler,))
        bot_thread.start()

        # Keep running
        await asyncio.sleep(float('inf'))

    except Exception as e:
        logger.error(f"Application error: {e}")
        await cache_manager.stop_cleanup()
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    finally:
        await cache_manager.stop_cleanup()
        remove_pid_file()


if __name__ == "__main__":
    asyncio.run(main())