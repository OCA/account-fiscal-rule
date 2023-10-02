# Copyright (C) 2020 Open Source Integrators
# Copyright (C) 2023 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from ast import literal_eval

from odoo import api, fields, models


class Settings(models.TransientModel):
    _inherit = "res.config.settings"

    avatax_api_call_notification_ids = fields.Many2many(
        "res.users",
        readonly=False,
    )
    call_counter_limit = fields.Integer(
        config_parameter="account_avatax_oca.call_counter_limit",
        default=100,
    )

    @api.model
    def get_values(self):
        res = super(Settings, self).get_values()
        ICPSudo = self.env["ir.config_parameter"].sudo()
        get_param = "account_avatax_oca.avatax_api_call_notification_ids"
        calls = ICPSudo.get_param(get_param)
        res.update(
            avatax_api_call_notification_ids=[(6, 0, literal_eval(calls))]
            if calls
            else False,
        )
        return res

    def set_values(self):
        res = super(Settings, self).set_values()
        ICPSudo = self.env["ir.config_parameter"].sudo()
        set_param = "account_avatax_oca.avatax_api_call_notification_ids"
        ICPSudo.set_param(set_param, self.avatax_api_call_notification_ids.ids)
        return res
