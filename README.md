# Pub/Sub App en Python (Versión Actualizada)

Aplicación completa de publicación/suscripción (Pub/Sub) con interfaz gráfica en Tkinter que permite múltiples usuarios gestionar tópicos y mensajes de forma persistente.

## 🚀 Características Principales

### 📝 Gestión de Tópicos
- **Crear nuevos tópicos**: Los usuarios pueden crear tópicos dinámicamente al publicar mensajes
- **Lista de tópicos disponibles**: Visualización en tiempo real de todos los tópicos existentes
- **Búsqueda de tópicos**: Filtrar tópicos por palabras clave en el contenido de los mensajes
- **Botón "Mostrar todos"**: Limpiar filtros de búsqueda y mostrar todos los tópicos

### 🔔 Sistema de Suscripciones
- **Suscripción a tópicos**: Los usuarios pueden suscribirse a múltiples tópicos
- **Panel de tópicos suscritos**: Lista dedicada que muestra solo los tópicos a los que está suscrito el usuario
- **Desuscripción**: Opción para desuscribirse de tópicos específicos
- **Filtros por palabra clave**: Recibir solo mensajes que contengan palabras específicas
- **Notificaciones en tiempo real**: Los mensajes aparecen automáticamente cuando son publicados

### 💬 Publicación de Mensajes
- **Mensajes con autoría**: Todos los mensajes incluyen automáticamente el nombre del usuario
- **Publicación instantánea**: Los mensajes se distribuyen inmediatamente a todos los suscriptores
- **Validación de entrada**: Verificación de que se ingrese tanto tópico como mensaje

### 👥 Gestión de Usuarios
- **Sistema de usuarios**: Cada usuario tiene su propia sesión personalizada
- **Persistencia de suscripciones**: Las suscripciones se guardan automáticamente por usuario
- **Restauración automática**: Al iniciar sesión, se restauran las suscripciones previas
- **Cambio de usuario**: Función de cerrar sesión para cambiar entre usuarios sin reiniciar la aplicación

### 💾 Persistencia Completa
- **Mensajes permanentes**: Todos los mensajes se guardan en archivos de texto
- **Historial por tópico**: Cada tópico mantiene su historial completo de mensajes
- **Suscripciones por usuario**: Cada usuario tiene un archivo dedicado para sus suscripciones
- **Carga automática**: Al suscribirse a un tópico, se cargan todos los mensajes históricos

## ⚡ Instalación y Uso

### Requisitos
- Python 3.6 o superior
- Tkinter (incluido en la mayoría de instalaciones de Python)

### Ejecución
```bash
python main.py
```

Al ejecutar la aplicación:
1. Se abrirá un diálogo para ingresar tu nombre de usuario
2. La interfaz principal se cargará con tus suscripciones previas (si existen)
3. Podrás comenzar a publicar mensajes y gestionar suscripciones inmediatamente

## 🗃 Estructura de Persistencia

### Mensajes
- **Ubicación**: `logs/{topico}.txt`
- **Formato**: `{usuario}: {mensaje}`
- **Codificación**: UTF-8 para soporte completo de caracteres especiales

### Suscripciones
- **Ubicación**: `subscriptions/{usuario}.txt`
- **Formato**: Un tópico por línea
- **Restauración**: Automática al iniciar sesión

## 🏗 Arquitectura del Sistema

### Componentes Principales

1. **Broker (`broker/broker.py`)**
   - Núcleo del sistema pub/sub
   - Gestiona suscripciones y publicaciones
   - Maneja filtros por palabra clave
   - Búsqueda en contenido de mensajes

2. **Interfaz de Usuario (`ui/app.py`)**
   - Interfaz gráfica con Tkinter
   - Gestión de sesiones de usuario
   - Área de visualización de mensajes en tiempo real
   - Controles para suscripción/desuscripción

3. **Persistencia (`utils/persistence.py`)**
   - Funciones de guardado y carga de datos
   - Gestión de archivos de mensajes y suscripciones
   - Soporte para caracteres UTF-8

4. **Punto de Entrada (`main.py`)**
   - Inicialización de la aplicación
   - Diálogo de autenticación de usuario

## 📋 Funcionalidades Detalladas

### Búsqueda Inteligente
- Busca palabras clave en el **contenido** de los mensajes, no solo en nombres de tópicos
- Búsqueda insensible a mayúsculas/minúsculas
- Resultados en tiempo real

### Filtros de Suscripción
- Posibilidad de filtrar mensajes por palabras clave al suscribirse
- Solo recibir notificaciones de mensajes que contengan términos específicos
- Útil para tópicos con mucho tráfico

### Gestión de Estado
- Restauración automática del estado de la aplicación
- Sincronización entre la lista de tópicos disponibles y suscritos
- Manejo de errores y validaciones de entrada

## 💡 Ejemplos de Uso

### Caso 1: Usuario Nuevo
1. Al ejecutar la aplicación, ingresa tu nombre (ej: "María")
2. Se creará automáticamente un archivo `subscriptions/María.txt`
3. Puedes empezar a crear tópicos y suscribirte inmediatamente

### Caso 2: Usuario Existente
1. Si ya tienes suscripciones guardadas, se restaurarán automáticamente
2. Verás todos tus tópicos suscritos en el panel derecho
3. Recibirás el historial completo de mensajes de cada tópico

### Caso 3: Búsqueda y Filtrado
1. Escribe una palabra clave en el campo "Filtrar"
2. Haz clic en "Buscar tópicos" para ver solo tópicos con mensajes que contengan esa palabra
3. Usa "Mostrar todos" para volver a la vista completa

## 🔧 Estructura de Directorios

```
lab2_pubsub_app/
├── main.py                    # Punto de entrada
├── requirements.txt           # Dependencias
├── README.md                 # Documentación
├── broker/                   # Lógica del sistema pub/sub
│   ├── __init__.py
│   └── broker.py
├── ui/                       # Interfaz gráfica
│   ├── __init__.py
│   └── app.py
├── utils/                    # Utilidades de persistencia
│   ├── __init__.py
│   └── persistence.py
├── logs/                     # Mensajes por tópico
│   ├── Cultura.txt
│   ├── Deportes.txt
│   ├── Noticias.txt
│   └── Tecnología.txt
└── subscriptions/            # Suscripciones por usuario
    ├── Bastián.txt
    ├── José M.txt
    ├── Macarena.txt
    └── [otros usuarios...]
```

## 🚀 Características Técnicas

- **Arquitectura modular**: Separación clara de responsabilidades
- **Patrones de diseño**: Implementación del patrón Observer para pub/sub
- **Manejo de errores**: Validaciones y mensajes informativos
- **Codificación**: Soporte completo UTF-8 para caracteres especiales
- **Interfaz responsive**: Diseño adaptativo con Tkinter
- **Estado persistente**: Sin pérdida de datos entre sesiones

---

**Desarrollado como sistema de demostración del patrón Pub/Sub con persistencia y múltiples usuarios.**
