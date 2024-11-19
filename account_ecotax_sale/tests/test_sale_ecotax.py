# © 2021-2023 Akretion (http://www.akretion.com)
#   @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import Form

from odoo.addons.account_ecotax.tests.test_ecotax import TestInvoiceEcotaxCommon


class TestsaleEcotaxCommon(TestInvoiceEcotaxCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_a = cls.env["product.product"].create(
            {
                "name": "product_a",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "weight": 100,
                "list_price": 200,
            }
        )
        cls.product_b = cls.env["product.product"].create(
            {
                "name": "product_b",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "list_price": 200,
                "weight": 400,
            }
        )

        cls.product_a.ecotax_line_product_ids = [
            (
                0,
                0,
                {
                    # 2.4
                    "classification_id": cls.ecotax_fixed.id,
                },
            )
        ]
        cls.product_b.ecotax_line_product_ids = [
            (
                0,
                0,
                {
                    "classification_id": cls.ecotax_weight.id,
                },
            )
        ]

    def create_sale_partner(self, partner_id, products_and_qty):
        sale_form = Form(self.env["sale.order"])
        sale_form.partner_id = partner_id

        for product, qty in products_and_qty:
            with sale_form.order_line.new() as line_form:
                line_form.product_id = product
                line_form.product_uom_qty = qty

        sale = sale_form.save()

        return sale

    def _test_01_classification_weight_based_ecotax(self):
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
        self.assertEqual(self.sale.amount_total, 600)
        self.assertEqual(self.sale.amount_ecotax, 48)

    def _test_02_classification_ecotax(self):
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
        self.assertEqual(self.sale.amount_total, 1000.0)
        self.assertEqual(self.sale.amount_ecotax, 47.0)


class TestsaleEcotax(TestsaleEcotaxCommon):
    def test_01_classification_weight_based_ecotax(self):
        self._test_01_classification_weight_based_ecotax()

    def test_02_classification_ecotax(self):
        self._test_02_classification_ecotax()
