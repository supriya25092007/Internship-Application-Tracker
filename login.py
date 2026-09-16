import tkinter as tk
from tkinter import messagebox

from database import db


class LoginWindow:
    COLORS = {
        "black": "#050508", "hero": "#0B0B18", "surface": "#11131C",
        "field": "#0B0D13", "red": "#FF0033", "red_button": "#EF4444",
        "red_hover": "#FF1748", "white": "#F8FAFC", "muted": "#9CA3AF",
        "line": "#303442",
    }

    def __init__(self, root, on_success):
        self.root = root
        self.on_success = on_success
        self.mode = "signin"
        self.password_visible = False
        self.remember_me = tk.BooleanVar(value=False)
        self.fields = {}
        self.build()

    def build(self):
        self.root.title("Internship Tracker | Sign in")
        self.root.configure(bg=self.COLORS["black"])
        self.root.geometry("1120x700")
        self.root.minsize(900, 620)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.build_hero()
        self.build_form()
        self.root.bind("<Return>", lambda _event: self.submit())

    def build_hero(self):
        hero = tk.Frame(self.root, bg=self.COLORS["hero"])
        hero.grid(row=0, column=0, sticky="nsew")
        hero.grid_rowconfigure(0, weight=1)
        hero.grid_columnconfigure(0, weight=1)
        canvas = tk.Canvas(hero, bg=self.COLORS["hero"], highlightthickness=0, bd=0)
        canvas.grid(row=0, column=0, sticky="nsew")
        canvas.bind("<Configure>", self.paint_hero)
        self.hero_canvas = canvas
        content = tk.Frame(canvas, bg=self.COLORS["hero"])
        canvas.create_window((58, 0), window=content, anchor="nw")
        content.bind("<Configure>", lambda _event: canvas.configure(scrollregion=canvas.bbox("all")))
        tk.Label(content, text="IAT", bg=self.COLORS["hero"], fg=self.COLORS["red"], font=("Segoe UI", 18, "bold")).pack(anchor="w", pady=(42, 0))
        tk.Label(content, text="INTERNSHIP APPLICATION TRACKER", bg=self.COLORS["hero"], fg="#FCA5B5", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(2, 0))
        tk.Label(content, text="Welcome\nBack", bg=self.COLORS["hero"], fg=self.COLORS["white"], justify="left", font=("Segoe UI", 40, "bold")).pack(anchor="w", pady=(108, 0))
        tk.Label(content, text="Manage and track your academic internship\njourney seamlessly.", bg=self.COLORS["hero"], fg="#D1D5DB", justify="left", font=("Segoe UI", 12)).pack(anchor="w", pady=(18, 0))
        badges = tk.Frame(content, bg=self.COLORS["hero"], highlightbackground="#7F1D35", highlightthickness=1, padx=17, pady=10)
        badges.pack(anchor="w", pady=(34, 0))
        tk.Label(badges, text="🌐   💼   ✉️   🎓", bg=self.COLORS["hero"], fg=self.COLORS["white"], font=("Segoe UI Emoji", 17)).pack()
        tk.Label(content, text="One focused place for the whole journey.", bg=self.COLORS["hero"], fg="#FB7185", font=("Segoe UI", 10, "italic")).pack(anchor="w", pady=(30, 0))

    def paint_hero(self, event):
        self.hero_canvas.delete("bg")
        colors = ("#0B0B18", "#11102A", "#17133A", "#21164A")
        band = max(event.height // len(colors), 1)
        for index, color in enumerate(colors):
            self.hero_canvas.create_rectangle(0, index * band, event.width, (index + 1) * band + 2, fill=color, outline=color, tags="bg")
        self.hero_canvas.tag_lower("bg")

    def build_form(self):
        self.form_panel = tk.Frame(self.root, bg=self.COLORS["surface"], padx=70)
        self.form_panel.grid(row=0, column=1, sticky="nsew")
        self.form_panel.grid_columnconfigure(0, weight=1)
        self.form_panel.grid_rowconfigure(0, weight=1)
        self.form = tk.Frame(self.form_panel, bg=self.COLORS["surface"])
        self.form.grid(row=0, column=0, sticky="ew")
        self.form.grid_columnconfigure(0, weight=1)
        self.render_form()

    def render_form(self):
        for child in self.form.winfo_children():
            child.destroy()
        self.fields = {}
        tk.Label(self.form, text="Sign in" if self.mode == "signin" else "Create account", bg=self.COLORS["surface"], fg=self.COLORS["white"], font=("Segoe UI", 29, "bold")).grid(row=0, column=0, sticky="w")
        tk.Label(self.form, text="Access your internship command center" if self.mode == "signin" else "Start organizing your internship journey", bg=self.COLORS["surface"], fg=self.COLORS["muted"], font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", pady=(7, 22))
        toggle = tk.Frame(self.form, bg=self.COLORS["field"], highlightbackground=self.COLORS["line"], highlightthickness=1)
        toggle.grid(row=2, column=0, sticky="ew", pady=(0, 22))
        toggle.grid_columnconfigure(0, weight=1); toggle.grid_columnconfigure(1, weight=1)
        self.toggle_button(toggle, "SIGN IN", "signin", 0)
        self.toggle_button(toggle, "SIGN UP", "signup", 1)
        row = 3
        if self.mode == "signup":
            self.make_field(row, "Name", "name"); row += 2
            self.make_field(row, "Email Address", "email"); row += 2
        self.make_field(row, "Email Address / Username" if self.mode == "signin" else "Username", "username"); row += 2
        self.make_field(row, "Password", "password", secret=True); row += 2
        if self.mode == "signup":
            self.make_field(row, "Confirm Password", "confirm_password", secret=True); row += 2
        if self.mode == "signin":
            options = tk.Frame(self.form, bg=self.COLORS["surface"])
            options.grid(row=row, column=0, sticky="ew", pady=(7, 0))
            tk.Checkbutton(options, text="Remember me", variable=self.remember_me, bg=self.COLORS["surface"], fg="#D1D5DB", selectcolor=self.COLORS["surface"], activebackground=self.COLORS["surface"], activeforeground=self.COLORS["white"], highlightthickness=0, font=("Segoe UI", 9)).pack(side="left")
            lost = tk.Label(options, text="Lost your password?", bg=self.COLORS["surface"], fg="#FB7185", cursor="hand2", font=("Segoe UI", 9, "underline"))
            lost.pack(side="right")
            lost.bind("<Button-1>", lambda _event: messagebox.showinfo("Password help", "Please contact your internship tracker administrator."))
            row += 1
        self.cta = tk.Button(self.form, text="Sign in now  →" if self.mode == "signin" else "Create account  →", command=self.submit, bg=self.COLORS["red_button"], fg="white", activebackground=self.COLORS["red_hover"], activeforeground="white", relief="flat", cursor="hand2", font=("Segoe UI", 11, "bold"), pady=12)
        self.cta.grid(row=row, column=0, sticky="ew", pady=(22, 0))
        self.cta.bind("<Enter>", lambda _event: self.cta.configure(bg=self.COLORS["red_hover"]))
        self.cta.bind("<Leave>", lambda _event: self.cta.configure(bg=self.COLORS["red_button"]))
        tk.Button(self.form, text="Clear form", command=self.clear, bg=self.COLORS["surface"], fg=self.COLORS["muted"], activebackground=self.COLORS["surface"], activeforeground=self.COLORS["white"], relief="flat", cursor="hand2", font=("Segoe UI", 9)).grid(row=row + 1, column=0, pady=(11, 0))
        tk.Label(self.form, text="By clicking 'Sign in now' you agree to Terms of Service | Privacy Policy", bg=self.COLORS["surface"], fg="#6B7280", wraplength=390, justify="center", font=("Segoe UI", 8)).grid(row=row + 2, column=0, pady=(26, 0))
        if self.fields:
            self.fields["username"].focus_set()

    def toggle_button(self, parent, text, mode, column):
        active = mode == self.mode
        button = tk.Button(parent, text=text, command=lambda: self.switch_mode(mode), bg=self.COLORS["red"] if active else self.COLORS["field"], fg="white" if active else self.COLORS["muted"], activebackground=self.COLORS["red_hover"], relief="flat", bd=0, cursor="hand2", font=("Segoe UI", 9, "bold"), pady=7)
        button.grid(row=0, column=column, sticky="ew", padx=2, pady=2)

    def make_field(self, row, label, name, secret=False):
        tk.Label(self.form, text=label, bg=self.COLORS["surface"], fg="#D1D5DB", font=("Segoe UI", 9, "bold")).grid(row=row, column=0, sticky="w", pady=(0, 6))
        frame = tk.Frame(self.form, bg=self.COLORS["field"], highlightbackground=self.COLORS["line"], highlightthickness=1)
        frame.grid(row=row + 1, column=0, sticky="ew")
        frame.grid_columnconfigure(0, weight=1)
        entry = tk.Entry(frame, show="•" if secret else "", bg=self.COLORS["field"], fg=self.COLORS["white"], insertbackground=self.COLORS["white"], relief="flat", font=("Segoe UI", 11))
        entry.grid(row=0, column=0, sticky="ew", ipady=10, padx=12)
        self.fields[name] = entry
        entry.bind("<FocusIn>", lambda _event: frame.configure(highlightbackground=self.COLORS["red"], highlightthickness=2))
        entry.bind("<FocusOut>", lambda _event: frame.configure(highlightbackground=self.COLORS["line"], highlightthickness=1))
        if secret:
            tk.Button(frame, text="◉", command=lambda: self.toggle_field(entry), bg=self.COLORS["field"], fg=self.COLORS["muted"], activebackground=self.COLORS["field"], relief="flat", cursor="hand2").grid(row=0, column=1, padx=5)

    def toggle_field(self, entry):
        entry.configure(show="" if entry.cget("show") else "•")

    def switch_mode(self, mode):
        self.mode = mode
        self.render_form()

    def clear(self):
        for entry in self.fields.values():
            entry.delete(0, tk.END)
        self.remember_me.set(False)
        if "username" in self.fields:
            self.fields["username"].focus_set()

    def submit(self):
        if self.mode == "signup":
            self.register()
        else:
            self.login()

    def login(self):
        username = self.fields["username"].get().strip()
        password = self.fields["password"].get()
        if not username or not password:
            messagebox.showerror("Missing details", "Enter a username and password.")
            return
        try:
            row = db.fetch_one("SELECT username FROM users WHERE username = %s AND password = %s", (username, password))
        except RuntimeError as error:
            messagebox.showerror("Sign in unavailable", "Create an account first, or check the users table.\n\n" + str(error))
            return
        if not row:
            messagebox.showerror("Sign in failed", "The username or password is incorrect.")
            return
        self.on_success()

    def register(self):
        values = {name: field.get().strip() for name, field in self.fields.items()}
        if not all(values.values()):
            messagebox.showerror("Missing details", "Complete all sign-up fields.")
            return
        if values["password"] != values["confirm_password"]:
            messagebox.showerror("Password mismatch", "Password and confirmation must match.")
            return
        try:
            db.execute("CREATE TABLE IF NOT EXISTS users (user_id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100) NOT NULL, email VARCHAR(150) NOT NULL UNIQUE, username VARCHAR(50) NOT NULL UNIQUE, password VARCHAR(255) NOT NULL)")
            db.execute("INSERT INTO users (name, email, username, password) VALUES (%s, %s, %s, %s)", (values["name"], values["email"], values["username"], values["password"]))
        except RuntimeError as error:
            messagebox.showerror("Registration failed", str(error))
            return
        messagebox.showinfo("Account created", "Your account was created. You can now sign in.")
        self.mode = "signin"
        self.render_form()
        self.fields["username"].insert(0, values["username"])

