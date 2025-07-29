
frappe.ui.form.on("Quotation", {
    onload:function(frm) {
    if (cur_frm.is_new() && cur_frm.doc.designing &&  !cur_frm.doc.amended_from){
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
