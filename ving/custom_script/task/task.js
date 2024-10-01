frappe.ui.form.on('Task', {
	refresh: function (frm) {
		if (cur_frm.doc.parent_task) {
			frappe.call({
				method: "get_assigment_status",
				doc: cur_frm.doc,
				callback: function (r) {
					if (r) {
						console.log(r.message)
						if (r.message) {
							$(".add-assignment-btn").css("display", "none");
						}
					}
				}
			});
		}
	}

})
