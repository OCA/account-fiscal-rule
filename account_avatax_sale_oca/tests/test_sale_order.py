# Copyright 2021 Open Source Integrators
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


from odoo.fields import Command
from odoo.tests import Form, common


class TestSaleOrder(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Customer",
            }
        )
        cls.empty_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
            }
        )
        cls.product = cls.env["product.product"].create({"name": "Super Product"})

    def test_sale_order_onchange(self):
        """We found a bug where the price when the decimal accuracy was 5,
        the price would be automatically reset to the pricelist price after
        saving the order. The reason was a wrong implementation of
        onchange_reset_avatax_amount. In this test we demonstrate that
        the error does not happen anymore."""
        # Change accuracy of product unit of measure
        self.env.ref("product.decimal_product_uom").digits = 5
        # Enable pricelists
        self.env.user.groups_id += self.env.ref("product.group_product_pricelist")
        self.pricelist = self.env["product.pricelist"].create(
            {
                "name": "Test pricelist",
                "discount_policy": "without_discount",
                "item_ids": [
                    Command.create(
                        {
                            "base": "list_price",
                            "min_quantity": 6,
                            "product_id": self.product.id,
                            "compute_price": "fixed",
                            "fixed_price": 20,
                        }
                    ),
                ],
            }
        )
        so = self.empty_order
        so_form = Form(so)
        so_form.pricelist_id = self.pricelist
        with so_form.order_line.new() as line:
            line.product_id = self.product
            line.product_uom_qty = 7.0
        so_form.save()
        with so_form.order_line.new() as line:
            line.product_id = self.product
            line.product_uom_qty = 7.0
        so_form.save()
        with Form(so) as so_form:
            with so_form.order_line.edit(0) as line0_form:
                line0_form.price_unit = 100.00000
            with so_form.order_line.edit(1) as line1_form:
                line1_form.price_unit = 100.00000
        so_form.save()
        self.assertEqual(so.tax_amount, 0.0)
        self.assertEqual(so.order_line[0].price_unit, 100.00000)
        self.assertEqual(so.order_line[0].tax_amt, 0.0)
        self.assertEqual(so.order_line[1].price_unit, 100.00000)
        self.assertEqual(so.order_line[1].tax_amt, 0.0)
        with Form(so) as so_form:
            with so_form.order_line.edit(1) as line1_form:
                line1_form.price_unit = 200.00000
        so_form.save()
        self.assertEqual(so.tax_amount, 0.0)
        self.assertEqual(so.order_line[0].price_unit, 100.00000)
        self.assertEqual(so.order_line[0].tax_amt, 0.0)
        self.assertEqual(so.order_line[1].price_unit, 200.00000)
        self.assertEqual(so.order_line[1].tax_amt, 0.0)
