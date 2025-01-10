frappe.ui.form.on("Stock Entry", {
    refresh: function (frm, doc, dt, dn) {
        frm.add_custom_button(__('Stock Entry'),
            function () {
                if (!cur_frm.doc.project) {
                    frappe.throw({
                        title: __("Mandatory"),
                        message: __("Please Select a Project")
                    });
                }
                else {
                    erpnext.utils.map_current_doc({
                        method: "ving.custom_script.sales_order.sales_order.make_stock_entry",
                        source_doctype: "Sales Order",
                        target: frm,
                        setters: {
                            custom_project: frm.doc.project,
                        },
                        get_query_filters: {
                            project: frm.doc.project,
                            docstatus: 1,
                        },

                    })
                }

            }, __("Get Items From"));

    },
 
  
  

    
   
})
