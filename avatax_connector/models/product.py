from odoo import api, fields, models


class ProductTaxCode(models.Model):
    """ Define type of tax code:
    @param type: product is use as product code,
    @param type: freight is use for shipping code
    @param type: service is use for service type product
    """
    _name = 'product.tax.code'
    _description = 'Tax Code'

    name = fields.Char('Code', required=True)
    description = fields.Char('Description')
    type = fields.Selection(
        [('product', 'Product'),
         ('freight', 'Freight'),
         ('service', 'Service'),
         ('digital', 'Digital'),
         ('other', 'Other')],
        'Type',
        required=True,
        help="Type of tax code as defined in AvaTax")
    company_id = fields.Many2one(
        'res.company', 'Company',
        required=True,
        default=lambda self: self.env['res.company']._get_main_company())


class ProductTemplate(models.Model):
    _inherit = "product.template"

    tax_code_id = fields.Many2one(
        'product.tax.code',
        'Product Tax Code',
        help="AvaTax Product Tax Code")

    @api.onchange('categ_id')
    def onchange_categ(self):
        self.tax_code_id = False
        if self.categ_id and self.categ_id.tax_code_id:
            self.tax_code_id = self.categ_id.tax_code_id.id

    @api.model
    def create(self, vals):
        p_brw = super(ProductTemplate, self).create(vals)
        if p_brw.categ_id.tax_code_id:
            p_brw.write({'tax_code_id': p_brw.categ_id.tax_code_id.id})
        else:
            p_brw.write({'tax_code_id': False})
        return p_brw

    def write(self, vals):
        if 'categ_id' in vals:
            p_brw = self.env['product.category'].browse(vals['categ_id'])
            if p_brw.tax_code_id:
                vals['tax_code_id'] = p_brw.tax_code_id.id
            else:
                vals['tax_code_id'] = False
        return super(ProductTemplate, self).write(vals)


class ProductCategory(models.Model):
    _inherit = "product.category"

    tax_code_id = fields.Many2one(
        'product.tax.code',
        'Tax Code',
        help="AvaTax Tax Code")
