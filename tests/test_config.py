"""Tests for config module."""

import os
import pytest
from pydantic import ValidationError

from config import AppConfig, ConfigError, get_config, load_config, reset_config


def test_app_config_valid():
    """Test valid AppConfig creation with all required fields."""
    config = AppConfig(
        rtsp_url="rtsp://test",
        bot_token="token",
        chat_id="123",
        motion_threshold=30,
        motion_sensitivity=0.5,
        motion_min_area=1000,
        cache_dir="./cache",
        cache_max_size_mb=500,
        cache_compression_enabled=True,
        cache_cleanup_interval=3600,
        storage_backend="local",
        video_buffer_seconds=30,
        video_max_duration=60,
        video_quality="medium",
        notification_cooldown_seconds=300,
        notification_quiet_hours_start=22,
        notification_quiet_hours_end=7,
        log_level="INFO",
        log_to_file=True,
        log_file_path="./cache/logs/kdx-pi-cam.log",
        log_rotation_enabled=True,
        log_max_file_size_mb=10,
        log_backup_count=7
    )
    assert config.rtsp_url == "rtsp://test"
    assert config.bot_token == "token"
    assert config.chat_id == "123"
    assert config.motion_threshold == 30
    assert config.motion_sensitivity == 0.5
    assert config.motion_min_area == 1000
    assert config.cache_dir == "./cache"
    assert config.cache_max_size_mb == 500
    assert config.cache_compression_enabled is True
    assert config.cache_cleanup_interval == 3600
    assert config.storage_backend == "local"
    assert config.video_buffer_seconds == 30
    assert config.video_max_duration == 60
    assert config.video_quality == "medium"
    assert config.notification_cooldown_seconds == 300
    assert config.notification_quiet_hours_start == 22
    assert config.notification_quiet_hours_end == 7
    assert config.log_level == "INFO"
    assert config.log_to_file is True
    assert config.log_file_path == "./cache/logs/kdx-pi-cam.log"
    assert config.log_rotation_enabled is True
    assert config.log_max_file_size_mb == 10
    assert config.log_backup_count == 7


def test_app_config_invalid():
    """Test invalid AppConfig raises ValidationError."""
    with pytest.raises(ValidationError):
        AppConfig(rtsp_url=None, bot_token=None, chat_id=None)


def test_load_config_missing_env(monkeypatch):
    """Test load_config with missing env vars."""
    env_vars = [
        "RTSP_URL", "BOT_TOKEN", "CHAT_ID", "MOTION_THRESHOLD", "MOTION_SENSITIVITY",
        "MOTION_MIN_AREA", "CACHE_DIR", "CACHE_MAX_SIZE_MB", "CACHE_COMPRESSION_ENABLED",
        "CACHE_CLEANUP_INTERVAL", "STORAGE_BACKEND", "VIDEO_BUFFER_SECONDS", "VIDEO_MAX_DURATION",
        "VIDEO_QUALITY", "NOTIFICATION_COOLDOWN_SECONDS", "NOTIFICATION_QUIET_HOURS_START",
        "NOTIFICATION_QUIET_HOURS_END", "LOG_LEVEL", "LOG_TO_FILE", "LOG_FILE_PATH",
        "LOG_ROTATION_ENABLED", "LOG_MAX_FILE_SIZE_MB", "LOG_BACKUP_COUNT"
    ]
    for var in env_vars:
        monkeypatch.delenv(var, raising=False)

    # Temporarily move .env file
    import os
    import shutil
    env_file = '.env'
    backup_file = '.env.backup'
    if os.path.exists(env_file):
        shutil.move(env_file, backup_file)

    reset_config()
    try:
        with pytest.raises(ConfigError):
            load_config()
    finally:
        if os.path.exists(backup_file):
            shutil.move(backup_file, env_file)


def test_get_config_singleton(monkeypatch):
    """Test get_config returns singleton."""
    # Set required env vars for the test
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

    config1 = get_config()
    config2 = get_config()
    assert config1 is config2