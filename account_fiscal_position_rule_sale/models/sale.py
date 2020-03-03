#   Copyright (C) 2009-TODAY Akretion <http://www.akretion.com>
#     @author Sébastien BEAU <sebastien.beau@akretion.com>
#     @author Renato Lima <renato.lima@akretion.com>
#     @author Raphaël Valyi <raphael.valyi@akretion.com>
#   Copyright 2012 Camptocamp SA
#     @author: Guewen Baconnier
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _fiscal_position_map(self, **kwargs):
        ctx = dict(self._context)
        ctx.update({"use_domain": ("use_sale", "=", True)})
        return (
            self.env["account.fiscal.position.rule"]
            .with_context(ctx)
            .apply_fiscal_mapping(**kwargs)
        )

    def _prepare_fiscal_position_map_kwargs(self):
        self.ensure_one()
        return {
            "company_id": self.company_id,
            "partner_id": self.partner_id,
            "partner_invoice_id": self.partner_invoice_id,
            "partner_shipping_id": self.partner_shipping_id,
        }

    @api.onchange(
        "partner_id", "partner_invoice_id", "partner_shipping_id", "company_id"
    )
    def onchange_fiscal_position_map(self):
        kwargs = self._prepare_fiscal_position_map_kwargs()
        obj_fiscal_position = self._fiscal_position_map(**kwargs)
        if obj_fiscal_position:
            self.fiscal_position_id = obj_fiscal_position.id
