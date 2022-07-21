# Copyright 2022 Akretion France (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    fiscal_position_product_rule_ids = fields.Many2many(
        "account.fiscal.position.product.rule", string="Fiscal Rule"
    )


class ProductTemplate(models.Model):
    _inherit = "product.template"

    fiscal_position_product_rule_ids = fields.Many2many(
        "account.fiscal.position.product.rule", string="Fiscal Rule"
    )

    def get_product_accounts(self, fiscal_pos=None):
        for product in self:
            if fiscal_pos:
                fiscal_product_rules = (
                    fiscal_pos.fiscal_position_product_rule_ids.filtered(
                        lambda r: product in r.product_tmpl_ids
                        or product.categ_id in r.product_category_ids
                    )
                )
                if fiscal_product_rules:
                    accounts = {}
                    accounts["income"] = fiscal_product_rules[0].account_income_id
                    accounts["expense"] = fiscal_product_rules[0].account_expense_id
                    return accounts
        return super().get_product_accounts(fiscal_pos=fiscal_pos)
