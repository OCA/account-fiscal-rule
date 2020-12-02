# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


{
    "name": "Default Partner Fiscal Position",
    "version": "9.0.1.0.1",
    "author": "Coop IT Easy SCRLfs",
    "category": "Accounting",
    "website": "https://www.coopiteasy.be",
    "depends": ["account"],
    "data": [
        "views/account_fiscal_position.xml",
        "security/ir.model.access.csv",
    ],
    "license": "AGPL-3",
    "summary": "Computes default partner fiscal position.",
    "installable": True,
}
