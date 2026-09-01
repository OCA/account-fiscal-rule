# Copyright (C) 2022 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def pre_init_hook(env):
    # Preserve key data when moving from account_avatax to account_avatax_oca
    # The process is to first install account_avatax_oca
    # and then uninstall account_avatax
    env.cr.execute(
        """
        UPDATE ir_model_data
        SET module = 'account_avatax_oca'
        WHERE name in ('avatax_fiscal_position_us', 'account_avatax')
    """
    )
