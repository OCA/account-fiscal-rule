# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


{
    "name": "Default Partner Fiscal Position",
    "version": "14.0.1.0.0",
    "author": "Odoo Community Association (OCA), Coop IT Easy SC",
    "category": "Accounting",
    "website": "https://github.com/OCA/account-fiscal-rule",
    "depends": ["account"],
    "data": [
        "views/account_fiscal_position.xml",
        "security/ir.model.access.csv",
    ],
    "license": "AGPL-3",
    "summary": "Computes default partner fiscal position.",
    "installable": True,
}
