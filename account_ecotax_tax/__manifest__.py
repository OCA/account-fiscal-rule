# © 2014-2023 Akretion (http://www.akretion.com)
#   @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Ecotax Management (with Odoo tax)",
    "summary": "Use Odoo tax mechanism to compute the ecotaxes ",
    "version": "16.0.1.0.0",
    "author": "Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-fiscal-rule",
    "category": "Localization/Account Taxes",
    "license": "AGPL-3",
    "maintainers": ["mourad-ehm", "florian-dacosta"],
    "depends": [
        "account_ecotax",
        "account_tax_python",
    ],
    "data": [
        "views/account_ecotax_classification_view.xml",
        "views/account_tax_view.xml",
        "views/account_move_view.xml",
        "report/invoice.xml",
    ],
    "installable": True,
}
