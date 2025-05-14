import frappe

def create_lead_address(doc, method):
    # Avoid duplication by checking if an address already exists
    existing_address = frappe.get_all("Address",
        filters={
            "link_doctype": "Lead",
            "link_name": doc.name
        },
        limit=1
    )

    if not existing_address:
        # Create a new Address linked to this Lead
        address = frappe.get_doc({
            "doctype": "Address",
            "address_title": doc.name,
            "address_type": "Billing",
            "address_line1": doc.get("custom_address_line1") or "",
            "address_line2": doc.get("custom_address_line2") or "",
            "city": doc.get("custom_city1") or "",
            "state": doc.get("custom_state1") or "",
            "pincode": doc.get("custom_postal_code") or "",
            "links": [{
                "link_doctype": "Lead",
                "link_name": doc.name
            }]
        })
        address.insert(ignore_permissions=True)