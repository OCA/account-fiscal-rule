# Copyright 2025 Moduon Team S.L. <info@moduon.team>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests import Form

from odoo.addons.base.tests.common import BaseCommon


class TestFiscalPositionViesWarning(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.company.vat_check_vies = True
        cls.partner_vies = cls.env["res.partner"].create(
            {
                "name": "Belgium Partner",
                "country_id": cls.env.ref("base.be").id,
                "vat": "BE0477472701",
                "vies_valid": True,
            }
        )
        cls.partner_not_vies = cls.env["res.partner"].create(
            {
                "name": "NL Partner",
                "country_id": cls.env.ref("base.nl").id,
                "vat": "NL946186650B01",
                "vies_valid": False,
            }
        )
        cls.fp_intra_community = cls.env["account.fiscal.position"].create(
            {
                "name": "Intra-community",
                "auto_apply": True,
                "is_show_vies_warning": True,
            }
        )
        cls.fp_other = cls.env["account.fiscal.position"].create(
            {
                "name": "Other Fiscal Position",
                "auto_apply": True,
            }
        )

    def _create_invoice(self, partner, fiscal_position):
        return self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": partner.id,
                "invoice_date": "2025-09-04",
                "date": "2025-09-04",
                "fiscal_position_id": fiscal_position.id,
                "invoice_line_ids": [
                    Command.create({"name": "line1", "price_unit": 110.0}),
                ],
            }
        )

    def test_show_vies_warning(self):
        with self.assertRaises(ValidationError):
            with Form(self.partner_not_vies) as form:
                form.property_account_position_id = self.fp_intra_community
                form.save()
        with Form(self.partner_not_vies) as form:
            form.property_account_position_id = self.fp_other
            form.save()
        with Form(self.partner_vies) as form:
            form.property_account_position_id = self.fp_intra_community
            form.save()
        self.assertEqual(
            self.partner_vies.property_account_position_id,
            self.fp_intra_community,
            "It's incorrect fiscal position",
        )
        with Form(self.partner_vies) as form:
            form.property_account_position_id = self.fp_other
            form.save()
        self.assertEqual(
            self.partner_vies.property_account_position_id,
            self.fp_other,
            "It's incorrect fiscal position",
        )

    def test_set_intra_community_fiscal_position_to_partner_not_vies(self):
        """Test set the intra-community fiscal position on the invoice if the partner
        fails VIES validation"""
        with self.assertRaises(ValidationError):
            invoice = self._create_invoice(
                self.partner_not_vies, self.fp_intra_community
            )
            invoice.action_post()

    def test_set_intra_community_fiscal_position_to_partner_vies(self):
        """Test set the intra-community fiscal position on the invoice if the partner
        passes VIES validation"""
        invoice = self._create_invoice(self.partner_vies, self.fp_intra_community)
        invoice.action_post()
        self.assertEqual(invoice.fiscal_position_id.id, self.fp_intra_community.id)

    def test_set_other_fiscal_position_to_partner_not_vies(self):
        """Test set an other fiscal position on the invoice if the partner
        fails VIES validation"""
        invoice = self._create_invoice(self.partner_not_vies, self.fp_other)
        invoice.action_post()
        self.assertEqual(invoice.fiscal_position_id.id, self.fp_other.id)

    def test_set_other_fiscal_position_to_partner_vies(self):
        """Test set an other fiscal position on the invoice if the partner
        passes VIES validation"""
        invoice = self._create_invoice(self.partner_vies, self.fp_other)
        invoice.action_post()
        self.assertEqual(invoice.fiscal_position_id.id, self.fp_other.id)

    def test_vies_warning_visibility(self):
        self.fp_other.auto_apply = True
        self.fp_other.vat_required = True
        self.env.company.vat_check_vies = False
        self.fp_other._compute_visible_vies_warning()
        self.assertFalse(self.fp_other.is_visible_show_vies_warning)

        self.fp_other.auto_apply = True
        self.fp_other.vat_required = True
        self.env.company.vat_check_vies = True
        self.fp_other._compute_visible_vies_warning()
        self.assertTrue(self.fp_other.is_visible_show_vies_warning)

        self.fp_other.auto_apply = True
        self.fp_other.vat_required = False
        self.fp_other._compute_visible_vies_warning()
        self.assertFalse(self.fp_other.is_visible_show_vies_warning)

        self.env.company.vat_check_vies = False
        self.fp_intra_community._compute_visible_vies_warning()
        self.assertFalse(self.fp_intra_community.is_visible_show_vies_warning)
