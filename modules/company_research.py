from dashboard import CrudView


class CompanyResearchView(CrudView):
	def __init__(self, parent):
		super().__init__(parent, "Company Research", "company_research", "research_id", [("company_id", "Company ID"), ("glassdoor_rating", "Glassdoor Rating"), ("avg_interview_difficulty", "Average Interview Difficulty"), ("common_questions", "Common Questions"), ("culture_notes", "Culture Notes"), ("source", "Source")])
