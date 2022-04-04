from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends("warehouse_id", "company_id")
    def _compute_ship_from_address_id(self):
        super(SaleOrder, self)._compute_ship_from_address_id()
        for order in self:
            order.ship_from_address_id = (
                order.warehouse_id.partner_id or order.company_id.partner_id
            )

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        vals = {
            "warehouse_id": self.warehouse_id.id,
            "ship_from_address_id": self.ship_from_address_id.id,
        }
        invoice_vals.update(vals)
        return invoice_vals
