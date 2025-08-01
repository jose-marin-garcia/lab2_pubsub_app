# Lab2 Pub/Sub App con RabbitMQ y Tkinter

Aplicación de publicación/suscripción en Python que utiliza RabbitMQ como broker y Tkinter para la interfaz gráfica. Incluye persistencia local de mensajes y suscripciones, y es multiusuario.

---

## 🚀 Características Principales

- **Pub/Sub con RabbitMQ**: Exchange tipo `topic`, binding por tópico, colas efímeras.
- **Persistencia local**: Copia de seguridad de mensajes en `logs/` y de suscripciones en `subscriptions/`.
- **Interfaz gráfica**: Gestión de usuarios, tópicos y mensajes en tiempo real.
- **Filtro por palabra clave**: Filtrar mensajes históricos y nuevos.
- **Multiusuario**: Cada sesión con usuario propio y restauración de suscripciones.

---

## 📦 Estructura de Directorios

```
lab2_pubsub_app/
├── broker/
│   ├── __init__.py
│   └── rabbit_broker.py    # Lógica de conexión y consumo/producción AMQP
├── ui/
│   ├── __init__.py
│   └── app.py              # Interfaz Tkinter
├── utils/
│   ├── __init__.py
│   └── persistence.py      # Guardado y carga de logs y suscripciones
├── logs/                   # Historial de mensajes (auto-generado)
├── subscriptions/          # Suscripciones por usuario (auto-generado)
├── migrate_logs.py         # Script para migrar logs existentes a RabbitMQ
├── main.py                 # Punto de entrada: inicia UI y pide usuario
└── README.md               # Documentación (Esto)
```

> **Tip:** No agregues `logs/` ni `subscriptions/` al control de versiones.

---

## 🛠️ Requisitos

- Python 3.6+
- RabbitMQ (local o en Docker)
- Tkinter (viene con Python)
- Pika (cliente AMQP): instalar con `pip install pika`

---

## ⚡ Puesta en Marcha

1. **Iniciar RabbitMQ**

   - Si usas Docker:
     ```bash
     docker start rabbit    # asume contenedor "rabbit" creado previamente
     ```
   - Si usas instalación local: asegúrate de que el servicio `RabbitMQ` esté **en ejecución**.
2. **Configurar credenciales**

   - Usuario: `guest`
   - Contraseña: `guest`
   - AMQP URL por defecto: `amqp://guest:guest@localhost:5672/%2F`
3. **Migrar historial a RabbitMQ (opcional)**
   Si ya tienes archivos en `logs/*.txt` y quieres enviarlos al exchange:

   ```bash
   python migrate_logs.py
   ```
4. **Ejecutar la aplicación**

   ```bash
   python main.py
   ```

   - Ingresa tu nombre de usuario cuando lo solicite.
   - Se restaurarán tus suscripciones previas.
5. **Abrir consola de gestión**

   - URL: http://localhost:15672
   - Usuario/Clave: `guest`/`guest`

---

## 🔄 Flujo de Trabajo

1. **Crear o seleccionar tópico**: Escribe un nombre en "Tópico nuevo".
2. **Publicar mensaje**: Ingresa texto y haz clic en "Publicar".
3. **Suscribirse**: Selecciona un tópico y haz clic en "Suscribirse".
4. **Ver mensajes**: Llegarán históricos y nuevos automáticamente.
5. **Desuscribirse**: Quita la suscripción para dejar de recibir.

---

## 🎯 Puntos Clave Técnicos

- **Exchange** `pubsub_exchange` (tipo `topic`, durable).
- **Colas efímeras**: Se crean con nombre aleatorio y `exclusive=True` para consumir.
- **auto_ack=True**: El mensaje se confirma y borra al entregarlo.
- **Hilos daemon**: Cada suscripción corre en su propio hilo para no bloquear la UI.
- **Persistencia**: `utils/persistence.py` mantiene respaldo en `logs/` y `subscriptions/`.

---

## 📖 Uso Avanzado

- **Filtrar por palabra**: Ingresa un término en "Filtrar" antes de suscribirte.
- **Buscar tópicos**: Encuentra rápidamente tópicos con mensajes que contengan un término.
- **Migrar logs**: Usa `migrate_logs.py` para poner logs antiguos en RabbitMQ y luego consumidos por la app.

---

¡Listo! Con esto tienes un sistema Pub/Sub robusto con RabbitMQ, historial persistente y una UI amigable para múltiples usuarios.
