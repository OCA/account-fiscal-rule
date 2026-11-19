# © 2014-2023 Akretion (http://www.akretion.com)
#   @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AcountMoveLine(models.Model):
    _inherit = "account.move.line"

    # the ecotax tax amount is injected from the line ecotax lines by the
    # tax engine: recompute the line totals when they change (e.g. forced
    # amount edited after the line creation)
    @api.depends("ecotax_line_ids.amount_total")
    def _compute_totals(self):
        return super()._compute_totals()

    # the ecotax tax is added according to the delivery country of the
    # document, which is not part of the standard dependencies
    @api.depends(
        "product_id",
        "move_id.partner_shipping_id",
    )
    def _compute_tax_ids(self):
        return super()._compute_tax_ids()

    def _get_computed_taxes(self):
        """Add the ecotax taxes of the eligible ecotax classifications."""
        tax_ids = super()._get_computed_taxes()
        if not self.move_id.is_sale_document(include_receipts=True):
            # Purchase documents are not supported.
            return tax_ids
        eligible_classifications = self._get_ecotax_eligible_classification()
        classifications = eligible_classifications.classification_id
        ecotax_ids = classifications.sale_ecotax_ids.filtered(
            lambda tax: tax.company_id == self.move_id.company_id
        )
        if ecotax_ids and self.move_id.fiscal_position_id:
            ecotax_ids = self.move_id.fiscal_position_id.map_tax(ecotax_ids)
        return tax_ids | ecotax_ids
