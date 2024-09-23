frappe.ui.form.on('Task', {
	refresh: function (frm) {
		frappe.call({
			method: "get_assigment_status",
			doc: cur_frm.doc,
			callback: function (r) {
				if (r) {
					console.log(r.message)
					if (r.message){
						$(".add-assignment-btn").css("display", "none");
					}
				}
			}
		});
	}

})
