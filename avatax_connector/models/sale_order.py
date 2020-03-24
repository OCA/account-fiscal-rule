from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
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
        self.tax_on_shipping_address = bool(self.partner_shipping_id)
        self.is_add_validate = bool(self.partner_id.validation_method)

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals.update({
            'exemption_code': self.exemption_code or '',
            'exemption_code_id': self.exemption_code_id.id or False,
            'exemption_locked': True,
            'location_code': self.location_code or '',
            'warehouse_id': self.warehouse_id.id or '',
            'tax_on_shipping_address': self.tax_on_shipping_address,
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
                'amount_untaxed': order.pricelist_id and order.pricelist_id.currency_id.round(amount_untaxed) or amount_untaxed,
                'amount_tax': order.pricelist_id and order.pricelist_id.currency_id.round(amount_tax) or amount_tax,
                'amount_total': amount_untaxed + amount_tax,
            })

    @api.depends('tax_on_shipping_address', 'partner_id', 'partner_shipping_id')
    def _compute_tax_id(self):
        for invoice in self:
            invoice.tax_add_id = invoice.partner_shipping_id if invoice.tax_on_shipping_address else invoice.partner_id

    exemption_code = fields.Char(
        'Exemption Number', help="It show the customer exemption number")
    is_add_validate = fields.Boolean('Address Is validated')
    exemption_code_id = fields.Many2one(
        'exemption.code', 'Exemption Code', help="It show the customer exemption code")
    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True,
                                     readonly=True, compute='_amount_all', track_visibility='always')
    amount_tax = fields.Monetary(
        string='Taxes', store=True, readonly=True, compute='_amount_all', track_visibility='always')
    amount_total = fields.Monetary(
        string='Total', store=True, readonly=True, compute='_amount_all', track_visibility='always')
    tax_amount = fields.Float('Tax Code Amount', digits='Sale Price')
    tax_on_shipping_address = fields.Boolean(
        'Tax based on shipping address', default=True)
    tax_add_id = fields.Many2one(
        'res.partner', 'Tax Address',
        readonly=True,
        states={'draft': [('readonly', False)]},
        compute='_compute_tax_id', store=True)
    tax_address = fields.Text('Tax Address Text')
    location_code = fields.Char(
        'Location Code', help='Origin address location code')

    def create_lines(self, order_lines):
        """ Tax line creation for calculating tax amount using avalara tax code. """
        lines = []
        for line in order_lines:
            if line.product_id:
                tax_code = (
                    line.product_id.tax_code_id and line.product_id.tax_code_id.name) or None
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

    def compute_tax(self):
        """ Create and update tax amount for each and every order line and shipping line.
        @param order_line: send sub_total of each line and get tax amount
        @param shiping_line: send shipping amount of each ship line and get ship tax amount
        """
        if self.env.context.get('doing_compute_tax'):
            return False
        self = self.with_context(doing_compute_tax=True)

        account_tax_obj = self.env['account.tax']
        avatax_config = self.company_id.get_avatax_config_company()

        # Make sure Avatax is configured
        if not avatax_config:
            raise UserError(_(
                'Your Avatax Countries settings are not configured. '
                'You need a country code in the Countries section.  \n'
                'If you have a multi-company installation, '
                'you must add settings for each company.  \n\n'
                'You can update settings in Avatax->Avatax API.'))

        tax_amount = o_tax_amt = 0.0

        # ship from Address / Origin Address either warehouse or company if none
        ship_from_address_id = self.warehouse_id.partner_id or self.company_id.partner_id

        compute_taxes = (self.env.context.get('avatax_recomputation') or
                         avatax_config.enable_immediate_calculation)
        if compute_taxes:
            ava_tax = account_tax_obj.search(
                [('is_avatax', '=', True),
                 ('type_tax_use', 'in', ['sale', 'all']),
                 ('company_id', '=', self.company_id.id)])

            shipping_add_id = self.tax_add_id

            lines = self.create_lines(self.order_line)
            order_date = self.date_order.date()
            if lines:
                if avatax_config.on_line:
                    # Line level tax calculation
                    # tax based on individual order line
                    tax_id = []
                    for line in lines:
                        tax_id = line['tax_id'] and [
                            tax.id for tax in line['tax_id']] or []
                        if ava_tax and ava_tax[0].id not in tax_id:
                            tax_id.append(ava_tax[0].id)
                        ol_tax_amt = account_tax_obj._get_compute_tax(
                            avatax_config, order_date,
                            self.name, 'SalesOrder', self.partner_id, ship_from_address_id,
                            shipping_add_id, [
                                line], self.user_id, self.exemption_code or None, self.exemption_code_id.code or None,
                            currency_id=self.currency_id).TotalTax
                        o_tax_amt += ol_tax_amt  # tax amount based on total order line total
                        line['id'].write(
                            {'tax_amt': ol_tax_amt, 'tax_id': [(6, 0, tax_id)]})
                    tax_amount = o_tax_amt

                elif avatax_config.on_order:
                    tax_amount = account_tax_obj._get_compute_tax(
                        avatax_config, order_date,
                        self.name, 'SalesOrder', self.partner_id, ship_from_address_id,
                        shipping_add_id, lines, self.user_id, self.exemption_code or None, self.exemption_code_id.code or None,
                        currency_id=self.currency_id).TotalTax
                    self.order_line.write({'tax_amt': 0.0})
                else:
                    raise UserError(
                        _('Please select system calls in Avatax API Configuration'))
            else:
                for o_line in self.order_line:
                    o_line.write({'tax_amt': 0.0})

        else:
            self.order_line.write({'tax_amt': 0.0})
        self.write({'tax_amount': tax_amount, 'order_line': []})
        return True

    def avalara_compute_taxes(self):
        """ It used to called manually calculation method of avalara and get tax amount"""
        self.with_context(avatax_recomputation=True).compute_tax()
        return True

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        self.with_context(avatax_recomputation=True).compute_tax()
        return res


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    tax_amt = fields.Float('Avalara Tax', help="tax calculate by avalara")
