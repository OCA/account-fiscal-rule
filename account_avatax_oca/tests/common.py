import socket
from contextlib import contextmanager
from unittest.mock import Mock, patch

from avalara import AvataxClient

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase

from .mocked_invoice_1_response import generate_response as generate_response_invoice_1

NOTHING = object()


class TestAvataxCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        res = super().setUpClass()
        cls.appname = "Odoo 17 - Open Source Integrators/OCA"
        cls.version = "a0o5a000007SPdsAAG"
        cls.hostname = socket.gethostname()
        url = ""
        cls.environment = (
            "sandbox" if "sandbox" in url or "development" in url else "production"
        )
        try:
            cls.client = AvataxClient(
                cls.appname, cls.version, cls.hostname, cls.environment
            )
        except NameError as exc:
            raise UserError(
                cls.env._(
                    "AvataxClient is not available in your system. "
                    "Please contact your system administrator "
                    "to 'pip3 install Avalara'"
                )
            ) from exc

        # Update address of company
        company = cls.env.user.company_id
        company.write(
            {
                "street": "255 Executive Park Blvd",
                "city": "San Francisco",
                "state_id": cls.env.ref("base.state_us_5").id,
                "country_id": cls.env.ref("base.us").id,
                "zip": "94134",
            }
        )

        cls.fp_avatax = cls.env["account.fiscal.position"].create(
            {
                "name": "Avatax",
                "is_avatax": True,
            }
        )

        # Create partner with correct US address
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Demo Sale Partner",
                "street": "2288 Market St",
                "city": "San Francisco",
                "state_id": cls.env.ref("base.state_us_5").id,
                "country_id": cls.env.ref("base.us").id,
                "zip": "94114",
                "property_account_position_id": cls.fp_avatax.id,
            }
        )

        cls.invoice = cls.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": cls.partner.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {"name": "Demo Invoice Line", "price_unit": 10, "quantity": 20},
                    )
                ],
            }
        )
        cls.avatax = cls.env.ref("account_avatax_oca.avatax_api_configuraation")
        cls.invoice_1_response = dict(
            generate_response_invoice_1(cls.invoice.invoice_line_ids)
        )

        return res

    @classmethod
    @contextmanager
    def _capture_create_or_adjust_transaction(
        cls, return_value=NOTHING, return_func=NOTHING, apply_args=False
    ):
        class Capture:
            mock_response = Mock()
            val = None

            def _capture_create_or_adjust_transaction(cls, model, include=None):
                cls.val = model
                if return_value is NOTHING:
                    cls.mock_response.json.return_value = return_func(model)
                else:
                    cls.mock_response.json.return_value = return_value
                if apply_args:
                    # Apply the real passed args and return them in the mocked response
                    cls.mock_response.json()["description"] = model[
                        "createTransactionModel"
                    ]["description"]
                    cls.mock_response.json()["type"] = model["createTransactionModel"][
                        "type"
                    ]
                    cls.mock_response.json()["code"] = model["createTransactionModel"][
                        "code"
                    ]
                    cls.mock_response.json()["date"] = model["createTransactionModel"][
                        "date"
                    ]
                    cls.mock_response.json()["salespersonCode"] = model[
                        "createTransactionModel"
                    ]["salespersonCode"]
                    cls.mock_response.json()["customerCode"] = model[
                        "createTransactionModel"
                    ]["customerCode"]
                    cls.mock_response.json()["lines"][0]["itemCode"] = model[
                        "createTransactionModel"
                    ]["lines"][0]["itemCode"]
                    cls.mock_response.json()["lines"][0]["taxCode"] = model[
                        "createTransactionModel"
                    ]["lines"][0]["taxCode"]
                    cls.mock_response.json()["lines"][0]["lineNumber"] = model[
                        "createTransactionModel"
                    ]["lines"][0]["number"]
                    cls.mock_response.json()["lines"][0]["description"] = model[
                        "createTransactionModel"
                    ]["lines"][0]["description"]
                    cls.mock_response.json()["lines"][0]["quantity"] = model[
                        "createTransactionModel"
                    ]["lines"][0]["quantity"]
                    cls.mock_response.json()["lines"][0]["lineAmount"] = model[
                        "createTransactionModel"
                    ]["lines"][0]["amount"]
                return cls.mock_response

        capture = Capture()
        with patch(
            "avalara.client_methods.Mixin.create_or_adjust_transaction",
            capture._capture_create_or_adjust_transaction,
        ):
            yield capture

    @classmethod
    @contextmanager
    def _capture_ping(cls, return_value=NOTHING):
        class Capture:
            mock_response = Mock()

            def _capture_ping(cls):
                if return_value is NOTHING:
                    default_response = {"key": "value"}
                    cls.mock_response.json.return_value = default_response
                else:
                    cls.mock_response.json.return_value = return_value
                return cls.mock_response

        capture = Capture()
        with patch("avalara.client_methods.Mixin.ping", capture._capture_ping):
            yield capture
