# Copyright 2025 Pierre Verkest <pierre@verkest.fr>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    "name": "Account tax product amount",
    "summary": "Manage tax amount per product variant",
    "version": "18.0.1.0.0",
    "category": "Accounting/Accounting",
    "license": "LGPL-3",
    "author": "Pierre Verkest, Odoo Community Association (OCA)",
    "maintainers": ["petrus-v"],
    "depends": ["account", "product"],
    "data": [
        "security/ir.model.access.csv",
        "security/ir_rules.xml",
        "views/account_tax_view.xml",
        "views/account_tax_product_amount_view.xml",
        "views/product_product_view.xml",
    ],
    "website": "https://github.com/OCA/account-fiscal-rule",
}
