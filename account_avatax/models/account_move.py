import logging

from odoo import api, fields, models
from odoo.tests.common import Form

_logger = logging.getLogger(__name__)


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
    avatax_amount = fields.Float(string="AvaTax")

    @api.depends(
        "line_ids.debit",
        "line_ids.credit",
        "line_ids.currency_id",
        "line_ids.amount_currency",
        "line_ids.amount_residual",
        "line_ids.amount_residual_currency",
        "line_ids.payment_id.state",
        "avatax_amount",
    )
    def _compute_amount(self):
        super()._compute_amount()
        for inv in self:
            if inv.avatax_amount:
                inv.amount_tax = inv.avatax_amount
                inv.amount_total = inv.amount_untaxed + inv.amount_tax
                sign = self.type in ["in_refund", "out_refund"] and -1 or 1
                inv.amount_total_signed = inv.amount_total * sign

    @api.depends("tax_on_shipping_address", "partner_id", "partner_shipping_id")
    def _compute_shipping_add_id(self):
        for invoice in self:
            invoice.shipping_add_id = (
                invoice.partner_shipping_id
                if invoice.tax_on_shipping_address
                else invoice.partner_id
            )

    @api.onchange("invoice_line_ids")
    def onchange_reset_avatax_amount(self):
        """
        When changing quantities or prices, reset the Avatax computed amount.
        The Odoo computed tax amount will then be shown, as a reference.
        The Avatax amount will be recomputed upon document validation.
        """
        for inv in self:
            inv.avatax_amount = 0
            inv.invoice_line_ids.write({"tax_amt": 0})

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
    def _get_avatax_doc_type(self, commit=True):
        self.ensure_one()
        if not commit:
            doc_type = "SalesOrder"
        elif self.type == "out_refund":
            doc_type = "ReturnInvoice"
        else:
            doc_type = "SalesInvoice"
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
        doc_type = self._get_avatax_doc_type(commit=commit)
        tax_date = self.get_origin_tax_date() or self.invoice_date
        taxable_lines = self._avatax_prepare_lines(doc_type)
        tax_result = avatax_config.create_transaction(
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
            ignore_error=300 if commit else None,
        )
        # If commiting, and document exists, try unvoiding it
        # Error number 300 = GetTaxError, Expected Saved|Posted
        if commit and tax_result.get("number") == 300:
            _logger.info(
                "Document %s (%s) already exists in Avatax. "
                "Should be a voided transaction. "
                "Unvoiding and re-commiting.",
                self.number,
                doc_type,
            )
            avatax_config.unvoid_transaction(self.name, doc_type)
            avatax_config.commit_transaction(self.name, doc_type)
            return True

        tax_result_lines = {int(x["lineNumber"]): x for x in tax_result["lines"]}
        taxes_to_set = []
        lines = self.invoice_line_ids.filtered(lambda l: not l.display_type)
        for index, line in enumerate(lines):
            tax_result_line = tax_result_lines.get(line.id)
            if tax_result_line:
                rate = tax_result_line["rate"]
                tax = Tax.get_avalara_tax(rate, doc_type)
                if tax and tax not in line.tax_ids:
                    line_taxes = line.tax_ids.filtered(lambda x: not x.is_avatax)
                    taxes_to_set.append((index, line_taxes | tax))
                line.tax_amt = tax_result_line["tax"]
        self.avatax_amount = tax_result["totalTax"]

        with Form(self) as move_form:
            for index, taxes in taxes_to_set:
                with move_form.invoice_line_ids.edit(index) as line_form:
                    line_form.tax_ids.clear()
                    for tax in taxes:
                        line_form.tax_ids.add(tax)

        return True

    # Same as v12
    def avatax_compute_taxes(self, commit=False):
        """
        Called from Invoice's Action menu.
        Forces computation of the Invoice taxes
        """
        for invoice in self:
            if invoice.fiscal_position_id.is_avatax:
                invoice._avatax_compute_tax(commit=commit)
        return True

    def avatax_commit_taxes(self):
        for invoice in self:
            avatax_config = invoice.company_id.get_avatax_config_company()
            if not avatax_config.disable_tax_reporting:
                doc_type = invoice._get_avatax_doc_type()
                avatax_config.commit_transaction(invoice.name, doc_type)
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
        # to ensure correct account moves
        # However, we can't save the invoice because it wasn't assigned a
        # number yet
        self.avatax_compute_taxes(commit=False)
        super().post()
        # We can only commit to Avatax after validating the invoice
        # because we need the generated Invoice number
        self.avatax_compute_taxes(commit=True)
        return True

    # prepare_return in v12
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
        """
        Sets invoice to Draft, either from the Posted or Cancelled states
        """
        for invoice in self:
            if (
                invoice.type in ["out_invoice", "out_refund"]
                and self.fiscal_position_id.is_avatax
                and invoice.state == "posted"
            ):
                avatax = self.company_id.get_avatax_config_company()
                doc_type = invoice._get_avatax_doc_type()
                avatax.void_transaction(invoice.name, doc_type)
        return super(AccountMove, self).button_draft()


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    tax_amt = fields.Float(string="AvaTax")
    avatax_amt = fields.Float(string="AvaTax")

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
        product = line.product_id
        if product.barcode and avatax_config.upc_enable:
            item_code = "UPC:%d" % product.barcode
        else:
            item_code = product.default_code or ("ID:%d" % product.id)
        tax_code = line.product_id.applicable_tax_code_id.name
        amount = sign * line.price_unit * line.quantity * (1 - line.discount / 100.0)
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
            "itemcode": item_code,
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

    @api.onchange("price_unit", "discount", "quantity")
    def onchange_reset_tax_amt(self):
        """
        When changing quantities or prices, reset the Avatax computed amount.
        The Odoo computed tax amount will then be shown, as a reference.
        The Avatax amount will be recomputed upon document validation.
        """
        for line in self:
            line.tax_amt = 0.0

    def _get_price_total_and_subtotal(
        self,
        price_unit=None,
        quantity=None,
        discount=None,
        currency=None,
        product=None,
        partner=None,
        taxes=None,
        move_type=None,
    ):
        """ Override tax amount, if we have an Avatax calculated amount """
        self.ensure_one()
        res = super()._get_price_total_and_subtotal(
            price_unit, quantity, discount, currency, product, partner, taxes, move_type
        )
        if self.tax_amt:
            res["price_total"] = res["price_total"] + self.tax_amt
        return res
