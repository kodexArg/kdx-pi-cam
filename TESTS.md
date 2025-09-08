# Plan de Pruebas para kdx-pi-cam

Tests para aplicación Python asíncrona de procesamiento de video RTSP con notificaciones Telegram.

## 1. Tests Unitarios

### 1.1. Infrastructure Layer

#### `infrastructure/config.py`
- Carga y validación de variables de entorno
- Validación de tipos (URLs, enteros, booleanos)

#### `infrastructure/events.py`
- Sistema de eventos asíncronos
- Registro, disparo y suscripción de eventos
- Manejo concurrente

#### `infrastructure/notifier.py`
- Sistema de notificaciones centralizado
- Logging con diferentes niveles
- Envío a Telegram y manejo de errores

### 1.2. Core Layer

#### `core/models.py`
- Entidades del dominio: creación y validación
- Eventos de logging estructurado
- Metadatos de archivos y caché

#### `core/video_manager.py`
- Lógica de negocio para gestión de video
- Validación de solicitudes y reglas de negocio
- Integración con almacenamiento

#### `core/notification_manager.py`
- Notificaciones inteligentes
- Reglas anti-spam y condiciones de usuario
- Manejo de errores con `notify.error`

### 1.3. Services Layer

#### `services/telegram_output.py`
- Envío de mensajes y archivos
- Rate limits y retry logic

#### `services/telegram_input.py`
- Recepción y procesamiento de comandos
- Validación de inputs

#### `services/file_storage_service.py`
- Gestión de archivos con caché FIFO
- Rotación automática y limpieza
- Backends de almacenamiento

#### `services/video_stream_service.py`
- Captura RTSP y detección de movimiento
- Buffer circular y extracción de segmentos
- Manejo de conexiones

### 1.4. Presentation Layer

#### `handlers/telegram_handler.py`
- Interfaz de usuario Telegram
- Comandos y callbacks
- Publicación de eventos

## 2. Tests de Integración

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

## 3. Tests de Sistema (End-to-End)

### 3.1. Solicitud de video y foto
- Comandos `/clip5`, `/clip20`, `/photo`
- Flujo completo: solicitud → procesamiento → caché → entrega

### 3.2. Detección de movimiento y notificación
- Detección automática y evaluación de condiciones
- Notificación a Telegram

### 3.3. Manejo de desconexiones
- Detección de desconexión RTSP
- Notificación de error y reconexión automática

## 4. Tests de Rendimiento

### 4.1. Procesamiento de video
- Tiempo de respuesta y uso de recursos
- Solicitudes concurrentes
- Rendimiento de caché y rotación FIFO

### 4.2. Detección de movimiento
- Tiempo de detección y uso de recursos

### 4.3. Comunicación con Telegram
- Tiempo de respuesta y rate limits
- Usuarios concurrentes

## 5. Tests de Seguridad

### 5.1. Validación de inputs
- Inputs maliciosos e inyección de comandos
- Solicitudes con duraciones inválidas

### 5.2. Manejo de credenciales
- Tokens no logueados en texto plano
- Carga segura desde variables de entorno

## 6. Tests de Configuración

### 6.1. Variables de entorno
- Variables requeridas y opcionales
- Configuración de caché y backends
- Manejo de errores de configuración