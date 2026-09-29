# Copyright 2025 Kencove, Open Source Integrators
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.tests.common import TransactionCase, tagged

from odoo.addons.account_avatax_website_sale.controllers.main import AvataxWebsiteSale
from odoo.addons.website_sale.controllers.main import WebsiteSale


@tagged("-at_install", "post_install")
class TestAvataxWebsiteSale(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Avatax WS Partner",
                "is_company": True,
                "street": "255 Executive Park Blvd",
                "city": "San Francisco",
                "state_id": cls.env.ref("base.state_us_5").id,
                "country_id": cls.env.ref("base.us").id,
                "zip": "94134",
            }
        )

    def test_controller_inherits_website_sale(self):
        self.assertTrue(issubclass(AvataxWebsiteSale, WebsiteSale))

    def test_sale_order_has_avatax_compute_method(self):
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
            }
        )
        self.assertTrue(callable(getattr(order, "_avatax_compute_tax", None)))

    def test_avatax_compute_tax_noop_on_empty_order(self):
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
            }
        )
        # _avatax_compute_tax starts with `self and self.ensure_one()` so
        # calling it on a single record with no Avatax config should return
        # early without raising.
        order._avatax_compute_tax()
