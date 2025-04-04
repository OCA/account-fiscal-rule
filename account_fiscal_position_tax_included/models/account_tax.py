# Copyright (C) 2019-Today GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountTax(models.Model):
    _inherit = "account.tax"

    @api.model
    def _fix_tax_included_price(self, price, prod_taxes, line_taxes):
        """Subtract tax amount from price when corresponding "price included"
        taxes do not apply. (for tax excluded)"""
        res = super()._fix_tax_included_price(price, prod_taxes, line_taxes)

        if price != res:
            return res
        if any([x.price_include for x in line_taxes]) and not any(
            [x.price_include for x in prod_taxes]
        ):
            # it's a switch between vat exc and vat incl
            return price * (100 + line_taxes[0].amount) / 100
        return res
