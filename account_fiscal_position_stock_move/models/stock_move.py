# Copyright 2023 Ecosoft Co., Ltd. <http://ecosoft.co.th>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    fiscal_position_id = fields.Many2one(
        comodel_name="account.fiscal.position",
        related="picking_id.fiscal_position_id",
    )

    def _account_entry_move(self, qty, description, svl_id, cost):
        """Pass fiscal position when create account.move"""
        self.ensure_one()
        self = self.with_context(default_fiscal_position_id=self.fiscal_position_id.id)
        res = super()._account_entry_move(qty, description, svl_id, cost)
        return res
