import frappe
from frappe import _
from frappe.model.mapper import get_mapped_doc
from frappe.model.document import Document


@frappe.whitelist()
def update_all():
    sql="""select name from `tabItem Price` """
    data =frappe.db.sql(sql,as_dict=1)
    for d in data:
        self=frappe.get_doc("Item Price",d.get("name"))
        method=None
        validate(self,method)
@frappe.whitelist()
def on_trash(self,method=None):
    pass
@frappe.whitelist()
def validate(self,method=None):
    item_row=checkif(self)
    if item_row:
        item=frappe.get_doc("Item price summmary",item_row)
        item.rate=self.price_list_rate
        item.from_date=self.valid_from
        item.to_date=self.valid_upto
        item.save()
    else:
        itm=frappe.get_doc("Item",self.item_code)
        row=itm.append("custom_item_prices",{})
        row.price_list=self.name
        row.rate=self.price_list_rate
        row.from_date=self.valid_from
        row.to_date=self.valid_upto
        if self.selling:
            row.type="Selling"
        else:
            row.type="Buying"
        imt.save()



def  checkif(self):
    sql="""select name from `tabItem price summmary` where item_price="{0}" and parent="{1}" """.format(self.name,self.item_code)
    data =frappe.db.sql(sql,as_dict=1)
    if data:
        return data[0].name
    else:
        return None
