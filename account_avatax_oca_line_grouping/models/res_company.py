# -*- coding: utf-8 -*-

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    avatax_group_lines = fields.Boolean(
        string="Group document lines for Avatax",
        help=(
            "If enabled, all lines of a Sales Order or Invoice will be sent to "
            "Avatax as a single aggregated line for tax computation."
        ),
        default=False,
    )
