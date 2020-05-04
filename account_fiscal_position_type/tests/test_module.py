# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class Tests(TransactionCase):
    at_install = False
    post_install = True

    def setUp(self):
        super(Tests, self).setUp()
        self.ResPartner = self.env['res.partner']
        self.AccountFiscalPosition = self.env['account.fiscal.position']
        self.company = self.env.ref('base.main_company')
        self.chart_template = self.env.ref(
            'l10n_generic_coa.configurable_chart_template')
        self.fiscal_position_template_purchase = self.env.ref(
            'account_fiscal_position_type.fiscal_position_template_purchase')
        self.fiscal_position_purchase = self.env.ref(
            'account_fiscal_position_type.fiscal_position_purchase')
        self.fiscal_position_sale = self.env.ref(
            'account_fiscal_position_type.fiscal_position_sale')

    # Test Section
    def test_chart_template_generation(self):

        # Generate new CoA based on template
        self.chart_template.generate_fiscal_position(
            False, False, self.company)

        # Check if the fiscal position has been correctly created
        position = self.AccountFiscalPosition.search([
            ('name', '=', self.fiscal_position_template_purchase.name),
            ('type_position_use', '=', 'purchase')])
        self.assertEqual(
            len(position), 1,
            "Correct Creation of 'purchase' Fiscal Position failed")

    def test_partner_check(self):
        with self.assertRaises(ValidationError):
            self.ResPartner.create({
                'name': 'Customer Demo',
                'customer': True,
                'supplier': False,
                'property_account_position_id':
                self.fiscal_position_purchase,
            })

        with self.assertRaises(ValidationError):
            self.ResPartner.create({
                'name': 'Supplier Demo',
                'customer': False,
                'supplier': True,
                'property_account_position_id':
                self.fiscal_position_sale,
            })
