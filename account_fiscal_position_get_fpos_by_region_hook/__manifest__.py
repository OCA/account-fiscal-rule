# Copyright 2021 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Fiscal Position Get Fpos By Region Hook",
    "summary": """
        Adds a hook to the function _get_fpos_by_region to be used in other modules""",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "author": "ForgeFlow S.L.,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-fiscal-rule",
    "depends": ["account"],
    "post_load": "post_load_hook",
}
