# Plan de Pruebas para kdx-pi-cam

Tests para aplicación Python asíncrona de procesamiento de video RTSP con notificaciones Telegram.

## 0. Tests de Validación de Entorno ⭐

**PRIORIDAD CRÍTICA**: Estos tests deben ejecutarse PRIMERO y pasar antes que cualquier otro.

### 0.1. Validación de Variables de Entorno → **tests/test_environment_validation.py**
- Verificación de existencia de variables obligatorias:
  - `RTSP_URL`: URL de la cámara RTSP
  - `BOT_TOKEN`: Token del bot de Telegram
  - `CHAT_ID`: ID del chat de Telegram para notificaciones
- Validación de formato básico de cada variable
- Verificación de que Config puede instanciarse correctamente
- Garantía de que las variables no están vacías

### 0.2. Validación de Dependencias → **tests/test_dependencies_validation.py**
- Verificación de dependencias principales:
  - `python-telegram-bot`: Integración con Telegram
  - `ffmpeg-python`: Procesamiento de video
  - `opencv-python`: Visión por computadora
  - `numpy`: Computación numérica
  - `pillow`: Procesamiento de imágenes
  - `pydantic`: Validación de datos
  - `python-dotenv`: Variables de entorno
  - `psutil`: Información del sistema
- Verificación de dependencias de desarrollo:
  - `pytest`: Framework de testing
  - `pytest-asyncio`: Testing asíncrono
- Validación de versión de Python (>=3.11)

**Objetivo**: Establecer una base sólida que garantice que el entorno está correctamente configurado. Una vez que estos tests pasan, el resto de tests pueden asumir que las variables de entorno y dependencias son válidas sin necesidad de validaciones adicionales.

**Beneficios**:
- ✅ Detección temprana de problemas de configuración y dependencias
- ✅ Mensajes de error claros y específicos
- ✅ Evita fallos confusos en tests posteriores
- ✅ Simplifica el resto de tests al eliminar validaciones repetitivas

---

## 1. Tests Unitarios

### 1.1. Infrastructure Layer

#### `infrastructure/config.py` → **tests/test_config.py**
- Carga y validación de variables de entorno
- Validación de tipos (URLs, enteros, booleanos)

#### `infrastructure/events.py` → **tests/test_events.py**
- Sistema de eventos asíncronos
- Registro, disparo y suscripción de eventos
- Manejo concurrente

#### `infrastructure/notifier.py` → **tests/test_notifier.py**
- Sistema de notificaciones centralizado
- Logging con diferentes niveles
- Envío a Telegram y manejo de errores

#### **tests/test_infrastructure.py** (Test general de Infrastructure Layer)
- Integración entre config, events y notifier
- Inicialización completa de la capa infrastructure
- Patrones Singleton y comunicación entre componentes

### 1.2. Core Layer

#### `core/models.py` → **tests/test_models.py**
- Entidades del dominio: creación y validación
- Eventos de logging estructurado
- Metadatos de archivos y caché

#### `core/video_manager.py` → **tests/test_video_manager.py**
- Lógica de negocio para gestión de video
- Validación de solicitudes y reglas de negocio
- Integración con almacenamiento

#### `core/notification_manager.py` → **tests/test_notification_manager.py**
- Notificaciones inteligentes
- Reglas anti-spam y condiciones de usuario
- Manejo de errores con `notify.error`

### 1.3. Services Layer

#### `services/telegram_output.py` → **tests/test_telegram_output.py**
- Envío de mensajes y archivos
- Rate limits y retry logic

#### `services/telegram_input.py` → **tests/test_telegram_input.py**
- Recepción y procesamiento de comandos
- Validación de inputs

#### `services/file_storage_service.py` → **tests/test_file_storage_service.py**
- Gestión de archivos con caché FIFO
- Rotación automática y limpieza
- Backends de almacenamiento

#### `services/video_stream_service.py` → **tests/test_video_stream_service.py**
- Captura RTSP y detección de movimiento
- Buffer circular y extracción de segmentos
- Manejo de conexiones

### 1.4. Presentation Layer

#### `handlers/telegram_handler.py` → **tests/test_telegram_handler.py**
- Interfaz de usuario Telegram
- Comandos y callbacks
- Publicación de eventos

### 1.5. Application Layer

#### `app.py` → **tests/test_app.py**
- Entry point y inicialización completa
- Integración de todos los servicios
- Manejo de shutdown graceful
- Flujo completo de la aplicación

## 2. Tests de Integración → **tests/test_integration.py**

### 2.1. Comunicación entre capas
- Bus de eventos asíncrono
- Flujos completos: solicitud de video y detección de movimiento

### 2.2. Notificaciones inteligentes
- Integración `notification_manager` y `notifier`
- Reglas anti-spam en escenarios reales

### 2.3. Servicio de video integrado
- Captura RTSP + detección de movimiento
- Sincronización y extracción de segmentos

### 2.4. Almacenamiento con video_manager
- Caché automático y rotación FIFO
- Recuperación desde caché

## 3. Tests de Sistema (End-to-End) → **tests/test_e2e.py**

### 3.1. Solicitud de video y foto
- Comandos `/clip5`, `/clip20`, `/photo`
- Flujo completo: solicitud → procesamiento → caché → entrega

### 3.2. Detección de movimiento y notificación
- Detección automática y evaluación de condiciones
- Notificación a Telegram

### 3.3. Manejo de desconexiones
- Detección de desconexión RTSP
- Notificación de error y reconexión automática

## 4. Tests de Rendimiento → **tests/test_performance.py**

### 4.1. Procesamiento de video
- Tiempo de respuesta y uso de recursos
- Solicitudes concurrentes
- Rendimiento de caché y rotación FIFO

### 4.2. Detección de movimiento
- Tiempo de detección y uso de recursos

### 4.3. Comunicación con Telegram
- Tiempo de respuesta y rate limits
- Usuarios concurrentes

## 5. Tests de Seguridad → **tests/test_security.py**

### 5.1. Validación de inputs
- Inputs maliciosos e inyección de comandos
- Solicitudes con duraciones inválidas

### 5.2. Manejo de credenciales
- Tokens no logueados en texto plano
- Carga segura desde variables de entorno

## 6. Tests de Configuración → **tests/test_configuration.py**

### 6.1. Variables de entorno
- Variables requeridas y opcionales
- Configuración de caché y backends
- Manejo de errores de configuración

---

## Estructura de Archivos de Test

```
tests/
├── __init__.py
├── conftest.py                    # Fixtures compartidas
├── test_environment_validation.py # ⭐ Validación de variables de entorno
├── test_dependencies_validation.py # ⭐ Validación de dependencias
├── test_infrastructure.py         # Test general Infrastructure Layer
├── test_config.py                 # infrastructure/config.py
├── test_events.py                 # infrastructure/events.py
├── test_notifier.py               # infrastructure/notifier.py
├── test_models.py                 # core/models.py
├── test_video_manager.py          # core/video_manager.py
├── test_notification_manager.py   # core/notification_manager.py
├── test_telegram_output.py        # services/telegram_output.py
├── test_telegram_input.py         # services/telegram_input.py
├── test_file_storage_service.py   # services/file_storage_service.py
├── test_video_stream_service.py   # services/video_stream_service.py
├── test_telegram_handler.py       # handlers/telegram_handler.py
├── test_app.py                    # app.py
├── test_integration.py            # Tests de integración
├── test_e2e.py                    # Tests end-to-end
├── test_performance.py            # Tests de rendimiento
├── test_security.py               # Tests de seguridad
└── test_configuration.py          # Tests de configuración
```

## Orden de Desarrollo de Tests (según TASK.md)

**Prioridad Crítica (Base del Sistema):**
0.1. `test_environment_validation.py` - ⭐ **EJECUTAR PRIMERO** - Validación de variables de entorno críticas
0.2. `test_dependencies_validation.py` - ⭐ **EJECUTAR SEGUNDO** - Validación de dependencias instaladas

**Prioridad Alta (Infrastructure Layer):**
1. `test_config.py` - Configuración centralizada con Singleton
2. `test_events.py` - Sistema de eventos asíncronos
3. `test_notifier.py` - Sistema de notificaciones centralizado
4. `test_infrastructure.py` - Integración completa de infrastructure

**Prioridad Media (Services & Core):**
5. `test_telegram_output.py` - Servicio básico de envío a Telegram
6. `test_telegram_input.py` - Servicio de recepción de comandos
7. `test_models.py` - Entidades del dominio
8. `test_video_stream_service.py` - Servicio RTSP y detección de movimiento
9. `test_video_manager.py` - Lógica de negocio para gestión de video
10. `test_file_storage_service.py` - Sistema de almacenamiento
11. `test_notification_manager.py` - Notificaciones inteligentes

**Prioridad Baja (Handlers & App):**
12. `test_telegram_handler.py` - Manejador de comandos Telegram
13. `test_app.py` - Entry point y integración completa

**Tests Especializados:**
14. `test_integration.py` - Tests de integración entre capas
15. `test_e2e.py` - Tests end-to-end completos
16. `test_performance.py` - Tests de rendimiento
17. `test_security.py` - Tests de seguridad
18. `test_configuration.py` - Tests de configuración

## Metodología de Testing

- **Testing Continuo**: Cada módulo se prueba antes de continuar con el siguiente
- **Mocks y Fixtures**: Usar `unittest.mock` y `pytest.fixtures` para aislar componentes
- **Cobertura**: Objetivo mínimo 80% de cobertura de código
- **Integración Incremental**: Tests de integración después de cada capa completada