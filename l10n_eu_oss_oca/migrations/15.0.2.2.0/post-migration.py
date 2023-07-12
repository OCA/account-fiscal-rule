# Copyright 2021 Sygel - Manuel Regidor
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade  # pylint: disable=W7936


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_tax at
        SET country_id = at.oss_country_id
        WHERE at.oss_country_id IS NOT NULL
        """,
    )
