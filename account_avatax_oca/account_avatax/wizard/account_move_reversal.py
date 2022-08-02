from odoo import fields, models


class AccountMoveReversal(models.TransientModel):
    """
    Account move reversal wizard, it cancel an account move by reversing it.
    """

    _inherit = "account.move.reversal"

    avatax_amt_line_override = fields.Boolean(
        string="Use Odoo Tax",
        default=False,
        help="The Odoo tax will be uploaded to Avatax",
    )

    def _prepare_default_reversal(self, move):
        res = super()._prepare_default_reversal(move)
        res.update({"avatax_amt_line_override": self.avatax_amt_line_override})
        return res
