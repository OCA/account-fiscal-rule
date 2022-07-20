# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Multi Vat Sale",
    "summary": """
        Determines the tax administration from the delivery address of the invoice.""",
    "version": "13.0.1.0.2",
    "development_status": "Beta",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "maintainers": ["ThomasBinsfeld"],
    "website": "https://github.com/OCA/account-fiscal-rule",
    "depends": ["account_multi_vat", "sale"],
    "data": ["views/sale_order.xml", "report/sale_order_report.xml"],
    "demo": [],
}
