import frappe

@frappe.whitelist()
def create_job_opening(**kwargs):
    """
    Create a new Job Opening
    """
    try:
        # Extract data from kwargs or form_dict
        data = kwargs or frappe.form_dict
        
        # Create Job Opening document
        job_opening = frappe.get_doc({
            "doctype": "Job Opening",
            "job_title": data.get("job_title"),
            "designation": data.get("designation"),
            "company": data.get("company"),
            "department": data.get("department"),
            "employment_type": data.get("employment_type"),
            "location": data.get("location"),
            "description": data.get("description"),
            "status": data.get("status", "Open"),
            "currency": data.get("currency", "INR"),
            "lower_range": data.get("lower_range"),
            "upper_range": data.get("upper_range"),
            "salary_per": data.get("salary_per", "Month"),
        })
        
        job_opening.insert(ignore_permissions=True)
        frappe.db.commit()
        
        return {
            "message": "Job Opening created successfully",
            "name": job_opening.name,
            "job_title": job_opening.job_title
        }
        
    except Exception as e:
        frappe.log_error(f"Failed to create job opening: {str(e)}")
        frappe.throw(f"Failed to create job opening: {str(e)}")

