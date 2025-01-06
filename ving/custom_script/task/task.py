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

	def validate(self):
		self.validate_dates()
		self.validate_progress()
		self.validate_status()
		self.update_depends_on()
		self.validate_dependencies_for_template_task()
		self.validate_completed_on()
		self.update_parent_status()



	def update_parent_status(self):
		current_status = frappe.db.get_value("Task", self.name, "status")
		if (
			self.parent_task
			and self.status == "Completed"
			and current_status != "Completed"
		):
			sql = """
				SELECT COUNT(name) AS incomplete_count
				FROM `tabTask`
				WHERE parent_task = %s
				AND name != %s
				AND status != 'Completed'
			"""
			incomplete_tasks = frappe.db.sql(sql, values=(self.parent_task, self.name), as_dict=True)

			if incomplete_tasks[0].incomplete_count == 0:
				frappe.db.set_value("Task", self.parent_task, "status", "Completed")

		elif (
			self.parent_task
			and current_status == "Completed"
			and self.status != "Completed"
		):
			frappe.db.set_value("Task", self.parent_task, "status", self.status)



					

			

							

