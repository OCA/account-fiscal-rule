# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.tests import tagged

from odoo.addons.account.tests.common import TestAccountReconciliationCommon


@tagged("post_install", "-at_install")
class TestEcotaxAccounting(TestAccountReconciliationCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.ecotax_journal = cls.env["account.journal"].create(
            {
                "name": "Ecotax",
                "code": "ECO",
                "type": "general",
            }
        )
        cls.ecotax_account1 = cls.env["account.account"].create(
            {
                "name": "Ecotax revenue",
                "code": "708015",
                "account_type": "income",
            }
        )
        cls.ecotax_account2 = cls.env["account.account"].create(
            {
                "name": "Ecotax revenue 2",
                "code": "708016",
                "account_type": "income",
            }
        )
        cls.product_account_revenue = cls.env["account.account"].create(
            {
                "name": "Product revenue",
                "code": "701016",
                "account_type": "income",
            }
        )
        cls.ecotax_classification1 = cls.env["account.ecotax.classification"].create(
            {
                "name": "Fixed Ecotax 1",
                "ecotax_type": "fixed",
                "default_fixed_ecotax": 0.4,
                "product_status": "M",
                "supplier_status": "MAN",
                "ecotax_account_id": cls.ecotax_account1.id,
            }
        )
        cls.env.company.write(
            {
                "ecotax_account_id": cls.ecotax_account2.id,
                "ecotax_journal_id": cls.ecotax_journal.id,
            }
        )
        cls.ecotax_classification2 = cls.env["account.ecotax.classification"].create(
            {
                "name": "Fixed Ecotax 2",
                "ecotax_type": "fixed",
                "default_fixed_ecotax": 0.2,
                "product_status": "M",
                "supplier_status": "MAN",
            }
        )
        cls.invoice_partner = cls.env["res.partner"].create({"name": "Test"})

    def test_invoice_ecotax_isolation(self):
        eco_class1_id = self.ecotax_classification1.id
        eco_class2_id = self.ecotax_classification2.id
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.invoice_partner.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "account_id": self.company_data[
                                "default_account_revenue"
                            ].id,
                            "price_unit": 10.0,
                            "quantity": 2.0,
                            "name": "invoice line 1",
                            "tax_ids": [(6, 0, [])],
                            "ecotax_line_ids": [
                                (
                                    0,
                                    0,
                                    {
                                        "classification_id": eco_class1_id,
                                    },
                                ),
                                (
                                    0,
                                    0,
                                    {
                                        "classification_id": eco_class2_id,
                                    },
                                ),
                            ],
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "account_id": self.product_account_revenue.id,
                            "price_unit": 20.0,
                            "quantity": 1.0,
                            "name": "invoice line 2",
                            "tax_ids": [(6, 0, [])],
                            "ecotax_line_ids": [
                                (
                                    0,
                                    0,
                                    {
                                        "classification_id": eco_class1_id,
                                    },
                                ),
                            ],
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "account_id": self.product_account_revenue.id,
                            "price_unit": 30.0,
                            "quantity": 2.0,
                            "name": "invoice line 2",
                            "tax_ids": [(6, 0, [])],
                            "ecotax_line_ids": [
                                (
                                    0,
                                    0,
                                    {
                                        "classification_id": eco_class2_id,
                                    },
                                ),
                            ],
                        },
                    ),
                ],
            }
        )
        invoice.action_post()
        self.assertEqual(invoice.amount_total, 100.0)

        ecotax_move = invoice.ecotax_move_id
        self.assertTrue(ecotax_move)
        self.assertEqual(ecotax_move.journal_id, self.ecotax_journal)
        self.assertEqual(ecotax_move.state, "posted")
        self.assertEqual(len(ecotax_move.line_ids), 4)
        default_product_line = ecotax_move.line_ids.filtered(
            lambda l: l.account_id == self.company_data["default_account_revenue"]
        )
        other_product_line = ecotax_move.line_ids.filtered(
            lambda l: l.account_id == self.product_account_revenue
        )
        ecotax1_line = ecotax_move.line_ids.filtered(
            lambda l: l.account_id == self.ecotax_account1
        )
        ecotax2_line = ecotax_move.line_ids.filtered(
            lambda l: l.account_id == self.ecotax_account2
        )

        self.assertAlmostEqual(default_product_line.debit, 1.2)
        self.assertAlmostEqual(other_product_line.debit, 0.8)
        self.assertAlmostEqual(ecotax1_line.credit, 1.2)
        self.assertAlmostEqual(ecotax2_line.credit, 0.8)

        # test update on invoice
        invoice.button_draft()
        self.assertEqual(ecotax_move.state, "cancel")
        line1 = invoice.invoice_line_ids.filtered(
            lambda l: l.account_id == self.company_data["default_account_revenue"]
        )
        line1.write({"quantity": 1.0})
        invoice.action_post()
        self.assertEqual(ecotax_move.state, "posted")
        ecotax1_line = ecotax_move.line_ids.filtered(
            lambda l: l.account_id == self.ecotax_account1
        )
        self.assertAlmostEqual(ecotax1_line.credit, 0.8)
