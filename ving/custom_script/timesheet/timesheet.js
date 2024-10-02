
frappe.ui.form.on('Timesheet', {
	// custom_from_time(frm) {
	// 	if (frm.doc.custom_from_time){
	// 	    cur_frm.set_value("custom_day",(getDayOfWeek(frm.doc.custom_from_time)))
		    
	// 	}
	// }
})

frappe.ui.form.on('Timesheet Detail', {
	to_time: function (frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		if (d.to_time){
			d.custom_to_day=getDayOfWeek(d.to_time)
			cur_frm.refresh()
			
			
		    
		}
	},
	from_time: function (frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		if (d.from_time){
			d.custom_from_day=getDayOfWeek(d.from_time)
			cur_frm.refresh()
		    
		}
	}
})



function getDayOfWeek(dateString) {
    const date = new Date(dateString);
    const options = { weekday: 'long' };
    return date.toLocaleDateString('en-US', options);
}

