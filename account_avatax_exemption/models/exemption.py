from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class ExemptionRule(models.Model):
    _name = "exemption.code.rule"
    _description = "Avatax Custom Rules"

    name = fields.Char(index=True, default=lambda self: _("New"))
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("progress", "In Progress"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
        ],
        default="draft",
        string="State",
    )
    exemption_code_id = fields.Many2one(
        "exemption.code",
        string="Entity Use Code",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    state_id = fields.Many2one(
        "res.country.state",
        readonly=True,
        states={"draft": [("readonly", False)]},
        string="Region",
    )
    avatax_id = fields.Char("Avatax Rule ID", readonly=True, copy=False)
    avatax_tax_code = fields.Many2one(
        "product.tax.code", readonly=True, states={"draft": [("readonly", False)]}
    )
    is_all_juris = fields.Boolean(
        default=True, readonly=True, states={"draft": [("readonly", False)]}
    )
    avatax_rate = fields.Float(readonly=True, states={"draft": [("readonly", False)]})
    taxable = fields.Boolean()

    @api.constrains("avatax_rate")
    def _check_avatax_rate(self):
        """
        Prevent the Avatax rate with range 0 to 100
        """
        for record in self:
            if record.avatax_rate < 0 or record.avatax_rate > 100:
                raise ValidationError(_("Avatax rate range is from 0 to 100"))

    @api.model
    def create(self, vals):
        if vals.get("name", _("New")) == _("New"):
            vals["name"] = self.env["ir.sequence"].next_by_code(
                "exemption.code.rule.sequence"
            ) or _("New")
        return super().create(vals)

    def export_exemption_rule(self):
        if self.filtered(lambda x: x.state != "draft"):
            raise UserError(_("Rule is not in Draft state to Export Custom Rule"))
        self.write({"state": "progress"})
        avalara_salestax = (
            self.env["avalara.salestax"]
            .sudo()
            .search([("exemption_rule_export", "=", True)], limit=1)
        )
        if not avalara_salestax:
            raise UserError(
                _("Avatax Exemption Rule export is disabled in Avatax configuration")
            )
        avalara_salestax.export_new_exemption_rules(
            rules=self.filtered(lambda x: not x.avatax_id)
        )
        return True

    def cancel_exemption_rule(self):
        self.ensure_one()
        if self.state != "done":
            raise UserError(_("Rule is not in Done state to Cancel Custom Rule"))
        self.write({"state": "progress"})
        avalara_salestax = (
            self.env["avalara.salestax"]
            .sudo()
            .search([("exemption_rule_export", "=", True)], limit=1)
        )
        if not avalara_salestax:
            raise UserError(
                _("Avatax Exemption Rule export is disabled in Avatax configuration")
            )
        avalara_salestax.with_delay(
            priority=5, max_retries=2, description="Cancel Custom Rule %s" % (self.name)
        )._cancel_custom_rule(self)
        return True

    def enable_exemption_rule(self):
        if self.filtered(lambda x: x.state != "cancel"):
            raise UserError(
                _("Rule is not in Cancelled state to Re-Export Custom Rule")
            )
        self.write({"state": "progress"})
        avalara_salestax = (
            self.env["avalara.salestax"]
            .sudo()
            .search([("exemption_rule_export", "=", True)], limit=1)
        )
        if not avalara_salestax:
            raise UserError(
                _("Avatax Exemption Rule export is disabled in Avatax configuration")
            )
        avalara_salestax.export_new_exemption_rules(
            rules=self.filtered(lambda x: not x.avatax_id)
        )
        return True

    def reset_to_draft(self):
        self.write(
            {
                "state": "draft",
            }
        )

    def cancel_exemption_rule_failed(self):
        self.ensure_one()
        queue_job_sudo = self.env["queue.job"].sudo()
        queue_job = queue_job_sudo.search(
            [
                ("method_name", "=", "_export_base_rule_based_on_type"),
                ("state", "!=", "done"),
                ("args", "ilike", "%[" + str(self.id) + "]%"),
            ],
            limit=1,
        )

        if queue_job:
            queue_job.write(
                {
                    "state": "done",
                }
            )
        self.write(
            {
                "state": "cancel",
            }
        )


class ExemptionCode(models.Model):
    _inherit = "exemption.code"

    flag = fields.Boolean(
        "Taxed by default",
        copy=False,
        help="helps to add custom rules for the nexus Avatax states",
    )
    rule_ids = fields.One2many("exemption.code.rule", "exemption_code_id")

    def create_rules(self):
        self.ensure_one()
        avalara_salestax = (
            self.env["avalara.salestax"]
            .sudo()
            .search([("exemption_rule_export", "=", True)], limit=1)
        )
        if not avalara_salestax:
            raise UserError(
                _("Avatax Exemption Rule export is disabled in Avatax configuration")
            )
        for rule in self.rule_ids.filtered(lambda x: x.state == "draft"):
            rule.export_exemption_rule()
        return True


class ResPartnerExemption(models.Model):
    _inherit = "res.partner.exemption"

    def search_exemption_line(self, avatax_id):
        exemption_line = (
            self.env["res.partner.exemption.line"]
            .sudo()
            .search([("avatax_id", "=", avatax_id)], limit=1)
        )
        if exemption_line:
            return "It is already Downloaded"
        avalara_salestax = (
            self.env["avalara.salestax"]
            .sudo()
            .search([("exemption_export", "=", True)], limit=1)
        )
        if avalara_salestax:
            job = avalara_salestax.with_delay(
                description="Download Exemption: %s" % (avatax_id)
            )._search_create_exemption_line(avatax_id)
            return "Success" if job else "Failed"
        else:
            return "Exemption Export is disabled in Avatax configuration!"

    def export_exemption(self):
        self.ensure_one()
        avalara_salestax = (
            self.env["avalara.salestax"]
            .sudo()
            .search([("exemption_export", "=", True)], limit=1)
        )
        if not avalara_salestax:
            raise UserError(
                _("Avatax Exemption export is disabled in Avatax configuration")
            )
        if not self.partner_id.customer_code:
            raise UserError(_("No Customer code added in Partner"))
        if not self.exemption_line_ids:
            raise UserError(_("No Exemption Lines added"))
        if self.partner_id and not self.partner_id.avatax_id:
            avalara_salestax.with_delay(
                priority=0,
                max_retries=2,
                description="Export Customer %s" % (self.partner_id.display_name),
            )._export_avatax_customer(self.partner_id)
        for exemption_line in self.exemption_line_ids:
            if not exemption_line.avatax_id:
                avalara_salestax.with_delay(
                    priority=5,
                    max_retries=2,
                    description="Export Exemption Line %s" % (exemption_line.name),
                )._export_avatax_exemption_line(exemption_line)
        self.write({"state": "progress"})
        return True

    def cancel_exemption(self):
        avalara_salestax = (
            self.env["avalara.salestax"]
            .sudo()
            .search([("exemption_export", "=", True)], limit=1)
        )
        if not avalara_salestax:
            raise UserError(
                _("Avatax Exemption export is disabled in Avatax configuration")
            )
        if self.state == "done":
            for exemption_line in self.exemption_line_ids:
                avalara_salestax.with_delay(
                    priority=5,
                    max_retries=2,
                    description="Disable Exemption Line %s" % (exemption_line.name),
                )._update_avatax_exemption_line_status(exemption_line, False)
            self.write({"state": "progress"})
        else:
            raise UserError(_("Exemption status needs to be in Done status to cancel"))
        return True

    def enable_exemption(self):
        avalara_salestax = (
            self.env["avalara.salestax"]
            .sudo()
            .search([("exemption_export", "=", True)], limit=1)
        )
        if not avalara_salestax:
            raise UserError(
                _("Avatax Exemption export is disabled in Avatax configuration")
            )
        if self.state == "cancel":
            for exemption_line in self.exemption_line_ids:
                avalara_salestax.with_delay(
                    priority=5,
                    max_retries=2,
                    description="Enable Exemption Line %s" % (exemption_line.name),
                )._update_avatax_exemption_line_status(exemption_line, True)
            self.write({"state": "progress"})
        else:
            raise UserError(
                _("Exemption status needs to be in Cancel status to enable")
            )
        return True
