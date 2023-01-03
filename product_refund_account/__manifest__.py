# Copyright 2022 Trey, Kilobytes de Soluciones - Vicent Cubells
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Product Refund Account",
    "summary": "Adds account to product to manage debit and credit notes",
    "author": "Trey (www.trey.es), Odoo Community Association (OCA)",
    "maintainers": ["cubells"],
    "website": "https://github.com/OCA/account-fiscal-rule",
    "license": "AGPL-3",
    "category": "Accounting & Finance",
    "version": "12.0.1.0.1",
    "depends": [
        "account",
    ],
    "data": [
        "views/product_category_views.xml",
        "views/product_template_views.xml",
    ],
}
