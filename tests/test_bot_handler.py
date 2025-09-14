"""Tests for bot_handler module."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from bot_handler import BotHandler


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
async def test_bot_handler_init():
    """Test BotHandler initialization."""
    with patch('config.get_config') as mock_config:
        mock_config.return_value.rtsp_url = "rtsp://test"
        mock_config.return_value.bot_token = "token"
        mock_config.return_value.chat_id = "123"
        mock_config.return_value.motion_threshold = 30

        handler = BotHandler()
        assert handler.video_processor is not None
        assert handler.motion_detector is not None


@pytest.mark.asyncio
async def test_start_command():
    """Test /start command."""
    with patch('config.get_config') as mock_config:
        mock_config.return_value.rtsp_url = "rtsp://test"
        mock_config.return_value.bot_token = "token"
        mock_config.return_value.chat_id = "123"
        mock_config.return_value.motion_threshold = 30

        handler = BotHandler()
        update = MagicMock()
        update.effective_chat.id = 123
        update.message = AsyncMock()

        # Mock VideoCapture to simulate successful connection
        mock_cap_instance = MagicMock()
        mock_cap_instance.isOpened.return_value = True
        with patch('video_processor.cv2.VideoCapture', return_value=mock_cap_instance):
            await handler.start_command(update, None)
            assert handler.monitoring
            update.message.reply_text.assert_called_with("Monitoring started successfully.")


@pytest.mark.asyncio
async def test_stop_command():
    """Test /stop command."""
    with patch('config.get_config') as mock_config:
        mock_config.return_value.rtsp_url = "rtsp://test"
        mock_config.return_value.bot_token = "token"
        mock_config.return_value.chat_id = "123"
        mock_config.return_value.motion_threshold = 30

        handler = BotHandler()
        handler.monitoring = True
        update = MagicMock()
        update.message = AsyncMock()

        await handler.stop_command(update, None)
        assert not handler.monitoring
        update.message.reply_text.assert_called_with("Monitoring stopped.")