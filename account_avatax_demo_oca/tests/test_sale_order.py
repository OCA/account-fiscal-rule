# Copyright 2025 Kencove, Open Source Integrators
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import json
import logging
import os

from odoo.tests.common import tagged

from odoo.addons.account_avatax_oca.tests.common import TestAvataxCommon

_logger = logging.getLogger(__name__)


@tagged("-at_install", "post_install")
class TestAvataxSaleOrder(TestAvataxCommon):
    @classmethod
    def setUpClass(cls):
        res = super().setUpClass()

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

        cls.NT_product = cls.env["product.product"].create(
            {
                "name": "NT Product",
                "list_price": 100,
                "sale_ok": True,
                "default_code": "TEST-NT",
                "tax_code_id": cls.env.ref(
                    "account_avatax_oca.avatax_product_taxcodeNT"
                ).id,
            }
        )

        cls.taxed_product = cls.env["product.product"].create(
            {
                "name": "Taxed Product",
                "list_price": 33,
                "sale_ok": True,
            }
        )

        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
                "is_company": True,
                "street": "77 Santa Barbara Rd",
                "city": "Pleasant Hill",
                "state_id": cls.env.ref("base.state_us_5").id,
                "country_id": cls.env.ref("base.us").id,
                "zip": "94523",
            }
        )

        # Create sale order
        cls.order = cls.env["sale.order"].create(
            {
                "company_id": cls.company.id,
                "partner_id": cls.partner.id,
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
                            "product_id": cls.NT_product.id,
                            "name": "NT Product",
                            "product_uom": cls.uom_unit.id,
                            "product_uom_qty": 1.0,
                        },
                    ),
                    (
                        0,
                        False,
                        {
                            "product_id": cls.taxed_product.id,
                            "name": "Taxed Product",
                            "product_uom": cls.uom_unit.id,
                            "product_uom_qty": 1.0,
                        },
                    ),
                ]
            }
        )

        return res

    def read_json(self, file_name):
        module_path = os.path.dirname(__file__)
        file_path = os.path.join(module_path, file_name)
        with open(file_path) as file:
            data = json.load(file)
            return data

    def _prepare_so_response(self):
        so_response = self.read_json("SaleOrder_response.json")
        so_response["customerCode"] = self.partner.customer_code
        for line in so_response["lines"]:
            if line["description"] == "NT Product":
                line["lineNumber"] = self.order.order_line[0].id
                line["itemCode"] = "TEST-NT"
            elif line["description"] == "Taxed Product":
                line["lineNumber"] = self.order.order_line[1].id
                line["itemCode"] = f"ID:{self.taxed_product.id}"
        return so_response

    def _assert_tax_computation(self, captured):
        response_json = captured.mock_response.json()
        self.assertEqual(
            response_json["lines"][0]["lineNumber"], self.order.order_line[0].id
        )
        self.assertEqual(
            response_json["lines"][1]["lineNumber"], self.order.order_line[1].id
        )
        self.assertEqual(response_json["lines"][0]["itemCode"], "TEST-NT")
        self.assertEqual(
            response_json["lines"][1]["itemCode"], f"ID:{self.taxed_product.id}"
        )
        self.assertEqual(response_json["type"], "SalesOrder")
        self.assertEqual(response_json["customerCode"], self.partner.customer_code)
        self.assertEqual(self.order.amount_tax, 3.06)
        self.assertEqual(self.order.amount_tax, response_json["totalTax"])

        for order_line in self.order.order_line:
            tax_names = order_line.tax_id.mapped("name")
            if order_line.name == "NT Product":
                self.assertIn(
                    "AVATAX", tax_names, "AVATAX tax not found in Non-Tax Product"
                )
                self.assertEqual(order_line.tax_amt, 0)
            elif order_line.name == "Taxed Product":
                self.assertTrue(order_line.tax_id)
                self.assertNotIn(
                    "AVATAX", tax_names, "AVATAX tax found in Taxed Product"
                )
                self.assertEqual(order_line.tax_amt, 3.06)
                self.assertEqual(response_json["lines"][1]["tax"], order_line.tax_amt)

    def test_compute_taxes_for_quotation(self):
        so_response = self._prepare_so_response()
        with self._capture_create_or_adjust_transaction(
            return_value=so_response
        ) as captured:
            self.order._avatax_compute_tax()
            self._assert_tax_computation(captured)

    def test_compute_taxes_for_quotation_with_apply_args(self):
        so_response = self._prepare_so_response()
        with self._capture_create_or_adjust_transaction(
            return_value=so_response, apply_args=True
        ) as captured:
            self.order._avatax_compute_tax()
            self._assert_tax_computation(captured)
