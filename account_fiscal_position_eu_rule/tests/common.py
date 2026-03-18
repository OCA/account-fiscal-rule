# Copyright 2026 Akretion
# @author Guillaume MASSON <guillaume.masson@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class FiscalPositionEuRuleCommon(BaseCommon):
    """Common fixtures for EU fiscal position rule tests.

    Country references
    ------------------
    - self.country_fr   France          (EU — member of base.europe)
    - self.country_de   Germany         (EU — member of base.europe)
    - self.country_ie   Ireland         (EU — member of base.europe)
    - self.country_hr   Croatia         (EU — member of base.europe)
    - self.country_gb   United Kingdom  (non-EU — not in base.europe)
    - self.country_us   United States   (non-EU — not in base.europe)

    Company / seller
    ----------------
    - self.company_fr   French company  (seller in all EU-seller test cases)

    Partners
    --------
    - self.partner_fr_b2b   French B2B   (VAT set, same country as seller)
    - self.partner_de_b2b         German B2B (VAT set, fiscal_position_type=b2b)
    - self.partner_de_b2b_vies_ko  German B2B with VAT but typed B2C (VIES invalid)
    - self.partner_de_b2c   German B2C   (no VAT)
    - self.partner_ie_b2b   Irish B2B    (VAT set)
    - self.partner_ie_b2c   Irish B2C    (no VAT — private individual)
    - self.partner_hr_b2c   Croatian B2C (no VAT)
    - self.partner_gb_b2b   UK B2B       (VAT set, non-EU)
    - self.partner_us_b2b   US B2B       (VAT set, non-EU)

    Delivery addresses
    ------------------
    Typed (fiscal_position_type set when account_fiscal_position_partner_type
    is installed — propagated from commercial parent in production):

    - self.delivery_fr_b2b   France,  fiscal_position_type=b2b
    - self.delivery_fr_b2c   France,  fiscal_position_type=b2c
    - self.delivery_de_b2b   Germany, fiscal_position_type=b2b
    - self.delivery_de_b2c   Germany, fiscal_position_type=b2c
    - self.delivery_ie_b2b   Ireland, fiscal_position_type=b2b
    - self.delivery_ie_b2c   Ireland, fiscal_position_type=b2c
    - self.delivery_hr_b2c   Croatia, fiscal_position_type=b2c

    Untyped (dropship — third-party address unrelated to the buyer):

    - self.delivery_ie   Ireland (no fiscal_position_type — dropship)

    Fiscal positions (all on company_fr)
    ------------------------------------
    - self.fp_fr_domestic          FR domestic VAT (seq 1, vat_required=True, country=FR)
    - self.fp_eu_intracom_b2b      Intra-EU B2B (seq 3, vat_required=True, group=europe)
    - self.fp_oss_de               OSS Germany (vat_required=False, country=DE)
    - self.fp_oss_ie               OSS Ireland (vat_required=False, country=IE)
    - self.fp_oss_hr               OSS Croatia (vat_required=False, country=HR)
    - self.fp_export               Export (seq 50, vat_required=False, no country)
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._setup_countries()
        cls._setup_company()
        cls._setup_partners()
        cls._setup_delivery_addresses()
        cls._setup_fiscal_positions()

    @classmethod
    def _setup_countries(cls):
        Country = cls.env["res.country"]
        cls.country_fr = Country.search([("code", "=", "FR")], limit=1)
        cls.country_de = Country.search([("code", "=", "DE")], limit=1)
        cls.country_ie = Country.search([("code", "=", "IE")], limit=1)
        cls.country_hr = Country.search([("code", "=", "HR")], limit=1)
        cls.country_gb = Country.search([("code", "=", "GB")], limit=1)
        cls.country_us = Country.search([("code", "=", "US")], limit=1)

    @classmethod
    def _setup_company(cls):
        cls.company_fr = cls.env["res.company"].create(
            {
                "name": "Test Company FR",
                "country_id": cls.country_fr.id,
                "vat": "FR46897818399",
            }
        )
        cls.seller_fr = cls.company_fr.partner_id

    @classmethod
    def _setup_partners(cls):
        Partner = cls.env["res.partner"]
        _has_partner_type = hasattr(Partner, "fiscal_position_type")

        cls.partner_fr_b2b = Partner.create(
            {
                "name": "FR B2B Partner",
                "country_id": cls.country_fr.id,
                "vat": "FR83404833048",
                "is_company": True,
                **(_has_partner_type and {"fiscal_position_type": "b2b"} or {}),
            }
        )
        cls.partner_de_b2b = Partner.create(
            {
                "name": "DE B2B Partner",
                "country_id": cls.country_de.id,
                "vat": "DE812345673",
                "is_company": True,
                **(_has_partner_type and {"fiscal_position_type": "b2b"} or {}),
            }
        )
        # Partner with VAT but explicitly typed B2C — used for EL-02 (VIES
        # validation failed or disabled). Also carries vies_passed=False when
        # base_vat_optional_vies is installed.
        cls.partner_de_b2b_vies_ko = Partner.create(
            {
                "name": "DE B2B Partner (VIES invalid)",
                "country_id": cls.country_de.id,
                "vat": "DE812345673",
                "is_company": True,
                **(_has_partner_type and {"fiscal_position_type": "b2c"} or {}),
            }
        )
        cls.partner_de_b2c = Partner.create(
            {
                "name": "DE B2C Partner",
                "country_id": cls.country_de.id,
                "is_company": False,
                **(_has_partner_type and {"fiscal_position_type": "b2c"} or {}),
            }
        )
        cls.partner_ie_b2b = Partner.create(
            {
                "name": "IE B2B Partner",
                "country_id": cls.country_ie.id,
                "vat": "IE1234567T",
                "is_company": True,
                **(_has_partner_type and {"fiscal_position_type": "b2b"} or {}),
            }
        )
        cls.partner_ie_b2c = Partner.create(
            {
                "name": "IE B2C Partner",
                "country_id": cls.country_ie.id,
                "is_company": False,
                **(_has_partner_type and {"fiscal_position_type": "b2c"} or {}),
            }
        )
        cls.partner_hr_b2c = Partner.create(
            {
                "name": "HR B2C Partner",
                "country_id": cls.country_hr.id,
                "is_company": False,
                **(_has_partner_type and {"fiscal_position_type": "b2c"} or {}),
            }
        )
        cls.partner_gb_b2b = Partner.create(
            {
                "name": "GB B2B Partner",
                "country_id": cls.country_gb.id,
                "vat": "GB123456782",
                "is_company": True,
                **(_has_partner_type and {"fiscal_position_type": "b2b"} or {}),
            }
        )
        cls.partner_us_b2b = Partner.create(
            {
                "name": "US B2B Partner",
                "country_id": cls.country_us.id,
                "vat": "US123456789",
                "is_company": True,
                **(_has_partner_type and {"fiscal_position_type": "b2b"} or {}),
            }
        )

    @classmethod
    def _setup_delivery_addresses(cls):
        Partner = cls.env["res.partner"]
        _hpt = hasattr(Partner, "fiscal_position_type")
        _b2b = {"fiscal_position_type": "b2b"} if _hpt else {}
        _b2c = {"fiscal_position_type": "b2c"} if _hpt else {}

        def _addr(name, country, type_vals):
            return Partner.create(
                {
                    "name": name,
                    "country_id": country.id,
                    "type": "delivery",
                    **type_vals,
                }
            )

        cls.delivery_fr_b2b = _addr("Delivery FR B2B", cls.country_fr, _b2b)
        cls.delivery_fr_b2c = _addr("Delivery FR B2C", cls.country_fr, _b2c)
        cls.delivery_de_b2b = _addr("Delivery DE B2B", cls.country_de, _b2b)
        cls.delivery_de_b2c = _addr("Delivery DE B2C", cls.country_de, _b2c)
        cls.delivery_ie_b2b = _addr("Delivery IE B2B", cls.country_ie, _b2b)
        cls.delivery_ie_b2c = _addr("Delivery IE B2C", cls.country_ie, _b2c)
        cls.delivery_hr_b2c = _addr("Delivery HR B2C", cls.country_hr, _b2c)
        # Untyped: dropship to a third party unrelated to the buyer
        cls.delivery_ie = _addr("Delivery IE", cls.country_ie, {})

    @classmethod
    def _setup_fiscal_positions(cls):
        FP = cls.env["account.fiscal.position"]

        # Deactivate any pre-existing auto-apply FPs that could interfere with
        # our assertions (other modules in the CI may create competing ones).
        FP.with_context(active_test=False).search(
            [
                ("auto_apply", "=", True),
                ("company_id", "in", [cls.company_fr.id, False]),
            ]
        ).write({"active": False})
        _has_fp_type = hasattr(FP, "fiscal_position_type")

        cls.fp_fr_domestic = FP.create(
            {
                "name": "Domestique - France",
                "company_id": cls.company_fr.id,
                "sequence": 1,
                "auto_apply": True,
                "vat_required": True,
                "country_id": cls.country_fr.id,
                **(_has_fp_type and {"fiscal_position_type": "b2b"} or {}),
            }
        )

        cls.fp_eu_intracom_b2b = FP.create(
            {
                "name": "Intra-EU B2B",
                "company_id": cls.company_fr.id,
                "sequence": 3,
                "auto_apply": True,
                "vat_required": True,
                "country_group_id": cls.env.ref("base.europe").id,
                **(_has_fp_type and {"fiscal_position_type": "b2b"} or {}),
            }
        )
        cls.fp_oss_de = FP.create(
            {
                "name": "OSS B2C Germany",
                "company_id": cls.company_fr.id,
                "auto_apply": True,
                "vat_required": False,
                "country_id": cls.country_de.id,
                **(_has_fp_type and {"fiscal_position_type": "b2c"} or {}),
            }
        )
        cls.fp_oss_ie = FP.create(
            {
                "name": "OSS B2C Ireland",
                "company_id": cls.company_fr.id,
                "auto_apply": True,
                "vat_required": False,
                "country_id": cls.country_ie.id,
                **(_has_fp_type and {"fiscal_position_type": "b2c"} or {}),
            }
        )
        cls.fp_oss_hr = FP.create(
            {
                "name": "OSS B2C Croatia",
                "company_id": cls.company_fr.id,
                "auto_apply": True,
                "vat_required": False,
                "country_id": cls.country_hr.id,
                **(_has_fp_type and {"fiscal_position_type": "b2c"} or {}),
            }
        )
        cls.fp_export_b2c = FP.create(
            {
                "name": "Import/Export Hors Europe (B2C)",
                "company_id": cls.company_fr.id,
                "sequence": 50,
                "auto_apply": True,
                "vat_required": False,
                **(_has_fp_type and {"fiscal_position_type": "b2c"} or {}),
            }
        )
        cls.fp_export_b2b = FP.create(
            {
                "name": "Import/Export Hors Europe (B2B)",
                "company_id": cls.company_fr.id,
                "sequence": 50,
                "auto_apply": True,
                "vat_required": False,
                **(_has_fp_type and {"fiscal_position_type": "b2b"} or {}),
            }
        )

    def _get_fp(self, partner, delivery=None, seller=None, is_service=False):
        """Call _get_fiscal_position() in the context of company_fr.

        ``seller`` and ``is_service`` are passed via context keys
        ``fp_eu_seller`` and ``fp_eu_is_service`` to avoid breaking the
        ``_get_fiscal_position()`` signature used by other modules.
        """
        ctx = {
            "fp_eu_seller": seller or self.seller_fr,
            "fp_eu_is_service": is_service,
        }
        return (
            self.env["account.fiscal.position"]
            .with_company(self.company_fr)
            .with_context(**ctx)
            ._get_fiscal_position(partner, delivery=delivery)
        )

    def assertFpIsDomesticFr(self, fp, msg=None):
        """Assert fp is the domestic FR position: vat_required=True, country=FR."""
        self.assertTrue(fp, msg or "Expected domestic FR FP, got empty recordset")
        self.assertTrue(
            fp.vat_required,
            msg or f"Domestic FR FP must have vat_required=True, got {fp.name!r}",
        )
        self.assertEqual(
            fp.country_id,
            self.country_fr,
            msg or f"Domestic FR FP must target country FR, got {fp.name!r}",
        )

    def assertFpIsIntracomB2B(self, fp, msg=None):
        """Assert fp is an intra-Community B2B position: vat_required=True, covers EU."""
        self.assertTrue(
            fp, msg or "Expected intra-Community B2B FP, got empty recordset"
        )
        self.assertTrue(
            fp.vat_required,
            msg
            or f"Intra-Community B2B FP must have vat_required=True, got {fp.name!r}",
        )
        eu_countries = self.env.ref("base.europe").country_ids
        covers_eu = (
            fp.country_group_id and fp.country_group_id.country_ids == eu_countries
        ) or (fp.country_id and fp.country_id in eu_countries)
        self.assertTrue(
            covers_eu,
            msg or f"Intra-Community B2B FP must cover EU countries, got {fp.name!r}",
        )

    def assertFpIsOssCountry(self, fp, country, msg=None):
        """Assert fp is an OSS position for country: vat_required=False, country_id=country."""
        self.assertTrue(
            fp, msg or f"Expected OSS FP for {country.code}, got empty recordset"
        )
        self.assertFalse(
            fp.vat_required,
            msg or f"OSS FP must have vat_required=False, got {fp.name!r}",
        )
        self.assertEqual(
            fp.country_id,
            country,
            msg or f"OSS FP must target country {country.code}, got {fp.name!r}",
        )

    def assertFpIsExport(self, fp, msg=None):
        """Assert fp is the export position: vat_required=False, no country, no group."""
        self.assertTrue(fp, msg or "Expected export FP, got empty recordset")
        self.assertFalse(
            fp.vat_required,
            msg or f"Export FP must have vat_required=False, got {fp.name!r}",
        )
        self.assertFalse(
            fp.country_id,
            msg or f"Export FP must have no country_id, got {fp.name!r}",
        )
        self.assertFalse(
            fp.country_group_id,
            msg or f"Export FP must have no country_group_id, got {fp.name!r}",
        )
