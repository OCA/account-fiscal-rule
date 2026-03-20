# Copyright 2026 Akretion
# @author Guillaume MASSON <guillaume.masson@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import Form

from .common import AccountMoveFiscalPositionEuRuleCommon


class TestAccountMoveFiscalPosition(AccountMoveFiscalPositionEuRuleCommon):
    """Integration tests for account_move_fiscal_position_eu_rule.

    Tests cover both outgoing (out_invoice) and incoming (in_invoice) moves,
    with and without partner_shipping_id, to verify that the correct triplet
    (seller, buyer, delivery) is passed to _get_fiscal_position() in each case.

    Fiscal rule logic is covered exhaustively in the main module tests.
    These tests focus on the correct construction of the triplet from the
    account.move fields.
    """

    # ── Outgoing invoices (out_invoice) ───────────────────────────────────────

    def test_out_invoice_export_non_eu_buyer_delivery_in_eu(self):
        """FR seller, UK buyer, delivery in IE → export 0%.

        Core bug case: delivery in EU must not trigger OSS when buyer is
        outside EU.
        """
        move = self._make_out_invoice(
            self.partner_gb_b2b,
            partner_shipping=self.delivery_ie_b2c,
        )
        self.assertFpIsExport(move.fiscal_position_id)

    def test_out_invoice_intracom_b2b_delivery_other_eu(self):
        """FR seller, DE B2B buyer, delivery in IE → intra-Community."""
        move = self._make_out_invoice(
            self.partner_de_b2b,
            partner_shipping=self.delivery_ie_b2b,
        )
        self.assertFpIsIntracomB2B(move.fiscal_position_id)

    def test_out_invoice_domestic_b2b_delivery_in_fr(self):
        """FR seller, DE B2B buyer, delivery in FR → domestic VAT."""
        move = self._make_out_invoice(
            self.partner_de_b2b,
            partner_shipping=self.delivery_fr_b2b,
        )
        self.assertFpIsDomesticFr(move.fiscal_position_id)

    def test_out_invoice_oss_b2c_delivery_in_buyer_country(self):
        """FR seller, DE B2C buyer, delivery in DE → OSS DE."""
        move = self._make_out_invoice(
            self.partner_de_b2c,
            partner_shipping=self.delivery_de_b2c,
        )
        self.assertFpIsOssCountry(move.fiscal_position_id, self.country_de)

    def test_out_invoice_oss_b2c_delivery_third_eu_country(self):
        """FR seller, DE B2C buyer, delivery in IE → OSS IE."""
        move = self._make_out_invoice(
            self.partner_de_b2c,
            partner_shipping=self.delivery_ie_b2c,
        )
        self.assertFpIsOssCountry(move.fiscal_position_id, self.country_ie)

    # ── Incoming invoices (in_invoice) ────────────────────────────────────────

    def test_in_invoice_uk_supplier_no_shipping(self):
        """FR buyer, UK supplier, no delivery → export FP on vendor bill."""
        move = self._make_in_invoice(self.partner_gb_b2b)
        self.assertFpIsExport(move.fiscal_position_id)

    def test_in_invoice_uk_supplier_dropship_ie(self):
        """FR buyer, UK supplier, dropship to IE → export FP.

        Even with a delivery address in Ireland, the UK supplier is outside
        the EU — the delivery address must not trigger OSS on the vendor bill.
        """
        move = self._make_in_invoice(
            self.partner_gb_b2b,
            partner_shipping=self.delivery_ie_b2c,
        )
        self.assertFpIsExport(move.fiscal_position_id)

    def test_in_invoice_de_supplier_standard(self):
        """FR buyer, DE supplier → intra-Community on vendor bill."""
        move = self._make_in_invoice(self.partner_de_b2b)
        self.assertFpIsIntracomB2B(move.fiscal_position_id)

    def test_in_invoice_de_supplier_dropship_ie(self):
        """FR buyer, DE supplier, dropship to IE → intra-Community.

        Both FR and DE are in the EU. Delivery to Ireland does not change
        the intra-Community nature of the supply on the vendor bill.
        """
        move = self._make_in_invoice(
            self.partner_de_b2b,
            partner_shipping=self.delivery_ie_b2b,
        )
        self.assertFpIsIntracomB2B(move.fiscal_position_id)

    # ── Recomputation on partner_shipping_id change ───────────────────────────

    def test_out_invoice_fp_recomputed_when_shipping_changes(self):
        """Changing partner_shipping_id recomputes the fiscal position."""
        move = self._make_out_invoice(
            self.partner_gb_b2b,
            partner_shipping=self.delivery_ie_b2c,
        )
        self.assertFpIsExport(move.fiscal_position_id)

        # Change delivery to Germany — FP must still be export (buyer is UK)
        with Form(move) as form:
            form.partner_shipping_id = self.delivery_de_b2c
        move = form.save()
        self.assertFpIsExport(move.fiscal_position_id)
