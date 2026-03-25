# Copyright 2026 Akretion
# @author Guillaume MASSON <guillaume.masson@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.account_fiscal_position_eu_rule.tests.common import (
    FiscalPositionEuRuleCommon,
)


class SaleFiscalPositionEuRuleCommon(FiscalPositionEuRuleCommon):
    """Fixtures for sale order fiscal position tests.

    Extends FiscalPositionEuRuleCommon with the minimal sale-specific objects
    needed to create real sale orders and trigger onchanges via Form.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._setup_sale_fixtures()

    @classmethod
    def _setup_sale_fixtures(cls):
        # Product
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "consu",
                "list_price": 100.0,
                "taxes_id": False,
            }
        )
        # Pricelist in company currency
        cls.pricelist = cls.env["product.pricelist"].create(
            {
                "name": "Test Pricelist",
                "currency_id": cls.env.company.currency_id.id,
            }
        )
