# Copyright (C) 2023 - ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Account fiscal position - Multi foreign VAT",
    "summary": "Allow having multiple foreign vat with same location",
    "version": "16.0.1.0.0",
    "author": "ForgeFlow S.L.,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-fiscal-rule",
    "license": "AGPL-3",
    "depends": ["account", "base_vat", "partner_identification"],
    "data": [
        "views/account_fiscal_position.xml",
        "views/account_move.xml",
    ],
}
