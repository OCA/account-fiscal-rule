# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


def migrate(cr, version):
    if not version:
        return
    cr.execute(
        """
        SELECT *
        FROM information_schema.columns
        WHERE table_name='account_move_line_ecotax' and column_name='product_id';
    """
    )
    # field could already be stored in case account_ecotax_report is installed.
    # then no need to managed these new stored fields.
    if cr.fetchall():
        return
    cr.execute(
        """
        ALTER TABLE account_move_line_ecotax ADD COLUMN product_id integer
    """
    )
    cr.execute(
        """
        ALTER TABLE account_move_line_ecotax ADD COLUMN quantity numeric
    """
    )
    cr.execute(
        """
        ALTER TABLE account_move_line_ecotax ADD COLUMN currency_id integer
    """
    )
    cr.execute(
        """
        UPDATE account_move_line_ecotax
        SET product_id = l.product_id,
            quantity = l.quantity,
            currency_id = l.currency_id
        FROM account_move_line l
        WHERE l.id = account_move_line_ecotax.account_move_line_id
    """
    )
