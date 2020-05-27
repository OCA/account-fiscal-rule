from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange("partner_id")
    def onchange_partner_id(self):
        """Override method to add new fields values.
        @param part- update vals with partner exemption number and code,
        also check address validation by avalara
        """
        super(SaleOrder, self).onchange_partner_id()
        self.exemption_code = self.partner_id.exemption_number or ""
        self.exemption_code_id = self.partner_id.exemption_code_id.id or None
        self.tax_on_shipping_address = bool(self.partner_shipping_id)

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals.update(
            {
                "exemption_code": self.exemption_code or "",
                "exemption_code_id": self.exemption_code_id.id or False,
                "exemption_locked": True,
                "location_code": self.location_code or "",
                "warehouse_id": self.warehouse_id.id or "",
                "tax_on_shipping_address": self.tax_on_shipping_address,
            }
        )
        return invoice_vals

    @api.depends("tax_on_shipping_address", "partner_id", "partner_shipping_id")
    def _compute_tax_address_id(self):
        for invoice in self:
            invoice.tax_address_id = (
                invoice.partner_shipping_id
                if invoice.tax_on_shipping_address
                else invoice.partner_id
            )

    exemption_code = fields.Char(
        "Exemption Number", help="It show the customer exemption number"
    )
    exemption_code_id = fields.Many2one(
        "exemption.code", "Exemption Code", help="It show the customer exemption code"
    )
    tax_on_shipping_address = fields.Boolean(
        "Tax based on shipping address", default=True
    )
    tax_address_id = fields.Many2one(
        "res.partner",
        "Tax Address",
        readonly=True,
        states={"draft": [("readonly", False)]},
        compute="_compute_tax_address_id",
        store=True,
        oldname="tax_add_id",
    )
    location_code = fields.Char("Location Code", help="Origin address location code")

    def _get_avatax_doc_type(self, commit=False):
        return "SalesOrder"

    def _avatax_prepare_lines(self, doc_type=None):
        """
        Prepare the lines to use for Avatax computation.
        Returns a list of dicts
        """
        lines = [
            line._avatax_prepare_line(sign=1, doc_type=doc_type)
            for line in self.order_line
        ]
        return lines

    def _avatax_compute_tax(self):
        """ Contact REST API and recompute taxes for a Sale Order """
        self and self.ensure_one()
        doc_type = self._get_avatax_doc_type()
        Tax = self.env["account.tax"]
        avatax_config = self.company_id.get_avatax_config_company()
        taxable_lines = self._avatax_prepare_lines(self.order_line)
        tax_result = Tax._get_compute_tax(
            avatax_config,
            self.date_order,
            self.name,
            doc_type,
            self.partner_id,
            self.warehouse_id.partner_id or self.company_id.partner_id,
            self.partner_shipping_id or self.partner_id,
            taxable_lines,
            self.user_id,
            self.exemption_code or None,
            self.exemption_code_id.code or None,
            currency_id=self.currency_id,
        )
        tax_result_lines = {int(x["lineNumber"]): x for x in tax_result["lines"]}
        for line in self.order_line:
            tax_result_line = tax_result_lines.get(line.id)
            if tax_result_line:
                # Should we check the rate with the tax amount?
                # tax_amount = tax_result_line["taxCalculated"]
                # rate = round(tax_amount / line.price_subtotal * 100, 2)
                rate = round(
                    sum(x["rate"] for x in tax_result_line["details"]) * 100, 4
                )
                tax = Tax.get_avalara_tax(rate, doc_type)
                if tax not in line.tax_id:
                    line_taxes = line.tax_id.filtered(lambda x: not x.is_avatax)
                    line.tax_id = line_taxes | tax
        return True

    def avalara_compute_taxes(self):
        """
        Use Avatax API to compute taxes.
        Sets the Taxes on each line, and lets odoo perfomr teh calculations.
        """
        for order in self:
            if order.fiscal_position_id.is_avatax:
                order._avatax_compute_tax()
        return True

    def action_confirm(self):
        avatax_config = self.company_id.get_avatax_config_company()
        if avatax_config and avatax_config.force_address_validation:
            for addr in [self.partner_id, self.partner_shipping_id]:
                if not addr.date_validation:
                    # The Confirm action will be interrupted
                    # if the address is not validated
                    return addr.button_avatax_validate_address()
        res = super(SaleOrder, self).action_confirm()
        if avatax_config:
            self.avalara_compute_taxes()
        return res


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _avatax_prepare_line(self, sign=1, doc_type=None):
        """
        Prepare a line to use for Avatax computation.
        Returns a dict
        """
        line = self
        res = {}
        # Add UPC to product item code
        avatax_config = line.company_id.get_avatax_config_company()
        if line.product_id.barcode and avatax_config.upc_enable:
            item_code = "upc:" + line.product_id.barcode
        else:
            item_code = line.product_id.default_code
        tax_code = (
            line.product_id.tax_code_id.name
            or line.product_id.categ_id.tax_code_id.name
        )
        amount = (
            sign
            * line.price_unit
            * line.product_uom_qty
            * (1 - line.discount / 100.0)
        )
        # Calculate discount amount
        discount_amount = 0.0
        is_discounted = False
        if line.discount:
            discount_amount = (
                sign
                * line.price_unit
                * line.product_uom_qty
                * line.discount
                / 100.0
            )
            is_discounted = True
        res = {
            "qty": line.product_uom_qty,
            "itemcode": line.product_id and item_code or None,
            "description": line.name,
            "discounted": is_discounted,
            "discount": discount_amount,
            "amount": amount,
            "tax_code": tax_code,
            "id": line,
            "tax_id": line.tax_id,
        }
        return res
