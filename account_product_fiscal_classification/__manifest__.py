# Copyright (C) 2014-Today GRAP (http://www.grap.coop)
# Copyright (C) 2016-Today La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Account Product - Fiscal Classification",
    "summary": "Simplify taxes management for products",
    "version": "14.0.1.0.0",
    "category": "Accounting",
    "author": "Akretion,GRAP,La Louve,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-fiscal-rule",
    "license": "AGPL-3",
    "depends": ["account", "account_menu"],
    "data": [
        "security/ir_rule.xml",
        "security/ir.model.access.csv",
        "views/view_product_template.xml",
        "wizard/view_wizard_change_fiscal_classification.xml",
        "views/view_product_category.xml",
        "views/view_account_product_fiscal_classification.xml",
        "views/view_account_product_fiscal_classification_template.xml",
    ],
    "demo": [
        "demo/res_company.xml",
        "demo/account_tax.xml",
        "demo/account_product_fiscal_classification.xml",
        "demo/product_template.xml",
        "demo/product_category.xml",
        "demo/res_groups.xml",
    ],
    "post_init_hook": "create_fiscal_classification_from_product_template",
    "installable": True,
}
