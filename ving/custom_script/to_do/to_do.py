import frappe
@frappe.whitelist()
def validate(self,method):
	if self.reference_type=="Task":
		sql="""select * from `tabTask Depends On` where parent="{0}" """.format(self.reference_name)
		for d in frappe.db.sql(sql, as_dict=True):
			if check_todo_exists(d,self):
				create_todo(d.subject,"Task",d.task,self)



def create_todo(description, reference_type, reference_name,self):
	todo = frappe.new_doc("ToDo")
	todo.description = description
	todo.allocated_to = self.allocated_to
	todo.date = self.date
	todo.priority =self.priority
	todo.assigned_by = self.assigned_by
	todo.owner = self.owner
	todo.assigned_by_full_name = self.assigned_by_full_name

	todo.reference_type = reference_type
	todo.reference_name = reference_name
	todo.insert()

@frappe.whitelist()
def check_todo_exists(d,self):
    exists = frappe.db.exists('ToDo', {
        'reference_name': d.task,
        'reference_type': "Task",
        'allocated_to': self.allocated_to
    })
    return exists
