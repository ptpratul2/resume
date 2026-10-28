# import frappe
# import json


# @frappe.whitelist()  # CHANGED: allow_guest=True hataya — ye function Salary Annexure record create karta hai
# def create_salary_annexure(data):
#     """Create a new Salary Annexure document"""
#     try:
#         if isinstance(data, str):
#             data = json.loads(data)

#         frappe.logger().info(f"Creating Salary Annexure with data: {data}")

#         # Validate required fields
#         if not data.get("custom_job_applicant"):
#             return {"success": False, "message": "Job Applicant is required"}

#         # NEW: Permission check — dynamic Role Permissions Manager settings ke hisaab se.
#         if not frappe.has_permission("Salary Annexure", ptype="create"):
#             return {"success": False, "message": "You do not have permission to create Salary Annexure"}

#         doc = frappe.get_doc({
#             "doctype": "Salary Annexure",
#             "custom_job_applicant": data.get("custom_job_applicant"),
#             "custom_salary_component_template": data.get("custom_salary_component_template", ""),
#             "custom_condition_template": data.get("custom_condition_template", ""),
#             "subtotal_a_monthly": data.get("subtotal_a_monthly", 0),
#             "subtotal_a_annual": data.get("subtotal_a_annual", 0),
#             "subtotal_b_monthly": data.get("subtotal_b_monthly", 0),
#             "subtotal_b_annual": data.get("subtotal_b_annual", 0),
#             "total_monthly": data.get("total_monthly", 0),
#             "total_annual": data.get("total_annual", 0),
#         })

#         # Add salary components
#         salary_components = data.get("salary_components", [])
#         if isinstance(salary_components, str):
#             salary_components = json.loads(salary_components)

#         for comp in salary_components:
#             doc.append("salary_components", {
#                 "salary_component": comp.get("salary_component"),
#                 "section": comp.get("section", "A"),
#                 "monthly": comp.get("monthly", 0),
#                 "annualized": comp.get("annualized", 0),
#             })

#         # Add conditions
#         conditions = data.get("conditions", [])
#         if isinstance(conditions, str):
#             conditions = json.loads(conditions)

#         for cond in conditions:
#             if cond.get("condition_text"):
#                 doc.append("custom_terms_and_condtions", {
#                     "condition_text": cond.get("condition_text"),
#                 })

#         doc.insert(ignore_permissions=False)  # CHANGED: True se False kiya, taaki Frappe ka internal permission engine bhi check kare (double-safety)
#         frappe.db.commit()

#         frappe.logger().info(f"Created Salary Annexure: {doc.name}")

#         return {
#             "success": True,
#             "message": f"Salary Annexure {doc.name} created successfully.",
#             "data": {"name": doc.name}
#         }

#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), "Salary Annexure Creation Failed")
#         frappe.db.rollback()
#         return {"success": False, "message": str(e)}


# @frappe.whitelist(allow_guest=True)
# def get_salary_component_templates():
#     """Get list of Salary Component Templates (Salary Structure)"""
#     try:
#         templates = frappe.get_all(
#             "Salary Component Template",
#             fields=["name"],
#             order_by="name"
#         )
#         return {"message": "Templates fetched successfully", "data": templates}
#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), "Salary Component Templates Fetch Failed")
#         return {"message": "No templates found", "data": []}


# @frappe.whitelist(allow_guest=True)
# def get_template_components(template_name):
#     """
#     Get salary components from a Salary Component Template.
#     Returns component name + section so the UI can populate the child table.
#     """
#     try:
#         if not template_name:
#             return {"message": "Template name required", "data": []}

#         template = frappe.get_doc("Salary Component Template", template_name)

#         components = []
#         if hasattr(template, "template_components"):
#             for row in template.template_components:
#                 components.append({
#                     "salary_component": row.salary_component,
#                     "section": getattr(row, "section", "A"),
#                 })

#         return {"message": "Components fetched", "data": components}
#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), "Template Components Fetch Failed")
#         return {"message": "No components found", "data": []}


# @frappe.whitelist(allow_guest=True)
# def get_condition_templates():
#     """Get list of Salary Annexure Condition Templates"""
#     try:
#         templates = frappe.get_all(
#             "Salary Annexure Condition Template",
#             fields=["name"],
#             order_by="name"
#         )
#         return {"message": "Condition templates fetched", "data": templates}
#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), "Condition Templates Fetch Failed")
#         return {"message": "No condition templates found", "data": []}


# @frappe.whitelist(allow_guest=True)
# def get_condition_template_rows(template_name):
#     """
#     Get condition rows from a Salary Annexure Condition Template.
#     """
#     try:
#         if not template_name:
#             return {"message": "Template name required", "data": []}

#         template = frappe.get_doc("Salary Annexure Condition Template", template_name)

#         rows = []
#         if hasattr(template, "conditions"):
#             for row in template.conditions:
#                 rows.append({
#                     "condition_text": getattr(row, "condition_text", ""),
#                 })

#         return {"message": "Conditions fetched", "data": rows}
#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), "Condition Template Rows Fetch Failed")
#         return {"message": "No conditions found", "data": []}


# @frappe.whitelist(allow_guest=True)
# def get_salary_annexure_list():
#     """Get list of all Salary Annexures"""
#     try:
#         annexures = frappe.get_all(
#             "Salary Annexure",
#             fields=[
#                 "name", "custom_job_applicant", "custom_salary_component_template",
#                 "subtotal_a_monthly", "subtotal_a_annual",
#                 "subtotal_b_monthly", "subtotal_b_annual",
#                 "total_monthly", "total_annual",
#                 "docstatus", "creation", "modified",
#                 "owner",
#             ],
#             order_by="creation desc"
#         )

#         # Resolve applicant name
#         for item in annexures:
#             if item.get("custom_job_applicant"):
#                 try:
#                     applicant = frappe.get_value(
#                         "Job Applicant",
#                         item["custom_job_applicant"],
#                         ["applicant_name", "email_id"],
#                         as_dict=True
#                     )
#                     if applicant:
#                         item["applicant_name"] = applicant.applicant_name
#                         item["applicant_email"] = applicant.email_id
#                 except Exception:
#                     item["applicant_name"] = item["custom_job_applicant"]

#         return {"message": "Salary annexures fetched", "data": annexures}
#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), "Salary Annexure List Fetch Failed")
#         return {"message": str(e), "data": []}


# @frappe.whitelist(allow_guest=True)
# def get_salary_annexure_details(annexure_name):
#     """Get full details of a single Salary Annexure"""
#     try:
#         if not annexure_name:
#             return {"success": False, "message": "Annexure name is required"}

#         doc = frappe.get_doc("Salary Annexure", annexure_name)
#         doc_dict = doc.as_dict()

#         # Flatten salary_components child table
#         components = []
#         for row in (doc.salary_components or []):
#             components.append({
#                 "salary_component": row.salary_component,
#                 "section": row.section,
#                 "monthly": row.monthly,
#                 "annualized": row.annualized,
#             })
#         doc_dict["salary_components"] = components

#         # Flatten conditions child table
#         conditions = []
#         for row in (doc.get("custom_terms_and_condtions") or []):
#             conditions.append({"condition_text": row.condition_text})
#         doc_dict["conditions"] = conditions

#         return {"success": True, "data": doc_dict}
#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), "Salary Annexure Details Fetch Failed")
#         return {"success": False, "message": str(e)}


# @frappe.whitelist()  # CHANGED: allow_guest=True hataya — ye function Salary Annexure record delete karta hai
# def delete_salary_annexure(annexure_name):
#     """Delete a Salary Annexure document"""
#     try:
#         if not annexure_name:
#             return {"success": False, "message": "Annexure name is required"}

#         # NEW: Permission check — dynamic Role Permissions Manager settings ke hisaab se.
#         if not frappe.has_permission("Salary Annexure", ptype="delete", doc=annexure_name):
#             return {"success": False, "message": "You do not have permission to delete this Salary Annexure"}

#         frappe.delete_doc("Salary Annexure", annexure_name, ignore_permissions=False)  # CHANGED: True se False kiya, taaki Frappe ka internal permission engine bhi check kare (double-safety)
#         frappe.db.commit()

#         return {"success": True, "message": f"Salary Annexure {annexure_name} deleted successfully"}
#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), "Salary Annexure Deletion Failed")
#         return {"success": False, "message": str(e)}


import frappe
import json


def _get_feedback_status_for_applicant(job_applicant):
    """
    Checks whether this Job Applicant has a Candidate Feedback
    (Interview Feedback) submitted with result = 'Cleared'.

    A Job Applicant can have multiple Interviews (multiple rounds), and each
    Interview can have one Interview Feedback. We consider the candidate
    eligible for a Salary Annexure if ANY of their feedback records has
    result == 'Cleared'.
    """
    if not job_applicant:
        return {"cleared": False, "reason": "No Job Applicant provided."}

    interview_names = frappe.get_all(
        "Interview",
        filters={"job_applicant": job_applicant},
        pluck="name",
    )

    if not interview_names:
        return {
            "cleared": False,
            "reason": (
                "No interview found for this candidate. Candidate Feedback "
                "must be submitted with result 'Cleared' before creating a "
                "Salary Annexure."
            ),
        }

    feedbacks = frappe.get_all(
        "Interview Feedback",
        filters={"interview": ["in", interview_names]},
        fields=["name", "result"],
        order_by="creation desc",
    )

    if not feedbacks:
        return {
            "cleared": False,
            "reason": (
                "Candidate Feedback has not been submitted yet. Please "
                "complete the Candidate Feedback (with result 'Cleared') "
                "before creating a Salary Annexure."
            ),
        }

    is_cleared = any((f.result or "").strip().lower() == "cleared" for f in feedbacks)

    if not is_cleared:
        return {
            "cleared": False,
            "reason": (
                "Candidate Feedback result is not 'Cleared'. Salary Annexure "
                "can only be created once the Candidate Feedback result is "
                "'Cleared'."
            ),
        }

    return {"cleared": True, "reason": ""}


@frappe.whitelist(allow_guest=True)
def check_candidate_feedback_status(job_applicant):
    """
    Frontend-facing check: lets the Salary Annexure form show a live
    warning/success banner as soon as a Job Applicant is selected, before
    the person fills the rest of the form.
    """
    try:
        status = _get_feedback_status_for_applicant(job_applicant)
        return {"message": "Success", "data": status}
    except Exception as e:
        frappe.log_error(
            frappe.get_traceback(), "Check Candidate Feedback Status Failed"
        )
        return {"message": "Error", "data": {"cleared": False, "reason": str(e)}}


@frappe.whitelist()  # CHANGED: allow_guest=True hataya — ye function Salary Annexure record create karta hai
def create_salary_annexure(data):
    """Create a new Salary Annexure document"""
    try:
        if isinstance(data, str):
            data = json.loads(data)

        frappe.logger().info(f"Creating Salary Annexure with data: {data}")

        # Validate required fields
        if not data.get("custom_job_applicant"):
            return {"success": False, "message": "Job Applicant is required"}

        # NEW: Permission check — dynamic Role Permissions Manager settings ke hisaab se.
        if not frappe.has_permission("Salary Annexure", ptype="create"):
            return {
                "success": False,
                "message": "You do not have permission to create Salary Annexure",
            }

        # NEW: Candidate Feedback gate — Salary Annexure can only be created once
        # the candidate's Interview Feedback has result = 'Cleared'. This is a
        # hard server-side check so it cannot be bypassed even if the frontend
        # is skipped or the API is called directly.
        feedback_status = _get_feedback_status_for_applicant(
            data.get("custom_job_applicant")
        )
        if not feedback_status.get("cleared"):
            return {
                "success": False,
                "message": feedback_status.get("reason")
                or "Candidate Feedback must be completed with result 'Cleared' before creating a Salary Annexure.",
            }

        doc = frappe.get_doc(
            {
                "doctype": "Salary Annexure",
                "custom_job_applicant": data.get("custom_job_applicant"),
                "custom_salary_component_template": data.get(
                    "custom_salary_component_template", ""
                ),
                "custom_condition_template": data.get("custom_condition_template", ""),
                "subtotal_a_monthly": data.get("subtotal_a_monthly", 0),
                "subtotal_a_annual": data.get("subtotal_a_annual", 0),
                "subtotal_b_monthly": data.get("subtotal_b_monthly", 0),
                "subtotal_b_annual": data.get("subtotal_b_annual", 0),
                "total_monthly": data.get("total_monthly", 0),
                "total_annual": data.get("total_annual", 0),
            }
        )

        # Add salary components
        salary_components = data.get("salary_components", [])
        if isinstance(salary_components, str):
            salary_components = json.loads(salary_components)

        for comp in salary_components:
            doc.append(
                "salary_components",
                {
                    "salary_component": comp.get("salary_component"),
                    "section": comp.get("section", "A"),
                    "monthly": comp.get("monthly", 0),
                    "annualized": comp.get("annualized", 0),
                },
            )

        # Add conditions
        conditions = data.get("conditions", [])
        if isinstance(conditions, str):
            conditions = json.loads(conditions)

        for cond in conditions:
            if cond.get("condition_text"):
                doc.append(
                    "custom_terms_and_condtions",
                    {
                        "condition_text": cond.get("condition_text"),
                    },
                )

        doc.insert(
            ignore_permissions=False
        )  # CHANGED: True se False kiya, taaki Frappe ka internal permission engine bhi check kare (double-safety)
        frappe.db.commit()

        frappe.logger().info(f"Created Salary Annexure: {doc.name}")

        return {
            "success": True,
            "message": f"Salary Annexure {doc.name} created successfully.",
            "data": {"name": doc.name},
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Salary Annexure Creation Failed")
        frappe.db.rollback()
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def get_salary_component_templates():
    """Get list of Salary Component Templates (Salary Structure)"""
    try:
        templates = frappe.get_all(
            "Salary Component Template", fields=["name"], order_by="name"
        )
        return {"message": "Templates fetched successfully", "data": templates}
    except Exception as e:
        frappe.log_error(
            frappe.get_traceback(), "Salary Component Templates Fetch Failed"
        )
        return {"message": "No templates found", "data": []}


@frappe.whitelist(allow_guest=True)
def get_template_components(template_name):
    """
    Get salary components from a Salary Component Template.
    Returns component name + section so the UI can populate the child table.
    """
    try:
        if not template_name:
            return {"message": "Template name required", "data": []}

        template = frappe.get_doc("Salary Component Template", template_name)

        components = []
        if hasattr(template, "template_components"):
            for row in template.template_components:
                components.append(
                    {
                        "salary_component": row.salary_component,
                        "section": getattr(row, "section", "A"),
                    }
                )

        return {"message": "Components fetched", "data": components}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Template Components Fetch Failed")
        return {"message": "No components found", "data": []}


@frappe.whitelist(allow_guest=True)
def get_condition_templates():
    """Get list of Salary Annexure Condition Templates"""
    try:
        templates = frappe.get_all(
            "Salary Annexure Condition Template", fields=["name"], order_by="name"
        )
        return {"message": "Condition templates fetched", "data": templates}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Condition Templates Fetch Failed")
        return {"message": "No condition templates found", "data": []}


@frappe.whitelist(allow_guest=True)
def get_condition_template_rows(template_name):
    """
    Get condition rows from a Salary Annexure Condition Template.
    """
    try:
        if not template_name:
            return {"message": "Template name required", "data": []}

        template = frappe.get_doc("Salary Annexure Condition Template", template_name)

        rows = []
        if hasattr(template, "conditions"):
            for row in template.conditions:
                rows.append(
                    {
                        "condition_text": getattr(row, "condition_text", ""),
                    }
                )

        return {"message": "Conditions fetched", "data": rows}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Condition Template Rows Fetch Failed")
        return {"message": "No conditions found", "data": []}


@frappe.whitelist(allow_guest=True)
def get_salary_annexure_list():
    """Get list of all Salary Annexures"""
    try:
        annexures = frappe.get_all(
            "Salary Annexure",
            fields=[
                "name",
                "custom_job_applicant",
                "custom_salary_component_template",
                "subtotal_a_monthly",
                "subtotal_a_annual",
                "subtotal_b_monthly",
                "subtotal_b_annual",
                "total_monthly",
                "total_annual",
                "docstatus",
                "creation",
                "modified",
                "owner",
                "modified_by",
                "last_change_summary",
            ],
            order_by="creation desc",
        )

        # Resolve applicant name
        for item in annexures:
            if not item.get("last_change_summary"):
                try:
                    c = frappe.db.get_value(
                        "Comment",
                        {
                            "reference_doctype": "Salary Annexure",
                            "reference_name": item["name"],
                            "comment_type": "Comment",
                        },
                        "content",
                        order_by="creation desc",
                    )
                    if c:
                        clean_c = c.replace("<p>", "").replace("</p>", "").strip()
                        if ":" in clean_c:
                            clean_c = clean_c.split(":", 1)[1].strip()
                        item["last_change_summary"] = clean_c
                except Exception:
                    pass
            if item.get("custom_job_applicant"):
                try:
                    applicant = frappe.get_value(
                        "Job Applicant",
                        item["custom_job_applicant"],
                        ["applicant_name", "email_id"],
                        as_dict=True,
                    )
                    if applicant:
                        item["applicant_name"] = applicant.applicant_name
                        item["applicant_email"] = applicant.email_id
                except Exception:
                    item["applicant_name"] = item["custom_job_applicant"]

        return {"message": "Salary annexures fetched", "data": annexures}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Salary Annexure List Fetch Failed")
        return {"message": str(e), "data": []}


@frappe.whitelist(allow_guest=True)
def get_salary_annexure_details(annexure_name):
    """Get full details of a single Salary Annexure"""
    try:
        if not annexure_name:
            return {"success": False, "message": "Annexure name is required"}

        doc = frappe.get_doc("Salary Annexure", annexure_name)
        doc_dict = doc.as_dict()

        # Flatten salary_components child table
        components = []
        for row in doc.salary_components or []:
            components.append(
                {
                    "salary_component": row.salary_component,
                    "section": row.section,
                    "monthly": row.monthly,
                    "annualized": row.annualized,
                }
            )
        doc_dict["salary_components"] = components

        # Flatten conditions child table
        conditions = []
        for row in doc.get("custom_terms_and_condtions") or []:
            conditions.append({"condition_text": row.condition_text})
        doc_dict["conditions"] = conditions

        return {"success": True, "data": doc_dict}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Salary Annexure Details Fetch Failed")
        return {"success": False, "message": str(e)}


@frappe.whitelist()  # CHANGED: allow_guest=True hataya — ye function Salary Annexure record delete karta hai
def delete_salary_annexure(annexure_name):
    """Delete a Salary Annexure document"""
    try:
        if not annexure_name:
            return {"success": False, "message": "Annexure name is required"}

        # NEW: Permission check — dynamic Role Permissions Manager settings ke hisaab se.
        if not frappe.has_permission(
            "Salary Annexure", ptype="delete", doc=annexure_name
        ):
            return {
                "success": False,
                "message": "You do not have permission to delete this Salary Annexure",
            }

        frappe.delete_doc(
            "Salary Annexure", annexure_name, ignore_permissions=False
        )  # CHANGED: True se False kiya, taaki Frappe ka internal permission engine bhi check kare (double-safety)
        frappe.db.commit()

        return {
            "success": True,
            "message": f"Salary Annexure {annexure_name} deleted successfully",
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Salary Annexure Deletion Failed")
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def get_annexure_by_applicant(job_applicant):
    """Check if a salary annexure exists for this job applicant and return full details"""
    try:
        if not job_applicant:
            return {
                "success": False,
                "exists": False,
                "message": "Applicant is required",
            }
        annexure_name = frappe.db.get_value(
            "Salary Annexure", {"custom_job_applicant": job_applicant}, "name"
        )
        if not annexure_name:
            return {"success": True, "exists": False, "message": "No existing annexure"}
        details = get_salary_annexure_details(annexure_name)
        if details.get("success"):
            return {"success": True, "exists": True, "data": details.get("data")}
        return {"success": False, "exists": True, "message": "Failed to load details"}
    except Exception as e:
        frappe.log_error(
            frappe.get_traceback(), "Failed to fetch annexure by applicant"
        )
        return {"success": False, "message": str(e)}


@frappe.whitelist()
def update_salary_annexure(data):
    """Update an existing Salary Annexure with precise component-level change tracking"""
    try:
        if isinstance(data, str):
            data = json.loads(data)
        annexure_name = data.get("name") or data.get("annexure_name")
        if not annexure_name:
            return {"success": False, "message": "Salary Annexure name is required"}
        if not frappe.db.exists("Salary Annexure", annexure_name):
            return {
                "success": False,
                "message": f"Salary Annexure {annexure_name} not found",
            }
        if not frappe.has_permission(
            "Salary Annexure", ptype="write", doc=annexure_name
        ):
            return {
                "success": False,
                "message": "You do not have permission to edit this Salary Annexure",
            }
        doc = frappe.get_doc("Salary Annexure", annexure_name)
        editor = frappe.session.user or "Unknown"
        editor_name = (
            frappe.db.get_value("User", editor, "full_name") or editor.split("@")[0]
        )
        old_monthly = float(doc.total_monthly or 0)
        old_annual = float(doc.total_annual or 0)
        new_monthly = float(data.get("total_monthly", old_monthly))
        new_annual = float(data.get("total_annual", old_annual))
        # Map existing components before modification
        old_comps_map = {}
        for c in doc.get("salary_components") or []:
            c_name = c.salary_component
            if c_name:
                old_comps_map[c_name] = {
                    "monthly": float(c.monthly or 0),
                    "annualized": float(c.annualized or 0),
                }
        # NEW: Map existing conditions before modification (for T&C change tracking)
        old_conds = [
            (c.condition_text or "").strip()
            for c in (doc.get("custom_terms_and_condtions") or [])
            if (c.condition_text or "").strip()
        ]
        # Update totals
        doc.total_monthly = new_monthly
        doc.total_annual = new_annual
        if "subtotal_a_monthly" in data:
            doc.subtotal_a_monthly = float(data.get("subtotal_a_monthly", 0))
        if "subtotal_a_annual" in data:
            doc.subtotal_a_annual = float(data.get("subtotal_a_annual", 0))
        if "subtotal_b_monthly" in data:
            doc.subtotal_b_monthly = float(data.get("subtotal_b_monthly", 0))
        if "subtotal_b_annual" in data:
            doc.subtotal_b_annual = float(data.get("subtotal_b_annual", 0))
        # Compare components to find exactly which ones changed
        comp_changes = []
        seen_comps = set()
        if "salary_components" in data:
            comps = data.get("salary_components")
            if isinstance(comps, str):
                comps = json.loads(comps)
            doc.set("salary_components", [])
            for c in comps:
                c_name = c.get("salary_component")
                if not c_name:
                    continue
                seen_comps.add(c_name)
                m_val = float(c.get("monthly", 0))
                a_val = float(c.get("annualized", 0))
                doc.append(
                    "salary_components",
                    {
                        "salary_component": c_name,
                        "section": c.get("section", "A"),
                        "monthly": m_val,
                        "annualized": a_val,
                    },
                )
                if c_name in old_comps_map:
                    old_m = round(old_comps_map[c_name]["monthly"], 2)
                    if abs(round(m_val, 2) - old_m) > 0.01:
                        comp_changes.append(f"{c_name}: ₹{old_m:,.0f} → ₹{m_val:,.0f}")
                else:
                    comp_changes.append(f"Added {c_name}: ₹{m_val:,.0f}")
            for old_c_name in old_comps_map:
                if old_c_name not in seen_comps:
                    comp_changes.append(f"Removed {old_c_name}")
        # Update terms & conditions (+ NEW: track added / removed conditions)
        cond_changes = []
        if "conditions" in data:
            conds = data.get("conditions")
            if isinstance(conds, str):
                conds = json.loads(conds)
            doc.set("custom_terms_and_condtions", [])
            new_conds = []
            for cond in conds:
                if cond.get("condition_text"):
                    new_conds.append((cond.get("condition_text") or "").strip())
                    doc.append(
                        "custom_terms_and_condtions",
                        {
                            "condition_text": cond.get("condition_text"),
                        },
                    )

            def _short(t):
                # ';' is the summary separator, so replace it inside clause text
                t = t.replace(";", ",")
                return t if len(t) <= 120 else t[:117] + "..."

            old_set, new_set = set(old_conds), set(new_conds)
            for t in new_conds:
                if t and t not in old_set:
                    cond_changes.append(f"Added condition: {_short(t)}")
            for t in old_conds:
                if t not in new_set:
                    cond_changes.append(f"Removed condition: {_short(t)}")
        # Generate summary of exact component + condition changes
        all_changes = comp_changes + cond_changes
        if all_changes:
            change_summary = "; ".join(all_changes)
        elif abs(round(new_annual, 2) - round(old_annual, 2)) > 0.01:
            change_summary = f"CTC changed: ₹{old_annual:,.0f} → ₹{new_annual:,.0f}"
        else:
            change_summary = "No changes made"
        try:
            doc.last_change_summary = change_summary
        except Exception:
            pass
        doc.flags.ignore_permissions = True
        doc.save()
        try:
            frappe.db.set_value(
                "Salary Annexure",
                annexure_name,
                "last_change_summary",
                change_summary,
                update_modified=False,
            )
        except Exception:
            pass
        frappe.db.commit()
        # Add comment for audit log
        comment_text = f"Updated by {editor_name} ({editor}): {change_summary}"
        try:
            doc.add_comment("Comment", text=comment_text)
        except Exception:
            pass
        return {
            "success": True,
            "message": f"Salary Annexure {annexure_name} updated successfully",
            "data": {
                "name": doc.name,
                "modified": str(doc.modified),
                "modified_by": doc.modified_by,
                "last_change_summary": change_summary,
                "changes": change_summary,
            },
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Salary Annexure Update Failed")
        frappe.db.rollback()
        return {"success": False, "message": str(e)}
