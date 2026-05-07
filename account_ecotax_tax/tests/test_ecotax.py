# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo.addons.account_ecotax.tests.test_ecotax import TestInvoiceEcotaxCommon


class TestInvoiceEcotaxTaxComon(TestInvoiceEcotaxCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        # ACCOUNTING STUFF
        # Main use case for using ecotax with tax is to manage the ecotax as not
        # included with tax not included (B2B case)
        # Also for this version, the included use case using tax is broken because
        # of a bug in Odoo core (check readme)
        cls.invoice_tax.price_include = False
        cls.invoice_ecotax_account = cls.env["account.account"].create(
            {
                "code": "707120",
                "name": "Ecotax Account",
                "account_type": "income",
                "company_id": cls.env.user.company_id.id,
            }
        )
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
        # ECOTAXES
        # 1- Fixed ecotax
        cls.ecotax_fixed.sale_ecotax_ids = cls.invoice_fixed_ecotax
        # 2- Weight-based ecotax
        cls.ecotax_weight.sale_ecotax_ids = cls.invoice_weight_based_ecotax


class TestInvoiceEcotaxTax(TestInvoiceEcotaxTaxComon):
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
            - invoice total amount: 115.5
            - line ecotax unit amount: 5.0
            - line ecotax total amount: 5.0
        """
        invoice = self._make_invoice(products=self._make_product(self.ecotax_fixed))
        self._run_checks(
            invoice,
            {"amount_ecotax": 5.0, "amount_total": 115.5},
            [{"ecotax_amount_unit": 5.0, "subtotal_ecotax": 5.0}],
        )
        new_qty = self._set_invoice_lines_random_quantities(invoice)[0]
        self._run_checks(
            invoice,
            {"amount_ecotax": 5.0 * new_qty, "amount_total": 115.5 * new_qty},
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
            - invoice total amount: 121.0
            - line ecotax unit amount: 10.0
            - line ecotax total amount: 10.0
        """
        product = self._make_product(self.ecotax_fixed)
        product.ecotax_line_product_ids[0].force_amount = 10
        invoice = self._make_invoice(products=product)
        self._run_checks(
            invoice,
            {"amount_ecotax": 10.0, "amount_total": 121.0},
            [{"ecotax_amount_unit": 10.0, "subtotal_ecotax": 10.0}],
        )
        new_qty = self._set_invoice_lines_random_quantities(invoice)[0]
        self._run_checks(
            invoice,
            {"amount_ecotax": 10.0 * new_qty, "amount_total": 121.0 * new_qty},
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
            - invoice total amount: 114.4
            - line ecotax unit amount: 4.0
            - line ecotax total amount: 4.0
        """
        invoice = self._make_invoice(products=self._make_product(self.ecotax_weight))
        self._run_checks(
            invoice,
            {"amount_ecotax": 4.0, "amount_total": 114.4},
            [{"ecotax_amount_unit": 4.0, "subtotal_ecotax": 4.0}],
        )
        new_qty = self._set_invoice_lines_random_quantities(invoice)[0]
        self._run_checks(
            invoice,
            {"amount_ecotax": 4.0 * new_qty, "amount_total": 114.4 * new_qty},
            [{"ecotax_amount_unit": 4.0, "subtotal_ecotax": 4.0 * new_qty}],
        )

    def test_04_mixed_ecotax(self):
        """Test mixed ecotax within the same invoice

        Creating an invoice with 3 lines (one per type with types tested above)

        Expected results (with 3 lines and qty = 1):
            - invoice ecotax amount: 19.0
            - invoice total amount: 350.9
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
            {"amount_ecotax": 19.0, "amount_total": 350.9},
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
                "amount_total": 115.5 * new_qtys[0]
                + 121.0 * new_qtys[1]
                + 114.4 * new_qtys[2],
            },
            [
                {"ecotax_amount_unit": 5.0, "subtotal_ecotax": 5.0 * new_qtys[0]},
                {"ecotax_amount_unit": 10.0, "subtotal_ecotax": 10.0 * new_qtys[1]},
                {"ecotax_amount_unit": 4.0, "subtotal_ecotax": 4.0 * new_qtys[2]},
            ],
        )

    def test_05_product_variants(self):
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
