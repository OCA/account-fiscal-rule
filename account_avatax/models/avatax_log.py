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
            self = self.search([])
            call_count = len(
                self.filtered(
                    lambda p: p.create_date_time.date() == fields.date.today()
                )
            )
            sales_call_count = len(
                self.filtered(
                    lambda p: p.create_date_time.date() == fields.date.today()
                )
                and self.avatax_type == "SalesOrder"
            )
            invoices_call_count = len(
                self.filtered(
                    lambda p: p.create_date_time.date() == fields.date.today()
                )
                and self.avatax_type == "SalesInvoice"
            )
            others_call_count = len(
                self.filtered(
                    lambda p: p.create_date_time.date() == fields.date.today()
                )
                and self.avatax_type == "others"
            )
        if call_count:
            self.env.ref(
                "account_avatax.reaching_limit_avatax_api_call_email"
            ).with_context(
                sales_call_count=sales_call_count.send_mail(self.id, force_send=True),
                invoices_call_count=invoices_call_count.send_mail(
                    self.id, force_send=True
                ),
                others_call_count=others_call_count.send_mail(self.id, force_send=True),
            )
