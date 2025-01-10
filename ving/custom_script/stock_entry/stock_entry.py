
import frappe

@frappe.whitelist()
def on_submit(self,method=None):
    if self.project and self.stock_entry_type=="Material Transfer":
        proj=frappe.get_doc("Project",self.project)
        proj.db_set("custom_total_transferred_material_cost",proj.custom_total_transferred_material_cost+self.total_outgoing_value)

@frappe.whitelist()
def on_cancel(self,method=None):
    if self.project and self.stock_entry_type=="Material Transfer":
        proj=frappe.get_doc("Project",self.project)
        proj.db_set("custom_total_transferred_material_cost",proj.custom_total_transferred_material_cost-self.total_outgoing_value)
