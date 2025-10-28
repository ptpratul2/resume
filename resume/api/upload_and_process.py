import frappe
import os
import uuid
from pdfminer.high_level import extract_text
from resume.resume.doctype.pdf_upload.pdf_upload import extract_text_with_ocr, parse_pdf_text

@frappe.whitelist(allow_guest=False)
def upload_and_process(job_opening=None):
    """
    Upload and process resume PDFs
    Creates Job Applicant records from uploaded resumes
    """
    # Disable CSRF check for file uploads
    frappe.local.flags.ignore_csrf = True
    
    # Get job_opening from parameters or form data
    if not job_opening:
        job_opening = frappe.form_dict.get("job_opening")
    
    if not job_opening:
        frappe.throw("Job Opening is required")

    try:
        # Get uploaded files
        files = frappe.request.files.getlist("files")
        if not files:
            frappe.throw("No files uploaded")

        created_applicants = []
        errors = []

        for file_storage in files:
            try:
                # Generate unique filename
                filename = f"{uuid.uuid4()}_{file_storage.filename}"
                file_path = frappe.get_site_path("private", "files", filename)

                # Save file to disk
                with open(file_path, "wb") as f:
                    f.write(file_storage.stream.read())

                file_url = f"/private/files/{filename}"

                # Extract text from PDF
                try:
                    text = extract_text(file_path)
                    if not text.strip():
                        text = extract_text_with_ocr(file_path)
                except Exception as e:
                    frappe.log_error(f"Text extraction failed for {filename}: {str(e)}")
                    errors.append(f"Failed to extract text from {file_storage.filename}")
                    continue

                # Parse extracted text
                try:
                    applicant_data = parse_pdf_text(text)
                except Exception as e:
                    frappe.log_error(f"Parsing failed for {filename}: {str(e)}")
                    errors.append(f"Failed to parse {file_storage.filename}")
                    continue

                # Validate required fields
                if not applicant_data.get("applicant_name") or not applicant_data.get("email"):
                    frappe.log_error(f"Missing required info in {filename}")
                    errors.append(f"Missing name or email in {file_storage.filename}")
                    continue

                # Check for duplicates
                if frappe.db.exists("Job Applicant", {
                    "email_id": applicant_data["email"],
                    "job_title": job_opening
                }):
                    errors.append(f"Applicant with email {applicant_data['email']} already exists for this job")
                    continue

                # Create Job Applicant
                try:
                    applicant_doc = frappe.get_doc({
                        "doctype": "Job Applicant",
                        "applicant_name": applicant_data["applicant_name"],
                        "email_id": applicant_data["email"],
                        "resume_attachment": file_url,
                        "status": "Open",
                        "phone_number": applicant_data.get("phone", ""),
                        "job_title": job_opening
                    })
                    
                    applicant_doc.insert(ignore_permissions=True)
                    frappe.db.commit()
                    
                    created_applicants.append(applicant_data["applicant_name"])

                except Exception as e:
                    frappe.log_error(f"Failed to create applicant from {filename}: {str(e)}")
                    errors.append(f"Failed to create applicant from {file_storage.filename}")

            except Exception as e:
                frappe.log_error(f"Error processing {file_storage.filename}: {str(e)}")
                errors.append(f"Error processing {file_storage.filename}")

        # Return results
        result = {
            "message": f"Successfully created {len(created_applicants)} applicant(s)",
            "created": len(created_applicants),
            "applicants": created_applicants,
        }
        
        if errors:
            result["errors"] = errors
            result["failed"] = len(errors)
        
        return result

    except Exception as e:
        frappe.log_error(f"Resume upload failed: {str(e)}")
        frappe.throw(f"Resume upload failed: {str(e)}")

