# Copyright 2026 Akretion
# @author Guillaume MASSON <guillaume.masson@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from .common import FiscalPositionEuRuleCommon


class TestEuServices(FiscalPositionEuRuleCommon):
    """Fiscal position resolution for services — EU seller.

    Directive 2006/112/EC, Arts. 44 and 45.
    The delivery address is always irrelevant for services.
    Test IDs follow the decision matrix in readme/DESCRIPTION.rst.
    """

    # ── S-01/02 : buyer outside EU ────────────────────────────────────────────

    def test_s01_export_non_eu_b2b(self):
        """S-01 : FR seller, GB B2B buyer → export 0% (Art. 44, outside EU)."""
        fp = self._get_fp(self.partner_gb_b2b, is_service=True)
        self.assertFpIsExport(fp)

    def test_s01_delivery_ignored_non_eu_b2b(self):
        """S-01 variant: delivery address must be ignored for non-EU B2B."""
        fp = self._get_fp(
            self.partner_gb_b2b,
            delivery=self.delivery_ie_b2c,
            is_service=True,
        )
        self.assertFpIsExport(fp)

    def test_s02_domestic_non_eu_b2c(self):
        """S-02 : FR seller, non-EU B2C buyer → domestic FR VAT (Art. 45).

        For B2C services, place of supply is the seller's country regardless
        of where the buyer is located.
        """
        partner_us_b2c = self.env["res.partner"].create(
            {
                "name": "US B2C Partner",
                "country_id": self.country_us.id,
                "is_company": False,
            }
        )
        fp = self._get_fp(partner_us_b2c, is_service=True)
        self.assertFpIsDomesticFr(fp)

    # ── S-03/04 : EU B2B buyer ────────────────────────────────────────────────

    def test_s03_domestic_eu_b2b_same_country(self):
        """S-03 : FR seller, FR B2B buyer → domestic (Art. 44, same country)."""
        fp = self._get_fp(self.partner_fr_b2b, is_service=True)
        self.assertFpIsDomesticFr(fp)

    def test_s04_intracom_eu_b2b_other_country(self):
        """S-04 : FR seller, DE B2B buyer → intra-Community (Art. 44)."""
        fp = self._get_fp(self.partner_de_b2b, is_service=True)
        self.assertFpIsIntracomB2B(fp)

    def test_s04_delivery_ignored_eu_b2b(self):
        """S-04 variant: delivery address must be ignored for EU B2B services.

        Passing different delivery addresses must always yield the same result.
        """
        fp_no_delivery = self._get_fp(self.partner_de_b2b, is_service=True)
        fp_delivery_fr = self._get_fp(
            self.partner_de_b2b, delivery=self.delivery_fr_b2b, is_service=True
        )
        fp_delivery_ie = self._get_fp(
            self.partner_de_b2b, delivery=self.delivery_ie_b2c, is_service=True
        )
        self.assertFpIsIntracomB2B(fp_no_delivery)
        self.assertFpIsIntracomB2B(fp_delivery_fr)
        self.assertFpIsIntracomB2B(fp_delivery_ie)

    # ── S-05 : EU B2C buyer ───────────────────────────────────────────────────

    def test_s05_domestic_eu_b2c(self):
        """S-05 : FR seller, DE B2C buyer → domestic FR VAT (Art. 45)."""
        fp = self._get_fp(self.partner_de_b2c, is_service=True)
        self.assertFpIsDomesticFr(fp)

    def test_s05_delivery_ignored_eu_b2c(self):
        """S-05 variant: delivery address must be ignored for EU B2C services."""
        fp_no_delivery = self._get_fp(self.partner_hr_b2c, is_service=True)
        fp_delivery_hr = self._get_fp(
            self.partner_hr_b2c, delivery=self.delivery_hr_b2c, is_service=True
        )
        self.assertFpIsDomesticFr(fp_no_delivery)
        self.assertFpIsDomesticFr(fp_delivery_hr)

    def test_s05_ie_private_individual(self):
        """S-05 variant: FR seller, IE private individual → domestic FR VAT."""
        fp = self._get_fp(
            self.partner_ie_b2c, delivery=self.delivery_ie_b2c, is_service=True
        )
        self.assertFpIsDomesticFr(fp)

    # ── Goods vs services divergence ─────────────────────────────────────────

    def test_goods_vs_services_b2c_differ(self):
        """EU B2C: goods → OSS delivery country, services → domestic seller."""
        fp_goods = self._get_fp(
            self.partner_hr_b2c, delivery=self.delivery_hr_b2c, is_service=False
        )
        fp_services = self._get_fp(
            self.partner_hr_b2c, delivery=self.delivery_hr_b2c, is_service=True
        )
        self.assertFpIsOssCountry(fp_goods, self.country_hr)
        self.assertFpIsDomesticFr(fp_services)

    def test_goods_vs_services_non_eu_same(self):
        """Non-EU buyer: both goods and services yield export."""
        fp_goods = self._get_fp(
            self.partner_gb_b2b, delivery=self.delivery_ie_b2c, is_service=False
        )
        fp_services = self._get_fp(
            self.partner_gb_b2b, delivery=self.delivery_ie_b2c, is_service=True
        )
        self.assertFpIsExport(fp_goods)
        self.assertFpIsExport(fp_services)
