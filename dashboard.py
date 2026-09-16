import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime

from database import db


COLORS = {
    "background": "#0C0D12", "sidebar": "#12131A", "active": "#1F222E",
    "surface": "#1A1D26", "field": "#0F1117", "border": "#2A2E3D",
    "blue": "#3B82F6", "green": "#10B981", "purple": "#8B5CF6",
    "amber": "#F59E0B", "cyan": "#06B6D4", "rose": "#EF4444",
    "white": "#F8FAFC", "muted": "#94A3B8",
}


def valid_date(value):
    if not value:
        return True
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return True
    except ValueError:
        return False


class CrudView:
    def __init__(self, parent, title, table, primary_key, fields, choices=None, search_fields=None, db_connection=None):
        self.parent = parent
        self.parent.grid_columnconfigure(1, weight=1)
        self.parent.grid_rowconfigure(2, weight=1)
        self.title = title
        self.table = table
        self.primary_key = primary_key
        self.fields = fields
        self.choices = choices or {}
        self.search_fields = search_fields or [field[0] for field in fields]
        self.db_connection = db_connection or db
        self.entries = {}
        self.build()
        self.load_data()

    def build(self):
        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_rowconfigure(0, weight=1)
        heading = tk.Frame(self.parent, bg=COLORS["background"])
        heading.grid(row=0, column=0, sticky="ew", padx=28, pady=(25, 16))
        heading.grid_columnconfigure(0, weight=1)
        tk.Label(heading, text=self.title, bg=COLORS["background"], fg=COLORS["white"], font=("Segoe UI", 23, "bold")).grid(row=0, column=0, sticky="w")
        self.search = tk.Entry(heading, width=28, bg=COLORS["field"], fg=COLORS["white"], insertbackground=COLORS["white"], relief="flat", font=("Segoe UI", 10))
        self.search.grid(row=0, column=2, sticky="ew", padx=(8, 0), ipady=8)
        self.button(heading, "⌕  Search", self.load_data, COLORS["blue"]).grid(row=0, column=1, sticky="e", ipady=5)

        form = tk.LabelFrame(self.parent, text="  Record details  ", bg=COLORS["surface"], fg=COLORS["blue"], highlightbackground=COLORS["border"], highlightthickness=1, bd=0, font=("Segoe UI", 10, "bold"), padx=15, pady=10)
        form.grid(row=1, column=0, sticky="ew", padx=28, pady=(0, 12))
        for index, (name, label) in enumerate(self.fields):
            row, column = divmod(index, 3)
            form.grid_columnconfigure(column, weight=1)
            label_row = row * 2
            entry_row = label_row + 1
            tk.Label(form, text=label, bg=COLORS["surface"], fg=COLORS["muted"], font=("Segoe UI", 10, "bold")).grid(row=label_row, column=column, sticky="ew", padx=5, pady=5)
            choices = self.choices.get(name, self.parent_choices(name))
            if choices is not None:
                widget = ttk.Combobox(form, values=choices, state="readonly", style="Dark.TCombobox", font=("Segoe UI", 10), width=25)
            else:
                widget = tk.Entry(form, bg=COLORS["field"], fg=COLORS["white"], insertbackground=COLORS["white"], relief="flat", font=("Segoe UI", 10), width=25)
            widget.grid(row=entry_row, column=column, sticky="ew", padx=5, pady=5, ipady=7)
            self.entries[name] = widget

        buttons = tk.Frame(form, bg=COLORS["surface"])
        button_row = ((len(self.fields) + 2) // 3) * 2
        buttons.grid(row=button_row, column=0, columnspan=3, sticky="w", padx=5, pady=5)
        for text, command, color in (("＋  Add", self.add, COLORS["blue"]), ("✎  Update", self.update, COLORS["green"]), ("⌫  Delete", self.delete, COLORS["rose"]), ("↺  Clear", self.clear, COLORS["muted"])):
            self.button(buttons, text, command, color).pack(side="left", padx=(0, 8))

        table_frame = tk.Frame(self.parent, bg=COLORS["background"])
        table_frame.grid(row=2, column=0, sticky="nsew", padx=28, pady=(0, 24))
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        columns = [self.primary_key] + [field[0] for field in self.fields]
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", style="Dark.Treeview")
        for column in columns:
            self.tree.heading(column, text=column.replace("_", " ").title())
            width = self.column_width(column)
            self.tree.column(column, width=width, minwidth=max(100, width - 40), anchor="w", stretch=False)
        self.tree.tag_configure("even", background=COLORS["surface"])
        self.tree.tag_configure("odd", background="#161822")
        self.tree.tag_configure("empty", foreground=COLORS["muted"], background=COLORS["surface"])
        self.tree.bind("<<TreeviewSelect>>", self.select_row)
        vertical_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview, style="Dark.Vertical.TScrollbar")
        horizontal_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview, style="Dark.Horizontal.TScrollbar")
        self.tree.configure(yscrollcommand=vertical_scrollbar.set, xscrollcommand=horizontal_scrollbar.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vertical_scrollbar.grid(row=0, column=1, sticky="ns")
        horizontal_scrollbar.grid(row=1, column=0, sticky="ew")

    def parent_choices(self, name):
        queries = {
            "company_id": "SELECT company_id FROM companies ORDER BY company_id",
            "application_id": "SELECT application_id FROM applications ORDER BY application_id DESC",
        }
        query = queries.get(name)
        if query is None:
            return None
        try:
            return tuple(str(row[0]) for row in self.db_connection.execute(query, fetch=True) or [])
        except RuntimeError:
            return ()

    def column_width(self, column):
        text_columns = ("notes", "role_title", "feedback", "message", "file_path", "common_questions", "culture_notes", "perks")
        date_columns = ("applied_date", "interview_date", "joining_date", "due_date", "upload_date", "reminder_date", "changed_on")
        if column in text_columns:
            return 240
        if column in date_columns:
            return 180
        if column in ("company_name", "contact_name", "designation", "skill_name", "task_name"):
            return 200
        return 135

    def button(self, parent, text, command, color):
        button = tk.Button(parent, text=text, command=command, bg=color, fg="white", activebackground=color, activeforeground="white", relief="flat", cursor="hand2", font=("Segoe UI", 9, "bold"), padx=14, pady=7)
        button.bind("<Enter>", lambda _event: button.configure(relief="solid", bd=1))
        button.bind("<Leave>", lambda _event: button.configure(relief="flat", bd=0))
        return button

    def values(self):
        values = []
        integer_fields = ("company_id", "application_id", "round_number", "self_rating", "overall_rating", "target_applications", "actual_applications", "target_interviews", "actual_interviews")
        decimal_fields = ("stipend", "stipend_offered", "glassdoor_rating")
        for name, label in self.fields:
            value = self.entries[name].get().strip()
            if (name.endswith("date") or name == "changed_on") and not valid_date(value):
                messagebox.showerror("Invalid date", label + " must use YYYY-MM-DD.")
                return None
            if name in integer_fields and value:
                try:
                    value = int(value)
                except ValueError:
                    messagebox.showerror("Invalid number", label + " must be a whole number.")
                    return None
            if name in decimal_fields and value:
                try:
                    value = float(value)
                except ValueError:
                    messagebox.showerror("Invalid number", label + " must be numeric.")
                    return None
            if name in ("company_id", "application_id") and value:
                try:
                    value = int(value)
                except ValueError:
                    messagebox.showerror("Invalid selection", "Choose an existing parent record for " + label + ".")
                    return None
            values.append(value or None)
        return tuple(values)

    def load_data(self):
        try:
            search = self.search.get().strip()
            columns = [self.primary_key] + [field[0] for field in self.fields]
            query = "SELECT * FROM " + self.table
            values = ()
            if search:
                query += " WHERE " + " OR ".join(field + " LIKE %s" for field in self.search_fields)
                values = tuple("%" + search + "%" for _field in self.search_fields)
            query += " ORDER BY " + self.primary_key + " DESC"
            rows = self.db_connection.execute(query, values, fetch=True) or []
            self.tree.delete(*self.tree.get_children())
            for index, row in enumerate(rows):
                self.tree.insert("", "end", values=row, tags=("even" if index % 2 == 0 else "odd",))
            if not rows:
                empty_row = ("No records found",) + ("",) * (len(columns) - 1)
                self.tree.insert("", "end", values=empty_row, tags=("empty",))
        except RuntimeError as error:
            messagebox.showerror("Database", str(error))

    def refresh(self):
        self.load_data()

    def select_row(self, _event=None):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], "values")[1:]
        if self.tree.item(selected[0], "values")[0] == "No records found":
            return
        for index, (name, _label) in enumerate(self.fields):
            widget = self.entries[name]
            if isinstance(widget, ttk.Combobox):
                widget.set("" if values[index] is None else values[index])
            else:
                widget.delete(0, tk.END)
                widget.insert(0, "" if values[index] is None else values[index])

    def clear(self):
        for widget in self.entries.values():
            widget.set("") if isinstance(widget, ttk.Combobox) else widget.delete(0, tk.END)
        self.tree.selection_remove(self.tree.selection())

    def add(self):
        values = self.values()
        if values is None:
            return
        try:
            columns = ", ".join(field[0] for field in self.fields)
            marks = ", ".join("%s" for _field in self.fields)
            inserted_id = self.db_connection.execute("INSERT INTO " + self.table + " (" + columns + ") VALUES (" + marks + ")", values)
            self.clear()
            self.load_data()
            for item in self.tree.get_children():
                if str(self.tree.item(item, "values")[0]) == str(inserted_id):
                    self.tree.selection_set(item)
                    self.tree.focus(item)
                    self.tree.see(item)
                    break
            messagebox.showinfo("Saved", "Record added successfully.")
        except RuntimeError as error:
            messagebox.showerror("Database", str(error))

    def update(self):
        selected = self.tree.selection(); values = self.values()
        if not selected or values is None:
            messagebox.showwarning("Select a record", "Select a row before updating.")
            return
        record_id = self.tree.item(selected[0], "values")[0]
        assignments = ", ".join(field[0] + " = %s" for field in self.fields)
        try:
            self.db_connection.execute("UPDATE " + self.table + " SET " + assignments + " WHERE " + self.primary_key + " = %s", values + (record_id,))
            self.clear(); self.load_data(); messagebox.showinfo("Updated", "Record updated successfully.")
        except RuntimeError as error:
            messagebox.showerror("Database", str(error))

    def delete(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select a record", "Select a row before deleting.")
            return
        if not messagebox.askyesno("Confirm delete", "Delete the selected record?"):
            return
        record_id = self.tree.item(selected[0], "values")[0]
        try:
            self.db_connection.execute("DELETE FROM " + self.table + " WHERE " + self.primary_key + " = %s", (record_id,))
            self.clear(); self.load_data(); messagebox.showinfo("Deleted", "Record deleted successfully.")
        except RuntimeError as error:
            messagebox.showerror("Database", str(error))


class DashboardView:
    def __init__(self, parent):
        self.parent = parent
        self.refresh_job = None
        self.build()
        self.schedule_refresh()

    def refresh(self):
        if not self.parent.winfo_exists():
            return
        for child in self.parent.winfo_children():
            child.destroy()
        self.build()
        self.schedule_refresh()

    def dispose(self):
        if self.refresh_job is not None:
            try:
                self.parent.after_cancel(self.refresh_job)
            except Exception:
                pass
            self.refresh_job = None

    def schedule_refresh(self):
        if self.refresh_job is not None:
            try:
                self.parent.after_cancel(self.refresh_job)
            except Exception:
                pass
        self.refresh_job = self.parent.after(15000, self.refresh)

    def build(self):
        tk.Label(self.parent, text="🏠  Overview", bg=COLORS["background"], fg=COLORS["white"], font=("Segoe UI", 24, "bold")).pack(anchor="w", padx=28, pady=(27, 4))
        tk.Label(self.parent, text="Your internship pipeline at a glance", bg=COLORS["background"], fg=COLORS["muted"], font=("Segoe UI", 10)).pack(anchor="w", padx=28, pady=(0, 20))
        cards = tk.Frame(self.parent, bg=COLORS["background"])
        cards.pack(fill="x", padx=28)
        metrics = (("💼  Total Applications", "SELECT COUNT(*) FROM applications", COLORS["blue"], ()), ("★  Shortlisted", "SELECT COUNT(*) FROM applications WHERE status = %s", COLORS["amber"], ("Shortlisted",)), ("📅  Interviews", "SELECT COUNT(*) FROM interviews", COLORS["green"], ()), ("✉  Offers", "SELECT COUNT(*) FROM offers_comparison", COLORS["purple"], ()))
        for index, (title, query, accent, values) in enumerate(metrics):
            row, column = divmod(index, 2)
            cards.grid_columnconfigure(column, weight=1)
            card = tk.Frame(cards, bg=COLORS["surface"], highlightbackground=COLORS["border"], highlightthickness=1, padx=18, pady=15)
            card.grid(row=row, column=column, sticky="ew", padx=(0 if column == 0 else 7, 7 if column == 0 else 0), pady=5)
            tk.Frame(card, bg=accent, height=4).pack(fill="x", pady=(0, 12))
            tk.Label(card, text=title, bg=COLORS["surface"], fg=COLORS["muted"], font=("Segoe UI", 9, "bold")).pack(anchor="w")
            try:
                count = db.fetch_one(query, values)[0]
            except (RuntimeError, TypeError):
                count = 0
            tk.Label(card, text=count, bg=COLORS["surface"], fg=COLORS["white"], font=("Segoe UI", 27, "bold")).pack(anchor="w")
            tk.Label(card, text="↑  Live from database", bg=COLORS["surface"], fg=accent, font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(3, 0))
        self.table_section("▦  Recent Applications", "SELECT a.application_id, c.company_name, a.role_title, a.status, a.applied_date FROM applications a LEFT JOIN companies c ON a.company_id = c.company_id ORDER BY a.application_id DESC LIMIT 6", ("ID", "Company", "Role", "Status", "Applied"))
        self.table_section("◷  Upcoming Interviews", "SELECT interview_id, application_id, interview_date, interview_type, result FROM interviews WHERE interview_date > CURDATE() ORDER BY interview_date ASC LIMIT 6", ("ID", "Application", "Date", "Type", "Result"))

    def table_section(self, title, query, headings):
        frame = tk.LabelFrame(self.parent, text="  " + title + "  ", bg=COLORS["surface"], fg=COLORS["blue"], highlightbackground=COLORS["border"], highlightthickness=1, bd=0, font=("Segoe UI", 10, "bold"), padx=10, pady=8)
        frame.pack(fill="both", expand=True, padx=28, pady=(12, 0))
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        tree = ttk.Treeview(frame, columns=headings, show="headings", height=5, style="Dark.Treeview")
        summary_widths = {"ID": 55, "Company": 150, "Role": 210, "Status": 120, "Applied": 120, "Application": 110, "Date": 120, "Type": 120, "Result": 110}
        for heading in headings:
            tree.heading(heading, text=heading)
            tree.column(heading, width=summary_widths.get(heading, 130), minwidth=summary_widths.get(heading, 130), stretch=True)
        for index, result in enumerate(self.fetch(query)):
            tree.insert("", "end", values=result, tags=("even" if index % 2 == 0 else "odd",))
        tree.tag_configure("even", background=COLORS["surface"])
        tree.tag_configure("odd", background="#161822")
        vertical_scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview, style="Dark.Vertical.TScrollbar")
        tree.configure(yscrollcommand=vertical_scrollbar.set)
        tree.grid(row=0, column=0, sticky="nsew")
        vertical_scrollbar.grid(row=0, column=1, sticky="ns")

    def fetch(self, query):
        try:
            return db.execute(query, fetch=True)
        except RuntimeError:
            return []


class ApplicationShell:
    def __init__(self, root):
        self.root = root
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.title("Internship Application Tracker")
        self.root.geometry("1280x800")
        self.root.minsize(980, 650)
        self.active_button = None
        self.style()
        self.build()

    def style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Dark.Treeview", background=COLORS["surface"], fieldbackground=COLORS["surface"], foreground=COLORS["white"], rowheight=31, borderwidth=0, relief="flat")
        style.configure("Dark.Treeview.Heading", background=COLORS["active"], foreground=COLORS["white"], font=("Segoe UI", 9, "bold"), relief="flat", padding=8)
        style.map("Dark.Treeview", background=[("selected", COLORS["blue"])], foreground=[("selected", COLORS["white"])])
        style.configure("Dark.TCombobox", fieldbackground=COLORS["field"], background=COLORS["field"], foreground=COLORS["white"], arrowcolor=COLORS["blue"])
        style.configure("Dark.Vertical.TScrollbar", background=COLORS["border"], troughcolor=COLORS["background"], bordercolor=COLORS["background"], lightcolor=COLORS["border"], darkcolor=COLORS["border"], arrowcolor=COLORS["muted"])
        style.configure("Dark.Horizontal.TScrollbar", background=COLORS["border"], troughcolor=COLORS["background"], bordercolor=COLORS["background"], lightcolor=COLORS["border"], darkcolor=COLORS["border"], arrowcolor=COLORS["muted"])

    def build(self):
        self.root.configure(bg=COLORS["background"])
        sidebar_host = tk.Frame(self.root, bg=COLORS["sidebar"], width=250)
        sidebar_host.pack(side="left", fill="y")
        sidebar_host.pack_propagate(False)
        sidebar_canvas = tk.Canvas(sidebar_host, bg=COLORS["sidebar"], highlightthickness=0, width=250)
        sidebar_scrollbar = ttk.Scrollbar(sidebar_host, orient="vertical", command=sidebar_canvas.yview, style="Dark.Vertical.TScrollbar")
        sidebar_canvas.configure(yscrollcommand=sidebar_scrollbar.set)
        sidebar_canvas.pack(side="left", fill="both", expand=True)
        sidebar_scrollbar.pack(side="right", fill="y")
        self.sidebar = tk.Frame(sidebar_canvas, bg=COLORS["sidebar"], width=250)
        sidebar_window = sidebar_canvas.create_window((0, 0), window=self.sidebar, anchor="nw")
        self.sidebar.bind("<Configure>", lambda _event: sidebar_canvas.configure(scrollregion=sidebar_canvas.bbox("all")))
        sidebar_canvas.bind("<Configure>", lambda event: sidebar_canvas.itemconfigure(sidebar_window, width=event.width))
        self.bind_mousewheel(sidebar_canvas)
        sidebar_host.bind("<Enter>", lambda _event: setattr(self, "active_scroll_canvas", sidebar_canvas))

        content_host = tk.Frame(self.root, bg=COLORS["background"])
        content_host.pack(side="right", fill="both", expand=True)
        content_canvas = tk.Canvas(content_host, bg=COLORS["background"], highlightthickness=0)
        content_scrollbar = ttk.Scrollbar(content_host, orient="vertical", command=content_canvas.yview, style="Dark.Vertical.TScrollbar")
        content_canvas.configure(yscrollcommand=content_scrollbar.set)
        content_canvas.pack(side="left", fill="both", expand=True)
        content_scrollbar.pack(side="right", fill="y")
        self.content = tk.Frame(content_canvas, bg=COLORS["background"])
        content_window = content_canvas.create_window((0, 0), window=self.content, anchor="nw")
        self.content.bind("<Configure>", lambda _event: content_canvas.configure(scrollregion=content_canvas.bbox("all")))
        content_canvas.bind("<Configure>", lambda event: content_canvas.itemconfigure(content_window, width=event.width))
        self.bind_mousewheel(content_canvas)
        content_host.bind("<Enter>", lambda _event: setattr(self, "active_scroll_canvas", content_canvas))
        self.sidebar_canvas = sidebar_canvas
        self.content_canvas = content_canvas
        self.build_sidebar()
        self.root.update_idletasks()
        sidebar_canvas.configure(scrollregion=sidebar_canvas.bbox("all"))
        sidebar_canvas.yview_moveto(0)
        self.show_dashboard()

    def bind_mousewheel(self, canvas):
        canvas.bind("<Enter>", lambda _event: setattr(self, "active_scroll_canvas", canvas))
        canvas.bind("<Leave>", lambda _event: setattr(self, "active_scroll_canvas", None))
        if not hasattr(self, "active_scroll_canvas"):
            self.active_scroll_canvas = None
            self.root.bind_all("<MouseWheel>", self.scroll_active_canvas)
            self.root.bind_all("<Next>", self.scroll_page_down)
            self.root.bind_all("<Prior>", self.scroll_page_up)
            self.root.bind_all("<Down>", self.scroll_line_down)
            self.root.bind_all("<Up>", self.scroll_line_up)

    def scroll_active_canvas(self, event):
        if self.active_scroll_canvas is not None:
            self.active_scroll_canvas.yview_scroll(int(-event.delta / 120), "units")

    def scroll_page_down(self, _event):
        if self.active_scroll_canvas is self.sidebar_canvas:
            self.sidebar_canvas.yview_scroll(5, "pages")

    def scroll_page_up(self, _event):
        if self.active_scroll_canvas is self.sidebar_canvas:
            self.sidebar_canvas.yview_scroll(-5, "pages")

    def scroll_line_down(self, _event):
        if self.active_scroll_canvas is self.sidebar_canvas:
            self.sidebar_canvas.yview_scroll(1, "units")

    def scroll_line_up(self, _event):
        if self.active_scroll_canvas is self.sidebar_canvas:
            self.sidebar_canvas.yview_scroll(-1, "units")

    def build_sidebar(self):
        tk.Label(self.sidebar, text="IAT", bg=COLORS["sidebar"], fg=COLORS["blue"], font=("Segoe UI", 31, "bold")).pack(anchor="w", padx=24, pady=(22, 0))
        tk.Label(self.sidebar, text="INTERNSHIP TRACKER", bg=COLORS["sidebar"], fg=COLORS["muted"], font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=27, pady=(0, 9))
        identity = tk.Frame(self.sidebar, bg=COLORS["active"], padx=12, pady=10)
        identity.pack(fill="x", padx=14, pady=(7, 22))
        tk.Label(identity, text="●  User profile", bg=COLORS["active"], fg=COLORS["green"], font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(identity, text="Internship Tracker / ID: USR-1001", bg=COLORS["active"], fg=COLORS["white"], font=("Segoe UI", 9)).pack(anchor="w", pady=(2, 0))
        more_button = tk.Button(self.sidebar, text="↓  More navigation", command=self.scroll_sidebar_bottom, anchor="w", bg=COLORS["active"], fg=COLORS["cyan"], activebackground=COLORS["blue"], activeforeground=COLORS["white"], relief="flat", cursor="hand2", font=("Segoe UI", 9, "bold"), padx=20, pady=7)
        more_button.pack(fill="x", padx=9, pady=(0, 10))
        groups = (("WORKSPACE", (("🏠  Dashboard", self.show_dashboard), ("💼  Applications", self.show_applications), ("🏢  Companies", self.show_companies), ("📊  Reports", self.show_reports))), ("MANAGE", (("📅  Interviews", self.show_interviews), ("✉  Contacts", self.show_contacts), ("⚡  Skills Required", self.show_skills), ("🎯  Preparation Tasks", self.show_tasks), ("▤  Documents", self.show_documents), ("🔔  Reminders", self.show_reminders))), ("INSIGHTS", (("⌂  Company Research", self.show_research), ("✉  Offer Comparison", self.show_offers), ("↗  Status History", self.show_history), ("🎯  Goals", self.show_goals))))
        for group_name, links in groups:
            tk.Label(self.sidebar, text=group_name, bg=COLORS["sidebar"], fg="#64748B", font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=24, pady=(5, 3))
            for text, command in links:
                button = tk.Button(self.sidebar, text=text, anchor="w", bg=COLORS["sidebar"], fg=COLORS["muted"], activebackground=COLORS["active"], activeforeground=COLORS["white"], relief="flat", bd=0, font=("Segoe UI", 9), cursor="hand2", padx=20, pady=6)
                button.configure(command=lambda c=command, b=button: self.activate(c, b))
                button.pack(fill="x", padx=9)
        top_button = tk.Button(self.sidebar, text="↑  Back to top", command=self.scroll_sidebar_top, anchor="w", bg=COLORS["active"], fg=COLORS["cyan"], activebackground=COLORS["blue"], activeforeground=COLORS["white"], relief="flat", cursor="hand2", font=("Segoe UI", 9, "bold"), padx=20, pady=7)
        top_button.pack(fill="x", padx=9, pady=(12, 6))
        help_badge = tk.Frame(self.sidebar, bg=COLORS["active"], padx=12, pady=9)
        help_badge.pack(fill="x", padx=14, pady=(18, 8))
        tk.Label(help_badge, text="?  Need a hand?", bg=COLORS["active"], fg=COLORS["white"], font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(help_badge, text="Your data is safely organized.", bg=COLORS["active"], fg=COLORS["muted"], font=("Segoe UI", 8)).pack(anchor="w")
        logout = tk.Button(self.sidebar, text="⇥  Logout", command=self.logout, anchor="w", bg=COLORS["sidebar"], fg=COLORS["amber"], activebackground=COLORS["rose"], relief="flat", font=("Segoe UI", 9, "bold"), padx=20, pady=10)
        logout.pack(fill="x", padx=9, pady=(0, 18))

    def scroll_sidebar_top(self):
        self.sidebar_canvas.yview_moveto(0)

    def scroll_sidebar_bottom(self):
        self.sidebar_canvas.yview_moveto(1)

    def activate(self, command, button):
        if self.active_button:
            self.active_button.configure(bg=COLORS["sidebar"], fg=COLORS["muted"])
        self.active_button = button
        button.configure(bg=COLORS["active"], fg=COLORS["white"])
        command()

    def show(self, factory):
        current_view = getattr(self, "current_view", None)
        if isinstance(current_view, DashboardView):
            current_view.dispose()
        for child in self.content.winfo_children():
            child.destroy()
        view = factory(self.content)
        self.current_view = view
        if isinstance(view, DashboardView):
            self.dashboard_view = view

    def refresh_dashboard(self):
        if getattr(self, "dashboard_view", None) is not None:
            self.dashboard_view.refresh()
        else:
            self.show_dashboard()

    def show_dashboard(self): self.show(DashboardView)
    def show_reports(self):
        from modules.reports import ReportsView
        self.show(lambda parent: ReportsView(parent, db))
    def crud(self, module): self.show(module)
    def show_applications(self): from modules.applications import ApplicationsView; self.crud(ApplicationsView)
    def show_companies(self): from modules.companies import CompaniesView; self.crud(CompaniesView)
    def show_interviews(self): from modules.interviews import InterviewsView; self.crud(InterviewsView)
    def show_contacts(self): from modules.contacts import ContactsView; self.crud(ContactsView)
    def show_skills(self): from modules.skills_requirement import SkillsView; self.crud(SkillsView)
    def show_tasks(self): from modules.preparation_tasks import PreparationTasksView; self.crud(PreparationTasksView)
    def show_documents(self): from modules.documents import DocumentsView; self.crud(DocumentsView)
    def show_reminders(self): from modules.reminders import RemindersView; self.crud(RemindersView)
    def show_research(self): from modules.company_research import CompanyResearchView; self.crud(CompanyResearchView)
    def show_offers(self): from modules.offers_comparison import OffersView; self.crud(OffersView)
    def show_history(self): from modules.status_history import StatusHistoryView; self.crud(StatusHistoryView)
    def show_goals(self): from modules.goals import GoalsView; self.crud(GoalsView)
    def logout(self):
        if messagebox.askyesno("Logout", "Close the dashboard?"):
            self.root.destroy()
