# -*- coding: utf-8 -*-

from openerp import api, fields, models, _


class product_tax_code(models.Model):
    """ Define type of tax code: 
    @param type: product is use as product code,
    @param type: freight is use for shipping code
    @param type: service is use for service type product  
    """
    _name = 'product.tax.code'
    _description = 'Tax Code'
   
    name = fields.Char('Code', required=True)
    description = fields.Char('Description')
    type = fields.Selection([('product', 'Product'), ('freight', 'Freight'), ('service', 'Service'),
                          ('digital', 'Digital'), ('other', 'Other')], 'Type', 
                          required=True, help="Type of tax code as defined in AvaTax")
    company_id = fields.Many2one('res.company', 'Company', required=True,
                            default=lambda self: self.env['res.company']._company_default_get('product.tax.code'))


class product_template(models.Model):
    _inherit = "product.template"

    tax_code_id = fields.Many2one('product.tax.code', 'Product Tax Code', help="AvaTax Product Tax Code")
    tax_apply = fields.Boolean('Tax Calculation',help="Use Following Tax code for this Product")
    
    @api.onchange('categ_id')
    def onchange_categ(self):
        self.tax_apply = False
        self.tax_code_id = False
        if self.categ_id and self.categ_id.tax_code_id:
            self.tax_apply = True
            self.tax_code_id = self.categ_id.tax_code_id.id
    
    @api.model
    def create(self, vals):
        p_brw = super(product_template, self).create(vals)
        if p_brw.categ_id and p_brw.categ_id.tax_code_id:
            p_brw.write({'tax_apply': True, 'tax_code_id': p_brw.categ_id.tax_code_id.id})
        else:
            p_brw.write({'tax_apply': False, 'tax_code_id': False})
        return p_brw
    
    @api.multi
    def write(self, vals):
        if 'categ_id' in vals:
            p_brw = self.env['product.category'].browse(vals['categ_id'])
            if p_brw.tax_code_id:
                vals['tax_apply'] = True
                vals['tax_code_id'] = p_brw.tax_code_id.id
            else:
                vals['tax_apply'] = False
                vals['tax_code_id'] = False
        return super(product_template, self).write(vals)

product_template()

class product_product(models.Model):
    _inherit = 'product.product'

    default_code = fields.Char('Product Code', required=True)

    _sql_constraints = [
        ('name_uniq', 'unique(default_code)', 'Product Reference Code must be unique per Company!')
    ]
     

class product_category(models.Model):
    _inherit = "product.category"
    
    tax_code_id = fields.Many2one('product.tax.code', 'Tax Code', help="AvaTax Tax Code")


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: