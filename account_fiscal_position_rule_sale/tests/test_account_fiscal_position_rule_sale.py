# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestAccountFiscalPositionRuleSale(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestAccountFiscalPositionRuleSale, cls).setUpClass()

        # MODELS
        cls.fiscal_position_model = cls.env["account.fiscal.position"]
        cls.fiscal_position_rule_model = cls.env["account.fiscal.position.rule"]
        cls.partner_model = cls.env["res.partner"]
        cls.sale_order_model = cls.env["sale.order"]

        # INSTANCES
        # Fiscal positions
        cls.fiscal_position_01 = cls.fiscal_position_model.create(
            {"name": "Fiscal position 01", "auto_apply": True}
        )
        cls.fiscal_position_02 = cls.fiscal_position_model.create(
            {"name": "Fiscal position 02", "auto_apply": True}
        )
        # Partners
        cls.partner_01 = cls.partner_model.create(
            {
                "name": "Partner 01",
                "company_id": cls.env.ref("base.main_company").id,
                "property_account_position_id": cls.fiscal_position_01.id,
            }
        )
        cls.partner_02 = cls.partner_model.create(
            {"name": "Partner 02", "company_id": cls.env.ref("base.main_company").id}
        )
        # Sale orders
        cls.sale_order_01 = cls.sale_order_model.create(
            {
                "partner_id": cls.partner_01.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.env.ref("product.product_product_2").id,
                            "product_uom": cls.env.ref("uom.product_uom_unit").id,
                            "product_uom_qty": 1,
                        },
                    )
                ],
            }
        )
        # Fiscal position rules
        cls.fiscal_position_rule_01 = cls.fiscal_position_rule_model.create(
            {
                "name": "Fiscal position rule 01",
                "fiscal_position_id": cls.fiscal_position_02.id,
                "company_id": cls.env.ref("base.main_company").id,
                "use_sale": True,
            }
        )

    def test_01(self):
        """
        Data:
            - A draft sale order
            - The partner has a fiscal position
        Test case:
            - Trigger the fiscal position onchange on the SO
        Expected result:
            - The partner's fiscal position is set on the SO
        """
        self.assertFalse(self.sale_order_01.fiscal_position_id)
        self.sale_order_01.onchange_fiscal_position_map()
        self.assertEqual(self.sale_order_01.fiscal_position_id, self.fiscal_position_01)

    def test_02(self):
        """
        Data:
            - A draft sale order
            - No fiscal position on the partner
            - A fiscal rule that should be used on the SO
        Test case:
            - Trigger the fiscal position onchange on the SO
        Expected result:
            - The rule's fiscal position is set on the SO
        """
        self.sale_order_01.partner_id = self.partner_02
        self.assertFalse(self.sale_order_01.fiscal_position_id)
        self.sale_order_01.onchange_fiscal_position_map()
        self.assertEqual(
            self.sale_order_01.fiscal_position_id,
            self.fiscal_position_rule_01.fiscal_position_id,
        )
