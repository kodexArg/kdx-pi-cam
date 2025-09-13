"""Motion detection logic for video frames.

This module detects motion in video frames using frame differencing,
thresholding, and contour analysis.
"""

import asyncio
import logging
import tempfile
import time
from typing import List, Optional, Tuple

import cv2
import numpy as np
from PIL import Image

from config import get_config
from cache_manager import get_cache_manager

logger = logging.getLogger(__name__)


class MotionDetector:
    """Detects motion in video frames."""

    def __init__(self):
        """Initialize the motion detector."""
        config = get_config()
        self.threshold = config.motion_threshold
        self.min_area = config.motion_min_area
        self.cooldown = config.notification_cooldown_seconds
        self.sensitivity = config.motion_sensitivity
        self.last_detection = 0.0

    def detect(self, frame1: np.ndarray, frame2: np.ndarray) -> bool:
        """Detect motion between two frames.

        Args:
            frame1: First frame.
            frame2: Second frame.

        Returns:
            True if motion detected, False otherwise.
        """
        if frame1 is None or frame2 is None or frame1.shape != frame2.shape:
            return False

        # Convert to grayscale
        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

        # Compute absolute difference
        diff = cv2.absdiff(gray1, gray2)

        # Apply threshold
        _, thresh = cv2.threshold(diff, self.threshold, 255, cv2.THRESH_BINARY)

        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Check for significant motion
        for contour in contours:
            if cv2.contourArea(contour) > self.min_area:
                return True
        return False

    def detect_in_buffer(self, frames: List[np.ndarray]) -> bool:
        """Detect motion in a buffer of frames.

        Args:
            frames: List of frames.

        Returns:
            True if motion detected, False otherwise.
        """
        if len(frames) < 2:
            return False

        # Check cooldown
        current_time = time.time()
        if current_time - self.last_detection < self.cooldown:
            return False

        # Detect motion between consecutive frames
        for i in range(1, len(frames)):
            if self.detect(frames[i-1], frames[i]):
                self.last_detection = current_time
                return True
        return False

    async def generate_photo(self, frame: np.ndarray) -> Optional[str]:
        """Generate a photo from a frame.

        Args:
            frame: The frame to save as photo.

        Returns:
            Path to the photo file, or None if failed.
        """
        try:
            cache_manager = get_cache_manager()
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False, dir=cache_manager.cache_dir) as tmp_file:
                img.save(tmp_file.name)
                return tmp_file.name
        except Exception as e:
            logger.error(f"Failed to generate photo: {e}")
            return None

    async def generate_clip(self, frames: List[np.ndarray], fps: int = 10) -> Optional[str]:
        """Generate a video clip from frames using OpenCV.

        Args:
            frames: List of frames.
            fps: Frames per second.

        Returns:
            Path to the clip file, or None if failed.
        """
        if not frames:
            return None

        try:
            cache_manager = get_cache_manager()
            height, width = frames[0].shape[:2]
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False, dir=cache_manager.cache_dir) as tmp_file:
                output_path = tmp_file.name

            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

            for frame in frames:
                out.write(frame)
            out.release()

            return output_path
        except Exception as e:
            logger.error(f"Failed to generate clip: {e}")
            return None