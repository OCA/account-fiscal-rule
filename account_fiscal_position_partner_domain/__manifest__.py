# Copyright 2021 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Fiscal Position Partner Domain",
    "summary": """
        Adds the ability to define a partner domain in the fiscal position to be used
        in the automatic detection""",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "author": "ForgeFlow S.L.,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-fiscal-rule",
    "depends": ["account_fiscal_position_get_fpos_by_region_hook"],
    "data": ["views/account_fiscal_position_views.xml"],
}
