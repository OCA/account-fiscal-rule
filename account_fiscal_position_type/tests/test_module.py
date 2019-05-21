# coding: utf-8
# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class Tests(TransactionCase):

    def setUp(self):
        super(Tests, self).setUp()
        self.AccountFiscalPosition = self.env['account.fiscal.position']
        self.WizardChart = self.env['wizard.multi.charts.accounts']
        self.coa = self.env.ref('account.configurable_chart_template')
        self.fpt_normal_tax = self.env.ref(
            'account.fiscal_position_normal_taxes_template1')
        self.fpt_tax_exempt = self.env.ref(
            'account.fiscal_position_tax_exempt_template2')
        self.company = self.env.ref('base.main_company')

    # Test Section
    # Test disabled because it requires this patch
    # https://github.com/OCA/OCB/pull/850
    # TODO-V10. In new full API, enable this test.
    def _disabled_test_template(self):
        wizard = self.WizardChart.create({
            'company_id': self.company.id,
            'chart_template_id': self.coa.id,
            'code_digits': 6,
            'currency_id': self.company.currency_id.id,
        })
        self.fpt_normal_tax.type_position_use = 'purchase'
        self.fpt_tax_exempt.type_position_use = 'sale'
        wizard.execute()

        fp_normal_taxes = self.AccountFiscalPosition.search([
            ('name', '=', self.fpt_normal_tax.name),
            ('type_position_use', '=', 'purchase')])
        self.AssertEqual(
            len(fp_normal_taxes), 1,
            "Correct Creation of 'purchase' Fiscal Position failed")

        fp_tax_exempt = self.AccountFiscalPosition.search([
            ('name', '=', self.fpt_tax_exempt.name),
            ('type_position_use', '=', 'sale')])
        self.AssertEqual(
            len(fp_tax_exempt), 1,
            "Correct Creation of 'sale' Fiscal Position failed")
