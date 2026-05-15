import frappe

@frappe.whitelist(allow_guest=True)
def get_csrf_token() -> str:
	return frappe.sessions.get_csrf_token()
