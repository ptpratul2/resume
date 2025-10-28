import frappe

def create_interview_custom_fields():
    """
    Create custom fields for Interview doctype
    """
    custom_fields = [
        {
            "doctype": "Custom Field",
            "dt": "Interview",
            "fieldname": "meeting_link",
            "label": "Meeting Link",
            "fieldtype": "Data",
            "insert_after": "to_time",
            "description": "Video conferencing link for the interview (Zoom, Google Meet, etc.)",
            "options": "URL"
        }
    ]
    
    for field in custom_fields:
        if not frappe.db.exists("Custom Field", {"dt": field["dt"], "fieldname": field["fieldname"]}):
            doc = frappe.get_doc(field)
            doc.insert(ignore_permissions=True)
            print(f"Created custom field: {field['fieldname']} in {field['dt']}")
        else:
            print(f"Custom field already exists: {field['fieldname']} in {field['dt']}")
    
    frappe.db.commit()

