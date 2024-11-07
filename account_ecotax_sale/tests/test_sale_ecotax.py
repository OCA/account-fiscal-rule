# © 2021-2023 Akretion (http://www.akretion.com)
#   @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import tagged
from odoo import Command

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("-at_install", "post_install")
class TestsaleEcotax(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref="l10n_fr.l10n_fr_pcg_chart_template"):
        super(TestsaleEcotax, cls).setUpClass(chart_template_ref)
        # ACCOUNTING STUFF
        # 1- Tax account
        cls.invoice_tax_account = cls.env["account.account"].create(
            {
                "code": "47590",
                "name": "Invoice Tax Account",
                "account_type": "liability_current",
                "company_id": cls.env.user.company_id.id,
            }
        )
        cls.invoice_ecotax_account = cls.env["account.account"].create(
            {
                "code": "707120",
                "name": "Ecotax Account",
                "account_type": "income",
                "company_id": cls.env.user.company_id.id,
            }
        )
        # 2- Invoice tax with included price to avoid unwanted amounts in tests
        cls.invoice_tax = cls.env["account.tax"].create(
            {
                "name": "Tax 10%",
                "price_include": False,
                "type_tax_use": "sale",
                "company_id": cls.env.user.company_id.id,
                "amount": 10,
                "tax_exigibility": "on_invoice",
                "invoice_repartition_line_ids": [
                    (
                        0,
                        0,
                        {
                            "factor_percent": 100,
                            "repartition_type": "base",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "factor_percent": 100,
                            "repartition_type": "tax",
                            "account_id": cls.invoice_tax_account.id,
                        },
                    ),
                ],
                "refund_repartition_line_ids": [
                    (
                        0,
                        0,
                        {
                            "factor_percent": 100,
                            "repartition_type": "base",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "factor_percent": 100,
                            "repartition_type": "tax",
                            "account_id": cls.invoice_tax_account.id,
                        },
                    ),
                ],
            }
        )
        # 3 Ecotaxes tax
        cls.invoice_fixed_ecotax = cls.env["account.tax"].create(
            {
                "name": "Fixed Ecotax",
                "type_tax_use": "sale",
                "company_id": cls.env.user.company_id.id,
                "price_include": False,
                "amount_type": "code",
                "include_base_amount": True,
                "sequence": 0,
                "is_ecotax": True,
                "python_compute": "result = (quantity and"
                " product.fixed_ecotax * quantity  or 0.0)",
                "tax_exigibility": "on_invoice",
                "invoice_repartition_line_ids": [
                    (
                        0,
                        0,
                        {
                            "factor_percent": 100,
                            "repartition_type": "base",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "factor_percent": 100,
                            "repartition_type": "tax",
                            "account_id": cls.invoice_ecotax_account.id,
                        },
                    ),
                ],
                "refund_repartition_line_ids": [
                    (
                        0,
                        0,
                        {
                            "factor_percent": 100,
                            "repartition_type": "base",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "factor_percent": 100,
                            "repartition_type": "tax",
                            "account_id": cls.invoice_ecotax_account.id,
                        },
                    ),
                ],
            }
        )
        cls.invoice_weight_based_ecotax = cls.env["account.tax"].create(
            {
                "name": "Weight Based Ecotax",
                "type_tax_use": "sale",
                "company_id": cls.env.user.company_id.id,
                "amount_type": "code",
                "include_base_amount": True,
                "price_include": False,
                "sequence": 0,
                "is_ecotax": True,
                "python_compute": "result = (quantity and"
                " product.weight_based_ecotax * quantity or 0.0)",
                "tax_exigibility": "on_invoice",
                "invoice_repartition_line_ids": [
                    (
                        0,
                        0,
                        {
                            "factor_percent": 100,
                            "repartition_type": "base",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "factor_percent": 100,
                            "repartition_type": "tax",
                            "account_id": cls.invoice_ecotax_account.id,
                        },
                    ),
                ],
                "refund_repartition_line_ids": [
                    (
                        0,
                        0,
                        {
                            "factor_percent": 100,
                            "repartition_type": "base",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "factor_percent": 100,
                            "repartition_type": "tax",
                            "account_id": cls.invoice_ecotax_account.id,
                        },
                    ),
                ],
            }
        )
        cls.ecotax_classification = cls.env["account.ecotax.classification"]
        cls.ecotax_classification1 = cls.ecotax_classification.create(
            {
                "name": "Fixed Ecotax",
                "ecotax_type": "fixed",
                "default_fixed_ecotax": 2.4,
                "product_status": "M",
                "supplier_status": "MAN",
                "sale_ecotax_ids": [(4, cls.invoice_fixed_ecotax.id)],
            }
        )
        cls.ecotax_classification2 = cls.ecotax_classification.create(
            {
                "name": "Weight based",
                "ecotax_type": "weight_based",
                "ecotax_coef": 0.04,
                "product_status": "P",
                "supplier_status": "MAN",
                "sale_ecotax_ids": [(4, cls.invoice_weight_based_ecotax.id)],
            }
        )
        cls.product_a.weight = 100
        cls.product_a.taxes_id = [Command.set(cls.invoice_tax.ids)]
        cls.product_a.ecotax_line_product_ids = [
            (
                0,
                0,
                {
                    "classification_id": cls.ecotax_classification1.id,
                },
            )
        ]
        cls.product_b.weight = 400
        cls.product_b.taxes_id = [Command.set(cls.invoice_tax.ids)]
        cls.product_b.ecotax_line_product_ids = [
            (
                0,
                0,
                {
                    "classification_id": cls.ecotax_classification2.id,
                },
            )
        ]

    def create_sale_partner(self, partner_id, product_id, sale_amount=0.00):
        order = self.env["sale.order"].create(
            {
                "partner_id": partner_id.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product_id.id,
                            "product_uom_qty": 1,
                            "price_unit": sale_amount,
                        },
                    )
                ],
            }
        )
        order.order_line._compute_tax_id()
        order.order_line._compute_ecotax()
        return order

    def test_02_classification_weight_based_ecotax(self):
        """Tests multiple lines with weight based ecotaxs"""
        # in order to test the correct assignment of fixed ecotax
        # I create a customer sale.
        partner12 = self.env.ref("base.res_partner_12")
        self.sale = self.create_sale_partner(
            sale_amount=200.00, partner_id=partner12, product_id=self.product_b
        )
        # I assign a product with fixed ecotaxte to sale line
        self.sale_line1 = self.sale.order_line[0]
        # make sure to have 1 tax and fix tax rate
        self.sale_line1.tax_id = self.sale_line1.tax_id[0]
        self.sale_line1.tax_id.amount = 20
        self.sale_line1._onchange_product_ecotax_line()
        self.sale_line1._compute_ecotax()
        self.sale_line1._compute_amount()
        self.sale._compute_amounts()
        self.assertEqual(self.product_b.ecotax_amount, 16)
        self.sale_line1.product_uom_qty = 3
        self.sale_line1._compute_tax_id()
        self.sale_line1._compute_ecotax()
        self.assertEqual(self.sale_line1.ecotax_amount_unit, 16)
        self.assertEqual(self.sale_line1.subtotal_ecotax, 48)
        self.assertEqual(self.sale.amount_total, 777.6)
        self.assertEqual(self.sale.amount_ecotax, 48)

    def test_03_classification_ecotax(self):
        """Tests multiple lines with mixed ecotaxs"""
        # in order to test the correct assignment of fixed ecotax
        # I create a customer sale.
        partner12 = self.env.ref("base.res_partner_12")
        self.sale = self.create_sale_partner(
            sale_amount=100.00, partner_id=partner12, product_id=self.product_a
        )
        # add line to SO
        self.env["sale.order.line"].create(
            {
                "product_id": self.product_b.id,
                "product_uom_qty": 2,
                "price_unit": 100,
                "order_id": self.sale.id,
            },
        )
        # I assign a product with fixed ecotaxte to sale line
        self.sale_line1 = self.sale.order_line[0]
        # make sure to have 1 tax and fix tax rate
        self.sale_line2 = self.sale.order_line[1]
        # make sure to have 1 tax and fix tax rate
        self.sale_line1._onchange_product_ecotax_line()
        self.sale_line1._compute_ecotax()
        self.assertEqual(self.product_a.ecotax_amount, 2.4)
        self.sale_line1.product_uom_qty = 3
        self.sale_line1._onchange_product_ecotax_line()
        self.assertEqual(self.sale_line1.ecotax_amount_unit, 2.4)
        self.assertAlmostEqual(self.sale_line1.subtotal_ecotax, 7.2)
        self.sale_line2._onchange_product_ecotax_line()
        self.sale_line1._compute_ecotax()
        self.assertEqual(self.sale_line2.ecotax_amount_unit, 16)
        self.assertEqual(self.sale_line2.subtotal_ecotax, 32)
        self.assertEqual(self.sale.amount_untaxed, 3200.0)
        self.assertEqual(self.sale.amount_ecotax, 39.2)
