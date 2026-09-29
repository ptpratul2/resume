import frappe
import secrets

@frappe.whitelist(allow_guest=True)
def send_otp_email(email=None, otp=None):
    try:
        frappe.sendmail(
            recipients=[email],
            subject="OTP For Document Upload",
            message=f"""
                <h2>Your OTP is {otp}</h2>
                <p>Valid for 15 minutes</p>
            """,
            delayed=False
        )

        return {"success": True}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "OTP Email Error")
        frappe.throw(str(e))

# @frappe.whitelist()
# def generate_document_link(applicant_name):

#     token = secrets.token_urlsafe(24)

#     doc = frappe.get_doc(
#         "Job Applicant",
#         applicant_name
#     )

#     doc.custom_verification_token = token
#     doc.save(ignore_permissions=True)

#     frappe.db.commit()
#     host_name = frappe.conf.get("host_name")

#     link = f"{host_name}/document-verify/{token}"

#     sender = frappe.session.user

#     frappe.sendmail(
#         recipients=[doc.email_id],
#         sender=sender,
#         subject="Upload Documents",
#         message=f"""
#             Hello {doc.applicant_name},<br><br>

#             Please upload your documents using link below:<br><br>

#             <a href="{link}">
#                 Upload Documents
#             </a>
#         """,
#         delayed=False
#     )

#     return {"success": True}

@frappe.whitelist()
def generate_document_link(applicant_name):

    token = secrets.token_urlsafe(24)

    doc = frappe.get_doc(
        "Job Applicant",
        applicant_name
    )

    doc.custom_verification_token = token
    doc.save(ignore_permissions=True)

    # 👇 NAYI LINE — HR jo button click kar raha hai, usi ko "owner" bana do
    # db_set direct DB update karta hai, validation/save cycle trigger nahi hota
    frappe.db.set_value(
        "Job Applicant",
        applicant_name,
        "owner",
        frappe.session.user
    )

    frappe.db.commit()
    host_name = frappe.conf.get("host_name")

    link = f"{host_name}/document-verify/{token}"

    sender = frappe.session.user

    frappe.sendmail(
        recipients=[doc.email_id],
        sender=sender,
        subject="Upload Documents",
        message=f"""
            Hello {doc.applicant_name},<br><br>
            Please upload your documents using link below:<br><br>
            <a href="{link}">Upload Documents</a>
        """,
        delayed=False
    )

    return {"success": True}


@frappe.whitelist(allow_guest=True)
def verify_document_token(token):

    row = frappe.db.get_value(
        "Job Applicant",
        {"custom_verification_token": token},
        ["name", "email_id"],
        as_dict=True
    )

    if not row:
        return {"valid": False}

    return {
        "valid": True,
        "email": row.email_id,
        "name": row.name
    }

@frappe.whitelist()
def set_document_owner(doctype, name, owner):
    """Force-set the owner of a document.

    Used because REST API insert/update ignores the 'owner' field
    passed in payload and defaults to the API-key user.
    """

    allowed_doctypes = [
        "Applicant Document",
        "Application Form",
        "Application Declaration"
    ]

    if doctype not in allowed_doctypes:
        return {"success": False, "message": f"Doctype {doctype} not allowed"}

    if not frappe.db.exists(doctype, name):
        return {"success": False, "message": f"{doctype} {name} not found"}

    if not frappe.db.exists("User", owner):
        return {"success": False, "message": f"User {owner} not found"}

    frappe.db.set_value(doctype, name, "owner", owner)
    frappe.db.commit()

    return {"success": True}
