from utils.persistence import save_message, list_topics, load_topic_messages

class Broker:
    def __init__(self):
        self.subscribers = {}
        self.messages = {}

        topics = list_topics()
        for topic in topics:
            self.messages[topic] = load_topic_messages(topic)

    def subscribe(self, topic, callback, filter_keyword=None):
        self.subscribers.setdefault(topic, []).append((callback, filter_keyword))
        for msg in self.messages.get(topic, []):
            if filter_keyword is None or filter_keyword in msg:
                callback(msg)

    def unsubscribe(self, topic, callback):
        if topic in self.subscribers:
            self.subscribers[topic] = [cb for cb in self.subscribers[topic] if cb[0] != callback]

    def publish(self, topic, message):
        self.messages.setdefault(topic, []).append(message)
        save_message(topic, message)
        for callback, filter_keyword in self.subscribers.get(topic, []):
            if filter_keyword is None or filter_keyword in message:
                callback(message)

    def get_topics(self):
        return list(self.messages.keys())

    def search_topics_by_keyword(self, keyword):
        result = []
        for topic, msgs in self.messages.items():
            for msg in msgs:
                if keyword.lower() in msg.lower():
                    result.append(topic)
                    break
        return result
