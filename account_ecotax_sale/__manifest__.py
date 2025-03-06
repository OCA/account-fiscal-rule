# © 2014-2023 Akretion (http://www.akretion.com)
#   @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "sale Ecotax Management",
    "summary": "Sale Ecotaxe",
    "version": "17.0.1.0.0",
    "maintainers": ["mourad-ehm", "florian-dacosta"],
    "author": "Akretion,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-fiscal-rule",
    "category": "Localization/Account Taxes",
    "license": "AGPL-3",
    "depends": ["account_ecotax", "sale"],
    "data": [
        "views/sale_view.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
}
