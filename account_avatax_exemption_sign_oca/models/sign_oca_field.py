# Copyright 2023 ForgeFlow S.L. (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SignOcaField(models.Model):
    _inherit = "sign.oca.field"

    is_exemption_number = fields.Boolean()
