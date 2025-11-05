# Copyright (C) 2025 Kencove - Mohamed Alkobrosli
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging
from datetime import datetime

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def add_avatax_app_fields(env):
    """Add 'appname' and 'version' columns if missing."""
    openupgrade.add_fields(
        env,
        [
            (
                "appname",  # field name
                "avalara.salestax",  # model name
                "avalara_salestax",  # table name
                "char",  # odoo field type
                False,  # SQL type override
                "account_avatax_oca",  # module name
                False,  # default value
            ),
            (
                "version",
                "avalara.salestax",
                "avalara_salestax",
                "char",
                False,
                "account_avatax_oca",
                False,
            ),
        ],
    )


@openupgrade.migrate()
def migrate(env, version):
    """Migration entry point for version 16.0.1.7.1"""
    add_avatax_app_fields(env)
    today_str = datetime.today().strftime("%Y%m%d")
    env.cr.execute(
        """
        UPDATE avalara_salestax
        SET appname = COALESCE(appname, %s),
            version = COALESCE(version, %s)
    """,
        (env.company.name, today_str),
    )
    _logger.info("======================================")
    _logger.info("Setting appname and version fields")
    _logger.info("======================================")
