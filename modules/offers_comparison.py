from dashboard import CrudView


class OffersView(CrudView):
	def __init__(self, parent):
		super().__init__(parent, "Offer Comparison", "offers_comparison", "offer_id", [("application_id", "Application ID"), ("stipend_offered", "Stipend Offered"), ("joining_date", "Joining Date (YYYY-MM-DD)"), ("location", "Location"), ("work_hours", "Work Hours"), ("perks", "Perks"), ("overall_rating", "Overall Rating"), ("final_decision", "Final Decision")], {"final_decision": ("Undecided", "Accepted", "Rejected")})
