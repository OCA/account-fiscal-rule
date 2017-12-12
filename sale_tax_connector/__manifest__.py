# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

# pylint: disable=C8101
{
    "name": "Tax Connector Base",
    "summary": "Provides centralized logic for connection with external tax"
               "connectors and subsequent caching of results.",
    "version": "10.0.1.0.0",
    "category": "Connector",
    "website": "https://laslabs.com",
    "author": "LasLabs",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "auto_install": True,
    "depends": [
        "base_tax_connector",
        "sale",
    ],
}
