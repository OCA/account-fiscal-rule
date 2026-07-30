# © 2014-2023 Akretion (http://www.akretion.com)
#   @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AcountMoveLine(models.Model):
    _inherit = "account.move.line"

    # replace compute method because we want to change the invalidation fields
    # (api.depends) and not add some. (we want to remove the ones on ecotax_line_ids)
    # because ecotax_line_ids now depends on the 2 next fields.
    subtotal_ecotax = fields.Float(compute="_compute_ecotax_tax")
    ecotax_amount_unit = fields.Float(
        compute="_compute_ecotax_tax",
    )

    def _get_ecotax_amounts(self):
        """Estimate the ecotax amounts from the product eligible ecotax lines.

        The ecotax lines of the move line are not used here on purpose:
        ``subtotal_ecotax``/``ecotax_amount_unit`` are the pre-creation
        estimate used to decide if ecotax lines should be generated
        (see ``_get_new_vals_list``). The definitive tax amount is computed
        from the move line ecotax lines by the tax engine itself
        (see account.tax._add_tax_details_in_base_line).
        """
        self.ensure_one()
        country = (
            self.move_id.partner_shipping_id.country_id
            or self.move_id.partner_id.country_id
        )
        eligible_lines = self.product_id._get_country_eligible_classification(country)
        if self.display_type == "tax" or not eligible_lines:
            return 0.0, 0.0
        # product ecotax amounts are expressed in the company currency
        company_currency = self.company_id.currency_id
        amount_unit = sum(eligible_lines.mapped("amount"))
        if self.currency_id and self.currency_id != company_currency:
            amount_unit = company_currency._convert(
                amount_unit,
                self.currency_id,
                self.company_id,
                self.move_id.date or fields.Date.context_today(self),
            )
        if self.display_type == "product" and self.move_id.is_invoice(True):
            quantity = self.quantity
        else:
            quantity = 1
        subtotal_ecotax = amount_unit * quantity
        if self.currency_id:
            subtotal_ecotax = self.currency_id.round(subtotal_ecotax)
        return amount_unit, subtotal_ecotax

    @api.depends(
        "currency_id",
        "tax_ids",
        "quantity",
        "product_id",
    )
    def _compute_ecotax_tax(self):
        return self._compute_ecotax()

    # the ecotax tax amount is injected from the line ecotax lines by the
    # tax engine: recompute the line totals when they change (e.g. forced
    # amount edited after the line creation)
    @api.depends("ecotax_line_ids.amount_total")
    def _compute_totals(self):
        return super()._compute_totals()

    def _get_new_vals_list(self):
        if not self.subtotal_ecotax:
            return []
        return super()._get_new_vals_list()

    # ensure lines are re-generated in case ecotax_amount_unit of invoice line change
    # without changing the product
    @api.depends("ecotax_amount_unit", "subtotal_ecotax")
    def _compute_ecotax_line_ids(self):
        return super()._compute_ecotax_line_ids()

    @api.depends(
        "product_id",
        "product_uom_id",
        "move_id.partner_id",
        "move_id.partner_shipping_id",
    )
    def _compute_tax_ids(self):
        return super()._compute_tax_ids()

    def _get_computed_taxes(self):
        tax_ids = super()._get_computed_taxes()
        ecotax_ids = self.env["account.tax"]
        country = (
            self.move_id.partner_shipping_id.country_id
            or self.move_id.partner_id.country_id
        )
        if self.move_id.is_sale_document(include_receipts=True):
            # Out invoice.
            eligible_classifications = (
                self.product_id._get_country_eligible_classification(country)
            )
            sale_ecotaxs = eligible_classifications.classification_id.sale_ecotax_ids
            ecotax_ids = sale_ecotaxs.filtered(
                lambda tax: tax.company_id == self.move_id.company_id
            )

        elif self.move_id.is_purchase_document(include_receipts=True):
            # In invoice.
            eligible_classifications = (
                self.product_id._get_country_eligible_classification(country)
            )
            purchase_ecotaxs = (
                eligible_classifications.classification_id.purchase_ecotax_ids
            )
            ecotax_ids = purchase_ecotaxs.filtered(
                lambda tax: tax.company_id == self.move_id.company_id
            )

        if ecotax_ids and self.move_id.fiscal_position_id:
            ecotax_ids = self.move_id.fiscal_position_id.map_tax(ecotax_ids)
        if ecotax_ids:
            tax_ids |= ecotax_ids

        return tax_ids
