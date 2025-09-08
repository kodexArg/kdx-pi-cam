# KDX Pi Cam - Librerías Python

## Core Dependencies
- **python-telegram-bot**: Librería para interactuar con la API de Telegram
- **ffmpeg-python**: Wrapper de FFmpeg para procesamiento de video
- **opencv-python**: Procesamiento de imágenes y computer vision
- **numpy**: Operaciones numéricas y manejo de arrays
- **pillow**: Manipulación de imágenes

## Utilidades
- **pydantic**: Validación de datos y modelos
- **python-dotenv**: Manejo de variables de entorno
- **psutil**: Información del sistema
- **asyncio**: Programación asíncrona (incluido en Python)

## Desarrollo y Testing
- **pytest**: Framework de testing

## Variables de Entorno Requeridas

El proyecto requiere **TODAS** las siguientes variables de entorno definidas en un archivo `.env`. 

> **Importante**: Copia el archivo `.env.example` como `.env` y configura todas las variables antes de ejecutar la aplicación.

### Variables Críticas del Sistema
Estas variables son esenciales para el funcionamiento básico:

- **RTSP_URL**: URL completa de la cámara RTSP incluyendo credenciales y parámetros de stream (ej: `rtsp://user:pass@192.168.1.100:554/cam/realmonitor?channel=1&subtype=0`)
- **BOT_TOKEN**: Token de autenticación del bot de Telegram obtenido desde @BotFather (ej: `1234567890:ABC123def456ghi789jkl012mno345pqr678`)
- **CHAT_ID**: ID numérico del chat de Telegram donde se enviarán notificaciones y respuestas (ej: `123456789`)

### Variables de Configuración
Estas variables controlan el comportamiento del sistema:

#### Almacenamiento y Caché
- **CACHE_DIR**: Directorio base para almacenamiento temporal de videos
- **CACHE_MAX_SIZE_MB**: Límite de tamaño del caché en megabytes antes de activar rotación FIFO
- **CACHE_COMPRESSION_ENABLED**: Activar compresión de archivos antiguos antes de eliminarlos (`true`/`false`)
- **CACHE_CLEANUP_INTERVAL**: Intervalo en segundos para limpieza automática de archivos expirados
- **STORAGE_BACKEND**: Tipo de backend de almacenamiento - `local`, `s3`, `azure`, `gcp`

#### Detección de Movimiento
- **MOTION_SENSITIVITY**: Sensibilidad del algoritmo de detección, valor entre 0.0 y 1.0
- **MOTION_MIN_AREA**: Área mínima en píxeles para considerar un movimiento válido

#### Procesamiento de Video
- **VIDEO_BUFFER_SECONDS**: Duración del buffer circular de video en memoria (segundos)
- **VIDEO_MAX_DURATION**: Duración máxima permitida para videos solicitados por usuarios (segundos)
- **VIDEO_QUALITY**: Calidad de video - `low`, `medium`, `high`

#### Sistema de Notificaciones
- **NOTIFICATION_COOLDOWN_SECONDS**: Tiempo mínimo entre notificaciones del mismo tipo para evitar spam (segundos)
- **NOTIFICATION_QUIET_HOURS_START**: Hora de inicio del modo silencioso (formato 24h)
- **NOTIFICATION_QUIET_HOURS_END**: Hora de fin del modo silencioso (formato 24h)

#### Logging y Depuración
- **LOG_LEVEL**: Nivel de logging - `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- **LOG_TO_FILE**: Guardar logs en archivo además de consola (`true`/`false`)
- **LOG_FILE_PATH**: Ruta completa del archivo de logs (./cache/logs/kdx-pi-cam.log)
- **LOG_ROTATION_ENABLED**: Activar rotación automática de logs (true/false)
- **LOG_MAX_FILE_SIZE_MB**: Tamaño máximo de cada archivo de log en MB antes de rotar
- **LOG_BACKUP_COUNT**: Número de archivos de backup a mantener

> **Importante**: Todas las variables son obligatorias y deben estar definidas en el archivo `.env` para el correcto funcionamiento del sistema.