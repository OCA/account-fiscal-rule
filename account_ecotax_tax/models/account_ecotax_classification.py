# © 2014-2023 Akretion (http://www.akretion.com)
#   @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountEcotaxClassification(models.Model):
    _inherit = "account.ecotax.classification"

    sale_ecotax_ids = fields.Many2many(
        "account.tax",
        "ecotax_classif_taxes_rel",
        "ecotax_classif_id",
        "tax_id",
        string="Sale EcoTax",
        domain=[("is_ecotax", "=", True), ("type_tax_use", "=", "sale")],
    )
    purchase_ecotax_ids = fields.Many2many(
        "account.tax",
        "ecotax_classif_purchase_taxes_rel",
        "ecotax_classif_id",
        "tax_id",
        string="Purchase EcoTax",
        domain=[("is_ecotax", "=", True), ("type_tax_use", "=", "purchase")],
    )
