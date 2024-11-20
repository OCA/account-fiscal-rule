# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    ecotax_account_id = fields.Many2one("account.account")
    ecotax_journal_id = fields.Many2one("account.journal")
