# Copyright (C) 2019-Today GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'

    usage_group_ids = fields.Many2many(
        comodel_name='res.groups', string="Usage Groups", help="If defined"
        ", the user should be member to one of there groups, to use this"
        " fiscal position when creating or updating a supplier, or an invoice")
