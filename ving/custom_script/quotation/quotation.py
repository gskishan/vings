from erpnext.selling.doctype.quotation.quotation import Quotation
from erpnext.selling.doctype.quotation.quotation import *

import frappe
from frappe import _

class CustomQuotation(Quotation):
    @frappe.whitelist()
    def get_designing(self):
        if self.designing:
            self.set("equipment",[])
            self.set("designing_total",[])
            self.set("items",[])


            doc=frappe.get_doc("Designing",self.designing)
            for d in doc.equipment:
                eq=self.append("equipment",{})
                eq.floor=d.floor
                eq.space=d.space
                eq.length=d.length
                eq.width=d.width
                eq.area=d.area
                eq.item_code=d.item_code
                eq.equipment_description=d.equipment_description
                eq.capacity=d.capacity
                eq.tr=d.tr
                eq.qty=d.qty
                eq.total_tr=d.total_tr

            for i in doc.designing_total:
                des=self.append("designing_total",{})
                des.floor=i.floor
                des.total_capacity_index=i.total_capacity_index
                des.total_tr=d.total_tr
                des.total_hp=i.total_hp
                des.total_qty=i.total_qty
                des.hp=i.hp
                des.odu_capacity=i.odu_capacity
                des.diversity=i.diversity
                des.max_capacity=i.max_capacity
                des.odu_combination__1=i.odu_combination__1
                des.odu_combination__2=i.odu_combination__2


            for f in doc.bill_of_quantity:
                row=self.append("items",{})
                row.item_code=f.item_code
                row.description=f.description
                row.qty=f.quantity
                row.uom=f.unit
                row.rate=f.rate
                row.type="Bill Item"
            
            for l in doc.designing_low_side:
                row=self.append("items",{})
                row.item_code=l.item_code
                row.qty=l.quantity
                row.uom=l.unit
                row.rate=l.rate
                row.type="Installation Item"