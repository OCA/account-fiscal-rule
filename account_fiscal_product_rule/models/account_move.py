# Copyright 2022 Akretion France (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.onchange("product_id")
    def _onchange_product_id(self):
        super()._onchange_product_id()
        for line in self:
            if not line.product_id or line.display_type in (
                "line_section",
                "line_note",
            ):
                continue

            taxes = line._get_computed_taxes()
            if (
                taxes
                and line.move_id.fiscal_position_id.fiscal_position_product_rule_ids
            ):
                taxes = line.move_id.fiscal_position_id.map_tax(
                    taxes, line.product_id, line.partner_id
                )
                line.tax_ids = taxes
                line.product_uom_id = line._get_computed_uom()
                line.price_unit = line.with_context(
                    product_id=line.product_id.id
                )._get_computed_price_unit()

    @api.onchange("product_uom_id")
    def _onchange_uom_id(self):
        super()._onchange_uom_id()
        for line in self:
            if line.display_type in ("line_section", "line_note"):
                continue

            taxes = line._get_computed_taxes()
            if (
                taxes
                and line.move_id.fiscal_position_id.fiscal_position_product_rule_ids
            ):
                taxes = line.move_id.fiscal_position_id.map_tax(
                    taxes, line.product_id, line.partner_id
                )
                line.tax_ids = taxes
                line.price_unit = line.with_context(
                    product_id=line.product_id.id
                )._get_computed_price_unit()
