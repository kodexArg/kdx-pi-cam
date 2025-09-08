from typing import Optional, Literal
from pydantic import BaseSettings, Field, validator
import os
from pathlib import Path


class Config(BaseSettings):
    """Configuración centralizada con validación usando pydantic y patrón Singleton."""
    
    _instance: Optional['Config'] = None
    
    # Variables Críticas del Sistema
    RTSP_URL: str = Field(..., description="URL de la cámara RTSP")
    BOT_TOKEN: str = Field(..., description="Token del bot de Telegram")
    CHAT_ID: str = Field(..., description="ID del chat de Telegram para notificaciones")
    
    # Almacenamiento y Caché
    CACHE_DIR: str = Field(default="./cache", description="Directorio base para almacenamiento temporal")
    CACHE_MAX_SIZE_MB: int = Field(default=500, description="Límite de tamaño del caché en MB")
    CACHE_COMPRESSION_ENABLED: bool = Field(default=True, description="Activar compresión de archivos antiguos")
    CACHE_CLEANUP_INTERVAL: int = Field(default=3600, description="Intervalo de limpieza automática en segundos")
    STORAGE_BACKEND: Literal["local", "s3", "azure", "gcp"] = Field(default="local", description="Tipo de backend de almacenamiento")
    
    # Detección de Movimiento
    MOTION_SENSITIVITY: float = Field(default=0.5, ge=0.0, le=1.0, description="Sensibilidad del algoritmo de detección")
    MOTION_MIN_AREA: int = Field(default=500, description="Área mínima en píxeles para movimiento válido")
    
    # Procesamiento de Video
    VIDEO_BUFFER_SECONDS: int = Field(default=30, description="Duración del buffer circular en segundos")
    VIDEO_MAX_DURATION: int = Field(default=60, description="Duración máxima de videos solicitados en segundos")
    VIDEO_QUALITY: Literal["low", "medium", "high"] = Field(default="medium", description="Calidad de video")
    
    # Sistema de Notificaciones
    NOTIFICATION_COOLDOWN_SECONDS: int = Field(default=300, description="Tiempo mínimo entre notificaciones")
    NOTIFICATION_QUIET_HOURS_START: int = Field(default=22, ge=0, le=23, description="Hora inicio modo silencioso")
    NOTIFICATION_QUIET_HOURS_END: int = Field(default=7, ge=0, le=23, description="Hora fin modo silencioso")
    
    # Logging y Depuración
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(default="INFO", description="Nivel de logging")
    LOG_TO_FILE: bool = Field(default=True, description="Guardar logs en archivo")
    LOG_FILE_PATH: str = Field(default="./cache/logs/kdx-pi-cam.log", description="Ruta del archivo de logs")
    LOG_ROTATION_ENABLED: bool = Field(default=True, description="Activar rotación automática de logs")
    LOG_MAX_FILE_SIZE_MB: int = Field(default=10, description="Tamaño máximo antes de rotar en MB")
    LOG_BACKUP_COUNT: int = Field(default=5, description="Número de archivos de backup a mantener")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
    
    @validator('CACHE_DIR', 'LOG_FILE_PATH')
    def validate_paths(cls, v):
        """Validar y crear directorios si no existen."""
        path = Path(v)
        if str(path).endswith('.log'):
            path = path.parent
        path.mkdir(parents=True, exist_ok=True)
        return v
    
    @validator('MOTION_SENSITIVITY')
    def validate_motion_sensitivity(cls, v):
        """Validar que la sensibilidad esté en el rango correcto."""
        if not 0.0 <= v <= 1.0:
            raise ValueError('MOTION_SENSITIVITY debe estar entre 0.0 y 1.0')
        return v
    
    @validator('NOTIFICATION_QUIET_HOURS_START', 'NOTIFICATION_QUIET_HOURS_END')
    def validate_quiet_hours(cls, v):
        """Validar que las horas estén en formato 24h."""
        if not 0 <= v <= 23:
            raise ValueError('Las horas deben estar entre 0 y 23')
        return v
    
    def __new__(cls):
        """Implementación del patrón Singleton."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inicializar configuración solo una vez."""
        if not hasattr(self, '_initialized'):
            super().__init__()
            self._initialized = True
    
    @classmethod
    def get_instance(cls) -> 'Config':
        """Obtener la instancia singleton de configuración."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def get_cache_path(self, filename: str) -> Path:
        """Obtener ruta completa para archivo en caché."""
        return Path(self.CACHE_DIR) / filename
    
    def get_log_path(self) -> Path:
        """Obtener ruta completa del archivo de log."""
        return Path(self.LOG_FILE_PATH)
    
    def is_quiet_hours(self) -> bool:
        """Verificar si estamos en horario silencioso."""
        from datetime import datetime
        current_hour = datetime.now().hour
        
        if self.NOTIFICATION_QUIET_HOURS_START <= self.NOTIFICATION_QUIET_HOURS_END:
            return self.NOTIFICATION_QUIET_HOURS_START <= current_hour <= self.NOTIFICATION_QUIET_HOURS_END
        else:
            return current_hour >= self.NOTIFICATION_QUIET_HOURS_START or current_hour <= self.NOTIFICATION_QUIET_HOURS_END


# Instancia global singleton
config = Config.get_instance()