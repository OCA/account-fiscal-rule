# © 2014-2023 Akretion (http://www.akretion.com)
#   @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command, api, fields, models


class AcountMoveLine(models.Model):
    _inherit = "account.move.line"

    ecotax_line_ids = fields.One2many(
        "account.move.line.ecotax",
        "account_move_line_id",
        string="Ecotax lines",
        copy=True,
    )
    subtotal_ecotax = fields.Float(
        string="Ecotax", digits="Ecotax", store=True, compute="_compute_ecotax"
    )
    ecotax_amount_unit = fields.Float(
        digits="Ecotax",
        string="Ecotax Unit",
        store=True,
        compute="_compute_ecotax",
    )

    @api.depends(
        "currency_id",
        "tax_ids",
        "quantity",
        "product_id",
    )
    def _compute_ecotax(self):
        for line in self:
            ecotax_ids = line.tax_ids.filtered(lambda tax: tax.is_ecotax)

            if line.display_type == "tax" or not ecotax_ids:
                continue
            if line.display_type == "product" and line.move_id.is_invoice(True):
                amount_currency = line.price_unit * (1 - line.discount / 100)
                handle_price_include = True
                quantity = line.quantity
            else:
                amount_currency = line.amount_currency
                handle_price_include = False
                quantity = 1
            compute_all_currency = ecotax_ids.compute_all(
                amount_currency,
                currency=line.currency_id,
                quantity=quantity,
                product=line.product_id,
                partner=line.move_id.partner_id or line.partner_id,
                is_refund=line.is_refund,
                handle_price_include=handle_price_include,
                include_caba_tags=line.move_id.always_tax_exigible,
            )
            subtotal_ecotax = 0.0
            for tax in compute_all_currency["taxes"]:
                subtotal_ecotax += tax["amount"]

            unit = subtotal_ecotax / quantity if quantity else subtotal_ecotax
            line.ecotax_amount_unit = unit
            line.subtotal_ecotax = subtotal_ecotax

    @api.onchange("product_id")
    def _onchange_product_ecotax_line(self):
        """Unlink and recreate ecotax_lines when modifying the product_id."""
        self.ecotax_line_ids.unlink()  # Remove all ecotax classification
        if self.product_id:
            self.ecotax_line_ids = [
                Command.create(
                    {
                        "classification_id": ecotaxline_prod.classification_id.id,
                        "force_amount_unit": ecotaxline_prod.force_amount,
                    }
                )
                for ecotaxline_prod in self.product_id.all_ecotax_line_product_ids
            ]

    def edit_ecotax_lines(self):
        view = {
            "name": ("Ecotax classification"),
            "view_type": "form",
            "view_mode": "form",
            "res_model": "account.move.line",
            "view_id": self.env.ref("account_ecotax.view_move_line_ecotax_form").id,
            "type": "ir.actions.act_window",
            "target": "new",
            "res_id": self.id,
        }
        return view

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
