# Copyright (c) 2024, GKT and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document
from collections import defaultdict


class Designing(Document):
	def validate(self):
		self.fill_bill()
		self.get_totals()




	def get_totals(self):
		floor_totals = defaultdict(lambda: {"capacity": 0, "qty": 0, "total_tr": 0, "tr": 0})

		for item in self.equipment:
			floor = item.get("floor")
			floor_totals[floor]["capacity"] += item.get("capacity", 0)
			floor_totals[floor]["qty"] += item.get("qty", 0)
			floor_totals[floor]["tr"] += item.get("tr", 0)
			floor_totals[floor]["total_tr"] += item.get("total_tr", 0)


		self.designing_total=[]

		for floor, totals in floor_totals.items():
			
			row=self.append("designing_total",{})
			row.floor=floor
			row.total_capacity_index=totals['capacity']
			row.total_tr=totals['total_tr']
			# row.total_hp=totals['total_hp']  #need to add
			row.total_qty=totals['qty']  
			row.hp=totals['hp']
			# row.odu_capacity=totalsd


			# print(f"Floor: {floor}")
			# print(f"  Total Capacity: {totals['capacity']}")
			# print(f"  Total Quantity: {totals['qty']}")
			# print(f"  Total TR: {totals['tr']}")
			# print(f"  Total Total_TR: {totals['total_tr']}")


	def fill_bill(self):
		data=self.sum_item()
		if data:
			for d in data:
				if not self.item_already_in(d.get("item_code")):
					row=self.append("bill_of_quantity",{})
					row.item_code=d.get("item_code")
					row.quantity=d.get("qty")
					row.unit=frappe.db.get_value('Item', d.get("item_code"), 'stock_uom')
					row.rate=get_item_price(d.get("item_code"),"Standard Selling")
					row.amount=row.rate*row.quantity
				
	def item_already_in(self,item):
		status=False
		for d in self.bill_of_quantity:
			if d.item_code==item:
				status=True
		return status

	def sum_item(self):
		item_totals = {}

		for item in self.equipment:
			code = item.get("item_code")
			qty = item.get("qty")
			
			if code in item_totals:
				item_totals[code] += qty
			else:
				item_totals[code] = qty

		return [{"item_code": code, "qty": total_qty} for code, total_qty in item_totals.items()]



def get_item_price(item_code, price_list):
   
    if not item_code or not price_list:
        frappe.throw("Item code and price list are required.")

    price_data = frappe.db.get_value(
        "Item Price",
        {"item_code": item_code, "price_list": price_list},
        ["price_list_rate"],
        as_dict=True
    )

    if price_data:
        return price_data.price_list_rate
    else:
        frappe.msgprint(f"Price not found for item {item_code} in price list {price_list}.")
