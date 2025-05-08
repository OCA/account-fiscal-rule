import ast
from math import copysign

from odoo import _, api, exceptions, fields, models
from odoo.tools.float_utils import float_compare, float_round


class AccountTax(models.Model):
    """Inherit to implement the tax using avatax API"""

    _inherit = "account.tax"

    is_avatax = fields.Boolean()

    @api.model
    def _get_avalara_tax_domain(self, tax_rate, doc_type, tax_name=None):
        domain = [
            ("amount", "=", tax_rate),
            ("is_avatax", "=", True),
            (
                "company_id",
                "=",
                self.env.company.id,
            ),
        ]
        if tax_name:
            domain.append(("name", "=", tax_name))
        return domain

    @api.model
    def _get_avalara_tax_name(self, tax_rate, doc_type=None):
        return _("{}%*").format(str(tax_rate))

    @api.model
    def get_avalara_tax(self, tax_rate, doc_type, tax_name=None):
        domain = self._get_avalara_tax_domain(tax_rate, doc_type, tax_name)
        tax = self.with_context(active_test=False).search(domain, limit=1)
        if tax and not tax.active:
            tax.active = True
        if not tax:
            domain = self._get_avalara_tax_domain(0, doc_type, "")
            tax_template = self.search(domain, limit=1)
            if not tax_template:
                raise exceptions.UserError(
                    _("Please configure Avatax Tax for Company %s:")
                    % self.env.company.name
                )
            # If you get a unique constraint error here,
            # check the data for your existing Avatax taxes.
            vals = {
                "amount": tax_rate,
                "name": tax_name
                if tax_name
                else self._get_avalara_tax_name(tax_rate, doc_type),
            }
            tax = tax_template.sudo().copy(default=vals)
            # Odoo core does not use the name set in default dict
            tax.name = vals.get("name")
        return tax

    # flake8: noqa: C901
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
        fixed_multiplicator=1,
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
            include_caba_tags=include_caba_tags,
            fixed_multiplicator=fixed_multiplicator,
        )
        avatax_invoice = self.env.context.get("avatax_invoice")
        current_aml = self.env["account.move.line"]
        if "current_aml" in self.env.context:
            current_aml = self.env["account.move.line"].browse(
                self.env.context.get("current_aml")
            )
            if not (
                current_aml.display_type == "product"
                and current_aml.account_type != "asset_receivable"
            ):
                avatax_invoice = False
        if not avatax_invoice and current_aml:
            avatax_invoice = current_aml.move_id
        if avatax_invoice:
            # Find the Avatax amount in the invoice Lines
            # Looks up the line for the current product, price_unit, and quantity
            # Note that the price_unit used must consider discount
            total_excluded = res["total_excluded"]
            digits = 6
            avatax_amount = None
            if current_aml:
                avatax_amount = copysign(current_aml.avatax_amt_line, total_excluded)
            else:
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
                        avatax_amount = copysign(line.avatax_amt_line, total_excluded)
                        current_aml = line
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
            response = ast.literal_eval(avatax_invoice.avatax_response_log or "{}")
            response_lines = {
                int(l["lineNumber"]): l for l in response.get("lines", [])
            }
            doc_type = avatax_invoice._get_avatax_doc_type()
            avatax_ids = self.search([("is_avatax", "=", True)]).ids
            line = current_aml
            line_result = response_lines.get(line.id)
            if not line_result:
                return res
            relevant_tax_ids = [
                x
                for x in res["taxes"]
                if x["id"] in line.tax_ids.ids and x["id"] in avatax_ids
            ]
            if not relevant_tax_ids:
                return res
            if not self:
                company = self.env.company
            else:
                company = self[0].company_id
            if not currency:
                currency = company.currency_id
            prec = currency.rounding
            round_tax = (
                False
                if company.tax_calculation_rounding_method == "round_globally"
                else True
            )
            if "round" in self.env.context:
                round_tax = bool(self.env.context["round"])

            if not round_tax:
                prec *= 1e-5
            base = price_unit * quantity
            if self._context.get("round_base", True):
                base = currency.round(base)
            sign = 1
            if currency.is_zero(base):
                sign = -1 if fixed_multiplicator < 0 else 1
            elif base < 0:
                sign = -1
            for detail in line_result.get("details", []):
                fixed = detail.get("unitOfBasis") == "FlatAmount"
                rate = detail["rate"] if fixed else detail["rate"] * 100
                tax_group_name = detail.get("taxName", "").removesuffix(" TAX")
                tax_name_display = "%s %s" % (
                    tax_group_name,
                    ("$ %.4g" if fixed else "%.4g%%") % round(rate, 4),
                )
                tax = self.get_avalara_tax(rate, doc_type, tax_name=tax_name_display)
                for tax_item in relevant_tax_ids:
                    if tax_item["id"] == tax.id:
                        tax_item["amount"] = (
                            float_round(detail["tax"], precision_rounding=prec) * sign
                        )
                        tax_item["base"] = float_round(
                            sign * detail["taxableAmount"], precision_rounding=prec
                        )
            res["total_included"] = total_excluded + sum(
                t["amount"] for t in res["taxes"]
            )
        return res
