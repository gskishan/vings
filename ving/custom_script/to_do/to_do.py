import frappe
@frappe.whitelist()
def validate(self,method):
  pass



def create_todo(description, reference_type, reference_name):
	todo = frappe.new_doc("ToDo")
	todo.description = description
	todo.owner = "Administrator"
	todo.reference_type = reference_type
	todo.reference_name = reference_name
	todo.insert()

