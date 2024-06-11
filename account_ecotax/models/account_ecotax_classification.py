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
            ("FAB", "Fabricant"),
            ("REV", "Revendeur sous sa marque"),
            ("INT", "Introducteur"),
            ("IMP", "Importateur"),
            ("DIS", "Vendeur à distance"),
        ],
        required=True,
        help="FAB ==> Fabricant : est établi en France et fabrique des EEE\n"
        "sous son propre nom ou sa propre marque, ou fait concevoir ou\n"
        " fabriquer des EEE et les commercialise sous\n"
        " son propre nom et sa propre marque\n"
        "REV ==> Revendeur sous sa marque : est établi en France et vend,\n"
        " sous son propre nom ou sa propre marque des EEE produits\n"
        " par d'autres fournisseurs"
        "INT ==> Introducteur : est établi en France et met sur le marché\n"
        "des EEE provenant d'un autre Etat membre"
        "IMP ==> Importateur : est établi en France et met sur marché\n"
        "des EEE provenant de pays hors Union Européenne"
        "DIS ==> Vendeur à distance : est établie dans un autre Etat\n"
        "membre ou dans un pays tiers et vend en France des EEE par\n"
        "communication à distance",
    )
    emebi_code = fields.Char()
    scale_code = fields.Char()
    sale_ecotax_ids = fields.Many2many(
        "account.tax",
        "ecotax_classif_taxes_rel",
        "ecotax_classif_id",
        "tax_id",
        string="Sale EcoTaxe",
        domain=[("is_ecotax", "=", True), ("type_tax_use", "=", "sale")],
    )
    purchase_ecotax_ids = fields.Many2many(
        "account.tax",
        "ecotax_classif_purchase_taxes_rel",
        "ecotax_classif_id",
        "tax_id",
        string="Purchase EcoTaxe",
        domain=[("is_ecotax", "=", True), ("type_tax_use", "=", "purchase")],
    )

    @api.depends("ecotax_type")
    def _compute_ecotax_vals(self):
        for classif in self:
            if classif.ecotax_type == "weight_based":
                classif.default_fixed_ecotax = 0
            if classif.ecotax_type == "fixed":
                classif.ecotax_coef = 0
