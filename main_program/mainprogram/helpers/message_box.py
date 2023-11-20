import tkinter as tk
from tkinter import messagebox

def show_popup_message(message):
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("Missing", message)