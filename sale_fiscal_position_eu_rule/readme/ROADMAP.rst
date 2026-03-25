- Restore a seller-aware cache in ``_compute_fiscal_position_id()`` to recover
  the performance optimisation removed in this override.
- Support for the ``is_service`` flag on sale order lines to handle mixed
  goods/services orders correctly at line level.
