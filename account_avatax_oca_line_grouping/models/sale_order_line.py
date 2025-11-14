# -*- coding: utf-8 -*-

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _avatax_prepare_line(self, sign=1, doc_type=None):
        """
        Prepare sales order line data for Avatax.

        When company.avatax_group_lines is enabled, only the first order line
        of the order will produce a dict, aggregating all lines.
        """
        order = self.order_id
        company = order.company_id

        if company and getattr(company, "avatax_group_lines", False):
            first_line = order.order_line[:1]
            if not first_line or self != first_line[0]:
                return {}

            total_amount = 0.0
            total_discount_amount = 0.0

            for line in order.order_line:
                line_net = (
                    line.price_unit
                    * line.product_uom_qty
                    * (1 - line.discount / 100.0)
                )
                total_amount += sign * line_net

                if line.discount:
                    total_discount_amount += (
                        sign
                        * line.price_unit
                        * line.product_uom_qty
                        * line.discount
                        / 100.0
                    )

            is_discounted = bool(total_discount_amount)

            line = first_line[0]
            product = line.product_id

            item_code = None
            tax_code = None
            upc_enable = False
            avatax_config = None

            if hasattr(company, "get_avatax_config_company"):
                avatax_config = company.get_avatax_config_company()
                if avatax_config:
                    upc_enable = bool(getattr(avatax_config, "upc_enable", False))

            if product:
                if product.barcode and upc_enable:
                    item_code = "UPC:%s" % product.barcode
                else:
                    item_code = product.default_code or "ID:%d" % product.id
                tax_code = product.applicable_tax_code_id.name

            if not item_code:
                item_code = "SO:%s" % (order.name or order.id)

            description = line.name or order.name or "Combined Items"

            return {
                "qty": 1,
                "itemcode": item_code,
                "description": description,
                "discounted": is_discounted,
                "discount": total_discount_amount,
                "amount": total_amount,
                "tax_code": tax_code,
                "id": line,
                "tax_id": line.tax_id,
            }

        return super()._avatax_prepare_line(sign=sign, doc_type=doc_type)
