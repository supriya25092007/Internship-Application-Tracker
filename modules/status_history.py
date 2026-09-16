from dashboard import CrudView


class StatusHistoryView(CrudView):
	def __init__(self, parent):
		super().__init__(parent, "Status History", "status_history", "history_id", [("application_id", "Application ID"), ("old_status", "Old Status"), ("new_status", "New Status"), ("changed_on", "Changed Date (YYYY-MM-DD)")])
