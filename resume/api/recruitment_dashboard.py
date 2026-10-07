import frappe
from frappe.utils import add_days, add_months, flt, get_first_day, getdate, nowdate
from resume.api.permissions import is_site_hr_user

RANGE_MONTHS = {"Last Month": 1, "Last 3 Months": 3, "Last 6 Months": 6, "Last Year": 12}

def _block_site_hr():
    """Site HR User / Site HR Manager ko dashboard data nahi milega."""
    if is_site_hr_user():
        frappe.throw(
            "You do not have permission to view the Recruitment Dashboard",
            frappe.PermissionError,
        )

def _source_field():
    # Jo field exist karti hai wahi use hogi
    meta = frappe.get_meta("Job Applicant")
    return "source_of_job_posting" if meta.has_field("source_of_job_posting") else "source"


def _group(doctype, field):
    """Field ke hisaab se count. Blank values skip hoti hain."""
    rows = frappe.db.sql(
        f"""select `{field}` as label, count(*) as total
            from `tab{doctype}`
            where ifnull(`{field}`, '') != ''
            group by `{field}`""",
        as_dict=True,
    )
    data = [{"label": r.label, "value": r.total} for r in rows]
    return sorted(data, key=lambda x: x["value"], reverse=True)


def _count_between(doctype, date_field, start, end, extra=None):
    filters = [[date_field, ">=", start], [date_field, "<", end]] + (extra or [])
    return frappe.db.count(doctype, filters)


def _pct_change(current, previous):
    if not previous:
        return 100 if current else 0
    return round((current - previous) / previous * 100, 1)


def _periods(start, end, interval):
    out, d = [], start
    while d <= end:
        if interval == "Monthly":
            out.append((d.strftime("%Y-%m"), d.strftime("%b %Y")))
            d = add_months(d, 1)
        elif interval == "Weekly":
            out.append((d.strftime("%G-W%V"), d.strftime("%d %b %Y")))
            d = add_days(d, 7)
        else:
            out.append((d.strftime("%Y-%m-%d"), d.strftime("%d %b")))
            d = add_days(d, 1)
    return out


def _frequency(doctype, date_range="Last Year", interval="Monthly"):
    months = RANGE_MONTHS.get(date_range, 12)
    interval = interval if interval in ("Daily", "Weekly", "Monthly") else "Monthly"
    today = getdate(nowdate())

    if interval == "Monthly":
        start = get_first_day(add_months(today, -months))
        fmt = "%%Y-%%m"
    elif interval == "Weekly":
        s = add_months(today, -months)
        start = add_days(s, -s.weekday())  # Monday se start
        fmt = "%%x-W%%v"
    else:
        start = add_months(today, -months)
        fmt = "%%Y-%%m-%%d"

    rows = frappe.db.sql(
        f"""select date_format(creation, '{fmt}') as period, count(name) as total
            from `tab{doctype}` where creation >= %s group by period""",
        (start,),
        as_dict=True,
    )
    counts = {r.period: r.total for r in rows}
    return [{"label": label, "value": counts.get(key, 0)} for key, label in _periods(start, today, interval)]


def _time_to_fill():
    # HRMS standard: Job Requisition ka average time_to_fill
    try:
        row = frappe.db.sql("select avg(time_to_fill) from `tabJob Requisition` where time_to_fill > 0")
        return round(flt(row[0][0]), 1)
    except Exception:
        return 0


@frappe.whitelist()
def get_dashboard_data():
    _block_site_hr()
    today = getdate(nowdate())
    this_start = get_first_day(today)
    next_start = add_months(this_start, 1)
    last_start = add_months(this_start, -1)

    # Job Openings
    openings_total = frappe.db.count("Job Opening")
    openings_open = frappe.db.count("Job Opening", {"status": "Open"})
    openings_closed = frappe.db.count("Job Opening", {"status": "Closed"})
    openings_this = _count_between("Job Opening", "creation", this_start, next_start)
    openings_last = _count_between("Job Opening", "creation", last_start, this_start)

    # Job Applicants
    applicants_total = frappe.db.count("Job Applicant")
    applicants_this = _count_between("Job Applicant", "creation", this_start, next_start)
    applicants_last = _count_between("Job Applicant", "creation", last_start, this_start)
    accepted = frappe.db.count("Job Applicant", {"status": "Accepted"})
    rejected = frappe.db.count("Job Applicant", {"status": "Rejected"})

    # Interviews
    interviews_total = frappe.db.count("Interview")
    interviews_this = _count_between("Interview", "creation", this_start, next_start)
    interviews_last = _count_between("Interview", "creation", last_start, this_start)

    # Job Offers
    offers_total = frappe.db.count("Job Offer")
    offers_accepted = frappe.db.count("Job Offer", {"status": "Accepted"})
    offers_this = _count_between("Job Offer", "offer_date", this_start, next_start)

    return {
        "success": True,
        "data": {
            "kpis": {
                "openings_total": openings_total,
                "openings_open": openings_open,
                "openings_closed": openings_closed,
                "openings_this_month": openings_this,
                "openings_change": _pct_change(openings_this, openings_last),
                "applicants_total": applicants_total,
                "applicants_this_month": applicants_this,
                "applicants_change": _pct_change(applicants_this, applicants_last),
                "interviews_total": interviews_total,
                "interviews_this_month": interviews_this,
                "interviews_change": _pct_change(interviews_this, interviews_last),
                "accepted": accepted,
                "rejected": rejected,
                "offers_this_month": offers_this,
                "applicant_to_hire": round(accepted / applicants_total * 100, 2) if applicants_total else 0,
                "offer_acceptance_rate": round(offers_accepted / offers_total * 100, 2) if offers_total else 0,
                "time_to_fill": _time_to_fill(),
            },
            "pipeline": _group("Job Applicant", "designation"),
            "source": _group("Job Applicant", _source_field()),
            "country": _group("Job Applicant", "country"),
            "application_status": _group("Job Applicant", "status"),
            "offer_status": _group("Job Offer", "status"),
            "interview_status": _group("Interview", "status"),
            "department": _group("Job Opening", "department"),
            "designation": _group("Job Opening", "designation"),
            "openings_monthly": _frequency("Job Opening", "Last Year", "Monthly"),
            "interviews_monthly": _frequency("Interview", "Last Year", "Monthly"),
            "applicants_monthly": _frequency("Job Applicant", "Last Year", "Monthly"),
            "frequency": _frequency("Job Applicant", "Last Year", "Monthly"),
        },
    }


@frappe.whitelist()
def get_application_frequency(date_range="Last Year", interval="Monthly"):
    _block_site_hr()
    """Sirf line chart ke filter (Last Year / Monthly) ke liye"""
    return {"success": True, "data": _frequency("Job Applicant", date_range, interval)}
