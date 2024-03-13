# Copyright 2022 Akretion France (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ProductCategory(models.Model):
    _name = "product.category"
    _inherit = ["product.category", "product.rule.mixin"]

    def get_matching_product_fiscal_rule(self, fiscal_pos):
        self.ensure_one()
        return self.fiscal_position_product_rule_ids.filtered(
            lambda r: r.fiscal_position_id == fiscal_pos
        ) or (
            self.parent_id
            and self.parent_id.get_matching_product_fiscal_rule(fiscal_pos)
        )


class ProductTemplate(models.Model):
    _name = "product.template"
    _inherit = ["product.template", "product.rule.mixin"]

    def get_matching_product_fiscal_rule(self, fiscal_pos):
        self.ensure_one()
        return self.fiscal_position_product_rule_ids.filtered(
            lambda r: r.fiscal_position_id == fiscal_pos
        ) or self.categ_id.get_matching_product_fiscal_rule(fiscal_pos)

    def get_product_accounts(self, fiscal_pos=None):
        if fiscal_pos:
            rule = self.get_matching_product_fiscal_rule(fiscal_pos)
            if rule:
                return {
                    "income": rule.account_income_id,
                    "expense": rule.account_expense_id,
                }
        return super().get_product_accounts(fiscal_pos=fiscal_pos)
