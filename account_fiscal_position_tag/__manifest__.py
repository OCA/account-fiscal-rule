# Copyright (C) 2021 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Account Fiscal Position Tags",
    "summary": "Add tags field on fiscal position",
    "version": "14.0.1.0.1",
    "category": "Accounting",
    "author": "GRAP,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-fiscal-rule",
    "license": "AGPL-3",
    "maintainers": ["legalsylvain"],
    "depends": [
        "account_menu",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/view_account_fiscal_position.xml",
        "views/view_account_fiscal_position_tag.xml",
        "views/view_account_fiscal_position_template.xml",
        "views/view_account_move.xml",
    ],
    "demo": [
        "demo/res_groups.xml",
        "demo/account_fiscal_position_tag.xml",
    ],
    "images": [
        "static/description/view_account_fiscal_position_form.png",
    ],
}
