from odoo import api, fields, models
from odoo.tests.common import Form


class AccountMove(models.Model):
    """Inherit to implement the tax calculation using avatax API"""

    _inherit = "account.move"

    @api.onchange("partner_id", "company_id")
    def _onchange_partner_id(self):
        res = super(AccountMove, self)._onchange_partner_id()
        if not self.exemption_locked:
            self.exemption_code = self.partner_id.exemption_number or ""
            self.exemption_code_id = self.partner_id.exemption_code_id.id or None
        return res

    @api.onchange("warehouse_id")
    def onchange_warehouse_id(self):
        if self.warehouse_id:
            if self.warehouse_id.company_id:
                self.company_id = self.warehouse_id.company_id
            if self.warehouse_id.code:
                self.location_code = self.warehouse_id.code

    # TODo: replace with "ref" ?
    invoice_doc_no = fields.Char(
        "Source/Ref Invoice No",
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="Reference of the invoice",
    )
    exemption_code = fields.Char(
        "Exemption Number", help="It show the customer exemption number"
    )
    exemption_code_id = fields.Many2one(
        "exemption.code", "Exemption Code", help="It show the customer exemption code"
    )
    exemption_locked = fields.Boolean(
        help="Exemption code won't be automatically changed, "
        "for instance, when changing the Customer."
    )
    tax_on_shipping_address = fields.Boolean(
        "Tax based on shipping address", default=True
    )
    shipping_add_id = fields.Many2one(
        "res.partner", "Tax Shipping Address", compute="_compute_shipping_add_id"
    )
    location_code = fields.Char(
        "Location Code", readonly=True, states={"draft": [("readonly", False)]}
    )
    warehouse_id = fields.Many2one("stock.warehouse", "Warehouse")
    tax_amount = fields.Monetary(
        string="AvaTax", store=True, readonly=True, currency_field="company_currency_id"
    )

    @api.depends("tax_on_shipping_address", "partner_id", "partner_shipping_id")
    def _compute_shipping_add_id(self):
        for invoice in self:
            invoice.shipping_add_id = (
                invoice.partner_shipping_id
                if invoice.tax_on_shipping_address
                else invoice.partner_id
            )

    # Same as v12
    def get_origin_tax_date(self):
        for inv_obj in self:
            if inv_obj.invoice_origin:
                a = inv_obj.invoice_origin
                if len(a.split(":")) > 1:
                    inv_origin = a.split(":")[1]
                else:
                    inv_origin = a.split(":")[0]
                inv_ids = self.search([("name", "=", inv_origin)])
                for invoice in inv_ids:
                    if invoice.invoice_date:
                        return invoice.invoice_date
                    else:
                        return inv_obj.invoice_date
        return False

    # Same as v12
    def _get_avatax_doc_type(self, commit=False):
        self.ensure_one()
        if self.type == "out_refund":
            doc_type = "ReturnInvoice"
        elif commit:
            doc_type = "SalesInvoice"
        else:
            doc_type = "SalesOrder"
        return doc_type

    # Same as v12
    def _avatax_prepare_lines(self, doc_type=None):
        """
        Prepare the lines to use for Avatax computation.
        Returns a list of dicts
        """
        sign = self.type == "out_invoice" and 1 or -1
        lines = [
            line._avatax_prepare_line(sign, doc_type) for line in self.invoice_line_ids
        ]
        return lines

    # Same as v12
    def _avatax_compute_tax(self, commit=False):
        """ Contact REST API and recompute taxes for a Sale Order """
        self and self.ensure_one()
        Tax = self.env["account.tax"]
        avatax_config = self.company_id.get_avatax_config_company()
        commit = commit and not avatax_config.disable_tax_reporting
        doc_type = self._get_avatax_doc_type(commit)
        tax_date = self.get_origin_tax_date() or self.invoice_date
        taxable_lines = self._avatax_prepare_lines(doc_type)
        tax_result = Tax._get_compute_tax(
            avatax_config,
            self.invoice_date or fields.Date.today(),
            self.name,
            doc_type,
            self.partner_id,
            self.warehouse_id.partner_id or self.company_id.partner_id,
            self.partner_shipping_id or self.partner_id,
            taxable_lines,
            self.user_id,
            self.exemption_code or None,
            self.exemption_code_id.code or None,
            commit,
            tax_date,
            self.invoice_doc_no,
            self.location_code or "",
            is_override=self.type == "out_refund",
            currency_id=self.currency_id,
        )

        tax_result_lines = {int(x["lineNumber"]): x for x in tax_result["lines"]}
        taxes_to_set = []
        lines = self.invoice_line_ids.filtered(lambda l: not l.display_type)
        for index, line in enumerate(lines):
            tax_result_line = tax_result_lines.get(line.id)
            if tax_result_line:
                # Should we check the rate with the tax amount?
                # tax_amount = tax_result_line["taxCalculated"]
                # rate = round(tax_amount / line.price_subtotal * 100, 2)
                rate = round(
                    sum(x["rate"] for x in tax_result_line["details"]) * 100, 4
                )
                tax = Tax.get_avalara_tax(rate, doc_type)
                if tax not in line.tax_ids:
                    line_taxes = line.tax_ids.filtered(lambda x: not x.is_avatax)
                    taxes_to_set.append((index, line_taxes | tax))

        with Form(self) as move_form:
            for index, taxes in taxes_to_set:
                with move_form.invoice_line_ids.edit(index) as line_form:
                    line_form.tax_ids.clear()
                    for tax in taxes:
                        line_form.tax_ids.add(tax)

        return True

    # Same as v12
    def avatax_compute_taxes(self, commit_avatax=False):
        """
        Called from Invoice's Action menu.
        Forces computation of the Invoice taxes
        """
        for invoice in self:
            if invoice.fiscal_position_id.is_avatax:
                invoice._avatax_compute_tax(commit=commit_avatax)
        return True

    # action_invoice_open in v12
    def post(self):
        avatax_config = self.company_id.get_avatax_config_company()
        if avatax_config and avatax_config.force_address_validation:
            for addr in [self.partner_id, self.partner_shipping_id]:
                if not addr.date_validation:
                    # The Validate action will be interrupted
                    # if the address is not validated
                    return addr.button_avatax_validate_address()
        # We should compute taxes before validating the invoice
        # , to ensure correct account moves
        # We can only commit to Avatax after validating the invoice
        # , because we need the generated Invoice number
        self.avatax_compute_taxes(commit_avatax=False)
        super().post()
        self.avatax_compute_taxes(commit_avatax=True)
        return True

    # prepare_redunf in v12
    def _reverse_move_vals(self, default_values, cancel=True):
        # OVERRIDE
        # Don't keep anglo-saxon lines if not cancelling an existing invoice.
        move_vals = super(AccountMove, self)._reverse_move_vals(
            default_values, cancel=cancel
        )
        move_vals.update(
            {
                "invoice_doc_no": self.name,
                "invoice_date": self.invoice_date,
                "tax_on_shipping_address": self.tax_on_shipping_address,
                "warehouse_id": self.warehouse_id.id,
                "location_code": self.location_code,
                "exemption_code": self.exemption_code or "",
                "exemption_code_id": self.exemption_code_id.id or None,
                "shipping_add_id": self.shipping_add_id.id,
            }
        )
        return move_vals

    # action_cancel in v12
    def button_draft(self):
        account_tax_obj = self.env["account.tax"]
        avatax_config = self.company_id.get_avatax_config_company()
        for invoice in self:
            if (
                invoice.type in ["out_invoice", "out_refund"]
                and self.fiscal_position_id.is_avatax
                and invoice.partner_id.country_id in avatax_config.country_ids
                and invoice.state != "draft"
            ):
                doc_type = (
                    invoice.type == "out_invoice" and "SalesInvoice" or "ReturnInvoice"
                )
                account_tax_obj.cancel_tax(
                    avatax_config, invoice.name, doc_type, "DocVoided"
                )
        return super(AccountMove, self).button_draft()


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    # Same in v12
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
            sign * line.price_unit * line.quantity * (1 - line.discount / 100.0)
        )
        # Calculate discount amount
        discount_amount = 0.0
        is_discounted = False
        if line.discount:
            discount_amount = (
                sign * line.price_unit * line.quantity * line.discount / 100.0
            )
            is_discounted = True
        res = {
            "qty": line.quantity,
            "itemcode": line.product_id and item_code or None,
            "description": line.name,
            "discounted": is_discounted,
            "discount": discount_amount,
            "amount": amount,
            "tax_code": tax_code,
            "id": line,
            "account_id": line.account_id.id,
            "tax_id": line.tax_ids,
        }
        return res
