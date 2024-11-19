# © 2021-2023 Akretion (http://www.akretion.com)
#   @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.addons.account_ecotax_sale.tests.test_sale_ecotax import TestsaleEcotaxCommon
from odoo.addons.account_ecotax_tax.tests.test_ecotax import TestInvoiceEcotaxTaxComon


class TestsaleEcotaxTax(TestInvoiceEcotaxTaxComon, TestsaleEcotaxCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_01_classification_weight_based_ecotax(self):
        self._test_01_classification_weight_based_ecotax()

    def test_02_classification_ecotax(self):
        self._test_02_classification_ecotax()
