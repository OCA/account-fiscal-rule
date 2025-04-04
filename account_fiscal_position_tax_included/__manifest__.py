# Copyright (C) 2015-Today GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Account Fiscal Position - Tax Excluded to Included",
    "summary": "Allow to map from tax excluded to tax included",
    "version": "12.0.1.1.3",
    "category": "Accounting",
    "author": "GRAP",
    "maintainers": ["legalsylvain"],
    "development_status": "Alpha",
    "website": "https://github.com/grap/grap-odoo-incubator",
    "license": "AGPL-3",
    "depends": ["account"],
    "demo": [
        "demo/account_tax.xml",
        "demo/account_fiscal_position.xml",
        "demo/product_product.xml",
    ],
    "installable": True,
}
