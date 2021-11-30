# Copyright (C) 2021 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class AccountFiscalPositionTag(models.Model):
    _name = "account.fiscal.position.tag"
    _description = "Account Fiscal Position Tags"

    name = fields.Char(required=True, readonly=True)

    code = fields.Char(required=True, readonly=True)
