"""Configuration management for kdx-pi-cam.

This module handles loading and validating environment variables using Pydantic.
"""

import os
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, ValidationError
from pydantic_settings import BaseSettings


class ConfigError(Exception):
    """Raised when configuration is invalid or missing."""
    pass


class AppConfig(BaseSettings):
    """Application configuration settings."""

    # Core settings
    rtsp_url: str = Field(..., description="RTSP stream URL")
    bot_token: str = Field(..., description="Telegram bot token")
    chat_id: str = Field(..., description="Telegram chat ID for notifications")

    # Motion detection settings
    motion_threshold: int = Field(..., description="Motion detection threshold (pixel difference)")
    motion_sensitivity: float = Field(..., description="Motion sensitivity (0.0 to 1.0)")
    motion_min_area: int = Field(..., description="Minimum area for motion detection (pixels)")

    # Cache settings
    cache_dir: str = Field(..., description="Cache directory path")
    cache_max_size_mb: int = Field(..., description="Maximum cache size in MB")
    cache_compression_enabled: bool = Field(..., description="Enable cache compression")
    cache_cleanup_interval: int = Field(..., description="Cache cleanup interval in seconds")

    # Storage settings
    storage_backend: str = Field(..., description="Storage backend (local, s3, azure, gcp)")

    # Video settings
    video_buffer_seconds: int = Field(..., description="Video buffer duration in seconds")
    video_max_duration: int = Field(..., description="Maximum video clip duration in seconds")
    video_quality: str = Field(..., description="Video quality (low, medium, high)")

    # Notification settings
    notification_cooldown_seconds: int = Field(..., description="Notification cooldown in seconds")
    notification_quiet_hours_start: int = Field(..., description="Quiet hours start time (24-hour format)")
    notification_quiet_hours_end: int = Field(..., description="Quiet hours end time (24-hour format)")

    # Logging settings
    log_level: str = Field(..., description="Logging level (DEBUG, INFO, WARNING, ERROR)")
    log_to_file: bool = Field(..., description="Enable logging to file")
    log_file_path: str = Field(..., description="Log file path")
    log_rotation_enabled: bool = Field(..., description="Enable log rotation")
    log_max_file_size_mb: int = Field(..., description="Maximum log file size in MB")
    log_backup_count: int = Field(..., description="Number of log backup files to keep")

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")


# Global config instance
_config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """Get the global configuration instance.

    Returns:
        AppConfig: The loaded configuration.

    Raises:
        ConfigError: If configuration loading fails.
    """
    global _config
    if _config is None:
        try:
            _config = AppConfig()
        except ValidationError as e:
            raise ConfigError(f"Configuration validation failed: {e}")
    return _config


def load_config() -> AppConfig:
    """Load and validate configuration from environment.

    Returns:
        AppConfig: The validated configuration.

    Raises:
        ConfigError: If required variables are missing or invalid.
    """
    return get_config()


def reset_config() -> None:
    """Reset the global configuration instance. For testing purposes."""
    global _config
    _config = None