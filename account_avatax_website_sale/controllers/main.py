from odoo.http import request

from odoo.addons.website_sale.controllers.main import WebsiteSale


class AvataxWebsiteSale(WebsiteSale):
    def shop_payment(self, **post):
        order = request.website.sale_get_order()
        order._avatax_compute_tax()
        return super(AvataxWebsiteSale, self).shop_payment(**post)
