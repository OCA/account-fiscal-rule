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
