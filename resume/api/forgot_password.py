import frappe
from frappe.rate_limiter import rate_limit

@frappe.whitelist(allow_guest=True)
@rate_limit(key="ip", limit=5, seconds=60)
def send_reset_link(email):
    """
    Forgot password wrapper with custom rate limit
    """

    # Prevent user enumeration
    if not frappe.db.exists("User", email):
        return {"not ok": True}


    frappe.core.doctype.user.user.reset_password(email)
    return {"ok": True} 