# Copyright 2021 Valentín Vinagre <valentin.vinagre@sygel.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Fiscal Position Partner Type",
    "version": "16.0.1.0.1",
    "category": "Accounting & Finance",
    "website": "https://github.com/OCA/account-fiscal-rule",
    "author": "Sygel Technology," "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "development_status": "Production/Stable",
    "depends": ["account"],
    "data": [
        "views/res_company.xml",
        "views/res_partner.xml",
        "views/account_fiscal_position.xml",
    ],
}
