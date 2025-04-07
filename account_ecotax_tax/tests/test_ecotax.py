# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo.addons.account_ecotax.tests.test_ecotax import TestInvoiceEcotaxCommon


class TestInvoiceEcotaxTaxComon(TestInvoiceEcotaxCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        # ACCOUNTING STUFF
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
                "price_include": True,
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
                "price_include": True,
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
        self._test_01_default_fixed_ecotax()

    def test_02_force_fixed_ecotax_on_product(self):
        self._test_02_force_fixed_ecotax_on_product()

    def test_03_weight_based_ecotax(self):
        self._test_03_weight_based_ecotax()

    def test_04_mixed_ecotax(self):
        self._test_04_mixed_ecotax()

    def test_05_product_variants(self):
        self._test_05_product_variants()
