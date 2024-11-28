# © 2014-2024 Akretion (http://www.akretion.com)
#   @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Ecotax Reporting",
    "summary": "Ecotax Reporting add fields and view to anlysis ecotaxe ",
    "version": "16.0.1.0.0",
    "author": "Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-fiscal-rule",
    "category": "Localization/Account Taxes",
    "license": "AGPL-3",
    "maintainers": ["mourad-ehm", "florian-dacosta"],
    "depends": [
        "account_ecotax",
    ],
    "data": [
        "views/account_move_line_ecotax_view.xml",
    ],
    "installable": True,
}
