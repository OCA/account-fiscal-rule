from odoo import fields, models


class FiscalPosition(models.Model):
    _inherit = "account.fiscal.position"

    is_avatax = fields.Boolean(string="Use Avatax API")
