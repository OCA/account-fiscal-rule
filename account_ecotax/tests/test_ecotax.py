# Copyright 2016-2023 Akretion France
#   @author: Alexis de Lattre <alexis.delattre@akretion.com>
# Copyright 2021 Camptocamp
#   @author Silvio Gregorini <silvio.gregorini@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from random import choice

from odoo.tests.common import Form, tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("-at_install", "post_install")
class TestInvoiceEcotaxe(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref)
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

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
                "price_include": True,
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
                "amount_type": "code",
                "is_ecotax": True,
                "python_compute": "result = product.fixed_ecotax or 0.0",
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
                "is_ecotax": True,
                "python_compute": "result = product.weight_based_ecotax or 0.0",
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
        # ECOTAXES
        # 1- Fixed ecotax
        cls.ecotax_fixed = cls.env["account.ecotax.classification"].create(
            {
                "name": "Fixed Ecotax",
                "ecotax_type": "fixed",
                "default_fixed_ecotax": 5.0,
                "product_status": "M",
                "supplier_status": "MAN",
            }
        )
        cls.ecotax_fixed.sale_ecotax_ids = cls.invoice_fixed_ecotax
        # 2- Weight-based ecotax
        cls.ecotax_weight = cls.env["account.ecotax.classification"].create(
            {
                "name": "Weight Based Ecotax",
                "ecotax_type": "weight_based",
                "ecotax_coef": 0.04,
                "product_status": "P",
                "supplier_status": "MAN",
            }
        )
        cls.ecotax_weight.sale_ecotax_ids = cls.invoice_weight_based_ecotax
        # MISC
        # 1- Invoice partner
        cls.invoice_partner = cls.env["res.partner"].create({"name": "Test"})

    @classmethod
    def _make_invoice(cls, products):
        """Creates a new customer invoice with given products and returns it"""
        return cls.init_invoice(
            "out_invoice",
            partner=cls.invoice_partner,
            products=products,
            company=cls.env.user.company_id,
            taxes=cls.invoice_tax,
        )

    @classmethod
    def _make_product(cls, ecotax_classification):
        """Creates a product template with given ecotax classification

        Returns the newly created template variant
        """
        tmpl = cls.env["product.template"].create(
            {
                "name": " - ".join(["Product", ecotax_classification.name]),
                "ecotax_line_product_ids": [
                    (
                        0,
                        0,
                        {
                            "classification_id": ecotax_classification.id,
                        },
                    )
                ],
                # For the sake of simplicity, every product will have a price
                # and weight of 100
                "list_price": 100.00,
                "weight": 100.00,
            }
        )
        return tmpl.product_variant_ids[0]

    @classmethod
    def _make_product_variants(cls, ecotax_classification):
        """Creates a product variants with given ecotax classification
        Returns the newly created template variants
        """
        size_attr = cls.env["product.attribute"].create(
            {
                "name": "Size",
                "create_variant": "always",
                "value_ids": [(0, 0, {"name": "S"}), (0, 0, {"name": "M"})],
            }
        )

        tmpl = cls.env["product.template"].create(
            {
                "name": " - ".join(["Product", ecotax_classification.name]),
                "ecotax_line_product_ids": [
                    (
                        0,
                        0,
                        {
                            "classification_id": ecotax_classification.id,
                        },
                    )
                ],
                # For the sake of simplicity, every product will have a price
                # and weight of 100
                "list_price": 100.00,
                "weight": 100.00,
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": size_attr.id,
                            "value_ids": [(6, 0, size_attr.value_ids.ids)],
                        },
                    )
                ],
            }
        )
        return tmpl.product_variant_ids

    @staticmethod
    def _set_invoice_lines_random_quantities(invoice) -> list:
        """For each invoice line, sets a random qty between 1 and 10

        Returns the list of new quantities as a list
        """
        new_qtys = []
        with Form(invoice) as invoice_form:
            for index in range(len(invoice.invoice_line_ids)):
                with invoice_form.invoice_line_ids.edit(index) as line_form:
                    new_qty = choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
                    line_form.quantity = new_qty
                    new_qtys.insert(index, new_qty)
                line_form.save()
        invoice_form.save()
        return new_qtys

    def _run_checks(self, inv, inv_expected_amounts, inv_lines_expected_amounts):
        self.assertEqual(inv.amount_ecotax, inv_expected_amounts["amount_ecotax"])
        self.assertEqual(inv.amount_total, inv_expected_amounts["amount_total"])
        self.assertEqual(len(inv.invoice_line_ids), len(inv_lines_expected_amounts))
        for inv_line, inv_line_expected_amounts in zip(
            inv.invoice_line_ids, inv_lines_expected_amounts
        ):
            self.assertEqual(
                inv_line.ecotax_amount_unit,
                inv_line_expected_amounts["ecotax_amount_unit"],
            )
            self.assertEqual(
                inv_line.subtotal_ecotax, inv_line_expected_amounts["subtotal_ecotax"]
            )

    def test_01_default_fixed_ecotax(self):
        """Test default fixed ecotax

        Ecotax classification data for this test:
            - fixed type
            - default amount: 5.0
        Product data for this test:
            - list price: 100
            - fixed ecotax
            - no manual amount

        Expected results (with 1 line and qty = 1):
            - invoice ecotax amount: 5.0
            - invoice total amount: 100.0
            - line ecotax unit amount: 5.0
            - line ecotax total amount: 5.0
        """
        invoice = self._make_invoice(products=self._make_product(self.ecotax_fixed))
        self._run_checks(
            invoice,
            {"amount_ecotax": 5.0, "amount_total": 100.0},
            [{"ecotax_amount_unit": 5.0, "subtotal_ecotax": 5.0}],
        )
        new_qty = self._set_invoice_lines_random_quantities(invoice)[0]
        self._run_checks(
            invoice,
            {"amount_ecotax": 5.0 * new_qty, "amount_total": 100.0 * new_qty},
            [{"ecotax_amount_unit": 5.0, "subtotal_ecotax": 5.0 * new_qty}],
        )

    def test_02_force_fixed_ecotax_on_product(self):
        """Test manual fixed ecotax

        Ecotax classification data for this test:
            - fixed type
            - default amount: 5.0
        Product data for this test:
            - list price: 100
            - fixed ecotax
            - Force ecotax amount: 10

        Expected results (with 1 line and qty = 1):
            - invoice ecotax amount: 10.0
            - invoice total amount: 100.0
            - line ecotax unit amount: 10.0
            - line ecotax total amount: 10.0
        """
        product = self._make_product(self.ecotax_fixed)
        product.ecotax_line_product_ids[0].force_amount = 10
        invoice = self._make_invoice(products=product)
        self._run_checks(
            invoice,
            {"amount_ecotax": 10.0, "amount_total": 100.0},
            [{"ecotax_amount_unit": 10.0, "subtotal_ecotax": 10.0}],
        )
        new_qty = self._set_invoice_lines_random_quantities(invoice)[0]
        self._run_checks(
            invoice,
            {"amount_ecotax": 10.0 * new_qty, "amount_total": 100.0 * new_qty},
            [{"ecotax_amount_unit": 10.0, "subtotal_ecotax": 10.0 * new_qty}],
        )

    def test_03_weight_based_ecotax(self):
        """Test weight based ecotax

        Ecotax classification data for this test:
            - weight based type
            - coefficient: 0.04
        Product data for this test:
            - list price: 100
            - weight based ecotax
            - weight: 100

        Expected results (with 1 line and qty = 1):
            - invoice ecotax amount: 4.0
            - invoice total amount: 100.0
            - line ecotax unit amount: 4.0
            - line ecotax total amount: 4.0
        """
        invoice = self._make_invoice(products=self._make_product(self.ecotax_weight))
        self._run_checks(
            invoice,
            {"amount_ecotax": 4.0, "amount_total": 100.0},
            [{"ecotax_amount_unit": 4.0, "subtotal_ecotax": 4.0}],
        )
        new_qty = self._set_invoice_lines_random_quantities(invoice)[0]
        self._run_checks(
            invoice,
            {"amount_ecotax": 4.0 * new_qty, "amount_total": 100.0 * new_qty},
            [{"ecotax_amount_unit": 4.0, "subtotal_ecotax": 4.0 * new_qty}],
        )

    def test_04_mixed_ecotax(self):
        """Test mixed ecotax within the same invoice

        Creating an invoice with 3 lines (one per type with types tested above)

        Expected results (with 3 lines and qty = 1):
            - invoice ecotax amount: 19.0
            - invoice total amount: 300.0
            - line ecotax unit amount (fixed ecotax): 5.0
            - line ecotax total amount (fixed ecotax): 5.0
            - line ecotax unit amount (manual ecotax): 10.0
            - line ecotax total amount (manual ecotax): 10.0
            - line ecotax unit amount (weight based ecotax): 4.0
            - line ecotax total amount (weight based ecotax): 4.0
        """
        default_fixed_product = self._make_product(self.ecotax_fixed)
        manual_fixed_product = self._make_product(self.ecotax_fixed)
        manual_fixed_product.ecotax_line_product_ids[0].force_amount = 10
        weight_based_product = self._make_product(self.ecotax_weight)
        invoice = self._make_invoice(
            products=default_fixed_product | manual_fixed_product | weight_based_product
        )
        self._run_checks(
            invoice,
            {"amount_ecotax": 19.0, "amount_total": 300.0},
            [
                {"ecotax_amount_unit": 5.0, "subtotal_ecotax": 5.0},
                {"ecotax_amount_unit": 10.0, "subtotal_ecotax": 10.0},
                {"ecotax_amount_unit": 4.0, "subtotal_ecotax": 4.0},
            ],
        )
        new_qtys = self._set_invoice_lines_random_quantities(invoice)
        self._run_checks(
            invoice,
            {
                "amount_ecotax": 5.0 * new_qtys[0]
                + 10.0 * new_qtys[1]
                + 4.0 * new_qtys[2],
                "amount_total": 100.0 * sum(new_qtys),
            },
            [
                {"ecotax_amount_unit": 5.0, "subtotal_ecotax": 5.0 * new_qtys[0]},
                {"ecotax_amount_unit": 10.0, "subtotal_ecotax": 10.0 * new_qtys[1]},
                {"ecotax_amount_unit": 4.0, "subtotal_ecotax": 4.0 * new_qtys[2]},
            ],
        )

    def test_05_force_ecotax_on_invoice(self):
        """Test force fixed ecotax

        Ecotax classification data for this test:
            - fixed type
            - default amount: 5.0
            - forced amount: 2
        Product data for this test:
            - list price: 100
            - fixed ecotax : 5

        Expected results (with 1 line and qty = 1):
            - invoice ecotax amount: 2.0
            - invoice total amount: 100.0
            - line ecotax unit amount: 2.0
            - line ecotax total amount: 2.0
        """
        product = self._make_product(self.ecotax_fixed)
        invoice = self._make_invoice(products=product)
        invoice.invoice_line_ids[0].ecotax_line_ids.force_amount_unit = 2
        self._run_checks(
            invoice,
            {"amount_ecotax": 2.0, "amount_total": 100.0},
            [{"ecotax_amount_unit": 2.0, "subtotal_ecotax": 2.0}],
        )
        new_qty = self._set_invoice_lines_random_quantities(invoice)[0]
        self._run_checks(
            invoice,
            {"amount_ecotax": 2.0 * new_qty, "amount_total": 100.0 * new_qty},
            [{"ecotax_amount_unit": 2.0, "subtotal_ecotax": 2.0 * new_qty}],
        )

    def test_06_product_variants(self):
        """
        Data:
            A product template with two variants
        Test Case:
            Add additional ecotax line to one variant
        Expected result:
            The additional ecotax line is not associated  to second variant
            the all ecotax lines of the variant contains both the ecotax
            line of the product template and the additional ecotax line
        """
        variants = self._make_product_variants(self.ecotax_fixed)
        self.assertEqual(len(variants), 2)
        variant_1 = variants[0]
        variant_2 = variants[1]
        self.assertEqual(
            variant_1.all_ecotax_line_product_ids,
            variant_2.all_ecotax_line_product_ids,
        )
        variant_1.additional_ecotax_line_product_ids = [
            (
                0,
                0,
                {
                    "classification_id": self.ecotax_weight.id,
                },
            )
        ]
        all_additional_ecotax = (
            variant_1.additional_ecotax_line_product_ids
            | variant_1.product_tmpl_id.ecotax_line_product_ids
        )
        self.assertEqual(
            len(variant_1.all_ecotax_line_product_ids),
            2,
        )
        self.assertEqual(
            len(variant_2.all_ecotax_line_product_ids),
            1,
        )
        self.assertEqual(
            variant_1.all_ecotax_line_product_ids,
            all_additional_ecotax,
        )
        self.assertEqual(
            variant_2.all_ecotax_line_product_ids,
            variant_2.product_tmpl_id.ecotax_line_product_ids,
        )
