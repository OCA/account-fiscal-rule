# Copyright 2026 Akretion
# @author Guillaume MASSON <guillaume.masson@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from .common import PurchaseFiscalPositionEuRuleCommon


class TestEuRuleDelivery(PurchaseFiscalPositionEuRuleCommon):
    """Unit tests for _get_eu_rule_delivery().

    Tests the three cases: purchase_stock absent, standard purchase,
    and dropship purchase.
    """

    def _make_po_record(self, partner):
        """Create a minimal PO record without using Form (no onchange needed)."""
        return (
            self.env["purchase.order"]
            .with_company(self.company_fr)
            .create(
                {
                    "partner_id": partner.id,
                }
            )
        )

    def test_delivery_without_purchase_stock(self):
        """When purchase_stock is absent, _get_eu_rule_delivery() returns None.

        We simulate the absence of purchase_stock by patching hasattr() to
        return False for dest_address_id and picking_type_id.
        """
        po = self._make_po_record(self.partner_gb_b2b)

        original_hasattr = hasattr

        def mock_hasattr(obj, name):
            if name in ("dest_address_id", "picking_type_id"):
                return False
            return original_hasattr(obj, name)

        with patch("builtins.hasattr", side_effect=mock_hasattr):
            delivery = po._get_eu_rule_delivery()

        self.assertFalse(delivery)

    def test_delivery_standard_purchase_with_purchase_stock(self):
        """Standard purchase: delivery = warehouse partner.

        We simulate purchase_stock by patching hasattr() to return True and
        providing a mock picking_type_id with a warehouse partner.
        """
        po = self._make_po_record(self.partner_gb_b2b)

        original_hasattr = hasattr

        def mock_hasattr(obj, name):
            if name == "dest_address_id":
                return True
            if name == "picking_type_id":
                return True
            return original_hasattr(obj, name)

        # Patch dest_address_id to be empty and picking_type_id to point
        # to a warehouse with a French partner address.
        with patch("builtins.hasattr", side_effect=mock_hasattr), patch.object(
            type(po),
            "dest_address_id",
            new_callable=lambda: property(lambda self: self.env["res.partner"]),
        ), patch.object(
            type(po),
            "picking_type_id",
            new_callable=lambda: property(
                lambda self: type(
                    "MockPickingType",
                    (),
                    {
                        "warehouse_id": type(
                            "MockWarehouse",
                            (),
                            {"partner_id": po.env.ref("base.main_partner")},
                        )()
                    },
                )()
            ),
        ):
            delivery = po._get_eu_rule_delivery()

        self.assertEqual(delivery, po.env.ref("base.main_partner"))

    def test_delivery_dropship(self):
        """Dropship purchase: delivery = dest_address_id."""
        po = self._make_po_record(self.partner_gb_b2b)

        original_hasattr = hasattr

        def mock_hasattr(obj, name):
            if name == "dest_address_id":
                return True
            return original_hasattr(obj, name)

        with patch("builtins.hasattr", side_effect=mock_hasattr), patch.object(
            type(po),
            "dest_address_id",
            new_callable=lambda: property(
                lambda self: po.env["res.partner"].browse(
                    po.env.ref("base.main_partner").id
                )
            ),
        ):
            delivery = po._get_eu_rule_delivery()

        self.assertEqual(delivery, po.env.ref("base.main_partner"))
