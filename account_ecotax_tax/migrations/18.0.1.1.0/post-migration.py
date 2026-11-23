# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


def migrate(cr, version):
    if not version:
        return
    cr.execute("""
        UPDATE account_tax
        SET amount_type = 'fixed', amount = 0.0
        WHERE is_ecotax
          AND amount_type = 'code'
    """)
