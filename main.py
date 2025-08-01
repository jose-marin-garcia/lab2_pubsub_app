# main.py

import tkinter as tk
from tkinter import simpledialog
from ui.app import PubSubApp

def ask_username():
    return simpledialog.askstring("Usuario", "Ingresa tu nombre de usuario:")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()            # ocultamos la ventana inicial
    app = PubSubApp(root, ask_username)
    if app.username:
        root.deiconify()       # mostramos la ventana de la app
        root.mainloop()
