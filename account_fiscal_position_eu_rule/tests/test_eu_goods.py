# Copyright 2026 Akretion
# @author Guillaume MASSON <guillaume.masson@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from .common import FiscalPositionEuRuleCommon


class TestEuGoods(FiscalPositionEuRuleCommon):
    """Fiscal position resolution for physical goods — EU seller.

    Test IDs follow the decision matrix in readme/DESCRIPTION.rst.
    Each test is run with typed delivery addresses (fiscal_position_type
    set when account_fiscal_position_partner_type is installed) to ensure
    correct behaviour regardless of which optional modules are present.
    """

    # ── G-01/02/03/04 : buyer outside EU ─────────────────────────────────────

    def test_g01_export_non_eu_b2b_delivery_outside_eu(self):
        """G-01 : FR seller, GB B2B buyer, delivery outside EU → export 0%."""
        fp = self._get_fp(self.partner_gb_b2b, delivery=None)
        self.assertFpIsExport(fp)

    def test_g02_export_non_eu_b2b_delivery_seller_country(self):
        """G-02 : FR seller, GB B2B buyer, delivery in FR → export 0%."""
        fp = self._get_fp(self.partner_gb_b2b, delivery=self.delivery_fr_b2b)
        self.assertFpIsExport(fp)

    def test_g03_export_non_eu_b2b_delivery_other_eu(self):
        """G-03 : FR seller, GB B2B buyer, delivery in IE → export 0%.

        Core dropship case: delivery is in EU but buyer is outside EU.
        """
        fp = self._get_fp(self.partner_gb_b2b, delivery=self.delivery_ie_b2c)
        self.assertFpIsExport(fp)

    def test_g04_export_non_eu_b2c_delivery_outside_eu(self):
        """G-04 : FR seller, non-EU B2C buyer (no VAT), delivery outside EU
        → export 0%."""
        partner_us_b2c = self.env["res.partner"].create(
            {
                "name": "US B2C Partner",
                "country_id": self.country_us.id,
                "is_company": False,
            }
        )
        fp = self._get_fp(partner_us_b2c, delivery=None)
        self.assertFpIsExport(fp)

    # ── G-05/06/07/08 : EU B2B buyer ─────────────────────────────────────────

    def test_g05_domestic_eu_b2b_delivery_seller_country(self):
        """G-05 : FR seller, DE B2B buyer, delivery in FR → domestic.

        Goods never leave France — no intra-Community transport.
        """
        fp = self._get_fp(self.partner_de_b2b, delivery=self.delivery_fr_b2b)
        self.assertFpIsDomesticFr(fp)

    def test_g06_intracom_eu_b2b_delivery_buyer_country(self):
        """G-06 : FR seller, DE B2B buyer, delivery in DE → intra-Community."""
        fp = self._get_fp(self.partner_de_b2b, delivery=self.delivery_de_b2b)
        self.assertFpIsIntracomB2B(fp)

    def test_g07_intracom_eu_b2b_delivery_third_eu(self):
        """G-07 : FR seller, DE B2B buyer, delivery in IE → intra-Community."""
        fp = self._get_fp(self.partner_de_b2b, delivery=self.delivery_ie_b2b)
        self.assertFpIsIntracomB2B(fp)

    def test_g08_export_eu_b2b_delivery_outside_eu(self):
        """G-08 : FR seller, DE B2B buyer, delivery outside EU → export 0%.

        The buyer is EU B2B but goods are shipped outside the EU.
        """
        partner_us_addr = self.env["res.partner"].create(
            {
                "name": "US Delivery Address",
                "country_id": self.country_us.id,
                "type": "delivery",
            }
        )
        fp = self._get_fp(self.partner_de_b2b, delivery=partner_us_addr)
        self.assertFpIsExport(fp)

    # ── G-09/10/11/12 : EU B2C buyer ─────────────────────────────────────────

    def test_g09_domestic_eu_b2c_delivery_seller_country(self):
        """G-09 : FR seller, IE B2C buyer, delivery in FR → domestic."""
        fp = self._get_fp(self.partner_ie_b2c, delivery=self.delivery_fr_b2c)
        self.assertFpIsDomesticFr(fp)

    def test_g10_oss_eu_b2c_delivery_buyer_country(self):
        """G-10 : FR seller, DE B2C buyer, delivery in DE → OSS DE."""
        fp = self._get_fp(self.partner_de_b2c, delivery=self.delivery_de_b2c)
        self.assertFpIsOssCountry(fp, self.country_de)

    def test_g11_oss_eu_b2c_delivery_third_eu(self):
        """G-11 : FR seller, DE B2C buyer, delivery in IE → OSS IE."""
        fp = self._get_fp(self.partner_de_b2c, delivery=self.delivery_ie_b2c)
        self.assertFpIsOssCountry(fp, self.country_ie)

    def test_g12_export_eu_b2c_delivery_outside_eu(self):
        """G-12 : FR seller, IE B2C buyer, delivery outside EU → export 0%."""
        partner_us_addr = self.env["res.partner"].create(
            {
                "name": "US Delivery Address",
                "country_id": self.country_us.id,
                "type": "delivery",
            }
        )
        fp = self._get_fp(self.partner_ie_b2c, delivery=partner_us_addr)
        self.assertFpIsExport(fp)

    # ── Cross-checks with untyped (dropship) delivery addresses ──────────────

    def test_g03_dropship_untyped_delivery(self):
        """G-03 variant: untyped delivery (dropship to unknown third party)
        must not change the export result."""
        fp = self._get_fp(self.partner_gb_b2b, delivery=self.delivery_ie)
        self.assertFpIsExport(fp)

    def test_g11_dropship_b2c_untyped_delivery(self):
        """G-11 variant: B2C buyer, untyped delivery in IE → OSS IE."""
        fp = self._get_fp(self.partner_de_b2c, delivery=self.delivery_ie)
        self.assertFpIsOssCountry(fp, self.country_ie)

    # ── Non-FR EU seller ──────────────────────────────────────────────────────

    def test_g_de_seller_domestic(self):
        """DE seller, DE B2B buyer, delivery in DE → domestic DE VAT."""
        company_de = self.env["res.company"].create(
            {
                "name": "Test Company DE",
                "country_id": self.country_de.id,
            }
        )
        _has_fp_type = hasattr(
            self.env["account.fiscal.position"], "fiscal_position_type"
        )
        self.env["account.fiscal.position"].create(
            {
                "name": "DE Domestic",
                "company_id": company_de.id,
                "sequence": 1,
                "auto_apply": True,
                "vat_required": True,
                "country_id": self.country_de.id,
                **(_has_fp_type and {"fiscal_position_type": "b2b"} or {}),
            }
        )
        fp = (
            self.env["account.fiscal.position"]
            .with_company(company_de)
            .with_context(fp_eu_seller=company_de.partner_id)
            ._get_fiscal_position(
                self.partner_de_b2b,
                delivery=self.delivery_de_b2b,
            )
        )
        self.assertTrue(fp.vat_required)
        self.assertEqual(fp.country_id, self.country_de)

    def test_g_de_seller_intracom(self):
        """DE seller, FR B2B buyer, delivery in FR → intra-Community."""
        company_de = self.env["res.company"].create(
            {
                "name": "Test Company DE",
                "country_id": self.country_de.id,
            }
        )
        _has_fp_type = hasattr(
            self.env["account.fiscal.position"], "fiscal_position_type"
        )
        self.env["account.fiscal.position"].create(
            {
                "name": "EU Intra-Community B2B (DE)",
                "company_id": company_de.id,
                "auto_apply": True,
                "vat_required": True,
                "country_group_id": self.env.ref("base.europe").id,
                **(_has_fp_type and {"fiscal_position_type": "b2b"} or {}),
            }
        )
        fp = (
            self.env["account.fiscal.position"]
            .with_company(company_de)
            .with_context(fp_eu_seller=company_de.partner_id)
            ._get_fiscal_position(
                self.partner_fr_b2b,
                delivery=self.delivery_fr_b2b,
            )
        )
        self.assertFpIsIntracomB2B(fp)

    def test_g_de_seller_export(self):
        """DE seller, GB B2B buyer, delivery in FR → export 0%."""
        company_de = self.env["res.company"].create(
            {
                "name": "Test Company DE",
                "country_id": self.country_de.id,
            }
        )
        _has_fp_type = hasattr(
            self.env["account.fiscal.position"], "fiscal_position_type"
        )
        self.env["account.fiscal.position"].create(
            {
                "name": "Export outside EU (DE)",
                "company_id": company_de.id,
                "sequence": 50,
                "auto_apply": True,
                "vat_required": False,
                **(_has_fp_type and {"fiscal_position_type": "b2b"} or {}),
            }
        )
        fp = (
            self.env["account.fiscal.position"]
            .with_company(company_de)
            .with_context(fp_eu_seller=company_de.partner_id)
            ._get_fiscal_position(
                self.partner_gb_b2b,
                delivery=self.delivery_fr_b2b,
            )
        )
        self.assertFpIsExport(fp)

    # ── No delivery address ───────────────────────────────────────────────────

    def test_no_delivery_b2b_eu_buyer(self):
        """No delivery: B2B EU buyer → intra-Community by buyer country."""
        fp = self._get_fp(self.partner_de_b2b, delivery=None)
        self.assertFpIsIntracomB2B(fp)

    def test_no_delivery_b2c_eu_buyer(self):
        """No delivery: B2C EU buyer → OSS by buyer country."""
        fp = self._get_fp(self.partner_de_b2c, delivery=None)
        self.assertFpIsOssCountry(fp, self.country_de)
