# API Reference

## config.py

### AppConfig
Pydantic model for application settings.

- `rtsp_url: str` - RTSP stream URL
- `bot_token: str` - Telegram bot token
- `chat_id: str` - Telegram chat ID
- `motion_threshold: int` - Motion detection threshold

### Functions
- `get_config() -> AppConfig` - Get singleton config instance
- `load_config() -> AppConfig` - Load and validate config

## video_processor.py

### VideoProcessor
Handles RTSP capture and video processing.

#### Methods
- `__init__(rtsp_url: str, buffer_size: int = 100)` - Initialize processor
- `start_capture() -> None` - Start async capture loop
- `stop_capture() -> None` - Stop capture
- `get_recent_frames(count: int) -> List[np.ndarray]` - Get recent frames
- `generate_clip(duration: float = 5.0) -> Optional[str]` - Generate video clip
- `capture_photo() -> Optional[np.ndarray]` - Capture single frame

## motion_detector.py

### MotionDetector
Detects motion in frames.

#### Methods
- `__init__(threshold: int = 30, min_area: int = 500, cooldown: float = 30.0)` - Initialize detector
- `detect(frame1: np.ndarray, frame2: np.ndarray) -> bool` - Detect motion between frames
- `detect_in_buffer(frames: List[np.ndarray]) -> bool` - Detect in frame list
- `generate_photo(frame: np.ndarray) -> Optional[str]` - Save frame as photo
- `generate_clip(frames: List[np.ndarray], fps: int = 10) -> Optional[str]` - Save frames as clip

## bot_handler.py

### BotHandler
Manages Telegram bot interactions.

#### Methods
- `__init__()` - Initialize handler
- `start_command(update: Update, context) -> None` - Handle /start
- `stop_command(update: Update, context) -> None` - Handle /stop
- `stream_command(update: Update, context) -> None` - Handle /stream
- `setup_application() -> Application` - Set up Telegram app
- `run() -> None` - Run bot polling

## main.py

### Functions
- `main() -> None` - Entry point