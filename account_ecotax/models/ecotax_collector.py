# Copyright 2021 Camptocamp
#   @author Silvio Gregorini <silvio.gregorini@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class EcotaxCollector(models.Model):
    _name = "ecotax.collector"
    _description = "Ecotax collector"

    name = fields.Char(required=True)
    partner_id = fields.Many2one("res.partner", string="Partner", required=False)
    active = fields.Boolean(default=True)
