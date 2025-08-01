# migrate_logs.py
from broker.rabbit_broker import RabbitBroker
from utils.persistence   import list_topics, load_topic_messages

def main():
    broker = RabbitBroker()              # se conecta a RabbitMQ
    topics = list_topics()               # p.ej. ['Cultura','Deportes',...]
    count = 0

    for topic in topics:
        for msg in load_topic_messages(topic):
            broker.publish(topic, msg)   # republica en AMQP
            count += 1

    print(f"Migrados {count} mensajes a RabbitMQ bajo exchange '{broker.EXCHANGE}'")

if __name__ == "__main__":
    main()
