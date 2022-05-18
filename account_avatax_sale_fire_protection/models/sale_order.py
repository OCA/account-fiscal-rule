# Copyright (C) 2022 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    is_fl_taxation = fields.Boolean(
        string="Florida Labor Taxable", compute="_compute_is_fl_taxation"
    )
    is_fl_address = fields.Boolean(
        string="Florida Address", compute="_compute_is_fl_address"
    )

    def _get_service_product_line(self):
        self.ensure_one()
        return self.order_line.filtered(lambda p: p.product_id.type == "service")

    def _compute_is_fl_taxation(self):
        for rec in self:
            is_fl_taxation = False
            if rec._get_avatax_condtion():
                result = rec._get_service_product_line().mapped("is_fl_tax_line")
                is_fl_taxation = result and all(result) or False
            rec.is_fl_taxation = is_fl_taxation

    def _compute_is_fl_address(self):
        for rec in self:
            is_fl_address = False
            if rec._get_avatax_condtion():
                is_fl_address = True
            rec.is_fl_address = is_fl_address

    def _get_avatax_condtion(self):
        for rec in self:
            if rec.partner_shipping_id.state_id.code == "FL":
                return True
            return False

    def _get_is_fl_taxable(self, line):
        for rec in self:
            if (
                rec.is_fl_taxation
                and line.product_id.tax_swapping_product_id
                and rec._get_avatax_condtion()
            ):
                return True
            return False

    def _get_is_fl_nontaxable(self, line):
        for rec in self:
            if not rec.is_fl_taxation and line.non_taxable_product_id:
                return True
            return False

    def _calculate_florida_product_taxation(self):
        for rec in self:
            for line in rec._get_service_product_line():
                sol_dict = {}
                if rec._get_is_fl_taxable(line):
                    if (
                        not line.non_taxable_product_id
                        and not line.taxable_product_id.id
                    ):
                        product_id = line.product_id
                        sol_dict.update(
                            {
                                "non_taxable_product_id": product_id.id,
                                "product_id": product_id.tax_swapping_product_id.id,
                                "taxable_product_id": product_id.tax_swapping_product_id.id,
                            }
                        )
                if rec._get_is_fl_nontaxable(line):
                    sol_dict.update(
                        {
                            "non_taxable_product_id": False,
                            "product_id": line.non_taxable_product_id.id,
                            "taxable_product_id": False,
                        }
                    )
                if sol_dict:
                    line.write(sol_dict)

    def avalara_compute_taxes(self):
        """
        Overwrite method for Calling _calculate_florida_product_taxation
        Use Avatax API to compute taxes.
        Sets the Taxes on each line, and lets odoo perfomr teh calculations.
        """
        for order in self:
            if order.fiscal_position_id.is_avatax:
                order._calculate_florida_product_taxation()
                order._avatax_compute_tax()
        return True


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    non_taxable_product_id = fields.Many2one(
        "product.product",
        string="Non Taxable Product",
    )
    taxable_product_id = fields.Many2one(
        "product.product",
        string="Taxable Product",
    )
    is_fl_tax_line = fields.Boolean(
        string="Florida Labor Taxable", compute="_compute_is_fl_tax_line"
    )

    def _get_fl_tax_line_compute_condtion(self):
        for rec in self:
            if (
                rec.order_id._get_avatax_condtion()
                and (
                    rec.product_id.tax_swapping_product_id
                    or rec.non_taxable_product_id.tax_swapping_product_id
                )
                and rec.product_id.type == "service"
            ):
                return True
            return False

    def _compute_is_fl_tax_line(self):
        for rec in self:
            is_fl_tax_line = False
            if rec._get_fl_tax_line_compute_condtion():
                is_fl_tax_line = True
            rec.is_fl_tax_line = is_fl_tax_line
