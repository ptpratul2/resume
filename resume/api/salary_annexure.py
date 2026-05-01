import frappe
import json


@frappe.whitelist(allow_guest=True)
def create_salary_annexure(data):
    """Create a new Salary Annexure document"""
    try:
        if isinstance(data, str):
            data = json.loads(data)

        frappe.logger().info(f"Creating Salary Annexure with data: {data}")

        # Validate required fields
        if not data.get("custom_job_applicant"):
            return {"success": False, "message": "Job Applicant is required"}

        doc = frappe.get_doc({
            "doctype": "Salary Annexure",
            "custom_job_applicant": data.get("custom_job_applicant"),
            "custom_salary_component_template": data.get("custom_salary_component_template", ""),
            "custom_condition_template": data.get("custom_condition_template", ""),
            "subtotal_a_monthly": data.get("subtotal_a_monthly", 0),
            "subtotal_a_annual": data.get("subtotal_a_annual", 0),
            "subtotal_b_monthly": data.get("subtotal_b_monthly", 0),
            "subtotal_b_annual": data.get("subtotal_b_annual", 0),
            "total_monthly": data.get("total_monthly", 0),
            "total_annual": data.get("total_annual", 0),
        })

        # Add salary components
        salary_components = data.get("salary_components", [])
        if isinstance(salary_components, str):
            salary_components = json.loads(salary_components)

        for comp in salary_components:
            doc.append("salary_components", {
                "salary_component": comp.get("salary_component"),
                "section": comp.get("section", "A"),
                "monthly": comp.get("monthly", 0),
                "annualized": comp.get("annualized", 0),
            })

        # Add conditions
        conditions = data.get("conditions", [])
        if isinstance(conditions, str):
            conditions = json.loads(conditions)

        for cond in conditions:
            if cond.get("condition_text"):
                doc.append("custom_terms_and_condtions", {
                    "condition_text": cond.get("condition_text"),
                })

        doc.insert(ignore_permissions=True)
        frappe.db.commit()

        frappe.logger().info(f"Created Salary Annexure: {doc.name}")

        return {
            "success": True,
            "message": f"Salary Annexure {doc.name} created successfully.",
            "data": {"name": doc.name}
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
            "Salary Component Template",
            fields=["name"],
            order_by="name"
        )
        return {"message": "Templates fetched successfully", "data": templates}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Salary Component Templates Fetch Failed")
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
                components.append({
                    "salary_component": row.salary_component,
                    "section": getattr(row, "section", "A"),
                })

        return {"message": "Components fetched", "data": components}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Template Components Fetch Failed")
        return {"message": "No components found", "data": []}


@frappe.whitelist(allow_guest=True)
def get_condition_templates():
    """Get list of Salary Annexure Condition Templates"""
    try:
        templates = frappe.get_all(
            "Salary Annexure Condition Template",
            fields=["name"],
            order_by="name"
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
                rows.append({
                    "condition_text": getattr(row, "condition_text", ""),
                })

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
                "name", "custom_job_applicant", "custom_salary_component_template",
                "subtotal_a_monthly", "subtotal_a_annual",
                "subtotal_b_monthly", "subtotal_b_annual",
                "total_monthly", "total_annual",
                "docstatus", "creation", "modified"
            ],
            order_by="creation desc"
        )

        # Resolve applicant name
        for item in annexures:
            if item.get("custom_job_applicant"):
                try:
                    applicant = frappe.get_value(
                        "Job Applicant",
                        item["custom_job_applicant"],
                        ["applicant_name", "email_id"],
                        as_dict=True
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
        for row in (doc.salary_components or []):
            components.append({
                "salary_component": row.salary_component,
                "section": row.section,
                "monthly": row.monthly,
                "annualized": row.annualized,
            })
        doc_dict["salary_components"] = components

        # Flatten conditions child table
        conditions = []
        for row in (doc.get("custom_terms_and_condtions") or []):
            conditions.append({"condition_text": row.condition_text})
        doc_dict["conditions"] = conditions

        return {"success": True, "data": doc_dict}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Salary Annexure Details Fetch Failed")
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def delete_salary_annexure(annexure_name):
    """Delete a Salary Annexure document"""
    try:
        if not annexure_name:
            return {"success": False, "message": "Annexure name is required"}

        frappe.delete_doc("Salary Annexure", annexure_name, ignore_permissions=True)
        frappe.db.commit()

        return {"success": True, "message": f"Salary Annexure {annexure_name} deleted successfully"}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Salary Annexure Deletion Failed")
        return {"success": False, "message": str(e)}


    