
import frappe

@frappe.whitelist()
def on_submit(self,method=None):
    if self.project and self.payment_type=="Receive":
        proj=frappe.get_doc("Project",self.project)
        proj.db_set("custom_total_amount_received",proj.custom_total_amount_received+self.paid_amount)

@frappe.whitelist()
def on_cancel(self,method=None):
    if self.project and self.payment_type=="Receive":
        proj=frappe.get_doc("Project",self.project)
        proj.db_set("custom_total_amount_received",proj.custom_total_amount_received-self.paid_amount)
