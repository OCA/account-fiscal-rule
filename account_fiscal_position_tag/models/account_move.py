# Copyright (C) 2021 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    tag_ids = fields.Many2many(
        comodel_name="account.fiscal.position.tag",
        string="Fiscal Position Tags",
        related="fiscal_position_id.tag_ids",
    )
