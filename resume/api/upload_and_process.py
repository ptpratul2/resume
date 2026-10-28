# import os
# import json

# import frappe
# from frappe import _
# from frappe.utils.password import get_decrypted_password
# import re

# from resume.api.parse_guards import (
#     applicant_exists_for_job,
#     should_skip_file_for_job,
# )
# from resume.resume.doctype.pdf_upload.pdf_upload import _extract_and_parse_file

# try:
#     from vaaman_ats_ai.api.resume.resume import create_resume_from_upload
# except ImportError:
#     def create_resume_from_upload(applicant_data, file_url, job_opening=None, applicant_doc=None):
#         pass


# # ---------------------------------------------------------------------------
# # Inline helpers (replaced vaaman_ats_ai dependency)
# # ---------------------------------------------------------------------------

# def calculate_experience_years(experience_list):
#     if not experience_list:
#         return 0
#     total_months = 0
#     for exp in experience_list:
#         try:
#             from_date = exp.get("from_date") or exp.get("start_date") or ""
#             to_date   = exp.get("to_date")   or exp.get("end_date")   or "Present"
#             if not from_date:
#                 continue
#             from datetime import datetime
#             start = datetime.strptime(from_date[:10], "%Y-%m-%d")
#             end   = datetime.now() if (to_date in ("Present", "") or not to_date) else datetime.strptime(to_date[:10], "%Y-%m-%d")
#             total_months += max(0, (end.year - start.year) * 12 + (end.month - start.month))
#         except Exception:
#             continue
#     return round(total_months / 12, 1)


# def flatten_resume_data(applicant_data):
#     experience = applicant_data.get("experience") or []
#     education  = applicant_data.get("education")  or []
#     skills     = applicant_data.get("skills")     or []

#     current_role    = (experience[0].get("title")        or experience[0].get("position")     or "") if experience else ""
#     current_company = (experience[0].get("company_name") or experience[0].get("company")      or "") if experience else ""
#     degree          = (education[0].get("degree")        or education[0].get("qualification") or "") if education  else ""
#     institution     = (education[0].get("institution")   or education[0].get("college")       or "") if education  else ""

#     if isinstance(skills, list):
#         skills_str = ", ".join(s if isinstance(s, str) else s.get("skill", "") for s in skills)
#     else:
#         skills_str = str(skills)

#     return {
#         "experience_years": calculate_experience_years(experience),
#         "location":         applicant_data.get("location") or applicant_data.get("current_location") or applicant_data.get("city") or "",
#         "skills":           skills_str,
#         "current_role":     current_role,
#         "current_company":  current_company,
#         "degree":           degree,
#         "institution":      institution,
#     }


# def clean_phone_numbers(phone):
#     if not phone:
#         return "", ""

#     if isinstance(phone, list):
#         normalized = []

#         for p in phone:
#             if isinstance(p, dict):
#                 normalized.append(
#                     str(
#                         p.get("phone")
#                         or p.get("number")
#                         or p.get("value")
#                         or ""
#                     )
#                 )
#             else:
#                 normalized.append(str(p or ""))

#         phone = ",".join(normalized)

#     numbers = re.split(r"[,\n;/]+", str(phone))

#     valid_numbers = []

#     for num in numbers:
#         num = num.strip()

#         num = re.sub(r"[^\d+]", "", num)

#         if len(re.sub(r"\D", "", num)) >= 10:
#             if num not in valid_numbers:
#                 valid_numbers.append(num)

#     first_number = valid_numbers[0] if valid_numbers else ""
#     remaining_numbers = ", ".join(valid_numbers[1:]) if len(valid_numbers) > 1 else ""

#     return first_number, remaining_numbers


# def _normalize_scalar(value):
#     if value is None:
#         return ""

#     if isinstance(value, (list, dict)):
#         return json.dumps(value)

#     return str(value)


# # ---------------------------------------------------------------------------
# # Main API
# # ---------------------------------------------------------------------------

# @frappe.whitelist()
# def upload_and_process(job_opening=None):
#     try:
#         frappe.local.flags.ignore_csrf = True
#     except Exception:
#         pass

#     if not job_opening:
#         job_opening = frappe.form_dict.get("job_opening")

#     is_data_bank = frappe.form_dict.get("is_data_bank") == "1"

#     job_title_for_ai = None
#     job_desc_for_ai  = None

#     if job_opening:
#         try:
#             job_doc = frappe.get_doc("Job Opening", job_opening)
#             if job_doc.get("status") == "Closed":
#                 frappe.throw(_("This Job Opening is closed."), title=_("Job Opening is closed"))
#             job_title_for_ai = job_doc.get("job_title") or job_opening
#             job_desc_for_ai  = job_doc.get("description")
#         except frappe.exceptions.ValidationError:
#             raise
#         except Exception:
#             frappe.log_error(message=f"Could not load Job Opening {job_opening}", title="upload_and_process: Job Opening lookup failed")

#     api_key = (
#         get_decrypted_password("ATS Settings", "ATS Settings", "gemini_api_key", raise_exception=False)
#         or frappe.conf.get("gemini_api_key")
#     )
#     if not api_key:
#         frappe.throw(_("Gemini API key is not configured."))

#     prompt_path = frappe.get_app_path("resume", "resume", "doctype", "pdf_upload", "resume_prompt.txt")
#     with open(prompt_path, "r") as f:
#         prompt_template = f.read()

#     # Collect files
#     files = []
#     try:
#         files = frappe.request.files.getlist("files")
#     except Exception:
#         f = frappe.request.files.get("files")
#         if f:
#             files = [f]

#     if not files:
#         frappe.throw("No files uploaded.")

#     # Tracking
#     created      = 0
#     total_files  = 0
#     parsed_count = 0
#     log_entries  = []

#     for file_storage in files:
#         filename_orig = getattr(file_storage, "filename", None) or "uploaded_file"
#         total_files  += 1
#         frappe.log_error(
#              f"Processing {filename_orig}",
#              "Resume Upload Debug"
#              )

#         # Save file
#         try:
#             try:
#                 file_content = file_storage.stream.read()
#             except Exception:
#                 file_storage.seek(0)
#                 file_content = file_storage.read()

#             saved_file = frappe.get_doc({
#                 "doctype": "File", "file_name": filename_orig,
#                 "content": file_content, "is_private": 1,
#             })
#             saved_file.insert(ignore_permissions=True)
#             frappe.log_error(
#     f"Saved {filename_orig}",
#     "Resume Upload Debug"
# )
#             file_url  = saved_file.file_url
#             file_path = saved_file.get_full_path()
#         except Exception as e:
#             frappe.log_error(message=f"File save failed {filename_orig}: {e}", title="upload_and_process: file save error")
#             log_entries.append({"file_name": filename_orig, "applicant_name": "", "email_id": "", "status": "Failed", "error_message": f"Could not save file: {str(e)[:400]}", "job_applicant": ""})
#             continue

#         if job_opening and should_skip_file_for_job(
#             file_url, saved_file.content_hash, job_opening
#         ):
#             log_entries.append({
#                 "file_name":      filename_orig,
#                 "applicant_name": "",
#                 "email_id":       "",
#                 "status":         "Skipped",
#                 "error_message":  "File already imported for this job opening",
#                 "full_error":     "",
#                 "parsed_json":    "",
#                 "job_applicant":  "",
#             })
#             continue

#         # Parse
#         ext  = os.path.splitext(file_path)[1].lower()
#         args = (file_path, file_url, job_title_for_ai, job_desc_for_ai, ext, api_key, prompt_template)

#         try:
#             _fu, _fname, applicant_data, err = _extract_and_parse_file(args)
#         except Exception as parse_exc:
#             err = str(parse_exc)
#             applicant_data = None

#         if isinstance(applicant_data, str):
#             try:
#                 applicant_data = json.loads(applicant_data)
#             except Exception:
#                 applicant_data = None

#         if err or not applicant_data:
#             frappe.log_error(message=f"Parse failed for {filename_orig}: {err or 'empty'}", title="upload_and_process: parse failed")
#             log_entries.append({
#                 "file_name":      filename_orig,
#                 "applicant_name": "",
#                 "email_id":       "",
#                 "status":         "Parse Error",
#                 "error_message":  str(err or "Empty result from AI")[:500],
#                 "full_error":     str(err or ""),        # full error no truncation
#                 "parsed_json":    "",                    # nothing parsed
#                 "job_applicant":  "",
#             })
#             continue

#         parsed_count += 1

#         # Normalise keys
#         for a, b in [("email_id", "email"), ("email", "email_id"), ("phone_number", "phone"), ("phone", "phone_number")]:
#             if a in applicant_data and b not in applicant_data:
#                 applicant_data[b] = applicant_data[a]

#         applicant_name = applicant_data.get("applicant_name") or applicant_data.get("name") or applicant_data.get("full_name")
#         email_value    = applicant_data.get("email") or applicant_data.get("email_id")

#         # Missing data
#         if not is_data_bank and (not applicant_name or not email_value):
#             frappe.log_error(message=f"Missing name/email for {filename_orig}", title="upload_and_process: missing data")
#             log_entries.append({
#                 "file_name":      filename_orig,
#                 "applicant_name": applicant_name or "",
#                 "email_id":       email_value or "",
#                 "status":         "Missing Data",
#                 "error_message":  "AI did not return candidate name or email.",
#                 "full_error":     "AI did not return candidate name or email.",
#                 "parsed_json":    json.dumps(applicant_data, indent=2) if applicant_data else "",
#                 "job_applicant":  "",
#             })
#             continue

#         # Duplicate check (post-parse safety net for email + job)
#         try:
#             email_norm = (email_value or "").strip().lower()
#             if job_opening and applicant_exists_for_job(email_norm, job_opening):
#                 existing_name = frappe.db.get_value(
#                     "Job Applicant",
#                     {"email_id": email_norm, "job_title": job_opening},
#                     "name",
#                 )
#                 log_entries.append({
#                     "file_name":      filename_orig,
#                     "applicant_name": applicant_name or "",
#                     "email_id":       email_value or "",
#                     "status":         "Duplicate",
#                     "error_message":  f"Already exists as {existing_name}",
#                     "full_error":     f"Already exists as {existing_name}",
#                     "parsed_json":    json.dumps(applicant_data, indent=2) if applicant_data else "",
#                     "job_applicant":  existing_name or "",
#                 })
#                 continue
#         except Exception as e:
#             frappe.log_error(message=f"Duplicate check failed for {email_value}: {e}", title="upload_and_process: duplicate check failed")

#         # Enrich
#         applicant_data["experience_years"] = calculate_experience_years(applicant_data.get("experience", []))
#         flat_data = flatten_resume_data(applicant_data)

#         allowed_fit_levels = ["", "Strong Fit", "Moderate Fit", "Weak Fit"]
#         fit_level = applicant_data.get("fit_level", "")
#         if fit_level not in allowed_fit_levels:
#             fit_level = ""

#         # Insert Job Applicant
#         try:
#             clean_phone, other_phones = clean_phone_numbers(
#            applicant_data.get("phone_number")
#            or applicant_data.get("phone")
#             or ""
#     )
#             applicant_doc = {
#                 "doctype": "Job Applicant",
#                 "applicant_name":          applicant_name,
#                 "email_id":                email_value,
#                 "resume_attachment":       file_url,
#                 "status":                  "Open",
#                 # "phone_number":            applicant_data.get("phone_number") or applicant_data.get("phone") or "",
#                 "phone_number": _normalize_scalar(clean_phone),
#                 "custom_phone_number_2": _normalize_scalar(other_phones),
#                 "applicant_rating":        applicant_data.get("applicant_rating") or applicant_data.get("rating") or 0,
#                 "score":                   applicant_data.get("score"),
#                 "fit_level":               fit_level,
#                 "justification_by_ai":     applicant_data.get("justification_by_ai", ""),
#                 "custom_parsed_json":      json.dumps(applicant_data),
#                 "custom_parse_status":     "Parsed",
#                 "custom_experience_years": flat_data["experience_years"],
#                 "current_location":        flat_data["location"],
#                 "custom_skills":           flat_data["skills"],
#                 "custom_current_role":     flat_data["current_role"],
#                 "custom_degree":           flat_data["degree"],
#                 "custom_institution":      flat_data["institution"],
#                 "custom_current_company":  (
#                     applicant_data.get("custom_current_company")
#                     or (applicant_data.get("experience", [{}])[0].get("company_name", "") if applicant_data.get("experience") else "")
#                 ),
#                 "custom_total_experience": applicant_data.get("custom_total_experience", ""),
#             }
#             if job_opening:
#                 applicant_doc["job_title"] = job_opening

#             applicant = frappe.get_doc(applicant_doc)
#             applicant.insert(ignore_permissions=True)
#             created += 1

#             # Link file to applicant
#             try:
#                 saved_file.reload()
#                 saved_file.attached_to_doctype = "Job Applicant"
#                 saved_file.attached_to_name    = applicant.name
#                 saved_file.save(ignore_permissions=True)
#             except Exception as file_link_err:
#                 frappe.log_error(message=f"Could not link file to applicant {applicant.name}: {file_link_err}", title="upload_and_process: file link error")

#             log_entries.append({
#                 "file_name":      filename_orig,
#                 "applicant_name": applicant_name or "",
#                 "email_id":       email_value or "",
#                 "status":         "Created",
#                 "error_message":  "",
#                 "full_error":     "",
#                 "parsed_json":    json.dumps(applicant_data, indent=2) if applicant_data else "",
#                 "job_applicant":  applicant.name,
#             })

#             try:
#                 create_resume_from_upload(applicant_data=applicant_data, file_url=file_url, job_opening=job_opening, applicant_doc=applicant)
#             except Exception as e:
#                 frappe.log_error(message=f"Resume creation failed: {e}", title="Resume Integration Error")

#             frappe.logger().info(f"Created Job Applicant {email_value} from {filename_orig}")

#         except Exception as e:
#             frappe.log_error(message=f"Failed to insert Job Applicant for {filename_orig} ({email_value}): {e}", title="upload_and_process: insert failed")
#             import traceback
#             log_entries.append({
#                 "file_name":      filename_orig,
#                 "applicant_name": applicant_name or "",
#                 "email_id":       email_value or "",
#                 "status":         "Failed",
#                 "error_message":  str(e)[:500],
#                 "full_error":     traceback.format_exc(),   # full Python traceback
#                 "parsed_json":    json.dumps(applicant_data, indent=2) if applicant_data else "",
#                 "job_applicant":  "",
#             })

#     # Write Resume Import Log
#     try:
#         parse_errors_count = sum(1 for e in log_entries if e["status"] == "Parse Error")
#         failed_count       = sum(1 for e in log_entries if e["status"] == "Failed")

#         if not log_entries:
#             batch_status = "Failed"
#         elif created == 0 and parse_errors_count == 0 and failed_count == 0:
#             batch_status = "Completed"
#         elif created == 0 and (parse_errors_count > 0 or failed_count > 0):
#             batch_status = "Failed"
#         elif parse_errors_count > 0 or failed_count > 0:
#             batch_status = "Partial"
#         else:
#             batch_status = "Completed"

#         resume_log = frappe.get_doc({
#             "doctype":           "Resume Import Log",
#             "pdf_upload":        "",
#             "job_title":         job_opening or "",
#             "total_files":       total_files,
#             "parsed_count":      parsed_count,
#             "created_count":     created,
#             "parse_error_count": parse_errors_count,
#             "status":            batch_status,
#             "processed_at":      frappe.utils.now(),
#             "file_results": [
#                     {
#                         "doctype":        "Resume Import Log Entry",
#                         "file_name":      e["file_name"],
#                         "applicant_name": e["applicant_name"],
#                         "email_id":       e["email_id"],
#                         "status":         e["status"],
#                         "error_message":  e["error_message"],
#                         "full_error":     e.get("full_error", ""),
#                         "parsed_json":    e.get("parsed_json", ""),
#                         "job_applicant":  e["job_applicant"],
#                     }
#                     for e in log_entries
#                 ],
#         })
#         resume_log.insert(ignore_permissions=True)
#         frappe.db.commit()
#         frappe.logger().info(f"Resume Import Log created: {resume_log.name}")

#     except Exception as log_err:
#         frappe.log_error(message=str(log_err), title="Resume Import Log creation failed")

#     return {"message": f"{created} Job Applicant(s) created."}


import os
import json
import traceback

import frappe
from frappe import _
from frappe.utils.password import get_decrypted_password
import re

from resume.api.parse_guards import (
    applicant_exists_for_job,
    should_skip_file_for_job,
)
from resume.resume.doctype.pdf_upload.pdf_upload import _extract_and_parse_file

try:
    from vaaman_ats_ai.api.resume.resume import create_resume_from_upload
except ImportError:

    def create_resume_from_upload(
        applicant_data, file_url, job_opening=None, applicant_doc=None
    ):
        pass


FINAL_STATUSES = ("Completed", "Partial", "Failed")


# ---------------------------------------------------------------------------
# Inline helpers (replaced vaaman_ats_ai dependency)
# ---------------------------------------------------------------------------


def calculate_experience_years(experience_list):
    if not experience_list:
        return 0
    total_months = 0
    for exp in experience_list:
        try:
            from_date = exp.get("from_date") or exp.get("start_date") or ""
            to_date = exp.get("to_date") or exp.get("end_date") or "Present"
            if not from_date:
                continue
            from datetime import datetime

            start = datetime.strptime(from_date[:10], "%Y-%m-%d")
            end = (
                datetime.now()
                if (to_date in ("Present", "") or not to_date)
                else datetime.strptime(to_date[:10], "%Y-%m-%d")
            )
            total_months += max(
                0, (end.year - start.year) * 12 + (end.month - start.month)
            )
        except Exception:
            continue
    return round(total_months / 12, 1)


def flatten_resume_data(applicant_data):
    experience = applicant_data.get("experience") or []
    education = applicant_data.get("education") or []
    skills = applicant_data.get("skills") or []

    current_role = (
        (experience[0].get("title") or experience[0].get("position") or "")
        if experience
        else ""
    )
    current_company = (
        (experience[0].get("company_name") or experience[0].get("company") or "")
        if experience
        else ""
    )
    degree = (
        (education[0].get("degree") or education[0].get("qualification") or "")
        if education
        else ""
    )
    institution = (
        (education[0].get("institution") or education[0].get("college") or "")
        if education
        else ""
    )

    if isinstance(skills, list):
        skills_str = ", ".join(
            s if isinstance(s, str) else s.get("skill", "") for s in skills
        )
    else:
        skills_str = str(skills)

    return {
        "experience_years": calculate_experience_years(experience),
        "location": applicant_data.get("location")
        or applicant_data.get("current_location")
        or applicant_data.get("city")
        or "",
        "skills": skills_str,
        "current_role": current_role,
        "current_company": current_company,
        "degree": degree,
        "institution": institution,
    }


def clean_phone_numbers(phone):
    if not phone:
        return "", ""

    if isinstance(phone, list):
        normalized = []

        for p in phone:
            if isinstance(p, dict):
                normalized.append(
                    str(p.get("phone") or p.get("number") or p.get("value") or "")
                )
            else:
                normalized.append(str(p or ""))

        phone = ",".join(normalized)

    numbers = re.split(r"[,\n;/]+", str(phone))

    valid_numbers = []

    for num in numbers:
        num = num.strip()

        num = re.sub(r"[^\d+]", "", num)

        if len(re.sub(r"\D", "", num)) >= 10:
            if num not in valid_numbers:
                valid_numbers.append(num)

    first_number = valid_numbers[0] if valid_numbers else ""
    remaining_numbers = ", ".join(valid_numbers[1:]) if len(valid_numbers) > 1 else ""

    return first_number, remaining_numbers


def _normalize_scalar(value):
    if value is None:
        return ""

    if isinstance(value, (list, dict)):
        return json.dumps(value)

    return str(value)


# ---------------------------------------------------------------------------
# Main API  (step 1: save files, create log, enqueue, return batch_id)
# ---------------------------------------------------------------------------


@frappe.whitelist()
def upload_and_process(job_opening=None):
    try:
        frappe.local.flags.ignore_csrf = True
    except Exception:
        pass

    # Permission check — dynamic Role Permissions Manager settings ke hisaab se.
    # Ye function "Job Applicant" records create karta hai, isliye create permission check kiya.
    if not frappe.has_permission("Job Applicant", ptype="create"):
        frappe.logger().error(
            f"Permission denied for user {frappe.session.user} to create Job Applicant"
        )
        frappe.throw(
            _("You do not have permission to upload resumes / create Job Applicants")
        )

    if not job_opening:
        job_opening = frappe.form_dict.get("job_opening")

    is_data_bank = frappe.form_dict.get("is_data_bank") == "1"

    if job_opening:
        try:
            job_doc = frappe.get_doc("Job Opening", job_opening)
            if job_doc.get("status") == "Closed":
                frappe.throw(
                    _("This Job Opening is closed."), title=_("Job Opening is closed")
                )
        except frappe.exceptions.ValidationError:
            raise
        except Exception:
            frappe.log_error(
                message=f"Could not load Job Opening {job_opening}",
                title="upload_and_process: Job Opening lookup failed",
            )

    api_key = get_decrypted_password(
        "ATS Settings", "ATS Settings", "gemini_api_key", raise_exception=False
    ) or frappe.conf.get("gemini_api_key")
    if not api_key:
        frappe.throw(_("Gemini API key is not configured."))

    # Collect files
    files = []
    try:
        files = frappe.request.files.getlist("files")
    except Exception:
        f = frappe.request.files.get("files")
        if f:
            files = [f]

    if not files:
        frappe.throw("No files uploaded.")

    entries = []

    for file_storage in files:
        filename_orig = getattr(file_storage, "filename", None) or "uploaded_file"
        frappe.log_error(f"Processing {filename_orig}", "Resume Upload Debug")

        # Save file
        try:
            try:
                file_content = file_storage.stream.read()
            except Exception:
                file_storage.seek(0)
                file_content = file_storage.read()

            saved_file = frappe.get_doc(
                {
                    "doctype": "File",
                    "file_name": filename_orig,
                    "content": file_content,
                    "is_private": 1,
                }
            )
            saved_file.insert(ignore_permissions=True)
            frappe.log_error(f"Saved {filename_orig}", "Resume Upload Debug")

            entries.append(
                {
                    "doctype": "Resume Import Log Entry",
                    "file_name": filename_orig,
                    "file_doc_name": saved_file.name,
                    "status": "Queued",
                }
            )
        except Exception as e:
            frappe.log_error(
                message=f"File save failed {filename_orig}: {e}",
                title="upload_and_process: file save error",
            )
            entries.append(
                {
                    "doctype": "Resume Import Log Entry",
                    "file_name": filename_orig,
                    "file_doc_name": "",
                    "applicant_name": "",
                    "email_id": "",
                    "status": "Failed",
                    "error_message": f"Could not save file: {str(e)[:400]}",
                    "full_error": traceback.format_exc(),
                    "job_applicant": "",
                }
            )

    resume_log = frappe.get_doc(
        {
            "doctype": "Resume Import Log",
            "pdf_upload": "",
            "job_title": job_opening or "",
            "total_files": len(files),
            "parsed_count": 0,
            "created_count": 0,
            "parse_error_count": 0,
            "status": "Processing",
            "processed_at": frappe.utils.now(),
            "file_results": entries,
        }
    )
    resume_log.insert(ignore_permissions=True)
    frappe.db.commit()  # worker ko log dikhna chahiye
    frappe.logger().info(f"Resume Import Log created: {resume_log.name}")

    frappe.enqueue(
        "resume.api.upload_and_process.process_batch",
        queue="default",
        timeout=3600,
        batch_id=resume_log.name,
        job_opening=job_opening,
        is_data_bank=is_data_bank,
        user=frappe.session.user,
    )

    # Frappe ise khud "message" mein wrap karega -> res.message.batch_id
    return {"batch_id": resume_log.name, "total_files": len(files)}


# ---------------------------------------------------------------------------
# Step 2: Background worker (purana loop logic yahin chalta hai)
# ---------------------------------------------------------------------------


def process_batch(batch_id, job_opening=None, is_data_bank=False, user=None):
    if user:
        frappe.set_user(user)

    job_title_for_ai = None
    job_desc_for_ai = None

    if job_opening:
        try:
            job_doc = frappe.get_doc("Job Opening", job_opening)
            job_title_for_ai = job_doc.get("job_title") or job_opening
            job_desc_for_ai = job_doc.get("description")
        except Exception:
            frappe.log_error(
                message=f"Could not load Job Opening {job_opening}",
                title="upload_and_process: Job Opening lookup failed",
            )

    api_key = get_decrypted_password(
        "ATS Settings", "ATS Settings", "gemini_api_key", raise_exception=False
    ) or frappe.conf.get("gemini_api_key")

    prompt_path = frappe.get_app_path(
        "resume", "resume", "doctype", "pdf_upload", "resume_prompt.txt"
    )
    with open(prompt_path, "r") as f:
        prompt_template = f.read()

    resume_log = frappe.get_doc("Resume Import Log", batch_id)
    created = 0
    parsed_count = 0

    for row in resume_log.file_results:
        if row.status != "Queued":
            continue

        filename_orig = row.file_name

        try:
            saved_file = frappe.get_doc("File", row.file_doc_name)
            file_url = saved_file.file_url
            file_path = saved_file.get_full_path()

            if job_opening and should_skip_file_for_job(
                file_url, saved_file.content_hash, job_opening
            ):
                row.status = "Skipped"
                row.error_message = "File already imported for this job opening"
                row.full_error = ""
                row.parsed_json = ""
                row.job_applicant = ""
                continue

            # Parse
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

            try:
                _fu, _fname, applicant_data, err = _extract_and_parse_file(args)
            except Exception as parse_exc:
                err = str(parse_exc)
                applicant_data = None

            if isinstance(applicant_data, str):
                try:
                    applicant_data = json.loads(applicant_data)
                except Exception:
                    applicant_data = None

            if err or not applicant_data:
                frappe.log_error(
                    message=f"Parse failed for {filename_orig}: {err or 'empty'}",
                    title="upload_and_process: parse failed",
                )
                row.status = "Parse Error"
                row.error_message = str(err or "Empty result from AI")[:500]
                row.full_error = str(err or "")
                row.parsed_json = ""
                row.job_applicant = ""
                continue

            parsed_count += 1

            result = _create_applicant(
                applicant_data,
                filename_orig,
                file_url,
                saved_file,
                job_opening,
                is_data_bank,
            )
            row.status = result["status"]
            row.applicant_name = result.get("applicant_name", "")
            row.email_id = result.get("email_id", "")
            row.error_message = result.get("error_message", "")
            row.full_error = result.get("full_error", "")
            row.parsed_json = result.get("parsed_json", "")
            row.job_applicant = result.get("job_applicant", "")
            if row.status == "Created":
                created += 1

        except Exception as e:
            frappe.log_error(
                message=f"process_batch failed for {filename_orig}: {e}",
                title="upload_and_process: process_batch error",
            )
            row.status = "Failed"
            row.error_message = str(e)[:500]
            row.full_error = traceback.format_exc()
        finally:
            # Har file ke baad save + commit, taaki polling ko live progress mile
            try:
                resume_log.parsed_count = parsed_count
                resume_log.created_count = created
                resume_log.save(ignore_permissions=True)
                frappe.db.commit()
            except Exception as save_err:
                frappe.log_error(
                    message=str(save_err), title="Resume Import Log update failed"
                )

    # Final batch status (same logic as before)
    try:
        entries = resume_log.file_results
        parse_errors_count = sum(1 for e in entries if e.status == "Parse Error")
        failed_count = sum(1 for e in entries if e.status == "Failed")

        if not entries:
            batch_status = "Failed"
        elif created == 0 and parse_errors_count == 0 and failed_count == 0:
            batch_status = "Completed"
        elif created == 0 and (parse_errors_count > 0 or failed_count > 0):
            batch_status = "Failed"
        elif parse_errors_count > 0 or failed_count > 0:
            batch_status = "Partial"
        else:
            batch_status = "Completed"

        resume_log.parsed_count = parsed_count
        resume_log.created_count = created
        resume_log.parse_error_count = parse_errors_count
        resume_log.status = batch_status
        resume_log.save(ignore_permissions=True)
        frappe.db.commit()
    except Exception as log_err:
        frappe.log_error(
            message=str(log_err), title="Resume Import Log creation failed"
        )


# ---------------------------------------------------------------------------
# Step 3: Ek file ka applicant banana (purane loop ka same logic)
# ---------------------------------------------------------------------------


def _create_applicant(
    applicant_data, filename_orig, file_url, saved_file, job_opening, is_data_bank
):
    # Normalise keys
    for a, b in [
        ("email_id", "email"),
        ("email", "email_id"),
        ("phone_number", "phone"),
        ("phone", "phone_number"),
    ]:
        if a in applicant_data and b not in applicant_data:
            applicant_data[b] = applicant_data[a]

    applicant_name = (
        applicant_data.get("applicant_name")
        or applicant_data.get("name")
        or applicant_data.get("full_name")
    )
    email_value = applicant_data.get("email") or applicant_data.get("email_id")

    # Missing data
    if not is_data_bank and (not applicant_name or not email_value):
        frappe.log_error(
            message=f"Missing name/email for {filename_orig}",
            title="upload_and_process: missing data",
        )
        return {
            "status": "Missing Data",
            "applicant_name": applicant_name or "",
            "email_id": email_value or "",
            "error_message": "AI did not return candidate name or email.",
            "full_error": "AI did not return candidate name or email.",
            "parsed_json": (
                json.dumps(applicant_data, indent=2) if applicant_data else ""
            ),
            "job_applicant": "",
        }

    # Duplicate check (post-parse safety net for email + job)
    try:
        email_norm = (email_value or "").strip().lower()
        if job_opening and applicant_exists_for_job(email_norm, job_opening):
            existing_name = frappe.db.get_value(
                "Job Applicant",
                {"email_id": email_norm, "job_title": job_opening},
                "name",
            )
            return {
                "status": "Duplicate",
                "applicant_name": applicant_name or "",
                "email_id": email_value or "",
                "error_message": f"Already exists as {existing_name}",
                "full_error": f"Already exists as {existing_name}",
                "parsed_json": (
                    json.dumps(applicant_data, indent=2) if applicant_data else ""
                ),
                "job_applicant": existing_name or "",
            }
    except Exception as e:
        frappe.log_error(
            message=f"Duplicate check failed for {email_value}: {e}",
            title="upload_and_process: duplicate check failed",
        )

    # Enrich
    applicant_data["experience_years"] = calculate_experience_years(
        applicant_data.get("experience", [])
    )
    flat_data = flatten_resume_data(applicant_data)

    if is_data_bank:
        applicant_data["justification_by_ai"] = ""
        applicant_data["fit_level"] = ""
        applicant_data["applicant_rating"] = 0
        applicant_data["rating"] = 0
        applicant_data["score"] = None

    allowed_fit_levels = ["", "Strong Fit", "Moderate Fit", "Weak Fit"]
    fit_level = applicant_data.get("fit_level", "")
    if fit_level not in allowed_fit_levels:
        fit_level = ""

    # Insert Job Applicant
    try:
        clean_phone, other_phones = clean_phone_numbers(
            applicant_data.get("phone_number") or applicant_data.get("phone") or ""
        )
        applicant_doc = {
            "doctype": "Job Applicant",
            "applicant_name": applicant_name,
            "email_id": email_value,
            "resume_attachment": file_url,
            "status": "Open",
            "phone_number": _normalize_scalar(clean_phone),
            "custom_phone_number_2": _normalize_scalar(other_phones),
            "applicant_rating": applicant_data.get("applicant_rating")
            or applicant_data.get("rating")
            or 0,
            "score": applicant_data.get("score"),
            "fit_level": fit_level,
            "justification_by_ai": applicant_data.get("justification_by_ai", ""),
            "custom_parsed_json": json.dumps(applicant_data),
            "custom_parse_status": "Parsed",
            "custom_experience_years": flat_data["experience_years"],
            "current_location": flat_data["location"],
            "custom_skills": flat_data["skills"],
            "custom_current_role": flat_data["current_role"],
            "custom_degree": flat_data["degree"],
            "custom_institution": flat_data["institution"],
            "custom_current_company": (
                applicant_data.get("custom_current_company")
                or (
                    applicant_data.get("experience", [{}])[0].get("company_name", "")
                    if applicant_data.get("experience")
                    else ""
                )
            ),
            "custom_total_experience": applicant_data.get(
                "custom_total_experience", ""
            ),
        }
        if job_opening:
            applicant_doc["job_title"] = job_opening

        applicant = frappe.get_doc(applicant_doc)
        applicant.insert(ignore_permissions=False)

        # Link file to applicant
        try:
            saved_file.reload()
            saved_file.attached_to_doctype = "Job Applicant"
            saved_file.attached_to_name = applicant.name
            saved_file.save(ignore_permissions=True)
        except Exception as file_link_err:
            frappe.log_error(
                message=f"Could not link file to applicant {applicant.name}: {file_link_err}",
                title="upload_and_process: file link error",
            )

        try:
            create_resume_from_upload(
                applicant_data=applicant_data,
                file_url=file_url,
                job_opening=job_opening,
                applicant_doc=applicant,
            )
        except Exception as e:
            frappe.log_error(
                message=f"Resume creation failed: {e}",
                title="Resume Integration Error",
            )

        frappe.logger().info(
            f"Created Job Applicant {email_value} from {filename_orig}"
        )

        return {
            "status": "Created",
            "applicant_name": applicant_name or "",
            "email_id": email_value or "",
            "error_message": "",
            "full_error": "",
            "parsed_json": (
                json.dumps(applicant_data, indent=2) if applicant_data else ""
            ),
            "job_applicant": applicant.name,
        }

    except Exception as e:
        frappe.log_error(
            message=f"Failed to insert Job Applicant for {filename_orig} ({email_value}): {e}",
            title="upload_and_process: insert failed",
        )
        return {
            "status": "Failed",
            "applicant_name": applicant_name or "",
            "email_id": email_value or "",
            "error_message": str(e)[:500],
            "full_error": traceback.format_exc(),
            "parsed_json": (
                json.dumps(applicant_data, indent=2) if applicant_data else ""
            ),
            "job_applicant": "",
        }


# ---------------------------------------------------------------------------
# Step 4: Status endpoint (frontend yahi poll karta hai)
# ---------------------------------------------------------------------------


@frappe.whitelist()
def get_upload_batch_status(batch_id):
    log = frappe.get_doc("Resume Import Log", batch_id)
    log.check_permission("read")

    files = [
        {
            "file_doc_name": r.get("file_doc_name") or "",
            "file_name": r.file_name,
            "status": r.status,
            "error_message": r.get("error_message") or "",
        }
        for r in log.file_results
    ]

    total = len(files) or 1
    done = sum(1 for f in files if f["status"] not in ("Queued", "Processing"))
    progress = 100 if log.status in FINAL_STATUSES else round(done / total * 100)

    return {"status": log.status, "progress": progress, "files": files}
