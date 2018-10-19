# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import time
from odoo.exceptions import UserError

@api.model
def get_origin_tax_date(self):
    """ partner address, on which avalara tax will calculate  """
    for inv_obj in self:
        if inv_obj.origin:
            a = inv_obj.origin

            if len(a.split(':')) > 1:
                inv_origin = a.split(':')[1]
            else:
                inv_origin = a.split(':')[0]

            inv_ids = self.search([('number', '=', inv_origin)])
            for invoice in inv_ids:
                if invoice.date_invoice:
                    return invoice.date_invoice
                else:
                    return inv_obj.date_invoice
        else:
            return False

class AccountInvoice(models.Model):
    """Inherit to implement the tax calculation using avatax API"""
    _inherit = "account.invoice"

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        res = super(AccountInvoice, self)._onchange_partner_id()
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
            if self.warehouse.company_id:
                self.company_id = self.warehouse.company_id.id
            if self.warehouse.code:
                self.location_code = self.warehouse.code

    @api.model
    def create(self, vals):
        res = super(AccountInvoice, self).create(vals)
        res.with_context(contact_avatax=True)._onchange_invoice_line_ids()
        return res

    @api.multi
    def write(self, vals):
        res = super(AccountInvoice, self).write(vals)
        if not self._context.get('contact_avatax') and self:
            for inv in self.filtered(lambda inv: inv.state == 'draft'):
                inv.with_context(contact_avatax=True)._onchange_invoice_line_ids()
        return res

    invoice_doc_no = fields.Char('Source/Ref Invoice No', readonly=True, states={'draft': [('readonly', False)]}, help="Reference of the invoice")
    invoice_date = fields.Date('Invoice Date', readonly=True)
    is_add_validate = fields.Boolean('Address validated')
    exemption_code = fields.Char('Exemption Number', help="It show the customer exemption number")
    exemption_code_id = fields.Many2one('exemption.code', 'Exemption Code', help="It show the customer exemption code")
    tax_on_shipping_address = fields.Boolean('Tax based on shipping address', default=False, required=True)
    shipping_add_id = fields.Many2one('res.partner', 'Tax Address', compute='_compute_shipping_add_id')
    shipping_address = fields.Text('Tax Address')
    location_code = fields.Char('Location code', readonly=True, states={'draft': [('readonly', False)]})
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse')

    @api.multi
    @api.depends('tax_on_shipping_address', 'partner_id', 'partner_shipping_id')
    def _compute_shipping_add_id(self):
        for invoice in self:
            invoice.shipping_add_id = invoice.partner_shipping_id if invoice.tax_on_shipping_address else invoice.partner_id

    @api.multi
    def compute(self):
        # self.compute_taxes()
        avatax_config_obj = self.env['avalara.salestax']
        account_tax_obj = self.env['account.tax']
        avatax_config = avatax_config_obj._get_avatax_config_company()

        for invoice in self:
            if avatax_config and not avatax_config.disable_tax_calculation and invoice.type in ['out_invoice', 'out_refund']:
                shipping_add_id = self.shipping_add_id
                if self.warehouse_id and self.warehouse_id.partner_id:
                    shipping_add_origin_id = self.warehouse_id.partner_id
                else:
                    shipping_add_origin_id = self.company_id.partner_id
                tax_date = get_origin_tax_date(self)
                if not tax_date:
                    tax_date = invoice.date_invoice or time.strftime('%Y-%m-%d')

                sign = invoice.type == 'out_invoice' and 1 or -1
                lines = self.create_lines(invoice.invoice_line_ids, sign)
                if lines:
                    if avatax_config.on_line:
                        ava_tax = account_tax_obj.search(
                                [('is_avatax', '=', True),
                                ('type_tax_use', 'in', ['sale', 'all']),
                                ('company_id', '=', self.company_id.id)])
                        tax_id = []
                        for line in lines:
                            tax_id = line['tax_id'] and [tax.id for tax in line['tax_id']] or []
                            if ava_tax and ava_tax[0].id not in tax_id:
                                tax_id.append(ava_tax[0].id)
                            ol_tax_amt = account_tax_obj._get_compute_tax(avatax_config, invoice.date_invoice,
                                                                       invoice.number, 'SalesOrder',
                                                                       invoice.partner_id, shipping_add_origin_id,
                                                                       shipping_add_id, [line], invoice.user_id, invoice.exemption_code or None, invoice.exemption_code_id.code or None,
                                                                       is_override=invoice.type == 'out_refund', currency_id=invoice.currency_id).TotalTax
    #                        o_tax_amt += ol_tax_amt  #tax amount based on total order line total   

                            line['id'].write({'tax_amt': ol_tax_amt, 'invoice_line_tax_ids': [(6, 0, tax_id)]})

                    elif avatax_config.on_order:
                        for o_line in invoice.invoice_line_ids:
                            o_line.write({'tax_amt': 0.0})
                else:
                    for o_line in invoice.invoice_line_ids:
                        o_line.write({'tax_amt': 0.0})
        return True

    @api.multi
    def invoice_validate(self):
        self.compute_taxes()
        return super(AccountInvoice, self.with_context(contact_avatax=True)).invoice_validate()

    @api.multi
    def action_invoice_open(self):
        self = self.with_context(contact_avatax=True)
        avatax_config_obj = self.env['avalara.salestax']
        account_tax_obj = self.env['account.tax']
        avatax_config = avatax_config_obj._get_avatax_config_company()

        res = super(AccountInvoice, self).action_invoice_open()

        # Bypass reporting
        if avatax_config and avatax_config.disable_tax_reporting:
            return res

        for invoice in self:
            if avatax_config and not avatax_config.disable_tax_calculation and invoice.type in ['out_invoice', 'out_refund']:
                shipping_add_id = invoice.shipping_add_id
                if invoice.warehouse_id and invoice.warehouse_id.partner_id:
                    shipping_add_origin_id = invoice.warehouse_id.partner_id
                else:
                    shipping_add_origin_id = invoice.company_id.partner_id
                tax_date = get_origin_tax_date(self)
                if not tax_date:
                    tax_date = invoice.date_invoice

                sign = invoice.type == 'out_invoice' and 1 or -1
                lines = self.create_lines(invoice.invoice_line_ids, sign)
                if lines:
                    account_tax_obj._get_compute_tax(avatax_config, invoice.date_invoice,
                                                     invoice.number, not invoice.invoice_doc_no and 'SalesInvoice' or 'ReturnInvoice',
                                                     invoice.partner_id, shipping_add_origin_id,
                                                     shipping_add_id, lines,
                                                     invoice.user_id, invoice.exemption_code or None, invoice.exemption_code_id.code or None,
                                                     True,  # commit
                                                     tax_date,
                                                     invoice.invoice_doc_no, invoice.location_code or '',
                                                     is_override=invoice.type == 'out_refund', currency_id=invoice.currency_id)
        return res

    @api.multi
    def action_commit_tax(self):
        avatax_config_obj = self.env['avalara.salestax']
        account_tax_obj = self.env['account.tax']
        avatax_config = avatax_config_obj._get_avatax_config_company()

        if avatax_config and avatax_config.disable_tax_reporting:
            return True

        for invoice in self:
            if avatax_config and not avatax_config.disable_tax_calculation and invoice.type in ['out_invoice', 'out_refund']:
                shipping_add_id = self.shipping_add_id
                if self.warehouse_id and self.warehouse_id.partner_id:
                    shipping_add_origin_id = self.warehouse_id.partner_id
                else:
                    shipping_add_origin_id = self.company_id.partner_id
                tax_date = get_origin_tax_date(self)
                if not tax_date:
                    tax_date = invoice.date_invoice

                sign = invoice.type == 'out_invoice' and 1 or -1
                lines = self.create_lines(invoice.invoice_line_ids, sign)
                if lines:
                    if avatax_config.on_line:
                        for line in lines:
                            ol_tax_amt = account_tax_obj._get_compute_tax(avatax_config, invoice.date_invoice,
                                                                       invoice.number, 'SalesOrder',
                                                                       invoice.partner_id, shipping_add_origin_id,
                                                                       shipping_add_id, [line], invoice.user_id, invoice.exemption_code or None, invoice.exemption_code_id.code or None,
                                                                       is_override=invoice.type == 'out_refund', currency_id=invoice.currency_id).TotalTax
    #                        o_tax_amt += ol_tax_amt  #tax amount based on total order line total   

                            line['id'].write({'tax_amt': ol_tax_amt})

                    elif avatax_config.on_order:
                        for o_line in invoice.invoice_line_ids:
                            o_line.write({'tax_amt': 0.0})
                    else:
                        raise UserError(_('Please select system calls in Avatax API Configuration.'))
                else:
                    for o_line in invoice.invoice_line_ids:
                        o_line.write({'tax_amt': 0.0})
                # extend list lines1 with lines2 to send all invoice lines in avalara
                if lines:
                    account_tax_obj._get_compute_tax(avatax_config, invoice.date_invoice,
                                                   invoice.number, not invoice.invoice_doc_no and 'SalesInvoice' or 'ReturnInvoice',
                                                   invoice.partner_id, shipping_add_origin_id,
                                                   shipping_add_id, lines, invoice.user_id, invoice.exemption_code or None, invoice.exemption_code_id.code or None,
                                                   False, tax_date,
                                                   invoice.invoice_doc_no, invoice.location_code or '',
                                                   is_override=invoice.type == 'out_refund', currency_id=invoice.currency_id)
            else:
                for o_line in invoice.invoice_line_ids:
                    o_line.write({'tax_amt': 0.0})
#                for s_line in invoice.shipping_lines:
#                    ship_order_line.write(cr, uid, [s_line.id], {'tax_amt': 0.0,})
        return True

    @api.multi
    def get_taxes_values(self):
        avatax_config = self.env['avalara.salestax']._get_avatax_config_company()
        account_tax_obj = self.env['account.tax']
        tax_grouped = {}
        if avatax_config and not avatax_config.disable_tax_calculation and self.type in ['out_invoice', 'out_refund']:
            # avatax charges customers per API call, so don't hit their API in every onchange, only when saving
            if not self._context.get('contact_avatax'):
                return {}
            if self.invoice_line_ids:
                lines = self.create_lines(self.invoice_line_ids)
                if lines:
                    if self.warehouse_id and self.warehouse_id.partner_id:
                        ship_from_address_id = self.warehouse_id.partner_id
                    else:
                        ship_from_address_id = self.company_id.partner_id
                    shipping_add_id = self.shipping_add_id
                    o_tax_amt = 0.0
                    tax = account_tax_obj.search(
                                [('is_avatax', '=', True),
                                ('type_tax_use', 'in', ['sale', 'all']),
                                ('company_id', '=', self.company_id.id)])
                    if not tax:
                        raise UserError(_('Please configure tax information in "AVATAX" settings.  The documentation will assist you in proper configuration of all the tax code settings as well as how they relate to the product. \n\n Accounting->Configuration->Taxes->Taxes'))

                    o_tax_amt = account_tax_obj._get_compute_tax(avatax_config, self.date_invoice or time.strftime('%Y-%m-%d'),
                                                    self.number, 'SalesOrder', self.partner_id, ship_from_address_id,
                                                    shipping_add_id, lines, self.user_id, self.exemption_code or None, self.exemption_code_id.code or None,
                                                    is_override=self.type == 'out_refund', currency_id=self.currency_id).TotalTax
                    o_tax_amt = float(o_tax_amt)
                    if o_tax_amt:
                        
                        val = {
                            'invoice_id': self.id,
                            'name': tax[0].name,
                            'tax_id': tax[0].id,
                            'amount': o_tax_amt,
                            'manual': False,
                            'sequence': tax[0].sequence,
                            'account_analytic_id': tax[0].analytic and lines[0]['account_analytic_id'] or False,
                            'account_id': self.type in ('out_invoice', 'in_invoice') and (tax[0].account_id.id or lines[0]['account_id']) or (tax[0].refund_account_id.id or lines[0]['account_id']),
                        }
                        if not val.get('account_analytic_id') and lines[0]['account_analytic_id'] and val['account_id'] == lines[0]['account_id']:
                            val['account_analytic_id'] = lines[0]['account_analytic_id']

                        key = tax[0].id
                        if key not in tax_grouped:
                            tax_grouped[key] = val
                        else:
                            tax_grouped[key]['amount'] += val['amount']

                for line in self.invoice_line_ids:
                    price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                    taxes = line.invoice_line_tax_ids.compute_all(price_unit, self.currency_id, line.quantity, line.product_id, self.partner_id)['taxes']
                    for tax in taxes:
                        val = {
                            'invoice_id': self.id,
                            'name': tax['name'],
                            'tax_id': tax['id'],
                            'amount': tax['amount'],
                            'manual': False,
                            'sequence': tax['sequence'],
                            'account_analytic_id': tax['analytic'] and line.account_analytic_id.id or False,
                            'account_id': self.type in ('out_invoice', 'in_invoice') and (tax['account_id'] or line.account_id.id) or (tax['refund_account_id'] or line.account_id.id),
                        }

                        # If the taxes generate moves on the same financial account as the invoice line,
                        # propagate the analytic account from the invoice line to the tax line.
                        # This is necessary in situations were (part of) the taxes cannot be reclaimed,
                        # to ensure the tax move is allocated to the proper analytic account.
                        if not val.get('account_analytic_id') and line.account_analytic_id and val['account_id'] == line.account_id.id:
                            val['account_analytic_id'] = line.account_analytic_id.id

                        key = tax['id']
                        if key not in tax_grouped:
                            tax_grouped[key] = val
                        else:
                            tax_grouped[key]['amount'] += val['amount']
                return tax_grouped
        else:
            tax_grouped = super(AccountInvoice, self).get_taxes_values()
        return tax_grouped

    @api.model
    def create_lines(self, invoice_lines, sign=1):
        avatax_config_obj = self.env['avalara.salestax']
        avatax_config = avatax_config_obj._get_avatax_config_company()
        lines = []
        for line in invoice_lines:
            # Add UPC to product item code
            if line.product_id.barcode and avatax_config.upc_enable:
                item_code = "upc:" + line.product_id.barcode
            else:
                item_code = line.product_id.default_code
            # Get Tax Code
            if line.product_id:
                tax_code = (line.product_id.tax_code_id and line.product_id.tax_code_id.name) or None
#            else:
#                tax_code = (line.product_id.categ_id.tax_code_id  and line.product_id.categ_id.tax_code_id.name) or None
            # Calculate discount amount
                discount_amount = 0.0
                is_discounted = False
                if line.discount != 0.0 or line.discount != None:
                    discount_amount = sign * line.price_unit * ((line.discount or 0.0)/100.0) * line.quantity,
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
                    'account_analytic_id': line.account_analytic_id.id,
                    'account_id': line.account_id.id,
                    'tax_id': line.invoice_line_tax_ids,
                })
        return lines

    @api.model
    def _prepare_refund(self, invoice, date_invoice=None, date=None, description=None, journal_id=None):
        values = super(AccountInvoice, self)._prepare_refund(invoice, date_invoice=date_invoice, date=date, description=description, journal_id=journal_id)
        values.update({
            'invoice_doc_no': invoice.number,
            'invoice_date': invoice.date_invoice,
            'tax_on_shipping_address': invoice.tax_on_shipping_address,
            'warehouse_id': invoice.warehouse_id.id,
            'location_code': invoice.location_code,
            'exemption_code': invoice.exemption_code or '',
            'exemption_code_id': invoice.exemption_code_id.id or None,
            'shipping_add_id': invoice.shipping_add_id.id,
        })
        return values

    @api.multi
    def action_cancel(self):
        account_tax_obj = self.env['account.tax']
        avatax_config = self.env['avalara.salestax']._get_avatax_config_company()
        for invoice in self:
            c_code = invoice.partner_id.country_id and invoice.partner_id.country_id.code or False
            cs_code = []    # Countries where Avalara address validation is enabled
            for c_brw in avatax_config.country_ids:
                cs_code.append(str(c_brw.code))
            if avatax_config and not avatax_config.disable_tax_calculation and invoice.type in ['out_invoice', 'out_refund'] and c_code in cs_code:
                doc_type = invoice.type == 'out_invoice' and 'SalesInvoice' or 'ReturnInvoice'
                account_tax_obj.cancel_tax(avatax_config, invoice.number, doc_type, 'DocVoided')
#        self.write({'internal_number':''})
        return super(AccountInvoice, self).action_cancel()


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    tax_amt = fields.Float('Avalara Tax', help="tax calculate by avalara")

    @api.onchange('product_id')
    def _onchange_product_id(self):
        avatax_config = self.env['avalara.salestax']._get_avatax_config_company()
        if not avatax_config.disable_tax_calculation:
            if self.invoice_id.type in ('out_invoice', 'out_refund'):
                taxes = self.product_id.taxes_id or self.account_id.tax_ids
            else:
                taxes = self.product_id.supplier_taxes_id or self.account_id.tax_ids

            if not all(taxes.mapped('is_avatax')):
                warning = {
                    'title': _('Warning!'),
                    'message': _('All used taxes must be configured to use Avatax!'),
                }
                return {'warning': warning}
        return super(AccountInvoiceLine, self)._onchange_product_id()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
