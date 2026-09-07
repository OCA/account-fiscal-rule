def pre_init_hook(env):
    env.cr.execute(
        """
        ALTER TABLE account_move ADD COLUMN IF NOT EXISTS amount_ecotax numeric
        """
    )
    env.cr.execute(
        """
        UPDATE account_move SET amount_ecotax = 0.0 WHERE amount_ecotax IS NULL
        """
    )
    env.cr.execute(
        """
        ALTER TABLE account_move_line ADD COLUMN IF NOT EXISTS subtotal_ecotax numeric
        """
    )
    env.cr.execute(
        """
        ALTER TABLE account_move_line
        ADD COLUMN IF NOT EXISTS ecotax_amount_unit numeric
        """
    )
    env.cr.execute(
        """
        UPDATE account_move_line
        SET ecotax_amount_unit = 0.0, subtotal_ecotax = 0.0
        WHERE ecotax_amount_unit IS NULL
        """
    )
