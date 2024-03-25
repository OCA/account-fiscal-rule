from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestAccountMultiForeignVat(TransactionCase):
    def setUp(self):
        super().setUp()
        self.country_dk = self.env["res.country"].search([("code", "=", "DK")])
        self.valid_vat_dk = "DK12345674"
        self.invalid_vat_dk = "INVALID VAT"
        self.fiscal_position_1 = self.env["account.fiscal.position"].create(
            {
                "name": "Denmark Fiscal Position 1",
                "country_id": self.country_dk.id,
                "foreign_vat": self.valid_vat_dk,
            }
        )
        self.fiscal_position_2 = self.env["account.fiscal.position"].create(
            {
                "name": "Denmark Fiscal Position 2",
                "country_id": self.country_dk.id,
                "foreign_vat": self.valid_vat_dk,
            }
        )

    def test_account_multi_foreign_vat(self):
        # Check that 2 fiscal position are created successfully
        self.assertTrue(self.fiscal_position_1)
        self.assertTrue(self.fiscal_position_2)

        # Check that both fiscal positions have the same foreign_vat and country_id
        self.assertEqual(
            self.fiscal_position_2.foreign_vat, self.fiscal_position_1.foreign_vat
        )
        self.assertEqual(
            self.fiscal_position_2.country_id, self.fiscal_position_1.country_id
        )

        # Check that you cannot enter an invalid vat
        with self.assertRaises(ValidationError):
            self.env["account.fiscal.position"].create(
                {
                    "name": "Denmark Fiscal Position 3",
                    "country_id": self.country_dk.id,
                    "foreign_vat": self.invalid_vat_dk,
                }
            )
