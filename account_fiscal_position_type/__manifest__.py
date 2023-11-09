# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Account Fiscal Position - Type",
    "summary": "Add sale / purchase type on fiscal position",
    "version": "16.0.1.0.3",
    "category": "Accounting",
    "author": "GRAP,Odoo Community Association (OCA)",
    "legalsylvain": ["legalsylvain"],
    "website": "https://github.com/OCA/account-fiscal-rule",
    "license": "AGPL-3",
    "development_status": "Beta",
    "depends": [
        "account",
    ],
    "data": [
        "views/view_account_move.xml",
        "views/view_account_fiscal_position.xml",
        "views/view_account_fiscal_position_template.xml",
    ],
    "demo": [
        "demo/res_groups.xml",
        "demo/account_fiscal_position.xml",
        "demo/account_chart_template.xml",
        "demo/account_fiscal_position_template.xml",
    ],
}
