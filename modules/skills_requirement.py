from dashboard import CrudView


class SkillsView(CrudView):
	def __init__(self, parent):
		super().__init__(parent, "Skills Required", "skills_required", "skill_id", [("application_id", "Application ID"), ("skill_name", "Skill Name"), ("proficiency_needed", "Proficiency Needed"), ("self_rating", "Self Rating")])
