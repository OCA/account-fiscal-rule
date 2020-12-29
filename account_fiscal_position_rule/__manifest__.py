# Copyright (C) 2009-TODAY Akretion <http://www.akretion.com>
#   @author Sébastien BEAU <sebastien.beau@akretion.com>
#   @author Renato Lima <renato.lima@akretion.com>
# Copyright 2012-TODAY Camptocamp SA
#   @author: Guewen Baconnier
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Account Fiscal Position Rule",
    "summary": "Account Fiscal Position Rule",
    "category": "Generic Modules/Accounting",
    "version": "13.0.1.2.0",
    "author": "Akretion, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "http://www.akretion.com",
    "depends": ["account", "l10n_generic_coa"],
    "data": [
        "security/ir.model.access.csv",
        "security/account_fiscal_position_rule_security.xml",
        "views/account_fiscal_position_rule_view.xml",
        "views/account_fiscal_position_rule_template_view.xml",
        "wizard/wizard_account_fiscal_position_rule_view.xml",
    ],
    "installable": True,
}
