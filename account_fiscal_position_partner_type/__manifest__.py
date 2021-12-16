# -*- coding: utf-8 -*-
# Copyright 2021 FactorLibre - Luis J. Salvatierra <luis.salvatierra@factorlibre.com>
# Copyright 2021 Valentín Vinagre <valentin.vinagre@sygel.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Fiscal Position Partner Type",
    "version": "10.0.1.0.0",
    "category": "Accounting & Finance",
    "website": "https://github.com/OCA/account-fiscal-rule",
    "author": "Sygel Technology," "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["account", "base_vat"],
    "data": [
        "views/res_company.xml",
        "views/res_partner.xml",
        "views/account_fiscal_position.xml",
    ],
}
