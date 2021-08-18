from ast import literal_eval

from dateutil.relativedelta import relativedelta

from odoo import fields, models


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
        call_counter_config_values = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("account_avatax.call_counter_limit")
        )
        if not self.avatax_request:
            logs = self.search([]).filtered(
                lambda p: p.create_date_time.date()
                == fields.date.today() - relativedelta(days=1)
            )
            sales_call_count = len(
                logs.filtered(lambda p: p.avatax_type == "SalesOrder")
            )
            invoices_call_count = len(
                logs.filtered(lambda p: p.avatax_type == "SalesInvoice")
            )
        if len(logs) > int(call_counter_config_values):
            avatax_api_call_notification = (
                self.env["ir.config_parameter"]
                .sudo()
                .get_param(
                    "account_avatax.avatax_api_call_notification_ids", default="[]"
                )
            )
            user_ids = literal_eval(avatax_api_call_notification)
            user_email = self.env["res.users"].browse(user_ids).mapped("login")
            email = ",".join(user_email)
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
