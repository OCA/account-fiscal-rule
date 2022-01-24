# Copyright 2021 Sygel - Manuel Regidor
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade  # pylint: disable=W7936


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_fiscal_position afp
        SET oss_oca = True
        WHERE afp.country_id IS NOT NULL AND
        afp.vat_required IS False AND
        afp.auto_apply IS True AND
        afp.fiscal_position_type = 'b2c'
        """,
    )
