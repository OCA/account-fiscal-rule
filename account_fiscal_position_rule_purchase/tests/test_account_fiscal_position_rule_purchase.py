# Copyright 2018 Camptocamp SA
#   @author: Thomas Nowicki
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.tests.common import SavepointCase


class Tests(SavepointCase):
    """Tests for 'Account Fiscal - Position Rule Purchase' Module"""

    @classmethod
    def setUpClass(cls):
        super(Tests, cls).setUpClass()

        cls.account_fiscal_position_test_for_rule = cls.env[
            "account.fiscal.position"
        ].create({"name": "name_account_fiscal_position_for_rule", "auto_apply": True})
        cls.fiscal_position_rule = cls.env["account.fiscal.position.rule"].create(
            {
                "name": "name_fiscal_position_rule",
                "company_id": cls.env.ref("base.main_company").id,
                "fiscal_position_id": cls.account_fiscal_position_test_for_rule.id,
                "use_purchase": True,
            }
        )
        cls.account_fiscal_position_test = cls.env["account.fiscal.position"].create(
            {"name": "internal_purchase", "auto_apply": True}
        )
        cls.partner_without_fiscal_position = cls.env["res.partner"].create(
            {"name": "partner_name_without_fiscal_position"}
        )
        cls.partner_with_fiscal_position = cls.env["res.partner"].create(
            {
                "name": "partner_name_with_fiscal_position",
                "property_account_position_id": cls.account_fiscal_position_test.id,
            }
        )

    def create_purchase_order(self, purchase_order, values):
        specs = purchase_order._onchange_spec()
        update = purchase_order.onchange(values, ["partner_id"], specs)
        value = update.get("value", {})

        for name, val in value.items():
            if isinstance(val, tuple):
                value[name] = val[0]
        values.update(value)

        return purchase_order.create(values)

    def test_00_fiscal_position(self):
        """Test if the purchase order from partner without fiscal position,
        and any fiscal position has already been declared then,
        has any fiscal position"""

        self.env["account.fiscal.position.rule"].search([]).unlink()
        purchase_order = self.env["purchase.order"]
        values = {
            "partner_id": self.partner_without_fiscal_position.id,
            "company_id": self.env.ref("base.main_company").id,
            "fiscal_position_id": False,
        }

        po = self.create_purchase_order(purchase_order, values)

        self.assertFalse(po.fiscal_position_id)

    def test_01_fiscal_position(self):
        """Test if the purchase order from partner with fiscal position,
        and any fiscal position has already been declared then,
        the purchase order fiscal position is the same as partner"""

        self.env["account.fiscal.position.rule"].search([]).unlink()
        purchase_order = self.env["purchase.order"]
        values = {
            "partner_id": self.partner_with_fiscal_position.id,
            "company_id": self.env.ref("base.main_company").id,
            "fiscal_position_id": False,
        }

        po = self.create_purchase_order(purchase_order, values)

        self.assertEqual(po.fiscal_position_id, self.account_fiscal_position_test)

    def test_02_fiscal_position(self):
        """Test if the purchase order from partner without fiscal position,
        has fiscal position from the main_company"""

        purchase_order = self.env["purchase.order"]
        values = {
            "partner_id": self.partner_without_fiscal_position.id,
            "company_id": self.env.ref("base.main_company").id,
            "fiscal_position_id": False,
        }

        po = self.create_purchase_order(purchase_order, values)

        self.assertEqual(
            po.fiscal_position_id, self.account_fiscal_position_test_for_rule
        )

    def test_03_fiscal_position(self):
        """Test if the purchase order from partner with fiscal position,
        has fiscal position from the partner"""

        purchase_order = self.env["purchase.order"]
        values = {
            "partner_id": self.partner_with_fiscal_position.id,
            "company_id": self.env.ref("base.main_company").id,
            "fiscal_position_id": False,
        }

        po = self.create_purchase_order(purchase_order, values)

        self.assertEqual(po.fiscal_position_id, self.account_fiscal_position_test)
