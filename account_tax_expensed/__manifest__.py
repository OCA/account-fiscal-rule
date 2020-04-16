# Copyright 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Taxes accounted as Expense on Customer Invoices",
    "summary": """
        Taxes supported by the seller computed on Customer Invoices.""",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": "Open Source Integrators,Odoo Community Association (OCA)",
    "depends": ["account"],
    "data": [
        "views/account_invoice.xml",
        "views/account_tax.xml",
    ],
}
