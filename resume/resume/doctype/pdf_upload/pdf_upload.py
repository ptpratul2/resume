import frappe
import os
from pdfminer.high_level import extract_text
from frappe.model.document import Document
import re
import pytesseract
from PIL import Image
from pdf2image import convert_from_path

class PDFUpload(Document):
    pass

@frappe.whitelist()
def process_pdfs(docname):
    """Reads uploaded PDF files, extracts text, and creates Job Applicant records."""
    doc = frappe.get_doc("PDF Upload", docname)

    if not doc.get("files"):
        frappe.throw("No PDF files uploaded")

    for file_entry in doc.get("files"):
        file_url = file_entry.get("file_upload")

        if not file_url:
            frappe.throw("Missing file URL in one of the entries.")
        
        # Determine if the file is public or private
        if file_url.startswith("/private/files/"):
            file_path = frappe.get_site_path(file_url.lstrip("/"))
        elif file_url.startswith("/files/"):
            file_path = frappe.get_site_path("public" + file_url)
        else:
            frappe.throw(f"Invalid file path: {file_url}")

        # Validate file existence
        if not os.path.exists(file_path):
            frappe.throw(f"File not found on server: {file_path}")

        try:
            # Extract text using pdfminer
            text = extract_text(file_path)
            
            # If text extraction failed, try using OCR
            if not text.strip():
                text = extract_text_with_ocr(file_path)
        except Exception as e:
            frappe.throw(f"Error extracting text from PDF: {e}")

        # Parse extracted text
        applicant_data = parse_pdf_text(text)
        print(applicant_data)
        
        if not applicant_data.get("applicant_name") or not applicant_data.get("email") or not applicant_data.get("phone"):
            frappe.throw(f"Missing required fields in {file_url}")

        # Check if applicant already exists using email
        if frappe.db.exists("Job Applicant", {"email_id": applicant_data["email"]}):
            frappe.msgprint(f"Applicant with email {applicant_data['email']} already exists.")
            continue

        # Create new Job Applicant record
        applicant = frappe.get_doc({
            "doctype": "Job Applicant",
            "applicant_name": applicant_data["applicant_name"],
            "email_id": applicant_data["email"],
            "resume_attachment": file_url,
            "status": "Open",
            "phone_number": applicant_data["phone"],
            "job_title": doc.job_title,
            "designation": doc.designation,
        })
        applicant.insert(ignore_permissions=True)

    frappe.msgprint("All Job Applicants Created Successfully")


def extract_text_with_ocr(file_path):
    """Extract text from scanned PDFs using Tesseract OCR."""
    try:
        images = convert_from_path(file_path)
        extracted_text = ""
        for image in images:
            extracted_text += pytesseract.image_to_string(image)
        return extracted_text.strip()
    except Exception as e:
        raise ValueError(f"Error extracting text with OCR: {e}")


def parse_pdf_text(text):
    applicant_data = {"applicant_name": "", "email": "", "phone": ""}

    # Regex patterns
    phone_pattern = re.compile(r'\b(?:\+?\d{1,4}[-.\s]?)?(?:\d{10}|\d{5}[-.\s]?\d{5})\b')
    email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    name_pattern = re.compile(r'^[A-Za-z\s.,-]{3,}$')

    # Extract email
    email_match = email_pattern.search(text)
    if email_match:
        applicant_data["email"] = email_match.group()

    # Extract phone number
    phone_match = phone_pattern.search(text)
    if phone_match:
        applicant_data["phone"] = phone_match.group()

    # Extract name by finding the first non-empty line with no numbers
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    for line in lines:
        if name_pattern.match(line) and not any(char.isdigit() for char in line):
            applicant_data["applicant_name"] = line
            break

    # Validation
    if not applicant_data["applicant_name"]:
        raise ValueError("Applicant name not found.")
    
    return applicant_data