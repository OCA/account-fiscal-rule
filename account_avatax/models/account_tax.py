import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class AccountTax(models.Model):
    """Inherit to implement the tax using avatax API"""

    _inherit = "account.tax"

    is_avatax = fields.Boolean("Is Avatax")

    @api.model
    def _get_avalara_tax_domain(self, tax_rate, doc_type):
        return [
            ("amount", "=", tax_rate),
            ("is_avatax", "=", True),
        ]

    @api.model
    def _get_avalara_tax_name(self, tax_rate, doc_type=None):
        return _("{}%*").format(str(tax_rate))

    @api.model
    def get_avalara_tax(self, tax_rate, doc_type):
        """
        Given a tax rate, returns the corresponding Tax record.
        The Tax is created if it doesn't exist yet.
        """
        if tax_rate:
            tax = self.with_context(active_test=False).search(
                self._get_avalara_tax_domain(tax_rate, doc_type), limit=1
            )
            if tax and not tax.active:
                tax.active = True
            if not tax:
                tax_template = self.search(
                    self._get_avalara_tax_domain(0, doc_type), limit=1
                )
                tax = tax_template.sudo().copy(default={"amount": tax_rate})
                tax.name = self._get_avalara_tax_name(tax_rate, doc_type)
            return tax
        else:
            return self
