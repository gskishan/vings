frappe.ui.form.on('Timesheet', {
	custom_from_time(frm) {
		if (frm.doc.custom_from_time){
		    cur_frm.set_value("custom_day",(getDayOfWeek(frm.doc.custom_from_time)))
		    
		}
	}
})


function getDayOfWeek(dateString) {
    const date = new Date(dateString);
    const options = { weekday: 'long' };
    return date.toLocaleDateString('en-US', options);
}

