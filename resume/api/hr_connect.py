# # import frappe


# # @frappe.whitelist()
# # def get_hr_connect_list():
# #     """
# #     Get all candidates who have actually joined (Joining Confirmation.join = 1),
# #     along with their 30/90/180 day HR Connect dates and statuses.

# #     30/90/180 day dates are calculated from custom_date_of_joining.
# #     Status (Done / Not Done Yet) and Confirmation Status are manually
# #     set by HR from the frontend.
# #     """
# #     try:
# #         # Only request custom status fields if they actually exist on the
# #         # doctype yet. This way the list still works even before the
# #         # custom_30_days_status / custom_90_days_status / custom_180_days_status /
# #         # custom_confirmation_status fields have been created in Frappe.
# #         meta = frappe.get_meta("Joining Confirmation")
# #         optional_fields = [
# #             "custom_30_days_status",
# #             "custom_90_days_status",
# #             "custom_180_days_status",
# #             "custom_confirmation_status",
# #             "custom_30_day_reminder_sent",
# #             "custom_90_day_reminder_sent",
# #             "custom_180_day_reminder_sent",
# #         ]
# #         existing_optional = [f for f in optional_fields if meta.has_field(f)]

# #         base_fields = ["name", "candidate_id", "custom_date_of_joining"]
# #         fields = base_fields + existing_optional

# #         records = frappe.get_all(
# #             "Joining Confirmation",
# #             filters={"join": 1},
# #             fields=fields,
# #             order_by="custom_date_of_joining desc",
# #         )

# #         if not records:
# #             return {"message": "success", "data": []}

# #         candidate_ids = [r.candidate_id for r in records if r.candidate_id]

# #         applicants = frappe.get_all(
# #             "Job Applicant",
# #             filters={"name": ["in", candidate_ids]},
# #             fields=["name", "applicant_name", "email_id", "phone_number"],
# #         )
# #         applicant_map = {a.name: a for a in applicants}

# #         offers = frappe.get_all(
# #             "Job Offer",
# #             filters={"job_applicant": ["in", candidate_ids]},
# #             fields=["job_applicant", "designation", "custom_grade"],
# #         )
# #         offer_map = {o.job_applicant: o for o in offers}

# #         result = []
# #         for r in records:
# #             # Without a joining date we cannot calculate 30/90/180 day connects
# #             if not r.custom_date_of_joining:
# #                 continue

# #             applicant = applicant_map.get(r.candidate_id, {}) or {}
# #             offer = offer_map.get(r.candidate_id, {}) or {}

# #             doj = frappe.utils.getdate(r.custom_date_of_joining)
# #             day_30_date = frappe.utils.add_days(doj, 30)
# #             day_90_date = frappe.utils.add_days(doj, 90)
# #             day_180_date = frappe.utils.add_days(doj, 180)

# #             result.append({
# #                 "candidate_id": r.candidate_id,
# #                 "applicant_name": applicant.get("applicant_name", ""),
# #                 "email": applicant.get("email_id", ""),
# #                 "phone": applicant.get("phone_number", ""),
# #                 "designation": offer.get("designation", "") or "",
# #                 "grade": offer.get("custom_grade", "") or "",
# #                 "date_of_joining": str(doj),
# #                 "day_30_date": str(day_30_date),
# #                 "day_30_status": r.custom_30_days_status or "Not Done Yet",
# #                 "day_30_reminder_sent": bool(r.custom_30_day_reminder_sent),
# #                 "day_90_date": str(day_90_date),
# #                 "day_90_status": r.custom_90_days_status or "Not Done Yet",
# #                 "day_90_reminder_sent": bool(r.custom_90_day_reminder_sent),
# #                 "day_180_date": str(day_180_date),
# #                 "day_180_status": r.custom_180_days_status or "Not Done Yet",
# #                 "day_180_reminder_sent": bool(r.custom_180_day_reminder_sent),
# #                 "confirmation_status": r.custom_confirmation_status or "Not Confirmed",
# #             })

# #         return {"message": "success", "data": result, "total": len(result)}

# #     except Exception as e:
# #         frappe.log_error(frappe.get_traceback(), "HR Connect Track Fetch Failed")
# #         return {"message": "error", "data": [], "error": str(e)}


# # @frappe.whitelist()
# # def update_hr_connect_status():
# #     """
# #     Update one status field on the candidate's Joining Confirmation record.

# #     field_type: '30_day' | '90_day' | '180_day' | 'confirmation'
# #     value:      the new dropdown value selected by HR
# #     """
# #     try:
# #         data = frappe.local.form_dict
# #         candidate_id = data.get("candidate_id")
# #         field_type = data.get("field_type")
# #         value = data.get("value")

# #         if not candidate_id:
# #             return {"success": False, "message": "Candidate ID is required"}

# #         field_map = {
# #             "30_day": "custom_30_days_status",
# #             "90_day": "custom_90_days_status",
# #             "180_day": "custom_180_days_status",
# #             "confirmation": "custom_confirmation_status",
# #         }
# #         fieldname = field_map.get(field_type)
# #         if not fieldname:
# #             return {"success": False, "message": "Invalid field_type"}

# #         # Give a clear message instead of a raw SQL error if the custom
# #         # field hasn't been created in Frappe yet.
# #         meta = frappe.get_meta("Joining Confirmation")
# #         if not meta.has_field(fieldname):
# #             return {
# #                 "success": False,
# #                 "message": (
# #                     f"Field '{fieldname}' does not exist on Joining Confirmation yet. "
# #                     "Please create it in Frappe: Setup → Customize Form → Joining Confirmation."
# #                 ),
# #             }

# #         existing = frappe.get_all(
# #             "Joining Confirmation",
# #             filters={"candidate_id": candidate_id},
# #             fields=["name"],
# #         )
# #         if not existing:
# #             return {"success": False, "message": "Joining Confirmation record not found"}

# #         frappe.db.set_value("Joining Confirmation", existing[0].name, fieldname, value)
# #         frappe.db.commit()

# #         return {"success": True, "message": f"{fieldname} updated successfully"}

# #     except Exception as e:
# #         frappe.log_error(str(e), "HR Connect Status Update Failed")
# #         frappe.db.rollback()
# #         return {"success": False, "message": str(e)}


# import frappe


# @frappe.whitelist()
# def get_hr_connect_list():
#     """
#     Get all candidates who have actually joined (Joining Confirmation.join = 1),
#     along with their 30/90/180/270/365 day HR Connect dates and statuses.

#     30/90/180/270/365 day dates are calculated from custom_date_of_joining.
#     Status (Done / Not Done Yet) and Confirmation Status are manually
#     set by HR from the frontend.
#     """
#     try:
#         # Only request custom status fields if they actually exist on the
#         # doctype yet. This way the list still works even before the
#         # custom_30_days_status / custom_90_days_status / custom_180_days_status /
#         # custom_270_days_status / custom_365_days_status /
#         # custom_confirmation_status fields have been created in Frappe.
#         meta = frappe.get_meta("Joining Confirmation")
#         optional_fields = [
#             "custom_30_days_status",
#             "custom_90_days_status",
#             "custom_180_days_status",
#             "custom_270_days_status",
#             "custom_365_days_status",
#             "custom_confirmation_status",
#             "custom_30_day_reminder_sent",
#             "custom_90_day_reminder_sent",
#             "custom_180_day_reminder_sent",
#             "custom_270_day_reminder_sent",
#             "custom_365_day_reminder_sent",
#         ]
#         existing_optional = [f for f in optional_fields if meta.has_field(f)]

#         base_fields = ["name", "candidate_id", "custom_date_of_joining"]
#         fields = base_fields + existing_optional

#         records = frappe.get_all(
#             "Joining Confirmation",
#             filters={"join": 1},
#             fields=fields,
#             order_by="custom_date_of_joining desc",
#         )

#         if not records:
#             return {"message": "success", "data": []}

#         candidate_ids = [r.candidate_id for r in records if r.candidate_id]

#         applicants = frappe.get_all(
#             "Job Applicant",
#             filters={"name": ["in", candidate_ids]},
#             fields=["name", "applicant_name", "email_id", "phone_number"],
#         )
#         applicant_map = {a.name: a for a in applicants}

#         offers = frappe.get_all(
#             "Job Offer",
#             filters={"job_applicant": ["in", candidate_ids]},
#             fields=["job_applicant", "designation", "custom_grade"],
#         )
#         offer_map = {o.job_applicant: o for o in offers}

#         result = []
#         for r in records:
#             # Without a joining date we cannot calculate 30/90/180/270/365 day connects
#             if not r.custom_date_of_joining:
#                 continue

#             applicant = applicant_map.get(r.candidate_id, {}) or {}
#             offer = offer_map.get(r.candidate_id, {}) or {}

#             doj = frappe.utils.getdate(r.custom_date_of_joining)
#             day_30_date = frappe.utils.add_days(doj, 30)
#             day_90_date = frappe.utils.add_days(doj, 90)
#             day_180_date = frappe.utils.add_days(doj, 180)
#             day_270_date = frappe.utils.add_days(doj, 270)
#             day_365_date = frappe.utils.add_days(doj, 365)

#             result.append({
#                 "candidate_id": r.candidate_id,
#                 "applicant_name": applicant.get("applicant_name", ""),
#                 "email": applicant.get("email_id", ""),
#                 "phone": applicant.get("phone_number", ""),
#                 "designation": offer.get("designation", "") or "",
#                 "grade": offer.get("custom_grade", "") or "",
#                 "date_of_joining": str(doj),
#                 "day_30_date": str(day_30_date),
#                 "day_30_status": r.custom_30_days_status or "Not Done Yet",
#                 "day_30_reminder_sent": bool(r.custom_30_day_reminder_sent),
#                 "day_90_date": str(day_90_date),
#                 "day_90_status": r.custom_90_days_status or "Not Done Yet",
#                 "day_90_reminder_sent": bool(r.custom_90_day_reminder_sent),
#                 "day_180_date": str(day_180_date),
#                 "day_180_status": r.custom_180_days_status or "Not Done Yet",
#                 "day_180_reminder_sent": bool(r.custom_180_day_reminder_sent),
#                 "day_270_date": str(day_270_date),
#                 "day_270_status": r.custom_270_days_status or "Not Done Yet",
#                 "day_270_reminder_sent": bool(r.custom_270_day_reminder_sent),
#                 "day_365_date": str(day_365_date),
#                 "day_365_status": r.custom_365_days_status or "Not Done Yet",
#                 "day_365_reminder_sent": bool(r.custom_365_day_reminder_sent),
#                 "confirmation_status": r.custom_confirmation_status or "Not Confirmed",
#             })

#         return {"message": "success", "data": result, "total": len(result)}

#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), "HR Connect Track Fetch Failed")
#         return {"message": "error", "data": [], "error": str(e)}


# @frappe.whitelist()
# def update_hr_connect_status():
#     """
#     Update one status field on the candidate's Joining Confirmation record.

#     field_type: '30_day' | '90_day' | '180_day' | '270_day' | '365_day' | 'confirmation'
#     value:      the new dropdown value selected by HR
#     """
#     try:
#         data = frappe.local.form_dict
#         candidate_id = data.get("candidate_id")
#         field_type = data.get("field_type")
#         value = data.get("value")

#         if not candidate_id:
#             return {"success": False, "message": "Candidate ID is required"}

#         field_map = {
#             "30_day": "custom_30_days_status",
#             "90_day": "custom_90_days_status",
#             "180_day": "custom_180_days_status",
#             "270_day": "custom_270_days_status",
#             "365_day": "custom_365_days_status",
#             "confirmation": "custom_confirmation_status",
#         }
#         fieldname = field_map.get(field_type)
#         if not fieldname:
#             return {"success": False, "message": "Invalid field_type"}

#         # Give a clear message instead of a raw SQL error if the custom
#         # field hasn't been created in Frappe yet.
#         meta = frappe.get_meta("Joining Confirmation")
#         if not meta.has_field(fieldname):
#             return {
#                 "success": False,
#                 "message": (
#                     f"Field '{fieldname}' does not exist on Joining Confirmation yet. "
#                     "Please create it in Frappe: Setup → Customize Form → Joining Confirmation."
#                 ),
#             }

#         existing = frappe.get_all(
#             "Joining Confirmation",
#             filters={"candidate_id": candidate_id},
#             fields=["name"],
#         )
#         if not existing:
#             return {"success": False, "message": "Joining Confirmation record not found"}

#         # NEW: Permission check — dynamic Role Permissions Manager settings ke hisaab se.
#         # frappe.db.set_value neeche seedha DB write karta hai aur permission engine ko
#         # bypass kar deta hai, isliye yaha explicit check zaroori hai.
#         if not frappe.has_permission("Joining Confirmation", ptype="write", doc=existing[0].name):
#             return {"success": False, "message": "You do not have permission to update this record"}

#         frappe.db.set_value("Joining Confirmation", existing[0].name, fieldname, value)
#         frappe.db.commit()

#         return {"success": True, "message": f"{fieldname} updated successfully"}

#     except Exception as e:
#         frappe.log_error(str(e), "HR Connect Status Update Failed")
#         frappe.db.rollback()
#         return {"success": False, "message": str(e)}


import frappe


@frappe.whitelist()
def get_hr_connect_list():
    """
    Get all candidates who have actually joined (Joining Confirmation.join = 1),
    along with their 30/90/180/270/365 day HR Connect dates, statuses, remarks,
    and the dynamic dropdown options for each status field (read straight from
    the Frappe field's Select options, instead of being hardcoded on the
    frontend).

    30/90/180/270/365 day dates are calculated from custom_date_of_joining.
    Status (Done / Not Done Yet / ... whatever is configured) and Confirmation
    Status are manually set by HR from the frontend. Remarks are free text,
    one per stage, also set by HR from the frontend.
    """
    try:
        # Only request custom fields if they actually exist on the doctype
        # yet. This way the list still works even before every custom field
        # has been created in Frappe.
        meta = frappe.get_meta("Joining Confirmation")
        optional_fields = [
            "custom_30_days_status",
            "custom_90_days_status",
            "custom_180_days_status",
            "custom_270_days_status",
            "custom_365_days_status",
            "custom_confirmation_status",
            "custom_30_day_reminder_sent",
            "custom_90_day_reminder_sent",
            "custom_180_day_reminder_sent",
            "custom_270_day_reminder_sent",
            "custom_365_day_reminder_sent",
            "custom_30_days_remark",
            "custom_90_days_remark",
            "custom_180_days_remark",
            "custom_270_days_remark",
            "custom_365_days_remark",
        ]
        existing_optional = [f for f in optional_fields if meta.has_field(f)]

        base_fields = ["name", "candidate_id", "custom_date_of_joining"]
        fields = base_fields + existing_optional

        records = frappe.get_all(
            "Joining Confirmation",
            filters={"join": 1},
            fields=fields,
            order_by="custom_date_of_joining desc",
        )

        # ── Dynamic status options ──────────────────────────────────────
        # Read the actual configured options for each Select field from
        # Frappe's meta, instead of hardcoding "Not Done Yet" / "Done" on
        # the frontend. If a field has 2 options, 3 options, or different
        # wording altogether, the UI will always match Frappe.
        status_option_fields = {
            "day_30": "custom_30_days_status",
            "day_90": "custom_90_days_status",
            "day_180": "custom_180_days_status",
            "day_270": "custom_270_days_status",
            "day_365": "custom_365_days_status",
            "confirmation": "custom_confirmation_status",
        }
        field_options = {}
        for key, fieldname in status_option_fields.items():
            if meta.has_field(fieldname):
                df = meta.get_field(fieldname)
                field_options[key] = [
                    o.strip() for o in (df.options or "").split("\n") if o.strip()
                ]
            else:
                field_options[key] = []

        if not records:
            return {"message": "success", "data": [], "options": field_options}

        candidate_ids = [r.candidate_id for r in records if r.candidate_id]

        applicants = frappe.get_all(
            "Job Applicant",
            filters={"name": ["in", candidate_ids]},
            fields=["name", "applicant_name", "email_id", "phone_number"],
        )
        applicant_map = {a.name: a for a in applicants}

        offers = frappe.get_all(
            "Job Offer",
            filters={"job_applicant": ["in", candidate_ids]},
            fields=["job_applicant", "designation", "custom_grade"],
        )
        offer_map = {o.job_applicant: o for o in offers}

        result = []
        for r in records:
            # Without a joining date we cannot calculate 30/90/180/270/365 day connects
            if not r.custom_date_of_joining:
                continue

            applicant = applicant_map.get(r.candidate_id, {}) or {}
            offer = offer_map.get(r.candidate_id, {}) or {}

            doj = frappe.utils.getdate(r.custom_date_of_joining)
            day_30_date = frappe.utils.add_days(doj, 30)
            day_90_date = frappe.utils.add_days(doj, 90)
            day_180_date = frappe.utils.add_days(doj, 180)
            day_270_date = frappe.utils.add_days(doj, 270)
            day_365_date = frappe.utils.add_days(doj, 365)

            result.append({
                "candidate_id": r.candidate_id,
                "applicant_name": applicant.get("applicant_name", ""),
                "email": applicant.get("email_id", ""),
                "phone": applicant.get("phone_number", ""),
                "designation": offer.get("designation", "") or "",
                "grade": offer.get("custom_grade", "") or "",
                "date_of_joining": str(doj),
                "day_30_date": str(day_30_date),
                "day_30_status": r.custom_30_days_status or "Not Done Yet",
                "day_30_reminder_sent": bool(r.custom_30_day_reminder_sent),
                "day_30_remark": r.custom_30_days_remark or "",
                "day_90_date": str(day_90_date),
                "day_90_status": r.custom_90_days_status or "Not Done Yet",
                "day_90_reminder_sent": bool(r.custom_90_day_reminder_sent),
                "day_90_remark": r.custom_90_days_remark or "",
                "day_180_date": str(day_180_date),
                "day_180_status": r.custom_180_days_status or "Not Done Yet",
                "day_180_reminder_sent": bool(r.custom_180_day_reminder_sent),
                "day_180_remark": r.custom_180_days_remark or "",
                "day_270_date": str(day_270_date),
                "day_270_status": r.custom_270_days_status or "Not Done Yet",
                "day_270_reminder_sent": bool(r.custom_270_day_reminder_sent),
                "day_270_remark": r.custom_270_days_remark or "",
                "day_365_date": str(day_365_date),
                "day_365_status": r.custom_365_days_status or "Not Done Yet",
                "day_365_reminder_sent": bool(r.custom_365_day_reminder_sent),
                "day_365_remark": r.custom_365_days_remark or "",
                "confirmation_status": r.custom_confirmation_status or "Not Confirmed",
            })

        return {
            "message": "success",
            "data": result,
            "total": len(result),
            "options": field_options,
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "HR Connect Track Fetch Failed")
        return {"message": "error", "data": [], "error": str(e)}


@frappe.whitelist()
def update_hr_connect_status():
    """
    Update one status field on the candidate's Joining Confirmation record.

    field_type: '30_day' | '90_day' | '180_day' | '270_day' | '365_day' | 'confirmation'
    value:      the new dropdown value selected by HR
    """
    try:
        data = frappe.local.form_dict
        candidate_id = data.get("candidate_id")
        field_type = data.get("field_type")
        value = data.get("value")

        if not candidate_id:
            return {"success": False, "message": "Candidate ID is required"}

        field_map = {
            "30_day": "custom_30_days_status",
            "90_day": "custom_90_days_status",
            "180_day": "custom_180_days_status",
            "270_day": "custom_270_days_status",
            "365_day": "custom_365_days_status",
            "confirmation": "custom_confirmation_status",
        }
        fieldname = field_map.get(field_type)
        if not fieldname:
            return {"success": False, "message": "Invalid field_type"}

        # Give a clear message instead of a raw SQL error if the custom
        # field hasn't been created in Frappe yet.
        meta = frappe.get_meta("Joining Confirmation")
        if not meta.has_field(fieldname):
            return {
                "success": False,
                "message": (
                    f"Field '{fieldname}' does not exist on Joining Confirmation yet. "
                    "Please create it in Frappe: Setup → Customize Form → Joining Confirmation."
                ),
            }

        existing = frappe.get_all(
            "Joining Confirmation",
            filters={"candidate_id": candidate_id},
            fields=["name"],
        )
        if not existing:
            return {"success": False, "message": "Joining Confirmation record not found"}

        # NEW: Permission check — dynamic Role Permissions Manager settings ke hisaab se.
        # frappe.db.set_value neeche seedha DB write karta hai aur permission engine ko
        # bypass kar deta hai, isliye yaha explicit check zaroori hai.
        if not frappe.has_permission("Joining Confirmation", ptype="write", doc=existing[0].name):
            return {"success": False, "message": "You do not have permission to update this record"}

        frappe.db.set_value("Joining Confirmation", existing[0].name, fieldname, value)
        frappe.db.commit()

        return {"success": True, "message": f"{fieldname} updated successfully"}

    except Exception as e:
        frappe.log_error(str(e), "HR Connect Status Update Failed")
        frappe.db.rollback()
        return {"success": False, "message": str(e)}


@frappe.whitelist()
def update_hr_connect_remark():
    """
    Update the remark text for one HR Connect stage (30/90/180/270/365 day)
    on the candidate's Joining Confirmation record.

    field_type: '30_day' | '90_day' | '180_day' | '270_day' | '365_day'
    remark:     free text typed by HR
    """
    try:
        data = frappe.local.form_dict
        candidate_id = data.get("candidate_id")
        field_type = data.get("field_type")
        remark = data.get("remark", "")

        if not candidate_id:
            return {"success": False, "message": "Candidate ID is required"}

        field_map = {
            "30_day": "custom_30_days_remark",
            "90_day": "custom_90_days_remark",
            "180_day": "custom_180_days_remark",
            "270_day": "custom_270_days_remark",
            "365_day": "custom_365_days_remark",
        }
        fieldname = field_map.get(field_type)
        if not fieldname:
            return {"success": False, "message": "Invalid field_type"}

        # Give a clear message instead of a raw SQL error if the custom
        # field hasn't been created in Frappe yet.
        meta = frappe.get_meta("Joining Confirmation")
        if not meta.has_field(fieldname):
            return {
                "success": False,
                "message": (
                    f"Field '{fieldname}' does not exist on Joining Confirmation yet. "
                    "Please create it in Frappe: Setup → Customize Form → Joining Confirmation."
                ),
            }

        existing = frappe.get_all(
            "Joining Confirmation",
            filters={"candidate_id": candidate_id},
            fields=["name"],
        )
        if not existing:
            return {"success": False, "message": "Joining Confirmation record not found"}

        # Same permission check as update_hr_connect_status, for consistency —
        # frappe.db.set_value bypasses the permission engine, so we check first.
        if not frappe.has_permission("Joining Confirmation", ptype="write", doc=existing[0].name):
            return {"success": False, "message": "You do not have permission to update this record"}

        frappe.db.set_value("Joining Confirmation", existing[0].name, fieldname, remark)
        frappe.db.commit()

        return {"success": True, "message": f"{fieldname} updated successfully"}

    except Exception as e:
        frappe.log_error(str(e), "HR Connect Remark Update Failed")
        frappe.db.rollback()
        return {"success": False, "message": str(e)}
    