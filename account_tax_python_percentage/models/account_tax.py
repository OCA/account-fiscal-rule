# Copyright 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class AccountTax(models.Model):
    _inherit = "account.tax"

    amount_type = fields.Selection(
        selection_add=[("code_perc", "Python Code using Percentage")]
    )
    python_compute = fields.Text(
        help="Compute the tax amount setting the variable 'result'.\n\n"
             ":param percentage: float, the Tax configuration percentage\n"
             ":param base_amount: float, actual amount to apply the tax to\n"
             ":param price_unit: float\n"
             ":param quantity: float\n"
             ":param company: res.company recordset singleton\n"
             ":param product: product.product recordset singleton or None\n"
             ":param partner: res.partner recordset singleton or None")

    def _prepare_compute_amount(
        self, price_unit, quantity=1.0, product=None, partner=None, base_amount=None
    ):
        company = self.env.user.company_id
        res = self.env.context.get("tax_computation_context", {})
        res.update(
            {
                "base_amount": base_amount,
                "price_unit": price_unit,
                "quantity": quantity,
                "product": product,
                "partner": partner,
                "company": company,
                "percentage": self.amount,
            }
        )
        return res

    def _compute_amount(
        self, base_amount, price_unit, quantity=1.0, product=None, partner=None
    ):
        self.ensure_one()
        if self.amount_type == "code_perc":
            if product and product._name == "product.template":
                product = product.product_variant_id
            localdict = self._prepare_compute_amount(
                price_unit, quantity, product, partner, base_amount
            )
            safe_eval(self.python_compute, localdict, mode="exec", nocopy=True)
            return localdict["result"]
        return super()._compute_amount(
            base_amount, price_unit, quantity, product, partner
        )

    @api.multi
    def compute_all(
        self, price_unit, currency=None, quantity=1.0, product=None, partner=None
    ):
        taxes = self.filtered(lambda r: r.amount_type != "code_perc")
        for tax in self.filtered(lambda r: r.amount_type == "code_perc"):
            localdict = tax._prepare_compute_amount(
                price_unit, quantity, product, partner
            )
            safe_eval(tax.python_applicable, localdict, mode="exec", nocopy=True)
            if localdict.get("result", False):
                taxes += tax
        return super().compute_all(
            price_unit, currency, quantity, product, partner
        )


class AccountTaxTemplatePython(models.Model):
    _inherit = "account.tax.template"

    amount_type = fields.Selection(
        selection_add=[("code_perc", "Python Code using Percentage")]
    )
