# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, exceptions, models
from odoo.fields import first


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.constrains("additional_ecotax_line_product_ids", "ecotax_line_product_ids")
    def check_ecotax_line_country(self):
        for product in self:
            countries = first(product.all_ecotax_line_product_ids).country_ids
            for ecotax_line in product.all_ecotax_line_product_ids:
                if ecotax_line.country_ids != countries:
                    raise exceptions.UserError(
                        _(
                            "All ecotax classification for a product should have the same "
                            "countries allowed. This is a restriction of the "
                            "account_ecotax_tax module."
                        )
                    )
