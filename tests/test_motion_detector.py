"""Tests for motion_detector module."""

import numpy as np
import pytest

from motion_detector import MotionDetector


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


def test_detect_no_motion():
    """Test detect with identical frames."""
    detector = MotionDetector()
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    assert not detector.detect(frame, frame)


def test_detect_motion(monkeypatch):
    """Test detect with different frames."""
    monkeypatch.setenv("MOTION_THRESHOLD", "10")
    detector = MotionDetector()
    frame1 = np.zeros((100, 100, 3), dtype=np.uint8)
    frame2 = np.ones((100, 100, 3), dtype=np.uint8) * 50
    assert detector.detect(frame1, frame2)


def test_detect_in_buffer():
    """Test detect_in_buffer."""
    detector = MotionDetector()
    frames = [np.zeros((100, 100, 3), dtype=np.uint8) for _ in range(5)]
    frames[2] = np.ones((100, 100, 3), dtype=np.uint8) * 100
    assert detector.detect_in_buffer(frames)


def test_detect_in_buffer_cooldown(monkeypatch):
    """Test cooldown in detect_in_buffer."""
    monkeypatch.setenv("NOTIFICATION_COOLDOWN_SECONDS", "0.1")
    detector = MotionDetector()
    frames = [np.zeros((100, 100, 3), dtype=np.uint8) for _ in range(5)]
    frames[2] = np.ones((100, 100, 3), dtype=np.uint8) * 100

    # First detection
    assert detector.detect_in_buffer(frames)

    # Second should be blocked by cooldown
    assert not detector.detect_in_buffer(frames)