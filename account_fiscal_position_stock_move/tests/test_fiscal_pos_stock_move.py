# Copyright 2021 Ecosoft Co., Ltd. <http://ecosoft.co.th>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import common
from odoo.tests.common import Form


class TestFiscalPosStockMove(common.TransactionCase):
    def setUp(self):
        super(TestFiscalPosStockMove, self).setUp()
        self.product_categ = self.env.ref("product.product_category_5")
        self.product_categ.property_valuation = "real_time"
        self.stock_val_account = self.product_categ.property_stock_valuation_account_id
        self.product_desk = self.env.ref("product.product_product_4d")
        self.product_desk.categ_id = self.product_categ
        self.picking_type_in = self.env.ref("stock.picking_type_in")
        # Fiscal Position
        self.new_account = self.env["account.account"].create(
            {
                "code": "100",
                "name": "New Account",
                "user_type_id": self.env.ref(
                    "account.data_account_type_current_assets"
                ).id,
            }
        )
        self.fiscal_pos = self.env["account.fiscal.position"].create(
            {
                "name": "Test Fiscal Pos",
                "account_ids": [
                    (
                        0,
                        0,
                        {
                            "account_src_id": self.stock_val_account.id,
                            "account_dest_id": self.new_account.id,
                        },
                    )
                ],
            }
        )

    def test_fiscal_pos_stock_move(self):
        """Create Picking In with realtime valuation product,
        Without fiscal position, I expect account entry to be normal."""
        # No Fiscal Pos, account is normal
        with Form(self.env["stock.picking"]) as f:
            f.picking_type_id = self.picking_type_in
            with f.move_ids_without_package.new() as line:
                line.product_id = self.product_desk
                line.product_uom_qty = 1
        picking = f.save()
        picking.action_confirm()
        picking.move_lines[0].quantity_done = 1
        picking.button_validate()
        self.assertEqual(picking.state, "done")
        move = self.env["account.move"].search(
            [("stock_move_id", "=", picking.move_lines[0].id)]
        )
        move_line = move.line_ids.filtered(lambda l: l.debit)
        self.assertEqual(move_line.account_id, self.stock_val_account)
        # With Fiscal Pos, account is changed to new account
        picking_fpos = picking.copy()
        picking_fpos.fiscal_position_id = self.fiscal_pos
        picking_fpos.action_confirm()
        picking_fpos.move_lines[0].quantity_done = 1
        picking_fpos.button_validate()
        move = self.env["account.move"].search(
            [("stock_move_id", "=", picking_fpos.move_lines[0].id)]
        )
        move_line = move.line_ids.filtered(lambda l: l.debit)
        self.assertEqual(move_line.account_id, self.new_account)
