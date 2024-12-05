import logging

from odoo.exceptions import UserError
from odoo.tests.common import tagged

from .common import TestAvataxCommon
from .mocked_invoice_1_response import response as response_invoice_1

_logger = logging.getLogger(__name__)


@tagged("-at_install", "post_install")
class TestAccountAvalaraInternal(TestAvataxCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_mocked_response(self):
        # mocking response with actual invoice line ids
        self.assertNotEqual(response_invoice_1["lines"][0]["lineNumber"], "229")
        first_line_id = self.invoice.invoice_line_ids[:1]

        with self._capture_create_or_adjust_transaction(
            return_value=self.invoice_1_response
        ) as captured:
            mock_response = captured._capture_create_or_adjust_transaction(
                model={"key": "value"}
            )
            self.assertNotEqual(
                self.invoice_1_response["lines"][0]["lineNumber"],
                "229",
            )
            self.assertEqual(
                self.invoice_1_response["lines"][0]["lineNumber"],
                first_line_id.id,
            )
            self.assertEqual(
                mock_response.json()["lines"][0]["lineNumber"],
                first_line_id.id,
            )

    def test_ping(self):
        # test not authenticated user
        with self._capture_ping() as captured:
            with self.assertRaises(UserError):
                self.env.user.lang = "en_US"
                res = self.avatax.ping()

        response = {
            "key": "connection to avalara is successful!",
            "authenticated": True,
        }
        # test authenticated user
        with self._capture_ping(return_value=response) as captured:
            # mocked method is not called and no returned vaules
            try:
                self.assertDictEqual(response, captured.mock_response.json())
            except AssertionError as e:
                _logger.info(f"AssertionError: \n===========> {e}")
            # mocked method is called and return value
            res = self.avatax.ping()
            self.assertTrue(res)
            # inserted return value is equal to returned value from mocked method
            self.assertDictEqual(response, captured.mock_response.json())

    def test__avatax_compute_tax(self):
        first_line_id = self.invoice.invoice_line_ids[:1]
        # test no tax records yet for invoice lines
        self.assertFalse(first_line_id.tax_ids)

        # Without applying arguments
        with self._capture_create_or_adjust_transaction(
            return_value=self.invoice_1_response
        ) as captured:
            tax_result = self.invoice._avatax_compute_tax()
            # test tax record is created for invoice lines
            self.assertEqual(
                captured.mock_response.json()["lines"][0]["lineNumber"],
                f"{self.invoice.invoice_line_ids[:1].id}",
            )
            self.assertEqual(
                captured.mock_response.json()["lines"][0]["itemCode"], "false"
            )
            self.assertEqual(captured.mock_response.json()["description"], "")
            self.assertEqual(captured.mock_response.json()["type"], "SalesInvoice")
            self.assertTrue(
                captured.mock_response.json()["customerCode"] == "CUST123456"
            )
            self.assertTrue(first_line_id.tax_ids)
            self.assertEqual(tax_result["totalTax"], 6.54)
            self.assertEqual(self.invoice_1_response["totalTax"], 6.54)
            self.assertEqual(tax_result["totalTaxable"], 90.0)
            self.assertEqual(self.invoice_1_response["totalTaxable"], 90.0)

        # With applying arguments
        with self._capture_create_or_adjust_transaction(
            return_value=self.invoice_1_response, apply_args=True
        ) as captured:
            tax_result = self.invoice._avatax_compute_tax()
            # test tax record is created for invoice lines
            self.assertEqual(
                captured.mock_response.json()["lines"][0]["lineNumber"],
                self.invoice.invoice_line_ids[:1].id,
            )
            self.assertEqual(
                captured.mock_response.json()["lines"][0]["itemCode"], "ID:0"
            )
            self.assertEqual(captured.mock_response.json()["description"], "Draft")
            self.assertEqual(captured.mock_response.json()["type"], "SalesOrder")
            self.assertTrue(
                captured.mock_response.json()["customerCode"] != "CUST123456"
            )
            self.assertTrue(first_line_id.tax_ids)
            self.assertEqual(tax_result["totalTax"], 6.54)
            self.assertEqual(self.invoice_1_response["totalTax"], 6.54)
            self.assertEqual(tax_result["totalTaxable"], 90.0)
            self.assertEqual(self.invoice_1_response["totalTaxable"], 90.0)

    def test_avatax_compute_taxes(self):
        with self._capture_create_or_adjust_transaction(
            return_value=self.invoice_1_response
        ):
            returne_true = self.invoice.avatax_compute_taxes()
            self.assertTrue(returne_true)
