# © 2014-2024 Akretion (http://www.akretion.com)
#   @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


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
            self.formula = """
quantity and product.fixed_ecotax * quantity or 0.0
            """

    def _eval_taxes_computation_prepare_product_fields(self):
        # In Odoo 18, product is passed as a dictionary in the eval context.
        # We need to specify which fields should be included in this dictionary.
        return super()._eval_taxes_computation_prepare_product_fields() | {
            "fixed_ecotax",
            "weight_based_ecotax",
            "ecotax_amount",
            "weight",
        }
