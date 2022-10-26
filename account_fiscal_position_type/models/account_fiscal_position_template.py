# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models

from .account_fiscal_position import AccountFiscalPosition


class AccountFiscalPositionTemplate(models.Model):
    _inherit = "account.fiscal.position.template"

    type_position_use = fields.Selection(
        string="Position Application",
        selection=AccountFiscalPosition._TYPE_POSITION_USE_SELECTION,
        default="all",
    )
