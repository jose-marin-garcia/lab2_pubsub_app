# broker/rabbit_broker.py

import pika
import threading
from utils.persistence import list_topics, load_topic_messages, save_message

class RabbitBroker:
    EXCHANGE      = 'pubsub_exchange'
    EXCHANGE_TYPE = 'topic'

    def __init__(self, amqp_url: str = 'amqp://guest:guest@127.0.0.1:5672/%2F'):
        self.amqp_url = amqp_url
        # Inicializa la conexión y canal de publicación
        self._setup_pub_channel()

        # Topics históricos desde disco
        self.topics = list_topics()

        # Subscripciones activas: topic -> [entries]
        # cada entry: dict(callback, connection, channel, consumer_tag, queue_name)
        self._subs = {}

    def _setup_pub_channel(self):
        """
        Establece o restablece la conexión y el canal para publicar.
        """
        params         = pika.URLParameters(self.amqp_url)
        self.pub_conn  = pika.BlockingConnection(params)
        self.pub_chan  = self.pub_conn.channel()
        self.pub_chan.exchange_declare(
            exchange=self.EXCHANGE,
            exchange_type=self.EXCHANGE_TYPE,
            durable=True
        )

    def publish(self, topic: str, message: str):
        """
        Persiste localmente, actualiza topics y publica con reconexión automática.
        """
        # 1) Persistencia en disco
        save_message(topic, message)
        if topic not in self.topics:
            self.topics.append(topic)

        # 2) Publicar, intentando reconectar si el canal está cerrado
        try:
            self.pub_chan.basic_publish(
                exchange=self.EXCHANGE,
                routing_key=topic,
                body=message
            )
        except (pika.exceptions.StreamLostError, pika.exceptions.ChannelWrongStateError) as e:
            print(f"[RabbitBroker] Advertencia: canal cerrado, reconectando... {e}")
            try:
                self._setup_pub_channel()
                self.pub_chan.basic_publish(
                    exchange=self.EXCHANGE,
                    routing_key=topic,
                    body=message
                )
            except Exception as err:
                print(f"[RabbitBroker] Error tras reconectar: {err}")

    def subscribe(self, topic: str, callback, filter_keyword: str = None):
        """
        Reenvía historial y arranca un consumidor en su propio hilo.
        """
        # 1) Reenvío de mensajes anteriores
        for msg in load_topic_messages(topic):
            if not filter_keyword or filter_keyword in msg:
                callback(msg)

        # 2) Consumidor en hilo
        # Parte 2.1: Abre una nueva conexión y canal AMQP para este consumidor
        def _worker():
            try:
                params = pika.URLParameters(self.amqp_url)
                conn   = pika.BlockingConnection(params)
                ch     = conn.channel()
                ch.exchange_declare(
                    exchange=self.EXCHANGE,
                    exchange_type=self.EXCHANGE_TYPE,
                    durable=True
                )

                # Parte 2.2: Crea una cola temporal con nombre aleatorio y mete ahí todos los mensajes del topic
                q = ch.queue_declare('', exclusive=True).method.queue
                ch.queue_bind(
                    exchange=self.EXCHANGE,
                    queue=q,
                    routing_key=topic
                )

                # Parte 2.3: Define como manejar cada mensaje, convirtiéndolo en texto
                def on_message(ch, method, props, body):
                    texto = body.decode('utf-8')
                    if not filter_keyword or filter_keyword in texto:
                        callback(texto)

                # Parte 2.4: Inicia el consumidor y guarda el consumer_tag para poder cancelarlo
                consumer_tag = ch.basic_consume(
                    queue=q,
                    on_message_callback=on_message,
                    auto_ack=True
                )

                # Parte 2.5: Registra esta suscripción para permitir su cancelación más adelante
                self._subs.setdefault(topic, []).append({
                    'callback': callback,
                    'connection': conn,
                    'channel': ch,
                    'consumer_tag': consumer_tag,
                    'queue_name': q
                })

                # Parte 2.6: Empieza a escuchar mensajes en este hilo sin bloquear la UI
                ch.start_consuming()
            except Exception as e:
                # Atrapar errores de consumo sin matar la app
                print(f"[RabbitBroker] Error en consumidor para topic '{topic}': {e}")

        # Lanza el hilo en segundo plano (daemon) para no bloquear la aplicación principal
        hilo = threading.Thread(target=_worker, daemon=True)
        hilo.start()


    def unsubscribe(self, topic: str, callback):
        """
        Cancela el consumo de forma segura y cierra recursos.
        """
        subs = self._subs.get(topic, [])
        for entry in subs[:]:
            if entry['callback'] == callback:
                conn  = entry['connection']
                ch    = entry['channel']
                tag   = entry['consumer_tag']

                # 1) parar el consuming desde el hilo de Pika
                def _stop():
                    try:
                        ch.stop_consuming()
                    except Exception:
                        pass
                conn.add_callback_threadsafe(_stop)

                # 2) cancelar el consumer
                try:
                    ch.basic_cancel(consumer_tag=tag)
                except Exception:
                    pass

                # 3) cerrar canal y conexión
                try:
                    ch.close()
                except Exception:
                    pass
                try:
                    conn.close()
                except Exception:
                    pass

                subs.remove(entry)
                break
        if not subs and topic in self._subs:
            self._subs.pop(topic)

    def get_topics(self) -> list:
        return self.topics.copy()

    def search_topics_by_keyword(self, keyword: str) -> list:
        found = []
        for topic in self.topics:
            for msg in load_topic_messages(topic):
                if keyword.lower() in msg.lower():
                    found.append(topic)
                    break
        return found


    def unsubscribe(self, topic: str, callback):
        """
        Cancela el consumo de forma segura y cierra recursos.
        """
        # 1) Encontrar la suscripción activa que coincide con este callback
        subs = self._subs.get(topic, [])
        for entry in subs[:]:
            if entry['callback'] == callback:
                conn  = entry['connection']  # Conexión del consumidor
                ch    = entry['channel']     # Canal AMQP usado
                tag   = entry['consumer_tag']# Etiqueta que identifica al consumidor

                # 2) Pedir al hilo de RabbitMQ que deje de consumir
                def _stop():
                    try:
                        ch.stop_consuming()  # Para el bucle de consumo
                    except Exception:
                        pass
                conn.add_callback_threadsafe(_stop)

                # 3) Desregistrar y cerrar el consumidor en el canal
                try:
                    ch.basic_cancel(consumer_tag=tag)  # Cancela el consumer
                except Exception:
                    pass

                # 4) Cerrar canal y conexión para liberar memoria
                try:
                    ch.close()    # Cierra el canal
                except Exception:
                    pass
                try:
                    conn.close()  # Cierra la conexión
                except Exception:
                    pass

                # 5) Eliminar la entrada de la lista de suscripciones
                subs.remove(entry)
                break

        # 6) Si no quedan suscriptores para este tópico, limpiar registro
        if not subs and topic in self._subs:
            self._subs.pop(topic)


    def get_topics(self) -> list:
        return self.topics.copy()

    def search_topics_by_keyword(self, keyword: str) -> list:
        found = []
        for topic in self.topics:
            for msg in load_topic_messages(topic):
                if keyword.lower() in msg.lower():
                    found.append(topic)
                    break
        return found