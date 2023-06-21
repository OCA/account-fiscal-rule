# Copyright 2023 Ecosoft Co., Ltd. <http://ecosoft.co.th>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def get_product_accounts(self, fiscal_pos=None):
        if not fiscal_pos and self.env.context.get("default_fiscal_position_id"):
            fiscal_pos_id = self.env.context["default_fiscal_position_id"]
            fiscal_pos = self.env["account.fiscal.position"].browse(fiscal_pos_id)
        accounts = super().get_product_accounts(fiscal_pos=fiscal_pos)
        return accounts
