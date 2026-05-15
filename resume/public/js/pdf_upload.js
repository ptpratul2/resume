// frappe.ui.form.on('PDF Upload', {
//     refresh(frm) {
//         frm.add_custom_button('Bulk Upload Resumes', () => {
//             console.log("Upload button clicked");

//             new frappe.ui.FileUploader({
//                 allow_multiple: true,
//                 on_success(file_list) {
//                     console.log("Files uploaded:", file_list);

//                     const files = Array.isArray(file_list) ? file_list : [file_list];

//                     files.forEach(file => {
//                         let row = frm.add_child("files");
//                         console.log("Adding row with:", file.file_url);
//                         row.file_upload = file.file_url;
//                     });

//                     frm.refresh_field("files");
//                 }
//             });
//         });
//     }
// });





// frappe.ui.form.on('PDF Upload', {
//     refresh(frm) {
//         frm.add_custom_button('Upload & Process Resumes', () => {
//             new frappe.ui.FileUploader({
//                 allow_multiple: true,
//                 restrictions: {
//                     allowed_file_types: ['.pdf']
//                 },
//                 on_success(file_list) {
//                     const files = Array.isArray(file_list) ? file_list : [file_list];
//                     const existingUrls = frm.doc.files.map(f => f.file_upload);

//                     files.forEach(file => {
//                         if (!existingUrls.includes(file.file_url)) {
//                             let row = frm.add_child("files");
//                             row.file_upload = file.file_url;
//                         }
//                     });

//                     frm.refresh_field("files");

//                     // Save and process
//                     frm.save().then(() => {
//                         frappe.call({
//                             method: "resume.resume.doctype.pdf_upload.pdf_upload.process_pdfs",
//                             args: {
//                                 docname: frm.doc.name
//                             },
//                             freeze: true,
//                             freeze_message: "Processing resumes...",
//                             callback: (r) => {
//                                 if (!r.exc) {
//                                     frappe.msgprint("PDFs uploaded and Job Applicants created.");
//                                     frm.reload_doc();
//                                 }
//                             }
//                         });
//                     });
//                 }
//             });
//         });
//     }
// });





function resume_pdf_upload_xhr_error_message(xhr) {
	let msg = __(
		'Request failed. Check Error Log and confirm a background worker is running (e.g. bench worker).'
	);
	try {
		const j = xhr.responseJSON || JSON.parse(xhr.responseText || '{}');
		if (j._server_messages) {
			const arr = JSON.parse(j._server_messages);
			const parts = arr.map((s) => {
				try {
					return JSON.parse(s).message;
				} catch (e) {
					return s;
				}
			});
			msg = parts.filter(Boolean).join('\n') || msg;
		} else if (j.message) {
			msg = j.message;
		}
	} catch (e) {
		/* keep default */
	}
	return msg;
}

frappe.ui.form.on('PDF Upload', {
    refresh(frm) {
        frm.add_custom_button(__('Process uploaded files'), () => {
            if (!frm.doc.job_title) {
                frappe.msgprint(__('Please select a Job Title first.'));
                return;
            }
            frappe.call({
                method: 'resume.resume.doctype.pdf_upload.pdf_upload.process_pdfs',
                args: { docname: frm.doc.name },
                freeze: true,
                freeze_message: __('Queueing resume processing...'),
                callback(r) {
                    if (!r.exc) {
                        frm.reload_doc();
                    }
                },
                error(xhr) {
                    frappe.msgprint({
                        title: __('Could not queue processing'),
                        indicator: 'red',
                        message: resume_pdf_upload_xhr_error_message(xhr),
                    });
                },
            });
        });

        frm.add_custom_button('Upload Resumes', () => {
            // Check karein ki mandatory fields bhari hain ya nahi
            if (!frm.doc.job_title) {
                frappe.msgprint(__("Please select a Job Title first."));
                return;
            }

            new frappe.ui.FileUploader({
                allow_multiple: true,
                restrictions: {
                    allowed_file_types: ['.pdf', '.doc', '.docx', '.txt', '.jpg', '.jpeg', '.png']
                },
                on_success(file) {
                    // Child table mein file add karein
                    let row = frm.add_child("files");
                    row.file_upload = file.file_url;
                    frm.refresh_field("files");
                },
                on_complete() {
                    frappe.show_alert({message: __("All files uploaded. Saving..."), indicator: 'blue'});
                    
                    // Forcefully form ko dirty mark karein taki save trigger ho
                    frm.dirty(); 

                    frm.save().then(() => {
                        // Agar save successful hua, tabhi Python call karein
                        frappe.call({
                            method: "resume.resume.doctype.pdf_upload.pdf_upload.process_pdfs",
                            args: {
                                docname: frm.doc.name
                            },
                            freeze: true,
                            freeze_message: __("AI is analyzing resumes..."),
                            callback: (r) => {
                                if (!r.exc) {
                                    frappe.msgprint({
                                        title: __('Success'),
                                        indicator: 'green',
                                        message: __('Resumes are being processed. Check Job Applicants after 1-2 minutes.')
                                    });
                                    frm.reload_doc();
                                }
                            },
                            error(xhr) {
                                frappe.msgprint({
                                    title: __('Processing error'),
                                    indicator: 'red',
                                    message: resume_pdf_upload_xhr_error_message(xhr),
                                });
                            }
                        });
                    }).catch((e) => {
                        frappe.msgprint(__("Save failed. Please check if all mandatory fields are filled."));
                        console.error("Save Error: ", e);
                    });
                }
            });
        });
    }
});
