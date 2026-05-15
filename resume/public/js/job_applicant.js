frappe.ui.form.on("Job Applicant", {
    refresh(frm) {

        if (!frm.is_new()) {

            frm.add_custom_button(
                "Send Document Link",

                function () {

                    frappe.call({
                        method:
                        "resume.api.api.generate_document_link",

                        args: {
                            applicant_name: frm.doc.name
                        },

                        callback: function(r) {

                            if (r.message.success) {
                                frappe.msgprint(
                                  "Email sent successfully"
                                );
                            }
                        }
                    });

                }
            );

        }

    }
});
