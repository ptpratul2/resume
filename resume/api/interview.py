import frappe
from datetime import datetime, timezone
import json


@frappe.whitelist()  # CHANGED: allow_guest=True hataya — ye function Interview record create karta hai
def create_interview_event():
    """Create a new interview event"""
    data = frappe.form_dict
    frappe.log("Received interview event data: {data}".format(data=json.dumps(dict(data), indent=2)))

    # Define required fields
    required_fields = ["interview_round", "job_applicant", "scheduled_on", "from_time", "to_time", "status"]
    for field in required_fields:
        if not data.get(field):
            frappe.throw(f"{field} is required")

    # NEW: Permission check — dynamic Role Permissions Manager settings ke hisaab se.
    # Ye Interview doctype ka naya record create karta hai.
    if not frappe.has_permission("Interview", ptype="create"):
        frappe.throw("You do not have permission to create an Interview")

    # Validate status
    status = data.get("status")
    frappe.log(f"status received: {status}")
    valid_statuses = ["Pending", "Scheduled", "Completed", "Cancelled", "Cleared", "Under Review", "Rejected"]
    if not status or status not in valid_statuses:
        frappe.throw(f"Invalid or missing status. Must be one of {', '.join(valid_statuses)}")

    # Validate time range
    from_time = data.get("from_time")
    to_time = data.get("to_time")
    
    if from_time and to_time:
        try:
            from_dt = datetime.strptime(from_time, "%H:%M")
            to_dt = datetime.strptime(to_time, "%H:%M")
            
            if from_dt >= to_dt:
                frappe.throw("From Time must be earlier than To Time")
        except ValueError:
            frappe.throw("Invalid time format. Please use HH:MM format")

    # Get location (optional field)
    location = data.get("location", "").strip() or None

    try:
        # Create the Interview document
        interview_doc = frappe.get_doc({
            "doctype": "Interview",
            "interview_round": data.interview_round,
            "job_applicant": data.job_applicant,
            "custom_interview_type": data.get("custom_interview_type") or None,
            "resume_link": data.get("resume_link"),
            "custom_meeting_link": data.get("meeting_link"),
            "custom_location": location,
            "status": status,
            "scheduled_on": data.scheduled_on,
            "from_time": from_time,
            "to_time": to_time,
            "notes": data.get("notes"),
        })
        
        # Add interviewers if provided
        if data.get("interviewers"):
            interviewers = json.loads(data.interviewers) if isinstance(data.interviewers, str) else data.interviewers
            for interviewer in interviewers:
                interview_doc.append("interview_details", {
                    "interviewer": interviewer
                })
        
        interview_doc.insert(ignore_permissions=False, ignore_links=True)  # CHANGED: True se False kiya, taaki Frappe ka internal permission engine bhi check kare (double-safety)
        frappe.db.commit()
        
        frappe.log(f"Created interview: {interview_doc.name}, status: {interview_doc.status}")
        return {
            "message": f"Interview {interview_doc.name} created successfully.",
            "doc": interview_doc.as_dict()
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Interview Creation Failed")
        frappe.throw(f"Failed to create interview due to a server error. Please contact support.")


@frappe.whitelist(allow_guest=True)
def get_interview_list():
    """Get list of all interviews"""
    try:

        # Site HR users can see only their own Interviews
        filters = {}

        from resume.api.permissions import is_site_hr_user

        if is_site_hr_user():
            filters["owner"] = frappe.session.user
        
        interviews = frappe.get_all(
            "Interview",
            filters=filters,
            fields=[
                "name",
                "interview_round",
                "custom_interview_type",
                "job_applicant",
                "resume_link",
                "custom_meeting_link",
                "custom_location",
                "status",
                "scheduled_on",
                "from_time",
                "to_time",
                "notes",
                "creation",
                "modified"
            ],
            order_by="scheduled_on desc"
        )
        
        # Get interviewers for each interview - FIXED
        for interview in interviews:
            try:
                interviewers = frappe.db.get_all(
                    "Interview Detail",
                    filters={"parent": interview.name},
                    fields=["interviewer"],
                    ignore_permissions=True
                )
                interview["interviewers"] = [i.interviewer for i in interviewers]
            except Exception as e:
                frappe.log_error(f"Error fetching interviewers for {interview.name}: {str(e)}")
                interview["interviewers"] = []
            
            # Map custom_meeting_link to meeting_link for frontend
            if "custom_meeting_link" in interview:
                interview["meeting_link"] = interview.get("custom_meeting_link")
            if "custom_location" in interview:
                interview["location"] = interview.get("custom_location")
        
        return {
            "message": "Interviews fetched successfully",
            "data": interviews
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Interview List Fetch Failed")
        frappe.throw("Failed to fetch interviews")


@frappe.whitelist(allow_guest=True)
def get_interview_details(interview_name):
    """Get details of a specific interview"""
    try:
        if not interview_name:
            frappe.throw("Interview name is required")
        
        interview = frappe.get_doc("Interview", interview_name)

        # Site HR users can access only their own Interview
        from resume.api.permissions import is_site_hr_user

        if is_site_hr_user() and interview.owner != frappe.session.user:
            frappe.throw(
                "You do not have permission to access this Interview.",
                title="Permission Denied"
            )
        
        # Get interviewers - FIXED
        try:
            interviewers = frappe.db.get_all(
                "Interview Detail",
                filters={"parent": interview_name},
                fields=["interviewer", "name"],
                ignore_permissions=True
            )
        except Exception as e:
            frappe.log_error(f"Error fetching interview details for {interview_name}: {str(e)}")
            interviewers = []
        
        interview_dict = interview.as_dict()
        interview_dict["interviewers"] = [i.interviewer for i in interviewers]
        
        # Map custom_meeting_link to meeting_link for frontend
        if hasattr(interview, 'custom_meeting_link'):
            interview_dict["meeting_link"] = interview.custom_meeting_link
        if hasattr(interview, 'custom_location'):
            interview_dict["location"] = interview.custom_location
        
        return {
            "message": "Interview details fetched successfully",
            "data": interview_dict
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Interview Details Fetch Failed")
        frappe.throw(f"Failed to fetch interview details: {str(e)}")


# @frappe.whitelist()  # CHANGED: allow_guest=True hataya — ye function Interview record write/update karta hai
# def update_interview_event():
#     """Update an existing interview"""
#     data = frappe.form_dict
#     frappe.log("Updating interview event: {data}".format(data=json.dumps(dict(data), indent=2)))

#     interview_name = data.get("name")
#     if not interview_name:
#         frappe.throw("Interview name is required for update")

#     # NEW: Permission check — dynamic Role Permissions Manager settings ke hisaab se.
#     if not frappe.has_permission("Interview", ptype="write", doc=interview_name):
#         frappe.throw("You do not have permission to update this Interview")

#     try:
#         interview_doc = frappe.get_doc("Interview", interview_name)

#         # Site HR users can update only their own Interview
#         from resume.api.permissions import is_site_hr_user

#         if is_site_hr_user() and interview_doc.owner != frappe.session.user:
#             frappe.throw(
#                 "You do not have permission to update this Interview.",
#                 title="Permission Denied"
#             )
        
#         # Update fields if provided
#         if data.get("interview_round"):
#             interview_doc.interview_round = data.interview_round
#         if data.get("job_applicant"):
#             interview_doc.job_applicant = data.job_applicant
#         if data.get("resume_link"):
#             interview_doc.resume_link = data.resume_link
#         if data.get("meeting_link"):
#             interview_doc.custom_meeting_link = data.meeting_link
#         if data.get("interview_type"):
#             interview_doc.custom_interview_type = data.interview_type      
#         if data.get("location"):
#             interview_doc.custom_location = data.location
#         if data.get("status"):
#             interview_doc.status = data.status
#         if data.get("scheduled_on"):
#             interview_doc.scheduled_on = data.scheduled_on
#         if data.get("from_time"):
#             interview_doc.from_time = data.from_time
#         if data.get("to_time"):
#             interview_doc.to_time = data.to_time
#         if data.get("notes"):
#             interview_doc.notes = data.notes
        
#         # Update interviewers if provided
#         if data.get("interviewers"):
#             interview_doc.interview_details = []
#             interviewers = json.loads(data.interviewers) if isinstance(data.interviewers, str) else data.interviewers
#             for interviewer in interviewers:
#                 interview_doc.append("interview_details", {
#                     "interviewer": interviewer
#                 })
        
#         interview_doc.save(ignore_permissions=False)  # CHANGED: True se False kiya, taaki Frappe ka internal permission engine bhi check kare (double-safety)
#         frappe.db.commit()
        
#         frappe.log(f"Updated interview: {interview_doc.name}")
#         return {
#             "message": f"Interview {interview_doc.name} updated successfully.",
#             "doc": interview_doc.as_dict()
#         }
        
#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), "Interview Update Failed")
#         frappe.throw(f"Failed to update interview: {str(e)}")

@frappe.whitelist()
def update_interview_event():
    """Update an existing interview"""
    data = frappe.form_dict
    frappe.log("Updating interview event: {data}".format(data=json.dumps(dict(data), indent=2)))

    interview_name = data.get("name")
    if not interview_name:
        frappe.throw("Interview name is required for update")

    if not frappe.has_permission("Interview", ptype="write", doc=interview_name):
        frappe.throw("You do not have permission to update this Interview")

    try:
        interview_doc = frappe.get_doc("Interview", interview_name)

        from resume.api.permissions import is_site_hr_user

        if is_site_hr_user() and interview_doc.owner != frappe.session.user:
            frappe.throw(
                "You do not have permission to update this Interview.",
                title="Permission Denied"
            )

        # Update fields if provided (excluding from_time/to_time — handled separately below)
        if data.get("interview_round"):
            interview_doc.interview_round = data.interview_round
        if data.get("job_applicant"):
            interview_doc.job_applicant = data.job_applicant
        if data.get("resume_link"):
            interview_doc.resume_link = data.resume_link
        if data.get("meeting_link"):
            interview_doc.custom_meeting_link = data.meeting_link
        if data.get("interview_type"):
            interview_doc.custom_interview_type = data.interview_type
        if data.get("location"):
            interview_doc.custom_location = data.location
        if data.get("status"):
            interview_doc.status = data.status
        if data.get("notes"):
            interview_doc.notes = data.notes

        # Update interviewers if provided
        if data.get("interviewers"):
            interview_doc.interview_details = []
            interviewers = json.loads(data.interviewers) if isinstance(data.interviewers, str) else data.interviewers
            for interviewer in interviewers:
                interview_doc.append("interview_details", {
                    "interviewer": interviewer
                })

        interview_doc.save(ignore_permissions=False)

        # 👇 NAYA BLOCK — scheduled_on/from_time/to_time "Set Only Once" restriction ki wajah se
        # normal doc.save() se change nahi hote, isliye direct DB update karo
        if data.get("scheduled_on"):
            frappe.db.set_value("Interview", interview_name, "scheduled_on", data.scheduled_on)
        if data.get("from_time"):
            frappe.db.set_value("Interview", interview_name, "from_time", data.from_time)
        if data.get("to_time"):
            frappe.db.set_value("Interview", interview_name, "to_time", data.to_time)

        frappe.db.commit()

        # Reload to return fresh data including the force-updated times
        interview_doc.reload()

        frappe.log(f"Updated interview: {interview_doc.name}")
        return {
            "message": f"Interview {interview_doc.name} updated successfully.",
            "doc": interview_doc.as_dict()
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Interview Update Failed")
        frappe.throw(f"Failed to update interview: {str(e)}")


@frappe.whitelist(allow_guest=True)
def get_job_applicants():
    """Get list of job applicants for dropdown"""
    try:

        # Site HR users can see only their own Job Applicants
        filters = {}

        from resume.api.permissions import is_site_hr_user

        if is_site_hr_user():
            filters["owner"] = frappe.session.user

        applicants = frappe.get_all(
            "Job Applicant",
            filters=filters,
            fields=["name", "applicant_name", "email_id"],
            order_by="creation desc"
        )
        
        return {
            "message": "Job applicants fetched successfully",
            "data": applicants
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Job Applicants Fetch Failed")
        frappe.throw("Failed to fetch job applicants")


@frappe.whitelist(allow_guest=True)
def get_interviewers():
    """Get list of available interviewers (users with interviewer role)"""
    try:
        interviewers = frappe.get_all(
            "User",
            filters={
                "enabled": 1,
                "name": ["!=", "Administrator"]
            },
            fields=["name", "full_name", "email"],
            order_by="full_name"
        )
        
        return {
            "message": "Interviewers fetched successfully",
            "data": interviewers
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Interviewers Fetch Failed")
        frappe.throw("Failed to fetch interviewers")


@frappe.whitelist()  # CHANGED: allow_guest=True hataya — ye function Interview record delete karta hai
def delete_interview(interview_name):
    """Delete an interview"""
    try:
        if not interview_name:
            frappe.throw("Interview name is required")

        # NEW: Permission check — dynamic Role Permissions Manager settings ke hisaab se.
        if not frappe.has_permission("Interview", ptype="delete", doc=interview_name):
            frappe.throw(
                "You do not have permission to delete this Interview.",
                title="Permission Denied"
            )

        # Site HR users can delete only their own Interview
        from resume.api.permissions import is_site_hr_user

        if is_site_hr_user():
            owner = frappe.db.get_value(
                "Interview",
                interview_name,
                "owner"
            )

            if owner != frappe.session.user:
                frappe.throw(
                    "You do not have permission to delete this Interview.",
                    title="Permission Denied"
                )
        
        frappe.delete_doc("Interview", interview_name, ignore_permissions=False)  # CHANGED: True se False kiya, taaki Frappe ka internal permission engine bhi check kare (double-safety)
        frappe.db.commit()
        
        return {
            "message": f"Interview {interview_name} deleted successfully"
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Interview Deletion Failed")
        frappe.throw(f"Failed to delete interview: {str(e)}")


@frappe.whitelist(allow_guest=True)
def get_interview_rounds():
    """Get list of interview rounds"""
    try:
        rounds = frappe.get_all(
            "Interview Round",
            fields=["name", "round_name"],
            order_by="name"
        )
        
        return {
            "message": "Interview rounds fetched successfully",
            "data": rounds
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Interview Rounds Fetch Failed")
        frappe.throw("Failed to fetch interview rounds")


@frappe.whitelist()  # CHANGED: allow_guest=True hataya — ye function Interview status write/update karta hai
def update_interview_status(interview_name, new_status):
    """Update interview status"""
    try:
        if not interview_name or not new_status:
            frappe.throw("Interview name and status are required")
        
        # Validate status
        valid_statuses = ["Pending", "Under Review", "Cleared", "Rejected"]
        if new_status not in valid_statuses:
            frappe.throw(f"Invalid status. Must be one of {', '.join(valid_statuses)}")

        # NEW: Permission check — dynamic Role Permissions Manager settings ke hisaab se.
        if not frappe.has_permission("Interview", ptype="write", doc=interview_name):
            frappe.throw(
                "You do not have permission to update this Interview.",
                title="Permission Denied"
            )
        
        interview_doc = frappe.get_doc("Interview", interview_name)

        # Site HR users can update status only for their own Interview
        from resume.api.permissions import is_site_hr_user

        if is_site_hr_user() and interview_doc.owner != frappe.session.user:
            frappe.throw(
                "You do not have permission to update this Interview.",
                title="Permission Denied"
            )

        interview_doc.status = new_status
        interview_doc.save(ignore_permissions=False)  # CHANGED: True se False kiya, taaki Frappe ka internal permission engine bhi check kare (double-safety)
        frappe.db.commit()
        
        frappe.log(f"Updated interview status: {interview_doc.name} to {new_status}")
        return {
            "message": f"Interview status updated to {new_status}",
            "data": interview_doc.as_dict()
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Interview Status Update Failed")
        frappe.throw(f"Failed to update interview status: {str(e)}")


@frappe.whitelist(allow_guest=True)
def get_existing_interview_for_round(job_applicant, interview_round):
    """Check if interview already exists for this applicant and round"""
    try:
        frappe.log(f"Checking for existing interview - Applicant: {job_applicant}, Round: {interview_round}")
        
        existing = frappe.db.get_value(
            "Interview",
            {
                "job_applicant": job_applicant,
                "interview_round": interview_round
            },
            ["name", "status", "scheduled_on", "from_time", "to_time"],
            as_dict=True
        )
        
        if existing:
            frappe.log(f"Found existing interview: {existing.name}")
            return {
                "exists": True,
                "interview": existing
            }
        
        frappe.log("No existing interview found")
        return {
            "exists": False,
            "interview": None
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Check Existing Interview Failed")
        return {
            "exists": False,
            "interview": None
        }


@frappe.whitelist(allow_guest=True)
def get_interview_type_options():
    """Get dynamic select options for custom_interview_type field"""
    try:
        meta = frappe.get_meta("Interview")
        field = next(
            (f for f in meta.fields if f.fieldname == "custom_interview_type"),
            None
        )
        if not field or not field.options:
            return {"message": "No options found", "data": []}

        options = [opt.strip() for opt in field.options.split("\n") if opt.strip()]
        return {
            "message": "Interview type options fetched successfully",
            "data": options
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Interview Type Options Fetch Failed")
        frappe.throw("Failed to fetch interview type options")
        