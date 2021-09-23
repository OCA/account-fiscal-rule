# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

import mock

from odoo.tests import Form, common


class TestAccountFiscalPostitionVies(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.ref("base.main_company")
        cls.fp_vat = cls.env["account.fiscal.position"].create(
            {"name": "Test vat required", "auto_apply": True, "vat_required": True}
        )
        cls.fp_vat_vies = cls.env["account.fiscal.position"].create(
            {
                "name": "Test vat VIES required",
                "auto_apply": True,
                "vat_required": True,
                "vat_vies_required": True,
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {"name": "Mr Odoo", "vat": "VAT", "country_id": cls.env.ref("base.es").id}
        )
        cls.vatnumber_path = "odoo.addons.base_vat.models.res_partner.vatnumber"

    def _create_invoice(self):
        move_form = Form(
            self.env["account.move"].with_context(default_type="out_invoice")
        )
        move_form.partner_id = self.partner
        return move_form

    def test_invoice_fiscal_position_views(self):
        invoice = self._create_invoice()
        self.assertEqual(invoice.fiscal_position_id, self.fp_vat)
        # We need to use mock to be sure vies_passed set True
        with mock.patch(self.vatnumber_path) as mock_vatnumber:
            self.company.vat_check_vies = True
            mock_vatnumber.check_vies.return_value = True
            self.partner.vat = "ESB87530432"
            invoice = self._create_invoice()
            self.assertEqual(invoice.fiscal_position_id, self.fp_vat_vies)
