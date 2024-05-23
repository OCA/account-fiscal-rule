# Copyright 2021 Camptocamp
#   @author Silvio Gregorini <silvio.gregorini@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountEcotaxCategory(models.Model):
    _name = "account.ecotax.category"
    _description = "Account Ecotax Category"

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    description = fields.Char()
    active = fields.Boolean(default=True)
