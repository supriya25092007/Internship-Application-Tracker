from dashboard import CrudView


class GoalsView(CrudView):
	def __init__(self, parent):
		super().__init__(parent, "Goals", "goals", "goal_id", [("goal_period", "Goal Period"), ("target_applications", "Target Applications"), ("actual_applications", "Actual Applications"), ("target_interviews", "Target Interviews"), ("actual_interviews", "Actual Interviews"), ("notes", "Notes")])
