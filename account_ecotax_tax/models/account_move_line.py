# © 2014-2023 Akretion (http://www.akretion.com)
#   @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AcountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _get_ecotax_amounts(self):
        self.ensure_one()
        ecotax_ids = self.tax_ids.filtered(lambda tax: tax.is_ecotax)

        if self.display_type == "tax" or not ecotax_ids:
            return 0.0, 0.0
        if self.display_type == "product" and self.move_id.is_invoice(True):
            amount_currency = self.price_unit * (1 - self.discount / 100)
            handle_price_include = True
            quantity = self.quantity
        else:
            amount_currency = self.amount_currency
            handle_price_include = False
            quantity = 1
        compute_all_currency = ecotax_ids.compute_all(
            amount_currency,
            currency=self.currency_id,
            quantity=quantity,
            product=self.product_id,
            partner=self.move_id.partner_id or self.partner_id,
            is_refund=self.is_refund,
            handle_price_include=handle_price_include,
            include_caba_tags=self.move_id.always_tax_exigible,
        )
        subtotal_ecotax = 0.0
        for tax in compute_all_currency["taxes"]:
            subtotal_ecotax += tax["amount"]

        amount_unit = subtotal_ecotax / quantity if quantity else subtotal_ecotax
        return amount_unit, subtotal_ecotax

    @api.depends(
        "currency_id",
        "tax_ids",
        "quantity",
        "product_id",
    )
    def _compute_ecotax(self):
        return super()._compute_ecotax()

    def _get_computed_taxes(self):
        tax_ids = super()._get_computed_taxes()
        ecotax_ids = self.env["account.tax"]
        if self.move_id.is_sale_document(include_receipts=True):
            # Out invoice.
            sale_ecotaxs = self.product_id.all_ecotax_line_product_ids.mapped(
                "classification_id"
            ).mapped("sale_ecotax_ids")
            ecotax_ids = sale_ecotaxs.filtered(
                lambda tax: tax.company_id == self.move_id.company_id
            )

        elif self.move_id.is_purchase_document(include_receipts=True):
            # In invoice.
            purchase_ecotaxs = self.product_id.all_ecotax_line_product_ids.mapped(
                "classification_id"
            ).mapped("purchase_ecotax_ids")
            ecotax_ids = purchase_ecotaxs.filtered(
                lambda tax: tax.company_id == self.move_id.company_id
            )

        if ecotax_ids and self.move_id.fiscal_position_id:
            ecotax_ids = self.move_id.fiscal_position_id.map_tax(ecotax_ids)
        if ecotax_ids:
            tax_ids |= ecotax_ids

        return tax_ids
