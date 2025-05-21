import ast

from odoo import models
from odoo.tools.float_utils import float_round


class AccountTax(models.Model):
    _inherit = "account.tax"

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
        for_avatax_object = self.env.context.get("for_avatax_object")
        if for_avatax_object:
            # Find the Avatax amount in the document Lines
            # Looks up the line for the current product, price_unit, and quantity
            # Note that the price_unit used must consider discount
            company = self.env.company if not self else self[0].company_id
            currency = currency or company.currency_id
            precision = currency.rounding
            round_tax = company.tax_calculation_rounding_method != "round_globally"
            if "round" in self.env.context:
                round_tax = bool(self.env.context["round"])
            if not round_tax:
                precision *= 1e-5
            base = price_unit * quantity
            if self._context.get("round_base", True):
                base = currency.round(base)
            sign = 1
            if currency.is_zero(base):
                sign = -1 if fixed_multiplicator < 0 else 1
            elif base < 0:
                sign = -1
            avatax_ids = self.search([("is_avatax", "=", True)]).ids
            avatax_config = for_avatax_object.company_id.get_avatax_config_company()
            if not avatax_config:
                return res
            for tax_data in [x for x in res["taxes"] if x["id"] in avatax_ids]:
                line = for_avatax_object.order_line.filtered(
                    lambda x: tax_data["id"] in x.tax_id.ids
                    and x.product_id == product
                    and x.product_uom_qty == quantity
                    and x.price_unit == price_unit
                )[:1]
                if not avatax_config.breakdown_all_taxes and line.tax_amt:
                    tax_data["amount"] = line.tax_amt
                else:
                    response = ast.literal_eval(
                        for_avatax_object.avatax_response_log or "{}"
                    )
                    response_lines = {
                        int(line["lineNumber"]): line
                        for line in response.get("lines", [])
                    }
                    doc_type = for_avatax_object._get_avatax_doc_type()
                    line_result = response_lines.get(line.id)
                    if not line_result:
                        continue
                    for detail in line_result.get("details", []):
                        fixed = detail.get("unitOfBasis") == "FlatAmount"
                        rate = detail["rate"] if fixed else detail["rate"] * 100
                        tax_group_name = detail["taxName"].removesuffix(" TAX")
                        tax_name_display = "%s %s" % (
                            tax_group_name,
                            ("$ %.4g" if fixed else "%.4g%%") % round(rate, 4),
                        )
                        tax = self.get_avalara_tax(
                            rate, doc_type, tax_name=tax_name_display
                        )
                        if tax_data["id"] == tax.id:  # Avatax Amount
                            tax_data["amount"] = (
                                float_round(detail["tax"], precision_rounding=precision)
                                * sign
                            )
                            tax_data["base"] = float_round(
                                sign * detail["taxableAmount"],
                                precision_rounding=precision,
                            )
                res["total_included"] = res["total_excluded"] + line.tax_amt
        return res
