import frappe
from frappe import _
from hrms.payroll.doctype.salary_slip.salary_slip import SalarySlip
from hrms.payroll.doctype.salary_slip.salary_slip import *
from frappe.utils import flt


class CustomSalarySlip(SalarySlip):
	def update_component_row(
		self,
		component_data,
		amount,
		component_type,
		additional_salary=None,
		is_recurring=0,
		data=None,
		default_amount=None,
		remove_if_zero_valued=None,
	):
		component_row = None
		for d in self.get(component_type):
			if d.salary_component != component_data.salary_component:
				continue

			if (not d.additional_salary and (not additional_salary or additional_salary.overwrite)) or (
				additional_salary and additional_salary.name == d.additional_salary
			):
				component_row = d
				break

		if additional_salary and additional_salary.overwrite:
			# Additional Salary with overwrite checked, remove default rows of same component
			self.set(
				component_type,
				[
					d
					for d in self.get(component_type)
					if d.salary_component != component_data.salary_component
					or (d.additional_salary and additional_salary.name != d.additional_salary)
					or d == component_row
				],
			)

		if not component_row:
			if not (amount or default_amount) and remove_if_zero_valued:
				return

			component_row = self.append(component_type)
			for attr in (
				"depends_on_payment_days",
				"salary_component",
				"abbr",
				"do_not_include_in_total",
				"is_tax_applicable",
				"is_flexible_benefit",
				"variable_based_on_taxable_salary",
				"exempted_from_income_tax",
			):
				component_row.set(attr, component_data.get(attr))

		if additional_salary:
			if additional_salary.overwrite:
				component_row.additional_amount = flt(
					flt(amount) - flt(component_row.get("default_amount", 0)),
					component_row.precision("additional_amount"),
				)
			else:
				component_row.default_amount = 0
				component_row.additional_amount = amount

			component_row.is_recurring_additional_salary = is_recurring
			component_row.additional_salary = additional_salary.name
			component_row.deduct_full_tax_on_selected_payroll_date = (
				additional_salary.deduct_full_tax_on_selected_payroll_date
			)
		else:
			component_row.default_amount = default_amount or amount
			component_row.additional_amount = 0
			component_row.deduct_full_tax_on_selected_payroll_date = (
				component_data.deduct_full_tax_on_selected_payroll_date
			)

		component_row.amount = amount
		self.update_component_amount_based_on_payment_days(component_row, remove_if_zero_valued)

			
		doc=frappe.get_doc("Salary Structure Assignment",self._salary_structure_assignment.name)
		for d in doc.custom_salary_component_variable:
			if d.salary_component==component_row.salary_component:
				if d.skip_calculation:
					component_row.amount=0.00
				else:
					if d.type=="Fuel Allowance":
						component_row.amount=d.variable*self.payment_days
					if d.type=="Night Allowance":
						component_row.amount=d.variable*350
					
					if d.type=="Loyalty Allowance":
						component_row.amount= (d.variable / 100) *self._salary_structure_assignment.base
					if d.type=="Performance Allowance":
						component_row.amount= (d.variable / 100) *self._salary_structure_assignment.base
				


		if data:
			data[component_row.abbr] = component_row.amount



@frappe.whitelist()
def get_all_variable_component(salary_structure):
    doc = frappe.get_doc("Salary Structure", salary_structure)
    
    components = []

    for earning in doc.earnings:
        variable_component, component_type = frappe.db.get_value(
            "Salary Component", 
            earning.salary_component, 
            ["custom_variable_component", "custom_component_type"]
        )

        if variable_component:
            components.append({
                "component": earning.salary_component,
                "type": component_type
            })

    return components

