from math import copysign

from odoo import _, api, exceptions, fields, models
from odoo.tools.float_utils import float_compare


class AccountTax(models.Model):
    """Inherit to implement the tax using avatax API"""

    _inherit = "account.tax"

    is_avatax = fields.Boolean()

    @api.model
    def _get_avalara_tax_domain(self, tax_rate, doc_type):
        return [
            ("amount", "=", tax_rate),
            ("is_avatax", "=", True),
            (
                "company_id",
                "=",
                self.env.company.id,
            ),
        ]

    @api.model
    def _get_avalara_tax_name(self, tax_rate, doc_type=None):
        return _("{}%*").format(str(tax_rate))

    @api.model
    def get_avalara_tax(self, tax_rate, doc_type):
        domain = self._get_avalara_tax_domain(tax_rate, doc_type)
        tax = self.with_context(active_test=False).search(domain, limit=1)
        if tax and not tax.active:
            tax.active = True
        if not tax:
            domain = self._get_avalara_tax_domain(0, doc_type)
            tax_template = self.search(domain, limit=1)
            if not tax_template:
                raise exceptions.UserError(
                    _("Please configure Avatax Tax for Company %s:")
                    % self.env.user.company_id.name
                )
            # If you get a unique constraint error here,
            # check the data for your existing Avatax taxes.
            vals = {
                "amount": tax_rate,
                "name": self._get_avalara_tax_name(tax_rate, doc_type),
            }
            tax = tax_template.sudo().copy(default=vals)
            # Odoo core does not use the name set in default dict
            tax.name = vals.get("name")
        return tax

    def compute_all(
        self,
        price_unit,
        currency=None,
        quantity=1.0,
        product=None,
        partner=None,
        is_refund=False,
        handle_price_include=True,
        include_caba_tags=False,
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
            include_caba_tags=False,
        )
        avatax_invoice = self.env.context.get("avatax_invoice")
        if avatax_invoice:
            # Find the Avatax amount in the invoice Lines
            # Looks up the line for the current product, price_unit, and quantity
            # Note that the price_unit used must consider discount
            base = res["total_excluded"]
            digits = 6
            avatax_amount = None
            for line in avatax_invoice.invoice_line_ids:
                price_unit = line.currency_id._convert(
                    price_unit,
                    avatax_invoice.company_id.currency_id,
                    avatax_invoice.company_id,
                    avatax_invoice.date,
                )
                if (
                    line.product_id == product
                    and float_compare(line.quantity, quantity, digits) == 0
                ):
                    line_price = line._get_avatax_amount(qty=1)
                    if float_compare(line_price, -price_unit, digits) == 0:
                        avatax_amount = copysign(line.avatax_amt_line, base)
                        break
            if avatax_amount is None:
                avatax_amount = 0.0
                raise exceptions.UserError(
                    _(
                        "Incorrect retrieval of Avatax amount for Invoice %(avatax_invoice)s:"
                        " product %(product.display_name)s, price_unit %(-price_unit)f"
                        " , quantity %(quantity)f"
                    )
                )
            for tax_item in res["taxes"]:
                if tax_item["amount"] != 0:
                    tax_item["amount"] = avatax_amount
            res["total_included"] = base + avatax_amount
        return res
