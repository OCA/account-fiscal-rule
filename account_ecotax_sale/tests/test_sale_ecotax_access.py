# Copyright 2026 Camptocamp SA (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.fields import Command
from odoo.tests import new_test_user

from .test_sale_ecotax import TestsaleEcotaxCommon


class TestSaleEcotaxAccess(TestsaleEcotaxCommon):
    def test_accounting_users_read_sale_ecotax_lines(self):
        sale = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [Command.create({"product_id": self.product_b.id})],
            }
        )
        for groups in (
            "account.group_account_invoice",
            "account.group_account_readonly",
        ):
            user = new_test_user(
                self.env, login=groups, groups=f"base.group_user,{groups}"
            )
            self.env.invalidate_all()
            self.assertEqual(
                sale.with_user(user).order_line.ecotax_line_ids.amount_unit, 16
            )
