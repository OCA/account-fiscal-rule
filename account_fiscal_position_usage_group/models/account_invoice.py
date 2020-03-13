# Copyright (C) 2019-Today GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.constrains("fiscal_position_id")
    def _check_access_fiscal_position(self):
        for invoice in self:
            groups = invoice.mapped(
                "fiscal_position_id.usage_group_ids")
            if groups and not any(
                    [x in self.env.user.groups_id.ids for x in groups.ids]):
                raise ValidationError(_(
                    "You can not use the fiscal position '%s' because"
                    " you're not a member of one of the following groups:\n\n"
                    " - %s"
                    "\n\n"
                    "Please contact your accountant or the administrator.") % (
                        invoice.fiscal_position_id.name,
                        "\n- ".join(groups.mapped('name'))))
