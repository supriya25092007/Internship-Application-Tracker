from dashboard import CrudView


class InterviewsView(CrudView):
	def __init__(self, parent):
		super().__init__(parent, "Interviews", "interviews", "interview_id", [("application_id", "Application ID"), ("round_number", "Round Number"), ("interview_date", "Interview Date (YYYY-MM-DD)"), ("interview_type", "Interview Type"), ("result", "Result"), ("feedback", "Feedback")], {"interview_type": ("Technical", "HR", "Managerial"), "result": ("Pending", "Passed", "Failed")})
