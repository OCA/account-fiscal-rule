# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from datetime import datetime
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        """Override method to add new fields values.
        @param part- update vals with partner exemption number and code,
        also check address validation by avalara
        """

        res = super(SaleOrder, self).onchange_partner_id()
        self.exemption_code = self.partner_id.exemption_number or ''
        self.exemption_code_id = self.partner_id.exemption_code_id.id or None
        self.tax_add_shipping = True
        self.tax_add_id = self.partner_shipping_id.id
        if self.partner_id.validation_method:
            self.is_add_validate = True
        else:
            self.is_add_validate = False
        return res

    @api.model
    def create(self, vals):
        ship_add_id = False
        if 'tax_add_default' in vals and vals['tax_add_default']:
            ship_add_id = vals['partner_id']
        elif 'tax_add_invoice' in vals and vals['tax_add_invoice']:
            ship_add_id = vals['partner_invoice_id']
        elif 'tax_add_shipping' in vals and vals['tax_add_shipping']:
            ship_add_id = vals['partner_shipping_id']
        if ship_add_id:
            vals['tax_add_id'] = ship_add_id
        res = super(SaleOrder, self).create(vals)
        res.compute_tax()
        return res

    @api.multi
    def write(self, vals):
        for self_obj in self:
            ship_add_id = False
            if 'tax_add_default' in vals and vals['tax_add_default']:
                ship_add_id = self_obj.partner_id
            elif 'tax_add_invoice' in vals and vals['tax_add_invoice']:
                ship_add_id = self_obj.partner_invoice_id or self_obj.partner_id
            elif 'tax_add_shipping' in vals and vals['tax_add_shipping']:
                ship_add_id = self_obj.partner_shipping_id or self_obj.partner_id
            if ship_add_id:
                vals['tax_add_id'] = ship_add_id.id

        res = super(SaleOrder, self).write(vals)

        if not self._context.get('avatax_recalculation'):
            for order in self:
                order.with_context(avatax_recalculation=True).compute_tax()

        return res

    @api.multi
    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals.update({
            'exemption_code': self.exemption_code or '',
            'exemption_code_id': self.exemption_code_id.id or False,
            'location_code': self.location_code or '',
            'tax_on_shipping_address': self.tax_add_shipping,
        })
        return invoice_vals

    @api.depends('order_line.price_total')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            amount_tax += order.tax_amount
            order.update({
                'amount_untaxed': order.pricelist_id.currency_id.round(amount_untaxed),
                'amount_tax': order.pricelist_id.currency_id.round(amount_tax),
                'amount_total': amount_untaxed + amount_tax,
            })

    @api.onchange('tax_add_default', 'partner_id')
    def default_tax_address(self):
        if self.tax_add_default and self.partner_id:
            self.tax_add_invoice = self.tax_add_shipping = False
            self.tax_add_default = True

    @api.onchange('tax_add_invoice', 'partner_invoice_id', 'partner_id')
    def invoice_tax_address(self):
        if (self.tax_add_invoice and self.partner_invoice_id) or (self.tax_add_invoice and self.partner_id):
            self.tax_add_default = self.tax_add_shipping = False
            self.tax_add_invoice = True

    @api.onchange('tax_add_shipping', 'partner_shipping_id', 'partner_id')
    def delivery_tax_address(self):
        if (self.tax_add_shipping and self.partner_shipping_id) or (self.tax_add_shipping and self.partner_id):
            self.tax_add_default = self.tax_add_invoice = False
            self.tax_add_shipping = True

    @api.multi
    @api.depends('partner_id', 'partner_invoice_id', 'partner_shipping_id',
                 'tax_add_default', 'tax_add_invoice', 'tax_add_shipping')
    def _compute_tax_id(self):
        for order in self:
            if order.tax_add_shipping:
                order.tax_add_id = order.partner_shipping_id or order.partner_id
            elif order.tax_add_invoice:
                order.tax_add_id = order.partner_invoice_id or order.partner_id
            else:
                order.tax_add_id = order.partner_id

    exemption_code = fields.Char('Exemption Number', help="It show the customer exemption number")
    is_add_validate = fields.Boolean('Address validated')
    exemption_code_id = fields.Many2one('exemption.code', 'Exemption Code', help="It show the customer exemption code")
    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all', track_visibility='always')
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all', track_visibility='always')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all', track_visibility='always')
    tax_amount = fields.Float('Tax Code Amount', digits=dp.get_precision('Sale Price'))
    tax_add_default = fields.Boolean('Default Address', readonly=True, states={'draft': [('readonly', False)]})
    tax_add_invoice = fields.Boolean('Invoice Address', readonly=True, states={'draft': [('readonly', False)]})
    tax_add_shipping = fields.Boolean('Delivery Address', default=True, readonly=True, states={'draft': [('readonly', False)]})
    tax_add_id = fields.Many2one('res.partner', 'Tax Address', readonly=True, states={'draft': [('readonly', False)]},
                                 compute='_compute_tax_id', store=True)
    tax_address = fields.Text('Tax Address')
    location_code = fields.Char('Location Code', help='Origin address location code')

    @api.model
    def create_lines(self, order_lines):
        """ Tax line creation for calculating tax amount using avalara tax code. """
        lines = []
        for line in order_lines:
            if line.product_id:
                tax_code = (line.product_id.tax_code_id and line.product_id.tax_code_id.name) or None
                lines.append({
                    'qty': line.product_uom_qty,
                    'itemcode': line.product_id and line.product_id.default_code or None,
                    'description': line.product_id.description or None,
                    'amount': line.price_unit * (1-(line.discount or 0.0)/100.0) * line.product_uom_qty,
                    'tax_code': tax_code,
                    'id': line,
                    'tax_id': line.tax_id,
                })
        return lines

    @api.model
    def compute_tax(self):
        """ Create and update tax amount for each and every order line and shipping line.
        @param order_line: send sub_total of each line and get tax amount
        @param shiiping_line: send shipping amount of each ship line and get ship tax amount
        """
        avatax_config_obj = self.env['avalara.salestax']
        account_tax_obj = self.env['account.tax']
        avatax_config = avatax_config_obj._get_avatax_config_company()

        # Make sure Avatax is configured
        if not avatax_config:
            raise UserError(_('Your Avatax Countries settings are not configured. You need a country code in the Countries section.  \nIf you have a multi-company installation, you must add settings for each company.  \n\nYou can update settings in Avatax->Avatax API.'))

        tax_amount = o_tax_amt = 0.0

        # ship from Address / Origin Address either warehouse or company if none
        if self.warehouse_id and self.warehouse_id.partner_id:
            ship_from_address_id = self.warehouse_id.partner_id
        else:
            ship_from_address_id = self.company_id.partner_id

        if avatax_config and not avatax_config.disable_tax_calculation:
            ava_tax = account_tax_obj.search(
                            [('is_avatax', '=', True),
                            ('type_tax_use', 'in', ['sale', 'all']),
                            ('company_id', '=', self.company_id.id)])

            shipping_add_id = self.tax_add_id

            lines = self.create_lines(self.order_line)

            order_date = (self.date_order).split(' ')[0]
            order_date = datetime.strptime(order_date, "%Y-%m-%d").date()
            if lines:
                if avatax_config.on_line:
                    # Line level tax calculation
                    # tax based on individual order line
                    tax_id = []
                    for line in lines:
                        tax_id = line['tax_id'] and [tax.id for tax in line['tax_id']] or []
                        if ava_tax and ava_tax[0].id not in tax_id:
                            tax_id.append(ava_tax[0].id)
                        ol_tax_amt = account_tax_obj._get_compute_tax(avatax_config, order_date,
                                                                    self.name, 'SalesOrder', self.partner_id, ship_from_address_id,
                                                                    shipping_add_id, [line], self.user_id, self.exemption_code or None, self.exemption_code_id.code or None,
                                                                    currency_id=self.currency_id).TotalTax
                        o_tax_amt += ol_tax_amt  # tax amount based on total order line total
                        line['id'].write({'tax_amt': ol_tax_amt, 'tax_id': [(6, 0, tax_id)]})

                    tax_amount = o_tax_amt

                elif avatax_config.on_order:
                    tax_amount = account_tax_obj._get_compute_tax(avatax_config, order_date,
                                                                    self.name, 'SalesOrder', self.partner_id, ship_from_address_id,
                                                                    shipping_add_id, lines, self.user_id, self.exemption_code or None, self.exemption_code_id.code or None,
                                                                    currency_id=self.currency_id).TotalTax

                    for o_line in self.order_line:
                        o_line.write({'tax_amt': 0.0})
                else:
                    raise UserError(_('Please select system calls in Avatax API Configuration'))
            else:
                for o_line in self.order_line:
                        o_line.write({'tax_amt': 0.0})

        else:
            for o_line in self.order_line:
                o_line.write({'tax_amt': 0.0})

        self.write({'tax_amount': tax_amount, 'order_line': []})
        return True

    @api.multi
    def button_dummy(self):
        """ It used to called manually calculation method of avalara and get tax amount"""
        self.compute_tax()
        return True

    @api.multi
    def action_confirm(self):
        self.compute_tax()
        return super(SaleOrder, self).action_confirm()


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    tax_amt = fields.Float('Avalara Tax', help="tax calculate by avalara")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
