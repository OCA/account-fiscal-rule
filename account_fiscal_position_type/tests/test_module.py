# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from unittest import mock

from odoo.tests import Form, TransactionCase, tagged
from odoo.tools import file_open


@tagged("-at_install", "post_install")
class Tests(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ResPartner = cls.env["res.partner"]
        cls.AccountFiscalPosition = cls.env["account.fiscal.position"]
        cls.company = cls.env.ref("base.main_company")
        # patch the chart template model to load data from /demo
        # and work without actually modifying the model
        with (
            mock.patch(
                "odoo.addons.account.models.chart_template.file_open"
            ) as patched_file_open,
            mock.patch.object(
                cls.env["account.chart.template"].__class__,
                "_get_chart_template_mapping",
            ) as patched_get_chart_template_mapping,
            mock.patch.object(
                cls.env["account.chart.template"].__class__,
                "_get_account_fiscal_position_type_template_data",
                create=True,
            ) as patched_get_account_fiscal_position_type_template_data,
        ):

            def file_open_from_demo(filename, *args):
                return file_open(filename.replace("/data/", "/demo/"), *args)

            patched_file_open.side_effect = file_open_from_demo

            del patched_get_chart_template_mapping._l10n_template
            patched_get_chart_template_mapping.return_value = {
                "account_fiscal_position_type_demo": {
                    "module": "account_fiscal_position_type",
                    "country_id": cls.company.country_id.id,
                }
            }

            patched_get_account_fiscal_position_type_template_data._l10n_template = (
                "account_fiscal_position_type_demo",
                "template_data",
            )
            patched_get_account_fiscal_position_type_template_data.return_value = {
                "code_digits": "6",
            }

            cls.env["account.chart.template"]._load(
                "account_fiscal_position_type_demo", cls.company, False
            )

        cls.fiscal_position_purchase = cls.env.ref(
            f"account.{cls.company.id}_fiscal_position_purchase",
            raise_if_not_found=False,
        )
        cls.fiscal_position_sale = cls.env.ref(
            f"account.{cls.company.id}_fiscal_position_sale",
            raise_if_not_found=False,
        )
        cls.fiscal_position_all = cls.env.ref(
            f"account.{cls.company.id}_fiscal_position_all",
            raise_if_not_found=False,
        )

    def test_chart_template_generation(self):
        """
        Check if the fiscal position has been correctly created
        """
        self.assertTrue(
            self.fiscal_position_purchase,
            "Correct Creation of 'purchase' Fiscal Position failed",
        )
        self.assertTrue(
            self.fiscal_position_sale,
            "Correct Creation of 'all' Fiscal Position failed",
        )
        self.assertTrue(
            self.fiscal_position_all, "Correct Creation of 'all' Fiscal Position failed"
        )

    def test_invoice_fiscal_position_domain(self):
        """
        Check if suitable fiscal_position_ids is filled correctly
        """
        customer_invoice = (
            self.env["account.move"]
            .with_context(default_move_type="out_invoice")
            .create(
                {
                    "partner_id": self.env["res.partner"].search([], limit=1).id,
                }
            )
        )
        self.assertEqual(
            customer_invoice.suitable_fiscal_position_ids.mapped("type_position_use"),
            ["sale", "all"],
        )

        supplier_invoice = (
            self.env["account.move"]
            .with_context(default_move_type="in_invoice")
            .create(
                {
                    "partner_id": self.env["res.partner"].search([], limit=1).id,
                }
            )
        )
        self.assertEqual(
            supplier_invoice.suitable_fiscal_position_ids.mapped("type_position_use"),
            ["purchase", "all"],
        )

    def test_invoice_fiscal_position_onchange(self):
        """
        Check that a wrongly set fiscal position is reset to empty
        """
        with Form(
            self.env["account.move"].with_context(default_move_type="in_invoice")
        ) as form:
            form.fiscal_position_id = self.fiscal_position_purchase
            self.assertTrue(form.fiscal_position_id)
            form.fiscal_position_id = self.fiscal_position_sale
            self.assertFalse(form.fiscal_position_id)
