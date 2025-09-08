# TASK.md - Construcción de kdx-pi-cam

Guía paso a paso para construir **kdx-pi-cam** siguiendo arquitectura por capas (Layered Architecture).

## Infrastructure Layer (Capa de Infraestructura)

[ ] Crear `infrastructure/config.py` - Implementar patrón Singleton para configuración centralizada con validación de variables de entorno críticas (RTSP_URL, BOT_TOKEN, CHAT_ID) y opcionales usando pydantic

[ ] Crear `infrastructure/events.py` - Implementar patrón Observer/Publisher-Subscriber para sistema de eventos asíncronos con bus centralizado y logging de eventos

[ ] Crear `infrastructure/notifier.py` - Implementar patrón Singleton para sistema de notificaciones centralizado con métodos info, error, warning, debug y clase Log para eventos tipificados

## Service Layer (Capa de Servicios)

[ ] Crear `services/telegram_output.py` - Implementar servicio de envío a Telegram con manejo de rate limits, retry logic y gestión de conexión usando python-telegram-bot

[ ] Crear `services/telegram_input.py` - Implementar servicio de recepción desde Telegram con manejo de webhooks/polling, procesamiento de comandos y publicación de eventos

[ ] Crear `services/file_storage_service.py` - Implementar patrón Strategy para gestión de archivos con interface FileStorageBackend, implementación LocalFileSystemStorage y caché FIFO con rotación automática

[ ] Crear `services/video_stream_service.py` - Implementar servicio integrado de video RTSP con detección de movimiento usando OpenCV, buffer circular y procesamiento unificado de frames

## Business Layer (Capa de Negocio)

[ ] Crear `core/models.py` - Definir entidades del dominio usando dataclasses o pydantic: VideoRequest, NotificationEvent, CameraStatus, UserSession, SystemEvent, UserActionEvent, FileMetadata, CacheEntry, StorageEvent, StorageStats

[ ] Crear `core/video_manager.py` - Implementar lógica de negocio para gestión de video con procesamiento de solicitudes, aplicación de reglas de negocio (timeouts, límites) y coordinación entre servicios

[ ] Crear `core/notification_manager.py` - Implementar lógica de negocio para notificaciones inteligentes con reglas anti-spam, evaluación de condiciones de usuario y clasificación de tipos de notificación

## Presentation Layer (Capa de Presentación)

[ ] Crear `handlers/telegram_handler.py` - Implementar interfaz de usuario Telegram con manejo de comandos (/start, /clip5, /clip20, /photo), callbacks de botones inline y validación básica de inputs

## Entry Point (Punto de Entrada)

[ ] Crear `app.py` - Implementar punto de entrada único con patrón Dependency Injection para inicialización de capas en orden correcto, configuración del sistema de eventos y manejo de shutdown graceful

## Configuración del Proyecto

[ ] Actualizar `pyproject.toml` - Configurar dependencias del proyecto usando uv con todas las librerías requeridas: python-telegram-bot, opencv-python, ffmpeg-python, numpy, pillow, pydantic, python-dotenv, psutil, pytest

[ ] Crear archivo `.env` - Copiar desde .env.example y configurar variables de entorno críticas y opcionales según REQUIREMENTS.md

## Testing y Validación

[ ] Ejecutar `uv sync` - Instalar todas las dependencias del proyecto

[ ] Ejecutar `uv run python app.py` - Probar inicialización básica de la aplicación y verificar que todas las capas se inicialicen correctamente

[ ] Validar comunicación entre capas - Verificar que el sistema de eventos funcione correctamente y que las dependencias estén bien inyectadas

---

**Patrones de Diseño Utilizados:**
- **Layered Architecture**: Separación clara de responsabilidades por capas
- **Singleton**: Para configuración y notificaciones centralizadas
- **Observer/Publisher-Subscriber**: Para comunicación asíncrona entre capas
- **Strategy**: Para intercambio de backends de almacenamiento
- **Dependency Injection**: Para inyección de dependencias en app.py

**Principios de Comunicación:**
- Presentation → Infrastructure (solo eventos y notifier)
- Business → Service + Infrastructure
- Service → Infrastructure
- Infrastructure → Ninguna dependencia externa