from erpnext.projects.doctype.task.task import Task
from erpnext.projects.doctype.task.task import *

import frappe
from frappe import _
class CustomTask(Task):
	@frappe.whitelist()
	def get_assigment_status(self):
			status=False
			for d in self.depends_on:
				if frappe.db.get_value("Task", d.task, "status") not in ("Completed", "Cancelled"):
					status=True
			return status
						

