# Copyright (C) 2021 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class AccountFiscalPositionTemplate(models.Model):
    _inherit = "account.fiscal.position.template"

    tag_ids = fields.Many2many(
        comodel_name="account.fiscal.position.tag",
        relation="account_fiscal_position_template_tag_rel",
        string="Tags",
    )
