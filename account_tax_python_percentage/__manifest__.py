# Copyright 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Define Taxes as Python code using Percentage",
    "summary": """
        Extend Python code computed taxes to also have
        the Percentage field available.
    """,
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": "Open Source Integrators,Odoo Community Association (OCA)",
    "depends": ["account_tax_python"],
    "data": [
        "views/account_tax.xml",
    ],
}
