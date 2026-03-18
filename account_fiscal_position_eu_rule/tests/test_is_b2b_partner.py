# Copyright 2026 Akretion
# @author Guillaume MASSON <guillaume.masson@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from .common import FiscalPositionEuRuleCommon


class TestIsB2bPartner(FiscalPositionEuRuleCommon):
    """Unit tests for _is_b2b_partner().

    Each test is self-contained and uses res.partner.create() to build
    partners with specific field combinations, so that the tests run correctly
    regardless of which optional modules are installed.

    Scenarios covered:

    ┌─────────────────────────────┬──────────────────┬──────────────────────┬────────┐
    │ vat    │ vat_check_vies     │ vies_passed      │ fiscal_position_type │ result │
    ├────────┼────────────────────┼──────────────────┼──────────────────────┼────────┤
    │ absent │ n/a                │ n/a              │ n/a                  │ False  │
    │ set    │ absent/False       │ absent           │ absent               │ True   │
    │ set    │ absent/False       │ absent           │ b2b                  │ True   │
    │ set    │ absent/False       │ absent           │ b2c                  │ False  │
    │ set    │ absent/False       │ False (disabled) │ b2b                  │ True   │
    │ set    │ absent/False       │ False (disabled) │ b2c                  │ False  │
    │ set    │ True               │ True             │ absent               │ True   │
    │ set    │ True               │ True             │ b2c                  │ True   │
    │ set    │ True               │ False            │ absent               │ False  │
    │ set    │ True               │ False            │ b2b                  │ False  │
    └────────┴────────────────────┴──────────────────┴──────────────────────┴────────┘
    """

    def _fp(self):
        """Return an AccountFiscalPosition recordset in company_fr context."""
        return self.env["account.fiscal.position"].with_company(self.company_fr)

    def _partner(self, vat=None, fiscal_position_type=None, vies_passed=None):
        """Build a res.partner with the given field values.

        Uses create() so that stored fields (fiscal_position_type, vies_passed)
        are actually persisted and readable by _is_b2b_partner.
        Fields belonging to optional modules are only set when installed.
        """
        vals = {"name": "Test Partner", "country_id": self.country_de.id}
        if vat:
            vals["vat"] = vat
        if fiscal_position_type and hasattr(
            self.env["res.partner"], "fiscal_position_type"
        ):
            vals["fiscal_position_type"] = fiscal_position_type
        partner = self.env["res.partner"].create(vals)
        if vies_passed is not None and hasattr(partner, "vies_passed"):
            partner.write({"vies_passed": vies_passed})
        return partner

    def _set_vat_check_vies(self, value):
        """Set vat_check_vies on company_fr if the field exists."""
        if hasattr(self.company_fr, "vat_check_vies"):
            self.company_fr.vat_check_vies = value

    # ── No VAT number ─────────────────────────────────────────────────────────

    def test_no_vat_is_b2c(self):
        """Partner without VAT is always B2C regardless of other fields."""
        partner = self._partner()
        self.assertFalse(self._fp()._is_b2b_partner(partner))

    def test_no_vat_with_fp_type_b2b_still_b2c(self):
        """fiscal_position_type=b2b cannot make a partner B2B without VAT."""
        partner = self._partner(fiscal_position_type="b2b")
        self.assertFalse(self._fp()._is_b2b_partner(partner))

    # ── fiscal_position_type only (no VIES, or VIES disabled) ─────────────────

    def test_fp_type_b2b_with_vat(self):
        """VAT + fiscal_position_type=b2b, VIES absent/disabled → B2B.

        Result is always True: with the module, fiscal_position_type=b2b
        drives the decision; without it, VAT presence is the fallback.
        """
        self._set_vat_check_vies(False)
        partner = self._partner(vat="DE812345673", fiscal_position_type="b2b")
        self.assertTrue(self._fp()._is_b2b_partner(partner))

    def test_fp_type_b2c_with_vat(self):
        """VAT + fiscal_position_type=b2c, VIES absent/disabled.

        With account_fiscal_position_partner_type: b2c overrides VAT → B2C.
        Without it: VAT presence is the only signal → B2B (correct fallback).
        """
        self._set_vat_check_vies(False)
        partner = self._partner(vat="DE812345673", fiscal_position_type="b2c")
        if hasattr(self.env["res.partner"], "fiscal_position_type"):
            self.assertFalse(self._fp()._is_b2b_partner(partner))
        else:
            self.assertTrue(self._fp()._is_b2b_partner(partner))

    def test_vies_disabled_fp_type_b2b(self):
        """VIES disabled + fiscal_position_type=b2b → always B2B.

        fiscal_position_type=b2b wins when the module is present;
        VAT presence wins as fallback when it is absent.
        """
        self._set_vat_check_vies(False)
        partner = self._partner(
            vat="DE812345673",
            fiscal_position_type="b2b",
            vies_passed=False,
        )
        self.assertTrue(self._fp()._is_b2b_partner(partner))

    def test_vies_disabled_fp_type_b2c(self):
        """VIES disabled + fiscal_position_type=b2c.

        With account_fiscal_position_partner_type: b2c overrides
        the meaningless vies_passed=False → B2C.
        Without it: VAT presence is the only signal → B2B (correct fallback).
        """
        self._set_vat_check_vies(False)
        partner = self._partner(
            vat="DE812345673",
            fiscal_position_type="b2c",
            vies_passed=False,
        )
        if hasattr(self.env["res.partner"], "fiscal_position_type"):
            self.assertFalse(self._fp()._is_b2b_partner(partner))
        else:
            self.assertTrue(self._fp()._is_b2b_partner(partner))

    # ── VIES active (vat_check_vies=True) ─────────────────────────────────────

    def test_vies_active_passed_true(self):
        """VIES active + vies_passed=True → B2B (VIES is authoritative)."""
        if not hasattr(self.company_fr, "vat_check_vies"):
            return
        self._set_vat_check_vies(True)
        partner = self._partner(vat="DE812345673", vies_passed=True)
        if not hasattr(partner, "vies_passed"):
            return
        self.assertTrue(self._fp()._is_b2b_partner(partner))

    def test_vies_active_passed_true_overrides_fp_type_b2c(self):
        """VIES active + vies_passed=True + fiscal_position_type=b2c → B2B.

        VIES confirmation takes priority over the manual fiscal_position_type.
        """
        if not hasattr(self.company_fr, "vat_check_vies"):
            return
        self._set_vat_check_vies(True)
        partner = self._partner(
            vat="DE812345673",
            fiscal_position_type="b2c",
            vies_passed=True,
        )
        if not hasattr(partner, "vies_passed"):
            return
        self.assertTrue(self._fp()._is_b2b_partner(partner))

    def test_vies_active_passed_false(self):
        """VIES active + vies_passed=False → B2C (VIES is authoritative)."""
        if not hasattr(self.company_fr, "vat_check_vies"):
            return
        self._set_vat_check_vies(True)
        partner = self._partner(vat="DE812345673", vies_passed=False)
        if not hasattr(partner, "vies_passed"):
            return
        self.assertFalse(self._fp()._is_b2b_partner(partner))

    def test_vies_active_passed_false_overrides_fp_type_b2b(self):
        """VIES active + vies_passed=False + fiscal_position_type=b2b → B2C.

        VIES explicit failure takes priority over the manual fiscal_position_type.
        """
        if not hasattr(self.company_fr, "vat_check_vies"):
            return
        self._set_vat_check_vies(True)
        partner = self._partner(
            vat="DE812345673",
            fiscal_position_type="b2b",
            vies_passed=False,
        )
        if not hasattr(partner, "vies_passed"):
            return
        self.assertFalse(self._fp()._is_b2b_partner(partner))
