# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    ecotax_account_id = fields.Many2one(
        "account.account",
        string="Ecotaxe Account",
        related="company_id.ecotax_account_id",
        readonly=False,
        help="When a customer invoices with ecotax is validated, if the ecotax "
        "classifications do not have any account configured, the ecotax amount "
        "will be isolated in this account.",
    )
    ecotax_journal_id = fields.Many2one(
        "account.journal",
        string="Ecotaxe Journal",
        related="company_id.ecotax_journal_id",
        readonly=False,
        help="Journal used to create the ecotax isolation accounting entries",
    )
