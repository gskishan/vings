// Copyright (c) 2024, GKT and contributors
// For license information, please see license.txt

frappe.ui.form.on("Designing", {
	refresh(frm) {

	},
    
});
frappe.ui.form.on("Designing equipment", {
    equipment_add: function(frm, cdt, cdn) {
        const row = locals[cdt][cdn]; 
        const previous_rows = frm.doc.equipment; 
    
        if (previous_rows.length > 1) {
            const last_row = previous_rows[previous_rows.length - 2]; 
            row.floor = last_row.floor; 
        } 
    
        frm.refresh_field('equipment');
    }


});