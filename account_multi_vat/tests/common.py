# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class CommonAccountMultiVat(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(CommonAccountMultiVat, cls).setUpClass()

        # MODELS
        cls.account_tag_model = cls.env["account.account.tag"]
        cls.partner_model = cls.env["res.partner"]
        cls.partner_id_category_model = cls.env["res.partner.id_category"]
        cls.partner_id_number_model = cls.env["res.partner.id_number"]
        cls.tax_model = cls.env["account.tax"]

        # INSTANCES
        cls.partner_01 = cls.partner_model.search([("vat", "=", False)], limit=1)
        cls.valid_vat = "LU11180925"
        cls.invalid_vat = "LU11180924"
        cls.valid_vat_be = "BE0477472701"
        cls.country_lu = cls.env.ref("base.lu")
        cls.country_be = cls.env.ref("base.be")
        cls.country_it = cls.env.ref("base.it")
        cls.vat_partner_lu = cls.partner_model.create(
            {
                "name": "LU Tax Administration",
                "is_tax_administration": True,
                "country_id": cls.country_lu.id,
            }
        )
        cls.vat_partner_be = cls.partner_model.create(
            {
                "name": "BE Tax Administration",
                "is_tax_administration": True,
                "country_id": cls.country_be.id,
            }
        )
        cls.partner_id_category_vat = cls.env.ref(
            "account_multi_vat.partner_id_category_vat"
        )
        cls.partner_id_category_dummy = cls.partner_id_category_model.create(
            {
                "name": "Dummy ID category",
                "code": "TEST",
                "validation_code": "failed = False",
            }
        )
        cls.account_tag_be_01 = cls.account_tag_model.create(
            {
                "name": "Account tag BE 01",
                "applicability": "taxes",
                "country_id": cls.country_be.id,
            }
        )
        cls.account_tag_lu_01 = cls.account_tag_model.create(
            {
                "name": "Account tag LU 01",
                "applicability": "taxes",
                "country_id": cls.country_lu.id,
            }
        )
