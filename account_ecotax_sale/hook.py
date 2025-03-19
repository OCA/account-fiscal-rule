def pre_init_hook(env):
    env.cr.execute(
        """
        ALTER TABLE sale_order ADD COLUMN IF NOT EXISTS amount_ecotax numeric
        """
    )
    env.cr.execute(
        """
        UPDATE sale_order SET amount_ecotax = 0.0 WHERE amount_ecotax IS NULL
        """
    )
    env.cr.execute(
        """
        ALTER TABLE sale_order_line ADD COLUMN IF NOT EXISTS subtotal_ecotax numeric
        """
    )
    env.cr.execute(
        """
        ALTER TABLE sale_order_line ADD COLUMN IF NOT EXISTS ecotax_amount_unit numeric
        """
    )
    env.cr.execute(
        """
        UPDATE sale_order_line
        SET ecotax_amount_unit = 0.0, subtotal_ecotax = 0.0
        WHERE ecotax_amount_unit IS NULL
        """
    )
