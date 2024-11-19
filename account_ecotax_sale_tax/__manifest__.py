# © 2014-2023 Akretion (http://www.akretion.com)
#   @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "sale Ecotax Management (as a tax)",
    "summary": "Sale Ecotaxe managed as a tax",
    "version": "16.0.2.0.0",
    "author": "Akretion,Odoo Community Association (OCA)",
    "maintainers": ["mourad-ehm", "florian-dacosta"],
    "website": "https://github.com/OCA/account-fiscal-rule",
    "category": "Localization/Account Taxes",
    "license": "AGPL-3",
    "depends": ["account_ecotax_sale", "account_ecotax_tax"],
    "data": ["views/sale_view.xml"],
    "installable": True,
    "auto_install": True,
}
