# Copyright 2026 Akretion
# @author Guillaume MASSON <guillaume.masson@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from .common import PurchaseFiscalPositionEuRuleCommon


class TestPurchaseFiscalPosition(PurchaseFiscalPositionEuRuleCommon):
    """Integration tests for purchase_fiscal_position_eu_rule.

    In a purchase order the triplet is inverted:
    - seller   = partner_id (supplier)
    - buyer    = company_id.partner_id (purchasing company)
    - delivery = dest_address_id (dropship) or warehouse address (standard)

    These tests verify that onchange_partner_id() passes the correct triplet
    to _get_fiscal_position().
    """

    def test_po_fr_buyer_uk_supplier_dropship_ie(self):
        """FR company buys from UK supplier, dropship to IE → export 0%.

        The FR company (buyer) purchases from UK (seller). The delivery is
        in Ireland. The fiscal position from the UK supplier's perspective
        is export — correctly 0% VAT regardless of delivery address.
        """
        po = self._make_purchase_order(
            self.partner_gb_b2b,
            dest_address=self.delivery_ie_b2c,
        )
        self.assertFpIsExport(po.fiscal_position_id)

    def test_po_fr_buyer_uk_supplier_no_dropship(self):
        """FR company buys from UK supplier, standard delivery → export 0%."""
        po = self._make_purchase_order(self.partner_gb_b2b)
        self.assertFpIsExport(po.fiscal_position_id)

    # ── Intra-Community purchase ──────────────────────────────────────────────

    def test_po_fr_buyer_de_supplier_standard(self):
        """FR company buys from DE supplier → intra-Community."""
        po = self._make_purchase_order(self.partner_de_b2b)
        self.assertFpIsIntracomB2B(po.fiscal_position_id)

    def test_po_fr_buyer_de_supplier_dropship_ie(self):
        """FR company buys from DE supplier, dropship to IE → intra-Community.

        Both supplier (DE) and buyer (FR) are in the EU. Delivery to IE
        does not change the intra-Community nature of the supply.
        """
        po = self._make_purchase_order(
            self.partner_de_b2b,
            dest_address=self.delivery_ie_b2c,
        )
        self.assertFpIsIntracomB2B(po.fiscal_position_id)

    # ── _prepare_invoice fallback ─────────────────────────────────────────────

    def test_prepare_invoice_fallback_uses_correct_triplet(self):
        """_prepare_invoice() fallback applies correct FP when FP is empty."""
        po = self._make_purchase_order(
            self.partner_gb_b2b,
            dest_address=self.delivery_ie_b2c,
        )
        po.fiscal_position_id = False
        invoice_vals = po._prepare_invoice()
        fp = self.env["account.fiscal.position"].browse(
            invoice_vals["fiscal_position_id"]
        )
        self.assertFpIsExport(fp)
