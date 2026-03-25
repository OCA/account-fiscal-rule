# Copyright 2026 Akretion
# @author Guillaume MASSON <guillaume.masson@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import Form

from odoo.addons.account_fiscal_position_eu_rule.tests.common import (
    FiscalPositionEuRuleCommon,
)


class PurchaseFiscalPositionEuRuleCommon(FiscalPositionEuRuleCommon):
    """Fixtures for purchase order fiscal position tests."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._setup_purchase_fixtures()

    @classmethod
    def _setup_purchase_fixtures(cls):
        # Product
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "consu",
            }
        )
        # Supplier info on FR seller for GB and DE partners
        cls.env["product.supplierinfo"].create(
            [
                {
                    "partner_id": cls.partner_gb_b2b.id,
                    "product_tmpl_id": cls.product.product_tmpl_id.id,
                    "price": 80.0,
                },
                {
                    "partner_id": cls.partner_de_b2b.id,
                    "product_tmpl_id": cls.product.product_tmpl_id.id,
                    "price": 80.0,
                },
            ]
        )

    def _make_purchase_order(self, partner, dest_address=None):
        """Create a purchase order via Form and return the saved record.

        :param partner: supplier partner (res.partner)
        :param dest_address: dropship delivery address (res.partner or None)
        :returns: purchase.order record
        """
        with Form(self.env["purchase.order"].with_company(self.company_fr)) as form:
            form.partner_id = partner
        purchase = form.save()
        if dest_address:
            purchase.dest_address_id = dest_address
        return purchase
