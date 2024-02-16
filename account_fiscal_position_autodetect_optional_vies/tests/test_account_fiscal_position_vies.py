# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from unittest import mock

from odoo.tests import Form, common


class TestAccountFiscalPositionVies(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.ref("base.main_company")
        # We make sure that there is no previous record
        fp_model = cls.env["account.fiscal.position"]
        fp_model.search([("auto_apply", "=", True)]).write({"auto_apply": False})
        cls.fp_vat = fp_model.create(
            {"name": "Test vat required", "auto_apply": True, "vat_required": True}
        )
        cls.fp_vat_vies = fp_model.create(
            {
                "name": "Test vat VIES required",
                "auto_apply": True,
                "vat_required": True,
                "vat_vies_required": True,
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Mr Odoo",
                "vat": "VAT",
                "country_id": cls.env.ref("base.es").id,
                "company_type": "company",
            }
        )
        cls.child_partner = cls.env["res.partner"].create(
            {"name": "Mr Odoo children", "parent_id": cls.partner.id}
        )
        cls.vatnumber_path = "odoo.addons.base_vat.models.res_partner.check_vies"

    def _create_invoice(self, partner):
        move_form = Form(
            self.env["account.move"].with_context(default_move_type="out_invoice")
        )
        move_form.partner_id = partner
        return move_form.save()

    def test_invoice_fiscal_position_without_vies(self):
        invoice = self._create_invoice(self.partner)
        self.assertEqual(invoice.fiscal_position_id, self.fp_vat)
        invoice2 = self._create_invoice(self.child_partner)
        self.assertEqual(invoice2.fiscal_position_id, self.fp_vat)

    def test_invoice_fiscal_position_with_vies(self):
        # We need to use mock to be sure vies_passed set True
        with mock.patch(self.vatnumber_path) as mock_vatnumber:
            self.company.vat_check_vies = True
            mock_vatnumber.check_vies.return_value = True
            self.partner.vat = "ESB87530432"
        invoice = self._create_invoice(self.partner)
        self.assertEqual(invoice.fiscal_position_id, self.fp_vat_vies)
        invoice2 = self._create_invoice(self.child_partner)
        self.assertEqual(invoice2.fiscal_position_id, self.fp_vat_vies)
