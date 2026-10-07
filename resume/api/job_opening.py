import frappe
import frappe.share
from datetime import datetime, timezone
import json

@frappe.whitelist()  # CHANGED: allow_guest=True hataya — guest user ka role-based permission check meaningful nahi hota
def create_job_opening():
    frappe.logger().info("=== CREATE JOB OPENING STARTED ===")
    
    try:
        # NEW STEP 0: Permission check — sabse pehle, dynamic Role Permissions Manager settings ke hisaab se
        if not frappe.has_permission("Job Opening", ptype="create"):
            frappe.logger().error(f"Permission denied for user {frappe.session.user} to create Job Opening")
            return {"success": False, "message": "You do not have permission to create Job Opening"}

        # Step 1: Get data
        frappe.logger().info("Step 1: Getting form data")
        data = frappe.form_dict
        frappe.logger().info(f"Received data: {json.dumps(dict(data), indent=2)}")

        # Step 2: Validate required fields
        frappe.logger().info("Step 2: Validating required fields")
        if not data.get("job_title"):
            frappe.logger().error("Validation failed: job_title missing")
            return {"success": False, "message": "Job title is required"}
        if not data.get("designation"):
            frappe.logger().error("Validation failed: designation missing")
            return {"success": False, "message": "Designation is required"}
        if not data.get("company"):
            frappe.logger().error("Validation failed: company missing")
            return {"success": False, "message": "Company is required"}

        # Step 3: Validate status DYNAMICALLY
        frappe.logger().info("Step 3: Validating status")
        status = data.get("status", "Open")
        
        try:
            meta = frappe.get_meta("Job Opening")
            status_field = meta.get_field("status")
            
            if status_field and status_field.options:
                valid_statuses = [s.strip() for s in status_field.options.split('\n') if s.strip()]
            else:
                valid_statuses = ["Open", "Closed"]
            
            frappe.logger().info(f"Valid statuses from DocType: {valid_statuses}")
            
            if status not in valid_statuses:
                return {"success": False, "message": f"Invalid status. Must be one of {', '.join(valid_statuses)}"}
                
        except Exception as e:
            frappe.logger().error(f"Error getting status options: {str(e)}")
            if status not in ["Open", "Closed"]:
                return {"success": False, "message": "Invalid status"}

        # Step 4: Process salary ranges
        frappe.logger().info("Step 4: Processing salary ranges")
        lower_range_final = None
        upper_range_final = None
        
        lower_range_val = data.get("lower_range")
        upper_range_val = data.get("upper_range")
        
        frappe.logger().info(f"Lower range: {lower_range_val}, Upper range: {upper_range_val}")

        if lower_range_val and upper_range_val:
            try:
                lower = float(lower_range_val)
                upper = float(upper_range_val)
                
                if lower <= 0 or upper <= 0:
                    return {"success": False, "message": "Salary ranges must be positive numbers"}
                if lower >= upper:
                    return {"success": False, "message": "Minimum salary must be less than maximum salary"}
                
                lower_range_final = lower
                upper_range_final = upper
                frappe.logger().info(f"Salary range processed: {lower_range_final} - {upper_range_final}")
            except (ValueError, TypeError) as e:
                frappe.logger().error(f"Salary conversion error: {str(e)}")
                return {"success": False, "message": "Salary ranges must be valid numbers"}

        # Step 5: Convert boolean values
        frappe.logger().info("Step 5: Converting boolean values")
        publish_salary = 1 if str(data.get("publish_salary_range")).lower() in ["true", "1"] else 0
        publish_website = 1 if str(data.get("publish_on_website")).lower() in ["true", "1"] else 0
        
        # Step 6: Parse dates
        frappe.logger().info("Step 6: Parsing dates")
        posted_on = data.get("posted_on") or datetime.now(timezone.utc).strftime("%Y-%m-%d")
        closes_on = data.get("closes_on") if data.get("closes_on") else None
        frappe.logger().info(f"Posted on: {posted_on}, Closes on: {closes_on}")
        
        # Step 7: Get optional fields
        frappe.logger().info("Step 7: Getting optional fields")
        location = data.get("location", "").strip() or None
        employment_type = data.get("employment_type", "").strip() or None
        department = data.get("department", "").strip() or None
        
        # Step 8: Create document dict
        frappe.logger().info("Step 8: Creating document dictionary")
        doc_dict = {
            "doctype": "Job Opening",
            "job_title": data.get("job_title"),
            "designation": data.get("designation"),
            "description": data.get("description", ""),
            "currency": data.get("currency", "INR"),
            "lower_range": lower_range_final,
            "upper_range": upper_range_final,
            "publish_salary_range": publish_salary,
            "company": data.get("company"),
            "employment_type": employment_type,
            "department": department,
            "location": location,
            "publish_on_website": publish_website,
            "posted_on": posted_on,
            "closes_on": closes_on,
            "status": status,
            "salary_per": data.get("salary_per", "Month")
        }
        
        frappe.logger().info(f"Document dict created: {json.dumps(doc_dict, indent=2, default=str)}")
        
        # Step 9: Create Job Opening document
        frappe.logger().info("Step 9: Creating frappe document")
        job_doc = frappe.get_doc(doc_dict)
        
        # Step 10: Insert document
        frappe.logger().info("Step 10: Inserting document")
        job_doc.insert(ignore_permissions=False, ignore_links=True)  # CHANGED: ignore_permissions=True se False kiya, taaki Frappe ka internal permission engine bhi check kare (double-safety)
        
        # Step 11: Commit
        frappe.logger().info("Step 11: Committing to database")
        frappe.db.commit()
        
        frappe.logger().info(f"=== SUCCESS: Job Opening {job_doc.name} created ===")
        
        return {
            "success": True,
            "message": f"Job Opening {job_doc.name} created successfully",
            "data": {
                "name": job_doc.name,
                "job_title": job_doc.job_title
            }
        }
        
    except Exception as e:
        frappe.logger().error(f"=== ERROR OCCURRED ===")
        frappe.logger().error(f"Error type: {type(e).__name__}")
        frappe.logger().error(f"Error message: {str(e)}")
        
        error_trace = frappe.get_traceback()
        frappe.logger().error(f"Full traceback: {error_trace}")
        
        frappe.db.rollback()
        frappe.log_error(title="Job Opening Creation Error", message=error_trace)
        
        return {
            "success": False,
            "message": f"Failed to create job opening: {str(e)}"
        }
        

@frappe.whitelist()
def delete_job_opening(name):
    try:
        if not frappe.db.exists("Job Opening", name):
            return {"success": False, "message": "Job Opening not found"}

        # NEW: Permission check — dynamic Role Permissions Manager settings ke hisaab se
        if not frappe.has_permission("Job Opening", ptype="delete", doc=name):
            frappe.logger().error(f"Permission denied for user {frappe.session.user} to delete Job Opening {name}")
            return {"success": False, "message": "You do not have permission to delete this Job Opening"}

        # ─────────────────────────────────────────
        # STEP 1: Find correct Interview link field
        # ─────────────────────────────────────────
        try:
            interview_meta = frappe.get_meta("Interview")
            interview_link_fields = [
                f.fieldname for f in interview_meta.fields
                if f.fieldtype == "Link" and f.options == "Job Opening"
            ]
            frappe.logger().info(f"Interview link fields to Job Opening: {interview_link_fields}")
        except Exception as e:
            frappe.logger().error(f"Error getting Interview meta: {str(e)}")
            interview_link_fields = []

        # STEP 2: Check for linked Interviews using correct field
        linked_interviews = []
        for field in interview_link_fields:
            results = frappe.get_all(
                "Interview",
                filters={field: name},
                pluck="name"
            )
            linked_interviews.extend(results)

        linked_interviews = list(set(linked_interviews))

        if linked_interviews:
            return {
                "success": False,
                "message": f"Cannot delete. This Job Opening is linked with {len(linked_interviews)} Interview(s). Please delete them first."
            }

        # ─────────────────────────────────────────
        # STEP 3: Check for linked Job Applicants
        # ─────────────────────────────────────────
        try:
            applicant_meta = frappe.get_meta("Job Applicant")
            applicant_link_fields = [
                f.fieldname for f in applicant_meta.fields
                if f.fieldtype == "Link" and f.options == "Job Opening"
            ]
            frappe.logger().info(f"Job Applicant link fields to Job Opening: {applicant_link_fields}")
        except Exception as e:
            frappe.logger().error(f"Error getting Job Applicant meta: {str(e)}")
            applicant_link_fields = []

        linked_applicants = []
        for field in applicant_link_fields:
            results = frappe.get_all(
                "Job Applicant",
                filters={field: name},
                pluck="name"
            )
            linked_applicants.extend(results)

        linked_applicants = list(set(linked_applicants))

        if linked_applicants:
            return {
                "success": False,
                "message": f"Cannot delete. This Job Opening is linked with {len(linked_applicants)} Job Applicant(s). Please delete them first."
            }

        # ─────────────────────────────────────────
        # STEP 4: No links — safe to delete
        # ─────────────────────────────────────────
        frappe.delete_doc("Job Opening", name, ignore_permissions=False, force=True)  # CHANGED: ignore_permissions=True se False kiya, taaki Frappe ka internal permission engine bhi check kare (double-safety)
        frappe.db.commit()

        return {"success": True, "message": f"{name} deleted successfully"}

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(title="Delete Job Opening Error", message=frappe.get_traceback())
        return {"success": False, "message": str(e)}     


@frappe.whitelist(allow_guest=True)
def get_applicant_counts():
    try:
        counts = {}
        
        applicants = frappe.get_all(
            "Job Applicant",
            fields=["name", "job_title"],
            limit_page_length=0
        )
        
        for applicant in applicants:
            jo = applicant.get("job_title")
            if jo and str(jo).strip():
                counts[jo] = counts.get(jo, 0) + 1
                
        return {"success": True, "data": counts}
        
    except Exception as e:
        frappe.log_error(str(e), "get_applicant_counts")
        return {"success": False, "data": {}, "error": str(e)}


# ── NEW: Update publish_on_website via direct DB write ────────────────────────
@frappe.whitelist()
def update_publish_on_website(name, publish_on_website):
    """
    Directly update publish_on_website on a Job Opening.
    Uses db.set_value + explicit commit to guarantee persistence.
    publish_on_website: "1" or "0" (comes as string from POST body)
    """
    try:
        if not frappe.db.exists("Job Opening", name):
            return {"success": False, "message": "Job Opening not found"}

        # Convert to int explicitly — Frappe Check field stores 0 or 1
        val = 1 if str(publish_on_website).strip() in ("1", "true", "True") else 0

        # db.set_value bypasses the form layer and writes directly to the DB
        # The actual DB column name is "publish" (not "publish_on_website")
        frappe.db.set_value(
            "Job Opening",
            name,
            "publish",
            val,
            update_modified=True   # touch `modified` so caches invalidate
        )
        frappe.db.commit()

        # Read back to confirm what was actually saved
        saved = frappe.db.get_value("Job Opening", name, "publish")
        frappe.logger().info(
            f"update_publish_on_website: {name} -> requested={val}, saved={saved}"
        )

        return {
            "success": True,
            "publish_on_website": int(saved),
            "message": f"publish_on_website updated to {saved}"
        }

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(title="Update Publish On Website Error", message=frappe.get_traceback())
        return {"success": False, "message": str(e)}
# ─────────────────────────────────────────────────────────────────────────────


# ═════════════════════════════════════════════════════════════════════════════
# NEW: SHARE JOB OPENING (Frappe "Share" dialog jaisa feature)
# Frappe ke built-in DocShare + frappe.share module use hota hai, isliye
# Desk ke Share dialog aur humari UI dono ek hi data dekhte hain.
# ═════════════════════════════════════════════════════════════════════════════
SHARE_DOCTYPE = "Job Opening"


def _to_flag(value):
    """'1' / 'true' / 1 / True  ->  1, baaki sab -> 0"""
    return 1 if str(value).strip().lower() in ("1", "true") else 0


# def _can_share(name):
#     """
#     Jis user ko Job Opening par 'share' permission hai wahi share kar sakta hai
#     (role se ya kisi ke share karne par mili permission se — Frappe Desk jaisa).
#     """
#     return frappe.has_permission(SHARE_DOCTYPE, ptype="share", doc=name)
def _can_share(name):
    """
    1. Administrator                         -> haan
    2. Recipient (kisi ne share kiya hai)    -> sirf tab jab DocShare mein share = 1
    3. Baaki (owner / koi bhi jo read kar sake) -> haan
    """
    if frappe.session.user == "Administrator":
        return True

    if _is_share_recipient(name):
        # Role mein Share ho tab bhi ignore: sirf DocShare ka share flag chalega
        return bool(frappe.db.get_value(
            "DocShare",
            {"share_doctype": SHARE_DOCTYPE, "share_name": name,
             "user": frappe.session.user, "everyone": 0},
            "share",
        ))

    return bool(frappe.has_permission(SHARE_DOCTYPE, ptype="read", doc=name))


def _is_share_recipient(name):
    """
    True agar current user ko ye Job Opening kisi ne SHARE ki hai (uske naam ki DocShare row hai).
    False agar opening user ne khud banayi hai / use share nahi hui.
    """
    return bool(
        frappe.db.exists(
            "DocShare",
            {
                "share_doctype": SHARE_DOCTYPE,
                "share_name": name,
                "user": frappe.session.user,
                "everyone": 0,
            },
        )
    )


# def _share_access(name):
#     """
#     can_share      -> Share permission hai? Nahi hai to button disabled.
#     can_view_list  -> "Currently shared with" dikhegi (jise share permission hai usse hamesha).
#     only_mine      -> True agar user ko ye opening kisi ne share ki hai: tab list mein SIRF wahi
#                       users aate hain jinko usne khud share kiya hai. False (owner/sharer) ko
#                       poori list dikhti hai.
#     """
#     can_share = bool(_can_share(name))
#     only_mine = can_share and _is_share_recipient(name)
#     return {"can_share": can_share, "can_view_list": can_share, "only_mine": bool(only_mine)}

def _share_access(name):
    is_recipient = _is_share_recipient(name)
    can_share = bool(_can_share(name))
    return {
        "can_share": can_share,
        "can_view_list": can_share,       # Share permission hai to list dikhegi
        "only_mine": can_share and is_recipient,   # recipient ko sirf apne diye hue
    }



def _remove_share(name, user):
    """
    Ek user ka share hata deta hai (DocShare row delete).
    Frappe Desk mein bhi saari permissions uncheck karne par yehi hota hai.

    frappe.share.remove() / delete_doc() DocShare doctype par delete permission maangte
    hain jo normal users ke role ko nahi hoti ("No permission for DocShare" error).
    Isliye seedha DB se delete karte hain. Security: _can_share() check
    set_doc_share() mein pehle hi ho chuka hota hai.
    """
    frappe.db.delete(
        "DocShare",
        {"share_doctype": SHARE_DOCTYPE, "share_name": name, "user": user, "everyone": 0},
    )
    # Shared user ki permission cache saaf karo, warna usse opening purani permission se dikhti rahegi
    frappe.clear_cache(user=user)
    frappe.clear_document_cache(SHARE_DOCTYPE, name)


def _get_doc_shares(name, shared_by=None):
    """
    Is Job Opening ke user-wise shares (Everyone wali row chhodkar).
    shared_by diya ho to sirf wahi shares jo us user ne banaye (DocShare ka owner = jisne share kiya).
    """
    filters = {"share_doctype": SHARE_DOCTYPE, "share_name": name, "everyone": 0}
    if shared_by:
        filters["owner"] = shared_by

    shares = frappe.get_all(
        "DocShare",
        filters=filters,
        fields=["user", "read", "write", "share", "submit"],
        order_by="creation asc",
        limit_page_length=0,
    )

    emails = [s.user for s in shares if s.user]
    full_names = {}
    if emails:
        for u in frappe.get_all(
            "User",
            filters={"name": ["in", emails]},
            fields=["name", "full_name"],
            limit_page_length=0,
        ):
            full_names[u.name] = u.full_name

    return [
        {
            "user": s.user,
            "full_name": full_names.get(s.user) or s.user,
            "read": int(s.read or 0),
            "write": int(s.write or 0),
            "share": int(s.share or 0),
            "submit": int(s.submit or 0),
        }
        for s in shares
    ]


# def _visible_shares(name):
#     """
#     Current user ko jo shares dikhane hain:
#     - Jise opening share hui hai -> sirf wo jo usne khud share kiye
#     - Baaki (owner / sharer)     -> sabhi
#     """
#     if _is_share_recipient(name):
#         return _get_doc_shares(name, shared_by=frappe.session.user)
#     return _get_doc_shares(name)
def _visible_shares(name):
    if _is_share_recipient(name):
        # B ko sirf wahi dikhein jo B ne khud share kiye
        return _get_doc_shares(name, shared_by=frappe.session.user)
    # A / owner ko poori list
    return _get_doc_shares(name)


@frappe.whitelist()
def get_share_users():
    """Share dialog ke dropdown ke liye User doctype se enabled users ki list."""
    try:
        users = frappe.get_all(
            "User",
            filters={
                "enabled": 1,
                "user_type": "System User",   # website/portal users nahi chahiye to rakho, warna hata do
                "name": ["not in", ["Administrator", "Guest"]],
            },
            fields=["name", "full_name"],
            order_by="full_name asc",
            limit_page_length=0,
        )
        return {
            "success": True,
            "data": [{"name": u.name, "full_name": u.full_name or u.name} for u in users],
        }
    except Exception as e:
        frappe.log_error(title="Get Share Users Error", message=frappe.get_traceback())
        return {"success": False, "data": [], "message": str(e)}


@frappe.whitelist()
def get_share_access(name):
    """
    Current user ke liye: Share button chalega ya disabled hoga (can_share),
    aur "Currently shared with" list dikhegi ya nahi (can_view_list).
    """
    try:
        if not frappe.db.exists(SHARE_DOCTYPE, name):
            return {"success": False, "can_share": False, "can_view_list": False, "message": "Job Opening not found"}

        return {"success": True, **_share_access(name)}

    except Exception as e:
        frappe.log_error(title="Get Share Access Error", message=frappe.get_traceback())
        return {"success": False, "can_share": False, "can_view_list": False, "message": str(e)}


@frappe.whitelist()
def get_doc_shares(name):
    """Ye Job Opening abhi kin users ke saath share hai (permissions ke saath)."""
    try:
        if not frappe.db.exists(SHARE_DOCTYPE, name):
            return {"success": False, "data": [], "message": "Job Opening not found"}

        if not frappe.has_permission(SHARE_DOCTYPE, ptype="read", doc=name):
            return {"success": False, "data": [], "message": "You do not have permission to view this Job Opening"}

        # Share permission nahi hai to list nahi; hai to _visible_shares ke hisaab se
        access = _share_access(name)
        if not access["can_view_list"]:
            return {"success": True, "data": [], **access}

        return {"success": True, "data": _visible_shares(name), **access}

    except Exception as e:
        frappe.log_error(title="Get Doc Shares Error", message=frappe.get_traceback())
        return {"success": False, "data": [], "message": str(e)}


@frappe.whitelist()
def set_doc_share(name, user, read=0, write=0, share=0, submit=0):
    """
    Ek user ke liye share add/update karta hai.
    - Pehle se share hai  -> permissions update
    - Naya user          -> add
    - Saari permissions 0 -> share remove (Frappe Desk jaisa)
    Response mein updated shares list wapas aati hai (jitni current user ko dikhani hai).
    """
    try:
        if not frappe.db.exists(SHARE_DOCTYPE, name):
            return {"success": False, "message": "Job Opening not found"}

        if not _can_share(name):
            return {"success": False, "message": "You do not have permission to share this Job Opening"}

        # Jise opening share hui hai wo sirf apne diye hue shares ko badal sakta hai
        is_recipient = _is_share_recipient(name)

        if not frappe.db.exists("User", {"name": user, "enabled": 1}):
            return {"success": False, "message": "Selected user not found or disabled"}

        # Agar ye user pehle se kisi AUR ne share kiya hua hai to recipient use chhu nahi sakta
        # (warna wo doosron ki permission badal/hata sakta tha). Apne diye hue share badal sakta hai.
        if is_recipient:
            existing_owner = frappe.db.get_value(
                "DocShare",
                {"share_doctype": SHARE_DOCTYPE, "share_name": name, "user": user, "everyone": 0},
                "owner",
            )
            if existing_owner and existing_owner != frappe.session.user:
                return {"success": False, "message": "This user already has access to this Job Opening"}

        read, write, share = _to_flag(read), _to_flag(write), _to_flag(share)
        submit = 0  # Job Opening submittable nahi hai, isliye hamesha 0

        # Frappe UI jaisa rule: write ya share dena hai to read bhi chahiye
        if write or share:
            read = 1

        if not (read or write or share):
            # Saari permissions hata di -> user ka share hat jaata hai (Frappe jaisa)
            _remove_share(name, user)
        else:
            frappe.share.add(
                SHARE_DOCTYPE,
                name,
                user,
                read=read,
                write=write,
                share=share,
                notify=0,
                # Role mein Share tick na ho tab bhi share ho sake (humara _can_share() check upar ho chuka hai)
                flags={"ignore_share_permission": True},
            )

        frappe.db.commit()
        return {"success": True, "data": _visible_shares(name)}

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(title="Set Doc Share Error", message=frappe.get_traceback())
        return {"success": False, "message": str(e)}


# ═════════════════════════════════════════════════════════════════════════════


# ─────────────────────────────────────────────────────────────
# Get current logged-in user's roles
# ─────────────────────────────────────────────────────────────
@frappe.whitelist()
def get_current_user_roles():
    try:
        user = frappe.session.user

        # All roles returned by Frappe
        roles = frappe.get_roles(user)

        # Direct roles actually assigned to the User
        assigned_roles = frappe.get_all(
            "Has Role",
            filters={
                "parent": user,
                "parenttype": "User",
            },
            pluck="role"
        )

        site_hr_roles = [
            "Site HR User",
            "Site HR Manager",
        ]

        # Site HR is determined from actual User role assignment,
        # not from frappe.get_roles(), because Administrator
        # automatically receives all roles.
        is_site_hr_role = any(
            role in assigned_roles
            for role in site_hr_roles
        )

        return {
            "success": True,
            "user": user,
            "roles": roles,
            "assigned_roles": assigned_roles,
            "is_site_hr_role": is_site_hr_role,
        }

    except Exception as e:
        frappe.log_error(
            title="Get Current User Roles Error",
            message=frappe.get_traceback()
        )

        return {
            "success": False,
            "roles": [],
            "assigned_roles": [],
            "is_site_hr_role": False,
            "message": str(e),
        }

    