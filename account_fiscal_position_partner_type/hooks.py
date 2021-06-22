# -*- coding: utf-8 -*-
# Copyright 2021 FactorLibre - Rodrigo Bonilla <rodrigo.bonilla@factorlibre.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def pre_init_hook(cr):
    cr.execute(
        """
ALTER TABLE res_company
ADD COLUMN default_fiscal_position_type character varying DEFAULT null
        """
    )
