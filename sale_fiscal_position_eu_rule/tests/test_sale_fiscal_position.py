# Copyright 2026 Akretion
# @author Guillaume MASSON <guillaume.masson@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import Form

from .common import SaleFiscalPositionEuRuleCommon


class TestSaleFiscalPosition(SaleFiscalPositionEuRuleCommon):
    """Integration tests for sale_fiscal_position_eu_rule.

    Each test creates a real sale order via Form, sets the partner and
    delivery address, and verifies that the fiscal position resolved on
    the SO matches the expected EU VAT rule.

    The underlying fiscal logic is already covered by the unit tests in
    account_fiscal_position_eu_rule. These tests focus on verifying that
    the correct triplet (seller, buyer, delivery) is passed from the SO
    to _get_fiscal_position().
    """

    def _make_sale_order(self, partner, partner_shipping=None):
        """Create a sale order via Form and return the saved record.

        Using Form ensures that _compute_fiscal_position_id() and all
        dependent onchanges are triggered exactly as they would be in the UI.

        :param partner: buyer partner (res.partner)
        :param partner_shipping: delivery address (res.partner or None)
        :returns: confirmed sale.order record
        """
        with Form(self.env["sale.order"].with_company(self.company_fr)) as form:
            form.partner_id = partner
            if partner_shipping:
                form.partner_shipping_id = partner_shipping
        return form.save()

    # ── Core bug case : non-EU buyer, delivery in EU ──────────────────────────

    def test_so_export_non_eu_buyer_delivery_in_eu(self):
        """FR seller, UK buyer, delivery in IE → export 0%.

        This is the core scenario from the Voltaire bug report:
        the delivery address is in Ireland but the buyer is a UK company.
        Without this module, Odoo would apply OSS Ireland (23%).
        """
        so = self._make_sale_order(
            self.partner_gb_b2b,
            partner_shipping=self.delivery_ie_b2c,
        )
        self.assertFpIsExport(so.fiscal_position_id)

    def test_so_export_non_eu_buyer_no_delivery(self):
        """FR seller, UK buyer, no explicit delivery → export 0%."""
        so = self._make_sale_order(self.partner_gb_b2b)
        self.assertFpIsExport(so.fiscal_position_id)

    # ── Intra-Community B2B ───────────────────────────────────────────────────

    def test_so_intracom_b2b_delivery_other_eu_country(self):
        """FR seller, DE B2B buyer, delivery in IE → intra-Community."""
        so = self._make_sale_order(
            self.partner_de_b2b,
            partner_shipping=self.delivery_ie_b2c,
        )
        self.assertFpIsIntracomB2B(so.fiscal_position_id)

    def test_so_domestic_b2b_delivery_in_seller_country(self):
        """FR seller, DE B2B buyer, delivery in FR → domestic VAT.

        Goods never leave France: domestic supply despite foreign buyer.
        """
        so = self._make_sale_order(
            self.partner_de_b2b,
            partner_shipping=self.delivery_fr_b2c,
        )
        self.assertFpIsDomesticFr(so.fiscal_position_id)

    # ── OSS B2C ──────────────────────────────────────────────────────────────

    def test_so_oss_b2c_delivery_in_buyer_country(self):
        """FR seller, DE B2C buyer, delivery in DE → OSS DE."""
        so = self._make_sale_order(
            self.partner_de_b2c,
            partner_shipping=self.delivery_de_b2c,
        )
        self.assertFpIsOssCountry(so.fiscal_position_id, self.country_de)

    def test_so_oss_b2c_delivery_third_eu_country(self):
        """FR seller, DE B2C buyer, delivery in IE → OSS IE."""
        so = self._make_sale_order(
            self.partner_de_b2c,
            partner_shipping=self.delivery_ie_b2c,
        )
        self.assertFpIsOssCountry(so.fiscal_position_id, self.country_ie)

    # ── _prepare_invoice fallback ─────────────────────────────────────────────

    def test_prepare_invoice_fallback_uses_correct_triplet(self):
        """_prepare_invoice() fallback applies correct FP when FP is empty.

        We force fiscal_position_id to False on the SO before calling
        _prepare_invoice() to exercise the fallback path.
        """
        so = self._make_sale_order(
            self.partner_gb_b2b,
            partner_shipping=self.delivery_ie_b2c,
        )
        # Force FP to empty to trigger the fallback in _prepare_invoice
        so.fiscal_position_id = False
        invoice_vals = so._prepare_invoice()
        fp = self.env["account.fiscal.position"].browse(
            invoice_vals["fiscal_position_id"]
        )
        self.assertFpIsExport(fp)

    # ── Recomputation on delivery change ─────────────────────────────────────

    def test_so_fp_recomputed_when_delivery_changes(self):
        """Changing delivery address recomputes the fiscal position.

        Verifies that _compute_fiscal_position_id() reacts correctly when
        partner_shipping_id is modified after the SO is created.
        """
        so = self._make_sale_order(
            self.partner_gb_b2b,
            partner_shipping=self.delivery_ie_b2c,
        )
        self.assertFpIsExport(so.fiscal_position_id)

        # Change delivery to France — FP must still be export (buyer is UK)
        with Form(so) as form:
            form.partner_shipping_id = self.delivery_fr_b2c
        so = form.save()
        self.assertFpIsExport(so.fiscal_position_id)
