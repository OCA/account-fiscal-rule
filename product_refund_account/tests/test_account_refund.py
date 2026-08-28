# Copyright 2022 Trey, Kilobytes de Soluciones - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


class TestRefundAccount(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Account = cls.env["account.account"]
        cls.refund_in_account = Account.create(
            {
                "name": "Account Refund In",
                "code": "608TEST",
                "account_type": "expense",
            }
        )
        cls.refund_out_account = Account.create(
            {
                "name": "Account Refund Out",
                "code": "708TEST",
                "account_type": "income",
            }
        )
        cls.test_category = cls.env["product.category"].create(
            {
                "name": "Test Refund Category",
                "property_account_income_categ_id": cls.company_data[
                    "default_account_revenue"
                ].id,
                "property_account_expense_categ_id": cls.company_data[
                    "default_account_expense"
                ].id,
                "property_account_refund_in_categ_id": cls.refund_in_account.id,
                "property_account_refund_out_categ_id": cls.refund_out_account.id,
            }
        )
        cls.test_product = cls.env["product.product"].create(
            {
                "name": "Test Refund Product",
                "categ_id": cls.test_category.id,
            }
        )
        cls.test_product_direct = cls.env["product.product"].create(
            {
                "name": "Test Refund Product (Direct Accounts)",
                "categ_id": cls.test_category.id,
                "property_account_refund_in_id": cls.refund_in_account.id,
                "property_account_refund_out_id": cls.refund_out_account.id,
            }
        )

    def test_direct_vendor_credit_note_from_category(self):
        """
        Account from category is used when creating a vendor credit note directly.
        """
        move = self.env["account.move"].create(
            {
                "move_type": "in_refund",
                "partner_id": self.partner_a.id,
                "journal_id": self.company_data["default_journal_purchase"].id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.test_product.id,
                            "quantity": 1.0,
                            "price_unit": 10.0,
                        },
                    )
                ],
            }
        )
        self.assertEqual(move.invoice_line_ids.account_id, self.refund_in_account)

    def test_direct_customer_credit_note_from_category(self):
        """
        Account from category is used when creating a customer credit note directly.
        """
        move = self.env["account.move"].create(
            {
                "move_type": "out_refund",
                "partner_id": self.partner_a.id,
                "journal_id": self.company_data["default_journal_sale"].id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.test_product.id,
                            "quantity": 1.0,
                            "price_unit": 10.0,
                        },
                    )
                ],
            }
        )
        self.assertEqual(move.invoice_line_ids.account_id, self.refund_out_account)

    def test_direct_vendor_credit_note_from_product(self):
        """
        Account from product takes precedence over category for vendor credit note.
        """
        move = self.env["account.move"].create(
            {
                "move_type": "in_refund",
                "partner_id": self.partner_a.id,
                "journal_id": self.company_data["default_journal_purchase"].id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.test_product_direct.id,
                            "quantity": 1.0,
                            "price_unit": 10.0,
                        },
                    )
                ],
            }
        )
        self.assertEqual(move.invoice_line_ids.account_id, self.refund_in_account)

    def test_direct_customer_credit_note_from_product(self):
        """
        Account from product takes precedence over category for customer credit note.
        """
        move = self.env["account.move"].create(
            {
                "move_type": "out_refund",
                "partner_id": self.partner_a.id,
                "journal_id": self.company_data["default_journal_sale"].id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.test_product_direct.id,
                            "quantity": 1.0,
                            "price_unit": 10.0,
                        },
                    )
                ],
            }
        )
        self.assertEqual(move.invoice_line_ids.account_id, self.refund_out_account)

    def test_reversed_vendor_invoice(self):
        """
        Refund account is applied when reversing a vendor invoice.
        """
        invoice = self.env["account.move"].create(
            {
                "move_type": "in_invoice",
                "partner_id": self.partner_a.id,
                "journal_id": self.company_data["default_journal_purchase"].id,
                "invoice_date": "2024-01-01",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.test_product.id,
                            "quantity": 1.0,
                            "price_unit": 10.0,
                        },
                    )
                ],
            }
        )
        invoice.action_post()
        refund = invoice._reverse_moves()
        self.assertEqual(refund.invoice_line_ids.account_id, self.refund_in_account)

    def test_reversed_customer_invoice(self):
        """
        Refund account is applied when reversing a customer invoice.
        """
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner_a.id,
                "journal_id": self.company_data["default_journal_sale"].id,
                "invoice_date": "2024-01-01",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.test_product.id,
                            "quantity": 1.0,
                            "price_unit": 10.0,
                        },
                    )
                ],
            }
        )
        invoice.action_post()
        refund = invoice._reverse_moves()
        self.assertEqual(refund.invoice_line_ids.account_id, self.refund_out_account)
