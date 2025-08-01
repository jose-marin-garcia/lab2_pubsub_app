# ui/app.py

import tkinter as tk
from tkinter import simpledialog, scrolledtext, messagebox
from broker.rabbit_broker import RabbitBroker as Broker
from utils.persistence import save_user_subscriptions, load_user_subscriptions

class PubSubApp:
    def __init__(self, root, username_callback):
        self.root = root
        self.username_callback = username_callback
        print("[UI] Inicializando broker...")
        self.broker = Broker()
        self.username = self.username_callback()
        self.subscribed_topics = {}

        if not self.username:
            self.root.destroy()
            return

        self.build_ui()
        self.restore_subscriptions()

    def build_ui(self):
        self.root.title(f"Pub/Sub Demo - Usuario: {self.username}")
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="Tópico:").grid(row=0, column=0)
        self.topic_entry = tk.Entry(self.root, width=20)
        self.topic_entry.grid(row=0, column=1)

        tk.Label(self.root, text="Mensaje:").grid(row=1, column=0)
        self.msg_entry = tk.Entry(self.root, width=40)
        self.msg_entry.grid(row=1, column=1)

        self.publish_btn = tk.Button(self.root, text="Publicar", command=self.publish)
        self.publish_btn.grid(row=2, column=1, sticky="ew")

        tk.Label(self.root, text="Filtrar (opcional):").grid(row=3, column=0)
        self.filter_entry = tk.Entry(self.root, width=20)
        self.filter_entry.grid(row=3, column=1)

        self.search_btn = tk.Button(self.root, text="Buscar tópicos", command=self.search_topics)
        self.search_btn.grid(row=4, column=1, sticky="ew")

        self.show_all_btn = tk.Button(self.root, text="Mostrar todos", command=self.refresh_topics)
        self.show_all_btn.grid(row=4, column=0, sticky="ew")

        tk.Label(self.root, text="Tópicos disponibles:").grid(row=5, column=0)
        self.topic_listbox = tk.Listbox(self.root, height=5, width=30)
        self.topic_listbox.grid(row=6, column=0)
        self.refresh_topics()

        tk.Label(self.root, text="Tópicos suscritos:").grid(row=5, column=1)
        self.subscribed_listbox = tk.Listbox(self.root, height=5, width=30)
        self.subscribed_listbox.grid(row=6, column=1)

        self.subscribe_btn = tk.Button(self.root, text="Suscribirse", command=self.subscribe)
        self.subscribe_btn.grid(row=7, column=0, sticky="ew")

        self.unsubscribe_btn = tk.Button(self.root, text="Desuscribirse", command=self.unsubscribe)
        self.unsubscribe_btn.grid(row=7, column=1, sticky="ew")

        self.output_area = scrolledtext.ScrolledText(self.root, width=65, height=15, state="disabled")
        self.output_area.grid(row=8, column=0, columnspan=2, pady=5)

        self.logout_btn = tk.Button(self.root, text="Cerrar sesión", command=self.logout)
        self.logout_btn.grid(row=9, column=1, sticky="ew")

    def publish(self):
        topic = self.topic_entry.get().strip()
        content = self.msg_entry.get().strip()
        if topic and content:
            message = f"{self.username}: {content}"
            self.broker.publish(topic, message)
            self.refresh_topics()
        else:
            messagebox.showwarning("Advertencia", "Debes ingresar un tópico y mensaje.")

    def subscribe(self):
        sel = self.topic_listbox.curselection()
        if not sel:
            messagebox.showwarning("Advertencia", "Selecciona un tópico disponible.")
            return
        topic = self.topic_listbox.get(sel)
        filt = self.filter_entry.get().strip() or None

        def callback(msg):
            self.output_area.configure(state="normal")
            self.output_area.insert(tk.END, f"[{topic}] {msg}\n")
            self.output_area.configure(state="disabled")

        print(f"[UI] Suscribiendo a {topic} (filtro={filt})")
        self.broker.subscribe(topic, callback, filt)
        self.subscribed_topics[topic] = callback
        self.refresh_subscribed_list()
        self.save_subscriptions()

    def unsubscribe(self):
        sel = self.subscribed_listbox.curselection()
        if not sel:
            messagebox.showwarning("Advertencia", "Selecciona un tópico suscrito.")
            return
        topic = self.subscribed_listbox.get(sel)
        callback = self.subscribed_topics.pop(topic, None)
        if callback:
            self.broker.unsubscribe(topic, callback)
            self.refresh_subscribed_list()
            self.output_area.configure(state="normal")
            self.output_area.insert(tk.END, f"[INFO] Te has desuscrito de '{topic}'\n")
            self.output_area.configure(state="disabled")
            self.save_subscriptions()

    def refresh_topics(self):
        self.topic_listbox.delete(0, tk.END)
        for t in self.broker.get_topics():
            self.topic_listbox.insert(tk.END, t)

    def refresh_subscribed_list(self):
        self.subscribed_listbox.delete(0, tk.END)
        for t in self.subscribed_topics:
            self.subscribed_listbox.insert(tk.END, t)

    def save_subscriptions(self):
        save_user_subscriptions(self.username, list(self.subscribed_topics.keys()))

    def restore_subscriptions(self):
        for topic in load_user_subscriptions(self.username):
            if topic in self.broker.get_topics():
                def gen_cb(t=topic):
                    def cb(msg):
                        self.output_area.configure(state="normal")
                        self.output_area.insert(tk.END, f"[{t}] {msg}\n")
                        self.output_area.configure(state="disabled")
                    return cb
                cb = gen_cb()
                print(f"[UI] Restaurando suscripción a {topic}")
                self.broker.subscribe(topic, cb)
                self.subscribed_topics[topic] = cb
        self.refresh_subscribed_list()

    def logout(self):
        self.save_subscriptions()
        self.username = self.username_callback()
        if self.username:
            self.subscribed_topics.clear()
            self.build_ui()
            self.restore_subscriptions()
        else:
            self.root.destroy()

    def search_topics(self):
        kw = self.filter_entry.get().strip()
        if not kw:
            messagebox.showwarning("Advertencia", "Ingresa una palabra clave para buscar.")
            return
        print(f"[UI] Buscando topics con '{kw}'")
        found = self.broker.search_topics_by_keyword(kw)
        self.topic_listbox.delete(0, tk.END)
        for t in found:
            self.topic_listbox.insert(tk.END, t)
