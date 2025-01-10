

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt

@frappe.whitelist()
def make_stock_entry(source_name, target_doc=None):
    def update_item(obj, target, source_parent):
        qty = (
            flt(obj.qty) - flt(obj.transferred)
            if flt(obj.qty) > flt(obj.transferred)
            else 0
        )
        target.qty = qty
        target.against_sales_order_item = obj.name
        target.against_sales_order= obj.parent
        target.conversion_factor = 1
      

    def set_missing_values(source, target):
        doc = frappe.get_doc(target)
        source_doc = frappe.get_doc(source)
        target.set_transfer_qty()
        target.set_actual_qty()
        target.calculate_rate_and_amount(raise_error_if_no_rate=False)

    doclist = get_mapped_doc(
        "Sales Order",
        source_name,
        {
            "Sales Order": {
                "doctype": "Stock Entry",
                "field_map": {
                    "project": "project",
                },
            },
            "Sales Order Item": {
                "doctype": "Stock Entry Detail",
                "field_map": {
                    "item_code": "item_code",
                    "item_name": "item_name",
                    "item_description": "item_description",
                    "qty": "qty",
                    "rate": "rate",
                    "uom": "uom",
                },
                "postprocess": update_item,
                "condition": lambda doc: (
                    flt(doc.transferred, doc.precision("transferred"))
                    < flt(doc.qty, doc.precision("qty"))
                ),
            },
        },
        target_doc,
        set_missing_values,
    )
    return doclist
