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

    def _get_ecotax_taxes(self):
        """Return the ecotax taxes of these classifications.

        No ``ensure_one``: the method is also called on the ecotax lines of
        a document being edited, which may have no classification yet (the
        web client materializes placeholder lines during an onchange).
        """
        return self.sale_ecotax_ids
