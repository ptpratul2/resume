# import frappe
# from datetime import datetime, timezone
# import json

# @frappe.whitelist(allow_guest=True)
# def create_job_opening():
#     frappe.logger().info("=== CREATE JOB OPENING STARTED ===")
    
#     try:
#         # Step 1: Get data
#         frappe.logger().info("Step 1: Getting form data")
#         data = frappe.form_dict
#         frappe.logger().info(f"Received data: {json.dumps(dict(data), indent=2)}")

#         # Step 2: Validate required fields
#         frappe.logger().info("Step 2: Validating required fields")
#         if not data.get("job_title"):
#             frappe.logger().error("Validation failed: job_title missing")
#             return {"success": False, "message": "Job title is required"}
#         if not data.get("designation"):
#             frappe.logger().error("Validation failed: designation missing")
#             return {"success": False, "message": "Designation is required"}
#         if not data.get("company"):
#             frappe.logger().error("Validation failed: company missing")
#             return {"success": False, "message": "Company is required"}

#         # Step 3: Validate status
#         frappe.logger().info("Step 3: Validating status")
#         status = data.get("status", "Open")
#         valid_statuses = ["Open", "Closed", "On Hold"]
#         if status not in valid_statuses:
#             return {"success": False, "message": f"Invalid status. Must be one of {', '.join(valid_statuses)}"}

#         # Step 4: Process salary ranges
#         frappe.logger().info("Step 4: Processing salary ranges")
#         lower_range_final = None
#         upper_range_final = None
        
#         lower_range_val = data.get("lower_range")
#         upper_range_val = data.get("upper_range")
        
#         frappe.logger().info(f"Lower range: {lower_range_val}, Upper range: {upper_range_val}")

#         if lower_range_val and upper_range_val:
#             try:
#                 lower = float(lower_range_val)
#                 upper = float(upper_range_val)
                
#                 if lower <= 0 or upper <= 0:
#                     return {"success": False, "message": "Salary ranges must be positive numbers"}
#                 if lower >= upper:
#                     return {"success": False, "message": "Minimum salary must be less than maximum salary"}
                
#                 lower_range_final = lower
#                 upper_range_final = upper
#                 frappe.logger().info(f"Salary range processed: {lower_range_final} - {upper_range_final}")
#             except (ValueError, TypeError) as e:
#                 frappe.logger().error(f"Salary conversion error: {str(e)}")
#                 return {"success": False, "message": "Salary ranges must be valid numbers"}

#         # Step 5: Convert boolean values
#         frappe.logger().info("Step 5: Converting boolean values")
#         publish_salary = 1 if str(data.get("publish_salary_range")).lower() in ["true", "1"] else 0
#         publish_website = 1 if str(data.get("publish_on_website")).lower() in ["true", "1"] else 0
        
#         # Step 6: Parse dates
#         frappe.logger().info("Step 6: Parsing dates")
#         posted_on = data.get("posted_on") or datetime.now(timezone.utc).strftime("%Y-%m-%d")
#         closes_on = data.get("closes_on") if data.get("closes_on") else None
#         frappe.logger().info(f"Posted on: {posted_on}, Closes on: {closes_on}")
        
#         # Step 7: Get optional fields
#         frappe.logger().info("Step 7: Getting optional fields")
#         location = data.get("location", "").strip() or None
#         employment_type = data.get("employment_type", "").strip() or None
#         department = data.get("department", "").strip() or None
        
#         # Step 8: Create document dict
#         frappe.logger().info("Step 8: Creating document dictionary")
#         doc_dict = {
#             "doctype": "Job Opening",
#             "job_title": data.get("job_title"),
#             "designation": data.get("designation"),
#             "description": data.get("description", ""),
#             "currency": data.get("currency", "INR"),
#             "lower_range": lower_range_final,
#             "upper_range": upper_range_final,
#             "publish_salary_range": publish_salary,
#             "company": data.get("company"),
#             "employment_type": employment_type,
#             "department": department,
#             "location": location,
#             "publish_on_website": publish_website,
#             "posted_on": posted_on,
#             "closes_on": closes_on,
#             "status": status,
#             "salary_per": data.get("salary_per", "Month")
#         }
        
#         frappe.logger().info(f"Document dict created: {json.dumps(doc_dict, indent=2, default=str)}")
        
#         # Step 9: Create Job Opening document
#         frappe.logger().info("Step 9: Creating frappe document")
#         job_doc = frappe.get_doc(doc_dict)
        
#         # Step 10: Insert document
#         frappe.logger().info("Step 10: Inserting document")
#         job_doc.insert(ignore_permissions=True, ignore_links=True)
        
#         # Step 11: Commit
#         frappe.logger().info("Step 11: Committing to database")
#         frappe.db.commit()
        
#         frappe.logger().info(f"=== SUCCESS: Job Opening {job_doc.name} created ===")
        
#         return {
#             "success": True,
#             "message": f"Job Opening {job_doc.name} created successfully",
#             "data": {
#                 "name": job_doc.name,
#                 "job_title": job_doc.job_title
#             }
#         }
        
#     except Exception as e:
#         frappe.logger().error(f"=== ERROR OCCURRED ===")
#         frappe.logger().error(f"Error type: {type(e).__name__}")
#         frappe.logger().error(f"Error message: {str(e)}")
        
#         error_trace = frappe.get_traceback()
#         frappe.logger().error(f"Full traceback: {error_trace}")
        
#         frappe.db.rollback()
#         frappe.log_error(title="Job Opening Creation Error", message=error_trace)
        
#         return {
#             "success": False,
#             "message": f"Failed to create job opening: {str(e)}"
#         }








import frappe
from datetime import datetime, timezone
import json

@frappe.whitelist(allow_guest=True)
def create_job_opening():
    frappe.logger().info("=== CREATE JOB OPENING STARTED ===")
    
    try:
        # Step 1: Get data
        frappe.logger().info("Step 1: Getting form data")
        data = frappe.form_dict
        frappe.logger().info(f"Received data: {json.dumps(dict(data), indent=2)}")

        # Step 2: Validate required fields
        frappe.logger().info("Step 2: Validating required fields")
        if not data.get("job_title"):
            frappe.logger().error("Validation failed: job_title missing")
            return {"success": False, "message": "Job title is required"}
        if not data.get("designation"):
            frappe.logger().error("Validation failed: designation missing")
            return {"success": False, "message": "Designation is required"}
        if not data.get("company"):
            frappe.logger().error("Validation failed: company missing")
            return {"success": False, "message": "Company is required"}

        # Step 3: Validate status DYNAMICALLY
        frappe.logger().info("Step 3: Validating status")
        status = data.get("status", "Open")
        
        try:
            meta = frappe.get_meta("Job Opening")
            status_field = meta.get_field("status")
            
            if status_field and status_field.options:
                valid_statuses = [s.strip() for s in status_field.options.split('\n') if s.strip()]
            else:
                valid_statuses = ["Open", "Closed"]
            
            frappe.logger().info(f"Valid statuses from DocType: {valid_statuses}")
            
            if status not in valid_statuses:
                return {"success": False, "message": f"Invalid status. Must be one of {', '.join(valid_statuses)}"}
                
        except Exception as e:
            frappe.logger().error(f"Error getting status options: {str(e)}")
            if status not in ["Open", "Closed"]:
                return {"success": False, "message": "Invalid status"}

        # Step 4: Process salary ranges
        frappe.logger().info("Step 4: Processing salary ranges")
        lower_range_final = None
        upper_range_final = None
        
        lower_range_val = data.get("lower_range")
        upper_range_val = data.get("upper_range")
        
        frappe.logger().info(f"Lower range: {lower_range_val}, Upper range: {upper_range_val}")

        if lower_range_val and upper_range_val:
            try:
                lower = float(lower_range_val)
                upper = float(upper_range_val)
                
                if lower <= 0 or upper <= 0:
                    return {"success": False, "message": "Salary ranges must be positive numbers"}
                if lower >= upper:
                    return {"success": False, "message": "Minimum salary must be less than maximum salary"}
                
                lower_range_final = lower
                upper_range_final = upper
                frappe.logger().info(f"Salary range processed: {lower_range_final} - {upper_range_final}")
            except (ValueError, TypeError) as e:
                frappe.logger().error(f"Salary conversion error: {str(e)}")
                return {"success": False, "message": "Salary ranges must be valid numbers"}

        # Step 5: Convert boolean values
        frappe.logger().info("Step 5: Converting boolean values")
        publish_salary = 1 if str(data.get("publish_salary_range")).lower() in ["true", "1"] else 0
        publish_website = 1 if str(data.get("publish_on_website")).lower() in ["true", "1"] else 0
        
        # Step 6: Parse dates
        frappe.logger().info("Step 6: Parsing dates")
        posted_on = data.get("posted_on") or datetime.now(timezone.utc).strftime("%Y-%m-%d")
        closes_on = data.get("closes_on") if data.get("closes_on") else None
        frappe.logger().info(f"Posted on: {posted_on}, Closes on: {closes_on}")
        
        # Step 7: Get optional fields
        frappe.logger().info("Step 7: Getting optional fields")
        location = data.get("location", "").strip() or None
        employment_type = data.get("employment_type", "").strip() or None
        department = data.get("department", "").strip() or None
        
        # Step 8: Create document dict
        frappe.logger().info("Step 8: Creating document dictionary")
        doc_dict = {
            "doctype": "Job Opening",
            "job_title": data.get("job_title"),
            "designation": data.get("designation"),
            "description": data.get("description", ""),
            "currency": data.get("currency", "INR"),
            "lower_range": lower_range_final,
            "upper_range": upper_range_final,
            "publish_salary_range": publish_salary,
            "company": data.get("company"),
            "employment_type": employment_type,
            "department": department,
            "location": location,
            "publish_on_website": publish_website,
            "posted_on": posted_on,
            "closes_on": closes_on,
            "status": status,
            "salary_per": data.get("salary_per", "Month")
        }
        
        frappe.logger().info(f"Document dict created: {json.dumps(doc_dict, indent=2, default=str)}")
        
        # Step 9: Create Job Opening document
        frappe.logger().info("Step 9: Creating frappe document")
        job_doc = frappe.get_doc(doc_dict)
        
        # Step 10: Insert document
        frappe.logger().info("Step 10: Inserting document")
        job_doc.insert(ignore_permissions=True, ignore_links=True)
        
        # Step 11: Commit
        frappe.logger().info("Step 11: Committing to database")
        frappe.db.commit()
        
        frappe.logger().info(f"=== SUCCESS: Job Opening {job_doc.name} created ===")
        
        return {
            "success": True,
            "message": f"Job Opening {job_doc.name} created successfully",
            "data": {
                "name": job_doc.name,
                "job_title": job_doc.job_title
            }
        }
        
    except Exception as e:
        frappe.logger().error(f"=== ERROR OCCURRED ===")
        frappe.logger().error(f"Error type: {type(e).__name__}")
        frappe.logger().error(f"Error message: {str(e)}")
        
        error_trace = frappe.get_traceback()
        frappe.logger().error(f"Full traceback: {error_trace}")
        
        frappe.db.rollback()
        frappe.log_error(title="Job Opening Creation Error", message=error_trace)
        
        return {
            "success": False,
            "message": f"Failed to create job opening: {str(e)}"
        }
        

@frappe.whitelist()
def delete_job_opening(name):
    try:
        if not frappe.db.exists("Job Opening", name):
            return {"success": False, "message": "Job Opening not found"}

        # ─────────────────────────────────────────
        # STEP 1: Find correct Interview link field
        # ─────────────────────────────────────────
        try:
            # Check what fields Interview has that link to Job Opening
            interview_meta = frappe.get_meta("Interview")
            interview_link_fields = [
                f.fieldname for f in interview_meta.fields
                if f.fieldtype == "Link" and f.options == "Job Opening"
            ]
            frappe.logger().info(f"Interview link fields to Job Opening: {interview_link_fields}")
        except Exception as e:
            frappe.logger().error(f"Error getting Interview meta: {str(e)}")
            interview_link_fields = []

        # STEP 2: Check for linked Interviews using correct field
        linked_interviews = []
        for field in interview_link_fields:
            results = frappe.get_all(
                "Interview",
                filters={field: name},
                pluck="name"
            )
            linked_interviews.extend(results)

        # Remove duplicates
        linked_interviews = list(set(linked_interviews))

        if linked_interviews:
            return {
                "success": False,
                "message": f"Cannot delete. This Job Opening is linked with {len(linked_interviews)} Interview(s). Please delete them first."
            }

        # ─────────────────────────────────────────
        # STEP 3: Check for linked Job Applicants
        # ─────────────────────────────────────────
        try:
            applicant_meta = frappe.get_meta("Job Applicant")
            applicant_link_fields = [
                f.fieldname for f in applicant_meta.fields
                if f.fieldtype == "Link" and f.options == "Job Opening"
            ]
            frappe.logger().info(f"Job Applicant link fields to Job Opening: {applicant_link_fields}")
        except Exception as e:
            frappe.logger().error(f"Error getting Job Applicant meta: {str(e)}")
            applicant_link_fields = []

        linked_applicants = []
        for field in applicant_link_fields:
            results = frappe.get_all(
                "Job Applicant",
                filters={field: name},
                pluck="name"
            )
            linked_applicants.extend(results)

        linked_applicants = list(set(linked_applicants))

        if linked_applicants:
            return {
                "success": False,
                "message": f"Cannot delete. This Job Opening is linked with {len(linked_applicants)} Job Applicant(s). Please delete them first."
            }

        # ─────────────────────────────────────────
        # STEP 4: No links — safe to delete
        # ─────────────────────────────────────────
        frappe.delete_doc("Job Opening", name, ignore_permissions=True, force=True)
        frappe.db.commit()

        return {"success": True, "message": f"{name} deleted successfully"}

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(title="Delete Job Opening Error", message=frappe.get_traceback())
        return {"success": False, "message": str(e)}     


@frappe.whitelist(allow_guest=True)
def get_applicant_counts():
    try:
        counts = {}
        
        applicants = frappe.get_all(
            "Job Applicant",
            fields=["name", "job_title"],
            limit_page_length=0
        )
        
        for applicant in applicants:
            jo = applicant.get("job_title")
            if jo and str(jo).strip():
                counts[jo] = counts.get(jo, 0) + 1
                
        return {"success": True, "data": counts}
        
    except Exception as e:
        frappe.log_error(str(e), "get_applicant_counts")
        return {"success": False, "data": {}, "error": str(e)}

