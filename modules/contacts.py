from dashboard import CrudView


class ContactsView(CrudView):
	def __init__(self, parent):
		super().__init__(parent, "Contacts", "contacts", "contact_id", [("company_id", "Company ID"), ("contact_name", "Contact Name"), ("designation", "Designation"), ("linkedin_url", "LinkedIn URL"), ("phone", "Phone"), ("email", "Email"), ("relationship", "Relationship")])
