from dashboard import CrudView


class RemindersView(CrudView):
	def __init__(self, parent):
		super().__init__(parent, "Reminders", "reminders", "reminder_id", [("application_id", "Application ID"), ("reminder_type", "Reminder Type"), ("reminder_date", "Reminder Date (YYYY-MM-DD)"), ("message", "Message"), ("is_sent", "Is Sent")], {"is_sent": ("0", "1")})
