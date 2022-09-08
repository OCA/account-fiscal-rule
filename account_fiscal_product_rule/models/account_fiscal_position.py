# Copyright 2022 Akretion France (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


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


class ProductRuleMixin(models.AbstractModel):
    _name = "product.rule.mixin"
    _description = "Product Rule Mixin"

    fiscal_position_product_rule_ids = fields.Many2many(
        "account.fiscal.position.product.rule", string="Product Fiscal Rules"
    )

    @api.constrains("fiscal_position_product_rule_ids")
    def _check_no_duplicate_fiscal_position(self):
        for record in self:
            fps = []
            # import pdb;pdb.set_trace()
            for rule in record.fiscal_position_product_rule_ids:
                if rule.fiscal_position_id in fps:
                    raise ValidationError(
                        _(
                            "A Fiscal Position Product Rule already exists for this product "
                            "or product category with this fiscal position !"
                        )
                    )
                else:
                    fps.append(rule.fiscal_position_id)


class AccountFiscalPosition(models.Model):
    _inherit = "account.fiscal.position"

    fiscal_position_product_rule_ids = fields.One2many(
        "account.fiscal.position.product.rule",
        "fiscal_position_id",
        string="Product Fiscal Rules",
    )

    def map_tax(self, taxes, product=None, partner=None):
        prod = product or self._context.get("product")
        if prod:
            rule = prod.product_tmpl_id.get_matching_product_fiscal_rule(self)
            if rule and taxes:
                tax_use = taxes[0].type_tax_use
                if tax_use == "sale" and rule.seller_tax_ids:
                    return rule.seller_tax_ids
                elif tax_use == "purchase" and rule.supplier_tax_ids:
                    return rule.supplier_tax_ids
        return super().map_tax(taxes=taxes, product=product, partner=partner)
