# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon

from . import common


class TestAccountMultiVat(common.CommonAccountMultiVat):
    def test_01(self):
        """
        Data:
            - A tax administration partner
            - A partner with no VAT
        Test case:
            - Set an invalid VAT number on the partner, via partner identification
            - partner_issued_id is set and is a tax administration
        Expected result:
            - ValidationError is raised
        """
        self.assertFalse(self.partner_01.has_vat)
        with self.assertRaises(ValidationError):
            self.partner_01.id_numbers = [
                (
                    0,
                    0,
                    {
                        "name": self.invalid_vat,
                        "category_id": self.partner_id_category_vat.id,
                        "partner_issued_id": self.vat_partner_lu.id,
                    },
                )
            ]

    def test_02(self):
        """
        Data:
            - A tax administration partner
            - A partner with no VAT
        Test case:
            - Set an valid VAT number on the partner, via partner identification
            - partner_issued_id is set and is a tax administration
        Expected result:
            - The VAT number is correctly set
            - has_vat is True on the partner
        """
        self.partner_01.id_numbers = [
            (
                0,
                0,
                {
                    "name": self.valid_vat,
                    "category_id": self.partner_id_category_vat.id,
                    "partner_issued_id": self.vat_partner_lu.id,
                },
            )
        ]
        self.assertEqual(self.partner_01.id_numbers.name, self.valid_vat)
        self.assertTrue(self.partner_01.has_vat)

    def test_03(self):
        """
        Data:
            - A tax administration partner
            - A partner with no VAT
        Test case:
            - Set an valid VAT number on the partner, via partner identification
            - partner_issued_id is set and is not a tax administration
        Expected result:
            - ValidationError is raised
        """
        self.vat_partner_lu.is_tax_administration = False
        with self.assertRaises(ValidationError):
            self.partner_01.id_numbers = [
                (
                    0,
                    0,
                    {
                        "name": self.valid_vat,
                        "category_id": self.partner_id_category_vat.id,
                        "partner_issued_id": self.vat_partner_lu.id,
                    },
                )
            ]

    def test_04(self):
        """
        Data:
            - A tax administration partner
            - A partner with no VAT
        Test case:
            - Set an valid VAT number on the partner, via partner identification
            - no partner_issued_id is set
        Expected result:
            - ValidationError is raised
        """
        with self.assertRaises(ValidationError):
            self.partner_01.id_numbers = [
                (
                    0,
                    0,
                    {
                        "name": self.valid_vat,
                        "category_id": self.partner_id_category_vat.id,
                        "partner_issued_id": False,
                    },
                )
            ]

    def test_05(self):
        """
        Data:
            - A tax administration partner
            - A partner with no VAT
        Test case:
            - Set a dummy identification category
            - Set a dummy identification value, via partner identification
            - no partner_issued_id is set
        Expected result:
            - The value is correctly set
            - has_vat is False on the partner
        """
        self.partner_01.id_numbers = [
            (
                0,
                0,
                {
                    "name": self.invalid_vat,
                    "category_id": self.partner_id_category_dummy.id,
                    "partner_issued_id": False,
                },
            )
        ]
        self.assertEqual(self.partner_01.id_numbers.name, self.invalid_vat)
        self.assertFalse(self.partner_01.has_vat)

    def test_06(self):
        """
        Data:
            - A tax administration partner
            - A partner with no VAT
        Test case:
            - Create a new partner identification number with VAT category
        Expected result:
            - The domain on the partner_issued_id must show only tax administrations
        """
        new_vat_partner_identification = self.partner_id_number_model.new(
            {"category_id": self.partner_id_category_vat.id}
        )
        onchange_res = new_vat_partner_identification._onchange_category_id_multi_vat()
        onchange_domain = onchange_res.get("domain", {}).get("partner_issued_id", [])
        domain_res = self.partner_model.search(onchange_domain)
        self.assertEqual(len(domain_res), 2)
        self.assertIn(self.vat_partner_be, domain_res)
        self.assertIn(self.vat_partner_lu, domain_res)

    def test_07(self):
        """
        Data:
            - A tax administration partner
            - A partner with no VAT
        Test case:
            - Create two new partner identification number with VAT category, for the
              same tax administration
        Expected result:
            - ValidationError is raised
        """
        with self.assertRaises(ValidationError):
            self.partner_01.id_numbers = [
                (
                    0,
                    0,
                    {
                        "name": self.valid_vat,
                        "category_id": self.partner_id_category_vat.id,
                        "partner_issued_id": self.vat_partner_lu.id,
                    },
                ),
                (
                    0,
                    0,
                    {
                        "name": self.valid_vat,
                        "category_id": self.partner_id_category_vat.id,
                        "partner_issued_id": self.vat_partner_lu.id,
                    },
                ),
            ]

    def test_08(self):
        """
        Data:
            - A partner with a two VAT numbers set via partner identification
              (LU and BE)
        Test case:
            1. Search the VAT number for BE
            2. Search the VAT number for LU
            3. Search the VAT number for another country
        Expected result:
            1. BE VAT number is returned
            1. LU VAT number is returned
            1. No VAT number is returned
        """
        self.partner_01.id_numbers = [
            (
                0,
                0,
                {
                    "name": self.valid_vat,
                    "category_id": self.partner_id_category_vat.id,
                    "partner_issued_id": self.vat_partner_lu.id,
                },
            ),
            (
                0,
                0,
                {
                    "name": self.valid_vat_be,
                    "category_id": self.partner_id_category_vat.id,
                    "partner_issued_id": self.vat_partner_be.id,
                },
            ),
        ]
        lu_vat_number = self.partner_01._get_vat_number_for_administration(
            self.vat_partner_lu
        )
        self.assertEqual(lu_vat_number, self.valid_vat)
        lu_vat_number = self.partner_01._get_vat_number_for_country(self.country_lu)
        self.assertEqual(lu_vat_number, self.valid_vat)
        be_vat_number = self.partner_01._get_vat_number_for_administration(
            self.vat_partner_be
        )
        self.assertEqual(be_vat_number, self.valid_vat_be)
        be_vat_number = self.partner_01._get_vat_number_for_country(self.country_be)
        self.assertEqual(be_vat_number, self.valid_vat_be)
        no_vat_number = self.partner_01._get_vat_number_for_administration()
        self.assertFalse(no_vat_number)
        no_vat_number = self.partner_01._get_vat_number_for_country(
            self.env["res.country"].browse()
        )
        self.assertFalse(no_vat_number)

    def test_09(self):
        """
        Data:
            - A tax administration partner for BE
        Test case:
            - Try to create a tax administration partner for the same country
        Expected result:
            - ValidationError is raised
        """
        with self.assertRaises(ValidationError):
            self.partner_model.create(
                {
                    "name": "LU Tax Administration duplicate",
                    "is_tax_administration": True,
                    "country_id": self.country_lu.id,
                }
            )

    def test_10(self):
        """
        Data:
            - No tax administration for IT
        Test case:
            1. Try to create a tax administration with no country
            2. Try to create a tax administration for IT
        Expected result:
            1. ValidationError is raised
            2. Tax administration created
        """
        with self.assertRaises(ValidationError):
            self.partner_model.create(
                {"name": "IT Tax Administration", "is_tax_administration": True}
            )
        self.assertTrue(
            self.partner_model.create(
                {
                    "name": "IT Tax Administration",
                    "is_tax_administration": True,
                    "country_id": self.country_it.id,
                }
            )
        )

    def test_11(self):
        """
        Data:
            - A tax with no tax administration
        Test case:
            - Set a tax administration on the tax, which has a different country
        Expected result:
            - The country of the tax administration is set on the tax
        """
        tax = self.tax_model.search([], limit=1)
        tax_country = tax.country_id
        self.assertNotEqual(tax_country, self.vat_partner_lu.country_id)
        tax.vat_partner_id = self.vat_partner_lu
        self.assertEqual(tax.country_id, self.vat_partner_lu.country_id)
        tax_repartition_lines = (
            tax.invoice_repartition_line_ids | tax.refund_repartition_line_ids
        )
        for tax_repartition_line in tax_repartition_lines:
            self.assertEqual(
                tax_repartition_line.country_id, self.vat_partner_lu.country_id
            )

    def test_12(self):
        """
        Data:
            - A tax with BE tax administration and BE tags
        Test case:
            1. Try to change the tax administration to LU tax administration without
               changing the tags
            2. Try to change the tax administration to LU after removing the tags
        Expected result:
            1. ValidationError is raised
            2. Tax administration changed
        """
        tax = self.tax_model.search([], limit=1)
        tax.vat_partner_id = self.vat_partner_be
        tax.invoice_repartition_line_ids.write(
            {"tag_ids": [(6, 0, self.account_tag_be_01.ids)]}
        )
        # 1
        with self.assertRaises(ValidationError):
            tax.vat_partner_id = self.vat_partner_lu
        # 2
        tax.invoice_repartition_line_ids.write({"tag_ids": [(5,)]})
        tax.vat_partner_id = self.vat_partner_lu
        self.assertEqual(tax.country_id, self.vat_partner_lu.country_id)

    def test_13(self):
        """
        Data:
            - A partner with no VAT
        Test case:
            - Set a direct VAT number on the partner (not via partner identification)
        Expected result:
            - has_vat is True (the VAT id category exists and the partner has a vat)
        """
        self.assertFalse(self.partner_01.has_vat)
        self.partner_01.vat = self.valid_vat
        self.assertTrue(self.partner_01.has_vat)

    def test_14(self):
        """
        Data:
            - A tax administration partner for LU
        Test case:
            - Set the tax administration back to a regular partner, then create a
              second tax administration for the same country
        Expected result:
            - No ValidationError is raised once the first one is no longer a tax
              administration
        """
        self.vat_partner_lu.is_tax_administration = False
        # Now there is no LU tax administration anymore, creating one must work
        new_lu_admin = self.partner_model.create(
            {
                "name": "LU Tax Administration 2",
                "is_tax_administration": True,
                "country_id": self.country_lu.id,
            }
        )
        self.assertTrue(new_lu_admin.is_tax_administration)


@tagged("post_install", "-at_install")
class TestAccountMultiVatInvoice(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.country_lu = cls.env.ref("base.lu")
        cls.country_be = cls.env.ref("base.be")
        cls.valid_vat = "LU11180925"
        cls.valid_vat_be = "BE0477472701"
        cls.partner_id_category_vat = cls.env.ref(
            "account_multi_vat.partner_id_category_vat"
        )
        cls.vat_partner_lu = cls.env["res.partner"].create(
            {
                "name": "LU Tax Administration",
                "is_tax_administration": True,
                "country_id": cls.country_lu.id,
            }
        )
        cls.vat_partner_be = cls.env["res.partner"].create(
            {
                "name": "BE Tax Administration",
                "is_tax_administration": True,
                "country_id": cls.country_be.id,
            }
        )
        # Give the invoiced partner a LU VAT number issued by the LU administration
        cls.partner_a.id_numbers = [
            (
                0,
                0,
                {
                    "name": cls.valid_vat,
                    "category_id": cls.partner_id_category_vat.id,
                    "partner_issued_id": cls.vat_partner_lu.id,
                },
            )
        ]

    def test_customer_vat_on_customer_invoice(self):
        """
        Data:
            - A customer with a LU VAT number issued by the LU tax administration
        Test case:
            - Create a customer invoice with the LU tax administration set
        Expected result:
            - customer_vat is the LU VAT number of the customer
        """
        invoice = self._create_invoice(
            move_type="out_invoice",
            partner_id=self.partner_a.id,
            customer_vat_partner_id=self.vat_partner_lu.id,
        )
        self.assertEqual(invoice.customer_vat, self.valid_vat)

    def test_customer_vat_without_matching_number(self):
        """
        Data:
            - A customer with a LU VAT number only
        Test case:
            - Create a customer invoice with the BE tax administration set (no BE
              number on the customer)
        Expected result:
            - customer_vat falls back on the partner's own vat
        """
        invoice = self._create_invoice(
            move_type="out_invoice",
            partner_id=self.partner_a.id,
            customer_vat_partner_id=self.vat_partner_be.id,
        )
        self.assertEqual(invoice.customer_vat, self.partner_a.vat or False)

    def test_customer_vat_on_vendor_bill_is_false(self):
        """
        Data:
            - A partner with a LU VAT number
        Test case:
            - Create a vendor bill with the LU tax administration set
        Expected result:
            - customer_vat is not computed on non-customer documents
        """
        bill = self._create_invoice(
            move_type="in_invoice",
            partner_id=self.partner_a.id,
            customer_vat_partner_id=self.vat_partner_lu.id,
        )
        self.assertFalse(bill.customer_vat)

    def test_customer_vat_recomputed_on_administration_change(self):
        """
        Data:
            - A customer invoice without tax administration
        Test case:
            - Set the LU tax administration on the invoice
        Expected result:
            - customer_vat is recomputed to the LU VAT number
        """
        invoice = self._create_invoice(
            move_type="out_invoice",
            partner_id=self.partner_a.id,
        )
        invoice.customer_vat_partner_id = self.vat_partner_lu
        self.assertEqual(invoice.customer_vat, self.valid_vat)

    def test_reversal_copies_customer_vat(self):
        """
        Data:
            - A posted customer invoice with a LU tax administration and customer_vat
        Test case:
            - Reverse the invoice through the reversal wizard
        Expected result:
            - The reversal move keeps the customer tax administration and customer_vat
        """
        invoice = self._create_invoice(
            move_type="out_invoice",
            partner_id=self.partner_a.id,
            customer_vat_partner_id=self.vat_partner_lu.id,
            post=True,
        )
        self.assertEqual(invoice.customer_vat, self.valid_vat)
        reversal_wizard = (
            self.env["account.move.reversal"]
            .with_context(active_model="account.move", active_ids=invoice.ids)
            .create({"journal_id": invoice.journal_id.id})
        )
        reversal_wizard.reverse_moves()
        reversal_move = reversal_wizard.new_move_ids
        self.assertEqual(reversal_move.customer_vat_partner_id, self.vat_partner_lu)
        self.assertEqual(reversal_move.customer_vat, self.valid_vat)
