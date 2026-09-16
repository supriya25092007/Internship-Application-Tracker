from dashboard import CrudView


class ApplicationsView(CrudView):
	def __init__(self, parent):
		super().__init__(parent, "Applications", "applications", "application_id", [("company_id", "Company ID"), ("role_title", "Role Title"), ("applied_date", "Applied Date (YYYY-MM-DD)"), ("status", "Status"), ("stipend", "Stipend"), ("mode", "Mode"), ("resume_version", "Resume Version"), ("notes", "Notes")], {"status": ("Applied", "Shortlisted", "Rejected", "Withdrawn", "Offer"), "mode": ("Remote", "Hybrid", "On-site")})
