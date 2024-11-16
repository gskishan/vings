
frappe.ui.form.on("Quotation", {
    onload:function(frm) {
    if (cur_frm.is_new() && cur_frm.doc.designing){
        frappe.call({
            doc: cur_frm.doc,
            method: "get_designing",
            callback: function (r) {
                console.log(r.message,"1")
                cur_frm.refresh_fields()

            }
        });

    }
    }

})