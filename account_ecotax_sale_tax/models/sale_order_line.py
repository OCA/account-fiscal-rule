# © 2015 -2023 Akretion (http://www.akretion.com)
#   @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    # The line totals depend on the ecotax lines, which is a one2many and can
    # never be precomputed: the ORM would downgrade these fields at runtime
    # with a warning (see fields.Field.resolve_depends). Declared explicitly
    # so that the intent is in the code and the warning is not raised.
    price_subtotal = fields.Monetary(precompute=False)
    price_tax = fields.Float(precompute=False)
    price_total = fields.Monetary(precompute=False)
    price_reduce_taxexcl = fields.Monetary(precompute=False)
    price_reduce_taxinc = fields.Monetary(precompute=False)

    # the ecotax tax amount is injected from the line ecotax lines by the
    # tax engine: recompute the line amounts when they change (e.g. forced
    # amount edited after the line creation)
    @api.depends("ecotax_line_ids.amount_total")
    def _compute_amount(self):
        return super()._compute_amount()

    # the ecotax tax is added according to the delivery country of the
    # document, which is not part of the standard dependencies
    @api.depends(
        "product_id",
        "company_id",
        "order_id.partner_id",
        "order_id.partner_shipping_id",
    )
    def _compute_tax_id(self):
        res = super()._compute_tax_id()
        for line in self:
            line.tax_id |= line._get_computed_ecotaxes()
        return res

    def _get_computed_ecotaxes(self):
        """Return the ecotax taxes of the eligible ecotax classifications."""
        self.ensure_one()
        eligible_classifications = self._get_ecotax_eligible_classification()
        classifications = eligible_classifications.classification_id
        ecotax_ids = classifications.sale_ecotax_ids.filtered(
            lambda tax: tax.company_id == self.order_id.company_id
        )
        if ecotax_ids and self.order_id.fiscal_position_id:
            ecotax_ids = self.order_id.fiscal_position_id.map_tax(ecotax_ids)
        return ecotax_ids

    def _prepare_invoice_line(self, **optional_values):
        res = super()._prepare_invoice_line(**optional_values)
        # remove ecoltax_line_ids value if empty in vals so it is recomputed during
        # invoice line creation. Example of use case : Ship a product not present in
        # SO. So line is created with qty 0 (so with no ecotax) but in invoice it is
        # added with a qty, with ecotax, so we want to recompute the ecotax report lines
        if "ecotax_line_ids" in res and not res["ecotax_line_ids"]:
            res.pop("ecotax_line_ids")
        return res
