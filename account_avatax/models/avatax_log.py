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
        if not self.avatax_request:
            logs = self.search([]).filtered(
                lambda p: p.create_date_time.date() == fields.date.today()
            )
            sales_call_count = len(
                logs.filtered(lambda p: p.avatax_type == "SalesOrder")
            )
            invoices_call_count = len(
                logs.filtered(lambda p: p.avatax_type == "SalesInvoice")
            )
        if len(logs):
            self.env.ref(
                "account_avatax.reaching_limit_avatax_api_call_email"
            ).with_context(
                {
                    "sales_call_count": sales_call_count,
                    "invoices_call_count": invoices_call_count,
                }
            ).send_mail(
                self.env.company.id, force_send=True
            )
