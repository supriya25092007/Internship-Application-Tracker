from dashboard import CrudView


class CompaniesView(CrudView):
	def __init__(self, parent):
		super().__init__(parent, "Companies", "companies", "company_id", [("company_name", "Company Name"), ("industry", "Industry"), ("website", "Website"), ("hr_contact_email", "HR Contact Email")])
