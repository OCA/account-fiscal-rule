# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class AccountFiscalPosition(models.Model):
    _inherit = "account.fiscal.position"

    country_line_ids = fields.One2many(
        comodel_name="fiscal.position.line",
        inverse_name="fiscal_position_id",
        string="Countries",
    )


class FiscalPositionLine(models.Model):
    _name = "fiscal.position.line"

    fiscal_position_id = fields.Many2one(
        comodel_name="account.fiscal.position",
        string="Fiscal Position",
        required=True,
    )
    country_id = fields.Many2one(
        comodel_name="res.country", string="Country", required=True
    )
