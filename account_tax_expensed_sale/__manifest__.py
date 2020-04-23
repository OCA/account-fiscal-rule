# Copyright 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Expensed Taxes on Sales Orders",
    "summary": """
        Vendor supported taxes on Sale Orders""",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": "Open Source Integrators,Odoo Community Association (OCA)",
    "depends": ["account_tax_expensed", "sale"],
    "data": [
        "views/sale_order.xml",
    ],
    "auto_install": True,  # Glue module
}
