import frappe


@frappe.whitelist()
def get_joining_track_list():
    """
    Get all candidates whose Job Offer status is Accepted, along with
    joining status (Selected / Joined), joining date, location, designation
    and HR remark.

    Data sources:
    - Job Offer: designation, custom_location_list, custom_joining_date, status
    - Joining Confirmation: join (0/1), custom_date_of_joining, custom_remark
    """
    try:
        # 1. Get all Accepted Job Offers
        offers = frappe.get_all(
            "Job Offer",
            filters=[["status", "like", "%Accept%"]],
            fields=[
                "name",
                "job_applicant",
                "applicant_name",
                "applicant_email",
                "designation",
                "custom_location_list",
                "custom_joining_date",
                "creation",
            ],
            order_by="creation desc",
        )

        if not offers:
            return {"message": "success", "data": []}

        applicant_ids = [o.job_applicant for o in offers if o.job_applicant]

        # 2. Get Joining Confirmation records for these applicants
        joining_records = frappe.get_all(
            "Joining Confirmation",
            filters={"candidate_id": ["in", applicant_ids]},
            fields=[
                "candidate_id",
                "join",
                "not_join",
                "offer_revoked",
                "custom_date_of_joining",
                "custom_remark",
            ],
        )
        joining_map = {j.candidate_id: j for j in joining_records}

        # 3. Get extra Job Applicant details (phone number, backup email)
        applicants = frappe.get_all(
            "Job Applicant",
            filters={"name": ["in", applicant_ids]},
            fields=["name", "phone_number", "email_id"],
        )
        applicant_map = {a.name: a for a in applicants}

        # 4. Build the response list
        result = []
        for offer in offers:
            jc = joining_map.get(offer.job_applicant)

            # Skip candidate entirely if Offer Revoked is checked in Joining Confirmation
            if jc and jc.get("offer_revoked") == 1:
                continue

            applicant_info = applicant_map.get(offer.job_applicant, {})

            is_joined = bool(jc and jc.get("join") == 1)

            result.append({
                "candidate_id": offer.job_applicant,
                "offer_name": offer.name,
                "applicant_name": offer.applicant_name,
                "email": offer.applicant_email or applicant_info.get("email_id", ""),
                "phone": applicant_info.get("phone_number", ""),
                "designation": offer.designation or "",
                "location": offer.custom_location_list or "",
                "status": "Joined" if is_joined else "Selected",
                "expected_joining_date": offer.custom_joining_date,
                "actual_joining_date": jc.get("custom_date_of_joining") if jc else None,
                "remark": (jc.get("custom_remark") if jc else "") or "",
            })

        return {"message": "success", "data": result, "total": len(result)}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Joining Track Fetch Failed")
        return {"message": "error", "data": [], "error": str(e)}


@frappe.whitelist()
def update_joining_remark():
    """
    Update / save HR remark for a candidate on the Joining Confirmation record.
    Creates a Joining Confirmation record if one doesn't exist yet
    (e.g. HR is adding a remark before the candidate has actually joined).
    """
    try:
        data = frappe.local.form_dict
        candidate_id = data.get("candidate_id")
        remark = data.get("remark", "")

        if not candidate_id:
            return {"success": False, "message": "Candidate ID is required"}

        existing = frappe.get_all(
            "Joining Confirmation",
            filters={"candidate_id": candidate_id},
            fields=["name"],
        )

        # NEW: Permission check — dynamic Role Permissions Manager settings ke hisaab se.
        # Agar record already exist karta hai toh "write" chahiye, warna "create" chahiye.
        required_ptype = "write" if existing else "create"
        if not frappe.has_permission("Joining Confirmation", ptype=required_ptype):
            return {"success": False, "message": "You do not have permission to update this record"}

        if existing:
            doc = frappe.get_doc("Joining Confirmation", existing[0].name)
        else:
            doc = frappe.new_doc("Joining Confirmation")
            doc.candidate_id = candidate_id

        doc.custom_remark = remark
        doc.save(ignore_permissions=False)  # CHANGED: True se False kiya, taaki Frappe ka internal permission engine bhi check kare (double-safety)
        frappe.db.commit()

        return {"success": True, "message": "Remark saved successfully"}

    except Exception as e:
        frappe.log_error(str(e), "Joining Remark Update Failed")
        frappe.db.rollback()
        return {"success": False, "message": str(e)}