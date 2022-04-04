from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    warehouse_id = fields.Many2one("stock.warehouse", "Warehouse")

    @api.onchange("warehouse_id")
    def onchange_warehouse_id(self):
        if self.warehouse_id:
            if self.warehouse_id.company_id:
                self.company_id = self.warehouse_id.company_id
            if self.warehouse_id.code:
                self.location_code = self.warehouse_id.code

    def _reverse_move_vals(self, default_values, cancel=True):
        move_vals = super(AccountMove, self)._reverse_move_vals(
            default_values, cancel=cancel
        )
        move_vals.update({"warehouse_id": self.warehouse_id.id})
        return move_vals

    @api.depends("warehouse_id", "company_id")
    def _compute_ship_from_address_id(self):
        super(AccountMove, self)._compute_ship_from_address_id()
        for invoice in self:
            invoice.ship_from_address_id = (
                invoice.warehouse_id.partner_id or invoice.company_id.partner_id
            )
