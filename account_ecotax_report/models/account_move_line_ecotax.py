# © 2014-2024 Akretion (http://www.akretion.com)
#   @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountMoveLineEcotax(models.Model):
    _inherit = "account.move.line.ecotax"

    company_id = fields.Many2one(
        comodel_name="res.company",
        related="account_move_line_id.company_id",
        readonly=True,
        store=True,
    )
    invoice_date = fields.Date(
        related="account_move_line_id.date",
        store=True,
    )
    invoice_state = fields.Selection(
        related="account_move_line_id.parent_state", store=True
    )
    classif_categ_id = fields.Many2one(
        "account.ecotax.category",
        string="Classification category",
        related="classification_id.categ_id",
        readonly=True,
        store=True,
    )
    sector_id = fields.Many2one(
        "ecotax.sector",
        string="Ecotax sector",
        related="classification_id.sector_id",
        readonly=True,
        store=True,
    )
    collector_id = fields.Many2one(
        "ecotax.collector",
        string="Ecotax collector",
        related="classification_id.collector_id",
        readonly=True,
        store=True,
    )
    ecotax_type = fields.Selection(
        related="classification_id.ecotax_type", readonly=True, store=True
    )
    supplier_status = fields.Selection(
        related="classification_id.supplier_status", readonly=True, store=True
    )
    currency_id = fields.Many2one(store=True)
    product_id = fields.Many2one(store=True)
    weight = fields.Float(
        related="product_id.weight",
        readonly=True,
        store=True,
    )
