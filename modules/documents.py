from dashboard import CrudView


class DocumentsView(CrudView):
	def __init__(self, parent):
		super().__init__(parent, "Documents", "documents", "document_id", [("application_id", "Application ID"), ("doc_type", "Document Type"), ("version_name", "Version Name"), ("file_path", "File Path"), ("upload_date", "Upload Date (YYYY-MM-DD)")])
