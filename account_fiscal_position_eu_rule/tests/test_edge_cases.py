# Copyright 2026 Akretion
# @author Guillaume MASSON <guillaume.masson@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from .common import FiscalPositionEuRuleCommon


class TestEdgeCases(FiscalPositionEuRuleCommon):
    """Edge cases and fallback behaviours (EL-01 to EL-06)."""

    # -- EL-01 : VIES disabled -> fiscal_position_type drives B2B ---------------

    def test_el01_vies_disabled_fp_type_b2b(self):
        """EL-01 : VIES disabled, fiscal_position_type=b2b -> intra-Community."""
        fp = self._get_fp(self.partner_de_b2b, delivery=self.delivery_de_b2b)
        self.assertFpIsIntracomB2B(fp)

    # -- EL-02 : VAT present but buyer is B2C -> OSS ----------------------------

    def test_el02_vat_present_but_b2c_typed(self):
        """EL-02 : partner with VAT but fiscal_position_type=b2c.

        With account_fiscal_position_partner_type: fiscal_position_type=b2c
        overrides VAT presence -> B2C -> OSS DE.
        Without it: partner_de_b2b_vies_ko has only a VAT number -> treated
        as B2B -> intra-Community (correct fallback behaviour).
        """
        fp = self._get_fp(self.partner_de_b2b_vies_ko, delivery=self.delivery_de_b2c)
        if hasattr(self.env["res.partner"], "fiscal_position_type"):
            self.assertFpIsOssCountry(fp, self.country_de)
        else:
            self.assertFpIsIntracomB2B(fp)

    # -- EL-03 : no delivery -> falls back to partner country -------------------

    def test_el03_no_delivery_falls_back_to_partner_country(self):
        """EL-03 : delivery=None -> buyer country used as fallback."""
        fp = self._get_fp(self.partner_de_b2b, delivery=None)
        self.assertFpIsIntracomB2B(fp)

        fp = self._get_fp(self.partner_de_b2c, delivery=None)
        self.assertFpIsOssCountry(fp, self.country_de)

        fp = self._get_fp(self.partner_gb_b2b, delivery=None)
        self.assertFpIsExport(fp)

    # -- EL-04 : no optional modules -> VAT number fallback --------------------

    def test_el04_base_vat_not_installed_fallback_to_vat_field(self):
        """EL-04 : no vies_passed, no fiscal_position_type -> VAT presence."""
        FiscalPosition = type(self.env["account.fiscal.position"])

        def _is_b2b_no_modules(self_fp, partner):
            return bool(partner.vat)

        with patch.object(FiscalPosition, "_is_b2b_partner", _is_b2b_no_modules):
            fp = self._get_fp(self.partner_de_b2b, delivery=self.delivery_de_b2b)
            self.assertFpIsIntracomB2B(fp)

            fp = self._get_fp(self.partner_de_b2c, delivery=self.delivery_de_b2c)
            self.assertFpIsOssCountry(fp, self.country_de)

    # -- EL-05 : manual fiscal position on partner -----------------------------

    def test_el05_manual_fp_has_absolute_priority(self):
        """EL-05 : property_account_position_id set -> always returned as-is."""
        sentinel_fp = self.env["account.fiscal.position"].create(
            {
                "name": "Sentinel FP",
                "company_id": self.company_fr.id,
            }
        )
        self.partner_gb_b2b.property_account_position_id = sentinel_fp
        try:
            fp = self._get_fp(self.partner_gb_b2b, delivery=self.delivery_de_b2b)
            self.assertEqual(fp, sentinel_fp)
        finally:
            self.partner_gb_b2b.property_account_position_id = False

    # -- EL-06 : seller outside EU -> super() called with original args --------

    def test_el06_seller_outside_eu_falls_back_to_odoo_default(self):
        """EL-06 : seller outside EU -> module does not interfere.

        When the seller is outside the EU, our override must delegate
        immediately to super() with the original partner and delivery,
        without altering any arguments.

        We patch the Odoo-stock _get_fiscal_position by importing the base
        class directly. This avoids fragile __bases__[0] traversal that breaks
        when other modules (e.g. account_avatax_oca) also inherit the model.
        """
        company_us = self.env["res.company"].create(
            {
                "name": "Test Company US",
                "country_id": self.country_us.id,
            }
        )
        fp_us_export = self.env["account.fiscal.position"].create(
            {
                "name": "US Export",
                "company_id": company_us.id,
                "auto_apply": True,
            }
        )
        calls = []

        def recording_get_fp(self_fp, partner, delivery=None):
            calls.append({"partner": partner, "delivery": delivery})
            return fp_us_export

        from odoo.addons.account.models.partner import (
            AccountFiscalPosition as OdooBaseFP,
        )

        with patch.object(OdooBaseFP, "_get_fiscal_position", recording_get_fp):
            self.env["account.fiscal.position"].with_company(company_us).with_context(
                fp_eu_seller=company_us.partner_id,
            )._get_fiscal_position(
                self.partner_de_b2b,
                delivery=self.delivery_ie_b2b,
            )

        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["partner"], self.partner_de_b2b)
        self.assertEqual(calls[0]["delivery"], self.delivery_ie_b2b)
