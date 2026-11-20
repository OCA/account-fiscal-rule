# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo.addons.account_ecotax.tests.test_ecotax import TestInvoiceEcotaxCommon


class TestInvoiceEcotaxTax(TestInvoiceEcotaxCommon):
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
