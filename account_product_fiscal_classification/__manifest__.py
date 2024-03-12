# Copyright (C) 2014-Today GRAP (http://www.grap.coop)
# Copyright (C) 2016-Today La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Account Product - Fiscal Classification",
    "summary": "Simplify taxes management for products",
    "version": "16.0.1.0.2",
    "category": "Accounting",
    "author": "Akretion,GRAP,La Louve,Odoo Community Association (OCA)",
    "maintainers": ["legalsylvain"],
    "website": "https://github.com/OCA/account-fiscal-rule",
    "license": "AGPL-3",
    "depends": ["account", "account_usability"],
    "data": [
        "security/ir_rule.xml",
        "security/ir.model.access.csv",
        "views/view_product_template.xml",
        "wizard/view_wizard_change_fiscal_classification.xml",
        "views/view_account_product_fiscal_classification.xml",
        "views/view_account_product_fiscal_rule.xml",
        "views/view_account_product_fiscal_classification_template.xml",
    ],
    "demo": [
        "demo/res_company.xml",
        "demo/res_users.xml",
        "demo/account_tax.xml",
        "demo/account_product_fiscal_classification.xml",
        "demo/product_template.xml",
        "demo/product_category.xml",
        "demo/account_chart_template.xml",
        "demo/account_tax_template.xml",
        "demo/account_product_fiscal_rule.xml",
        "demo/account_product_fiscal_classification_template.xml",
    ],
    "post_init_hook": "create_fiscal_classification_from_product_template",
    "installable": True,
}
