import pytest
import os
from pydantic import ValidationError
from dotenv import load_dotenv
from infrastructure.config import Config

# Cargar variables de entorno desde .env
load_dotenv()


class TestEnvironmentValidation:
    """Test de validación completa de variables de entorno."""
    
    def test_all_environment_variables_exist(self):
        """Verificar que TODAS las variables de entorno están definidas."""
        # Variables críticas del sistema
        critical_vars = {
            "RTSP_URL": "URL de la cámara RTSP",
            "BOT_TOKEN": "Token del bot de Telegram", 
            "CHAT_ID": "ID del chat de Telegram"
        }
        
        # Variables de almacenamiento y caché
        storage_vars = {
            "CACHE_DIR": "Directorio base para almacenamiento temporal",
            "CACHE_MAX_SIZE_MB": "Límite de tamaño del caché en MB",
            "CACHE_COMPRESSION_ENABLED": "Activar compresión de archivos antiguos",
            "CACHE_CLEANUP_INTERVAL": "Intervalo de limpieza automática",
            "STORAGE_BACKEND": "Tipo de backend de almacenamiento"
        }
        
        # Variables de detección de movimiento
        motion_vars = {
            "MOTION_SENSITIVITY": "Sensibilidad del algoritmo de detección",
            "MOTION_MIN_AREA": "Área mínima en píxeles para movimiento válido"
        }
        
        # Variables de procesamiento de video
        video_vars = {
            "VIDEO_BUFFER_SECONDS": "Duración del buffer circular",
            "VIDEO_MAX_DURATION": "Duración máxima de videos solicitados",
            "VIDEO_QUALITY": "Calidad de video"
        }
        
        # Variables del sistema de notificaciones
        notification_vars = {
            "NOTIFICATION_COOLDOWN_SECONDS": "Tiempo mínimo entre notificaciones",
            "NOTIFICATION_QUIET_HOURS_START": "Hora inicio modo silencioso",
            "NOTIFICATION_QUIET_HOURS_END": "Hora fin modo silencioso"
        }
        
        # Variables de logging y depuración
        logging_vars = {
            "LOG_LEVEL": "Nivel de logging",
            "LOG_TO_FILE": "Guardar logs en archivo",
            "LOG_FILE_PATH": "Ruta del archivo de logs",
            "LOG_ROTATION_ENABLED": "Activar rotación automática de logs",
            "LOG_MAX_FILE_SIZE_MB": "Tamaño máximo antes de rotar",
            "LOG_BACKUP_COUNT": "Número de archivos de backup a mantener"
        }
        
        # Combinar todas las variables
        all_vars = {
            **critical_vars,
            **storage_vars,
            **motion_vars,
            **video_vars,
            **notification_vars,
            **logging_vars
        }
        
        missing_vars = []
        for var_name, description in all_vars.items():
            if not os.environ.get(var_name):
                missing_vars.append(f"{var_name} ({description})")
        
        if missing_vars:
            # Organizar por categorías para mejor legibilidad
            error_msg = "Variables de entorno no definidas:\n"
            
            missing_critical = [v for v in missing_vars if any(c in v for c in critical_vars.keys())]
            missing_storage = [v for v in missing_vars if any(c in v for c in storage_vars.keys())]
            missing_motion = [v for v in missing_vars if any(c in v for c in motion_vars.keys())]
            missing_video = [v for v in missing_vars if any(c in v for c in video_vars.keys())]
            missing_notification = [v for v in missing_vars if any(c in v for c in notification_vars.keys())]
            missing_logging = [v for v in missing_vars if any(c in v for c in logging_vars.keys())]
            
            if missing_critical:
                error_msg += f"\n🔴 CRÍTICAS: {', '.join(missing_critical)}"
            if missing_storage:
                error_msg += f"\n💾 ALMACENAMIENTO: {', '.join(missing_storage)}"
            if missing_motion:
                error_msg += f"\n🎯 DETECCIÓN: {', '.join(missing_motion)}"
            if missing_video:
                error_msg += f"\n🎥 VIDEO: {', '.join(missing_video)}"
            if missing_notification:
                error_msg += f"\n🔔 NOTIFICACIONES: {', '.join(missing_notification)}"
            if missing_logging:
                error_msg += f"\n📝 LOGGING: {', '.join(missing_logging)}"
            
            error_msg += "\n\n💡 Copia .env.example como .env y configura todas las variables."
            
            pytest.fail(error_msg)
    
    def test_critical_environment_variables_not_empty(self):
        """Verificar que las variables críticas no están vacías."""
        critical_vars = ["RTSP_URL", "BOT_TOKEN", "CHAT_ID"]
        
        empty_vars = []
        for var_name in critical_vars:
            value = os.environ.get(var_name, "")
            if not value.strip():
                empty_vars.append(var_name)
        
        assert not empty_vars, (
            f"Variables de entorno críticas están vacías: {', '.join(empty_vars)}. "
            "Estas variables deben tener valores válidos."
        )
    
    def test_numeric_environment_variables_format(self):
        """Verificar que las variables numéricas tienen formato válido."""
        numeric_vars = {
            "CACHE_MAX_SIZE_MB": "entero positivo",
            "CACHE_CLEANUP_INTERVAL": "entero positivo",
            "MOTION_MIN_AREA": "entero positivo",
            "VIDEO_BUFFER_SECONDS": "entero positivo",
            "VIDEO_MAX_DURATION": "entero positivo",
            "NOTIFICATION_COOLDOWN_SECONDS": "entero positivo",
            "NOTIFICATION_QUIET_HOURS_START": "entero 0-23",
            "NOTIFICATION_QUIET_HOURS_END": "entero 0-23",
            "LOG_MAX_FILE_SIZE_MB": "entero positivo",
            "LOG_BACKUP_COUNT": "entero positivo"
        }
        
        invalid_vars = []
        for var_name, expected_format in numeric_vars.items():
            value = os.environ.get(var_name, "")
            if value:
                try:
                    num_value = int(value)
                    if "0-23" in expected_format and not (0 <= num_value <= 23):
                        invalid_vars.append(f"{var_name}={value} (debe estar entre 0-23)")
                    elif "positivo" in expected_format and num_value <= 0:
                        invalid_vars.append(f"{var_name}={value} (debe ser positivo)")
                except ValueError:
                    invalid_vars.append(f"{var_name}={value} (debe ser {expected_format})")
        
        assert not invalid_vars, (
            f"Variables numéricas con formato inválido: {', '.join(invalid_vars)}"
        )
    
    def test_boolean_environment_variables_format(self):
        """Verificar que las variables booleanas tienen formato válido."""
        boolean_vars = [
            "CACHE_COMPRESSION_ENABLED",
            "LOG_TO_FILE",
            "LOG_ROTATION_ENABLED"
        ]
        
        invalid_vars = []
        valid_boolean_values = {"true", "false", "1", "0", "yes", "no", "on", "off"}
        
        for var_name in boolean_vars:
            value = os.environ.get(var_name, "").lower()
            if value and value not in valid_boolean_values:
                invalid_vars.append(f"{var_name}={value}")
        
        assert not invalid_vars, (
            f"Variables booleanas con formato inválido: {', '.join(invalid_vars)}. "
            f"Valores válidos: {', '.join(sorted(valid_boolean_values))}"
        )
    
    def test_choice_environment_variables_format(self):
        """Verificar que las variables de elección tienen valores válidos."""
        choice_vars = {
            "STORAGE_BACKEND": ["local", "s3", "azure", "gcp"],
            "VIDEO_QUALITY": ["low", "medium", "high"],
            "LOG_LEVEL": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        }
        
        invalid_vars = []
        for var_name, valid_choices in choice_vars.items():
            value = os.environ.get(var_name, "")
            if value and value not in valid_choices:
                invalid_vars.append(f"{var_name}={value} (válidos: {', '.join(valid_choices)})")
        
        assert not invalid_vars, (
            f"Variables de elección con valores inválidos: {', '.join(invalid_vars)}"
        )
    
    def test_float_environment_variables_format(self):
        """Verificar que MOTION_SENSITIVITY tiene formato válido (0.0-1.0)."""
        value = os.environ.get("MOTION_SENSITIVITY", "")
        if value:
            try:
                float_value = float(value)
                assert 0.0 <= float_value <= 1.0, (
                    f"MOTION_SENSITIVITY={value} debe estar entre 0.0 y 1.0"
                )
            except ValueError:
                pytest.fail(f"MOTION_SENSITIVITY={value} debe ser un número decimal")
    
    def test_config_can_be_instantiated_with_env_vars(self):
        """Verificar que Config puede instanciarse correctamente con las variables de entorno."""
        try:
            # Resetear singleton para forzar nueva instanciación
            Config._instance = None
            config = Config()
            
            # Verificar que las propiedades críticas están disponibles
            assert hasattr(config, 'RTSP_URL')
            assert hasattr(config, 'BOT_TOKEN')
            assert hasattr(config, 'CHAT_ID')
            
            # Verificar que no son None o vacías
            assert config.RTSP_URL
            assert config.BOT_TOKEN
            assert config.CHAT_ID
            
        except ValidationError as e:
            pytest.fail(
                f"Error de validación al instanciar Config: {e}. "
                "Verificar que las variables de entorno tienen el formato correcto."
            )
        except Exception as e:
            pytest.fail(
                f"Error inesperado al instanciar Config: {e}. "
                "Verificar la configuración del entorno."
            )
    
    def test_rtsp_url_format(self):
        """Verificar que RTSP_URL tiene un formato básico válido."""
        rtsp_url = os.environ.get("RTSP_URL", "")
        
        assert rtsp_url.startswith(("rtsp://", "rtsps://")), (
            f"RTSP_URL debe comenzar con 'rtsp://' o 'rtsps://', actual: {rtsp_url}"
        )
    
    def test_bot_token_format(self):
        """Verificar que BOT_TOKEN tiene un formato básico válido."""
        bot_token = os.environ.get("BOT_TOKEN", "")
        
        # Token de Telegram tiene formato: número:cadena_alfanumérica
        assert ":" in bot_token, (
            f"BOT_TOKEN debe tener formato 'número:token', actual: {bot_token[:20]}..."
        )
        
        parts = bot_token.split(":")
        assert len(parts) == 2, (
            f"BOT_TOKEN debe tener exactamente un ':' separando ID y token"
        )
        
        assert parts[0].isdigit(), (
            f"La primera parte del BOT_TOKEN debe ser numérica (bot ID)"
        )
        
        assert len(parts[1]) >= 35, (
            f"La segunda parte del BOT_TOKEN debe tener al menos 35 caracteres"
        )
    
    def test_chat_id_format(self):
        """Verificar que CHAT_ID tiene un formato válido."""
        chat_id = os.environ.get("CHAT_ID", "")
        
        # Chat ID puede ser positivo (usuario) o negativo (grupo/canal)
        assert chat_id.lstrip("-").isdigit(), (
            f"CHAT_ID debe ser un número (positivo para usuarios, negativo para grupos), actual: {chat_id}"
        )
        
        # Verificar longitud mínima razonable
        assert len(chat_id.lstrip("-")) >= 8, (
            f"CHAT_ID debe tener al menos 8 dígitos, actual: {chat_id}"
        )