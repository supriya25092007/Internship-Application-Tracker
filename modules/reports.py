import tkinter as tk
from tkinter import ttk


COLORS = {
    "background": "#0C0D12", "surface": "#1A1D26", "active": "#1F222E",
    "border": "#2A2E3D", "blue": "#3B82F6", "green": "#10B981",
    "purple": "#8B5CF6", "amber": "#F59E0B", "cyan": "#06B6D4",
    "rose": "#EF4444", "white": "#F8FAFC", "muted": "#94A3B8",
}


class ReportsView(tk.Frame):
    def __init__(self, parent, db_connection=None):
        super().__init__(parent, bg=COLORS["background"])
        self.pack(fill="both", expand=True)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.db_connection = db_connection
        self.metric_values = {}
        self.status_tree = None
        self.company_tree = None
        try:
            self.configure_styles()
            self.build_ui()
            self.load_data()
        except Exception as error:
            self.show_initialization_warning(error)

    def configure_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Reports.Treeview", background=COLORS["surface"], fieldbackground=COLORS["surface"], foreground=COLORS["white"], rowheight=32, borderwidth=0)
        style.configure("Reports.Treeview.Heading", background=COLORS["active"], foreground=COLORS["white"], font=("Segoe UI", 9, "bold"), relief="flat", padding=8)
        style.map("Reports.Treeview", background=[("selected", COLORS["blue"])], foreground=[("selected", COLORS["white"])])
        style.configure("Reports.Vertical.TScrollbar", background=COLORS["border"], troughcolor=COLORS["background"], bordercolor=COLORS["background"], lightcolor=COLORS["border"], darkcolor=COLORS["border"], arrowcolor=COLORS["muted"])
        style.configure("Reports.Horizontal.TScrollbar", background=COLORS["border"], troughcolor=COLORS["background"], bordercolor=COLORS["background"], lightcolor=COLORS["border"], darkcolor=COLORS["border"], arrowcolor=COLORS["muted"])

    def build_ui(self):
        canvas = tk.Canvas(self, bg=COLORS["background"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview, style="Reports.Vertical.TScrollbar")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        body = tk.Frame(canvas, bg=COLORS["background"])
        window_id = canvas.create_window((0, 0), window=body, anchor="nw")
        body.bind("<Configure>", lambda _event: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda event: canvas.itemconfigure(window_id, width=event.width))

        header = tk.Frame(body, bg=COLORS["background"])
        header.pack(fill="x", padx=28, pady=(25, 19))
        tk.Label(header, text="📊  Application Analytics & Reports", bg=COLORS["background"], fg=COLORS["white"], font=("Segoe UI", 24, "bold")).pack(side="left")
        tk.Button(header, text="⟳  Refresh Analytics", command=self.load_data, bg=COLORS["blue"], fg="white", activebackground="#2563EB", relief="flat", cursor="hand2", font=("Segoe UI", 9, "bold"), padx=14, pady=8).pack(side="right")

        cards = tk.Frame(body, bg=COLORS["background"])
        cards.pack(fill="x", padx=28)
        cards.grid_columnconfigure(0, weight=1)
        cards.grid_columnconfigure(1, weight=1)
        definitions = (
            ("total", "Total Applications", COLORS["blue"], "get_total_applications"),
            ("pending", "In Review / Pending", COLORS["amber"], "get_pending_applications"),
            ("interviews", "Interviews", COLORS["green"], "get_interviews"),
            ("offers", "Offers", COLORS["purple"], "get_offers"),
        )
        for index, (key, title, accent, _loader) in enumerate(definitions):
            row, column = divmod(index, 2)
            card = tk.Frame(cards, bg=COLORS["surface"], highlightbackground=COLORS["border"], highlightthickness=1, padx=18, pady=15)
            card.grid(row=row, column=column, sticky="nsew", padx=(0 if column == 0 else 7, 7 if column == 0 else 0), pady=5)
            tk.Frame(card, bg=accent, height=4).pack(fill="x", pady=(0, 12))
            tk.Label(card, text=title, bg=COLORS["surface"], fg=COLORS["muted"], font=("Segoe UI", 10, "bold")).pack(anchor="w")
            value = tk.Label(card, text="0", bg=COLORS["surface"], fg=COLORS["white"], font=("Segoe UI", 28, "bold"))
            value.pack(anchor="w", pady=(8, 3))
            tk.Label(card, text="Live from applications", bg=COLORS["surface"], fg=accent, font=("Segoe UI", 8, "bold")).pack(anchor="w")
            self.metric_values[key] = value

        tables = tk.Frame(body, bg=COLORS["background"])
        tables.pack(fill="both", expand=True, padx=28, pady=(17, 24))
        tables.grid_columnconfigure(0, weight=1)
        tables.grid_columnconfigure(1, weight=1)
        self.status_tree = self.create_table(tables, "Applications by Status", ("Status", "Total Count"), 0)
        self.company_tree = self.create_table(tables, "Applications by Company", ("Company Name", "Applications"), 1)

    def create_table(self, parent, title, columns, column):
        section = tk.LabelFrame(parent, text="  " + title + "  ", bg=COLORS["surface"], fg=COLORS["blue"], highlightbackground=COLORS["border"], highlightthickness=1, bd=0, font=("Segoe UI", 10, "bold"), padx=12, pady=10)
        section.grid(row=0, column=column, sticky="nsew", padx=(0 if column == 0 else 8, 8 if column == 0 else 0))
        section.grid_rowconfigure(0, weight=1)
        section.grid_columnconfigure(0, weight=1)
        tree = ttk.Treeview(section, columns=columns, show="headings", height=9, style="Reports.Treeview")
        for heading in columns:
            tree.heading(heading, text=heading)
        tree.column(columns[0], width=220, minwidth=180, anchor="w", stretch=False)
        tree.column(columns[1], width=150, minwidth=150, anchor="center", stretch=False)
        tree.tag_configure("even", background=COLORS["surface"])
        tree.tag_configure("odd", background="#161822")
        tree.tag_configure("empty", foreground=COLORS["muted"], background=COLORS["surface"])
        vertical = ttk.Scrollbar(section, orient="vertical", command=tree.yview, style="Reports.Vertical.TScrollbar")
        tree.grid(row=0, column=0, sticky="nsew")
        vertical.grid(row=0, column=1, sticky="ns")
        tree.configure(yscrollcommand=vertical.set)
        return tree

    def query_rows(self, query, values=()):
        try:
            if self.db_connection is None:
                return []
            return self.db_connection.execute(query, values, fetch=True) or []
        except Exception:
            return []

    def query_count(self, query, values=()):
        try:
            rows = self.query_rows(query, values)
            if not rows or rows[0][0] is None:
                return 0
            return int(rows[0][0])
        except Exception:
            return 0

    def get_total_applications(self):
        try:
            return self.query_count("SELECT COUNT(*) FROM applications")
        except Exception:
            return 0

    def get_pending_applications(self):
        try:
            return self.query_count("SELECT COUNT(*) FROM applications WHERE status LIKE %s OR status LIKE %s", ("%App%", "%Pend%"))
        except Exception:
            return 0

    def get_interviews(self):
        try:
            return self.query_count("SELECT COUNT(*) FROM applications WHERE status LIKE %s", ("%Interv%",))
        except Exception:
            return 0

    def get_offers(self):
        try:
            return self.query_count("SELECT COUNT(*) FROM applications WHERE status LIKE %s", ("%Offer%",))
        except Exception:
            return 0

    def load_data(self):
        if self.status_tree is None or self.company_tree is None:
            return
        try:
            self.metric_values["total"].configure(text=str(self.get_total_applications()))
            self.metric_values["pending"].configure(text=str(self.get_pending_applications()))
            self.metric_values["interviews"].configure(text=str(self.get_interviews()))
            self.metric_values["offers"].configure(text=str(self.get_offers()))
        except Exception as error:
            self.show_initialization_warning(error)
            return

        self.fill_tree(self.status_tree, self.query_rows("SELECT status, COUNT(*) FROM applications GROUP BY status ORDER BY status"), "Status")
        company_query = ("SELECT COALESCE(c.company_name, 'Unknown Company'), COUNT(a.application_id) "
                         "FROM applications a LEFT JOIN companies c ON a.company_id = c.company_id "
                         "GROUP BY c.company_id, c.company_name ORDER BY COUNT(a.application_id) DESC, c.company_name")
        self.fill_tree(self.company_tree, self.query_rows(company_query), "Company Name")

    def fill_tree(self, tree, rows, first_label):
        tree.delete(*tree.get_children())
        if not rows:
            tree.insert("", "end", values=("No data available", ""), tags=("empty",))
            return
        for index, row in enumerate(rows):
            tree.insert("", "end", values=(row[0] or first_label, row[1] or 0), tags=("even" if index % 2 == 0 else "odd",))

    def refresh_data(self):
        self.load_data()

    def show_initialization_warning(self, error):
        tk.Label(self, text="Report Initialization Warning: " + str(error), bg=COLORS["background"], fg=COLORS["rose"], font=("Segoe UI", 16, "bold"), wraplength=900, justify="left").pack(fill="both", expand=True, padx=40, pady=40)
