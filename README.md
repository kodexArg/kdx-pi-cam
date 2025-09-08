# kdx-pi-cam

> **Repositorio**: [kodexArg/kdx-pi-cam](https://github.com/kodexArg/kdx-pi-cam)

Aplicación Python asíncrona que procesa video de una cámara RTSP bajo demanda a través de Telegram. Los usuarios envían comandos y reciben videos como respuesta, con detección automática de movimiento y notificaciones inteligentes.

## Características Principales

- 📹 **Captura de video bajo demanda** desde cámara RTSP
- 🤖 **Interfaz Telegram** con comandos `/clip5`, `/clip20`, `/photo`
- 🔍 **Detección de movimiento** automática con notificaciones
- 💾 **Sistema de caché FIFO** para gestión eficiente de archivos
- 🏗️ **Arquitectura por capas** escalable y mantenible
- ⚡ **Procesamiento asíncrono** de alta performance

## Instalación Rápida

```bash
# Clonar repositorio
git clone <repository-url>
cd kdx-pi-cam

# Instalar dependencias con uv
uv sync

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# Ejecutar aplicación
uv run python app.py
```

## Documentación

### 📋 [REQUIREMENTS.md](./REQUIREMENTS.md)
**Dependencias y configuración del sistema**
- Lista completa de librerías Python requeridas
- Variables de entorno obligatorias y opcionales
- Configuración de cámara RTSP, bot de Telegram y sistema de caché
- Parámetros de detección de movimiento y logging

### 🏛️ [AI.md](./AI.md) 
**Arquitectura y diseño del sistema**
- Arquitectura por capas detallada (Presentation, Business, Service, Infrastructure)
- Flujos de datos y comunicación entre componentes
- Patrones de diseño implementados (Strategy, Events)
- Principios de desarrollo y mejores prácticas

### 🧪 [TESTS.md](./TESTS.md)
**Plan de pruebas completo**
- Tests unitarios por cada capa y componente
- Tests de integración y end-to-end
- Tests de rendimiento y seguridad
- Estrategias de testing para aplicaciones asíncronas

## Comandos de Telegram

- `/start` - Inicializar bot
- `/clip5` - Video de 5 segundos
- `/clip20` - Video de 20 segundos  
- `/photo` - Captura de imagen actual

## Tecnologías

- **Python 3.11+** con programación asíncrona
- **python-telegram-bot** para integración con Telegram
- **OpenCV** para procesamiento de video y detección de movimiento
- **FFmpeg** para manipulación de streams RTSP
- **pytest** para testing completo

## Licencia

MIT License - Ver archivo LICENSE para detalles.