# Copyright 2023 ForgeFlow S.L. (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SignOcaTemplate(models.Model):
    _inherit = "sign.oca.template"

    is_exemption = fields.Boolean(copy=False)
    exemption_type = fields.Many2one("res.partner.exemption.type", copy=False)
