# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.account_multi_vat.tests import common


class TestAccountMultiVatSale(common.CommonAccountMultiVat):
    @classmethod
    def setUpClass(cls):
        super(TestAccountMultiVatSale, cls).setUpClass()

        # MODELS
        cls.account_move_model = cls.env["account.move"]

        # INSTANCES
        cls.invoice_01 = cls.account_move_model.create(
            {
                "name": "Invoice 01",
                "partner_id": cls.partner_01.id,
                # 'account_id': self.account_receivable.id,
                "type": "out_invoice",
                # 'invoice_user_id': self.salesperson.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            # 'product_id': product.id,
                            "quantity": 1,
                            "price_unit": 1,
                            "name": "Invoice line 01",
                            # 'account_id': self.account_revenue.id,
                            # 'tax_ids': [(6, 0, (self.tax.id, self.retention_tax.id))],
                        },
                    )
                ],
            }
        )
        cls.partner_01.write(
            {
                "id_numbers": [
                    (
                        0,
                        0,
                        {
                            "name": cls.valid_vat,
                            "category_id": cls.partner_id_category_vat.id,
                            "partner_issued_id": cls.vat_partner_lu.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": cls.valid_vat_be,
                            "category_id": cls.partner_id_category_vat.id,
                            "partner_issued_id": cls.vat_partner_be.id,
                        },
                    ),
                ],
                "child_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Partner 01 BE",
                            "country_id": cls.country_be.id,
                            "type": "other",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Partner 01 LU",
                            "country_id": cls.country_lu.id,
                            "type": "other",
                        },
                    ),
                ],
            }
        )

    def test_01(self):
        """
        Data:
            - A partner with LU and BE VAT numbers
            - A draft invoice with no shipping address
        Test case:
            1. Set a LU address
            2. Set a BE address
        Expected result:
            1. LU VAT number of the customer set on the invoice
            2. BE VAT number of the customer set on the invoice
        """
        self.assertFalse(self.invoice_01.partner_shipping_id)
        self.assertFalse(self.invoice_01.customer_vat_partner_id)
        self.assertFalse(self.invoice_01.customer_vat)
        # 1
        self.invoice_01.partner_shipping_id = self.partner_01.child_ids.filtered(
            lambda p: p.country_id == self.country_lu
        )[0]
        self.assertEqual(self.invoice_01.customer_vat_partner_id, self.vat_partner_lu)
        self.assertEqual(self.invoice_01.customer_vat, self.valid_vat)
        # 2
        self.invoice_01.partner_shipping_id = self.partner_01.child_ids.filtered(
            lambda p: p.country_id == self.country_be
        )[0]
        self.assertEqual(self.invoice_01.customer_vat_partner_id, self.vat_partner_be)
        self.assertEqual(self.invoice_01.customer_vat, self.valid_vat_be)
