# Copyright (C) 2019-Today GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.onchange("fiscal_position_id")
    def _onchange_fiscal_position_id(self):
        """
        Trigger the recompute of the taxes if the fiscal position is
        changed on the invoice.
        """
        for line in self.mapped("invoice_line_ids"):
            line._set_taxes()
