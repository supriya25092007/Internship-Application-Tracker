import unittest
from unittest.mock import patch

from dashboard import ApplicationShell, CrudView, DashboardView


class DummyDashboard:
    def __init__(self):
        self.refreshed = 0

    def refresh(self):
        self.refreshed += 1


class DummyParent:
    def __init__(self):
        self.cancelled_job = None

    def after_cancel(self, job):
        self.cancelled_job = job


class DummyDatabase:
    def execute(self, _query, _values):
        return 42


class DummyTree:
    def get_children(self):
        return ("saved-row",)

    def item(self, _item, _option):
        return ("42", "Acme")

    def selection_set(self, item):
        self.selected = item

    def focus(self, item):
        self.focused = item

    def see(self, item):
        self.visible = item


class DashboardRefreshTests(unittest.TestCase):
    def test_application_shell_refresh_dashboard_invokes_current_dashboard(self):
        shell = object.__new__(ApplicationShell)
        shell.dashboard_view = DummyDashboard()

        shell.refresh_dashboard()

        self.assertEqual(shell.dashboard_view.refreshed, 1)

    def test_dashboard_view_has_refresh_method(self):
        self.assertTrue(callable(getattr(DashboardView, "refresh", None)))

    def test_dashboard_view_dispose_cancels_scheduled_refresh(self):
        parent = DummyParent()
        view = object.__new__(DashboardView)
        view.parent = parent
        view.refresh_job = "refresh-job"

        view.dispose()

        self.assertEqual(parent.cancelled_job, "refresh-job")
        self.assertIsNone(view.refresh_job)

    def test_add_selects_database_assigned_id_after_reload(self):
        view = object.__new__(CrudView)
        view.fields = [("company_name", "Company Name")]
        view.table = "companies"
        view.db_connection = DummyDatabase()
        view.tree = DummyTree()
        view.values = lambda: ("Acme",)
        view.clear = lambda: None
        view.load_data = lambda: None

        with patch("dashboard.messagebox.showinfo"):
            view.add()

        self.assertEqual(view.tree.selected, "saved-row")
        self.assertEqual(view.tree.focused, "saved-row")
        self.assertEqual(view.tree.visible, "saved-row")


if __name__ == "__main__":
    unittest.main()
