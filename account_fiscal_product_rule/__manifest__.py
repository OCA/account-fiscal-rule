# Copyright 2022 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Account Fiscal Product Rule",
    "version": "14.0.1.0.0",
    "category": "Accounting & Finance",
    "author": "Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-fiscal-rule",
    "license": "AGPL-3",
    "depends": ["account"],
    "data": [
        "security/ir.model.access.csv",
        "views/product.xml",
        "views/account_fiscal_position.xml",
    ],
    "installable": True,
}
