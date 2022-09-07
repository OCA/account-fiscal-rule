# Copyright 2022 Akretion France (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountFiscalPositionProductRule(models.Model):
    _name = "account.fiscal.position.product.rule"
    _description = "Account Fiscal Position Rule in Product"

    name = fields.Char(required=True)
    fiscal_position_id = fields.Many2one("account.fiscal.position", required=True)
    product_tmpl_ids = fields.Many2many("product.template")
    product_category_ids = fields.Many2many("product.category")
    account_income_id = fields.Many2one("account.account")
    account_expense_id = fields.Many2one("account.account")
    seller_tax_ids = fields.Many2many("account.tax", "account_tax_seller")
    supplier_tax_ids = fields.Many2many(
        "account.tax",
        "account_tax_supplier",
    )
    company_id = fields.Many2one(related="fiscal_position_id.company_id")


class AccountFiscalPosition(models.Model):
    _inherit = "account.fiscal.position"

    fiscal_position_product_rule_ids = fields.One2many(
        "account.fiscal.position.product.rule",
        "fiscal_position_id",
        string="Product Fiscal Rules",
    )

    def map_tax(self, taxes, product=None, partner=None):
        if product or self.env.context.get("product_id", False):
            if not product:
                product = self.env["product.product"].browse(
                    self.env.context.get("product_id", False)
                )
            for fp in self:
                fiscal_product_rules = (
                    product.product_tmpl_id.get_matching_product_fiscal_rule(fp)
                )
                if fiscal_product_rules:
                    res = self.env["account.tax"]
                    if (
                        taxes[0].type_tax_use == "sale"
                        and fiscal_product_rules[0].seller_tax_ids
                    ):
                        res = fiscal_product_rules[0].seller_tax_ids[0]
                    if (
                        taxes[0].type_tax_use == "purchase"
                        and fiscal_product_rules[0].supplier_tax_ids
                    ):
                        res = fiscal_product_rules[0].supplier_tax_ids[0]
                    if res:
                        return res
        return super().map_tax(taxes=taxes, product=product, partner=partner)
