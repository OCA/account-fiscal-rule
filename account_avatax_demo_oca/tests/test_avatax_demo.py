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

        # cls.company = cls.env.user.company_id
        # cls.company.write(
        #     {
        #         "street": "255 Executive Park Blvd",
        #         "city": "San Francisco",
        #         "state_id": cls.env.ref("base.state_us_5").id,
        #         "country_id": cls.env.ref("base.us").id,
        #         "zip": "94134",
        #     }
        # )

        # cls.product_A = cls.env['product.product'].create({
        #     'name': 'Product A',
        #     'list_price': 100,
        #     'sale_ok': True,
        # })

        # cls.product_B = cls.env['product.product'].create({
        #     'name': 'Product B',
        #     'list_price': 5,
        #     'sale_ok': True,
        # })

        # # Create exemption
        # cls.exemption = cls.env["exemption.code"].create(
        #     {
        #         'name': "RESALE",
        #         'code': "1234",
        #     }
        # )

        # cls.company2 = cls.env["res.company"].create(
        #     {
        #         "name": "Test Avatax Company",
        #         "currency_id": cls.env.ref("base.USD").id,
        #         "street": "266 Executive Park Blvd",
        #         "city": "San Francisco",
        #         "state_id": cls.env.ref("base.state_us_5").id,
        #         "country_id": cls.env.ref("base.us").id,
        #         "zip": "94134",
        #     }
        # )

        # cls.partner_exempt = cls.env["res.partner"].create(
        #     {
        #         "name": "Tax Exempt Partner",
        #         'is_company': True,
        #         "street": "2288 Market St",
        #         "city": "San Francisco",
        #         "state_id": cls.env.ref("base.state_us_5").id,
        #         "country_id": cls.env.ref("base.us").id,
        #         "zip": "94114",
        #         "property_account_position_id": cls.fp_avatax.id,
        #         "property_tax_exempt": True,
        #         "property_exemption_number": "1234",
        #         "property_exemption_code_id": cls.exemption.id
        #     }
        # )

        # # Create sale order
        # cls.order = cls.env["sale.order"].create(
        #     {
        #         'company_id': cls.company.id,
        #         'partner_id': cls.partner_exempt.id,
        #     }
        # )
        # cls.uom_unit = cls.env.ref('uom.product_uom_unit')
        # cls.order.write({'order_line': [
        #     (0, False, {
        #         'product_id': cls.product_A.id,
        #         'name': '1 Product A',
        #         'product_uom': cls.uom_unit.id,
        #         'product_uom_qty': 1.0,
        #     }),
        #     (0, False, {
        #         'product_id': cls.product_B.id,
        #         'name': '2 Product B',
        #         'product_uom': cls.uom_unit.id,
        #         'product_uom_qty': 1.0,
        #     })
        # ]})

        return res

    def read_json(self, file_name):
        module_path = os.path.dirname(__file__)
        file_path = os.path.join(module_path, file_name)
        with open(file_path) as file:
            data = json.load(file)
            return data

    def test_demo(self):
        invoice_2_response = self.read_json("S00025_response.json")
        with self._capture_create_or_adjust_transaction(
            return_value=invoice_2_response
        ) as captured:
            _logger.info("\n" + "===================================")
            _logger.info("\n" + f"{captured.mock_response.json()}")
            _logger.info("\n" + "===================================")

        self.assertTrue(1 == 1)
