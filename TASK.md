# TASK.md - Construcción de kdx-pi-cam

Guía paso a paso para construir **kdx-pi-cam** con desarrollo incremental. El archivo `app.py` se mantiene abierto y evoluciona según las necesidades que surjan.

## Configuración Inicial del Proyecto

[ ] Actualizar `pyproject.toml` - Configurar dependencias básicas: python-telegram-bot, opencv-python, ffmpeg-python, numpy, pillow, pydantic, python-dotenv, psutil, pytest

[ ] Crear archivo `.env` - Copiar desde .env.example y configurar variables críticas: RTSP_URL, BOT_TOKEN, CHAT_ID

[ ] Ejecutar `uv sync` - Instalar dependencias del proyecto

## Desarrollo Incremental (app.py siempre abierto)

[ ] Crear `infrastructure/config.py` - Implementar configuración centralizada con patrón Singleton y validación de variables de entorno usando pydantic

[ ] Crear `app.py` inicial - Entry point básico que importa config, inicializa logging básico y define estructura main() con manejo de shutdown graceful

[ ] Probar `app.py` inicial - Ejecutar `uv run python app.py` para verificar configuración básica y imports

[ ] Expandir `app.py` - Añadir sistema de eventos asíncronos básico y estructura para inicialización de servicios

[ ] Crear `infrastructure/events.py` - Implementar patrón Observer/Publisher-Subscriber para comunicación asíncrona entre componentes

[ ] Actualizar `app.py` - Integrar sistema de eventos y preparar inicialización de servicios Telegram

[ ] Crear `infrastructure/notifier.py` - Sistema de notificaciones centralizado con métodos info, error, warning, debug y logging estructurado

[ ] Actualizar `app.py` - Integrar notifier como singleton global y configurar logging avanzado

[ ] Crear `services/telegram_output.py` - Servicio básico de envío a Telegram con manejo de conexión y rate limits

[ ] Actualizar `app.py` - Inicializar servicio de output de Telegram y probar envío básico de mensajes

[ ] Crear `services/telegram_input.py` - Servicio de recepción de comandos Telegram con polling/webhooks y publicación de eventos

[ ] Actualizar `app.py` - Integrar servicio de input de Telegram y configurar manejo de comandos básicos

[ ] Crear `handlers/telegram_handler.py` - Manejador de comandos Telegram (/start, /clip5, /clip20, /photo) con validación básica

[ ] Actualizar `app.py` - Conectar handler de Telegram con sistema de eventos y probar comandos básicos

[ ] Crear `core/models.py` - Entidades del dominio: VideoRequest, NotificationEvent, CameraStatus, UserSession, SystemEvent, FileMetadata

[ ] Crear `services/video_stream_service.py` - Servicio RTSP básico con conexión a cámara y buffer circular simple

[ ] Actualizar `app.py` - Inicializar servicio de video y probar conexión RTSP básica

[ ] Expandir `services/video_stream_service.py` - Añadir detección de movimiento con OpenCV y procesamiento unificado de frames

[ ] Crear `core/video_manager.py` - Lógica de negocio para gestión de video con procesamiento de solicitudes y reglas de timeout

[ ] Actualizar `app.py` - Integrar video manager y conectar con handlers de Telegram para comandos de video

[ ] Crear `services/file_storage_service.py` - Sistema de almacenamiento con patrón Strategy, caché FIFO y rotación automática

[ ] Actualizar `app.py` - Integrar servicio de almacenamiento y configurar gestión de archivos temporales

[ ] Crear `core/notification_manager.py` - Lógica de notificaciones inteligentes con reglas anti-spam y evaluación de condiciones

[ ] Actualizar `app.py` final - Integrar notification manager, configurar todos los servicios y optimizar inicialización completa

## Testing y Validación Final

[ ] Probar funcionalidad completa - Ejecutar `uv run python app.py` y verificar todos los comandos Telegram funcionando

[ ] Validar detección de movimiento - Probar notificaciones automáticas y sistema anti-spam

[ ] Verificar gestión de archivos - Comprobar caché FIFO, rotación automática y limpieza de archivos temporales

---

**Metodología de Desarrollo:**
- **Desarrollo Incremental**: app.py evoluciona continuamente según necesidades
- **Testing Continuo**: Probar cada integración antes de continuar
- **Refactoring Progresivo**: Mejorar código existente al añadir nuevas funcionalidades

**Patrones de Diseño:**
- **Singleton**: Configuración y notificaciones centralizadas
- **Observer/Publisher-Subscriber**: Comunicación asíncrona entre componentes
- **Strategy**: Backends intercambiables de almacenamiento
- **Dependency Injection**: Inyección progresiva en app.py

**Principio Clave:**
- **app.py como núcleo evolutivo**: Se mantiene abierto durante todo el desarrollo, integrando cada nuevo componente y probando su funcionamiento antes de continuar