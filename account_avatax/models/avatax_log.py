from odoo import fields, models
from dateutil.relativedelta import relativedelta


class AvataxLog(models.Model):
    _name = "avatax.log"
    _description = "Avatax API call counter"

    avatax_request = fields.Text(string="Avatax Request")
    avatax_response = fields.Text(string="Avatax Response")
    create_date_time = fields.Datetime("Create Date & Time")
    avatax_type = fields.Selection(
        [
            ("SalesOrder", "Sale Transaction"),
            ("SalesInvoice", "Invoice Transaction"),
            ("others", "Others"),
        ]
    )

    def name_get(self):
        result = []
        for log in self:
            name = "Avatax Log" + " " + str(log.id)
            result.append((log.id, name))
        return result

    def avatax_api_call_counter(self):
        call_counter_config_values = self.env["ir.config_parameter"].sudo().get_param('account_avatax.call_counter_limit')
        if not self.avatax_request:
            logs = self.search([]).filtered(
                lambda p: p.create_date_time.date() == fields.date.today()-relativedelta(days=1)
            )
            sales_call_count = len(
                logs.filtered(lambda p: p.avatax_type == "SalesOrder")
            )
            invoices_call_count = len(
                logs.filtered(lambda p: p.avatax_type == "SalesInvoice")
            )
        if len(logs) > int(call_counter_config_values):
            avatax_api_call_notification = self.env["ir.config_parameter"].sudo().get_param('account_avatax.avatax_api_call_notification_ids')
            if avatax_api_call_notification:
                avatax_api_call_ids = avatax_api_call_notification.replace("[","").replace("]","")
                if avatax_api_call_ids:
                    partner_ids = avatax_api_call_ids.split(",")
                    for partner_id in partner_ids:
                        call_email=self.env['res.partner'].browse(int(partner_id))
                        email = call_email.email
                        self.env.ref(
                            "account_avatax.reaching_limit_avatax_api_call_email"
                        ).with_context(
                            {
                                "sales_call_count": sales_call_count,
                                "invoices_call_count": invoices_call_count,
                                "email": email,
                            }
                        ).send_mail(
                            self.env.company.id, force_send=True
                        )
