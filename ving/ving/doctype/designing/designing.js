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
    },
    tr:function(frm,cdt,cdn){
        const row = locals[cdt][cdn];
        console.log(row.tr*row.qtyy)
        if (row.tr && row.qty){
            row.total_tr=row.tr*row.qty
        }
        cur_frm.refresh_fields()
    },
    qty:function(frm,cdt,cdn){
        const row = locals[cdt][cdn];
        console.log(row.tr*row.qtyy)
        if (row.tr && row.qty){
            row.total_tr=row.tr*row.qty
        }
        cur_frm.refresh_fields()
    },
    length:function(frm,cdt,cdn){
        const row = locals[cdt][cdn];
        if (row.length && row.width){
            row.area=row.length*row.width
        }
        cur_frm.refresh_fields()
    },
    width:function(frm,cdt,cdn){
        const row = locals[cdt][cdn];
        if (row.length && row.width){
            row.area=row.length*row.width
        }
        cur_frm.refresh_fields()
    }



});

frappe.ui.form.on("Designing Low Side", {
    quantity: function(frm, cdt, cdn) {
        const row = locals[cdt][cdn]; 
        if (row.rate && row.quantity){
            row.amount=row.quantity*row.rate

        }
        cur_frm.refresh_fields()
    },
    rate: function(frm, cdt, cdn) {
        const row = locals[cdt][cdn]; 
        if (row.rate && row.quantity){
            row.amount=row.quantity*row.rate

        }
        cur_frm.refresh_fields()
    }


});