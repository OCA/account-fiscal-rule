# © 2014-2023 Akretion (http://www.akretion.com)
#   @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountEcotaxClassification(models.Model):
    _name = "account.ecotax.classification"
    _description = "Account Ecotax Classification"

    name = fields.Char(required=True)
    code = fields.Char()
    ecotax_type = fields.Selection(
        [("fixed", "Fixed"), ("weight_based", "Weight based")],
        required=True,
        help="If ecotax is weight based,"
        "the ecotax coef must take into account\n"
        "the weight unit of measure (kg by default)",
    )
    ecotax_coef = fields.Float(
        digits="Ecotax", compute="_compute_ecotax_vals", readonly=False, store=True
    )
    default_fixed_ecotax = fields.Float(
        digits="Ecotax",
        help="Default fixed ecotax amount.",
        compute="_compute_ecotax_vals",
        readonly=False,
        store=True,
    )
    categ_id = fields.Many2one(
        comodel_name="account.ecotax.category",
        string="Category",
    )
    sector_id = fields.Many2one(
        comodel_name="ecotax.sector",
        string="Ecotax sector",
    )
    collector_id = fields.Many2one(
        comodel_name="ecotax.collector",
        string="Ecotax collector",
    )
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        comodel_name="res.company",
        default=lambda self: self.env.company,
        help="Specify a company"
        " if you want to define this Ecotax Classification only for specific"
        " company. Otherwise, this Fiscal Classification will be available"
        " for all companies.",
    )
    product_status = fields.Selection(
        [("M", "Menager"), ("P", "Professionnel")],
        required=True,
    )
    supplier_status = fields.Selection(
        [
            ("MAN", "Manufacturer"),
            ("RES", "Reseller, under their own brand"),
            ("INT", "Introducer"),
            ("IMP", "Importer"),
            ("REM", "Remote vendor"),
        ],
        required=True,
        help="MAN ==> Manufacturer: is locally established in the country, "
        "and manufactures goods which are subject to ecotaxes\n"
        "under their own name and brand, or designs such goods, "
        "subcontracts the manufacturing and then sells them under "
        "their own name and brand\n"
        "RES ==> Reseller, under their own brand: is locally established "
        "in the country, and sells under their own name or brand goods"
        " subject to ecotax manufactured by others\n"
        "INT ==> Introducer: is locally established and sells on the local "
        "market goods subject to ecotax coming from other countries "
        "of the European Union\n"
        "IMP ==> Importer: is established in France, and sells on the local"
        " market goods subject to ecotax coming from countries outside"
        "the European Union\n"
        "REM ==> Remote vendor: is established in another country of "
        "the European Union or outside the EU, and remotely sells good "
        "subject to ecotaxes to customers in the country",
    )
    intrastat_code = fields.Char()
    scale_code = fields.Char()

    @api.depends("ecotax_type")
    def _compute_ecotax_vals(self):
        for classif in self:
            if classif.ecotax_type == "weight_based":
                classif.default_fixed_ecotax = 0
            elif classif.ecotax_type == "fixed":
                classif.ecotax_coef = 0
