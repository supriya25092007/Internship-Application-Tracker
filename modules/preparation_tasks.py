from dashboard import CrudView


class PreparationTasksView(CrudView):
	def __init__(self, parent):
		super().__init__(parent, "Preparation Tasks", "preparation_tasks", "task_id", [("application_id", "Application ID"), ("task_name", "Task Name"), ("due_date", "Due Date (YYYY-MM-DD)"), ("is_completed", "Is Completed")], {"is_completed": ("0", "1")})
