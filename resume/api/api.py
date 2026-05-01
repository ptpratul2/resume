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

@frappe.whitelist()
def generate_document_link(applicant_name):

    token = secrets.token_urlsafe(24)

    doc = frappe.get_doc(
        "Job Applicant",
        applicant_name
    )

    doc.custom_verification_token = token
    doc.save(ignore_permissions=True)

    frappe.db.commit()

    link = f"https://ats.octavision.in/document-verify/{token}"

    frappe.sendmail(
        recipients=[doc.email_id],
        subject="Upload Documents",
        message=f"""
            Hello {doc.applicant_name},<br><br>

            Please upload your documents using link below:<br><br>

            <a href="{link}">
                Upload Documents
            </a>
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

