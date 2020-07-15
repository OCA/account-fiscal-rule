import logging

from odoo import _, api, fields, models
from odoo.tools.float_utils import float_compare

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
                # If you get a unique constraint error here,
                # check the data for your existing Avatax taxes.
                tax.name = self._get_avalara_tax_name(tax_rate, doc_type)
            return tax
        else:
            return self

    def compute_all(
        self,
        price_unit,
        currency=None,
        quantity=1.0,
        product=None,
        partner=None,
        is_refund=False,
        handle_price_include=True,
    ):
        """
        Adopted as the central point to inject custom tax computations.
        Avatax logic is triggered if the "avatax_invoice" is set in the context.
        To find the Avatax amount, we search an Invoice line with the same
        quantity, price and product.
        """
        res = super().compute_all(
            price_unit,
            currency,
            quantity,
            product,
            partner,
            is_refund,
            handle_price_include,
        )
        avatax_invoice = self.env.context.get("avatax_invoice")
        if avatax_invoice:
            digits = 6
            invoice_line = avatax_invoice.invoice_line_ids.filtered(
                lambda x: float_compare(x.price_unit, -price_unit, digits)
                and float_compare(x.quantity, quantity, digits)
                and x.product_id == product
            )[:1]
            avatax_amount = -invoice_line.avatax_amt_line
            for tax_item in res["taxes"]:
                if tax_item["amount"] != 0:
                    tax_item["amount"] = avatax_amount
            res["total_included"] = res["total_excluded"] + avatax_amount
        return res
