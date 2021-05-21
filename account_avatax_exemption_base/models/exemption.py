from datetime import timedelta

from odoo import _, api, fields, models


class ResPartnerGroupState(models.Model):
    _name = "res.partner.group.state"
    _description = "Avatax Group of States"

    name = fields.Char()
    country_id = fields.Many2one("res.country")
    state_ids = fields.Many2many(
        "res.country.state",
    )


class ResPartnerExemptionLine(models.Model):
    _name = "res.partner.exemption.line"
    _description = "Avatax Exemption Line"

    name = fields.Char(index=True, default=lambda self: _("New"))
    exemption_id = fields.Many2one("res.partner.exemption", required=True)
    partner_id = fields.Many2one(related="exemption_id.partner_id", store=True)
    state_id = fields.Many2one("res.country.state")
    avatax_id = fields.Char("Avatax Certificate ID", copy=False, readonly=True)
    avatax_status = fields.Boolean(default=True)
    linked_to_customer = fields.Boolean(readonly=True)
    add_exemption_number = fields.Boolean()
    exemption_number = fields.Char()

    @api.model
    def create(self, vals):
        if vals.get("name", _("New")) == _("New"):
            vals["name"] = self.env["ir.sequence"].next_by_code(
                "exemption.line.sequence"
            ) or _("New")
        return super().create(vals)


class ResPartnerExemptionBusinessType(models.Model):
    _name = "res.partner.exemption.business.type"
    _description = "Exemption Activity Type"

    name = fields.Char(required=True)
    avatax_id = fields.Char(required=True, readonly=True)
    exemption_code_id = fields.Many2one("exemption.code", string="Entity Use Code")


class ResPartnerExemptionType(models.Model):
    _name = "res.partner.exemption.type"
    _description = "Avatax Exemption Type"

    name = fields.Char()
    business_type = fields.Many2one(
        "res.partner.exemption.business.type",
        string="Activity Type",
    )
    exemption_code_id = fields.Many2one(
        related="business_type.exemption_code_id",
        string="Entity Use Code",
        readonly=True,
    )
    group_of_state = fields.Many2one(
        "res.partner.group.state", string="Group of States"
    )
    state_ids = fields.Many2many("res.country.state", string="States")
    exemption_validity_duration = fields.Integer(
        help="Validity duration in days", default=30
    )

    @api.onchange("group_of_state")
    def onchange_group_of_state(self):
        if self.group_of_state.state_ids and not self.state_ids:
            self.state_ids = [(6, 0, self.group_of_state.state_ids.ids)]


class ResPartnerExemption(models.Model):
    _name = "res.partner.exemption"
    _description = "Avatax Exemption"
    _inherit = [
        "res.partner.exemption.type",
        "mail.thread",
        "mail.activity.mixin",
    ]

    partner_id = fields.Many2one(
        "res.partner",
        required=True,
        index=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    exemption_type = fields.Many2one(
        "res.partner.exemption.type",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    # Fields already defined in Avatax Exemption Type, adding only readonly attrs
    business_type = fields.Many2one(
        string="Activity Type", readonly=True, states={"draft": [("readonly", False)]}
    )
    exemption_code_id = fields.Many2one(
        related="business_type.exemption_code_id",
        string="Entity Use Code",
        readonly=True,
    )
    group_of_state = fields.Many2one(
        readonly=True, states={"draft": [("readonly", False)]}
    )
    state_ids = fields.Many2many(readonly=True, states={"draft": [("readonly", False)]})

    exemption_number = fields.Char(
        readonly=True, states={"draft": [("readonly", False)]}
    )
    exemption_number_type = fields.Selection(
        [
            ("exemption_number/taxpayer_id", "Exemption Number/Taxpayer ID"),
            ("foreign_diplomat_number", "Foreign Diplomat Number"),
            ("drivers_license_number", "Drivers License Number"),
            ("fein", "FEIN"),
        ],
        default="exemption_number/taxpayer_id",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    effective_date = fields.Date(
        default=lambda self: fields.Date.today(),
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    expiry_date = fields.Date(readonly=True, states={"draft": [("readonly", False)]})
    exemption_line_ids = fields.One2many(
        "res.partner.exemption.line",
        "exemption_id",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("progress", "In Progress"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
        ],
        default="draft",
    )

    def _get_document_folder(self):
        return self.env.company.documents_exemption_folder

    def _check_create_documents(self):
        return (
            self.env.company.documents_exemption_settings
            and super()._check_create_documents()
        )

    def name_get(self):
        res = []
        for record in self:
            if record.exemption_number:
                name = "{} - {}".format(
                    record.exemption_number,
                    record.partner_id.display_name,
                )
            else:
                name = record.partner_id.display_name
            if record.exemption_type:
                name = "{} - {}".format(record.exemption_type.name, name)
            res.append((record.id, name))
        return res

    @api.onchange("partner_id")
    def onchange_partner_id(self):
        avalara_salestax = (
            self.env["avalara.salestax"]
            .sudo()
            .search([("exemption_export", "=", True)], limit=1)
        )
        if avalara_salestax.use_commercial_entity:
            self.partner_id = self.partner_id.commercial_partner_id.id
            return {"domain": {"partner_id": [("parent_id", "=", False)]}}

    @api.onchange("exemption_type", "group_of_state")
    def onchange_exemption_type(self):
        self.business_type = self.exemption_type.business_type.id
        if self.exemption_type.group_of_state and not self.group_of_state:
            self.group_of_state = self.exemption_type.group_of_state.id
        if self.exemption_type or self.group_of_state:
            state_ids = []
            if self.exemption_type.group_of_state.state_ids:
                state_ids += self.exemption_type.group_of_state.state_ids.ids
            if self.exemption_type.state_ids:
                state_ids += self.exemption_type.state_ids.ids
            if self.group_of_state.state_ids:
                state_ids += self.group_of_state.state_ids.ids
            self.state_ids = [(6, 0, list(set(state_ids)))]

    @api.onchange("exemption_type", "effective_date")
    def onchange_effective_date(self):
        if self.exemption_type.exemption_validity_duration and self.effective_date:
            self.expiry_date = self.effective_date + timedelta(
                days=self.exemption_type.exemption_validity_duration
            )

    @api.onchange("state_ids")
    def onchange_state_ids(self):
        if not any(self.exemption_line_ids.mapped("avatax_id")) and not any(
            self.exemption_line_ids.mapped("add_exemption_number")
        ):
            self.exemption_line_ids = [(6, 0, [])]
        for state_id in self.state_ids.ids:
            if state_id not in self.exemption_line_ids.mapped("state_id").ids:
                self.exemption_line_ids += self.exemption_line_ids.new(
                    {
                        "partner_id": self.partner_id.id,
                        "exemption_id": self.id,
                        "state_id": state_id,
                        "avatax_status": True,
                    }
                )
