# Copyright 2022 Akretion France (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountFiscalProductRule(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        # ===== Taxes =====
        cls.tax_sale = cls.company_data["default_tax_sale"].copy(default={"amount": 30})
        # ===== Accounts =====
        cls.account_income = cls.copy_account(
            cls.company_data["default_account_revenue"]
        )
        cls.account_income.code = "123456"
        # ===== Fiscal Position Product Rules =====
        cls.fiscal_product_rule = cls.env[
            "account.fiscal.position.product.rule"
        ].create(
            {
                "name": "Fiscal Product Rule",
                "fiscal_position_id": cls.fiscal_pos_a.id,
                "seller_tax_ids": [(6, 0, cls.tax_sale.ids)],
                "account_income_id": cls.account_income.id,
            }
        )
        cls.copy_fiscal_product_rule = cls.fiscal_product_rule.copy(
            default={"name": "Fiscal Product Rule (copy)"}
        )

    def test_no_rule(self):
        invoice = self.init_invoice(
            "out_invoice", partner=self.partner_b, products=[self.product_a]
        )
        line = invoice.line_ids.filtered(lambda r: r.product_id == self.product_a)
        # check the tax/account
        self.assertEqual(len(line.tax_ids), 1)
        self.assertEqual(line.tax_ids[0].amount, 15.0)
        self.assertEqual(line.account_id.code, "400000 (1)")

    def test_rule_on_parent_categ(self):
        categ = self.env.ref("product.product_category_1")
        categ.parent_id.fiscal_position_product_rule_ids = self.fiscal_product_rule
        self.product_a.categ_id = categ
        invoice = self.init_invoice(
            "out_invoice", partner=self.partner_b, products=[self.product_a]
        )
        line = invoice.line_ids.filtered(lambda r: r.product_id == self.product_a)
        # check the tax/account is the on define by the rule
        self.assertEqual(len(line.tax_ids), 1)
        self.assertEqual(line.tax_ids[0].amount, 30.0)
        self.assertEqual(line.account_id.code, "123456")

    def test_rule_on_categ(self):
        self.product_a.categ_id.fiscal_position_product_rule_ids = (
            self.fiscal_product_rule
        )
        invoice = self.init_invoice(
            "out_invoice", partner=self.partner_b, products=[self.product_a]
        )
        line = invoice.line_ids.filtered(lambda r: r.product_id == self.product_a)
        # check the tax/account is the on define by the rule
        self.assertEqual(len(line.tax_ids), 1)
        self.assertEqual(line.tax_ids[0].amount, 30.0)
        self.assertEqual(line.account_id.code, "123456")

    def test_rule_on_product(self):
        self.product_a.fiscal_position_product_rule_ids = self.fiscal_product_rule
        invoice = self.init_invoice(
            "out_invoice", partner=self.partner_b, products=[self.product_a]
        )
        line = invoice.line_ids.filtered(lambda r: r.product_id == self.product_a)
        # check the tax/account is the on define by the rule
        self.assertEqual(len(line.tax_ids), 1)
        self.assertEqual(line.tax_ids[0].amount, 30.0)
        self.assertEqual(line.account_id.code, "123456")

    def test_no_duplicate_fiscal_position(self):
        self.product_a.fiscal_position_product_rule_ids = self.fiscal_product_rule
        with self.assertRaises(ValidationError):
            self.product_a.fiscal_position_product_rule_ids += (
                self.copy_fiscal_product_rule
            )
