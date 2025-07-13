import os

def save_message(topic, message):
    os.makedirs("logs", exist_ok=True)
    file_path = os.path.join("logs", f"{topic}.txt")
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(message + "\n")

def list_topics():
    if not os.path.exists("logs"):
        return []
    return [f.replace(".txt", "") for f in os.listdir("logs") if f.endswith(".txt")]

def load_topic_messages(topic):
    file_path = os.path.join("logs", f"{topic}.txt")
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines()]

def save_user_subscriptions(username, topics):
    os.makedirs("subscriptions", exist_ok=True)
    file_path = os.path.join("subscriptions", f"{username}.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        for topic in topics:
            f.write(topic + "\n")

def load_user_subscriptions(username):
    file_path = os.path.join("subscriptions", f"{username}.txt")
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines()]
