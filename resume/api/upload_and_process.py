# apps/resume/resume/api/upload_and_process.py
import os
import uuid

import frappe
from frappe import _

from resume.resume.doctype.pdf_upload.pdf_upload import _extract_and_parse_file, extract_text_from_any_file, process_resume_pipeline
from vaaman_ats_ai.api.resume.resume import (
    create_resume_from_upload,
    calculate_experience_years,
    flatten_resume_data,
)

@frappe.whitelist()
def upload_and_process(job_opening=None):
    """
    Upload files (multipart/form-data 'files') and create Job Applicant records.
    Uses the same extract + Gemini pipeline as PDF Upload (supports .pdf, .doc, .docx, images, .txt).

    Expects:
      - files: multipart form files (one or many)
      - job_opening: name/ID of the Job Opening (optional)
    Returns:
      JSON with message of created count or raises a frappe exception on fatal errors.
    """
    try:
        frappe.local.flags.ignore_csrf = True
    except Exception:
        pass

    if not job_opening:
        job_opening = frappe.form_dict.get("job_opening")
        
    # ✅ ADD THIS HERE 👇
    is_data_bank = frappe.form_dict.get("is_data_bank") == "1"

    job_doc = None
    job_title_for_ai = None
    job_desc_for_ai = None
    if job_opening:
        try:
            job_doc = frappe.get_doc("Job Opening", job_opening)
            if job_doc.get("status") == "Closed":
                frappe.throw(
                    _(
                        "This Job Opening is closed. Reopen it or use an active Job Opening before uploading resumes."
                    ),
                    title=_("Job Opening is closed"),
                )
            job_title_for_ai = job_doc.get("job_title") or job_opening
            job_desc_for_ai = job_doc.get("description")
        except frappe.exceptions.ValidationError:
            raise
        except Exception:
            frappe.log_error(
                message=f"Could not load Job Opening {job_opening}",
                title="upload_and_process: Job Opening lookup failed",
            )

    api_key = frappe.conf.get("gemini_api_key")
    if not api_key:
        frappe.throw(
            _("Gemini API key is not configured. Set <code>gemini_api_key</code> in site_config.json.")
        )

    prompt_path = frappe.get_app_path("resume", "resume", "doctype", "pdf_upload", "resume_prompt.txt")
    with open(prompt_path, "r") as f:
        prompt_template = f.read()

    try:
        files = []
        try:
            files = frappe.request.files.getlist("files")
        except Exception:
            f = frappe.request.files.get("files")
            if f:
                files = [f]

        if not files:
            frappe.throw("No files uploaded. Please upload at least one file as the 'files' field.")

        created = 0

        for file_storage in files:
            filename_orig = getattr(file_storage, "filename", None) or "uploaded_file"
            filename = f"{uuid.uuid4().hex}_{filename_orig}"
            dest_dir = frappe.get_site_path("private", "files")
            os.makedirs(dest_dir, exist_ok=True)
            file_path = os.path.join(dest_dir, filename)

            try:
                with open(file_path, "wb") as f:
                    try:
                        f.write(file_storage.stream.read())
                    except Exception:
                        file_storage.seek(0)
                        f.write(file_storage.read())
            except Exception as e:
                frappe.log_error(
                    message=f"Failed to save uploaded file {filename_orig}: {e}",
                    title="upload_and_process: file save error",
                )
                continue

            file_url = f"/private/files/{filename}"
            ext = os.path.splitext(file_path)[1].lower()

            args = (
                file_path,
                file_url,
                job_title_for_ai,
                job_desc_for_ai,
                ext,
                api_key,
                prompt_template,
            )
            _fu, applicant_data, err = _extract_and_parse_file(args)
            # applicant_data = extract_text_from_any_file(file_path)
            
            # applicant_data = process_resume_pipeline(
            #     file_path=file_path,
            #     job_title=job_title_for_ai,
            #     job_desc=job_desc_for_ai
            # )

            # err = None if applicant_data else "Parsing failed"
            
            # if is_data_bank:
                # _fu, applicant_data, err = _extract_and_parse_file(args)
                # text = extract_text_from_any_file(file_path)
                # applicant_data = text   # raw text
                # err = None
            # else:
                # applicant_data = extract_text_from_any_file(file_path)
                # _fu, applicant_data, err = _extract_and_parse_file(args)
                # text = extract_text_from_any_file(file_path)
                # applicant_data = text   # raw text
                # err = None
                
            # 🔥 FIX HERE
            if isinstance(applicant_data, str):
                import json
                try:
                    applicant_data = json.loads(applicant_data)
                except:
                    continue
            # frappe.log_error(
            #         message=f"applicant_data:",
            #         title=applicant_data,
            #     )
            
            import json
            frappe.log_error(
                message=json.dumps(applicant_data, indent=2) if applicant_data else "No applicant data",
                title="Applicant Data Log"
            )
            if err or not applicant_data:
                frappe.log_error(
                    message=f"Parse failed for {filename_orig}: {err or 'empty result'}",
                    title="upload_and_process: parse failed",
                )
                continue
            
            # 🔥 Your integration (SAFE)
            # try:
            #     applicant_data["experience_years"] = calculate_experience_years(applicant_data.get("experience", []))
            #     create_resume_from_upload(
            #         applicant_data=applicant_data,
            #         file_url=file_url,
            #         job_opening=job_opening
            #     )
                
            # except Exception as e:
            #     frappe.log_error(
            #         message=f"Resume creation failed: {e}",
            #         title="Resume Integration Error"
            #     )

            if "email_id" in applicant_data and "email" not in applicant_data:
                applicant_data["email"] = applicant_data["email_id"]
            if "email" in applicant_data and "email_id" not in applicant_data:
                applicant_data["email_id"] = applicant_data["email"]

            if "phone_number" in applicant_data and "phone" not in applicant_data:
                applicant_data["phone"] = applicant_data["phone_number"]
            if "phone" in applicant_data and "phone_number" not in applicant_data:
                applicant_data["phone_number"] = applicant_data["phone"]

            applicant_name = applicant_data.get("applicant_name") or applicant_data.get("name") or applicant_data.get("full_name")
            email_value = applicant_data.get("email") or applicant_data.get("email_id")

            # if not applicant_name or not email_value:
            if not is_data_bank and (not applicant_name or not email_value):
                frappe.log_error(
                    message=f"Missing required applicant info (name/email) for {filename_orig}: keys={list(applicant_data.keys())}",
                    title="upload_and_process: missing data",
                )
                continue

            try:
                exists_filters = {"email_id": email_value}
                if job_opening:
                    exists_filters["job_title"] = job_opening
                if frappe.db.exists("Job Applicant", exists_filters):
                    frappe.log_error(
                        message=f"Duplicate applicant for email {email_value} and job {job_opening}",
                        title="upload_and_process: duplicate",
                    )
                    continue
            except Exception as e:
                frappe.log_error(
                    message=f"Error checking duplicates for {email_value}: {e}",
                    title="upload_and_process: duplicate check failed",
                )
            
            applicant_data["experience_years"] = calculate_experience_years(applicant_data.get("experience", []))
            # ✅ Flatten data (reuse your logic)
            flat_data = flatten_resume_data(applicant_data)
            
            # ✅ sanitize fit_level BEFORE insert
            allowed_fit_levels = ["", "Strong Fit", "Moderate Fit", "Weak Fit"]

            fit_level = applicant_data.get("fit_level", "")

            if fit_level not in allowed_fit_levels:
                fit_level = ""

            try:
                applicant_doc = {
                    "doctype": "Job Applicant",
                    "applicant_name": applicant_name,
                    "email_id": email_value,
                    "resume_attachment": file_url,
                    "status": "Open",
                    "phone_number": applicant_data.get("phone_number") or applicant_data.get("phone") or "",
                    "applicant_rating": applicant_data.get("applicant_rating") or applicant_data.get("rating") or 0,
                    "score": applicant_data.get("score"),
                    # "fit_level": applicant_data.get("fit_level"),
                    "fit_level": fit_level,
                    "justification_by_ai": applicant_data.get("justification_by_ai", ""),
                    "custom_parsed_json": json.dumps(applicant_data),
                    "custom_parse_status": "Parsed",
                    "custom_experience_years": flat_data["experience_years"],
                    # "custom_location": flat_data["location"],
                    "current_location": flat_data["location"],
                    "custom_skills": flat_data["skills"],
                    "custom_current_role": flat_data["current_role"],
                    "custom_degree": flat_data["degree"],
                    "custom_institution": flat_data["institution"],
                }

                if job_opening:
                    applicant_doc["job_title"] = job_opening

                applicant = frappe.get_doc(applicant_doc)
                applicant.insert(ignore_permissions=True)
                created += 1
                try:
                    create_resume_from_upload(
                        applicant_data=applicant_data,
                        file_url=file_url,
                        job_opening=job_opening,
                        applicant_doc=applicant
                    )
                    
                except Exception as e:
                    frappe.log_error(
                        message=f"Resume creation failed: {e}",
                        title="Resume Integration Error"
                    )
                frappe.logger().info(f"Created Job Applicant {email_value} from {filename_orig}")
            except Exception as e:
                frappe.log_error(
                    message=f"Failed to insert Job Applicant for {filename_orig} ({email_value}): {e}",
                    title="upload_and_process: insert failed",
                )
                continue

        return {"message": f"{created} Job Applicant(s) created."}

    except Exception as e:
        frappe.log_error(message=f"Resume upload failed: {e}", title="upload_and_process: critical")
        frappe.throw("Resume upload failed. See error logs.")
