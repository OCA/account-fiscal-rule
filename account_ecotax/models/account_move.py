# © 2014-2023 Akretion (http://www.akretion.com)
#   @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.tools.misc import formatLang


class AccountMove(models.Model):
    _inherit = "account.move"

    amount_ecotax = fields.Float(
        digits="Ecotax",
        string="Included Ecotax",
        store=True,
        compute="_compute_ecotax",
    )

    @api.depends("invoice_line_ids.subtotal_ecotax")
    def _compute_ecotax(self):
        for move in self:
            move.amount_ecotax = sum(move.line_ids.mapped("subtotal_ecotax"))

    def _get_formatted_ecotax_amount(self):
        self.ensure_one()
        return formatLang(self.env, self.amount_ecotax, currency_obj=self.currency_id)
