# Copyright 2026 Akretion
# @author Guillaume MASSON <guillaume.masson@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _get_eu_rule_delivery(self):
        """Return the effective delivery address for EU fiscal position resolution.

        In a standard purchase, goods are delivered to the company's warehouse.
        In a dropship purchase, goods are delivered directly to the end customer
        via dest_address_id (available when purchase_stock is installed).

        Both fields belong to purchase_stock and are absent when only the base
        purchase module is installed. A defensive hasattr() check is used so
        that this module remains functional without purchase_stock.

        :returns: res.partner record or None
        """
        self.ensure_one()
        # dest_address_id and picking_type_id are defined in purchase_stock.
        dest = (
            self.dest_address_id
            if hasattr(self, "dest_address_id") and self.dest_address_id
            else None
        )
        if dest:
            return dest
        warehouse_partner = (
            self.picking_type_id.warehouse_id.partner_id
            if hasattr(self, "picking_type_id") and self.picking_type_id
            else None
        )
        return warehouse_partner or None

    @api.onchange("partner_id", "company_id")
    def onchange_partner_id(self):
        """Override to pass the seller and delivery address to
        _get_fiscal_position().

        In a purchase order the triplet is inverted compared to a sale order:
        - seller   = partner_id (the supplier / vendor)
        - buyer    = company_id.partner_id (the purchasing company)
        - delivery = dest_address_id (dropship) or warehouse address (standard)

        This ensures that a French supplier invoicing a UK subsidiary with
        dropship delivery to Ireland is correctly treated as an export (0% VAT)
        rather than being assigned an OSS Irish fiscal position.
        """
        res = super().onchange_partner_id()
        if self.partner_id:
            self = self.with_company(self.company_id)
            self.fiscal_position_id = (
                self.env["account.fiscal.position"]
                .with_context(fp_eu_seller=self.partner_id)
                ._get_fiscal_position(
                    self.company_id.partner_id, delivery=self._get_eu_rule_delivery()
                )
            )
        return res

    def _prepare_invoice(self):
        """Override to pass the seller to _get_fiscal_position() in the
        fallback call that occurs when fiscal_position_id is not set.
        """
        vals = super()._prepare_invoice()
        if not self.fiscal_position_id:
            partner_invoice = self.env["res.partner"].browse(
                self.partner_id.address_get(["invoice"])["invoice"]
            )
            vals["fiscal_position_id"] = (
                self.env["account.fiscal.position"]
                .with_company(self.company_id)
                .with_context(fp_eu_seller=partner_invoice)
                ._get_fiscal_position(
                    self.company_id.partner_id, delivery=self._get_eu_rule_delivery()
                )
            ).id
        return vals
