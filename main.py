import tkinter as tk
from login import LoginWindow
from dashboard import ApplicationShell


def open_dashboard(root):
    for widget in root.winfo_children():
        widget.destroy()
    ApplicationShell(root)


if __name__ == "__main__":
    root = tk.Tk()
    root.state("zoomed")
    root.minsize(1280, 720)
    LoginWindow(root, lambda: open_dashboard(root))
    root.mainloop()