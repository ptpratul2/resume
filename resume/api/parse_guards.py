"""Shared duplicate / skip guards for resume ingestion (email, upload, PDF batch)."""

import frappe


def applicant_exists_for_job(email, job_opening):
    if not email or not job_opening:
        return False
    return bool(
        frappe.db.exists(
            "Job Applicant",
            {
                "email_id": (email or "").strip().lower(),
                "job_title": job_opening,
            },
        )
    )


def resume_content_hash_already_processed(content_hash, job_opening=None):
    if not content_hash:
        return False
    file_urls = frappe.get_all(
        "File",
        filters={"content_hash": content_hash},
        pluck="file_url",
    )
    if not file_urls:
        return False
    filters = {"resume_attachment": ["in", file_urls]}
    if job_opening:
        filters["job_title"] = job_opening
    return bool(frappe.db.exists("Job Applicant", filters))


def attachment_already_processed_for_job(file_url, job_opening=None):
    if not file_url:
        return False
    filters = {"resume_attachment": file_url}
    if job_opening:
        filters["job_title"] = job_opening
    return bool(frappe.db.exists("Job Applicant", filters))


def should_skip_file_for_job(file_url, content_hash, job_opening=None):
    """True when this file was already imported for the given job opening."""
    if job_opening and attachment_already_processed_for_job(file_url, job_opening):
        return True
    if job_opening and resume_content_hash_already_processed(content_hash, job_opening):
        return True
    return False
