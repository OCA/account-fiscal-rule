# Copyright (C) 2022 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import SavepointCase


class TestSaleOrder(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestSaleOrder, cls).setUpClass()
        cls.us = cls.env.ref("base.us")
        cls.labor_category = cls.env["product.category"].create({"name": "All / Labor"})
        cls.state_florida = cls.env.ref("base.state_us_10")
        cls.fiscal_pos = cls.env["account.fiscal.position"].create(
            {"name": "Test Avatax Fiscal", "is_avatax": True}
        )
        cls.partner_1 = cls.env["res.partner"].create(
            {
                "name": "Julia Agrolait",
                "street": "10000 W Colonial Dr",
                "city": "Ocoee",
                "state_id": cls.state_florida.id,
                "zip": "34761-3400",
                "country_id": cls.us.id,
                "email": "julia@agrolait.example.com",
            }
        )
        cls.labor_pm_taxable = cls.env["product.product"].create(
            {
                "name": "LABOR - PM TAXABLE",
                "type": "service",
                "standard_price": 40.0,
                "list_price": 90.0,
                "categ_id": cls.labor_category.id,
            }
        )
        cls.labor_pm = cls.env["product.product"].create(
            {
                "name": "LABOR - PM",
                "type": "service",
                "standard_price": 40.0,
                "list_price": 90.0,
                "categ_id": cls.labor_category.id,
                "tax_swapping_product_id": cls.labor_pm_taxable.id,
            }
        )
        cls.labor_reg = cls.env["product.product"].create(
            {
                "name": "LABOR - REGULAR",
                "type": "service",
                "standard_price": 40.0,
                "list_price": 90.0,
                "categ_id": cls.labor_category.id,
            }
        )
        SaleOrder = cls.env["sale.order"].with_context(tracking_disable=True)
        cls.sale_order = SaleOrder.create(
            {
                "partner_id": cls.partner_1.id,
                "partner_invoice_id": cls.partner_1.id,
                "partner_shipping_id": cls.partner_1.id,
                "fiscal_position_id": cls.fiscal_pos.id,
            }
        )

        cls.sol_product_labor_pm = cls.env["sale.order.line"].create(
            {
                "name": cls.labor_pm.name,
                "product_id": cls.labor_pm.id,
                "product_uom_qty": 2,
                "product_uom": cls.labor_pm.uom_id.id,
                "price_unit": cls.labor_pm.list_price,
                "order_id": cls.sale_order.id,
                "tax_id": False,
            }
        )
        cls.sol_product_labor_reg = cls.env["sale.order.line"].create(
            {
                "name": cls.labor_reg.name,
                "product_id": cls.labor_reg.id,
                "product_uom_qty": 2,
                "product_uom": cls.labor_reg.uom_id.id,
                "price_unit": cls.labor_reg.list_price,
                "order_id": cls.sale_order.id,
                "tax_id": False,
            }
        )

    def test_sale_order(self):
        self.sale_order.avalara_compute_taxes()
