import frappe
from frappe import _
from hrms.payroll.doctype.salary_slip.salary_slip import SalarySlip
from hrms.payroll.doctype.salary_slip.salary_slip import *
from frappe.utils import flt


class CustomSalarySlip(SalarySlip):
	def pull_sal_struct(self):
		from hrms.payroll.doctype.salary_structure.salary_structure import make_salary_slip

		if self.salary_slip_based_on_timesheet:
			self.salary_structure = self._salary_structure_doc.name
			self.hour_rate = self._salary_structure_doc.hour_rate
			self.base_hour_rate = flt(self.hour_rate) * flt(self.exchange_rate)
			self.total_working_hours = sum([d.working_hours or 0.0 for d in self.timesheets]) or 0.0
			wages_amount = self.hour_rate * self.total_working_hours

			self.add_earning_for_hourly_wages(self, self._salary_structure_doc.salary_component, wages_amount)

		make_salary_slip(self._salary_structure_doc.name, self)
		self.calculate_deduction_unpaid_leave()

	def before_validate(self):
		self.calculate_deduction_unpaid_leave()
	@frappe.whitelist()
	def calculate_deduction_unpaid_leave(self):
		frappe.errprint("1")
		
		if self.leave_without_pay > 0:
			frappe.errprint([self.leave_without_pay, len(self.earnings),"2"])
			
			total_amount = 0
			for d in self.earnings:
				if frappe.db.get_value('Salary Component', d.salary_component, 'custom_deduct_on_unpaid_leave'):
					frappe.errprint([self.leave_without_pay, "23"])
					total_amount += d.amount
			
			if total_amount > 0:
				frappe.errprint([total_amount, "24"])
				
				if self.total_working_days > 0:  
					total_deduction = (total_amount / self.total_working_days) * self.leave_without_pay
					frappe.errprint([total_deduction, "25"])
				else:
					frappe.throw("Total working days cannot be zero.")
					return
				
				found = False
				for d in self.deductions:
					if d.salary_component == "Leave W/O Pay":
						d.amount = total_deduction
						found = True
						break
				
				if not found:
					row = self.append("deductions", {})
					row.salary_component = "Leave W/O Pay"
					row.amount = total_deduction

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
		basic_sal=0
		for c in self.earnings:
			if c.salary_component=="Basic":
				basic_sal=c.amount
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
						component_row.amount= (d.variable / 100) * basic_sal
					if d.type=="Performance Allowance":
						component_row.amount= (d.variable / 100) * basic_sal
					if d.type=="No Leave bonus":
						if self.total_working_days==self.payment_days:
							component_row.amount= 500
						else:
							component_row.amount= 0.00
							
				


		if data:
			data[component_row.abbr] = component_row.amount
		self.calculate_deduction_updaid_leave()



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
