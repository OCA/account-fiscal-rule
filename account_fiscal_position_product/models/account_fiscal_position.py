#  Copyright 2022 Simone Rubino - TAKOBI
#  Copyright 2024 Damien Carlier - TOODIGIT
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountFiscalPosition(models.Model):
    _inherit = "account.fiscal.position"

    @api.model
    def map_tax(self, taxes, product=None, partner=None):
        """
        Apply tax mapping matching product(s)/category(ies) or none.
        Otherwise, return the original taxes.
        """
        if not self:
            return taxes
        product = product or self.env.context.get("on_change_product_from_aml")
        result = self.env["account.tax"]
        for tax in taxes:
            result |= self._get_applicable_mapping(tax, product)
        return result if result else taxes

    def _get_applicable_mapping(self, taxes, product):
        """
        return the first tax mapping that matches this order:
        - product(s)
        - category(ies)
        - no product(s) and category(ies)
        :param taxes:
        :param product:
        :return:
        """
        domain = [
            "&",
            "&",
            ("position_id", "=", self.id),
            ("tax_src_id", "in", taxes.ids),
        ]
        if product:
            domain.extend(
                [
                    "|",
                    "|",
                    ("product_category_ids", "parent_of", product.categ_id.ids),
                    ("product_ids", "in", product.ids),
                ]
            )
        domain.extend(
            [
                "&",
                ("product_category_ids", "=", False),
                ("product_ids", "=", False),
            ]
        )
        rules = (
            self.env["account.fiscal.position.tax"]
            .search(domain)
            .sorted(lambda a: (a.product_ids, a.product_category_ids), reverse=True)
        )
        tax_dest = self.env["account.tax"]
        if rules:
            tax_dest = rules[0].tax_dest_id
        return tax_dest
