import frappe


# =========================================================
# SITE HR ROLES
# =========================================================

SITE_HR_ROLES = {
    "Site HR User",
    "Site HR Manager",
}


# =========================================================
# GET DIRECTLY ASSIGNED ROLES
# =========================================================

def get_direct_roles(user=None):
    """
    Returns only the roles directly assigned to the user.

    We use Has Role instead of frappe.get_roles()
    so that Administrator/other users are not incorrectly
    treated as Site HR.
    """

    user = user or frappe.session.user

    roles = frappe.get_all(
        "Has Role",
        filters={
            "parent": user,
            "parenttype": "User",
        },
        pluck="role"
    )

    return set(roles)


# =========================================================
# CHECK WHETHER CURRENT USER IS SITE HR
# =========================================================

def is_site_hr_user(user=None):
    """
    Returns True only when the user has a directly assigned
    Site HR User or Site HR Manager role.
    """

    user = user or frappe.session.user

    direct_roles = get_direct_roles(user)

    return bool(
        SITE_HR_ROLES.intersection(direct_roles)
    )


# =========================================================
# GET OWNER CONDITION
# =========================================================

def get_owner_condition(doctype, user=None):
    """
    Site HR:
        Only records created by the logged-in user.

    Other roles:
        No restriction, so they can see all records.
    """

    user = user or frappe.session.user

    # Other roles can see everything
    if not is_site_hr_user(user):
        return ""

    # Site HR can see only their own records
    return f"`tab{doctype}`.`owner` = {frappe.db.escape(user)}"


# =========================================================
# JOB OPENING
# =========================================================

def job_opening_query(user=None):
    return get_owner_condition("Job Opening", user)

def job_applicant_query(user):
    return get_owner_condition("Job Applicant", user)

def interview_query(user):
    return get_owner_condition("Interview", user)

def interview_feedback_query(user=None):
    return get_owner_condition("Interview Feedback", user)

def applicant_document_query(user=None):
    user = user or frappe.session.user

    if not is_site_hr_user(user):
        return ""

    user = frappe.db.escape(user)

    return f"""
        EXISTS (
            SELECT 1
            FROM `tabJob Applicant` ja
            WHERE ja.name = `tabApplicant Document`.`applicant_name`
            AND ja.owner = {user}
        )
    """


# =========================================================
# GENERIC OWNER CHECK
# =========================================================

def check_owner_access(doctype, name, user=None):
    """
    Used when accessing/updating/deleting one specific document.

    Site HR:
        Allowed only if they are the owner.

    Other roles:
        Allowed.
    """

    user = user or frappe.session.user

    # Other roles have full access
    if not is_site_hr_user(user):
        return True

    # Get document owner
    owner = frappe.db.get_value(
        doctype,
        name,
        "owner"
    )

    # Site HR can access only their own document
    return owner == user

@frappe.whitelist()
def check_is_site_hr_user():
    """Expose is_site_hr_user() check to frontend for conditional UI rendering."""
    return {"is_site_hr": is_site_hr_user()}