import frappe
import os
from frappe import _

@frappe.whitelist()
def parse_cv_and_create_applicant_direct(file_url, job_id, designation):
    """
    Parse CV and create Job Applicant directly from Job Opening.
    No PDF Upload, no score/fit_level/justification_by_ai.
    """
    if not file_url or not job_id:
        frappe.throw(_("File or Job Opening ID is missing."))

    from resume.resume.doctype.pdf_upload.pdf_upload import (
        extract_text_from_any_file,
        _parse_text_threadsafe,
        _parse_pdf_threadsafe,
    )

    # Resolve file path
    site_url = frappe.utils.get_url()
    if file_url.startswith(site_url):
        file_url = file_url.split(site_url, 1)[1]
    if not file_url.startswith("/"):
        file_url = "/" + file_url

    file_path = None
    file_list = frappe.get_all("File", filters={"file_url": file_url}, limit=1)
    if file_list:
        try:
            file_doc = frappe.get_doc("File", file_list[0].name)
            file_path = file_doc.get_full_path()
        except Exception:
            pass
    if not file_path or not os.path.exists(file_path):
        path_parts = file_url.lstrip("/").split("/") if file_url.startswith("/private") else ["public"] + file_url.lstrip("/").split("/")
        file_path = os.path.abspath(frappe.get_site_path(*path_parts))

    if not os.path.exists(file_path):
        frappe.throw(_("File not found on server: {0}").format(file_path))

    api_key = frappe.conf.get("gemini_api_key")
    if not api_key:
        frappe.throw(_("Gemini API key missing in site_config.json"))

    prompt_path = frappe.get_app_path("resume", "resume", "doctype", "pdf_upload", "parse_only_prompt.txt")
    with open(prompt_path, "r") as f:
        prompt_template = f.read()

    ext = os.path.splitext(file_path)[1].lower()
    job_desc = frappe.db.get_value("Job Opening", job_id, "description")
    job_title = job_id

    if ext == ".pdf":
        text = extract_text_from_any_file(file_path)
        if text:
            applicant_data = _parse_text_threadsafe(api_key, prompt_template, text, job_title, job_desc)
        else:
            applicant_data = _parse_pdf_threadsafe(api_key, prompt_template, file_path, job_title, job_desc)
    else:
        text = extract_text_from_any_file(file_path)
        if not text:
            frappe.throw(_("Could not extract text from file."))
        applicant_data = _parse_text_threadsafe(api_key, prompt_template, text, job_title, job_desc)

    email = applicant_data.get("email_id")
    if not email or not applicant_data.get("applicant_name"):
        frappe.throw(_("Could not extract name/email from resume."))

    if frappe.db.exists("Job Applicant", {"email_id": email, "job_title": job_id}):
        frappe.throw(_("Applicant with email {0} already exists for this job.").format(email))

    status_options = frappe.get_meta("Job Applicant").get_options("status") or ""
    valid_statuses = [s.strip() for s in status_options.split("\n") if s.strip()]
    default_status = "CV Submitted" if "CV Submitted" in valid_statuses else (valid_statuses[0] if valid_statuses else "Open")

    applicant = frappe.get_doc({
        "doctype": "Job Applicant",
        "applicant_name": applicant_data.get("applicant_name"),
        "email_id": email,
        "phone_number": applicant_data.get("phone_number", ""),
        "custom_phone_number_2": applicant_data.get("custom_phone_number_2", ""),
        "resume_attachment": file_url,
        "status": default_status,
        "job_title": job_id,
        "designation": designation,
    })
    applicant.insert(ignore_permissions=True)
    frappe.db.commit()

    return {"applicant_name": applicant.applicant_name, "name": applicant.name}


@frappe.whitelist()
def save_cv_to_pdf_upload(file_url, job_id, designation, action):
    if not file_url or not job_id:
        frappe.throw(_("File or Job Opening ID is missing."))

    pdf_upload_name = frappe.db.get_value("PDF Upload", {"job_title": job_id}, "name")

    if pdf_upload_name:
        doc = frappe.get_doc("PDF Upload", pdf_upload_name)
    else:
        # Agar nahi hai toh naya record banayein
        doc = frappe.new_doc("PDF Upload")
        # Job Opening ki 'name' field -> PDF Upload ki 'job_title' field mein
        doc.job_title = job_id
        # Job Opening ki 'designation' field -> PDF Upload ki 'designation' field mein
        doc.designation = designation

    # 2. Child table 'files' mein entry add karein
    doc.append("files", {
        "file_upload": file_url
    })

    # 3. Save aur Commit
    doc.save(ignore_permissions=True)
    frappe.db.commit()

    # Action specific processing yahan trigger karein
    if action == "Parse":
        # parse_cv(file_url)
        pass
    elif action == "Score":
        # score_cv(file_url)
        pass

    return doc.name