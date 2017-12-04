# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "Tax Connector Base",
    "summary": "Provides centralized logic for connection with external tax"
               "connectors and subsequent caching of results.",
    "version": "10.0.1.0.0",
    "category": "Connector",
    "website": "https://laslabs.com",
    "author": "LasLabs, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "account",
        # @TODO: Figure out how to install below in a hook when testing.
        "purchase",
        "sale",
    ],
}
