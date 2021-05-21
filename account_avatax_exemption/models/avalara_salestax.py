import requests

from odoo import _, fields, models
from odoo.exceptions import UserError

from odoo.addons.account_avatax.models.avatax_rest_api import AvaTaxRESTService
from odoo.addons.queue_job.exception import FailedJobError


class AvalaraSalestax(models.Model):
    _inherit = "avalara.salestax"

    avatax_company_id = fields.Char(
        "Company ID",
        help="The company ID as defined in the Admin Console of AvaTax",
    )
    tax_item_export = fields.Boolean()
    exemption_export = fields.Boolean()
    exemption_rule_export = fields.Boolean()
    use_commercial_entity = fields.Boolean(default=True)

    def create_transaction(
        self,
        doc_date,
        doc_code,
        doc_type,
        partner,
        ship_from_address,
        shipping_address,
        lines,
        user=None,
        exemption_number=None,
        exemption_code_name=None,
        commit=False,
        invoice_date=None,
        reference_code=None,
        location_code=None,
        is_override=None,
        currency_id=None,
        ignore_error=None,
    ):
        if self.use_commercial_entity and partner.commercial_partner_id:
            partner = partner.commercial_partner_id
        return super().create_transaction(
            doc_date,
            doc_code,
            doc_type,
            partner,
            ship_from_address,
            shipping_address,
            lines,
            user=user,
            exemption_number=exemption_number,
            exemption_code_name=exemption_code_name,
            commit=commit,
            invoice_date=invoice_date,
            reference_code=reference_code,
            location_code=location_code,
            is_override=is_override,
            currency_id=currency_id,
            ignore_error=ignore_error,
        )

    def set_tax_item_info_to_product(self, record, product):
        vals = {}
        product_tax_codes = self.env["product.tax.code"].search([])
        if product:
            tax_code = product_tax_codes.filtered(lambda x: x.name == record["taxCode"])
            if not tax_code:
                tax_code = product_tax_codes.create(
                    {
                        "type": "product",
                        "name": record["taxCode"],
                    }
                )
            vals["tax_code_id"] = tax_code.id
            vals["avatax_item_id"] = record["id"]
            product.with_context(skip_job_creation=True).write(vals)

    def import_exemption_activity_type(self):
        self.ensure_one()
        business_type_obj = self.env["res.partner.exemption.business.type"]
        avatax_restpoint = AvaTaxRESTService(config=self)
        r = avatax_restpoint.client.list_certificate_exempt_reasons()
        result = r.json()
        if "error" in result:
            error = result["error"]
            error_message = "Code: {}\nMessage: {}\nTarget: {}\nDetails;{}".format(
                error.get("code", False),
                error.get("message", False),
                error.get("target", False),
                error.get("details", False),
            )
            raise FailedJobError(error_message)
        for record in result["value"]:
            business_type = business_type_obj.search(
                ["|", ("name", "=", record["name"]), ("avatax_id", "=", record["id"])],
                limit=1,
            )
            if not business_type:
                business_type_obj.create(
                    {
                        "name": record["name"],
                        "avatax_id": record["id"],
                    }
                )

    def import_exemption_country_state_code(self):
        self.ensure_one()
        state_obj = self.env["res.country.state"]
        avatax_restpoint = AvaTaxRESTService(config=self)
        r = avatax_restpoint.client.list_jurisdictions()
        result = r.json()
        if "error" in result:
            error = result["error"]
            error_message = "Code: {}\nMessage: {}\nTarget: {}\nDetails;{}".format(
                error.get("code", False),
                error.get("message", False),
                error.get("target", False),
                error.get("details", False),
            )
            raise FailedJobError(error_message)
        for record in result["value"]:
            if record["type"] != "State":
                continue
            state = state_obj.search(
                [
                    ("code", "=", record["region"]),
                    ("country_id.code", "=", record["country"]),
                    ("avatax_code", "=", False),
                ],
                limit=1,
            )
            if state:
                state.write(
                    {
                        "avatax_code": record["code"],
                        "avatax_name": record["name"],
                    }
                )

        r2 = avatax_restpoint.client.list_nexus_by_company(self.avatax_company_id)
        result2 = r2.json()
        if "error" in result2:
            error = result2["error"]
            error_message = "Code: {}\nMessage: {}\nTarget: {}\nDetails;{}".format(
                error.get("code", False),
                error.get("message", False),
                error.get("target", False),
                error.get("details", False),
            )
            raise FailedJobError(error_message)
        for record in result2["value"]:
            if record["jurisdictionTypeId"] != "State":
                continue
            state = state_obj.search(
                [
                    ("code", "=", record["region"]),
                    ("country_id.code", "=", record["country"]),
                ],
                limit=1,
            )
            if state:
                state.write(
                    {
                        "avatax_nexus": True,
                    }
                )

        exemption_rule_obj = self.env["exemption.code.rule"]
        states = state_obj.search([("avatax_nexus", "=", True)])
        entity_use_codes = self.env["exemption.code"].search([])
        for state in states:
            for use_code in entity_use_codes.filtered(lambda x: x.flag):
                exemption_rule = exemption_rule_obj.search(
                    [
                        ("exemption_code_id", "=", use_code.id),
                        ("state_id", "=", state.id),
                        ("taxable", "=", True),
                    ],
                    limit=1,
                )
                if exemption_rule:
                    continue
                else:
                    exemption_rule_obj.create(
                        {
                            "exemption_code_id": use_code.id,
                            "state_id": state.id,
                            "taxable": True,
                            "state": "draft",
                        }
                    )

    def import_tax_items(self):
        self.ensure_one()
        products = self.env["product.product"].search(
            [("default_code", "!=", False), ("avatax_item_id", "=", False)]
        )

        avatax_restpoint = AvaTaxRESTService(config=self)
        client = avatax_restpoint.client

        result_vals = []
        main_url = url = "{}/api/v2/companies/{}/items".format(
            client.base_url, self.avatax_company_id
        )
        count = 0
        while True:
            r = requests.get(
                url,
                auth=client.auth,
                headers=client.client_header,
                timeout=client.timeout_limit if client.timeout_limit else 1200,
            )
            result = r.json()
            count += 1000
            if "error" in result:
                error = result["error"]
                error_message = "Code: {}\nMessage: {}\nTarget: {}\nDetails;{}".format(
                    error.get("code", False),
                    error.get("message", False),
                    error.get("target", False),
                    error.get("details", False),
                )
                raise FailedJobError(error_message)
            result_vals += result["value"]
            if result["@recordsetCount"] <= count:
                break
            else:
                url = main_url + "?%24skip=" + str(count)

        for product in products:
            for record in result_vals:
                if product.default_code == record["itemCode"]:
                    self.set_tax_item_info_to_product(record, product)
                    break

    def export_new_tax_items(self):
        if not self.ids:
            self = self.search([("tax_item_export", "=", True)], limit=1)
        if not self.tax_item_export:
            return
        products = self.env["product.product"].search(
            [
                ("default_code", "!=", False),
                ("avatax_item_id", "=", False),
                "|",
                ("tax_code_id", "!=", False),
                ("categ_id.tax_code_id", "!=", False),
            ],
        )

        for product in products:
            self.with_delay(
                description="Export Tax Item %s" % (product.display_name)
            )._export_tax_item(product)

    def export_new_exemption_rules(self, rules=None):
        if not self.ids:
            self = self.search([("exemption_rule_export", "=", True)], limit=1)
        if not self.exemption_rule_export:
            return
        if not rules:
            rules = self.env["exemption.code.rule"].search(
                [("avatax_id", "=", False), ("state", "=", "progress")],
            )

        queue_job_sudo = self.env["queue.job"].sudo()
        for rule in rules:
            job = queue_job_sudo.search(
                [
                    ("method_name", "=", "_export_base_rule_based_on_type"),
                    ("state", "!=", "done"),
                    ("args", "ilike", "%[" + str(rule.id) + "]%"),
                ],
                limit=1,
            )
            if not job:
                self.with_delay(
                    priority=5,
                    max_retries=2,
                    description="Export Rule %s" % (rule.name),
                )._export_base_rule_based_on_type(rule)

    def download_exemptions(self):
        if not self.ids:
            self = self.search([("exemption_export", "=", True)], limit=1)
        if not self.exemption_export:
            raise UserError(
                _("Avatax Exemption export is disabled in Avatax configuration")
            )

        avatax_restpoint = AvaTaxRESTService(config=self)
        count = 0
        result_vals = []
        include_option = None
        while True:
            r = avatax_restpoint.client.query_certificates(
                self.avatax_company_id, include_option
            )
            result = r.json()
            count += 100
            if "error" in result:
                error = result["error"]
                error_message = "Code: {}\nMessage: {}\nTarget: {}\nDetails;{}".format(
                    error.get("code", False),
                    error.get("message", False),
                    error.get("target", False),
                    error.get("details", False),
                )
                raise UserError(error_message)
            result_vals += result["value"]
            if result["@recordsetCount"] <= count:
                break
            else:
                include_option = "$skip=" + str(count)

        exemptions = (
            self.env["res.partner.exemption.line"]
            .sudo()
            .search([("avatax_id", "!=", False)])
        )
        for exemption in result_vals:
            avatax_id = exemption["id"]
            if avatax_id not in exemptions.mapped("avatax_id"):
                self.with_delay(
                    description="Download Exemption: %s" % (avatax_id)
                )._search_create_exemption_line(avatax_id)

    def _export_base_rule_based_on_type(self, rule):
        error_message = False
        if not rule.state_id.avatax_code:
            raise FailedJobError("Avatax code for State not setup")
        if not rule.exemption_code_id.flag:
            raise FailedJobError("Taxed by Default is disabled in Exemption Code")
        avatax_restpoint = AvaTaxRESTService(config=self)

        avatax_value = 0
        rule_type = "ExemptEntityRule"
        if rule.taxable:
            avatax_value = 1
        elif rule.avatax_rate == 100.0:
            avatax_value = 1
        elif rule.avatax_rate:
            rule_type = "RateOverrideRule"
            avatax_value = rule.avatax_rate / 100
        tax_rule_info = {
            "companyId": self.avatax_company_id,
            "taxCode": rule.avatax_tax_code.name or None,
            "taxTypeId": "BothSalesAndUseTax",
            "taxRuleTypeId": rule_type,
            "jurisCode": rule.state_id.avatax_code,
            "jurisName": rule.state_id.avatax_name,
            "jurisTypeId": "STA",
            "jurisdictionTypeId": "State",
            "isAllJuris": rule.is_all_juris,
            "value": avatax_value,
            "cap": 0,
            "threshold": 0,
            "effectiveDate": fields.Datetime.to_string(fields.Date.today()),
            "description": "%s - %s - %s"
            % (rule.state_id.avatax_name, rule.exemption_code_id.code, rule.name),
            "country": rule.state_id.country_id.code,
            "region": rule.state_id.code,
            "stateFIPS": rule.state_id.avatax_code,
            "taxTypeGroup": "SalesAndUse",
            "customerUsageType": rule.exemption_code_id.code,
            "taxSubType": "ALL",
        }
        r = avatax_restpoint.client.create_tax_rules(
            self.avatax_company_id, [tax_rule_info]
        )
        result = r.json()
        if "error" in result:
            error = result["error"]
            error_message = (
                "Rule: %s\nCode: %s\nMessage: %s\nTarget: %s\nDetails;%s"
                % (
                    rule.name,
                    error.get("code", False),
                    error.get("message", False),
                    error.get("target", False),
                    error.get("details", False),
                )
            )
            raise FailedJobError(error_message)
        rule.write(
            {
                "avatax_id": result[0]["id"],
                "state": "done",
            }
        )

        return result

    def _cancel_custom_rule(self, rule):
        error_message = False
        if not rule.avatax_id:
            raise FailedJobError("Avatax Custom Rule ID not available")
        avatax_restpoint = AvaTaxRESTService(config=self)

        r = avatax_restpoint.client.delete_tax_rule(
            self.avatax_company_id, rule.avatax_id
        )
        result = r.json()
        if "error" in result:
            error = result["error"]
            error_message = (
                "Rule: %s\nCode: %s\nMessage: %s\nTarget: %s\nDetails;%s"
                % (
                    rule.name,
                    error.get("code", False),
                    error.get("message", False),
                    error.get("target", False),
                    error.get("details", False),
                )
            )
            raise FailedJobError(error_message)
        rule.write(
            {
                "avatax_id": False,
                "state": "cancel",
            }
        )

        return result

    def _export_tax_item(self, product):
        error_message = False
        if not self.tax_item_export:
            raise FailedJobError("Tax Item Export is disabled in Avatax configuration")
        if product.avatax_item_id:
            return "Product exported with Avatax ID: %s" % (product.avatax_item_id)
        avatax_restpoint = AvaTaxRESTService(config=self)

        item_info = {
            "itemCode": product.default_code,
            "taxCode": product.tax_code_id.name or product.categ_id.tax_code_id.name,
            "description": product.name,
        }
        r = avatax_restpoint.client.create_items(self.avatax_company_id, item_info)
        result = r.json()
        if "error" in result:
            error = result["error"]
            error_message = (
                "Product: %s\nCode: %s\nMessage: %s\nTarget: %s\nDetails;%s"
                % (
                    product.display_name,
                    error.get("code", False),
                    error.get("message", False),
                    error.get("target", False),
                    error.get("details", False),
                )
            )
            raise FailedJobError(error_message)
        product.with_context(skip_job_creation=True).write(
            {
                "avatax_item_id": result[0]["id"],
            }
        )

        return result

    def _delete_tax_item(self, product):
        error_message = False
        if not self.tax_item_export:
            raise FailedJobError("Tax Item Export is disabled in Avatax configuration")
        if not product.avatax_item_id:
            return "Avatax ID not available in Product: %s" % (product.display_name)
        avatax_restpoint = AvaTaxRESTService(config=self)

        r = avatax_restpoint.client.delete_item(
            self.avatax_company_id, product.avatax_item_id
        )
        result = r.json()
        if "error" in result:
            error = result["error"]
            error_message = (
                "Product: %s\nCode: %s\nMessage: %s\nTarget: %s\nDetails;%s"
                % (
                    product.display_name,
                    error.get("code", False),
                    error.get("message", False),
                    error.get("target", False),
                    error.get("details", False),
                )
            )
            raise FailedJobError(error_message)
        product.with_context(skip_job_creation=True).write(
            {
                "avatax_item_id": False,
            }
        )

        return result

    def _update_tax_item(self, tax_item_id, product):
        if not self.tax_item_export:
            raise FailedJobError("Tax Item Export is disabled in Avatax configuration")
        error_message = False
        avatax_restpoint = AvaTaxRESTService(config=self)

        item_info = {
            "itemCode": product.default_code,
            "taxCode": product.tax_code_id.name or product.categ_id.tax_code_id.name,
            "description": product.name,
        }
        r = avatax_restpoint.client.update_item(
            self.avatax_company_id, tax_item_id, item_info
        )
        result = r.json()
        if "error" in result:
            error = result["error"]
            error_message = (
                "Product: %s\nCode: %s\nMessage: %s\nTarget: %s\nDetails;%s"
                % (
                    product.display_name,
                    error.get("code", False),
                    error.get("message", False),
                    error.get("target", False),
                    error.get("details", False),
                )
            )
            raise FailedJobError(error_message)

        return result

    def _export_avatax_customer(self, partner):
        error_message = False
        if not self.exemption_export:
            raise FailedJobError(
                "Avatax Exemption export is disabled in Avatax configuration"
            )

        avatax_restpoint = AvaTaxRESTService(config=self)
        if partner.avatax_id:
            return "Avatax Customer ID: %s" % (partner.avatax_id)
        customer_info = [
            {
                "customerCode": partner.customer_code,
                "alternateId": partner.id,
                "name": partner.name,
                "line1": partner.street,
                "city": partner.city,
                "postalCode": partner.zip,
                "phoneNumber": partner.phone,
                "emailAddress": partner.email,
                "contactName": partner.name,
                "country": partner.country_id.code,
                "region": partner.state_id.code,
            }
        ]
        r = avatax_restpoint.client.create_customers(
            self.avatax_company_id, customer_info
        )
        result = r.json()
        if "error" in result:
            error = result["error"]
            error_message = (
                "Partner: %s\nCode: %s\nMessage: %s\nTarget: %s\nDetails;%s"
                % (
                    partner.display_name,
                    error.get("code", False),
                    error.get("message", False),
                    error.get("target", False),
                    error.get("details", False),
                )
            )
            raise FailedJobError(error_message)
        partner.with_context(skip_job_creation=True).write(
            {
                "avatax_id": result[0]["id"],
            }
        )

        return result

    def _export_avatax_exemption_line(self, exemption_line):
        error_message = False
        if not self.exemption_export:
            raise FailedJobError(
                "Avatax Exemption export is disabled in Avatax configuration"
            )

        avatax_restpoint = AvaTaxRESTService(config=self)
        if exemption_line.avatax_id:
            return "Avatax Customer ID: %s" % (exemption_line.avatax_id)
        exemption_line_info = [
            {
                "signedDate": fields.Datetime.to_string(
                    exemption_line.exemption_id.effective_date
                ),
                "expirationDate": fields.Datetime.to_string(
                    exemption_line.exemption_id.expiry_date
                ),
                "filename": exemption_line.name,
                "valid": True,
                "exemptionNumber": exemption_line.exemption_number
                if exemption_line.add_exemption_number
                else exemption_line.exemption_id.exemption_number,
                "exemptPercentage": 100.0,
                "validatedExemptionReason": {
                    "name": exemption_line.exemption_id.business_type.name,
                },
                "exemptionReason": {
                    "name": exemption_line.exemption_id.business_type.name,
                },
                "exposureZone": {
                    "name": exemption_line.state_id.name,
                },
                "pages": [None],
            }
        ]
        r = avatax_restpoint.client.create_certificates(
            self.avatax_company_id, exemption_line_info
        )
        result = r.json()
        if "error" in result:
            error = result["error"]
            error_message = (
                "Exemption: %s\nCode: %s\nMessage: %s\nTarget: %s\nDetails;%s"
                % (
                    exemption_line.display_name,
                    error.get("code", False),
                    error.get("message", False),
                    error.get("target", False),
                    error.get("details", False),
                )
            )
            raise FailedJobError(error_message)
        exemption_line.write(
            {
                "avatax_id": result[0]["id"],
            }
        )

        self.with_delay(
            priority=6,
            max_retries=2,
            description="Link Customer %s with Exemption %s"
            % (exemption_line.partner_id.display_name, exemption_line.name),
        ).link_certificates_to_customer(exemption_line)

        return result

    def link_certificates_to_customer(self, exemption_line):
        error_message = False
        if not self.exemption_export:
            raise FailedJobError(
                "Avatax Exemption export is disabled in Avatax configuration"
            )
        if not exemption_line.exemption_id.partner_id.avatax_id:
            raise FailedJobError("Avatax Customer export has failed")

        avatax_restpoint = AvaTaxRESTService(config=self)
        r = avatax_restpoint.client.link_certificates_to_customer(
            self.avatax_company_id,
            exemption_line.exemption_id.partner_id.customer_code,
            {"certificates": [exemption_line.avatax_id]},
        )
        result = r.json()
        if "error" in result:
            error = result["error"]
            error_message = (
                "Exemption: %s\nCode: %s\nMessage: %s\nTarget: %s\nDetails;%s"
                % (
                    exemption_line.display_name,
                    error.get("code", False),
                    error.get("message", False),
                    error.get("target", False),
                    error.get("details", False),
                )
            )
            raise FailedJobError(error_message)
        exemption_line.write(
            {
                "linked_to_customer": True,
            }
        )
        if all(
            exemption_line.exemption_id.exemption_line_ids.mapped("linked_to_customer")
        ):
            exemption_line.exemption_id.write(
                {
                    "state": "done",
                }
            )
        return result

    def _update_avatax_exemption_line_status(self, exemption_line, exemption_status):
        error_message = False
        if not self.exemption_export:
            raise FailedJobError(
                "Avatax Exemption export is disabled in Avatax configuration"
            )

        avatax_restpoint = AvaTaxRESTService(config=self)
        if not exemption_line.avatax_id:
            raise FailedJobError("Avatax Exemption ID is not found")

        r1 = avatax_restpoint.client.get_certificate(
            self.avatax_company_id, exemption_line.avatax_id
        )
        result1 = r1.json()
        if "error" in result1:
            error = result1["error"]
            error_message = (
                "Exemption: %s\nCode: %s\nMessage: %s\nTarget: %s\nDetails;%s"
                % (
                    exemption_line.display_name,
                    error.get("code", False),
                    error.get("message", False),
                    error.get("target", False),
                    error.get("details", False),
                )
            )
            raise FailedJobError(error_message)
        exemption_line_info = dict(result1)
        exemption_line_info["valid"] = exemption_status
        r2 = avatax_restpoint.client.update_certificate(
            self.avatax_company_id, exemption_line.avatax_id, exemption_line_info
        )
        result2 = r2.json()
        if "error" in result2:
            error = result2["error"]
            error_message = (
                "Exemption: %s\nCode: %s\nMessage: %s\nTarget: %s\nDetails;%s"
                % (
                    exemption_line.display_name,
                    error.get("code", False),
                    error.get("message", False),
                    error.get("target", False),
                    error.get("details", False),
                )
            )
            raise FailedJobError(error_message)
        exemption_line.write(
            {
                "avatax_status": exemption_status,
            }
        )
        exemption_line.exemption_id.write(
            {
                "state": "done" if exemption_status else "cancel",
            }
        )

        return result2

    def _search_create_exemption_line(self, avatax_id):
        exemption_sudo = self.env["res.partner.exemption"].sudo()
        partner_sudo = self.env["res.partner"].sudo()
        error_message = False
        if not self.exemption_export:
            raise FailedJobError(
                "Avatax Exemption export is disabled in Avatax configuration"
            )

        avatax_restpoint = AvaTaxRESTService(config=self)
        r = avatax_restpoint.client.get_certificate(
            self.avatax_company_id, avatax_id, "$include=customers"
        )
        result = r.json()
        if "error" in result:
            error = result["error"]
            error_message = "Code: {}\nMessage: {}\nTarget: {}\nDetails;{}".format(
                error.get("code", False),
                error.get("message", False),
                error.get("target", False),
                error.get("details", False),
            )
            raise FailedJobError(error_message)
        if result.get("customers", []):
            customer_info = result["customers"][0]
            partner = partner_sudo.search(
                [("avatax_id", "=", customer_info["id"])], limit=1
            )
            if partner:
                partner.customer_code = customer_info["customerCode"]
            if not partner:
                partner = partner_sudo.search(
                    [("customer_code", "=", customer_info["customerCode"])], limit=1
                )
            if not partner:
                partner = partner_sudo.search(
                    [("customer_code", "=", "%s:0" % (customer_info["customerCode"]))],
                    limit=1,
                )
            if not partner:
                state = self.env["res.country.state"]
                if "region" in customer_info:
                    state = (
                        self.env["res.country.state"]
                        .sudo()
                        .search(
                            [
                                ("code", "=", customer_info["region"]),
                                ("country_id.code", "=", customer_info["country"]),
                            ],
                            limit=1,
                        )
                    )
                partner_vals = {
                    "name": customer_info["name"],
                    "street": customer_info["line1"],
                    "city": customer_info["city"],
                    "zip": customer_info["postalCode"],
                    "state_id": state.id,
                    "country_id": state.country_id.id,
                    "email": customer_info.get("emailAddress", False),
                    "phone": customer_info.get("phoneNumber", False),
                    "avatax_id": customer_info["id"],
                    "customer_code": customer_info["customerCode"],
                }
                partner = partner_sudo.create(partner_vals)

            # Check if exemption is already available in system
            exemption_line = (
                self.env["res.partner.exemption.line"]
                .sudo()
                .search([("avatax_id", "=", result["id"])], limit=1)
            )
            if exemption_line:
                return "Exemption Already Downloaded\nSearch Response: %s" % (result)
            exposure_zone_info = result["exposureZone"]
            exposure_state = (
                self.env["res.country.state"]
                .sudo()
                .search(
                    [
                        ("code", "=", exposure_zone_info["region"]),
                        ("country_id.code", "=", exposure_zone_info["country"]),
                    ],
                    limit=1,
                )
            )
            business_type = (
                self.env["res.partner.exemption.business.type"]
                .sudo()
                .search([("avatax_id", "=", result["exemptionReason"]["id"])], limit=1)
            )
            exemption_line_vals = {
                "state_id": exposure_state.id,
                "avatax_id": result["id"],
                "avatax_status": result["valid"],
                "linked_to_customer": True,
            }
            exemption_sudo.create(
                {
                    "partner_id": partner.id,
                    "business_type": business_type.id,
                    "exemption_code_id": business_type.exemption_code_id.id,
                    "state_ids": [(6, 0, [exposure_state.id])],
                    "exemption_number": result["exemptionNumber"],
                    "effective_date": result["signedDate"],
                    "expiry_date": result["expirationDate"],
                    "state": "done" if result["valid"] else "cancel",
                    "exemption_line_ids": [(0, 0, exemption_line_vals)],
                }
            )
            return result
        else:
            raise FailedJobError("Exemption ID is not linked with a customer in Avatax")
