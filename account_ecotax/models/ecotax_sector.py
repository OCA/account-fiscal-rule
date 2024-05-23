# Copyright 2021 Camptocamp
#   @author Silvio Gregorini <silvio.gregorini@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class EcotaxSector(models.Model):
    _name = "ecotax.sector"
    _description = "Ecotax Sector"

    name = fields.Char(required=True)
    description = fields.Char()
    active = fields.Boolean(default=True)
