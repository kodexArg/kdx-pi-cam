"""Video processor for RTSP stream capture and clip generation.

This module handles capturing frames from an RTSP stream using OpenCV,
buffering them, and generating video clips using FFmpeg.
"""

import asyncio
import logging
import os
import tempfile
from typing import List, Optional

import cv2
import ffmpeg
import numpy as np
import psutil

from cache_manager import get_cache_manager
from config import get_config

logger = logging.getLogger(__name__)


class VideoProcessor:
    """Handles RTSP stream capture and video processing."""

    def __init__(self, rtsp_url: str, error_callback: Optional[callable] = None):
        """Initialize the video processor.

        Args:
            rtsp_url: The RTSP stream URL.
            error_callback: Optional callback for error notifications.
        """
        config = get_config()
        self.rtsp_url = rtsp_url
        # Assuming 10 FPS, buffer for VIDEO_BUFFER_SECONDS
        self.buffer_size = config.video_buffer_seconds * 10
        self.max_clip_duration = config.video_max_duration
        self.frame_buffer: List[np.ndarray] = []
        self.cap: Optional[cv2.VideoCapture] = None
        self.running = False
        self.task: Optional[asyncio.Task] = None
        self.error_callback = error_callback
        self.consecutive_failures = 0

    def _mask_url(self, url: str) -> str:
        """Mask credentials in RTSP URL for logging."""
        import re
        return re.sub(r'://([^:]+):([^@]+)@', r'://***:***@', url)

    async def start_capture(self) -> None:
        """Start capturing frames from the RTSP stream."""
        if self.running:
            return
        self.cap = cv2.VideoCapture(self.rtsp_url)
        if not self.cap.isOpened():
            logger.error(f"Failed to open RTSP stream: {self._mask_url(self.rtsp_url)}. OpenCV error code: {self.cap.get(cv2.CAP_PROP_POS_FRAMES) if self.cap else 'N/A'}")
            self.cap = None
            return
        self.running = True
        self.task = asyncio.create_task(self._capture_loop())

    @property
    def is_connected(self) -> bool:
        """Check if RTSP stream is currently connected."""
        return self.cap is not None and self.cap.isOpened()

    async def stop_capture(self) -> None:
        """Stop capturing frames."""
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        if self.cap:
            self.cap.release()

    async def _capture_loop(self) -> None:
        """Main capture loop."""
        while self.running:
            try:
                if not self.cap or not self.cap.isOpened():
                    self.cap = cv2.VideoCapture(self.rtsp_url)
                    if not self.cap.isOpened():
                        logger.error(f"Failed to open RTSP stream: {self._mask_url(self.rtsp_url)}. OpenCV error code: {self.cap.get(cv2.CAP_PROP_POS_FRAMES) if self.cap else 'N/A'}")
                        self.consecutive_failures += 1
                        if self.consecutive_failures >= 3 and self.error_callback:
                            await self.error_callback("Warning: Unable to connect to RTSP stream. Monitoring may not work properly.")
                            self.consecutive_failures = 0  # Reset to avoid spam
                        await asyncio.sleep(5)  # Retry after 5 seconds
                        continue
                    else:
                        logger.info(f"Successfully opened RTSP stream: {self._mask_url(self.rtsp_url)}")
                else:
                    self.consecutive_failures = 0  # Reset on success

                ret, frame = await asyncio.get_event_loop().run_in_executor(None, self.cap.read)
                if ret:
                    self.frame_buffer.append(frame)
                    if len(self.frame_buffer) > self.buffer_size:
                        self.frame_buffer.pop(0)
                else:
                    logger.warning(f"Failed to read frame from RTSP stream: {self._mask_url(self.rtsp_url)}. Frame buffer size: {len(self.frame_buffer)}")
                    await asyncio.sleep(1)

                # Throttle to ~10 FPS
                await asyncio.sleep(0.1)

                # Check CPU usage
                cpu_percent = psutil.cpu_percent()
                if cpu_percent > 80:
                    logger.warning(f"High CPU usage: {cpu_percent}%")
                    await asyncio.sleep(0.5)  # Slow down

            except Exception as e:
                logger.error(f"Error in capture loop: {e}. RTSP URL: {self._mask_url(self.rtsp_url)}")
                await asyncio.sleep(5)

    def get_recent_frames(self, count: int) -> List[np.ndarray]:
        """Get the most recent frames from the buffer.

        Args:
            count: Number of frames to retrieve.

        Returns:
            List of frames.
        """
        return self.frame_buffer[-count:] if len(self.frame_buffer) >= count else self.frame_buffer.copy()

    async def generate_clip(self, duration: float = 5.0) -> Optional[str]:
        """Generate a video clip from recent frames.

        Args:
            duration: Clip duration in seconds.

        Returns:
            Path to the generated clip file, or None if failed.
        """
        # Cap duration to max_clip_duration
        duration = min(duration, self.max_clip_duration)
        frames = self.get_recent_frames(int(duration * 10))  # Assuming 10 FPS
        if not frames:
            return None

        cache_manager = get_cache_manager()
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False, dir=cache_manager.cache_dir) as tmp_file:
            output_path = tmp_file.name

        try:
            # Use FFmpeg to create clip from frames
            process = (
                ffmpeg
                .input('pipe:', format='rawvideo', pix_fmt='bgr24', s=f'{frames[0].shape[1]}x{frames[0].shape[0]}')
                .output(output_path, vcodec='libx264', pix_fmt='yuv420p', r=10)
                .run_async(pipe_stdin=True)
            )

            for frame in frames:
                process.stdin.write(frame.tobytes())
            process.stdin.close()
            process.wait()

            return output_path
        except Exception as e:
            logger.error(f"Failed to generate clip: {e}")
            if os.path.exists(output_path):
                os.remove(output_path)
            return None

    async def capture_photo(self) -> Optional[np.ndarray]:
        """Capture a single photo frame.

        Returns:
            The captured frame, or None if failed.
        """
        if self.frame_buffer:
            return self.frame_buffer[-1].copy()
        return None