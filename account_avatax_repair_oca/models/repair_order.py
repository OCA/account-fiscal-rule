from odoo import api, fields, models


class Repair(models.Model):
    _inherit = "repair.order"

    amount_tax_avatax = fields.Monetary(string="AvaTax")

    hide_exemption = fields.Boolean(
        "Hide Exemption & Tax Based on shipping address",
        compute="_compute_hide_exemption",
        default=lambda self: self.env.company.get_avatax_config_company,
        help="Uncheck the this field to show exemption fields on SO/Invoice form view. "
        "Also, it will show Tax based on shipping address button",
    )

    is_avatax = fields.Boolean(compute="_compute_is_avatax")
    exemption_code = fields.Char(
        "Exemption Number",
        compute="_compute_onchange_exemption",
        readonly=False,  # New computed writeable fields
        store=True,
        help="It show the customer exemption number",
        copy=False,
    )
    exemption_code_id = fields.Many2one(
        "exemption.code",
        "Exemption Code",
        compute="_compute_onchange_exemption",
        readonly=False,  # New computed writeable fields
        store=True,
        help="It show the customer exemption code",
        copy=False,
    )
    tax_address_id = fields.Many2one(
        "res.partner",
        "Tax Address",
        readonly=True,
        states={"draft": [("readonly", False)]},
        compute="_compute_tax_address_id",
        store=True,
        copy=False,
    )
    location_code = fields.Char("Location Code", help="Origin address location code")
    calculate_tax_on_save = fields.Boolean()
    avatax_request_log = fields.Text(
        "Avatax API Request Log", readonly=True, copy=False
    )
    avatax_response_log = fields.Text(
        "Avatax API Response Log", readonly=True, copy=False
    )

    @api.model
    @api.depends("company_id", "partner_id", "partner_invoice_id", "state")
    def _compute_hide_exemption(self):
        avatax_config = self.env.company.get_avatax_config_company()
        for order in self:
            order.hide_exemption = avatax_config.hide_exemption

    @api.depends("partner_invoice_id", "tax_address_id", "company_id")
    def _compute_onchange_exemption(self):
        for repair in self.filtered(lambda x: x.state not in ["done", "cancel"]):
            invoice_partner = repair.partner_invoice_id.commercial_partner_id
            ship_to_address = repair.tax_address_id
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
                repair.company_id.id
            )
            repair.exemption_code = exemption_address.property_exemption_number
            repair.exemption_code_id = exemption_address.property_exemption_code_id

    def _create_invoices(self, group=False):
        res = super(Repair, self)._create_invoices(group)
        for repair_id in res:
            if repair_id not in res:
                continue
            repair = self.env["repair.order"].browse(repair_id)
            invoice = self.env["account.move"].browse(res[repair_id])

            invoice.write(
                {
                    "exemption_code": repair.exemption_code or "",
                    "exemption_code_id": repair.exemption_code_id.id or False,
                    "exemption_locked": True,
                    "location_code": repair.location_code or "",
                    "warehouse_id": repair.location_id.get_warehouse().id or "",
                    "tax_on_shipping_address": True,
                    "so_partner_id": repair.partner_id,
                }
            )
        return res

    @api.onchange("operations", "fees_lines")
    def onchange_reset_avatax_amount(self):
        """
        When changing quantities or prices, reset the Avatax computed amount.
        The Odoo computed tax amount will then be shown, as a reference.
        The Avatax amount will be recomputed upon document validation.
        """
        for repair in self:
            repair.amount_tax_avatax = 0
            repair.operations.write({"tax_amt_avatax": 0})
            repair.fees_lines.write({"tax_amt_avatax": 0})

    @api.depends("amount_tax_avatax")
    def _amount_tax(self):
        res = super()._amount_tax()
        for order in self:
            if order.amount_tax_avatax:
                order.update(
                    {
                        "amount_tax": order.amount_tax_avatax,
                    }
                )
        return res

    @api.depends("partner_id")
    def _compute_tax_address_id(self):
        for repair in self:
            repair.tax_address_id = repair.partner_id

    @api.depends("partner_invoice_id", "partner_id", "address_id")
    def _compute_is_avatax(self):
        repair = self.with_company(self.company_id)
        partner_invoice = repair.partner_invoice_id or repair.partner_id
        fpos = self.env["account.fiscal.position"].get_fiscal_position(
            partner_invoice.id, delivery_id=repair.address_id.id
        )
        self.is_avatax = fpos

    def _get_avatax_doc_type(self, commit=False):
        return "SalesOrder"

    def _avatax_prepare_lines(self, operations, fees_lines, doc_type=None):
        """
        Prepare the lines to use for Avatax computation.
        Returns a list of dicts
        """
        lines = [
            line._avatax_prepare_line(sign=1, doc_type=doc_type) for line in operations
        ]
        lines2 = [
            line._avatax_prepare_line(sign=1, doc_type=doc_type) for line in fees_lines
        ]
        lines.extend(lines2)
        return [x for x in lines if x]

    def _avatax_compute_tax(self):
        """Contact REST API and recompute taxes for a Sale Order"""
        self and self.ensure_one()
        doc_type = self._get_avatax_doc_type()
        Tax = self.env["account.tax"]
        avatax_config = self.company_id.get_avatax_config_company()
        if not avatax_config:
            return False
        warehouse = self.location_id.get_warehouse()
        partner = self.partner_id
        if avatax_config.use_partner_invoice_id:
            partner = self.partner_invoice_id
        taxable_lines = self._avatax_prepare_lines(self.operations, self.fees_lines)
        if taxable_lines:
            tax_result = avatax_config.create_transaction(
                fields.Date.today(),
                self.name,
                doc_type,
                partner,
                warehouse.partner_id or self.company_id.partner_id,
                self.tax_address_id or self.partner_id,
                taxable_lines,
                self.user_id,
                self.exemption_code or None,
                self.exemption_code_id.code or None,
                currency_id=self.currency_id,
                log_to_record=self,
            )
            tax_result_lines = {int(x["lineNumber"]): x for x in tax_result["lines"]}
            for line in self.operations:
                external_line_identifier = self.env.context.get(
                    "lineNumber", False
                )  # Used in tests
                line_id = external_line_identifier or line.id
                tax_result_line = tax_result_lines.get(line_id)
                if tax_result_line:
                    # Should we check the rate with the tax amount?
                    # tax_amount = tax_result_line["taxCalculated"]
                    # rate = round(tax_amount / line.price_subtotal * 100, 2)
                    rate = tax_result_line["rate"]
                    tax = Tax.get_avalara_tax(rate, doc_type)
                    if tax not in line.tax_id:
                        line_taxes = (
                            tax
                            if avatax_config.override_line_taxes
                            else tax | line.tax_id.filtered(lambda x: not x.is_avatax)
                        )
                        line.tax_id = line_taxes
                    line.tax_amt_avatax = tax_result_line["tax"]

            for line in self.fees_lines:
                tax_result_line = tax_result_lines.get(line.id)
                if tax_result_line:
                    # Should we check the rate with the tax amount?
                    # tax_amount = tax_result_line["taxCalculated"]
                    # rate = round(tax_amount / line.price_subtotal * 100, 2)
                    rate = tax_result_line["rate"]
                    tax = Tax.get_avalara_tax(rate, doc_type)
                    if tax not in line.tax_id:
                        line_taxes = (
                            tax
                            if avatax_config.override_line_taxes
                            else tax | line.tax_id.filtered(lambda x: not x.is_avatax)
                        )
                        line.tax_id = line_taxes
                    line.tax_amt_avatax = tax_result_line["tax"]

            self.amount_tax_avatax = tax_result.get("totalTax")
        return True

    def avalara_compute_taxes(self):
        """
        Use Avatax API to compute taxes.
        Sets the Taxes on each line, and lets odoo perfomr teh calculations.
        """
        for repair in self:
            if repair.is_avatax:
                repair._avatax_compute_tax()
        return True

    def action_repair_confirm(self):
        avatax_config = self.company_id.get_avatax_config_company()
        if avatax_config and avatax_config.force_address_validation:
            addr = self.tax_address_id
            if not addr.date_validation:
                # The Confirm action will be interrupted
                # if the address is not validated
                return addr.button_avatax_validate_address()
        if avatax_config:
            self.avalara_compute_taxes()
        res = super(Repair, self).action_repair_confirm()
        return res

    @api.onchange(
        "operations",
        "fees_lines",
        "tax_address_id",
        "partner_id",
    )
    def onchange_avatax_calculation(self):
        avatax_config = self.env.company.get_avatax_config_company()
        self.calculate_tax_on_save = False
        if avatax_config.repair_calculate_tax:
            if (
                self._origin.tax_address_id.street != self.tax_address_id.street
                or self._origin.partner_id != self.partner_id
            ):
                self.calculate_tax_on_save = True
                return
            for line in self.operations:
                if (
                    line._origin.product_uom_qty != line.product_uom_qty
                    or line._origin.price_unit != line.price_unit
                ):
                    self.calculate_tax_on_save = True
                    break
            for line2 in self.fees_lines:
                if (
                    line2._origin.product_uom_qty != line2.product_uom_qty
                    or line2._origin.price_unit != line2.price_unit
                ):
                    self.calculate_tax_on_save = True
                    break

    @api.model
    def create(self, vals):
        record = super(Repair, self).create(vals)
        avatax_config = self.env.company.get_avatax_config_company()
        if (
            avatax_config.repair_calculate_tax
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
        result = super(Repair, self).write(vals)
        avatax_config = self.env.company.get_avatax_config_company()
        for record in self:
            if (
                avatax_config.repair_calculate_tax
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

    def copy(self, default=None):
        repair = super().copy(default)
        avatax_config = self.env.company.get_avatax_config_company()
        if (
            avatax_config.repair_calculate_tax
            and repair.state != "done"
            and not self._context.get("skip_second_write", False)
        ):
            repair.with_context(skip_second_write=True).write(
                {
                    "calculate_tax_on_save": False,
                }
            )
            repair.avalara_compute_taxes()
        return repair
