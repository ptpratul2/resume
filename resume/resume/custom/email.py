# # =========================================
# # Interview Consolidated Email (Interviewer)
# # =========================================

# import frappe
# from frappe.utils import formatdate, now_datetime, add_days, validate_email_address
# from frappe import _


# def interview_daily_summary():
#     """
#     - Collect Interviews (First Round)
#     - Group by interviewer email
#     - Send ONE email per interviewer
#     - Attach candidate resume(s)
#     """

#     frappe.logger().info("Starting Interview Daily Summary")

#     # -------------------------------------
#     # Last 24 hours (adjust if needed)
#     # -------------------------------------
#     from_date = add_days(now_datetime(), -1)

#     # -------------------------------------
#     # Fetch Interviews
#     # -------------------------------------
#     interviews = frappe.get_all(
#         "Interview",
#         filters={
#             "scheduled_on": [">=", from_date],
#             "interview_round": "First Round"
#         },
#         fields=[
#             "name",
#             "job_applicant",
#             "designation",
#             "scheduled_on",
#             "from_time",
#             "custom_meeting_link",
#             "custom_location",
#             "interview_round"
#         ]
#     )

#     if not interviews:
#         frappe.logger().info("No interviews found")
#         return 0

#     # -------------------------------------
#     # Group interviews by interviewer
#     # -------------------------------------
#     interviews_by_interviewer = {}

#     for interview in interviews:

#         interviewers = frappe.get_all(
#             "Interview Detail",
#             filters={"parent": interview.name},
#             fields=["interviewer"]
#         )

#         for row in interviewers:
#             email = row.interviewer

#             if not email:
#                 continue

#             email = email.strip().lower()

#             if not validate_email_address(email):
#                 continue

#             interviews_by_interviewer.setdefault(email, []).append(interview)

#     if not interviews_by_interviewer:
#         frappe.logger().info("No valid interviewer emails found")
#         return len(interviews)

#     # -------------------------------------
#     # Send ONE email per interviewer
#     # -------------------------------------
#     sent_count = 0

#     for interviewer_email, interviewer_interviews in interviews_by_interviewer.items():

#         try:
#             rows = []
#             attachments = []

#             for interview in interviewer_interviews:

#                 # ---------------------------------
#                 # Fetch Job Applicant details
#                 # ---------------------------------
#                 applicant = frappe.db.get_value(
#                     "Job Applicant",
#                     interview.job_applicant,
#                     ["applicant_name", "email_id"],
#                     as_dict=True
#                 )

#                 candidate_name = applicant.applicant_name if applicant else "Candidate"

#                 # ---------------------------------
#                 # Attach Resume (same as First Round)
#                 # ---------------------------------
#                 resume_file = frappe.db.get_value(
#                     "File",
#                     {
#                         "attached_to_doctype": "Job Applicant",
#                         "attached_to_name": interview.job_applicant
#                     },
#                     ["file_name", "file_url"],
#                     order_by="creation desc",
#                     as_dict=True
#                 )

#                 if resume_file:
#                     attachments.append({
#                         "fname": resume_file.file_name,
#                         "file_url": resume_file.file_url
#                     })

#                 # ---------------------------------
#                 # Table Row
#                 # ---------------------------------
#                 rows.append(f"""
#                 <tr>
#                     <td style="border:1px solid #ddd;padding:6px;">
#                         {candidate_name}
#                     </td>
#                     <td style="border:1px solid #ddd;padding:6px;">
#                         {interview.designation or "-"}
#                     </td>
#                     <td style="border:1px solid #ddd;padding:6px;">
#                         {interview.interview_round}
#                     </td>
#                     <td style="border:1px solid #ddd;padding:6px;">
#                         {formatdate(interview.scheduled_on)}
#                     </td>
#                     <td style="border:1px solid #ddd;padding:6px;">
#                         {interview.from_time}
#                     </td>
#                     <td style="border:1px solid #ddd;padding:6px;">
#                         {interview.custom_location or "-"}
#                     </td>
#                     <td style="border:1px solid #ddd;padding:6px;">
#                         <a href="{interview.custom_meeting_link}">
#                             {interview.custom_meeting_link}
#                         </a>
#                     </td>
#                 </tr>
#                 """)

#             # ---------------------------------
#             # Email Content
#             # ---------------------------------
#             subject = _("Interview Schedule Summary ({0} Candidates)").format(
#                 len(interviewer_interviews)
#             )

#             message = f"""
# <div style="font-family:Arial,sans-serif;font-size:12px;">

# <p>Dear Sir,</p>

# <p>Please find below the interview schedule:</p>

# <table style="border-collapse:collapse;width:100%;">
#     <thead>
#         <tr style="background:#f2f2f2;">
#             <th style="border:1px solid #ddd;padding:6px;">Candidate</th>
#             <th style="border:1px solid #ddd;padding:6px;">Designation</th>
#             <th style="border:1px solid #ddd;padding:6px;">Round</th>
#             <th style="border:1px solid #ddd;padding:6px;">Date</th>
#             <th style="border:1px solid #ddd;padding:6px;">Time</th>
#             <th style="border:1px solid #ddd;padding:6px;">Location</th>
#             <th style="border:1px solid #ddd;padding:6px;">Meeting Link</th>
#         </tr>
#     </thead>
#     <tbody>
#         {''.join(rows)}
#     </tbody>
# </table>

# <br>

# <p>
# <b>Candidate Feedback Link:</b><br>
# <a href="https://ats.octavision.in/candidate-feedback" target="_blank">
# https://ats.octavision.in/candidate-feedback
# </a>
# </p>

# <br>

# <p>Regards,<br>
# HR Team</p>

# </div>
# """

#             frappe.sendmail(
#                 recipients=[interviewer_email],
#                 subject=subject,
#                 message=message,
#                 attachments=attachments,
#                 delayed=False
#             )

#             sent_count += 1
#             frappe.logger().info(f"Interview summary sent to {interviewer_email}")

#         except Exception:
#             frappe.logger().error(
#                 frappe.get_traceback(),
#                 f"Interview summary failed for {interviewer_email}"
#             )

#     frappe.db.commit()
#     return sent_count
