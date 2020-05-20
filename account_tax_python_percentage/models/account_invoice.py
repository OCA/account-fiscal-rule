# Copyright 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountInvoice(models.Model):
    _inherit = "account.Invoice"

    def get_taxes_values(self):
        return (
            super()
            .with_context(tax_python_code_doc=self)
            .get_taxes_values()
        )
