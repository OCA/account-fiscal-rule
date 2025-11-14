{
    "name": "Avalara Avatax Line Grouping",
    "version": "16.0.1.0.0",
    "category": "Accounting",
    "summary": "Group document lines as a single line for Avatax computation",
    "description": """
AvaTax Line Grouping
====================

This addon extends ``account_avatax_oca`` to optionally send a single
aggregated line per document (Sales Order / Customer Invoice) to AvaTax
for tax computation, instead of one line per Odoo line.
""",
    "author": "Binhex, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-fiscal-rule",
    "license": "AGPL-3",
    "depends": [
        "account_avatax_oca",
        "account_avatax_sale_oca",
    ],
    "data": [
        "views/avalara_salestax_view.xml",
    ],
    "demo": [],
    "installable": True,
    "application": False,
}
