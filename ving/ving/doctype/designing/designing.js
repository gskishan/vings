// Copyright (c) 2024, GKT and contributors
// For license information, please see license.txt

frappe.ui.form.on("Designing", {
    refresh(frm) {

        $('[data-fieldname="insert_total"]button').css("background-color", "#2490ef")
		$('[data-fieldname="insert_total"]button').css("color", "white")


	if (cur_frm.doc.docstatus==1){
        frm.add_custom_button("Create Quotation", function () {
		    frappe.new_doc('Quotation', {
			designing:cur_frm.doc.name,
		      });
        });
	}
    },
    insert_total:function(frm){
        console.log("yes")
        frappe.call({
            doc: cur_frm.doc,
            method: "get_totals",
            callback: function (r) {
                console.log(r.message,"1")
                cur_frm.refresh_fields()

            }
        });
    }

});
frappe.ui.form.on("Designing equipment", {
    equipment_add: function (frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        const previous_rows = frm.doc.equipment;

        if (previous_rows.length > 1) {
            const last_row = previous_rows[previous_rows.length - 2];
            row.floor = last_row.floor;
        }

        frm.refresh_field('equipment');
    },
    tr: function (frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        console.log(row.tr * row.qtyy)
        if (row.tr && row.qty) {
            row.total_tr = row.tr * row.qty
        }
        cur_frm.refresh_fields()
    },
    qty: function (frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        console.log(row.tr * row.qtyy)
        if (row.tr && row.qty) {
            row.total_tr = row.tr * row.qty
        }
        cur_frm.refresh_fields()
    },
    length: function (frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        if (row.length && row.width) {
            row.area = row.length * row.width
        }
        cur_frm.refresh_fields()
    },
    width: function (frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        if (row.length && row.width) {
            row.area = row.length * row.width
        }
        cur_frm.refresh_fields()
    },
    



});

frappe.ui.form.on("Designing Low Side", {
    quantity: function (frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        if (row.rate && row.quantity) {
            row.amount = row.quantity * row.rate

        }
        cur_frm.refresh_fields()
    },
    rate: function (frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        if (row.rate && row.quantity) {
            row.amount = row.quantity * row.rate

        }
        cur_frm.refresh_fields()
    }


});
