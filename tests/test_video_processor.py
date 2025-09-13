"""Tests for video_processor module."""

import asyncio
import numpy as np
import pytest
from unittest.mock import MagicMock, patch

from video_processor import VideoProcessor


@pytest.fixture(autouse=True)
def set_env_vars(monkeypatch):
    """Set required env vars for tests."""
    env_vars = {
        "RTSP_URL": "rtsp://test",
        "BOT_TOKEN": "token",
        "CHAT_ID": "123",
        "MOTION_THRESHOLD": "30",
        "MOTION_SENSITIVITY": "0.5",
        "MOTION_MIN_AREA": "1000",
        "CACHE_DIR": "./cache",
        "CACHE_MAX_SIZE_MB": "500",
        "CACHE_COMPRESSION_ENABLED": "true",
        "CACHE_CLEANUP_INTERVAL": "3600",
        "STORAGE_BACKEND": "local",
        "VIDEO_BUFFER_SECONDS": "30",
        "VIDEO_MAX_DURATION": "60",
        "VIDEO_QUALITY": "medium",
        "NOTIFICATION_COOLDOWN_SECONDS": "300",
        "NOTIFICATION_QUIET_HOURS_START": "22",
        "NOTIFICATION_QUIET_HOURS_END": "7",
        "LOG_LEVEL": "INFO",
        "LOG_TO_FILE": "true",
        "LOG_FILE_PATH": "./cache/logs/kdx-pi-cam.log",
        "LOG_ROTATION_ENABLED": "true",
        "LOG_MAX_FILE_SIZE_MB": "10",
        "LOG_BACKUP_COUNT": "7"
    }
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)


@pytest.mark.asyncio
async def test_video_processor_init():
    """Test VideoProcessor initialization."""
    processor = VideoProcessor("rtsp://test")
    assert processor.rtsp_url == "rtsp://test"
    assert processor.buffer_size == 300  # 30 seconds * 10 FPS
    assert len(processor.frame_buffer) == 0


@pytest.mark.asyncio
async def test_get_recent_frames():
    """Test get_recent_frames."""
    processor = VideoProcessor("rtsp://test")
    frames = [np.zeros((100, 100, 3), dtype=np.uint8) for _ in range(10)]
    processor.frame_buffer = frames

    recent = processor.get_recent_frames(3)
    assert len(recent) == 3
    assert recent == frames[-3:]


@patch('cv2.VideoCapture')
@pytest.mark.asyncio
async def test_start_capture(mock_cap):
    """Test start_capture."""
    mock_cap_instance = MagicMock()
    mock_cap_instance.isOpened.return_value = True
    mock_cap_instance.read.return_value = (True, np.zeros((100, 100, 3), dtype=np.uint8))
    mock_cap.return_value = mock_cap_instance

    processor = VideoProcessor("rtsp://test")
    await processor.start_capture()
    assert processor.running
    assert processor.cap is not None

    await processor.stop_capture()
    assert not processor.running


@pytest.mark.asyncio
async def test_capture_photo():
    """Test capture_photo."""
    processor = VideoProcessor("rtsp://test")
    processor.frame_buffer = [np.zeros((100, 100, 3), dtype=np.uint8)]

    photo = await processor.capture_photo()
    assert photo is not None
    assert isinstance(photo, np.ndarray)