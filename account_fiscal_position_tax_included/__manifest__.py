# Copyright (C) 2019-Today Sylvain LE GAL (http://www.grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Account Fiscal Position - Tax Excluded to Included",
    "summary": "Allow to map from tax excluded to tax included",
    "version": "16.0.1.0.0",
    "category": "Accounting",
    "author": "GRAP, Odoo Community Association (OCA)",
    "maintainers": ["legalsylvain"],
    "website": "https://github.com/OCA/account-fiscal-rule",
    "license": "AGPL-3",
    "depends": ["account"],
    "demo": [
        "demo/account_tax.xml",
        "demo/account_fiscal_position.xml",
        "demo/product_product.xml",
    ],
    "installable": True,
}
