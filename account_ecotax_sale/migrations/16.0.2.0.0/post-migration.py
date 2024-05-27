# Copyright 2024 Akretion France (http://www.akretion.com/)
#   @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Due to the bug of update module we need to deactivate view
    openupgrade.logged_query(
        env.cr,
        """
            TRUNCATE TABLE account_ecotax_category RESTART IDENTITY CASCADE;
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
            TRUNCATE TABLE ecotax_sector RESTART IDENTITY CASCADE;
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
            TRUNCATE TABLE ecotax_collector RESTART IDENTITY CASCADE;
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
             TRUNCATE TABLE account_ecotax_classification RESTART IDENTITY CASCADE;
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
            TRUNCATE TABLE account_move_line_ecotax RESTART IDENTITY CASCADE;
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
            TRUNCATE TABLE ecotax_line_product RESTART IDENTITY CASCADE;
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
            INSERT INTO account_ecotax_category (name, code, description, active)
             SELECT name, code, description, active FROM account_ecotaxe_category order by id;
        """,
    )

    openupgrade.logged_query(
        env.cr,
        """
            INSERT INTO ecotax_sector (name, description, active)
             SELECT name, description, active FROM ecotaxe_sector order by id;
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
            INSERT INTO ecotax_collector (name, partner_id, active)
             SELECT name, partner_id, active FROM ecotaxe_collector order by id;
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE account_ecotax_classification ADD COLUMN old_id INTEGER;
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
            INSERT INTO account_ecotax_classification (name, code, ecotax_type, ecotax_coef, default_fixed_ecotax,
             categ_id, sector_id, collector_id, active, company_id,
             product_status, supplier_status, emebi_code, scale_code, old_id)
             SELECT name, code, ecotaxe_type, ecotaxe_coef, default_fixed_ecotaxe,
             categ_id, sector_id, collector_id, active, company_id,
             product_status, supplier_status, emebi_code, scale_code, id FROM account_ecotaxe_classification order by id;
        """,  # noqa
    )
    openupgrade.logged_query(
        env.cr,
        """
            UPDATE account_move SET amount_ecotax = amount_ecotaxe;
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
            UPDATE account_move_line SET subtotal_ecotax = subtotal_ecotaxe, ecotax_amount_unit = ecotaxe_amount_unit;
        """,  # noqa
    )
    openupgrade.logged_query(
        env.cr,
        """
            INSERT INTO account_move_line_ecotax (classification_id, account_move_line_id, amount_unit, force_amount_unit, amount_total)
             SELECT cls.id, account_move_line_id, amount_unit, force_amount_unit, amount_total FROM account_move_line_ecotaxe mle
             INNER JOIN account_ecotax_classification cls on mle.classification_id = cls.old_id  order by id;
        """,  # noqa
    )

    openupgrade.logged_query(
        env.cr,
        """
            INSERT INTO ecotax_line_product (product_tmpl_id, product_id, classification_id, force_amount, amount)
             SELECT product_tmplt_id, product_id, cls.id, force_amount, amount FROM ecotaxe_line_product lp
            INNER JOIN account_ecotax_classification cls on lp.classification_id = cls.old_id
            order by id;
        """,  # noqa
    )
    openupgrade.logged_query(
        env.cr,
        """
            UPDATE product_product SET ecotax_amount = ecotaxe_amount;
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
            UPDATE product_template SET ecotax_amount = ecotaxe_amount;
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
            INSERT INTO sale_order_line_ecotax (classification_id, sale_order_line_id, amount_unit, force_amount_unit, amount_total)
             SELECT cls.id, sale_order_line_id, amount_unit, force_amount_unit, amount_total FROM sale_order_line_ecotaxe ole
             INNER JOIN account_ecotax_classification cls on ole.classification_id = cls.old_id  order by id;
        """,  # noqa
    )

    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE account_ecotax_classification DROP COLUMN old_id;
        """,
    )
