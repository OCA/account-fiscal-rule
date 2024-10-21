from odoo import models


class QueueJob(models.Model):
    _inherit = "queue.job"

    def _related_action_avatax_rule(self):
        rule = self.args[0]
        action = self.env.ref(
            "account_avatax_exemption.exemption_rule_act_window"
        ).read([])[0]
        action.update(
            {
                "view_mode": "form",
                "res_id": rule.id,
                "domain": [("id", "=", rule.id)],
            }
        )
        return action

    def _related_action_avatax_tax_item(self):
        product = self.args[0]
        action = self.env.ref("product.product_normal_action_sell").read([])[0]
        action.update(
            {
                "view_mode": "form",
                "res_id": product.id,
                "domain": [("id", "=", product.id)],
            }
        )
        return action

    def _related_action_avatax_customer(self):
        partner = self.args[0]
        action = self.env.ref("account.res_partner_action_customer").read([])[0]
        action.update(
            {
                "view_mode": "form",
                "res_id": partner.id,
                "domain": [("id", "=", partner.id)],
            }
        )
        return action
