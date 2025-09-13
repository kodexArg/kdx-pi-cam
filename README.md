# kdx-pi-cam

A streamlined asynchronous Python Telegram bot for monitoring a single RTSP camera stream with basic motion detection, capturing frames, and sending notifications to a specified chat ID.

## Features

- 📹 RTSP stream capture and frame buffering
- 🤖 Telegram bot commands for start/stop monitoring and on-demand captures
- 🔍 Basic motion detection via frame differencing
- 📸 Photo and video clip generation on motion or command
- ⚡ Async processing for non-blocking I/O

## Installation

1. Clone the repository and navigate to the directory.
2. Install dependencies: `uv sync`
3. Copy `.env.example` to `.env` and configure:
   - `RTSP_URL`: Your RTSP stream URL
   - `BOT_TOKEN`: Telegram bot token from @BotFather
   - `CHAT_ID`: Telegram chat ID for notifications
   - `MOTION_THRESHOLD`: Detection sensitivity (default 30)
4. Run: `uv run python main.py` or `uv run kdx-pi-cam`

## Usage

Start the bot and send commands in Telegram:

- `/start`: Begin monitoring the RTSP stream and motion detection
- `/stop`: Halt monitoring
- `/stream`: Send a live photo from the current frame

Motion detection automatically sends clips/photos to the chat when triggered.

## Architecture

```
[Telegram Bot API] <--> [bot_handler.py] (Commands: /start, /stop, /stream)
                          |
                          v
[config.py] --> [video_processor.py] (RTSP Capture & Buffer)
                          |
                          v
[motion_detector.py] (Frame Diff → Threshold → Detect)
                          |
                          v
[Telegram Send] (Clip/Photo to CHAT_ID)
```

## Troubleshooting

- **RTSP connection failed**: Check URL, credentials, and network access.
- **No motion detected**: Adjust `MOTION_THRESHOLD` in `.env`.
- **Bot not responding**: Verify `BOT_TOKEN` and `CHAT_ID`.
- **High CPU**: Ensure FFmpeg is installed; monitor with system tools.

## Technologies

- Python 3.11+
- python-telegram-bot
- opencv-python==4.13.*
- numpy, pillow, pydantic, python-dotenv, ffmpeg-python, psutil

## Contribution Guidelines

- Fork the repo and create a feature branch.
- Write tests for new code.
- Follow PEP 8; use type hints and docstrings.
- Submit a PR with a clear description.

## License

MIT