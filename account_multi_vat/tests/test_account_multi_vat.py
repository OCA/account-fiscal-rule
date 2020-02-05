# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError

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
