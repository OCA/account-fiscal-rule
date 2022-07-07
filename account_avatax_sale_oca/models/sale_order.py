from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    @api.depends("company_id", "partner_id", "partner_invoice_id", "state")
    def _compute_hide_exemption(self):
        avatax_config = self.env.company.get_avatax_config_company()
        for order in self:
            order.hide_exemption = avatax_config.hide_exemption

    hide_exemption = fields.Boolean(
        "Hide Exemption & Tax Based on shipping address",
        compute=_compute_hide_exemption,  # For past transactions visibility
        default=lambda self: self.env.company.get_avatax_config_company,
        help="Uncheck the this field to show exemption fields on SO/Invoice form view. "
        "Also, it will show Tax based on shipping address button",
    )
    tax_amount = fields.Monetary(string="AvaTax")

    @api.onchange("partner_shipping_id", "partner_id")
    def onchange_partner_shipping_id(self):
        """
        Apply the exemption number and code from the Invoice Partner Data
        We can only apply an exemption status that matches the delivery
        address Country and State.

        The setup for this is to add contact/addresses for the Invoicing Partner,
        for each of the states we can claim exepmtion for.
        """
        res = super(SaleOrder, self).onchange_partner_shipping_id()
        self.tax_on_shipping_address = bool(self.partner_shipping_id)
        return res

    @api.depends("partner_invoice_id", "tax_address_id", "company_id")
    def _compute_onchange_exemption(self):
        for order in self.filtered(lambda x: x.state not in ["done", "cancel"]):
            invoice_partner = order.partner_invoice_id.commercial_partner_id
            ship_to_address = order.tax_address_id
            # Find an exemption address matching the Country + State
            # of the Delivery address
            exemption_addresses = (
                invoice_partner | invoice_partner.child_ids
            ).filtered("property_tax_exempt")
            exemption_address_naive = exemption_addresses.filtered(
                lambda a: a.country_id == ship_to_address.country_id
                and (
                    a.state_id == ship_to_address.state_id
                    or invoice_partner.property_exemption_country_wide
                )
            )[:1]
            # Force Company to get the correct values form the Property fields
            exemption_address = exemption_address_naive.with_company(
                order.company_id.id
            )
            order.exemption_code = exemption_address.property_exemption_number
            order.exemption_code_id = exemption_address.property_exemption_code_id

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
                "so_partner_id": self.partner_id.id,
            }
        )
        return invoice_vals

    @api.onchange("order_line", "fiscal_position_id")
    def onchange_reset_avatax_amount(self):
        """
        When changing quantities or prices, reset the Avatax computed amount.
        The Odoo computed tax amount will then be shown, as a reference.
        The Avatax amount will be recomputed upon document validation.
        """
        for order in self:
            order.tax_amount = 0
            order.order_line.write({"tax_amt": 0})

    @api.depends("order_line.price_total", "order_line.product_uom_qty", "tax_amount")
    def _amount_all(self):
        """
        Compute fields amount_untaxed, amount_tax, amount_total
        Their computation needs to be overriden,
        to use the amounts returned by Avatax service, stored in specific fields.
        """
        super()._amount_all()
        for order in self:
            if order.tax_amount:
                order.update(
                    {
                        "amount_tax": order.tax_amount,
                        "amount_total": order.amount_untaxed + order.tax_amount,
                    }
                )

    @api.depends("tax_on_shipping_address", "partner_id", "partner_shipping_id")
    def _compute_tax_address_id(self):
        for invoice in self:
            invoice.tax_address_id = (
                invoice.partner_shipping_id
                if invoice.tax_on_shipping_address
                else invoice.partner_id
            )

    is_avatax = fields.Boolean(related="fiscal_position_id.is_avatax")
    exemption_code = fields.Char(
        "Exemption Number",
        compute=_compute_onchange_exemption,
        readonly=False,  # New computed writeable fields
        store=True,
        help="It show the customer exemption number",
    )
    exemption_code_id = fields.Many2one(
        "exemption.code",
        "Exemption Code",
        compute=_compute_onchange_exemption,
        readonly=False,  # New computed writeable fields
        store=True,
        help="It show the customer exemption code",
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
    )
    location_code = fields.Char("Location Code", help="Origin address location code")
    calculate_tax_on_save = fields.Boolean()
    avatax_request_log = fields.Text(
        "Avatax API Request Log", readonly=True, copy=False
    )
    avatax_response_log = fields.Text(
        "Avatax API Response Log", readonly=True, copy=False
    )

    def _get_avatax_doc_type(self, commit=False):
        return "SalesOrder"

    def _avatax_prepare_lines(self, order_lines, doc_type=None):
        """
        Prepare the lines to use for Avatax computation.
        Returns a list of dicts
        """
        lines = [
            line._avatax_prepare_line(sign=1, doc_type=doc_type)
            for line in order_lines.filtered(lambda line: not line.display_type)
        ]
        return [x for x in lines if x]

    def _avatax_compute_tax(self):
        """Contact REST API and recompute taxes for a Sale Order"""
        self and self.ensure_one()
        doc_type = self._get_avatax_doc_type()
        Tax = self.env["account.tax"]
        avatax_config = self.company_id.get_avatax_config_company()
        if not avatax_config:
            return False
        partner = self.partner_id
        if avatax_config.use_partner_invoice_id:
            partner = self.partner_invoice_id
        taxable_lines = self._avatax_prepare_lines(self.order_line)
        tax_result = avatax_config.create_transaction(
            self.date_order,
            self.name,
            doc_type,
            partner,
            self.warehouse_id.partner_id or self.company_id.partner_id,
            self.tax_address_id or self.partner_id,
            taxable_lines,
            self.user_id,
            self.exemption_code or None,
            self.exemption_code_id.code or None,
            currency_id=self.currency_id,
            log_to_record=self,
        )
        tax_result_lines = {int(x["lineNumber"]): x for x in tax_result["lines"]}
        for line in self.order_line:
            tax_result_line = tax_result_lines.get(line.id)
            if tax_result_line:
                fixed_tax_amount = tax_result_line["tax"]
                retail_delivery_fee_tax = line.retail_delivery_fee_id.tax_ids
                retail_delivery_fee_tax_match = retail_delivery_fee_tax.filtered(
                    lambda t: t.amount == fixed_tax_amount
                )
                # Should we check the rate with the tax amount?
                # tax_amount = tax_result_line["taxCalculated"]
                # rate = round(tax_amount / line.price_subtotal * 100, 2)
                if not line.retail_delivery_fee:
                    rate = tax_result_line["rate"]
                    tax = Tax.get_avalara_tax(rate, doc_type)
                # setting Retail Delivery Fee from avatax salestax
                elif retail_delivery_fee_tax_match:
                    tax = retail_delivery_fee_tax_match
                # tax amount doesn't match means creating copy record with new amount
                elif retail_delivery_fee_tax:
                    retail_delivery_fee_tax = retail_delivery_fee_tax[0]
                    vals = {
                        "amount": fixed_tax_amount,
                        "name": f"{retail_delivery_fee_tax.name} - {fixed_tax_amount}",
                    }
                    tax = retail_delivery_fee_tax.sudo().copy(default=vals)
                    line.retail_delivery_fee_id.tax_ids |= tax
                if tax not in line.tax_id:
                    line_taxes = (
                        tax
                        if avatax_config.override_line_taxes
                        else tax | line.tax_id.filtered(lambda x: not x.is_avatax)
                    )
                    line.tax_id = line_taxes
                line.tax_amt = tax_result_line["tax"]
        self.tax_amount = tax_result.get("totalTax")
        return True

    def add_retail_product(self):
        order_line = self.env["sale.order.line"].sudo()
        avatax_config = self.company_id.get_avatax_config_company()
        if avatax_config:
            retail_group = avatax_config.retail_group_ids.filtered(
                lambda r: r.country_id.code == self.tax_address_id.country_id.code
                and r.state_id.code == self.tax_address_id.state_id.code
            )
            if retail_group:
                retail_group = retail_group[0]
                order_line = self.order_line.filtered(
                    lambda l: l.retail_delivery_fee
                    and l.product_id == retail_group.product_id
                )
                if not order_line:
                    temp_order_line = order_line.new(
                        {
                            "product_id": retail_group.product_id.id,
                            "price_unit": retail_group.amount,
                            "retail_delivery_fee": True,
                            "retail_delivery_fee_id": retail_group.id,
                            "order_id": self.id,
                        }
                    )
                    for method in temp_order_line._onchange_methods.get(
                        "product_id", ()
                    ):
                        method(temp_order_line)
                    vals = temp_order_line._convert_to_write(temp_order_line._cache)
                    vals["price_unit"] = retail_group.amount
                    order_line = order_line.create(vals)
                else:
                    order_line_to_edit = order_line.filtered(
                        lambda o: o.retail_delivery_fee_id
                        and o.price_unit != retail_group.amount
                    )
                    if order_line_to_edit:
                        self.write(
                            {
                                "order_line": [
                                    (
                                        1,
                                        order_line_to_edit.id,
                                        {"price_unit": retail_group.amount},
                                    )
                                ]
                            }
                        )
            order_to_unlink = self.order_line.filtered(
                lambda o: o.retail_delivery_fee
                and o.retail_delivery_fee_id != retail_group
            )
            if order_to_unlink:
                self.write({"order_line": [(2, x.id) for x in order_to_unlink]})

    def avalara_compute_taxes(self):
        """
        Use Avatax API to compute taxes.
        Sets the Taxes on each line, and lets odoo perfomr teh calculations.
        """
        for order in self:
            if order.fiscal_position_id.is_avatax:
                order.add_retail_product()
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
        if avatax_config:
            self.avalara_compute_taxes()
        res = super(SaleOrder, self).action_confirm()
        return res

    @api.onchange(
        "order_line",
        "tax_on_shipping_address",
        "tax_address_id",
        "partner_id",
    )
    def onchange_avatax_calculation(self):
        avatax_config = self.env.company.get_avatax_config_company()
        self.calculate_tax_on_save = False
        if avatax_config.sale_calculate_tax:
            if (
                self._origin.tax_address_id.street != self.tax_address_id.street
                or self._origin.partner_id != self.partner_id
                or self._origin.tax_on_shipping_address != self.tax_on_shipping_address
            ):
                self.calculate_tax_on_save = True
                return
            for line in self.order_line:
                if (
                    line._origin.product_uom_qty != line.product_uom_qty
                    or line._origin.discount != line.discount
                    or line._origin.price_unit != line.price_unit
                    or line._origin.warehouse_id != line.warehouse_id
                ):
                    self.calculate_tax_on_save = True
                    break

    @api.model
    def create(self, vals):
        record = super(SaleOrder, self).create(vals)
        avatax_config = self.env.company.get_avatax_config_company()
        if (
            avatax_config.sale_calculate_tax
            and record.calculate_tax_on_save
            and not self._context.get("skip_second_write", False)
        ):
            record.with_context(skip_second_write=True).write(
                {
                    "calculate_tax_on_save": False,
                }
            )
            record.avalara_compute_taxes()
        return record

    def write(self, vals):
        result = super(SaleOrder, self).write(vals)
        avatax_config = self.env.company.get_avatax_config_company()
        for record in self:
            if (
                avatax_config.sale_calculate_tax
                and record.calculate_tax_on_save
                and record.state != "done"
                and not self._context.get("skip_second_write", False)
            ):
                record.with_context(skip_second_write=True).write(
                    {
                        "calculate_tax_on_save": False,
                    }
                )
                record.avalara_compute_taxes()
        return result


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    tax_amt = fields.Monetary(string="AvaTax")
    retail_delivery_fee = fields.Boolean()
    retail_delivery_fee_id = fields.Many2one("retail.group")

    def _avatax_prepare_line(self, sign=1, doc_type=None):
        """
        Prepare a line to use for Avatax computation.
        Returns a dict
        """
        line = self
        res = {}
        # Add UPC to product item code
        avatax_config = line.company_id.get_avatax_config_company()
        product = line.product_id
        if product.barcode and avatax_config.upc_enable:
            item_code = "UPC:%d" % product.barcode
        else:
            item_code = product.default_code or ("ID:%d" % product.id)
        tax_code = line.product_id.applicable_tax_code_id.name
        amount = (
            sign * line.price_unit * line.product_uom_qty * (1 - line.discount / 100.0)
        )
        # Calculate discount amount
        discount_amount = 0.0
        is_discounted = False
        if line.discount:
            discount_amount = (
                sign * line.price_unit * line.product_uom_qty * line.discount / 100.0
            )
            is_discounted = True
        res = {
            "qty": line.product_uom_qty,
            "itemcode": item_code,
            "description": line.name,
            "discounted": is_discounted,
            "discount": discount_amount,
            "amount": amount,
            "tax_code": tax_code,
            "id": line,
            "tax_id": line.tax_id,
        }
        return res

    def _prepare_invoice_line(self, **optional_values):
        invoice_line_vals = super(SaleOrderLine, self)._prepare_invoice_line(
            **optional_values
        )
        invoice_line_vals.update(
            {
                "retail_delivery_fee": self.retail_delivery_fee,
                "retail_delivery_fee_id": self.retail_delivery_fee_id,
            }
        )
        return invoice_line_vals

    @api.onchange("product_uom_qty", "discount", "price_unit", "tax_id")
    def onchange_reset_avatax_amount(self):
        """
        When changing quantities or prices, reset the Avatax computed amount.
        The Odoo computed tax amount will then be shown, as a reference.
        The Avatax amount will be recomputed upon document validation.
        """
        for line in self:
            line.tax_amt = 0
            line.order_id.tax_amount = 0

    @api.onchange("product_id")
    def product_id_change(self):
        super(SaleOrderLine, self).product_id_change()
        avatax_config = self.company_id.get_avatax_config_company()
        if avatax_config:
            order = self.order_id
            retail_group = avatax_config.retail_group_ids.filtered(
                lambda r: r.country_id.code == order.tax_address_id.country_id.code
                and r.state_id.code == order.tax_address_id.state_id.code
            )
            if retail_group and self.product_id == retail_group.product_id:
                self.retail_delivery_fee = True
                retail_line = (
                    order.order_line.filtered(
                        lambda l: l.retail_delivery_fee and l.retail_delivery_fee_id
                    )
                    - self
                )
                if not retail_line:
                    self.retail_delivery_fee_id = retail_group.id

    @api.depends("product_uom_qty", "discount", "price_unit", "tax_id", "tax_amt")
    def _compute_amount(self):
        """
        If we have a Avatax computed amount, use it instead of the Odoo computed one
        """
        super()._compute_amount()
        for line in self:
            if line.tax_amt:  # Has Avatax computed amount
                vals = {
                    "price_tax": line.tax_amt,
                    "price_total": line.price_subtotal + line.tax_amt,
                }
                line.update(vals)
