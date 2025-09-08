# kdx-pi-cam

**kdx-pi-cam** es una aplicación Python asíncrona basada en `python-telegram-bot` que procesa video de una cámara RTSP bajo demanda. Los usuarios envían comandos a través de Telegram como input, y la aplicación responde con cortos de video como output. Además, incluye un servicio de detección de movimientos que monitorea continuamente el stream RTSP y genera notificaciones automáticas.

La aplicación utiliza un sistema de notificaciones centralizado (`Notifier`) que soporta logging estructurado y envío opcional a Telegram, permitiendo que toda la aplicación use un único punto de salida para logs y notificaciones.

## Arquitectura

Aplicación Python asíncrona con **arquitectura por capas** (layered architecture):

### Entry Point
- `app.py`: Inicialización y orquestación de capas

### Presentation Layer (`handlers/`)
- `telegram_handler.py`: Manejo de comandos y callbacks de Telegram

### Business Layer (`core/`)
- `video_manager.py`: Lógica de negocio para captura y procesamiento
- `notification_manager.py`: Gestión de notificaciones y alertas

### Service Layer (`services/`)
- `telegram_output.py`: Envío de mensajes a Telegram
- `telegram_input.py`: Recepción de comandos desde Telegram
- `file_storage_service.py`: Gestión de archivos con caché FIFO
- `video_stream_service.py`: Servicio de video con RTSP y detección de movimiento

### Infrastructure Layer (`infrastructure/`)
- `config.py`: Configuración y variables de entorno
- `events.py`: Sistema de eventos asíncronos
- `notifier.py`: Sistema de notificaciones centralizado

## Estructura del Proyecto

```
kdx-pi-cam/
├── handlers/                        # Capa de Presentación
│   └── telegram_handler.py          # Comandos Telegram (usa telegram_input.py)
├── core/                            # Capa de Negocio
│   ├── video_manager.py             # Lógica de video (usa file_storage_service)
│   ├── notification_manager.py      # Lógica de notificaciones (usa Notifier)
│   └── models.py                    # Entidades del dominio
├── services/                        # Capa de Servicios
│   ├── telegram_output.py           # Envío a Telegram
│   ├── telegram_input.py            # Recepción desde Telegram
│   ├── file_storage_service.py      # Gestión de archivos con caché FIFO
│   └── video_stream_service.py      # Servicio de video con RTSP y detección de movimiento
├── infrastructure/                  # Capa de Infraestructura
│   ├── config.py                    # Configuración
│   ├── events.py                    # Eventos
│   └── notifier.py                  # Clase Notifier centralizada
├── .env                             # Variables de entorno (no versionado)
├── pyproject.toml                   # Configuración del proyecto y dependencias (uv)
├── uv.lock                          # Lock file de dependencias (uv)
└── app.py                           # Punto de entrada
```

## Descripción Detallada de Capas

### Entry Point

#### `app.py`
- **Responsabilidad**: Punto de entrada único de la aplicación
- **Funciones**:
  - Inicialización de todas las capas en orden correcto
  - Configuración del sistema de eventos
  - Orquestación del ciclo de vida de la aplicación
  - Manejo de shutdown graceful 
- **Dependencias**: Todas las capas (para inicialización)
- **Comunicación**: Configura el bus de eventos para comunicación entre capas

### Presentation Layer (`handlers/`)

#### `telegram_handler.py`
- **Responsabilidad**: Interfaz de usuario a través de Telegram
- **Funciones**:
  - Recepción de comandos de usuario (`/start`, `/clip5`, `/clip20`, `/photo`)
  - Manejo de callbacks de botones inline
  - Validación básica de inputs
  - Formateo de respuestas para Telegram
- **Dependencias**: Solo infrastructure (eventos)
- **Comunicación**: Publica eventos hacia Business Layer
- **Restricciones**: No contiene lógica de negocio

### Business Layer (`core/`)

#### `video_manager.py`
- **Responsabilidad**: Lógica de negocio para gestión de video
- **Funciones**:
  - Procesamiento de solicitudes de video
  - Aplicación de reglas de negocio (timeouts, límites)
  - Coordinación entre servicios de video
  - Gestión de estados de captura
- **Dependencias**: Service Layer (RTSP), Infrastructure (Notifier)
- **Comunicación**: Consume eventos de Presentation, usa Services y Notifier

#### `notification_manager.py`
- **Responsabilidad**: Lógica de negocio para notificaciones inteligentes
- **Funciones**:
  - Determinación de cuándo notificar según reglas de negocio
  - Aplicación de reglas anti-spam (cooldown, frecuencia)
  - Clasificación y priorización de tipos de notificación
  - Evaluación de condiciones de usuario (silenciado, horarios)
  - Agregación de contexto relevante según el tipo de evento
  - Gestión de estados de notificación por usuario
- **Dependencias**: Infrastructure (Notifier)
- **Comunicación**: Consume eventos de negocio, usa Notifier para envío
- **Diferencia con Notifier**: Contiene inteligencia de negocio, mientras que Notifier es solo el mecanismo de envío

#### `models.py`
- **Responsabilidad**: Entidades del dominio
- **Contenido**:
  - `VideoRequest`: Solicitud de captura de video
  - `NotificationEvent`: Evento de notificación
  - `CameraStatus`: Estado de la cámara
  - `UserSession`: Sesión de usuario
  - `SystemEvent`: Evento del sistema con timestamp y tipo para logging estructurado
  - `UserActionEvent`: Evento de acción de usuario con user_id, acción y detalles para logging estructurado
  - `FileMetadata`: Metadatos de archivo (path, size, timestamp, type, checksum)
  - `CacheEntry`: Entrada de caché con información de acceso y expiración
  - `StorageEvent`: Evento de almacenamiento (file_stored, file_deleted, cache_full)
  - `StorageStats`: Estadísticas de uso del almacenamiento (total_size, files_count, cache_hit_rate)
- **Dependencias**: Ninguna (entidades puras)

### Service Layer (`services/`)

#### `telegram_output.py`
- **Responsabilidad**: Envío de mensajes a Telegram
- **Funciones**:
  - Envío de mensajes y archivos
  - Gestión de conexión con Telegram
  - Manejo de rate limits
  - Retry logic para fallos de red
- **Dependencias**: Infrastructure (config)
- **Comunicación**: Usado por Infrastructure (Notifier)

#### `telegram_input.py`
- **Responsabilidad**: Recepción de comandos desde Telegram
- **Funciones**:
  - Manejo de webhooks/polling
  - Procesamiento de comandos de usuario
  - Gestión de callbacks de botones
  - Validación de inputs
- **Dependencias**: Infrastructure (config, events)
- **Comunicación**: Publica eventos hacia Business Layer

#### `file_storage_service.py`
- **Responsabilidad**: Gestión integral de archivos con caché y rotación FIFO
- **Funciones**:
  - Caché de videos con tamaño configurable en MB
  - Rotación automática FIFO cuando se excede el límite
  - Escritura asíncrona en disco con buffer
  - Gestión de metadatos de archivos (timestamp, tamaño, tipo)
  - Limpieza automática de archivos expirados
  - Compresión opcional de archivos antiguos
- **Patrón de Diseño**: Strategy Pattern para diferentes backends de almacenamiento
- **Implementaciones**:
  - `LocalFileSystemStorage`: Almacenamiento en disco local (implementación por defecto)
  - `S3FileSystemStorage`: Almacenamiento en AWS S3 (ejemplo de escalabilidad)
  - `AzureBlobStorage`: Almacenamiento en Azure Blob (ejemplo de escalabilidad)
- **Dependencias**: Infrastructure (config, events, notifier)
- **Comunicación**: Usado por Business Layer (video_manager), publica eventos de storage
- **Características**:
  - Interface `FileStorageBackend` para intercambio de implementaciones
  - Configuración por variables de entorno (tamaño caché, directorio, compresión)
  - Métricas de uso de almacenamiento y rendimiento
  - Recuperación automática ante fallos de escritura

#### `video_stream_service.py`
- **Responsabilidad**: Servicio de video que integra captura RTSP y detección de movimiento
- **Funciones**:
  - Conexión permanente al stream RTSP con buffer circular
  - Detección de movimiento integrada en el mismo loop de procesamiento
  - Extracción de segmentos de video bajo demanda
  - Manejo unificado de reconexiones y estados
- **Dependencias**: Infrastructure (config, events, notifier)
- **Comunicación**: Publica eventos `frame_available`, `motion_detected`, `stream_connected/disconnected`
- **Características**:
  - Procesamiento eficiente de frames en un solo loop
  - Sincronización perfecta entre captura y detección
  - Gestión integrada de estados de conexión
  - Buffer circular optimizado para ambas funciones

### Infrastructure Layer (`infrastructure/`)

#### `config.py`
- **Responsabilidad**: Configuración centralizada
- **Contenido**:
  - Variables de entorno
  - Configuración de servicios externos
  - Parámetros de la aplicación
  - Validación de configuración
- **Variables Críticas del Sistema**:
  - `RTSP_URL`: URL de la cámara RTSP
  - `BOT_TOKEN`: Token del bot de Telegram
  - `CHAT_ID`: ID del chat de Telegram para notificaciones
- **Almacenamiento y Caché**:
  - `CACHE_DIR`: Directorio base para almacenamiento temporal
  - `CACHE_MAX_SIZE_MB`: Límite de tamaño del caché en MB
  - `CACHE_COMPRESSION_ENABLED`: Activar compresión de archivos antiguos
  - `CACHE_CLEANUP_INTERVAL`: Intervalo de limpieza automática
  - `STORAGE_BACKEND`: Tipo de backend (`local`, `s3`, `azure`, `gcp`)
- **Detección de Movimiento**:
  - `MOTION_SENSITIVITY`: Sensibilidad del algoritmo (0.0-1.0)
  - `MOTION_MIN_AREA`: Área mínima en píxeles para movimiento válido
- **Procesamiento de Video**:
  - `VIDEO_BUFFER_SECONDS`: Duración del buffer circular
  - `VIDEO_MAX_DURATION`: Duración máxima de videos solicitados
  - `VIDEO_QUALITY`: Calidad de video (`low`, `medium`, `high`)
- **Sistema de Notificaciones**:
  - `NOTIFICATION_COOLDOWN_SECONDS`: Tiempo mínimo entre notificaciones
  - `NOTIFICATION_QUIET_HOURS_START`: Hora inicio modo silencioso
  - `NOTIFICATION_QUIET_HOURS_END`: Hora fin modo silencioso
- **Logging y Depuración**:
  - `LOG_LEVEL`: Nivel de logging (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`)
  - `LOG_TO_FILE`: Guardar logs en archivo (`true`/`false`)
  - `LOG_FILE_PATH`: Ruta del archivo de logs (./cache/logs/kdx-pi-cam.log)
  - `LOG_ROTATION_ENABLED`: Activar rotación automática de logs
  - `LOG_MAX_FILE_SIZE_MB`: Tamaño máximo antes de rotar (MB)
  - `LOG_BACKUP_COUNT`: Número de archivos de backup a mantener
- **Dependencias**: Ninguna
- **Uso**: Inyectado en todas las capas que lo necesiten
- **⚠️ Nota para AI**: Las 3 variables de entorno obligatorias se asumen existentes en `.env` y no requieren validación adicional por parte de la AI

#### `events.py`
- **Responsabilidad**: Sistema de eventos asíncronos
- **Funciones**:
  - Bus de eventos centralizado
  - Publicación/suscripción de eventos
  - Manejo asíncrono de eventos
  - Logging de eventos para debugging
- **Dependencias**: Ninguna
- **Comunicación**: Usado por todas las capas

#### `notifier.py`
- **Responsabilidad**: Sistema de notificaciones centralizado (infraestructura)
- **Funciones**:
  - `Notifier.info(message, to_telegram=False)`: Información general
  - `Notifier.error(message, to_telegram=False)`: Errores del sistema
  - `Notifier.warning(message, to_telegram=False)`: Advertencias
  - `Notifier.debug(message, to_telegram=False)`: Información de debug
  - `Log.system_event(event: SystemEvent)`: Eventos del sistema con timestamp usando clase Log tipificada
  - `Log.user_action_event(event: UserActionEvent)`: Acciones de usuario usando clase Log tipificada
- **Características**:
  - Logging estructurado interno con `logger`
  - Parámetro `to_telegram` opcional (default: False)
  - Único punto de salida técnico para toda la aplicación
  - Formateo automático según el canal de salida
  - Manejo asíncrono de envíos a Telegram
- **Dependencias**: Service Layer (telegram_output.py cuando to_telegram=True)
- **Uso**: Instancia única accesible desde todas las capas para logging directo
- **Diferencia con NotificationManager**: Es herramienta técnica sin lógica de negocio

## Flujo de Datos

### Flujo Principal (Solicitud de Video)

1. **Presentation**: `telegram_handler.py` recibe comando `/clip5`
2. **Event**: Publica `VideoRequested(seconds=5, user_id=123)`
3. **Business**: `video_manager.py` consume evento y valida solicitud
4. **Service**: Llama a `video_stream_service.py` para obtener video de 5 segundos
5. **Service**: `video_stream_service.py` extrae segmento del buffer
6. **Business**: `video_manager.py` procesa el video
7. **Service**: `video_manager.py` usa `file_storage_service.py` para almacenar video en caché
8. **Service**: `file_storage_service.py` gestiona rotación FIFO si es necesario
9. **Service**: Usa `telegram_output.py` para enviar video al usuario
10. **Infrastructure**: `events.py` maneja toda la comunicación asíncrona

### Flujo de Gestión de Caché

1. **Service**: `file_storage_service.py` monitorea el tamaño del caché continuamente
2. **Event**: Si se excede el límite, publica `CacheLimitExceeded(current_size, limit)`
3. **Service**: Ejecuta rotación FIFO eliminando archivos más antiguos
4. **Event**: Publica `FileDeleted(file_path, reason='cache_rotation')`
5. **Infrastructure**: `notifier.py` registra eventos de gestión de caché
6. **Optional**: Compresión de archivos antes de eliminación según configuración

### Flujo de Notificaciones

#### Notificaciones Simples (Logging directo)
1. **Cualquier capa**: Usa `notifier.info("Mensaje")` directamente
2. **Infrastructure**: `notifier.py` registra en log
3. **Opcional**: Si `to_telegram=True`, envía via `telegram_output.py`

#### Notificaciones Inteligentes (Con lógica de negocio)
1. **Service**: `video_stream_service.py` detecta desconexión
2. **Event**: Publica `ConnectionLost(timestamp, reason)`
3. **Business**: `notification_manager.py` evalúa:
   - ¿Ya notifiqué hace poco? (anti-spam)
   - ¿Es horario válido para notificar?
   - ¿El usuario tiene notificaciones habilitadas?
4. **Business**: Si procede, usa `notifier.error(message, to_telegram=True)`
5. **Infrastructure**: `notifier.py` envía via `telegram_output.py`
6. **Infrastructure**: `events.py` coordina todo el flujo asíncrono

## Principios de Comunicación

### Reglas de Dependencia
- **Presentation** → **Infrastructure** (solo eventos y notifier)
- **Business** → **Service** + **Infrastructure**
- **Service** → **Infrastructure**
- **Infrastructure** → Ninguna

### Comunicación Asíncrona
- Todas las capas se comunican a través del bus de eventos (`events.py`)
- No hay referencias directas entre Presentation y Business
- Los eventos son el único mecanismo de acoplamiento entre capas
- `events.py` permite desacoplamiento total y comunicación asíncrona

### Sistema de Notificaciones Dual
- **Notificaciones directas**: Cualquier capa → `notifier.py` (logging simple)
- **Notificaciones inteligentes**: Eventos → `notification_manager.py` → `notifier.py`
- **Principio**: Usar notifier directamente para logs, notification_manager para lógica de negocio

### Inyección de Dependencias
- `app.py` configura todas las dependencias
- Cada capa recibe solo las dependencias que necesita
- Las interfaces están definidas implícitamente por uso
- `notifier.py` es inyectado como singleton global

## Diseño del Servicio de Video

### Arquitectura Integrada

**kdx-pi-cam** utiliza un diseño integrado para el procesamiento de video a través de `video_stream_service.py`, que combina la captura RTSP y la detección de movimiento en un solo servicio optimizado.

### Ventajas del Diseño Integrado

- **Eficiencia de recursos**: Un solo loop procesa frames para ambas funciones
- **Sincronización perfecta**: Detección y captura en el mismo contexto temporal
- **Menor latencia**: Sin overhead de comunicación entre servicios separados
- **Simplicidad operacional**: Un solo punto de gestión para el procesamiento de video
- **Coherencia de estado**: Estado unificado de conexión y buffer

### Implementación

El servicio mantiene una arquitectura interna clara:
- Métodos separados para cada responsabilidad (`_process_rtsp_frame`, `_detect_motion`)
- Interfaces bien definidas para facilitar testing
- Eventos separados (`frame_available`, `motion_detected`) para comunicación con otras capas
- Composition pattern para algoritmos de detección intercambiables

## Diseño del Servicio de Almacenamiento

### Arquitectura Extensible con Strategy Pattern

**kdx-pi-cam** implementa un sistema de almacenamiento flexible a través de `file_storage_service.py`, que utiliza el patrón Strategy para soportar múltiples backends de almacenamiento.

### Características del Sistema de Caché

- **Caché FIFO inteligente**: Rotación automática basada en tamaño configurable en MB
- **Gestión asíncrona**: Escritura no bloqueante con buffer interno
- **Metadatos completos**: Tracking de timestamp, tamaño, tipo y checksum
- **Recuperación ante fallos**: Retry automático y logging de errores
- **Métricas en tiempo real**: Estadísticas de uso y rendimiento

### Backends de Almacenamiento

#### Implementación Local (Por Defecto)
- `LocalFileSystemStorage`: Almacenamiento en disco local optimizado
- Gestión de directorios automática
- Compresión opcional de archivos antiguos
- Limpieza programada de archivos temporales

#### Escalabilidad Cloud (Ejemplos de Extensión)
- `S3FileSystemStorage`: Integración con AWS S3 para almacenamiento distribuido
- `AzureBlobStorage`: Soporte para Azure Blob Storage
- `GCPCloudStorage`: Extensión para Google Cloud Storage

### Ventajas del Diseño Strategy

- **Intercambiabilidad**: Cambio de backend sin modificar código cliente
- **Testabilidad**: Mock backends para testing unitario
- **Configurabilidad**: Selección de backend por variables de entorno
- **Extensibilidad**: Nuevos backends sin modificar código existente
- **Consistencia**: Interface uniforme independiente del backend

### Interface FileStorageBackend

```python
class FileStorageBackend(Protocol):
    async def store_file(self, file_path: str, content: bytes) -> FileMetadata
    async def retrieve_file(self, file_path: str) -> bytes
    async def delete_file(self, file_path: str) -> bool
    async def list_files(self) -> List[FileMetadata]
    async def get_storage_stats(self) -> StorageStats
    async def cleanup_expired_files(self) -> int
```

## Comandos de Captura de Imagen

### Comando `/photo`

**kdx-pi-cam** incluye funcionalidad de captura de imágenes estáticas a través del comando `/photo`, que permite obtener instantáneas del stream RTSP sin necesidad de grabar video.

### Flujo de Captura de Imagen

1. **Presentation**: `telegram_handler.py` recibe comando `/photo`
2. **Event**: Publica `PhotoRequested(user_id=123)`
3. **Business**: `video_manager.py` consume evento y solicita captura
4. **Service**: `video_stream_service.py` extrae frame actual del buffer
5. **Infrastructure**: `file_storage_service.py` almacena imagen en caché
6. **Presentation**: Telegram envía imagen al usuario

### Características de la Captura

- **Captura instantánea**: Utiliza el frame más reciente del buffer circular
- **Formato optimizado**: Compresión JPEG con calidad configurable
- **Gestión de caché**: Almacenamiento temporal con limpieza automática
- **Respuesta rápida**: Sin necesidad de inicializar nueva conexión RTSP
- **Metadatos incluidos**: Timestamp y información de la cámara

### Configuración del Caché

- `CACHE_MAX_SIZE_MB`: Tamaño máximo del caché en megabytes
- `CACHE_DIR`: Directorio base para almacenamiento local
- `CACHE_COMPRESSION_ENABLED`: Activar compresión de archivos antiguos
- `CACHE_CLEANUP_INTERVAL`: Intervalo de limpieza automática en segundos
- `STORAGE_BACKEND`: Tipo de backend (`local`, `s3`, `azure`, `gcp`)

## Beneficios de la Arquitectura

- **Separación de responsabilidades**: Cada capa tiene un propósito específico
- **Testabilidad**: Cada capa se puede testear independientemente
- **Mantenibilidad**: Cambios en una capa no afectan otras
- **Escalabilidad**: Fácil agregar nuevos handlers o servicios
- **Flexibilidad**: Intercambio de implementaciones sin afectar otras capas