# -*- encoding: utf-8 -*-
# Copyright 2021 Valentín Vinagre <valentin.vinagre@sygel.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "L10n EU OSS",
    "version": "8.0.1.1.0",
    "category": "Accounting & Finance",
    "website": "https://github.com/OCA/l10n-spain",
    "author": "Sygel Technology," "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "development_status": "Production/Stable",
    "depends": ["account", "account_fiscal_position_partner_type"],
    "data": [
        "security/ir.model.access.csv",
        "data/oss.tax.rate.csv",
        "wizard/l10n_eu_oss_wizard.xml",
        "views/res_config_settings.xml",
    ],
}
