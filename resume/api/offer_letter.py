import frappe
from datetime import datetime
import json
from frappe.model.workflow import apply_workflow, get_transitions, get_workflow_name, get_workflow_state_field

@frappe.whitelist(allow_guest=True)
def create_job_offer(data):
    """Create a new job offer"""
    try:
        import json
        if isinstance(data, str):
            data = json.loads(data)
        
        # Log the incoming data for debugging
        frappe.logger().info(f"Creating job offer with data: {data}")
        
        # Validate required fields
        required_fields = ["job_applicant", "applicant_name", "designation", "company", "status"]
        for field in required_fields:
            if not data.get(field):
                return {
                    "success": False,
                    "message": f"{field} is required"
                }

        # Validate status
        status = data.get("status")
        frappe.log(f"status received: {status}")
        # valid_statuses = ["Awaiting Response", "Accepted", "Rejected", "Pending"]
        # if not status or status not in valid_statuses:
        #     return {
        #         "success": False,
        #         "message": f"Invalid or missing status. Must be one of {', '.join(valid_statuses)}"
        #     }
        meta = frappe.get_meta("Job Offer")
        status_field = next((f for f in meta.fields if f.fieldname == "status"), None)
        valid_statuses = [s.strip() for s in status_field.options.split("\n") if s.strip()] if status_field else []
        if valid_statuses and status not in valid_statuses:
            return {
                "success": False,
                "message": f"Invalid status. Must be one of {', '.join(valid_statuses)}"
            }
                    # ✅ CHECK IF INTERVIEW IS SCHEDULED
        interviews = frappe.get_all(
            "Interview",
            filters={
                "job_applicant": data.get("job_applicant"),
                "docstatus": ["!=", 2]  # ignore cancelled interviews
            },
            fields=["name"],
            limit=1
        )

        if not interviews:
            return {
                "success": False,
                "message": "Cannot create Offer Letter. No interview has been scheduled for this candidate."
            }

        # Create the Job Offer document
        job_offer_doc = frappe.get_doc({
            "doctype": "Job Offer",
            "job_applicant": data.get("job_applicant"),
            "applicant_name": data.get("applicant_name"),
            "applicant_email": data.get("applicant_email", ""),
            "offer_date": data.get("offer_date", ""),
            "designation": data.get("designation"),
            "company": data.get("company"),
            "status": status,
            "job_offer_term_template": data.get("job_offer_template", ""),
            "custom_offer_acceptance_date": data.get("custom_offer_acceptance_date", ""),
            "custom_grade": data.get("custom_grade", ""),
            "custom_mobile_no": data.get("custom_mobile_no", ""),
            "custom_contact_name": data.get("custom_contact_name", ""),
            "custom_joining_date": data.get("custom_joining_date", ""),
            "custom_salary_annexure": data.get("custom_salary_annexure", ""),
            "custom_location_list": data.get("custom_location_list", ""),
            "custom_current_company": data.get("custom_current_company", ""),
            "custom_qualification": data.get("custom_qualification", ""),
            "custom_total_experience": data.get("custom_total_experience", ""),
            "custom_our_budget_in_ctc_only": data.get("custom_our_budget_in_ctc_only") or 0,
            "custom_current_ctc_of_candidate": data.get("custom_current_ctc_of_candidate") or 0,
            "custom_ctc_to_be_offered": data.get("custom_ctc_to_be_offered") or 0,
            "custom_interviewed_by_vaaman": data.get("custom_interviewed_by_vaaman", ""),
            "custom_interviewed_by_client": data.get("custom_interviewed_by_client", ""),
            "custom_replacementnew_position": data.get("custom_replacementnew_position", ""),
            "custom_source_of_hiring": data.get("custom_source_of_hiring", ""),
            "custom_background_verification_done_details": data.get("custom_background_verification_done_details", ""),
        })
        
        # Add job offer terms if provided
        terms_list = []
        offer_terms_data = data.get("offer_terms")
        
        # Handle if offer_terms is a JSON string
        if isinstance(offer_terms_data, str):
            try:
                offer_terms_data = json.loads(offer_terms_data)
            except:
                offer_terms_data = []
        
        if offer_terms_data and isinstance(offer_terms_data, list):
            for term in offer_terms_data:
                if term.get("offer_term") and term.get("value_description"):
                    job_offer_doc.append("offer_terms", {
                        "offer_term": term.get("offer_term"),
                        "value": term.get("value_description")
                    })
                    terms_list.append({
                        "offer_term": term.get("offer_term"),
                        "value": term.get("value_description")
                    })
        
        job_offer_doc.insert(ignore_permissions=True)
        frappe.db.commit()
        
        frappe.log(f"Created job offer: {job_offer_doc.name}, status: {job_offer_doc.status}")
        
        return {
            "success": True,
            "message": f"Job Offer {job_offer_doc.name} created successfully.",
            "data": {
                "name": job_offer_doc.name,
                "job_applicant": data.get("job_applicant"),
                "applicant_name": data.get("applicant_name"),
                "applicant_email": data.get("applicant_email", ""),
                "offer_date": data.get("offer_date", ""),
                "designation": data.get("designation"),
                "company": data.get("company"),
                "status": status,
                "job_offer_term_template": data.get("job_offer_template", ""),
                "custom_offer_acceptance_date": data.get("custom_offer_acceptance_date", ""),
                "custom_grade": data.get("custom_grade", ""),
                "custom_mobile_no": data.get("custom_mobile_no", ""),
                "custom_contact_name": data.get("custom_contact_name", ""),
                "custom_joining_date": data.get("custom_joining_date", ""),
                "custom_salary_annexure": data.get("custom_salary_annexure", ""),   
                "custom_location_list": data.get("custom_location_list", ""),
                "custom_current_company": data.get("custom_current_company", ""),
                "custom_qualification": data.get("custom_qualification", ""),
                "custom_total_experience": data.get("custom_total_experience", ""),
                "custom_our_budget_in_ctc_only": data.get("custom_our_budget_in_ctc_only") or 0,
                "custom_current_ctc_of_candidate": data.get("custom_current_ctc_of_candidate") or 0,
                "custom_ctc_to_be_offered": data.get("custom_ctc_to_be_offered") or 0,
                "custom_interviewed_by_vaaman": data.get("custom_interviewed_by_vaaman", ""),
                "custom_interviewed_by_client": data.get("custom_interviewed_by_client", ""),
                "custom_replacementnew_position": data.get("custom_replacementnew_position", ""),
                "custom_source_of_hiring": data.get("custom_source_of_hiring", ""),
                "custom_background_verification_done_details": data.get("custom_background_verification_done_details", ""),
                "offer_terms": terms_list
            }
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Job Offer Creation Failed")
        frappe.db.rollback()
        return {
            "success": False,
            "message": str(e)
        }


@frappe.whitelist(allow_guest=True)
def get_job_offer_list():
    """Get list of all job offers"""
    try:
        job_offers = frappe.get_all(
            "Job Offer",
            fields=[
                "name",
                "job_applicant",
                "applicant_name",
                "applicant_email",
                "offer_date",
                "designation",
                "company",
                "status",
                "job_offer_term_template",
                "custom_offer_acceptance_date",
                "custom_grade",
                "custom_mobile_no",
                "custom_contact_name",
                "custom_joining_date",
                "custom_location_list",
                "custom_current_company",
                "custom_qualification",
                "custom_total_experience",
                "custom_our_budget_in_ctc_only",
                "custom_current_ctc_of_candidate",
                "custom_ctc_to_be_offered",
                "custom_interviewed_by_vaaman",
                "custom_interviewed_by_client",
                "custom_replacementnew_position",
                "custom_source_of_hiring",
                "custom_background_verification_done_details",
                "workflow_state",
                "creation",
                "modified"
            ],
            order_by="creation desc"
        )
        
        # Get offer terms for each job offer
        for offer in job_offers:
            offer_terms = frappe.get_all(
                "Job Offer Term",
                filters={"parent": offer.name},
                fields=["offer_term", "value"]
            )
            offer["offer_terms"] = offer_terms
        
        return {
            "message": "Job offers fetched successfully",
            "data": job_offers
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Job Offer List Fetch Failed")
        frappe.throw("Failed to fetch job offers")


@frappe.whitelist(allow_guest=True)
def get_job_offer_details(job_offer_name):
    """Get details of a specific job offer"""
    try:
        if not job_offer_name:
            frappe.throw("Job offer name is required")
        
        job_offer = frappe.get_doc("Job Offer", job_offer_name)
        
        # Get offer terms
        offer_terms = frappe.get_all(
            "Job Offer Term",
            filters={"parent": job_offer_name},
            fields=["offer_term", "value", "name"]
        )
        
        job_offer_dict = job_offer.as_dict()
        job_offer_dict["offer_terms"] = offer_terms
        
        return {
            "message": "Job offer details fetched successfully",
            "data": job_offer_dict
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Job Offer Details Fetch Failed")
        frappe.throw(f"Failed to fetch job offer details: {str(e)}")


@frappe.whitelist(allow_guest=True)
def update_job_offer():
    """Update an existing job offer"""
    data = frappe.form_dict
    frappe.log("Updating job offer: {data}".format(data=json.dumps(dict(data), indent=2)))

    job_offer_name = data.get("name")
    if not job_offer_name:
        frappe.throw("Job offer name is required for update")

    try:
        job_offer_doc = frappe.get_doc("Job Offer", job_offer_name)
        
        # Update fields if provided
        if data.get("job_applicant"):
            job_offer_doc.job_applicant = data.job_applicant
        if data.get("applicant_name"):
            job_offer_doc.applicant_name = data.applicant_name
        if data.get("applicant_email"):
            job_offer_doc.applicant_email = data.applicant_email
        if data.get("offer_date"):
            job_offer_doc.offer_date = data.offer_date
        if data.get("designation"):
            job_offer_doc.designation = data.designation
        if data.get("company"):
            job_offer_doc.company = data.company
        if data.get("status"):
            job_offer_doc.status = data.status
        if data.get("job_offer_template"):
            job_offer_doc.job_offer_term_template = data.job_offer_template
        if data.get("custom_location_list"):
            job_offer_doc.custom_location_list = data.custom_location_list
        if data.get("custom_current_company"):
            job_offer_doc.custom_current_company = data.custom_current_company
        if data.get("custom_qualification"):
            job_offer_doc.custom_qualification = data.custom_qualification
        if data.get("custom_total_experience"):
            job_offer_doc.custom_total_experience = data.custom_total_experience
        if data.get("custom_our_budget_in_ctc_only"):
            job_offer_doc.custom_our_budget_in_ctc_only = data.custom_our_budget_in_ctc_only
        if data.get("custom_current_ctc_of_candidate"):
            job_offer_doc.custom_current_ctc_of_candidate = data.custom_current_ctc_of_candidate
        if data.get("custom_ctc_to_be_offered"):
            job_offer_doc.custom_ctc_to_be_offered = data.custom_ctc_to_be_offered
        if data.get("custom_interviewed_by_vaaman"):
            job_offer_doc.custom_interviewed_by_vaaman = data.custom_interviewed_by_vaaman
        if data.get("custom_interviewed_by_client"):
            job_offer_doc.custom_interviewed_by_client = data.custom_interviewed_by_client
        if data.get("custom_replacementnew_position"):
            job_offer_doc.custom_replacementnew_position = data.custom_replacementnew_position
        if data.get("custom_source_of_hiring"):
            job_offer_doc.custom_source_of_hiring = data.custom_source_of_hiring
        if data.get("custom_background_verification_done_details"):
            job_offer_doc.custom_background_verification_done_details = data.custom_background_verification_done_details   
        
        # Update offer terms if provided
        if data.get("offer_terms"):
            # Clear existing offer terms
            job_offer_doc.offer_terms = []
            
            offer_terms = json.loads(data.offer_terms) if isinstance(data.offer_terms, str) else data.offer_terms
            for term in offer_terms:
                if term.get("offer_term") and term.get("value_description"):
                    job_offer_doc.append("offer_terms", {
                        "offer_term": term.get("offer_term"),
                        "value": term.get("value_description")
                    })
        
        job_offer_doc.save(ignore_permissions=True)
        frappe.db.commit()
        
        frappe.log(f"Updated job offer: {job_offer_doc.name}")
        return {
            "message": f"Job Offer {job_offer_doc.name} updated successfully.",
            "doc": job_offer_doc.as_dict()
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Job Offer Update Failed")
        frappe.throw(f"Failed to update job offer: {str(e)}")


@frappe.whitelist(allow_guest=True)
def delete_job_offer(job_offer_name):
    """Delete a job offer"""
    try:
        if not job_offer_name:
            frappe.throw("Job offer name is required")
        
        frappe.delete_doc("Job Offer", job_offer_name, ignore_permissions=True)
        frappe.db.commit()
        
        return {
            "message": f"Job Offer {job_offer_name} deleted successfully"
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Job Offer Deletion Failed")
        frappe.throw(f"Failed to delete job offer: {str(e)}")


@frappe.whitelist(allow_guest=True)
def get_job_applicants():
    """Get list of job applicants for dropdown"""
    try:
        applicants = frappe.get_all(
            "Job Applicant",
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
def get_job_offer_templates():
    """Get list of job offer term templates"""
    try:
        # Try to get templates with error handling for different field names
        templates = frappe.get_all(
            "Job Offer Term Template",
            fields=["name"],
            order_by="name"
        )
        
        # Get the actual field names from meta
        if templates:
            # Try to get the template name field dynamically
            result = []
            for template in templates:
                try:
                    doc = frappe.get_doc("Job Offer Term Template", template.name)
                    result.append({
                        "name": doc.name,
                        "offer_term_template_name": doc.get("offer_term_template_name") or doc.name
                    })
                except:
                    result.append({
                        "name": template.name,
                        "offer_term_template_name": template.name
                    })
            
            return {
                "message": "Job offer templates fetched successfully",
                "data": result
            }
        
        return {
            "message": "Job offer templates fetched successfully",
            "data": []
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Job Offer Templates Fetch Failed")
        # Return empty list instead of throwing error
        return {
            "message": "No templates found",
            "data": []
        }


@frappe.whitelist(allow_guest=True)
def get_companies():
    """Get list of companies"""
    try:
        companies = frappe.get_all(
            "Company",
            fields=["name", "company_name"],
            order_by="name"
        )
        
        return {
            "message": "Companies fetched successfully",
            "data": companies
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Companies Fetch Failed")
        frappe.throw("Failed to fetch companies")


@frappe.whitelist(allow_guest=True)
def get_locations():
    """Get list of locations"""
    try:
        locations = frappe.get_all(
            "Location",
            filters={"is_group": 0},
            fields=["name"],
            order_by="name"
        )
        return {
            "message": "Locations fetched successfully",
            "data": locations
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Locations Fetch Failed")
        return {
            "message": "No locations found",
            "data": []
        }


@frappe.whitelist(allow_guest=True)
def get_designations():
    """Get list of designations"""
    try:
        designations = frappe.get_all(
            "Designation",
            fields=["name", "designation_name"],
            order_by="name"
        )
        
        return {
            "message": "Designations fetched successfully",
            "data": designations
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Designations Fetch Failed")
        frappe.throw("Failed to fetch designations")

@frappe.whitelist(allow_guest=True)
def get_template_terms(template_name):
    """Get offer terms from a template"""
    try:
        if not template_name:
            frappe.throw("Template name is required")

        template = frappe.get_doc("Job Offer Term Template", template_name)

        terms = []
        if hasattr(template, 'offer_terms'):
            for term in template.offer_terms:
                terms.append({
                    "offer_term": getattr(term, "offer_term", "") or getattr(term, "term", "") or getattr(term, "title", ""),
                    "value": getattr(term, "value", "") or getattr(term, "desc", "") or getattr(term, "description", "")
                })

        return {
            "message": "Template terms fetched successfully",
            "data": terms
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Template Terms Fetch Failed")
        return {
            "message": "No terms found",
            "data": []
        }

@frappe.whitelist(allow_guest=True)
def get_job_applicant_details(job_applicant_name):
    """Get job applicant details including designation and company"""
    try:
        if not job_applicant_name:
            frappe.throw("Job applicant name is required")
        
        # Get job applicant
        applicant = frappe.get_doc("Job Applicant", job_applicant_name)
        
        # Get designation from applicant
        designation = applicant.get("designation") or ""
        
        # Get company - try to get from job opening if linked
        company = ""
        if hasattr(applicant, "job_title") and applicant.job_title:
            # Try to get job opening
            try:
                job_opening = frappe.get_all(
                    "Job Opening",
                    filters={"name": applicant.job_title},
                    fields=["company"],
                    limit=1
                )
                if job_opening:
                    company = job_opening[0].get("company", "")
            except:
                pass
        
        # If still no company, try to get default company
        if not company:
            try:
                default_company = frappe.get_all(
                    "Company",
                    fields=["name"],
                    limit=1
                )
                if default_company:
                    company = default_company[0].get("name", "")
            except:
                pass
        
        return {
            "message": "Job applicant details fetched successfully",
            "data": {
                "name": applicant.name,
                "applicant_name": applicant.applicant_name,
                "email_id": applicant.email_id or "",
                "designation": designation,
                "company": company,
                "current_company": applicant.get("custom_current_company") or "",
                "qualification": applicant.get("highest_qualification") or "",
                "total_experience": applicant.get("custom_total_experience") or ""
            }
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Job Applicant Details Fetch Failed")
        frappe.throw(f"Failed to fetch job applicant details: {str(e)}")

@frappe.whitelist(allow_guest=True)
def get_employee_grades():
    """Get list of employee grades"""
    try:
        grades = frappe.get_all(
            "Employee Grade",
            fields=["name"],
            order_by="name"
        )
        return {
            "message": "Employee grades fetched successfully",
            "data": grades
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Employee Grades Fetch Failed")
        return {
            "message": "No grades found",
            "data": []
        }


@frappe.whitelist(allow_guest=True)
def check_existing_offer(job_applicant):
    """Check if an offer already exists for a job applicant"""
    try:
        if not job_applicant:
            return {
                "exists": False,
                "message": "Job applicant is required"
            }
        
        existing_offers = frappe.get_all(
            "Job Offer",
            filters={"job_applicant": job_applicant},
            fields=["name", "applicant_email", "status"],
            limit=1
        )
        
        if existing_offers:
            offer = existing_offers[0]
            return {
                "exists": True,
                "message": f"Job Offer '{offer['name']}' already exists for this applicant",
                "offer_name": offer['name'],
                "status": offer['status']
            }
        
        return {
            "exists": False,
            "message": "No existing offer found"
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Check Existing Offer Failed")
        return {
            "exists": False,
            "message": str(e)
        }


@frappe.whitelist(allow_guest=True)
def get_salary_annexures():
    """Get list of Salary Annexures"""
    try:
        annexures = frappe.get_all(
            "Salary Annexure",
            fields=["name"],
            order_by="name"
        )
        return {
            "message": "Salary Annexures fetched successfully",
            "data": annexures
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Salary Annexures Fetch Failed")
        return {
            "message": "No salary annexures found",
            "data": []
        }

@frappe.whitelist(allow_guest=True)
def get_job_offer_statuses():
    """Get valid statuses for Job Offer from Frappe meta"""
    try:
        meta = frappe.get_meta("Job Offer")
        status_field = next((f for f in meta.fields if f.fieldname == "status"), None)
        if status_field and status_field.options:
            statuses = [s.strip() for s in status_field.options.split("\n") if s.strip()]
        else:
            statuses = ["Awaiting Response", "Accepted", "Rejected"]
        return {"message": "Statuses fetched", "data": statuses}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Job Offer Statuses Fetch Failed")
        return {"message": "Error", "data": ["Awaiting Response", "Accepted", "Rejected"]}


@frappe.whitelist(allow_guest=True)
def update_job_offer_status():
    """Update only the status of a job offer"""
    # Works for both GET (query params) and POST (form data)
    job_offer_name = frappe.form_dict.get("name") or frappe.local.form_dict.get("name")
    new_status = frappe.form_dict.get("status") or frappe.local.form_dict.get("status")

    frappe.logger().info(f"[update_job_offer_status] name={job_offer_name}, status={new_status}")

    if not job_offer_name:
        return {"success": False, "message": "Job offer name is required"}
    if not new_status:
        return {"success": False, "message": "Status is required"}

    try:
        # Check if doc exists first
        if not frappe.db.exists("Job Offer", job_offer_name):
            return {"success": False, "message": f"Job Offer {job_offer_name} not found"}

        frappe.db.set_value("Job Offer", job_offer_name, "status", new_status, update_modified=True)
        frappe.db.commit()

        return {
            "message": f"Status updated to {new_status}",
            "success": True
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Job Offer Status Update Failed")
        # Return instead of throw so we get 200 with error detail
        return {"success": False, "message": str(e)}       


@frappe.whitelist(allow_guest=True)
def get_offer_workflow_actions(job_offer_name):
    """Get available workflow actions for the current user on this Job Offer"""
    try:
        if not job_offer_name:
            frappe.throw("Job offer name is required")

        doc = frappe.get_doc("Job Offer", job_offer_name)

        # Dynamically resolve the workflow state field configured on the Workflow doctype
        workflow_name = get_workflow_name(doc.doctype)
        state_field = get_workflow_state_field(workflow_name) if workflow_name else None
        current_state = doc.get(state_field) if state_field else None

        transitions = get_transitions(doc)
        actions = [t.get("action") for t in transitions]

        return {
            "message": "Workflow actions fetched",
            "data": {
                "workflow_name": workflow_name,
                "workflow_state_field": state_field,
                "workflow_state": current_state,
                "status": doc.get("status"),
                "actions": actions
            }
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Workflow Actions Failed")
        return {"message": "Error", "data": {"workflow_state": "", "actions": []}}

@frappe.whitelist(allow_guest=True)
def apply_offer_workflow_action():
    """Apply a workflow action (Approve / Reject / Review) to a Job Offer"""
    job_offer_name = frappe.form_dict.get("name") or frappe.local.form_dict.get("name")
    action = frappe.form_dict.get("action") or frappe.local.form_dict.get("action")

    if not job_offer_name:
        return {"success": False, "message": "Job offer name is required"}
    if not action:
        return {"success": False, "message": "Action is required"}

    try:
        doc = frappe.get_doc("Job Offer", job_offer_name)
        apply_workflow(doc, action)
        frappe.db.commit()

        # Dynamically resolve the workflow state field after the transition
        workflow_name = get_workflow_name(doc.doctype)
        state_field = get_workflow_state_field(workflow_name) if workflow_name else None
        current_state = doc.get(state_field) if state_field else None

        return {
            "success": True,
            "message": f"'{action}' applied successfully",
            "workflow_state": current_state,
            "status": doc.get("status")
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Apply Workflow Action Failed")
        frappe.db.rollback()
        return {"success": False, "message": str(e)}    
    