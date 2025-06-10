
import frappe
from frappe import _
from hrms.payroll.doctype.salary_slip.salary_slip import SalarySlip
from hrms.payroll.doctype.salary_slip.salary_slip import *
from frappe.utils import flt
import unicodedata
from datetime import date

import frappe
from frappe import _
from frappe.utils import (
	add_days,
	cint,
	date_diff,
	flt,

	getdate,
	rounded,
)
from hrms.payroll.doctype.payroll_period.payroll_period import (
	get_period_factor,
)
from hrms.payroll.doctype.salary_slip.salary_slip_loan_utils import (
	
	set_loan_repayment,
)

from hrms.hr.doctype.leave_application.leave_application import get_leave_details

import erpnext
from ving.ving.report.employees_working_on_a_holiday_with_employee_filters.employees_working_on_a_holiday_with_employee_filters import execute as work_on_holidays

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
		self.calculate_net_pay()


	def before_validate(self):
		self.calculate_deduction_unpaid_leave()
		self.calculate_net_pay()

	@frappe.whitelist()
	def calculate_net_pay(self, skip_tax_breakup_computation: bool = False):
		def set_gross_pay_and_base_gross_pay():
			self.gross_pay = self.get_component_totals("earnings", depends_on_payment_days=1)
			self.base_gross_pay = flt(
				flt(self.gross_pay) * flt(self.exchange_rate), self.precision("base_gross_pay")
			)

		if self.salary_structure:
			self.calculate_component_amounts("earnings")

		# get remaining numbers of sub-period (period for which one salary is processed)
		if self.payroll_period:
			self.remaining_sub_periods = get_period_factor(
				self.employee,
				self.start_date,
				self.end_date,
				self.payroll_frequency,
				self.payroll_period,
				joining_date=self.joining_date,
				relieving_date=self.relieving_date,
			)[1]

		set_gross_pay_and_base_gross_pay()

		if self.salary_structure:
			self.calculate_component_amounts("deductions")

		set_loan_repayment(self)

		self.set_precision_for_component_amounts()
		self.set_net_pay()
		if not skip_tax_breakup_computation:
			self.compute_income_tax_breakup()

	def set_net_pay(self):
		self.total_deduction = self.get_component_totals("deductions")
		self.base_total_deduction = flt(
			flt(self.total_deduction) * flt(self.exchange_rate), self.precision("base_total_deduction")
		)
		self.net_pay = flt(self.gross_pay) - (
			flt(self.total_deduction) + flt(self.get("total_loan_repayment"))
		)
		self.rounded_total = rounded(self.net_pay)
		self.base_net_pay = flt(flt(self.net_pay) * flt(self.exchange_rate), self.precision("base_net_pay"))
		self.base_rounded_total = flt(rounded(self.base_net_pay), self.precision("base_net_pay"))
		if self.hour_rate:
			self.base_hour_rate = flt(
				flt(self.hour_rate) * flt(self.exchange_rate), self.precision("base_hour_rate")
			)
		self.set_net_total_in_words()




	def get_working_days_details(self, lwp=None, for_preview=0):
		payroll_settings = frappe.get_cached_value(
			"Payroll Settings",
			None,
			(
				"payroll_based_on",
				"include_holidays_in_total_working_days",
				"consider_marked_attendance_on_holidays",
				"daily_wages_fraction_for_half_day",
				"consider_unmarked_attendance_as",
			),
			as_dict=1,
		)

		consider_marked_attendance_on_holidays = (
			payroll_settings.include_holidays_in_total_working_days
			and payroll_settings.consider_marked_attendance_on_holidays
		)

		daily_wages_fraction_for_half_day = flt(payroll_settings.daily_wages_fraction_for_half_day) or 0.5

		working_days = date_diff(self.end_date, self.start_date) + 1
		if for_preview:
			self.total_working_days = working_days
			self.payment_days = working_days
			return

		holidays = self.get_holidays_for_employee(self.start_date, self.end_date)
		working_days_list = [add_days(getdate(self.start_date), days=day) for day in range(0, working_days)]

		if not cint(payroll_settings.include_holidays_in_total_working_days):
			working_days_list = [i for i in working_days_list if i not in holidays]

			working_days -= len(holidays)
			if working_days < 0:
				frappe.throw(_("There are more holidays than working days this month."))

		if not payroll_settings.payroll_based_on:
			frappe.throw(_("Please set Payroll based on in Payroll settings"))

		if payroll_settings.payroll_based_on == "Attendance":
			actual_lwp, absent = self.calculate_lwp_ppl_and_absent_days_based_on_attendance(
				holidays, daily_wages_fraction_for_half_day, consider_marked_attendance_on_holidays
			)
			self.absent_days = absent
		else:
			actual_lwp = self.calculate_lwp_or_ppl_based_on_leave_application(
				holidays, working_days_list, daily_wages_fraction_for_half_day
			)

		if not lwp:
			lwp = actual_lwp
		elif lwp != actual_lwp:
			frappe.msgprint(
				_("Leave Without Pay does not match with approved {} records").format(
					payroll_settings.payroll_based_on
				)
			)

		self.leave_without_pay = lwp
		self.total_working_days = working_days

		payment_days = self.get_payment_days(payroll_settings.include_holidays_in_total_working_days)

		if flt(payment_days) > flt(lwp):
			self.payment_days = flt(payment_days) - flt(lwp)

			if payroll_settings.payroll_based_on == "Attendance":
				self.payment_days -= flt(absent)

			consider_unmarked_attendance_as = payroll_settings.consider_unmarked_attendance_as or "Present"

			if (
				payroll_settings.payroll_based_on == "Attendance"
				and consider_unmarked_attendance_as == "Absent"
			):
				unmarked_days = self.get_unmarked_days(
					payroll_settings.include_holidays_in_total_working_days, holidays
				)
				self.absent_days += unmarked_days  # will be treated as absent
				self.payment_days -= unmarked_days
		else:
			self.payment_days = 0
		filters = {
			"company": self.get("company"),
			"employee": self.get("employee"),
			"from_date": self.get("start_date"),
			"to_date": self.get("end_date"),
		}
		filters = frappe._dict(filters)
		
		result = work_on_holidays(filters)[1]
		count=len(result)
		self.set("custom_worked_on_holiday",count)

	def get_component_totals(self, component_type, depends_on_payment_days=0):
		total = 0.0
		for d in self.get(component_type):
			if not d.do_not_include_in_total:
				if depends_on_payment_days:
					amount = self.get_amount_based_on_payment_days(d)[0]
				else:
					amount = flt(d.amount, d.precision("amount"))
					

				total += amount
		return total

	@frappe.whitelist()
	def calculate_deduction_unpaid_leave(self):
		
		if (self.leave_without_pay and self.leave_without_pay > 0) or (self.absent_days and self.absent_days>0):
			
			total_amount = 0
			for d in self.earnings:
				if frappe.db.get_value('Salary Component', d.salary_component, 'custom_deduct_on_unpaid_leave'):
					total_amount += d.amount
			
			if total_amount > 0:
				
				if self.total_working_days and self.total_working_days > 0:  
					total_amount = total_amount or 0
					total_working_days = self.total_working_days 
					absent_days = self.absent_days or 0
					leave_without_pay = self.leave_without_pay or 0
					

					total_deduction = (total_amount / total_working_days) * (absent_days + leave_without_pay)
					

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
							holidays = self.get_holidays_for_employee(self.start_date, self.end_date)
							data = get_leave_details(self.employee, self.end_date)
							total_leaves_taken = sum(leave.get("leaves_taken", 0) for leave in data["leave_allocation"].values())


							no_of_holiday=flt(len(holidays))
							# frappe.errprint([self.total_working_days,no_of_holiday,total_leaves_taken,self.leave_without_pay,self.absent_days,self.custom_worked_on_holiday])
							component_row.amount=d.variable*(self.total_working_days-no_of_holiday-total_leaves_taken-self.leave_without_pay-self.absent_days+self.custom_worked_on_holiday)
						if d.type=="Night Allowance":
							component_row.amount=d.variable*350
						
						if d.type=="Loyalty Allowance":
							component_row.amount= (d.variable / 100) * basic_sal
						if d.type=="Performance Allowance":
							component_row.amount= (d.variable / 100) * basic_sal
						leave_data = get_leave_details(self.employee, self.end_date)
						leave_allocation = leave_data.get("leave_allocation", {})

						total_leaves_taken = 0
						for leave_type, details in leave_allocation.items():
							total_leaves_taken += details.get("leaves_taken", 0)
						if d.type=="No Leave bonus":

							
							if total_leaves_taken==0:
								component_row.amount= 500
							else:
								component_row.amount= 0.00
						if d.type=="One day extra payment":
							if total_leaves_taken==0:
								ttl=0
								for e in self.earnings:
									if e.salary_component in ["Basic","House Rent Allowance","B & L Allowance","Dearness Allowance","Wheat Allowance"]:
										ttl+=e.amount
								# for de in self.deductions:
								# 	if de.salary_component =='ESI':
								# 		ttl+=de.amount
								component_row.amount=ttl/self.total_working_days
							else:
								component_row.amount= 0.00

						if d.type=="Work on Holidays":
							if self.custom_worked_on_holiday:
								ttl=0
								for e in self.earnings:
									if e.salary_component in ["Basic","House Rent Allowance","B & L Allowance","Dearness Allowance","Wheat Allowance"]:
										ttl+=e.amount
								for de in self.deductions:
									if de.salary_component =='ESI':
										ttl+=de.amount
								leave_appplication=get_leave_details(self.employee,self.end_date)
								leaves_taken = leave_appplication["leave_allocation"].get("Casual Leave", {}).get("leaves_taken", 0)

								
								component_row.amount=ttl/self.total_working_days*(self.custom_worked_on_holiday)
							else:
								component_row.amount= 0.00
						
								
				


		if data:
			data[component_row.abbr] = component_row.amount
		self.calculate_deduction_unpaid_leave()



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
