# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountEcotaxClassification(models.Model):
    _inherit = "account.ecotax.classification"

    ecotax_account_id = fields.Many2one(
        "account.account",
        string="Ecotaxe Account",
        help="In case a customer invoice is validated with ecotax of this "
        "classification, the ecotax amount will be transfered from the product "
        "account to this account. If this field is not set, the account "
        "configured on company level will be used",
    )
