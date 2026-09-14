# Copyright 2025 Kencove, Open Source Integrators
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import logging

from odoo.tests.common import tagged

from odoo.addons.account_avatax_oca.tests.common import TestAvataxCommon

_logger = logging.getLogger(__name__)


@tagged("-at_install", "post_install")
class TestAvataxSaleOrder(TestAvataxCommon):
    @classmethod
    def setUpClass(cls):
        res = super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.company = cls.env.user.company_id
        cls.company.write(
            {
                "street": "255 Executive Park Blvd",
                "city": "San Francisco",
                "state_id": cls.env.ref("base.state_us_5").id,
                "country_id": cls.env.ref("base.us").id,
                "zip": "94134",
            }
        )

        cls.product_A = cls.env["product.product"].create(
            {
                "name": "Product A",
                "list_price": 100,
                "sale_ok": True,
            }
        )

        cls.product_B = cls.env["product.product"].create(
            {
                "name": "Product B",
                "list_price": 5,
                "sale_ok": True,
            }
        )

        # Create exemption
        cls.exemption = cls.env["exemption.code"].create(
            {
                "name": "RESALE",
                "code": "1234",
            }
        )

        cls.company2 = cls.env["res.company"].create(
            {
                "name": "Test Avatax Company",
                "currency_id": cls.env.ref("base.USD").id,
                "street": "266 Executive Park Blvd",
                "city": "San Francisco",
                "state_id": cls.env.ref("base.state_us_5").id,
                "country_id": cls.env.ref("base.us").id,
                "zip": "94134",
            }
        )

        cls.partner_exempt = cls.env["res.partner"].create(
            {
                "name": "Tax Exempt Partner",
                "is_company": True,
                "street": "2288 Market St",
                "city": "San Francisco",
                "state_id": cls.env.ref("base.state_us_5").id,
                "country_id": cls.env.ref("base.us").id,
                "zip": "94114",
                "property_account_position_id": cls.fp_avatax.id,
                "property_tax_exempt": True,
                "property_exemption_number": "1234",
                "property_exemption_code_id": cls.exemption.id,
            }
        )

        # Create sale order
        cls.order = cls.env["sale.order"].create(
            {
                "company_id": cls.company.id,
                "partner_id": cls.partner_exempt.id,
            }
        )
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.order.write(
            {
                "order_line": [
                    (
                        0,
                        False,
                        {
                            "product_id": cls.product_A.id,
                            "name": "1 Product A",
                            "product_uom_id": cls.uom_unit.id,
                            "product_uom_qty": 1.0,
                        },
                    ),
                    (
                        0,
                        False,
                        {
                            "product_id": cls.product_B.id,
                            "name": "2 Product B",
                            "product_uom_id": cls.uom_unit.id,
                            "product_uom_qty": 1.0,
                        },
                    ),
                ]
            }
        )

        return res

    def test__compute_onchange_exemption(self):
        self.assertEqual(self.order.exemption_code, "1234")
        self.assertTrue(self.order.exemption_code_id)
        # code and number are none for not configured avatax company
        self.order.company_id = self.company2.id
        self.assertFalse(self.order.exemption_code)
        self.assertFalse(self.order.exemption_code_id)
        # code and number are computed for configured avatax company
        self.order.company_id = self.company.id
        self.assertEqual(self.order.exemption_code, "1234")
        self.assertTrue(self.order.exemption_code_id)

    def test_sale_order_tax_calculation(self):
        # Create an Avatax template tax (0%) for the company
        self.env["account.tax"].create(
            {
                "name": "Avatax 0%",
                "amount": 0.0,
                "is_avatax": True,
                "company_id": self.company.id,
                "amount_type": "percent",
                "type_tax_use": "sale",
            }
        )
        # Configure AvaTax on the company
        self.avatax.write(
            {
                "sale_calculate_tax": True,
            }
        )
        # Use our mock response
        mock_response = {
            "totalTax": 15.0,
            "lines": [
                {
                    "lineNumber": int(self.order.order_line[0].id),
                    "taxCalculated": 10.0,
                    "taxableAmount": 100.0,
                    "rate": 10.0,
                    "tax": 10.0,
                    "details": [
                        {
                            "rate": 0.1,
                            "tax": 10.0,
                        }
                    ],
                },
                {
                    "lineNumber": int(self.order.order_line[1].id),
                    "taxCalculated": 5.0,
                    "taxableAmount": 50.0,
                    "rate": 10.0,
                    "tax": 5.0,
                    "details": [
                        {
                            "rate": 0.1,
                            "tax": 5.0,
                        }
                    ],
                },
            ],
        }
        with self._capture_create_or_adjust_transaction(return_value=mock_response):
            self.order.avalara_compute_taxes()

        # Verify the taxes are correctly calculated/assigned
        self.assertEqual(self.order.tax_amount, 15.0)
        self.assertEqual(self.order.order_line[0].tax_amt, 10.0)
        self.assertEqual(self.order.order_line[1].tax_amt, 5.0)

    def test_compute_hide_exemption(self):
        self.avatax.hide_exemption = False
        self.order.invalidate_recordset(["hide_exemption"])
        self.assertFalse(self.order.hide_exemption)

        self.avatax.hide_exemption = True
        self.order.invalidate_recordset(["hide_exemption"])
        self.assertTrue(self.order.hide_exemption)

    def test_compute_onchange_exemption_non_exempt_partner(self):
        order = self.env["sale.order"].create(
            {
                "company_id": self.company.id,
                "partner_id": self.partner.id,
            }
        )
        self.assertFalse(order.exemption_code)
        self.assertFalse(order.exemption_code_id)

    def test_account_move_onchange_shipping_address(self):
        move = self.env["account.move"].new(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
            }
        )
        move.partner_shipping_id = self.partner
        move._onchange_partner_shipping_id()
        self.assertTrue(move.tax_on_shipping_address)

        move.partner_shipping_id = False
        move._onchange_partner_shipping_id()
        self.assertFalse(move.tax_on_shipping_address)
