import time
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    """Inherit to implement the tax calculation using avatax API"""
    _inherit = "account.move"

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        res = super(AccountMove, self)._onchange_partner_id()
        if not self.exemption_locked:
            self.exemption_code = self.partner_id.exemption_number or ''
            self.exemption_code_id = self.partner_id.exemption_code_id.id or None
        if self.partner_id.validation_method:
            self.is_add_validate = True
        else:
            self.is_add_validate = False
        return res

    @api.onchange('warehouse_id')
    def onchange_warehouse_id(self):
        if self.warehouse_id:
            if self.warehouse_id.company_id:
                self.company_id = self.warehouse_id.company_id
            if self.warehouse_id.code:
                self.location_code = self.warehouse_id.code

    invoice_doc_no = fields.Char('Source/Ref Invoice No', readonly=True, states={
                                 'draft': [('readonly', False)]}, help="Reference of the invoice")
    invoice_date = fields.Date('Tax Invoice Date', readonly=True)
    is_add_validate = fields.Boolean('Address Is Validated')
    exemption_code = fields.Char(
        'Exemption Number', help="It show the customer exemption number")
    exemption_code_id = fields.Many2one(
        'exemption.code', 'Exemption Code', help="It show the customer exemption code")
    exemption_locked = fields.Boolean(
        help="Exemption code won't be automatically changed, "
        "for instance, when changing the Customer.")
    tax_on_shipping_address = fields.Boolean(
        'Tax based on shipping address', default=True)
    shipping_add_id = fields.Many2one(
        'res.partner', 'Tax Shipping Address', compute='_compute_shipping_add_id')
    shipping_address = fields.Text('Tax Shipping Address Text')
    location_code = fields.Char('Location Code', readonly=True, states={
                                'draft': [('readonly', False)]})
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse')
    disable_tax_calculation = fields.Boolean('Disable Avatax Tax calculation')
    tax_amount = fields.Monetary(string='AvaTax', store=True, readonly=True,
                                 currency_field='company_currency_id')

    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, tracking=True,
                                     compute='_compute_amount')
    amount_tax = fields.Monetary(string='Tax', store=True, readonly=True,
                                 compute='_compute_amount')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True,
                                   compute='_compute_amount',
                                   inverse='_inverse_amount_total')
    amount_residual = fields.Monetary(string='Amount Due', store=True,
                                      compute='_compute_amount')
    amount_untaxed_signed = fields.Monetary(string='Untaxed Amount Signed', store=True, readonly=True,
                                            compute='_compute_amount', currency_field='company_currency_id')
    amount_tax_signed = fields.Monetary(string='Tax Signed', store=True, readonly=True,
                                        compute='_compute_amount', currency_field='company_currency_id')
    amount_total_signed = fields.Monetary(string='Total Signed', store=True, readonly=True,
                                          compute='_compute_amount', currency_field='company_currency_id')
    amount_residual_signed = fields.Monetary(string='Amount Due Signed', store=True,
                                             compute='_compute_amount', currency_field='company_currency_id')
    invoice_payment_state = fields.Selection(selection=[
        ('not_paid', 'Not Paid'),
        ('in_payment', 'In Payment'),
        ('paid', 'Paid')],
        string='Payment', store=True, readonly=True, copy=False, tracking=True,
        compute='_compute_amount')

    @api.depends(
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state',
        'tax_amount')
    def _compute_amount(self):
        invoice_ids = [move.id for move in self if move.id and move.is_invoice(
            include_receipts=True)]
        self.env['account.payment'].flush(['state'])
        if invoice_ids:
            self._cr.execute(
                '''
                    SELECT move.id
                    FROM account_move move
                    JOIN account_move_line line ON line.move_id = move.id
                    JOIN account_partial_reconcile part ON part.debit_move_id = line.id OR part.credit_move_id = line.id
                    JOIN account_move_line rec_line ON
                        (rec_line.id = part.credit_move_id AND line.id = part.debit_move_id)
                        OR
                        (rec_line.id = part.debit_move_id AND line.id = part.credit_move_id)
                    JOIN account_payment payment ON payment.id = rec_line.payment_id
                    JOIN account_journal journal ON journal.id = rec_line.journal_id
                    WHERE payment.state IN ('posted', 'sent')
                    AND journal.post_at = 'bank_rec'
                    AND move.id IN %s
                ''', [tuple(invoice_ids)]
            )
            in_payment_set = set(res[0] for res in self._cr.fetchall())
        else:
            in_payment_set = {}

        for move in self:
            total_untaxed = 0.0
            total_untaxed_currency = 0.0
            total_tax = 0.0
            total_tax_currency = 0.0
            total_residual = 0.0
            total_residual_currency = 0.0
            total = 0.0
            total_currency = 0.0
            currencies = set()

            if move.tax_amount:
                sign = move.type == 'out_invoice' and -1 or 1
                total_tax += move.tax_amount * sign
                total += move.tax_amount * sign
                total_tax_currency += move.tax_amount * sign
                total_currency += move.tax_amount * sign

            for line in move.line_ids:
                if line.currency_id:
                    currencies.add(line.currency_id)

                if move.is_invoice(include_receipts=True):
                    # === Invoices ===
                    if not line.exclude_from_invoice_tab:
                        # Untaxed amount.
                        total_untaxed += line.balance
                        total_untaxed_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.tax_line_id:
                        # Tax amount.
                        total_tax += line.balance
                        total_tax_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.account_id.user_type_id.type in ('receivable', 'payable'):
                        # Residual amount.
                        total_residual += line.amount_residual
                        total_residual_currency += line.amount_residual_currency
                else:
                    # === Miscellaneous journal entry ===
                    if line.debit:
                        total += line.balance
                        total_currency += line.amount_currency
            if move.type == 'entry' or move.is_outbound():
                sign = 1
            else:
                sign = -1
            move.amount_untaxed = sign * \
                (total_untaxed_currency if len(currencies) == 1 else total_untaxed)
            move.amount_tax = sign * \
                (total_tax_currency if len(currencies) == 1 else total_tax)
            move.amount_total = sign * \
                (total_currency if len(currencies) == 1 else total)
            move.amount_residual = -sign * \
                (total_residual_currency if len(currencies) == 1 else total_residual)
            move.amount_untaxed_signed = -total_untaxed
            move.amount_tax_signed = -total_tax
            move.amount_total_signed = abs(
                total) if move.type == 'entry' else -total
            move.amount_residual_signed = total_residual
            currency = len(currencies) == 1 and currencies.pop(
            ) or move.company_id.currency_id
            is_paid = currency and currency.is_zero(
                move.amount_residual) or not move.amount_residual

            # Compute 'invoice_payment_state'.
            if move.type == 'entry':
                move.invoice_payment_state = False
            elif move.state == 'posted' and is_paid:
                if move.id in in_payment_set:
                    move.invoice_payment_state = 'in_payment'
                else:
                    move.invoice_payment_state = 'paid'
            else:
                move.invoice_payment_state = 'not_paid'

    @api.depends('tax_on_shipping_address', 'partner_id', 'partner_shipping_id')
    def _compute_shipping_add_id(self):
        for invoice in self:
            invoice.shipping_add_id = invoice.partner_shipping_id if invoice.tax_on_shipping_address else invoice.partner_id

    def get_origin_tax_date(self):
        for inv_obj in self:
            if inv_obj.invoice_origin:
                a = inv_obj.invoice_origin
                if len(a.split(':')) > 1:
                    inv_origin = a.split(':')[1]
                else:
                    inv_origin = a.split(':')[0]
                inv_ids = self.search([('name', '=', inv_origin)])
                for invoice in inv_ids:
                    if invoice.invoice_date:
                        return invoice.invoice_date
                    else:
                        return inv_obj.invoice_date
        return False

    def avatax_compute_taxes(self, contact_avatax=True, commit_avatax=False):
        """
        Called from Invoice's Action menu.
        Forces computation of the Invoice taxes

        Extends the standard method reponsible for computing taxes.
        Returns a dict with the taxes values, ready to be use to create tax_line_ids.
        """
        tax_amount = o_tax_amt = 0.0
        sign = self.type == 'out_invoice' and 1 or -1
        avatax_config = self.company_id.get_avatax_config_company()
        account_tax_obj = self.env['account.tax']
        # avatax charges customers per API call, so don't hit their API in every onchange, only when saving
        contact_avatax = contact_avatax or self.env.context.get(
            'contact_avatax') or avatax_config.enable_immediate_calculation
        if contact_avatax and self.type in ['out_invoice', 'out_refund']:
            ava_tax = account_tax_obj.search(
                [('is_avatax', '=', True),
                 ('type_tax_use', 'in', ['sale', 'all']),
                 ('company_id', '=', self.company_id.id)])
            if not ava_tax:
                raise UserError(_(
                    'Please configure tax information in "AVATAX" settings.  '
                    'The documentation will assist you in proper configuration '
                    'of all the tax code settings as well as '
                    'how they relate to the product. '
                    '\n\n Accounting->Configuration->Taxes->Taxes'))

            tax_date = self.get_origin_tax_date() or self.invoice_date
            lines = self.create_lines(sign)
            if lines:
                ship_from_address_id = self.warehouse_id.partner_id or self.company_id.partner_id
                if commit_avatax:
                    doc_type = 'ReturnInvoice' if self.invoice_doc_no else 'SalesInvoice'
                else:
                    doc_type = 'SalesOrder'
                if avatax_config.on_line:
                    tax_id = []
                    for line in lines:
                        tax_id = line['tax_id'] and [
                            tax.id for tax in line['tax_id']] or []
                        if ava_tax and ava_tax[0].id not in tax_id:
                            tax_id.append(ava_tax[0].id)
                        ol_tax_amt = account_tax_obj._get_compute_tax(
                            avatax_config, self.invoice_date or time.strftime(
                                '%Y-%m-%d'),
                            self.name,
                            doc_type,  # 'SalesOrder',
                            self.partner_id, ship_from_address_id,
                            self.shipping_add_id,
                            [line], self.user_id, self.exemption_code or None, self.exemption_code_id.code or None,
                            currency_id=self.currency_id).TotalTax
                        o_tax_amt += ol_tax_amt
                        line['id'].write(
                            {'tax_amt': ol_tax_amt,
                             #                              'tax_line_id': tax_id[0],
                             'tax_ids': [(6, 0, tax_id)]})
                    tax_amount = o_tax_amt
                elif avatax_config.on_order:
                    tax_amount = account_tax_obj._get_compute_tax(
                        avatax_config, self.invoice_date or time.strftime(
                            '%Y-%m-%d'),
                        self.name,
                        doc_type,  # 'SalesOrder',
                        self.partner_id, ship_from_address_id,
                        self.shipping_add_id,
                        lines, self.user_id, self.exemption_code or None, self.exemption_code_id.code or None,
                        commit_avatax, tax_date,
                        self.invoice_doc_no, self.location_code or '',
                        is_override=self.type == 'out_refund', currency_id=self.currency_id).TotalTax
                    self.invoice_line_ids.write({'tax_amt': 0.0})
                else:
                    raise UserError(
                        _('Please select system calls in Avatax API Configuration'))
            else:
                for o_line in self.invoice_line_ids:
                    o_line.write({'tax_amt': 0.0})
        self.write({'tax_amount': tax_amount * sign})
        return True

    def create_lines(self, sign=1):
        """
        Prepare the lines to use for Avatax computation.
        Returns a list of dicts
        """
        avatax_config = self.company_id.get_avatax_config_company()
        lines = []
        for line in self.invoice_line_ids:
            # Add UPC to product item code
            if line.product_id.barcode and avatax_config.upc_enable:
                item_code = "upc:" + line.product_id.barcode
            else:
                item_code = line.product_id.default_code
            # Get Tax Code
            # if line.product_id:
            tax_code = (
                line.product_id.tax_code_id and line.product_id.tax_code_id.name) or None
            # else:
            #    tax_code = (line.product_id.categ_id.tax_code_id  and line.product_id.categ_id.tax_code_id.name) or None
            # Calculate discount amount
            discount_amount = 0.0
            is_discounted = False
            if line.discount != 0.0 or line.discount != None:
                discount_amount = sign * line.price_unit * \
                    ((line.discount or 0.0)/100.0) * line.quantity,
                is_discounted = True
            lines.append({
                'qty': line.quantity,
                'itemcode': line.product_id and item_code or None,
                'description': line.name,
                'discounted': is_discounted,
                'discount': discount_amount[0],
                'amount': sign * line.price_unit * (1-(line.discount or 0.0)/100.0) * line.quantity,
                'tax_code': tax_code,
                'id': line,
                'account_analytic_id': line.analytic_account_id.id,
                'analytic_tag_ids': line.analytic_tag_ids.ids,
                'account_id': line.account_id.id,
                'tax_id': line.tax_ids,
            })
        return lines

    def action_post(self):
        self.avatax_compute_taxes(commit_avatax=True)
        super().action_post()

    def _reverse_move_vals(self, default_values, cancel=True):
        # OVERRIDE
        # Don't keep anglo-saxon lines if not cancelling an existing invoice.
        move_vals = super(AccountMove, self)._reverse_move_vals(
            default_values, cancel=cancel)
        move_vals.update({
            'invoice_doc_no': self.name,
            'invoice_date': self.invoice_date,
            'tax_on_shipping_address': self.tax_on_shipping_address,
            'warehouse_id': self.warehouse_id.id,
            'location_code': self.location_code,
            'exemption_code': self.exemption_code or '',
            'exemption_code_id': self.exemption_code_id.id or None,
            'shipping_add_id': self.shipping_add_id.id,
        })
        return move_vals

    def button_cancel(self):
        account_tax_obj = self.env['account.tax']
        avatax_config = self.company_id.get_avatax_config_company()
        for invoice in self:
            if (invoice.type in ['out_invoice', 'out_refund'] and
                    invoice.partner_id.country_id in avatax_config.country_ids and
                    invoice.state != 'posted'):
                doc_type = invoice.type == 'out_invoice' and 'SalesInvoice' or 'ReturnInvoice'
                account_tax_obj.cancel_tax(
                    avatax_config, invoice.name, doc_type, 'DocVoided')
        return super(AccountMove, self).button_cancel()


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    tax_amt = fields.Float(string='Avalara Tax',
                           help="Tax computed by Avalara",)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        avatax_config = self.company_id.get_avatax_config_company()
        if not avatax_config.disable_tax_calculation:
            if self.move_id.type in ('out_invoice', 'out_refund'):
                taxes = self.product_id.taxes_id or self.account_id.tax_ids
            else:
                taxes = self.product_id.supplier_taxes_id or self.account_id.tax_ids

            if not all(taxes.mapped('is_avatax')):
                warning = {
                    'title': _('Warning!'),
                    'message': _('All used taxes must be configured to use Avatax!'),
                }
                return {'warning': warning}
        return super(AccountMoveLine, self)._onchange_product_id()
