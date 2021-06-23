# Copyright 2021 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountFiscalPosition(models.Model):
    _inherit = "account.fiscal.position"

    def _get_base_domain(self, vat_required, company_id):
        return [
            ("auto_apply", "=", True),
            ("vat_required", "=", vat_required),
            ("company_id", "in", [company_id, False]),
        ]
