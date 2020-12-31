from odoo import fields, models


class ProductTaxCode(models.Model):
    _inherit = "product.tax.code"

    rule_ids = fields.One2many(
        "exemption.code.rule",
        "avatax_tax_code",
        "Avatax Rules",
    )


class ProductCategory(models.Model):
    _inherit = "product.category"

    def write(self, vals):
        res = super().write(vals)
        if "tax_code_id" in vals:
            products = self.env["product.product"].search(
                [("categ_id", "in", self.ids)]
            )
            if products:
                products.create_job_taxitem()
        return res


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def write(self, vals):
        res = super().write(vals)
        if "tax_code_id" in vals or "categ_id" in vals:
            for template in self:
                template.product_variant_ids.create_job_taxitem()
        return res


class ProductProduct(models.Model):
    _inherit = "product.product"

    avatax_item_id = fields.Char(
        "Avatax TaxItem",
        copy=False,
        readonly=True,
    )

    def create_job_taxitem(self):
        avalara_salestax = (
            self.env["avalara.salestax"]
            .sudo()
            .search([("tax_item_export", "=", True)], limit=1)
        )
        queue_job_sudo = self.env["queue.job"].sudo()
        if not avalara_salestax or self._context.get("skip_job_creation", False):
            return
        self = self.with_context(skip_job_creation=True)
        for product in self.filtered(lambda p: p.default_code):
            if product.categ_id.tax_code_id or product.tax_code_id:
                if product.avatax_item_id:
                    job = queue_job_sudo.search(
                        [
                            ("method_name", "=", "_update_tax_item"),
                            ("state", "!=", "done"),
                            ("args", "ilike", "%[" + str(product.id) + "]%"),
                        ],
                        limit=1,
                    )
                    if not job:
                        avalara_salestax.with_delay(
                            description="Update Tax Item %s" % (product.display_name)
                        )._update_tax_item(product.avatax_item_id, product)
                else:
                    job = queue_job_sudo.search(
                        [
                            ("method_name", "=", "_export_tax_item"),
                            ("state", "!=", "done"),
                            ("args", "ilike", "%[" + str(product.id) + "]%"),
                        ],
                        limit=1,
                    )
                    if not job:
                        avalara_salestax.with_delay(
                            description="Export Tax Item %s" % (product.display_name)
                        )._export_tax_item(product)
            elif (
                product.avatax_item_id
                and not product.categ_id.tax_code_id
                and not product.tax_code_id
            ):
                job = queue_job_sudo.search(
                    [
                        ("method_name", "=", "_delete_tax_item"),
                        ("state", "!=", "done"),
                        ("args", "ilike", "%[" + str(product.id) + "]%"),
                    ],
                    limit=1,
                )
                if not job:
                    avalara_salestax.with_delay(
                        description="Delete Tax Item %s" % (product.display_name)
                    )._delete_tax_item(product)

    def write(self, vals):
        res = super().write(vals)
        if "tax_code_id" in vals or "categ_id" in vals:
            self.create_job_taxitem()
        return res
