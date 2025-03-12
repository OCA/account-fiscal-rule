from odoo import fields, models


class Company(models.Model):
    _inherit = "res.company"

    # Although it is a One2many field, is is ensured to be one or zero records
    avatax_configuration_id = fields.One2many("avalara.salestax", "company_id")
