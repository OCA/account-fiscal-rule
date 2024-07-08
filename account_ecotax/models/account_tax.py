# © 2014-2024 Akretion (http://www.akretion.com)
#   @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.tools.misc import formatLang


class AccountTax(models.Model):
    _inherit = "account.tax"

    is_ecotax = fields.Boolean(
        "Ecotax",
        help="Warning : To include Ecotax "
        "in the VAT tax check this :\n"
        '1: check  "included in base amount "\n'
        "2: The Ecotax sequence must be less then "
        "VAT tax (in sale and purchase)",
    )

    @api.onchange("is_ecotax")
    def onchange_is_ecotax(self):
        if self.is_ecotax:
            self.amount_type = "code"
            self.include_base_amount = True
            self.python_compute = """
# price_unit
# product: product.product object or None
# partner: res.partner object or None
# for weight based ecotax
# result = product.weight_based_ecotax or 0.0
result = product.fixed_ecotax or 0.0
            """

    @api.model
    def _prepare_tax_totals(
        self, base_lines, currency, tax_lines=None, is_company_currency_requested=False
    ):
        """Include Ecotax when this method is called upon a single invoice

        NB: `_prepare_tax_totals()` is called when field `_compute_tax_totals` is
        computed, which is used in invoice form view to display taxes and
        totals.
        """
        res = super()._prepare_tax_totals(
            base_lines,
            currency,
            tax_lines=tax_lines,
            is_company_currency_requested=is_company_currency_requested,
        )

        move_id = self.env.context.get("move_id", False)
        if not move_id:
            return res

        move = self.env["account.move"].browse(move_id)
        base_amt = move.amount_total
        ecotax_amt = move.amount_ecotax
        if not ecotax_amt:
            return res

        fmt_ecotax_amt = formatLang(self.env, ecotax_amt, currency_obj=currency)
        fmt_base_amt = formatLang(self.env, base_amt, currency_obj=currency)
        data = list(res["groups_by_subtotal"].get(_("Untaxed Amount")) or [])
        data.append(
            {
                "tax_group_name": _("Included Ecotax"),
                "tax_group_amount": ecotax_amt,
                "formatted_tax_group_amount": fmt_ecotax_amt,
                "tax_group_base_amount": base_amt,
                "formatted_tax_group_base_amount": fmt_base_amt,
                "tax_group_id": False,  # Not an actual tax
                "group_key": "Included Ecotax",
            }
        )
        res["groups_by_subtotal"][_("Untaxed Amount")] = data
        return res
