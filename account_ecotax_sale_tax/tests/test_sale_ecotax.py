# © 2021-2023 Akretion (http://www.akretion.com)
#   @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.tests.common import Form

from odoo.addons.account_ecotax_sale.tests.test_sale_ecotax import TestsaleEcotaxCommon
from odoo.addons.account_ecotax_tax.tests.test_ecotax import TestInvoiceEcotaxTaxComon


class TestsaleEcotaxTax(TestInvoiceEcotaxTaxComon, TestsaleEcotaxCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_01_classification_weight_based_ecotax(self):
        """Tests  with weight based ecotaxs"""
        # in order to test the correct assignment of weight ecotax
        # I create a customer sale.
        partner12 = self.env.ref("base.res_partner_12")
        self.sale = self.create_sale_partner(
            partner_id=partner12, products_and_qty=[(self.product_b, 1.0)]
        )
        self.assertEqual(self.product_b.ecotax_amount, 16)
        so_form = Form(self.sale)
        with so_form.order_line.edit(0) as line:
            line.product_uom_qty = 3.0
        so_form.save()
        self.assertEqual(self.sale.order_line.ecotax_amount_unit, 16)
        self.assertEqual(self.sale.order_line.subtotal_ecotax, 48)
        self.assertEqual(self.sale.amount_total, 648)
        self.assertEqual(self.sale.amount_ecotax, 48)

    def test_02_classification_ecotax(self):
        """Tests multiple lines with mixed ecotaxs"""
        # in order to test the correct assignment of fixed ecotax and weight ecotax
        # I create a customer sale.
        partner12 = self.env.ref("base.res_partner_12")
        self.sale = self.create_sale_partner(
            partner_id=partner12,
            products_and_qty=[(self.product_a, 1.0), (self.product_b, 2.0)],
        )
        # I assign a product with fixed ecotaxte to sale line
        sale_line1 = self.sale.order_line[0]
        # make sure to have 1 tax and fix tax rate
        sale_line2 = self.sale.order_line[1]
        # make sure to have 1 tax and fix tax rate
        self.assertEqual(self.product_a.ecotax_amount, 5.0)
        so_form = Form(self.sale)
        with so_form.order_line.edit(0) as line:
            line.product_uom_qty = 3.0
        so_form.save()

        self.assertEqual(sale_line1.ecotax_amount_unit, 5.0)
        self.assertAlmostEqual(sale_line1.subtotal_ecotax, 15.0)
        self.assertEqual(sale_line2.ecotax_amount_unit, 16)
        self.assertEqual(sale_line2.subtotal_ecotax, 32)
        self.assertEqual(self.sale.amount_total, 1047.0)
        self.assertEqual(self.sale.amount_ecotax, 47.0)
