import frappe

@frappe.whitelist()
def get_interviewers():
    """
    Get all users who have the 'Interviewer' role
    Returns user details including name, full_name, and email
    """
    try:
        # Query to get users with Interviewer role
        interviewers = frappe.db.sql("""
            SELECT DISTINCT 
                u.name, 
                u.full_name, 
                u.email,
                u.user_image
            FROM `tabUser` u
            INNER JOIN `tabHas Role` hr ON hr.parent = u.name
            WHERE hr.role = 'Interviewer'
            AND u.enabled = 1
            AND u.name NOT IN ('Administrator', 'Guest')
            ORDER BY u.full_name
        """, as_dict=1)
        
        return {
            "message": "Success",
            "data": interviewers,
            "count": len(interviewers)
        }
        
    except Exception as e:
        frappe.log_error(f"Error fetching interviewers: {str(e)}")
        return {
            "message": "Error fetching interviewers",
            "data": [],
            "count": 0,
            "error": str(e)
        }


@frappe.whitelist()
def get_interview_details(interview_name):
    """
    Get interview details including all related information
    """
    try:
        interview = frappe.get_doc("Interview", interview_name)
        
        return {
            "message": "Success",
            "data": interview.as_dict()
        }
        
    except Exception as e:
        frappe.log_error(f"Error fetching interview details: {str(e)}")
        frappe.throw(f"Error fetching interview details: {str(e)}")

