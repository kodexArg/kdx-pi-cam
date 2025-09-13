"""Telegram bot handler for kdx-pi-cam.

This module handles Telegram bot commands and integrates with video processing and motion detection.
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from config import get_config
from motion_detector import MotionDetector
from video_processor import VideoProcessor

logger = logging.getLogger(__name__)


class BotHandler:
    """Handles Telegram bot interactions."""

    def __init__(self):
        """Initialize the bot handler."""
        config = get_config()
        self.application: Optional[Application] = None
        self.video_processor = VideoProcessor(config.rtsp_url)
        self.motion_detector = MotionDetector()
        self.monitoring_task: Optional[asyncio.Task] = None
        self.monitoring = False
        self.quiet_start = config.notification_quiet_hours_start
        self.quiet_end = config.notification_quiet_hours_end

    def _is_quiet_hours(self) -> bool:
        """Check if current time is in quiet hours."""
        now = datetime.now().hour
        if self.quiet_start < self.quiet_end:
            return self.quiet_start <= now < self.quiet_end
        else:
            # Overnight quiet hours
            return now >= self.quiet_start or now < self.quiet_end

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command."""
        if self.monitoring:
            await update.message.reply_text("Monitoring is already running.")
            return

        self.monitoring = True
        await self.video_processor.start_capture()
        self.monitoring_task = asyncio.create_task(self._monitor_motion(update.effective_chat.id))
        await update.message.reply_text("Monitoring started.")

    async def stop_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /stop command."""
        if not self.monitoring:
            await update.message.reply_text("Monitoring is not running.")
            return

        self.monitoring = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        await self.video_processor.stop_capture()
        await update.message.reply_text("Monitoring stopped.")

    async def stream_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /stream command."""
        if not self.monitoring:
            await update.message.reply_text("Monitoring is not running. Use /start first.")
            return

        # Send a photo
        frame = await self.video_processor.capture_photo()
        if frame is not None:
            photo_path = await self.motion_detector.generate_photo(frame)
            if photo_path:
                with open(photo_path, 'rb') as photo_file:
                    await update.message.reply_photo(photo_file)
                import os
                os.remove(photo_path)
            else:
                await update.message.reply_text("Failed to capture photo.")
        else:
            await update.message.reply_text("No frames available.")

    async def _monitor_motion(self, chat_id: int) -> None:
        """Monitor for motion and send notifications."""
        while self.monitoring:
            try:
                frames = self.video_processor.get_recent_frames(10)  # Last 10 frames
                if self.motion_detector.detect_in_buffer(frames):
                    if self._is_quiet_hours():
                        logger.info("Motion detected but in quiet hours, skipping notification")
                        continue
                    # Send notification
                    clip_path = await self.video_processor.generate_clip(5.0)
                    if clip_path:
                        with open(clip_path, 'rb') as clip_file:
                            await self.application.bot.send_video(chat_id, clip_file, caption="Motion detected!")
                        import os
                        os.remove(clip_path)
                    else:
                        await self.application.bot.send_message(chat_id, "Motion detected!")
                await asyncio.sleep(1)  # Check every second
            except Exception as e:
                logger.error(f"Error in motion monitoring: {e}")
                await asyncio.sleep(5)

    def setup_application(self) -> Application:
        """Set up the Telegram application."""
        config = get_config()
        self.application = Application.builder().token(config.bot_token).build()

        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("stop", self.stop_command))
        self.application.add_handler(CommandHandler("stream", self.stream_command))

        return self.application

    async def run(self) -> None:
        """Run the bot."""
        if not self.application:
            self.setup_application()
        await self.application.run_polling()