from odoo import fields, models


class ProductTaxCode(models.Model):
    """Define type of tax code:
    @param type: product is use as product code,
    @param type: freight is use for shipping code
    @param type: service is use for service type product
    """

    _name = "product.tax.code"
    _description = "AvaTax Code"

    name = fields.Char("Code", required=True)
    description = fields.Char()
    type = fields.Selection(
        [
            ("product", "Product"),
            ("freight", "Freight"),
            ("service", "Service"),
            ("digital", "Digital"),
            ("other", "Other"),
        ],
        required=True,
        help="Type of tax code as defined in AvaTax",
    )


class ProductTemplate(models.Model):
    _inherit = "product.template"

    tax_code_id = fields.Many2one(
        "product.tax.code", "Product AvaTax Code", help="AvaTax Product Tax Code"
    )

    def _compute_applicable_tax_code(self):
        for product in self:
            product.applicable_tax_code_id = (
                product.tax_code_id or product.categ_id.applicable_tax_code_id
            )

    applicable_tax_code_id = fields.Many2one(
        "product.tax.code",
        "Applicable AvaTax Code",
        compute=_compute_applicable_tax_code,
    )


class ProductCategory(models.Model):
    _inherit = "product.category"

    tax_code_id = fields.Many2one("product.tax.code", "AvaTax Code")

    def _compute_applicable_tax_code(self):
        for categ in self:
            categ.applicable_tax_code_id = categ.tax_code_id
            if not categ.applicable_tax_code_id and categ.parent_id:
                categ.applicable_tax_code_id = categ.parent_id.applicable_tax_code_id

    applicable_tax_code_id = fields.Many2one(
        "product.tax.code",
        "Applicable AvaTax Code",
        compute=_compute_applicable_tax_code,
    )
