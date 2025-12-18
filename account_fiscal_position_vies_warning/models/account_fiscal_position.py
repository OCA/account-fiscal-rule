# Copyright 2025 Moduon Team S.L. <info@moduon.team>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountFiscalPosition(models.Model):
    _inherit = "account.fiscal.position"

    is_show_vies_warning = fields.Boolean(
        "Show Vies Warning",
        help="If this field is checked and "
        "the partner does not pass VIES "
        "validation, the partner record "
        "cannot be saved, and any invoices "
        "for this partner cannot be "
        "confirmed if this fiscal position "
        "is selected in the Partner form or "
        "on an Invoice",
    )

    is_visible_show_vies_warning = fields.Boolean(
        "Visible Show Vies Warning", compute="_compute_visible_vies_warning"
    )

    def raise_vies_warning(self, partner_name):
        raise ValidationError(
            _(
                "You can't set the Fiscal Position to %(fiscal_pos)s, "
                "%(partner_name)s doesn't pass VIES VAT number validation!"
            )
            % {
                "fiscal_pos": self.name,
                "partner_name": partner_name,
            }
        )

    @api.depends("auto_apply", "vat_required", "company_id.vat_check_vies")
    def _compute_visible_vies_warning(self):
        for record in self:
            record.is_visible_show_vies_warning = bool(
                record.auto_apply
                and record.vat_required
                and record.company_id.vat_check_vies
            )
