# Copyright (C) 2019-Today GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestModule(TransactionCase):

    def setUp(self):
        super().setUp()
        self.ResPartner = self.env['res.partner']
        self.AccountInvoice = self.env['account.invoice']

        self.fiscal_position_everybody = self.env.ref(
            'account_fiscal_position_usage_group.fiscal_position_everybody')
        self.fiscal_position_restricted = self.env.ref(
            'account_fiscal_position_usage_group.fiscal_position_restricted')
        self.demo_group_restricted = self.env.ref(
            'account_fiscal_position_usage_group.demo_group_restricted')
        self.partner_vals = {
            'name': 'Demo',
        }
        self.invoice_vals = {
            'partner_id': self.env.ref("base.res_partner_2").id,
        }

    # Test Section
    def test_01_create_partner_with_non_restricted_position(self):
        self.partner_vals.update({
            'property_account_position_id': self.fiscal_position_everybody.id,
        })
        self.ResPartner.create(self.partner_vals)

    def test_02_create_partner_with_restricted_position_forbidden(self):
        self.partner_vals.update({
            'property_account_position_id': self.fiscal_position_restricted.id,
        })
        # Should fail if current user is not member of the group
        with self.assertRaises(ValidationError):
            self.ResPartner.create(self.partner_vals)

    def test_03_create_partner_with_restricted_position_allowed(self):
        self.partner_vals.update({
            'property_account_position_id': self.fiscal_position_restricted.id,
        })
        # Should success if current user is member of the group
        self.demo_group_restricted.users = [self.env.user.id]
        self.ResPartner.create(self.partner_vals)

    def test_04_create_invoice_with_non_restricted_position(self):
        self.invoice_vals.update({
            'fiscal_position_id': self.fiscal_position_everybody.id,
        })
        self.AccountInvoice.create(self.invoice_vals)

    def test_05_create_invoice_with_restricted_position_forbidden(self):
        self.invoice_vals.update({
            'fiscal_position_id': self.fiscal_position_restricted.id,
        })
        # Should fail if current user is not member of the group
        with self.assertRaises(ValidationError):
            self.AccountInvoice.create(self.invoice_vals)

    def test_06_create_invoice_with_restricted_position_allowed(self):
        self.invoice_vals.update({
            'fiscal_position_id': self.fiscal_position_restricted.id,
        })
        # Should success if current user is member of the group
        self.demo_group_restricted.users = [self.env.user.id]
        self.AccountInvoice.create(self.invoice_vals)
