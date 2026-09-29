# import frappe
# from frappe import _
# from frappe.utils import now_datetime
# import json

# @frappe.whitelist()
# def get_applicant_document(name):
#     """Get Applicant Document details with linked data"""
#     try:
#         if not frappe.db.exists("Applicant Document", name):
#             return {
#                 "status": "error",
#                 "message": f"Applicant Document {name} not found"
#             }
        
#         doc = frappe.get_doc("Applicant Document", name)
        
#         applicant_data = {}
#         if doc.applicant_name:
#             applicant_data = frappe.db.get_value(
#                 "Job Applicant",
#                 doc.applicant_name,
#                 ["applicant_name", "email_id", "phone_number"],
#                 as_dict=True
#             ) or {}
        
#         employee_data = {}
#         if doc.employee:
#             employee_data = frappe.db.get_value(
#                 "Employee",
#                 doc.employee,
#                 ["employee_name", "personal_email", "cell_number"],
#                 as_dict=True
#             ) or {}
        
#         return {
#             "status": "success",
#             "data": {
#                 **doc.as_dict(),
#                 "applicant_details": applicant_data,
#                 "employee_details": employee_data
#             }
#         }
        
#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), "Get Applicant Document Error")
#         return {
#             "status": "error",
#             "message": str(e)
#         }


# @frappe.whitelist()
# def get_applicant_documents_list(filters=None, limit_start=0, limit_page_length=20):
#     """Get list of Applicant Documents with pagination"""
#     try:
#         filters_dict = json.loads(filters) if filters else {}
        
#         documents = frappe.get_all(
#             "Applicant Document",
#             filters=filters_dict,
#             fields=[
#                 "name", "applicant_name", "employee", "creation", "modified",
#                 "aadhar_card", "passport", "experience", "education",
#                 "bank_details", "pan", "medical", "photos",
#                 "custom_background_verification", "custom_salary_slip", 
#                 "custom_additional_document"
#             ],
#             start=int(limit_start),
#             page_length=int(limit_page_length),
#             order_by="creation desc"
#         )
        
#         for doc in documents:
#             if doc.applicant_name:
#                 applicant = frappe.db.get_value(
#                     "Job Applicant",
#                     doc.applicant_name,
#                     ["applicant_name", "email_id"],
#                     as_dict=True
#                 )
#                 doc["applicant_details"] = applicant or {}
            
#             if doc.employee:
#                 employee = frappe.db.get_value(
#                     "Employee",
#                     doc.employee,
#                     ["employee_name", "personal_email"],
#                     as_dict=True
#                 )
#                 doc["employee_details"] = employee or {}
        
#         return {
#             "status": "success",
#             "data": documents,
#             "total": frappe.db.count("Applicant Document", filters_dict)
#         }
        
#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), "Get Applicant Documents List Error")
#         return {
#             "status": "error",
#             "message": str(e)
#         }


# def delete_file_safely(file_url):
#     """Helper function to safely delete a file"""
#     if not file_url:
#         return
    
#     try:
#         file_doc = frappe.get_doc("File", {"file_url": file_url})
#         file_doc.delete(ignore_permissions=True)
#     except Exception as e:
#         frappe.log_error(f"Error deleting file {file_url}: {str(e)}", "File Deletion Error")


# def delete_multiple_files(field_value):
#     """Helper function to delete multiple files stored as JSON array"""
#     if not field_value:
#         return
    
#     try:
#         file_urls = json.loads(field_value)
#         if isinstance(file_urls, list):
#             for url in file_urls:
#                 delete_file_safely(url)
#         else:
#             delete_file_safely(field_value)
#     except json.JSONDecodeError:
#         delete_file_safely(field_value)


# @frappe.whitelist()
# def delete_applicant_document(name):
#     """Delete Applicant Document and associated files"""
#     try:
#         if not frappe.db.exists("Applicant Document", name):
#             return {
#                 "status": "error",
#                 "message": f"Applicant Document {name} not found"
#             }
        
#         doc = frappe.get_doc("Applicant Document", name)
        
#         single_file_fields = [
#             "aadhar_card", "passport", "experience", "education",
#             "bank_details", "pan", "medical", "photos"
#         ]
        
#         for field in single_file_fields:
#             file_url = doc.get(field)
#             delete_file_safely(file_url)
        
#         multiple_file_fields = [
#             "custom_background_verification",
#             "custom_salary_slip",
#             "custom_additional_document"
#         ]
        
#         for field in multiple_file_fields:
#             field_value = doc.get(field)
#             delete_multiple_files(field_value)
        
#         frappe.delete_doc("Applicant Document", name, ignore_permissions=True)
#         frappe.db.commit()
        
#         return {
#             "status": "success",
#             "message": "Applicant Document deleted successfully"
#         }
        
#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), "Delete Applicant Document Error")
#         return {
#             "status": "error",
#             "message": str(e)
#         }


# @frappe.whitelist()
# def update_applicant_document(name, data):
#     """Update existing Applicant Document with partial updates support"""
#     try:
#         if not frappe.db.exists("Applicant Document", name):
#             return {
#                 "status": "error",
#                 "message": f"Applicant Document {name} not found"
#             }
        
#         doc = frappe.get_doc("Applicant Document", name)
        
#         if isinstance(data, str):
#             data = json.loads(data)
        
#         if data.get("applicant_name"):
#             if not frappe.db.exists("Job Applicant", data["applicant_name"]):
#                 return {
#                     "status": "error",
#                     "message": f"Job Applicant {data['applicant_name']} does not exist"
#                 }
#             doc.applicant_name = data["applicant_name"]
        
#         if data.get("employee"):
#             if not frappe.db.exists("Employee", data["employee"]):
#                 return {
#                     "status": "error",
#                     "message": f"Employee {data['employee']} does not exist"
#                 }
#             doc.employee = data["employee"]
        
#         single_file_fields = [
#             "aadhar_card", "passport", "experience", "education",
#             "bank_details", "pan", "medical", "photos"
#         ]
        
#         for field in single_file_fields:
#             if field in data and data[field]:
#                 doc.set(field, data[field])
        
#         multiple_file_fields = [
#             "custom_background_verification",
#             "custom_salary_slip",
#             "custom_additional_document"
#         ]
        
#         for field in multiple_file_fields:
#             if field in data and data[field]:
#                 doc.set(field, data[field])
        
#         doc.save(ignore_permissions=True)
#         frappe.db.commit()
        
#         return {
#             "status": "success",
#             "message": "Applicant Document updated successfully",
#             "data": doc.as_dict()
#         }
        
#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), "Update Applicant Document Error")
#         return {
#             "status": "error",
#             "message": str(e)
#         }


# @frappe.whitelist()
# def get_applicant_document_by_applicant(applicant_name):
#     """Get Applicant Document by applicant name"""
#     try:
#         if not frappe.db.exists("Job Applicant", applicant_name):
#             return {
#                 "status": "error",
#                 "message": f"Job Applicant {applicant_name} not found"
#             }
        
#         doc_name = frappe.db.get_value(
#             "Applicant Document",
#             {"applicant_name": applicant_name},
#             "name"
#         )
        
#         if not doc_name:
#             return {
#                 "status": "success",
#                 "message": "No document found for this applicant",
#                 "data": None
#             }
        
#         doc = frappe.get_doc("Applicant Document", doc_name)
        
#         applicant_data = {}
#         if doc.applicant_name:
#             applicant_data = frappe.db.get_value(
#                 "Job Applicant",
#                 doc.applicant_name,
#                 ["applicant_name", "email_id", "phone_number"],
#                 as_dict=True
#             ) or {}
        
#         employee_data = {}
#         if doc.employee:
#             employee_data = frappe.db.get_value(
#                 "Employee",
#                 doc.employee,
#                 ["employee_name", "personal_email", "cell_number"],
#                 as_dict=True
#             ) or {}
        
#         return {
#             "status": "success",
#             "data": {
#                 **doc.as_dict(),
#                 "applicant_details": applicant_data,
#                 "employee_details": employee_data
#             }
#         }
        
#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), "Get Applicant Document By Applicant Error")
#         return {
#             "status": "error",
#             "message": str(e)
#         }


# @frappe.whitelist()
# def get_document_upload_status(applicant_name):
#     """Get upload status for all documents for a specific applicant"""
#     try:
#         if not frappe.db.exists("Job Applicant", applicant_name):
#             return {
#                 "status": "error",
#                 "message": f"Job Applicant {applicant_name} not found"
#             }
        
#         doc_name = frappe.db.get_value(
#             "Applicant Document",
#             {"applicant_name": applicant_name},
#             "name"
#         )
        
#         if not doc_name:
#             return {
#                 "status": "success",
#                 "message": "No documents uploaded yet",
#                 "uploaded": {},
#                 "missing": [
#                     "aadhar_card", "passport", "experience", "education",
#                     "bank_details", "pan", "medical", "photos",
#                     "custom_background_verification", "custom_salary_slip",
#                     "custom_additional_document"
#                 ],
#                 "upload_count": 0,
#                 "total_count": 11
#             }
        
#         doc = frappe.get_doc("Applicant Document", doc_name)
        
#         file_fields = [
#             "aadhar_card", "passport", "experience", "education",
#             "bank_details", "pan", "medical", "photos",
#             "custom_background_verification", "custom_salary_slip",
#             "custom_additional_document"
#         ]
        
#         uploaded = {}
#         missing = []
        
#         for field in file_fields:
#             value = doc.get(field)
#             if value:
#                 if field in ["custom_background_verification", "custom_salary_slip", "custom_additional_document"]:
#                     try:
#                         files = json.loads(value)
#                         if isinstance(files, list) and len(files) > 0:
#                             uploaded[field] = files
#                         else:
#                             missing.append(field)
#                     except:
#                         uploaded[field] = value
#                 else:
#                     uploaded[field] = value
#             else:
#                 missing.append(field)
        
#         return {
#             "status": "success",
#             "document_id": doc_name,
#             "uploaded": uploaded,
#             "missing": missing,
#             "upload_count": len(uploaded),
#             "total_count": len(file_fields)
#         }
        
#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), "Get Document Upload Status Error")
#         return {
#             "status": "error",
#             "message": str(e)
#         }   


# @frappe.whitelist()
# def get_feedback_applicants():
#     try:
#         # First let's see what fields actually exist
#         applicants = frappe.db.sql("""
#             SELECT 
#                 inf.job_applicant as name,
#                 ja.applicant_name as applicant_name,
#                 MAX(inf.creation) as latest_feedback
#             FROM `tabInterview Feedback` inf
#             INNER JOIN `tabJob Applicant` ja 
#                 ON ja.name = inf.job_applicant
#             WHERE inf.job_applicant IS NOT NULL
#             AND inf.job_applicant != ''
#             GROUP BY inf.job_applicant, ja.applicant_name
#             ORDER BY latest_feedback DESC
#         """, as_dict=True)

#         return {
#             "success": True,
#             "data": applicants
#         }

#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), "Get Feedback Applicants Error")
#         return {
#             "success": False,
#             "message": str(e)
#         }
    

import frappe
from frappe import _
from frappe.utils import now_datetime
import json

from resume.api.permissions import is_site_hr_user


def _check_site_hr_applicant_owner(applicant_name):
    """
    Site HR User / Site HR Manager can access only their own Job Applicant data.

    Important:
    Applicant Document is often created by Administrator through the
    candidate/public document-upload flow, so we check the OWNER of the
    linked Job Applicant instead of Applicant Document.owner.
    """

    if not is_site_hr_user():
        return

    if not applicant_name:
        frappe.throw(
            _("Applicant is required."),
            title=_("Permission Denied")
        )

    applicant_owner = frappe.db.get_value(
        "Job Applicant",
        applicant_name,
        "owner"
    )

    if applicant_owner != frappe.session.user:
        frappe.throw(
            _("You can access documents only for applicants created by your login."),
            title=_("Permission Denied")
        )


def _get_site_hr_applicant_names():
    """
    Return Job Applicants owned by current Site HR user.

    Other roles receive None so existing behaviour remains unchanged.
    """

    if not is_site_hr_user():
        return None

    return frappe.get_all(
        "Job Applicant",
        filters={
            "owner": frappe.session.user
        },
        pluck="name"
    )


@frappe.whitelist()
def get_applicant_document(name):
    """Get Applicant Document details with linked data"""

    try:
        if not frappe.db.exists("Applicant Document", name):
            return {
                "status": "error",
                "message": f"Applicant Document {name} not found"
            }

        doc = frappe.get_doc("Applicant Document", name)

        # Site HR can access only documents linked to their own Job Applicant
        _check_site_hr_applicant_owner(doc.applicant_name)

        applicant_data = {}

        if doc.applicant_name:
            applicant_data = frappe.db.get_value(
                "Job Applicant",
                doc.applicant_name,
                ["applicant_name", "email_id", "phone_number"],
                as_dict=True
            ) or {}

        employee_data = {}

        if doc.employee:
            employee_data = frappe.db.get_value(
                "Employee",
                doc.employee,
                ["employee_name", "personal_email", "cell_number"],
                as_dict=True
            ) or {}

        return {
            "status": "success",
            "data": {
                **doc.as_dict(),
                "applicant_details": applicant_data,
                "employee_details": employee_data
            }
        }

    except Exception as e:
        frappe.log_error(
            frappe.get_traceback(),
            "Get Applicant Document Error"
        )

        return {
            "status": "error",
            "message": str(e)
        }


@frappe.whitelist()
def get_applicant_documents_list(
    filters=None,
    limit_start=0,
    limit_page_length=20
):
    """Get list of Applicant Documents with pagination"""

    try:
        filters_dict = json.loads(filters) if filters else {}

        # ---------------------------------------------------------
        # SITE HR DATA ISOLATION
        #
        # Applicant Document.owner may be Administrator because
        # candidate uploads documents through public flow.
        #
        # Therefore filter through linked Job Applicant.owner.
        # ---------------------------------------------------------

        site_hr_applicants = _get_site_hr_applicant_names()

        if site_hr_applicants is not None:

            if not site_hr_applicants:
                return {
                    "status": "success",
                    "data": [],
                    "total": 0
                }

            filters_dict["applicant_name"] = [
                "in",
                site_hr_applicants
            ]

        documents = frappe.get_all(
            "Applicant Document",
            filters=filters_dict,
            fields=[
                "name",
                "applicant_name",
                "employee",
                "creation",
                "modified",
                "aadhar_card",
                "passport",
                "experience",
                "education",
                "bank_details",
                "pan",
                "medical",
                "photos",
                "custom_background_verification",
                "custom_salary_slip",
                "custom_additional_document"
            ],
            start=int(limit_start),
            page_length=int(limit_page_length),
            order_by="creation desc"
        )

        for doc in documents:

            if doc.applicant_name:
                applicant = frappe.db.get_value(
                    "Job Applicant",
                    doc.applicant_name,
                    ["applicant_name", "email_id"],
                    as_dict=True
                )

                doc["applicant_details"] = applicant or {}

            if doc.employee:
                employee = frappe.db.get_value(
                    "Employee",
                    doc.employee,
                    ["employee_name", "personal_email"],
                    as_dict=True
                )

                doc["employee_details"] = employee or {}

        return {
            "status": "success",
            "data": documents,
            "total": frappe.db.count(
                "Applicant Document",
                filters_dict
            )
        }

    except Exception as e:
        frappe.log_error(
            frappe.get_traceback(),
            "Get Applicant Documents List Error"
        )

        return {
            "status": "error",
            "message": str(e)
        }


def delete_file_safely(file_url):
    """Helper function to safely delete a file"""

    if not file_url:
        return

    try:
        file_doc = frappe.get_doc(
            "File",
            {"file_url": file_url}
        )

        file_doc.delete(ignore_permissions=True)

    except Exception as e:
        frappe.log_error(
            f"Error deleting file {file_url}: {str(e)}",
            "File Deletion Error"
        )


def delete_multiple_files(field_value):
    """Helper function to delete multiple files stored as JSON array"""

    if not field_value:
        return

    try:
        file_urls = json.loads(field_value)

        if isinstance(file_urls, list):

            for url in file_urls:
                delete_file_safely(url)

        else:
            delete_file_safely(field_value)

    except json.JSONDecodeError:
        delete_file_safely(field_value)


@frappe.whitelist()
def delete_applicant_document(name):
    """Delete Applicant Document and associated files"""

    try:
        if not frappe.db.exists("Applicant Document", name):
            return {
                "status": "error",
                "message": f"Applicant Document {name} not found"
            }

        doc = frappe.get_doc(
            "Applicant Document",
            name
        )

        # NEW: Permission check — dynamic Role Permissions Manager settings ke hisaab se.
        if not frappe.has_permission("Applicant Document", ptype="delete", doc=name):
            frappe.throw(_("You do not have permission to delete this Applicant Document"))

        # Site HR can delete only their own applicant's document
        _check_site_hr_applicant_owner(doc.applicant_name)

        single_file_fields = [
            "aadhar_card",
            "passport",
            "experience",
            "education",
            "bank_details",
            "pan",
            "medical",
            "photos"
        ]

        for field in single_file_fields:

            file_url = doc.get(field)

            delete_file_safely(file_url)

        multiple_file_fields = [
            "custom_background_verification",
            "custom_salary_slip",
            "custom_additional_document"
        ]

        for field in multiple_file_fields:

            field_value = doc.get(field)

            delete_multiple_files(field_value)

        frappe.delete_doc(
            "Applicant Document",
            name,
            ignore_permissions=False,  # CHANGED: True se False kiya, taaki Frappe ka internal permission engine bhi check kare (double-safety)
            force=True
        )

        frappe.db.commit()

        return {
            "status": "success",
            "message": "Applicant Document deleted successfully"
        }

    except Exception as e:
        frappe.log_error(
            frappe.get_traceback(),
            "Delete Applicant Document Error"
        )

        return {
            "status": "error",
            "message": str(e)
        }


@frappe.whitelist()
def update_applicant_document(name, data):
    """Update existing Applicant Document with partial updates support"""

    try:
        if not frappe.db.exists("Applicant Document", name):
            return {
                "status": "error",
                "message": f"Applicant Document {name} not found"
            }

        doc = frappe.get_doc(
            "Applicant Document",
            name
        )

        # NEW: Permission check — dynamic Role Permissions Manager settings ke hisaab se.
        if not frappe.has_permission("Applicant Document", ptype="write", doc=name):
            frappe.throw(_("You do not have permission to update this Applicant Document"))

        # Site HR can update only their own applicant's document
        _check_site_hr_applicant_owner(doc.applicant_name)

        if isinstance(data, str):
            data = json.loads(data)

        if data.get("applicant_name"):

            if not frappe.db.exists(
                "Job Applicant",
                data["applicant_name"]
            ):
                return {
                    "status": "error",
                    "message": (
                        f"Job Applicant "
                        f"{data['applicant_name']} does not exist"
                    )
                }

            # If applicant is changed, make sure the new applicant
            # also belongs to the current Site HR user.
            _check_site_hr_applicant_owner(
                data["applicant_name"]
            )

            doc.applicant_name = data["applicant_name"]

        if data.get("employee"):

            if not frappe.db.exists(
                "Employee",
                data["employee"]
            ):
                return {
                    "status": "error",
                    "message": (
                        f"Employee "
                        f"{data['employee']} does not exist"
                    )
                }

            doc.employee = data["employee"]

        single_file_fields = [
            "aadhar_card",
            "passport",
            "experience",
            "education",
            "bank_details",
            "pan",
            "medical",
            "photos"
        ]

        for field in single_file_fields:

            if field in data and data[field]:
                doc.set(
                    field,
                    data[field]
                )

        multiple_file_fields = [
            "custom_background_verification",
            "custom_salary_slip",
            "custom_additional_document"
        ]

        for field in multiple_file_fields:

            if field in data and data[field]:
                doc.set(
                    field,
                    data[field]
                )

        doc.save(ignore_permissions=False)  # CHANGED: True se False kiya, taaki Frappe ka internal permission engine bhi check kare (double-safety)

        frappe.db.commit()

        return {
            "status": "success",
            "message": "Applicant Document updated successfully",
            "data": doc.as_dict()
        }

    except Exception as e:
        frappe.log_error(
            frappe.get_traceback(),
            "Update Applicant Document Error"
        )

        return {
            "status": "error",
            "message": str(e)
        }


@frappe.whitelist()
def get_applicant_document_by_applicant(applicant_name):
    """Get Applicant Document by applicant name"""

    try:
        if not frappe.db.exists(
            "Job Applicant",
            applicant_name
        ):
            return {
                "status": "error",
                "message": (
                    f"Job Applicant "
                    f"{applicant_name} not found"
                )
            }

        # Site HR can access only their own applicant
        _check_site_hr_applicant_owner(applicant_name)

        doc_name = frappe.db.get_value(
            "Applicant Document",
            {
                "applicant_name": applicant_name
            },
            "name"
        )

        if not doc_name:
            return {
                "status": "success",
                "message": "No document found for this applicant",
                "data": None
            }

        doc = frappe.get_doc(
            "Applicant Document",
            doc_name
        )

        applicant_data = {}

        if doc.applicant_name:
            applicant_data = frappe.db.get_value(
                "Job Applicant",
                doc.applicant_name,
                [
                    "applicant_name",
                    "email_id",
                    "phone_number"
                ],
                as_dict=True
            ) or {}

        employee_data = {}

        if doc.employee:
            employee_data = frappe.db.get_value(
                "Employee",
                doc.employee,
                [
                    "employee_name",
                    "personal_email",
                    "cell_number"
                ],
                as_dict=True
            ) or {}

        return {
            "status": "success",
            "data": {
                **doc.as_dict(),
                "applicant_details": applicant_data,
                "employee_details": employee_data
            }
        }

    except Exception as e:
        frappe.log_error(
            frappe.get_traceback(),
            "Get Applicant Document By Applicant Error"
        )

        return {
            "status": "error",
            "message": str(e)
        }


@frappe.whitelist()
def get_document_upload_status(applicant_name):
    """Get upload status for all documents for a specific applicant"""

    try:
        if not frappe.db.exists(
            "Job Applicant",
            applicant_name
        ):
            return {
                "status": "error",
                "message": (
                    f"Job Applicant "
                    f"{applicant_name} not found"
                )
            }

        # Site HR can access only their own applicant
        _check_site_hr_applicant_owner(applicant_name)

        doc_name = frappe.db.get_value(
            "Applicant Document",
            {
                "applicant_name": applicant_name
            },
            "name"
        )

        if not doc_name:
            return {
                "status": "success",
                "message": "No documents uploaded yet",
                "uploaded": {},
                "missing": [
                    "aadhar_card",
                    "passport",
                    "experience",
                    "education",
                    "bank_details",
                    "pan",
                    "medical",
                    "photos",
                    "custom_background_verification",
                    "custom_salary_slip",
                    "custom_additional_document"
                ],
                "upload_count": 0,
                "total_count": 11
            }

        doc = frappe.get_doc(
            "Applicant Document",
            doc_name
        )

        file_fields = [
            "aadhar_card",
            "passport",
            "experience",
            "education",
            "bank_details",
            "pan",
            "medical",
            "photos",
            "custom_background_verification",
            "custom_salary_slip",
            "custom_additional_document"
        ]

        uploaded = {}
        missing = []

        for field in file_fields:

            value = doc.get(field)

            if value:

                if field in [
                    "custom_background_verification",
                    "custom_salary_slip",
                    "custom_additional_document"
                ]:

                    try:
                        files = json.loads(value)

                        if (
                            isinstance(files, list)
                            and len(files) > 0
                        ):
                            uploaded[field] = files
                        else:
                            missing.append(field)

                    except:
                        uploaded[field] = value

                else:
                    uploaded[field] = value

            else:
                missing.append(field)

        return {
            "status": "success",
            "document_id": doc_name,
            "uploaded": uploaded,
            "missing": missing,
            "upload_count": len(uploaded),
            "total_count": len(file_fields)
        }

    except Exception as e:
        frappe.log_error(
            frappe.get_traceback(),
            "Get Document Upload Status Error"
        )

        return {
            "status": "error",
            "message": str(e)
        }


@frappe.whitelist()
def get_feedback_applicants():

    try:

        # Site HR should see feedback applicants only for their own
        # Job Applicants.

        if is_site_hr_user():

            applicants = frappe.db.sql("""
                SELECT 
                    inf.job_applicant as name,
                    ja.applicant_name as applicant_name,
                    MAX(inf.creation) as latest_feedback
                FROM `tabInterview Feedback` inf
                INNER JOIN `tabJob Applicant` ja 
                    ON ja.name = inf.job_applicant
                WHERE inf.job_applicant IS NOT NULL
                AND inf.job_applicant != ''
                AND ja.owner = %s
                GROUP BY inf.job_applicant, ja.applicant_name
                ORDER BY latest_feedback DESC
            """, (
                frappe.session.user,
            ), as_dict=True)

        else:

            applicants = frappe.db.sql("""
                SELECT 
                    inf.job_applicant as name,
                    ja.applicant_name as applicant_name,
                    MAX(inf.creation) as latest_feedback
                FROM `tabInterview Feedback` inf
                INNER JOIN `tabJob Applicant` ja 
                    ON ja.name = inf.job_applicant
                WHERE inf.job_applicant IS NOT NULL
                AND inf.job_applicant != ''
                GROUP BY inf.job_applicant, ja.applicant_name
                ORDER BY latest_feedback DESC
            """, as_dict=True)

        return {
            "success": True,
            "data": applicants
        }

    except Exception as e:

        frappe.log_error(
            frappe.get_traceback(),
            "Get Feedback Applicants Error"
        )

        return {
            "success": False,
            "message": str(e)
        }


# @frappe.whitelist()
# def create_applicant_document(data):
#     """Create a new Applicant Document"""

#     try:
#         if isinstance(data, str):
#             data = json.loads(data)

#         applicant_name = data.get("applicant_name")

#         if not applicant_name:
#             return {
#                 "status": "error",
#                 "message": "Applicant Name is required"
#             }

#         if not frappe.db.exists("Job Applicant", applicant_name):
#             return {
#                 "status": "error",
#                 "message": f"Job Applicant {applicant_name} does not exist"
#             }

#         # ↓↓↓ YAHA ADD KARNA HAI — required-field aur existence checks ke baad,
#         #     lekin doc create karne se pehle
#         if not frappe.has_permission("Applicant Document", ptype="create"):
#             frappe.throw("You do not have permission to create Applicant Document")
#         # ↑↑↑ YAHA TAK

#         # Site HR can create a document only for their own applicant
#         _check_site_hr_applicant_owner(applicant_name)

#         doc_dict = {
#             "doctype": "Applicant Document",
#             "applicant_name": applicant_name,
#         }

#         if data.get("employee"):
#             if not frappe.db.exists("Employee", data["employee"]):
#                 return {
#                     "status": "error",
#                     "message": f"Employee {data['employee']} does not exist"
#                 }
#             doc_dict["employee"] = data["employee"]

#         single_file_fields = [
#             "aadhar_card", "passport", "experience", "education",
#             "bank_details", "pan", "medical", "photos"
#         ]
#         for field in single_file_fields:
#             if data.get(field):
#                 doc_dict[field] = data[field]

#         multiple_file_fields = [
#             "custom_background_verification",
#             "custom_salary_slip",
#             "custom_additional_document"
#         ]
#         for field in multiple_file_fields:
#             if data.get(field):
#                 doc_dict[field] = data[field]

#         doc = frappe.get_doc(doc_dict)
#         doc.insert(ignore_permissions=False)

#         frappe.db.commit()

#         return {
#             "status": "success",
#             "message": "Applicant Document created successfully",
#             "data": doc.as_dict()
#         }

#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), "Create Applicant Document Error")
#         frappe.db.rollback()
#         return {
#             "status": "error",
#             "message": str(e)
#         }

@frappe.whitelist()
def create_applicant_document(data):
    """Create a new Applicant Document"""

    try:
        if isinstance(data, str):
            data = json.loads(data)

        applicant_name = data.get("applicant_name")

        if not applicant_name:
            return {"status": "error", "message": "Applicant Name is required"}

        if not frappe.db.exists("Job Applicant", applicant_name):
            return {"status": "error", "message": f"Job Applicant {applicant_name} does not exist"}

        if not frappe.has_permission("Applicant Document", ptype="create"):
            frappe.throw("You do not have permission to create Applicant Document")

        _check_site_hr_applicant_owner(applicant_name)

        doc_dict = {
            "doctype": "Applicant Document",
            "applicant_name": applicant_name,
        }

        if data.get("employee"):
            if not frappe.db.exists("Employee", data["employee"]):
                return {"status": "error", "message": f"Employee {data['employee']} does not exist"}
            doc_dict["employee"] = data["employee"]

        single_file_fields = [
            "aadhar_card", "passport", "experience", "education",
            "bank_details", "pan", "medical", "photos"
        ]
        for field in single_file_fields:
            if data.get(field):
                doc_dict[field] = data[field]

        multiple_file_fields = [
            "custom_background_verification",
            "custom_salary_slip",
            "custom_additional_document"
        ]
        for field in multiple_file_fields:
            if data.get(field):
                doc_dict[field] = data[field]

        doc = frappe.get_doc(doc_dict)

        # 👇 NAYA BLOCK — Job Applicant ke sahi "owner" (HR jisne link bheja) ko
        # is naye Applicant Document ka owner bana do, warna insert Administrator/Guest
        # session se hoga toh owner automatically Administrator ban jayega
        applicant_owner = frappe.db.get_value(
            "Job Applicant", applicant_name, "owner"
        )
        if applicant_owner:
            doc.owner = applicant_owner

        doc.insert(ignore_permissions=False)

        frappe.db.commit()

        return {
            "status": "success",
            "message": "Applicant Document created successfully",
            "data": doc.as_dict()
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Create Applicant Document Error")
        frappe.db.rollback()
        return {"status": "error", "message": str(e)} 

       