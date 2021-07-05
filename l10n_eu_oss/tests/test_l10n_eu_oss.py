# Copyright 2021 Valentin Vinagre <valentin.vinagre@sygel.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import SavepointCase


class TestL10nEuOss(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestL10nEuOss, cls).setUpClass()
        # MODELS
        cls.oss_wizard = cls.env["l10n.eu.oss.wizard"]
        cls.res_country = cls.env["res.country"]
        cls.account_tax = cls.env["account.tax"]
        cls.account_fiscal_position = cls.env["account.fiscal.position"]
        # INSTANCES
        # Company
        cls.company_main = cls.env.ref("base.main_company")
        # Sale Taxes
        tax_vals = {
            "name": "general tax",
            "amount": 20.0,
            "type_tax_use": "sale",
            "amount_type": "percent",
            "company_id": cls.company_main.id,
        }
        cls.general_tax = cls.account_tax.create(tax_vals)
        tax_vals.update({"name": "reduced tax", "amount": 10.0})
        cls.reduced_tax = cls.account_tax.create(tax_vals)
        tax_vals.update({"name": "superreduced tax", "amount": 5.0})
        cls.superreduced_tax = cls.account_tax.create(tax_vals)
        tax_vals.update({"name": "second superreduced tax", "amount": 2.0})
        cls.second_superreduced_tax = cls.account_tax.create(tax_vals)
        # Oss tax rate
        cls.oss_tax_rate_fr = cls.env.ref("l10n_eu_oss.oss_eu_rate_fr")
        # Country
        cls.country_fr = cls.env.ref("base.fr")

    def _default_todo_country_ids(self):
        eu_country_group = self.env.ref("base.europe", raise_if_not_found=False)
        eu_fiscal = self.env["account.fiscal.position"].search(
            [
                ("country_id", "in", eu_country_group.country_ids.ids),
                ("vat_required", "=", False),
                ("auto_apply", "=", True),
                ("company_id", "=", self.company_main.id),
                ("fiscal_position_type", "=", "b2c"),
            ]
        )
        return (
            eu_country_group.country_ids
            - eu_fiscal.mapped("country_id")
            - self.company_main.country_id
        )

    @classmethod
    def _oss_wizard_create(cls, extra_vals):
        vals = cls.oss_wizard.default_get(list(cls.oss_wizard.fields_get()))
        vals.update(extra_vals)
        oss_wizard_id = cls.oss_wizard.create(vals)
        return oss_wizard_id

    def _fpos_search(self, country_id):
        return self.account_fiscal_position.search(
            [
                ("country_id", "=", country_id),
                ("vat_required", "=", False),
                ("auto_apply", "=", True),
                ("company_id", "=", self.company_main.id),
                ("fiscal_position_type", "=", "b2c"),
            ]
        )

    def _tax_search(self, country_id, amount):
        return self.account_tax.search(
            [
                ("amount", "=", amount),
                ("type_tax_use", "=", "sale"),
                ("oss_country_id", "=", country_id),
                ("company_id", "=", self.company_main.id),
            ]
        )

    def test_01(self):
        wizard_vals = {
            "company_id": self.company_main.id,
            "general_tax": self.general_tax.id,
        }
        wizard = self._oss_wizard_create(wizard_vals)
        self.assertEqual(wizard.todo_country_ids, self._default_todo_country_ids())
        self.assertEqual(wizard.done_country_ids, self.res_country)
        wizard.todo_country_ids = [(6, 0, [self.country_fr.id])]
        wizard.generate_eu_oss_taxes()
        fpos_id = self._fpos_search(self.country_fr.id)
        self.assertEqual(len(fpos_id.tax_ids), 1)
        self.assertEqual(fpos_id.tax_ids[0].tax_src_id.id, self.general_tax.id)
        self.assertEqual(
            fpos_id.tax_ids[0].tax_dest_id.amount, self.oss_tax_rate_fr.general_rate
        )
        # Change amount in one tax and relaunch wizard
        original_amount = self.oss_tax_rate_fr.general_rate
        self.oss_tax_rate_fr.general_rate = 19.9
        wizard = self._oss_wizard_create(wizard_vals)
        self.assertEqual(
            wizard.todo_country_ids, self._default_todo_country_ids() - self.country_fr
        )
        self.assertEqual(wizard.done_country_ids, self.country_fr)
        wizard.todo_country_ids = [(6, 0, [self.country_fr.id])]
        wizard.generate_eu_oss_taxes()
        self.assertEqual(len(fpos_id.tax_ids), 1)
        self.assertEqual(fpos_id.tax_ids[0].tax_dest_id.amount, 19.9)
        original_tax = self._tax_search(self.country_fr.id, original_amount)
        self.assertTrue(original_tax)
