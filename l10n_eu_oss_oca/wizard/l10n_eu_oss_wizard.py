# Copyright 2021 Valentin Vinagre <valentin.vinagre@sygel.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class L10nEuOssWizard(models.TransientModel):
    _name = "l10n.eu.oss.wizard"
    _description = "l10n.eu.oss.wizard"

    def _get_default_company_id(self):
        return self.env.company.id

    def _get_eu_res_country_group(self):
        eu_group = self.env.ref("base.europe", raise_if_not_found=False)
        if not eu_group:
            raise ValidationError(
                _(
                    "The Europe country group cannot be found. "
                    "Please update the base module."
                )
            )
        return eu_group

    def _default_fiscal_position_id(self):
        user = self.env.user
        eu_country_group = self._get_eu_res_country_group()
        return self.env["account.fiscal.position"].search(
            [
                ("company_id", "=", user.company_id.id),
                ("vat_required", "=", True),
                ("country_group_id", "=", eu_country_group.id),
            ],
            limit=1,
        )

    def _default_done_country_ids(self):
        user = self.env.user
        eu_country_group = self._get_eu_res_country_group()
        return (
            eu_country_group.country_ids
            - self._default_todo_country_ids()
            - user.company_id.country_id
        )

    def _default_todo_country_ids(self):
        user = self.env.user
        eu_country_group = self._get_eu_res_country_group()
        eu_fiscal = self.env["account.fiscal.position"].search(
            [
                ("country_id", "in", eu_country_group.country_ids.ids),
                ("vat_required", "=", False),
                ("auto_apply", "=", True),
                ("company_id", "=", user.company_id.id),
                ("fiscal_position_type", "=", "b2c"),
            ]
        )
        return (
            eu_country_group.country_ids
            - eu_fiscal.mapped("country_id")
            - user.company_id.country_id
        )

    company_id = fields.Many2one(
        "res.company", string="Company", required=True, default=_get_default_company_id
    )
    done_country_ids = fields.Many2many(
        "res.country",
        "l10n_eu_oss_country_rel_done",
        default=_default_done_country_ids,
        string="Already Supported",
    )
    todo_country_ids = fields.Many2many(
        "res.country",
        "l10n_eu_oss_country_rel_todo",
        default=_default_todo_country_ids,
        string="EU Customers From",
        required=True,
    )
    price_include_tax = fields.Boolean(default=False)
    general_tax = fields.Many2one(comodel_name="account.tax", required=True)
    reduced_tax = fields.Many2one(
        comodel_name="account.tax",
    )
    superreduced_tax = fields.Many2one(
        comodel_name="account.tax",
        string="Super Reduced Tax",
    )
    second_superreduced_tax = fields.Many2one(
        comodel_name="account.tax", string="Second Super Reduced Tax"
    )

    def _prepare_tax_group_vals(self, rate):
        return {"name": _("OSS VAT %s%%") % rate}

    def _prepare_repartition_line_vals(self, original_rep_lines):
        return [
            (
                0,
                0,
                {
                    "factor_percent": line.factor_percent,
                    "repartition_type": line.repartition_type,
                    "account_id": line.repartition_type == "tax"
                    and line.account_id.id
                    or None,
                    "company_id": line.company_id.id,
                    "sequence": line.sequence,
                },
            )
            for line in original_rep_lines
        ]

    def _prepare_tax_vals(self, country_id, tax_id, rate, tax_group):
        return {
            "name": _("OSS for EU to %(country_name)s: %(rate)s")
            % {"country_name": country_id.name, "rate": rate},
            "country_id": self.company_id.account_fiscal_country_id.id,
            "amount": rate,
            "invoice_repartition_line_ids": self._prepare_repartition_line_vals(
                tax_id.invoice_repartition_line_ids
            ),
            "refund_repartition_line_ids": self._prepare_repartition_line_vals(
                tax_id.refund_repartition_line_ids
            ),
            "type_tax_use": "sale",
            "description": "EU-OSS-VAT-{}-{}".format(country_id.code, rate),
            "oss_country_id": country_id.id,
            "company_id": self.company_id.id,
            "price_include": self.price_include_tax,
            "tax_group_id": tax_group.id,
            "sequence": 1000,
        }

    def generate_dict_taxes(self, selected_taxes, oss_rate_id):
        dict_taxes = {}
        # delete emptys values
        oss_rate_id = [i for i in oss_rate_id if i != 0.0]
        for idx, value in enumerate(selected_taxes):
            dict_taxes[value] = oss_rate_id[
                idx if idx < len(oss_rate_id) else len(oss_rate_id) - 1
            ]
        return dict_taxes

    def _prepare_fiscal_position_vals(self, country, taxes_data, oss_states):
        fiscal_pos_name = _("Intra-EU B2C in %(country_name)s") % {
            "country_name": country.name
        }
        fiscal_pos_name += " (EU-OSS-%s)" % country.code
        if oss_states:
            fiscal_pos_name += f" ({', '.join(oss_states.mapped('name'))})"
        return {
            "name": fiscal_pos_name,
            "company_id": self.company_id.id,
            "vat_required": False,
            "auto_apply": True,
            "country_id": country.id,
            "fiscal_position_type": "b2c",
            "tax_ids": [(0, 0, tax_data) for tax_data in taxes_data],
            "oss_oca": True,
            "state_ids": [(6, 0, oss_states.ids)],
        }

    def update_fpos(self, fpos_id, taxes_data):
        fpos_id.mapped("tax_ids").filtered(
            lambda x: x.tax_dest_id.oss_country_id
        ).unlink()
        fpos_id.write({"tax_ids": [(0, 0, tax_data) for tax_data in taxes_data]})

    def generate_eu_oss_taxes(self):
        oss_rate = self.env["oss.tax.rate"]
        account_tax = self.env["account.tax"]
        account_tax_group = self.env["account.tax.group"]
        selected_taxes = []
        fpos_obj = self.env["account.fiscal.position"]
        # Get the taxes configured in the wizard
        if self.general_tax:
            selected_taxes.append(self.general_tax)
        if self.reduced_tax:
            selected_taxes.append(self.reduced_tax)
        if self.superreduced_tax:
            selected_taxes.append(self.superreduced_tax)
        if self.second_superreduced_tax:
            selected_taxes.append(self.second_superreduced_tax)
        for country in self.todo_country_ids:
            oss_rates = oss_rate.search([("oss_country_id", "=", country.id)])
            for oss_rate in oss_rates:
                taxes_data = []
                # Create taxes dict to create
                dict_taxes = self.generate_dict_taxes(
                    selected_taxes, oss_rate.get_rates_list()
                )
                # Create and search taxes
                last_rate = None
                tax_dest_id = None
                for tax, rate in dict_taxes.items():
                    if last_rate != rate:
                        tax_dest_id = self.env["account.tax"].search(
                            [
                                ("amount", "=", rate),
                                ("type_tax_use", "=", "sale"),
                                ("oss_country_id", "=", country.id),
                                ("company_id", "=", self.company_id.id),
                            ],
                            limit=1,
                        )
                        if not tax_dest_id:
                            tax_group = account_tax_group.search(
                                [
                                    (
                                        "name",
                                        "=",
                                        self._prepare_tax_group_vals(rate)["name"],
                                    )
                                ],
                                limit=1,
                            )
                            if not tax_group:
                                tax_group = account_tax_group.create(
                                    self._prepare_tax_group_vals(rate)
                                )
                            tax_dest_id = account_tax.create(
                                self._prepare_tax_vals(country, tax, rate, tax_group)
                            )
                    taxes_data.append(
                        {"tax_src_id": tax.id, "tax_dest_id": tax_dest_id.id}
                    )
                    last_rate = rate
                # Create a fiscal position for the country
                domain = [
                    ("country_id", "=", country.id),
                    ("vat_required", "=", False),
                    ("auto_apply", "=", True),
                    ("company_id", "=", self.company_id.id),
                    ("fiscal_position_type", "=", "b2c"),
                    ("oss_oca", "=", True),
                ]
                if oss_rate.oss_state_ids:
                    domain.append(("state_ids", "in", oss_rate.oss_state_ids.ids))
                else:
                    domain.append(("state_ids", "=", False))
                fpos = self.env["account.fiscal.position"].search(domain)
                if not fpos:
                    data_fiscal = self._prepare_fiscal_position_vals(
                        country, taxes_data, oss_rate.oss_state_ids
                    )
                    fpos_obj.create(data_fiscal)
                else:
                    self.update_fpos(fpos, taxes_data)
        return {"type": "ir.actions.act_window_close"}
