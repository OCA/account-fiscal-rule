# © 2014-2023 Akretion (http://www.akretion.com)
#   @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Ecotax Management",
    "summary": "Ecotax Management:  in French context is a 'cost' "
    "added to the sale price of electrical or electronic appliances or furnishing items",
    "version": "16.0.1.0.0",
    "author": "Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-fiscal-rule",
    "category": "Localization/Account Taxes",
    "license": "AGPL-3",
    "maintainers": ["mourad-ehm"],
    "depends": [
        "account",
        "account_tax_python",
    ],
    "data": [
        "data/decimal_precision.xml",
        "security/ir_rule.xml",
        "security/ir.model.access.csv",
        "views/account_ecotax_category_view.xml",
        "views/ecotax_sector_view.xml",
        "views/ecotax_collector_view.xml",
        "views/account_ecotax_classification_view.xml",
        "views/account_move_view.xml",
        "views/product_template_view.xml",
        "views/product_view.xml",
        "views/account_tax_view.xml",
    ],
    "installable": True,
}
