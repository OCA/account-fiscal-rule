# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Ecotaxe Accounting",
    "summary": "Automatically isolate ecotaxe amount in a dedicated account",
    "version": "16.0.1.0.0",
    "category": "Fiscale Rules",
    "author": "Akretion,Odoo Community Association (OCA)",
    "excludes": ["account_ecotax_tax"],
    "maintainers": ["florian-dacosta"],
    "website": "https://github.com/OCA/account-fiscal-rule",
    "license": "AGPL-3",
    "depends": ["account_ecotax"],
    "data": [
        "views/account_ecotax_classification.xml",
        "views/res_config_settings.xml",
    ],
    "installable": True,
}
