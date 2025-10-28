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

    if not isinstance(text, str):
        text = str(text) if text else ""
    if not text or len(text.strip()) < 3:
        raise ValueError("Applicant name not found.")

    try:
        email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        phone_pattern = re.compile(r'\b(?:\+?\d{1,4}[-.\s]?)?(?:\d{10}|\d{5}[-.\s]?\d{5})\b')
        email_match = email_pattern.search(text)
        if email_match:
            applicant_data["email"] = email_match.group()
        phone_match = phone_pattern.search(text)
        if phone_match:
            applicant_data["phone"] = phone_match.group()
    except:
        pass

    exclude = {'curriculum', 'curriculam', 'vitae', 'resume', 'cv', 'objective', 'profile', 'summary',
               'experience', 'education', 'qualification', 'skills', 'contact', 'email', 'phone',
               'address', 'developer', 'engineer', 'designer', 'manager', 'analyst', 'consultant',
               'nationality', 'india', 'marital', 'status', 'passing', 'year', 'responsibility',
               'role', 'society', 'institute', 'electronic', 'rajput', 'village', 'personal',
               'information', 'applied', 'industrial', 'mern', 'stack', 'development', 'board',
               'june', 'july', 'august', 'september', 'october', 'november', 'december', 'january',
               'february', 'march', 'april', 'may', 'para', 'arya', 'flat', 'floor', 'basic',
               'acadmic', 'credentials', 'college', 'ward', 'tehsil', 'district', 'madhya', 'pradesh',
               'training', 'honest', 'and', 'thanking', 'you', 'core', 'competencies', 'human',
               'resource', 'department', 'iti', 'i', 't', 'higher', 'secondary', 'examination',
               'traditionally', 'professional', 'apr', 'new', 'kosad', 'can', 'hindi', 'look',
               'forward', 'positive', 'proficient', 'git', 'for', 'suthar', 'sbsstc', 'ferozepur'}

    try:
        lines = [l.strip() for l in text.split('\n') if l.strip()][:30]
    except:
        lines = []

    # Strategy 1: Pattern-based
    try:
        for line in lines[:20]:
            if '@' in line or re.search(r'[\/\\()\[\]{}]', line):
                continue
            if re.search(r'\d', line):
                parts = re.split(r'\s{3,}', line)
                if parts:
                    line = parts[0]
            if len(line) > 40:
                continue
            line_clean = re.sub(r'^(Name|Full Name)[:\-\s]+', '', line, flags=re.IGNORECASE).strip()
            words = [w.strip('.,:-') for w in line_clean.split() if w.strip('.,:-') and w.isalpha()]
            if 2 <= len(words) <= 4 and all(w[0].isupper() for w in words):
                name_str = ' '.join(words)
                if any(len(w) >= 3 for w in words) and not any(ex in name_str.lower() for ex in exclude):
                    applicant_data["applicant_name"] = name_str
                    return applicant_data
    except:
        pass

    # Strategy 2: NLP
    try:
        nlp = spacy.load('en_core_web_sm')
        for line in lines[:15]:
            if '@' in line or re.search(r'\d', line) or len(line) > 40:
                continue
            doc = nlp(line)
            for ent in doc.ents:
                if ent.label_ == 'PERSON':
                    name = ent.text.strip()
                    words = [w for w in name.split() if w.isalpha()]
                    if 2 <= len(words) <= 4 and not any(ex in name.lower() for ex in exclude):
                        applicant_data["applicant_name"] = name
                        return applicant_data
    except:
        pass

    # Strategy 3: Look for "Name:" pattern aggressively
    try:
        for line in lines[:30]:
            if re.search(r'\b(Name|Full Name|Candidate Name|Applicant Name)\s*[:\-]', line, re.IGNORECASE):
                # Extract everything after "Name:" until line end or special chars
                match = re.search(r'\b(?:Name|Full Name|Candidate Name|Applicant Name)\s*[:\-]\s*([A-Z][a-zA-Z\s\.]+?)(?:\s{3,}|\||$|[0-9])', line, re.IGNORECASE)
                if match:
                    candidate = match.group(1).strip()
                    # Clean up dots and extra spaces
                    candidate = re.sub(r'\.+', ' ', candidate).strip()
                    words = [w for w in candidate.split() if w.isalpha() and len(w) >= 2]
                    if 1 <= len(words) <= 4:
                        name_str = ' '.join(words)
                        if len(name_str) >= 3 and not any(ex in name_str.lower() for ex in exclude):
                            applicant_data["applicant_name"] = name_str
                            return applicant_data
    except:
        pass

    # Strategy 4: Simple capitalized lines
    try:
        for line in lines[:25]:
            if '@' in line or len(line) > 50:
                continue
            if 5 <= len(line) <= 35 and all(c.isalpha() or c.isspace() for c in line):
                words = [w for w in line.split() if w.isalpha()]
                if 2 <= len(words) <= 4 and all(w[0].isupper() for w in words):
                    if not any(ex in line.lower() for ex in exclude):
                        applicant_data["applicant_name"] = line.strip()
                        return applicant_data
    except:
        pass

    # Strategy 5: Last resort
    try:
        for line in lines[:25]:
            words = [w for w in line.split() if w.isalpha() and len(w) >= 2]
            if 2 <= len(words) <= 4:
                candidate = ' '.join(words)
                if candidate[0].isupper() and len(candidate) >= 5:
                    candidate_lower = candidate.lower()
                    if not any(candidate_lower == ex or candidate_lower.startswith(ex + ' ') or
                              candidate_lower.endswith(' ' + ex) or (' ' + ex + ' ') in candidate_lower
                              for ex in exclude):
                        applicant_data["applicant_name"] = candidate
                        return applicant_data
    except:
        pass

    # Strategy 6: Absolute fallback
    try:
        for line in lines:
            words = [w for w in line.split() if w and w[0].isupper() and w.isalpha() and len(w) >= 2]
            if len(words) >= 2:
                candidate = ' '.join(words[:2])
                candidate_lower = candidate.lower()
                if not any(candidate_lower == ex or candidate_lower.startswith(ex + ' ') or
                          candidate_lower.endswith(' ' + ex) or (' ' + ex + ' ') in candidate_lower
                          for ex in exclude):
                    applicant_data["applicant_name"] = candidate
                    return applicant_data
    except:
        pass

    if not applicant_data["applicant_name"]:
        raise ValueError("Applicant name not found.")

    return applicant_data