# Copyright 2023 Ecosoft Co., Ltd. <http://ecosoft.co.th>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    fiscal_position_id = fields.Many2one(
        comodel_name="account.fiscal.position",
        string="Fiscal Position",
        readonly=True,
        states={"draft": [("readonly", False)]},
        check_company=True,
        help="Fiscal positions are used to adapt accounts of account moves.",
    )
