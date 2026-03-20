# Copyright 2026 Akretion
# @author Guillaume MASSON <guillaume.masson@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import Form

from odoo.addons.account_fiscal_position_eu_rule.tests.common import (
    FiscalPositionEuRuleCommon,
)


class AccountMoveFiscalPositionEuRuleCommon(FiscalPositionEuRuleCommon):
    """Fixtures for account move fiscal position tests.

    Extends FiscalPositionEuRuleCommon with the minimal accounting setup
    required to create invoices on company_fr:
    - Receivable and payable accounts (required by _onchange_partner_id)
    - Revenue account (customer invoice lines)
    - Expense account (vendor bill lines)
    - Sale and purchase journals
    - A minimal chart of accounts flag to prevent RedirectWarning from
      Odoo's _onchange_partner_id when no CoA is installed.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._setup_account_fixtures()

    @classmethod
    def _setup_account_fixtures(cls):
        Account = cls.env["account.account"]

        cls.account_receivable = Account.create(
            {
                "name": "Test Receivable",
                "code": "TREC",
                "account_type": "asset_receivable",
                "company_id": cls.company_fr.id,
                "reconcile": True,
            }
        )
        cls.account_payable = Account.create(
            {
                "name": "Test Payable",
                "code": "TPAY",
                "account_type": "liability_payable",
                "company_id": cls.company_fr.id,
                "reconcile": True,
            }
        )
        cls.account_revenue = Account.create(
            {
                "name": "Test Revenue",
                "code": "TREV",
                "account_type": "income",
                "company_id": cls.company_fr.id,
            }
        )
        cls.account_expense = Account.create(
            {
                "name": "Test Expense",
                "code": "TEXP",
                "account_type": "expense",
                "company_id": cls.company_fr.id,
            }
        )

        # Assign receivable/payable as default properties on all partners
        # used in invoice tests so that _onchange_partner_id does not raise.
        partners = (
            cls.partner_fr_b2b
            | cls.partner_de_b2b
            | cls.partner_de_b2c
            | cls.partner_ie_b2b
            | cls.partner_ie_b2c
            | cls.partner_gb_b2b
            | cls.partner_us_b2b
        )
        partners.with_company(cls.company_fr).write(
            {
                "property_account_receivable_id": cls.account_receivable.id,
                "property_account_payable_id": cls.account_payable.id,
            }
        )

        cls.journal_sale = cls.env["account.journal"].create(
            {
                "name": "Test Sale Journal",
                "code": "TSALE",
                "type": "sale",
                "company_id": cls.company_fr.id,
            }
        )
        cls.journal_purchase = cls.env["account.journal"].create(
            {
                "name": "Test Purchase Journal",
                "code": "TPUR",
                "type": "purchase",
                "company_id": cls.company_fr.id,
            }
        )

        cls.env["account.journal"].create(
            {
                "name": "Miscellaneous",
                "code": "MISC",
                "type": "general",
                "company_id": cls.company_fr.id,
            }
        )

    def _make_out_invoice(self, partner, partner_shipping=None):
        """Create a customer invoice via Form."""
        self.env.user.groups_id += self.env.ref(
            "account.group_delivery_invoice_address"
        )
        self.env.user.groups_id += self.env.ref("account.group_account_user")
        with Form(
            self.env["account.move"]
            .with_company(self.company_fr)
            .with_context(default_move_type="out_invoice")
        ) as form:
            form.partner_id = partner
            if partner_shipping:
                form.partner_shipping_id = partner_shipping
            with form.invoice_line_ids.new() as line:
                line.account_id = self.account_revenue
                line.name = "Test line"
                line.price_unit = 100.0
        return form.save()

    def _make_in_invoice(self, partner, partner_shipping=None):
        """Create a vendor bill via Form."""
        self.env.user.groups_id += self.env.ref(
            "account.group_delivery_invoice_address"
        )
        self.env.user.groups_id += self.env.ref("account.group_account_user")
        with Form(
            self.env["account.move"]
            .with_company(self.company_fr)
            .with_context(default_move_type="in_invoice")
        ) as form:
            form.partner_id = partner
            with form.invoice_line_ids.new() as line:
                line.account_id = self.account_expense
                line.name = "Test line"
                line.price_unit = 100.0
        bill = form.save()
        if partner_shipping:
            bill.partner_shipping_id = partner_shipping
        return bill
