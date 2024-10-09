import logging

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    """Inherit to implement the tax calculation using avatax API"""

    _inherit = "account.move"

    @api.depends("partner_shipping_id", "partner_id", "company_id")
    def _compute_onchange_exemption(self):
        """
        Set the exemption to use for the Invoice.
        An exemption can be applied if
        there an exemption for the delivery address Country + State
        - Get the delivery address Country & State
        - Search the invoiced commercial partner addresses
          for an exemption in this Country & State
        - In case there is a "country wide" exemption, use it.

        Example:
        - ACME company partner, USA CA, has exemption status
        - ACME Invoicing address, USA CA, no exemption status
        - ACME Delivery address, USA CA, no exemption status

        Invoice to ACME Invoicing, Shipped to ACME Delivery with be exempt.

        For this to work properly, the "exemption_lock" is no longer supported.
        """
        for invoice in self.filtered(lambda x: x.state == "draft"):
            invoice_partner = invoice.partner_id.commercial_partner_id
            ship_to_address = (
                hasattr(invoice, "partner_shipping_id")
                and invoice.partner_shipping_id
                or invoice_partner
            )
            # Find an exemption address matching the Country + State
            # of the Delivery address
            exemption_addresses = (
                invoice_partner | invoice_partner.child_ids
            ).filtered("property_tax_exempt")

            exemption_address_naive = exemption_addresses.filtered(
                lambda a,
                ship_to_address=ship_to_address,
                invoice_partner=invoice_partner: a.country_id
                == ship_to_address.country_id
                and (
                    a.state_id == ship_to_address.state_id
                    or invoice_partner.property_exemption_country_wide
                )
            )[:1]
            # Force Company to get the correct values from the Property fields
            exemption_address = exemption_address_naive.with_company(
                invoice.company_id.id
            )
            invoice.exemption_code = exemption_address.property_exemption_number
            invoice.exemption_code_id = exemption_address.property_exemption_code_id

    @api.onchange("warehouse_id")
    def onchange_warehouse_id(self):
        if self.warehouse_id:
            if self.warehouse_id.company_id:
                self.company_id = self.warehouse_id.company_id
            if self.warehouse_id.code:
                self.location_code = self.warehouse_id.code

    is_avatax = fields.Boolean(related="fiscal_position_id.is_avatax")
    invoice_doc_no = fields.Char(
        "Source/Ref Invoice No",
        readonly=True,
        help="Reference of the invoice",
    )
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
    exemption_locked = fields.Boolean(
        help="Exemption code won't be automatically changed, "
        "for instance, when changing the Customer."
    )
    tax_on_shipping_address = fields.Boolean(
        "Tax based on shipping address", default=True
    )
    tax_address_id = fields.Many2one(
        "res.partner", "Tax Shipping Address", compute="_compute_tax_address_id"
    )
    location_code = fields.Char()
    warehouse_id = fields.Many2one("stock.warehouse", "Warehouse")
    avatax_amount = fields.Float(string="AvaTax", copy=False)
    calculate_tax_on_save = fields.Boolean()
    so_partner_id = fields.Many2one(comodel_name="res.partner", string="SO Partner")
    avatax_request_log = fields.Text(
        "Avatax API Request Log", readonly=True, copy=False
    )
    avatax_response_log = fields.Text(
        "Avatax API Response Log", readonly=True, copy=False
    )

    @api.model
    @api.depends("company_id")
    def _compute_hide_exemption(self):
        avatax_config = self.env.company.get_avatax_config_company()
        for inv in self:
            inv.hide_exemption = avatax_config.hide_exemption

    hide_exemption = fields.Boolean(
        "Hide Exemption & Tax Based on shipping address",
        compute=_compute_hide_exemption,  # For past transactions visibility
        default=lambda self: self.env.company.get_avatax_config_company,
        help="Uncheck the this field to show exemption fields on SO/Invoice form view. "
        "Also, it will show Tax based on shipping address button",
    )

    @api.depends("tax_on_shipping_address", "partner_id", "partner_shipping_id")
    def _compute_tax_address_id(self):
        for invoice in self:
            invoice.tax_address_id = (
                invoice.partner_shipping_id
                if invoice.tax_on_shipping_address
                else invoice.partner_id
            )

    @api.onchange("tax_address_id", "fiscal_position_id")
    def onchange_reset_avatax_amount(self):
        """
        When changing quantities or prices, reset the Avatax computed amount.
        The Odoo computed tax amount will then be shown, as a reference.
        The Avatax amount will be recomputed upon document validation.
        """
        for inv in self:
            inv.avatax_amount = 0
            for line in inv.invoice_line_ids:
                line.avatax_amt_line = 0

    # Same as v12
    def get_origin_tax_date(self):
        if self.invoice_doc_no:
            orig_invoice = self.search(
                [
                    ("name", "=", self.invoice_doc_no),
                    ("partner_id", "=", self.partner_id.id),
                ]
            )
            return orig_invoice.invoice_date
        return False

    # Same as v12
    def _get_avatax_doc_type(self, commit=True):
        self.ensure_one()
        avatax_config = self.company_id.get_avatax_config_company()
        if avatax_config.disable_tax_reporting:
            commit = False
        if "refund" in self.move_type:
            doc_type = "ReturnInvoice" if commit else "ReturnOrder"
        else:
            doc_type = "SalesInvoice" if commit else "SalesOrder"
        return doc_type

    # Same as v12
    def _avatax_prepare_lines(self, doc_type=None):
        """
        Prepare the lines to use for Avatax computation.
        Returns a list of dicts
        """
        sign = 1 if self.move_type.startswith("out") else -1
        lines = [
            line._avatax_prepare_line(sign, doc_type)
            for line in self.invoice_line_ids
            if line.price_subtotal or line.quantity
        ]
        return [x for x in lines if x]

    # Same as v12
    def _avatax_compute_tax(self, commit=False):
        """Contact REST API and recompute taxes for a Sale Order"""
        # Override to handle lines with split taxes (e.g. TN)
        self and self.ensure_one()
        avatax_config = self.company_id.get_avatax_config_company()
        if not avatax_config:
            # Skip Avatax computation if no configuration is found
            return
        doc_type = self._get_avatax_doc_type(commit=commit)
        tax_date = self.get_origin_tax_date() or self.invoice_date
        taxable_lines = self._avatax_prepare_lines(doc_type)
        tax_result = avatax_config.create_transaction(
            self.invoice_date or fields.Date.today(),
            self.name,
            doc_type,
            self.so_partner_id
            if self.so_partner_id and avatax_config.use_so_partner_id
            else self.partner_id,
            self.warehouse_id.partner_id or self.company_id.partner_id,
            self.tax_address_id or self.partner_id,
            taxable_lines,
            self.user_id,
            self.exemption_code or None,
            self.exemption_code_id.code or None,
            commit,
            tax_date,
            # TODO: can we report self.invoice_doc_no?
            self.name if self.move_type == "out_refund" else "",
            self.location_code or "",
            is_override=self.move_type == "out_refund",
            currency_id=self.currency_id,
            ignore_error=300 if commit else None,
            log_to_record=self,
        )
        # If commiting, and document exists, try unvoiding it
        # Error number 300 = GetTaxError, Expected Saved|Posted
        if commit and tax_result.get("number") == 300:
            _logger.info(
                "Document %s (%s) already exists in Avatax. "
                "Should be a voided transaction. "
                "Unvoiding and re-commiting.",
                self.name,
                doc_type,
            )
            avatax_config.unvoid_transaction(self.name, doc_type)
            avatax_config.commit_transaction(self.name, doc_type)
            return tax_result

        if self.state == "draft":
            Tax = self.env["account.tax"]
            tax_result_lines = {int(x["lineNumber"]): x for x in tax_result["lines"]}
            taxes_to_set = {}
            for line in self.invoice_line_ids:
                tax_result_line = tax_result_lines.get(line.id)
                if tax_result_line:
                    # rate = tax_result_line.get("rate", 0.0)
                    tax_calculation = 0.0
                    if tax_result_line["taxableAmount"]:
                        tax_calculation = (
                            tax_result_line["taxCalculated"]
                            / tax_result_line["taxableAmount"]
                        )
                    rate = round(tax_calculation * 100, 4)
                    tax = Tax.get_avalara_tax(rate, doc_type)
                    if tax and tax not in line.tax_ids:
                        line_taxes = line.tax_ids.filtered(lambda x: not x.is_avatax)
                        taxes_to_set[line.id] = line_taxes | tax
                    line.avatax_amt_line = tax_result_line["tax"]
            self.with_context(check_move_validity=False).avatax_amount = tax_result[
                "totalTax"
            ]
            container = {"records": self}

            # Set Taxes on lines in a way that properly triggers onchanges
            # This same approach is also used by the official account_taxcloud connector

            # for index, taxes in taxes_to_set:
            #     # Access the invoice line by index
            #     line = self.invoice_line_ids[index]
            #     # Update the tax_ids field
            #     line.write({"tax_ids": [(6, 0, [tax.id for tax in taxes])]})

            with (
                self.with_context(
                    avatax_invoice=self, check_move_validity=False
                )._sync_dynamic_lines(container),
                self.line_ids.mapped("move_id")._check_balanced(container),
            ):
                for line_id in taxes_to_set.keys():
                    line = self.invoice_line_ids.filtered(
                        lambda x, line_id=line_id: x.id == line_id
                    )
                    line.write({"tax_ids": [(6, 0, [])]})
                    line.with_context(
                        avatax_invoice=self, check_move_validity=False
                    ).write({"tax_ids": taxes_to_set.get(line_id).ids})
            # After taxes are changed is needed to force compute taxes again,
            # in 16 version change of tax doesn't trigger compute of taxes
            # on header for unknown reason
            self._compute_amount()
            if float_compare(
                self.amount_untaxed + max(self.amount_tax, abs(self.avatax_amount)),
                self.amount_residual,
                precision_rounding=self.currency_id.rounding or 0.001,
            ):
                taxes_data = {
                    iline.id: iline.tax_ids for iline in self.invoice_line_ids
                }
                self.invoice_line_ids.write({"tax_ids": [(6, 0, [])]})
                for line in self.invoice_line_ids:
                    line.write({"tax_ids": taxes_data[line.id].ids})
        return tax_result

    # Same as v13
    def avatax_compute_taxes(self, commit=False):
        """
        Called from Invoice's Action menu.
        Forces computation of the Invoice taxes
        """
        for invoice in self:
            if (
                invoice.move_type in ["out_invoice", "out_refund"]
                and invoice.fiscal_position_id.is_avatax
                and (invoice.state == "draft" or commit)
            ):
                invoice._avatax_compute_tax(commit=commit)
        return True

    def avatax_commit_taxes(self):
        for invoice in self:
            avatax_config = invoice.company_id.get_avatax_config_company()
            if not avatax_config.disable_tax_reporting:
                doc_type = invoice._get_avatax_doc_type()
                avatax_config.commit_transaction(invoice.name, doc_type)
        return True

    def is_avatax_calculated(self):
        """
        Only apply Avatax for these types of documents.
        Can be extended to support other types.
        """
        return self.is_sale_document()

    def _post(self, soft=True):
        for invoice in self:
            if invoice.is_avatax_calculated():
                avatax_config = self.company_id.get_avatax_config_company()
                if avatax_config and avatax_config.force_address_validation:
                    for addr in [self.partner_id, self.partner_shipping_id]:
                        if not addr.date_validation:
                            # The Validate action will be interrupted
                            # if the address is not validated
                            raise UserError(
                                self.env._("Avatax address is not validated!")
                            )
                # We should compute taxes before validating the invoice
                # to ensure correct account moves
                # However, we can't save the invoice because it wasn't assigned a
                # number yet
                invoice.avatax_compute_taxes(commit=False)
        res = super()._post(soft=soft)
        for invoice in res:
            if invoice.is_avatax_calculated():
                # We can only commit to Avatax after validating the invoice
                # because we need the generated Invoice number
                invoice.avatax_compute_taxes(commit=True)
        return res

    # prepare_return in v12
    def _reverse_move_vals(self, default_values, cancel=True):
        # OVERRIDE
        # Don't keep anglo-saxon lines if not cancelling an existing invoice.
        move_vals = super()._reverse_move_vals(default_values, cancel=cancel)
        move_vals.update(
            {
                "invoice_doc_no": self.name,
                "invoice_date": default_values
                and default_values.get("invoice_date")
                or self.invoice_date,
                "tax_on_shipping_address": self.tax_on_shipping_address,
                "warehouse_id": self.warehouse_id.id,
                "location_code": self.location_code,
                "exemption_code": self.exemption_code or "",
                "exemption_code_id": self.exemption_code_id.id or None,
                "tax_address_id": self.tax_address_id.id,
            }
        )
        return move_vals

    # action_cancel in v12
    def button_draft(self):
        """
        Sets invoice to Draft, either from the Posted or Cancelled states
        """
        posted_invoices = self.filtered(
            lambda invoice: invoice.move_type in ["out_invoice", "out_refund"]
            and invoice.fiscal_position_id.is_avatax
            and invoice.state == "posted"
        )
        res = super().button_draft()
        for invoice in posted_invoices:
            avatax_config = invoice.company_id.get_avatax_config_company()
            if avatax_config:
                doc_type = invoice._get_avatax_doc_type()
                avatax_config.void_transaction(invoice.name, doc_type)
        return res

    @api.onchange(
        "invoice_line_ids",
        "warehouse_id",
        "tax_address_id",
        "tax_on_shipping_address",
        "partner_id",
    )
    def onchange_avatax_calculation(self):
        avatax_config = self.env.company.get_avatax_config_company()
        self.calculate_tax_on_save = False
        if avatax_config.invoice_calculate_tax:
            if (
                self._origin.warehouse_id != self.warehouse_id
                or self._origin.tax_address_id.street != self.tax_address_id.street
                or self._origin.partner_id != self.partner_id
                or self._origin.tax_on_shipping_address != self.tax_on_shipping_address
            ):
                self.calculate_tax_on_save = True
                return
            for line in self.invoice_line_ids:
                if (
                    line._origin.price_unit != line.price_unit
                    or line._origin.discount != line.discount
                    or line._origin.quantity != line.quantity
                ) and line.display_type == "product":
                    self.calculate_tax_on_save = True
                    break

    def write(self, vals):
        result = super().write(vals)
        avatax_config = self.env.company.get_avatax_config_company()
        for record in self:
            if (
                avatax_config.invoice_calculate_tax
                and record.calculate_tax_on_save
                and record.state == "draft"
                and not self._context.get("skip_second_write", False)
            ):
                record.with_context(skip_second_write=True).write(
                    {"calculate_tax_on_save": False}
                )
                record.avatax_compute_taxes()
        return result

    @api.model_create_multi
    def create(self, vals_list):
        moves = super().create(vals_list)
        avatax_config = self.env.company.get_avatax_config_company()
        for move in moves:
            if (
                avatax_config.invoice_calculate_tax
                and move.calculate_tax_on_save
                and not self._context.get("skip_second_write", False)
            ):
                move.with_context(skip_second_write=True).write(
                    {"calculate_tax_on_save": False}
                )
                move.avatax_compute_taxes()
        return moves


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    avatax_amt_line = fields.Float(string="AvaTax Line", copy=False)

    def _get_avatax_amount(self, qty=None):
        """
        Return the company currency line amount, after discounts,
        to use for Tax calculation.

        Can be used to compute unit price only, using qty=1.

        Code extracted from account/models/account_move.py,
        from the compute_base_line_taxes() nested function,
        adjusted to compute line amount instead of unit price.
        """
        self.ensure_one()
        base_line = self
        move = base_line.move_id
        sign = -1 if move.is_inbound() else 1
        quantity = qty or base_line.quantity
        base_amount = base_line.price_unit * quantity
        if base_line.currency_id:
            price_unit_foreign_curr = (
                sign * base_amount * (1 - (base_line.discount / 100.0))
            )
            price_unit_comp_curr = base_line.currency_id._convert(
                price_unit_foreign_curr,
                move.company_id.currency_id,
                move.company_id,
                move.date,
            )
        else:
            price_unit_comp_curr = (
                sign * base_amount * (1 - (base_line.discount / 100.0))
            )
        return -price_unit_comp_curr

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
        amount = sign * line._get_avatax_amount()
        if line.quantity < 0:
            amount = -amount
        res = {
            "qty": line.quantity,
            "itemcode": item_code,
            "description": line.name,
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
            line.avatax_amt_line = 0.0
            line.move_id.avatax_amount = 0.0
