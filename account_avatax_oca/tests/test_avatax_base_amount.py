# Copyright 2026 FactorLibre
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import Command
from odoo.tests import common


class TestAvataxBaseAmount(common.TransactionCase):
    """Taxable base reported to AvaTax for price included taxes.

    A tax flagged as ``price_include`` is embedded in ``price_unit``, so the raw
    line amount is gross. Reporting it as a taxable base overstates both the
    base and the tax on the AvaTax side, while the Odoo document itself stays
    balanced, which makes the defect invisible from Odoo alone.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Avatax Base Customer"})
        tax_vals = {
            "amount_type": "percent",
            "type_tax_use": "sale",
            "company_id": cls.env.company.id,
        }
        cls.tax_included = cls.env["account.tax"].create(
            dict(tax_vals, name="Test 8.75% included", amount=8.75, price_include=True)
        )
        cls.tax_excluded = cls.env["account.tax"].create(
            dict(tax_vals, name="Test 8.75% excluded", amount=8.75, price_include=False)
        )
        cls.tax_extra_excluded = cls.env["account.tax"].create(
            dict(tax_vals, name="Test 5% excluded", amount=5.0, price_include=False)
        )
        cls.tax_zero_included = cls.env["account.tax"].create(
            dict(tax_vals, name="Test 0% included", amount=0.0, price_include=True)
        )
        # Same as tax_included but flagged as AvaTax. The invoice path filters
        # out the taxes it owns before setting the new one, so a flagged tax is
        # replaced while an unflagged one is kept alongside it.
        cls.tax_included_avatax = cls.env["account.tax"].create(
            dict(
                tax_vals,
                name="Test 8.75% included AvaTax",
                amount=8.75,
                price_include=True,
                is_avatax=True,
            )
        )

    def _create_invoice(self, line_vals, move_type="out_invoice"):
        return self.env["account.move"].create(
            {
                "move_type": move_type,
                "partner_id": self.partner.id,
                "invoice_line_ids": [Command.create(vals) for vals in line_vals],
            }
        )

    def _line(self, taxes, price_unit=340.0, quantity=1.0, discount=0.0):
        return {
            "name": "Test line",
            "price_unit": price_unit,
            "quantity": quantity,
            "discount": discount,
            "tax_ids": [Command.set(taxes.ids)],
        }

    def test_01_avatax_amount_price_include(self):
        """Gross 340 with an 8.75% included tax reports a net base of 312.64."""
        invoice = self._create_invoice([self._line(self.tax_included)])
        line = invoice.invoice_line_ids
        self.assertAlmostEqual(line._get_avatax_amount(), 312.64, places=2)
        # The gross amount is what the buggy behaviour used to report.
        self.assertNotAlmostEqual(line._get_avatax_amount(), 340.0, places=2)
        # And the reported base matches the subtotal Odoo displays (V2).
        self.assertAlmostEqual(line._get_avatax_amount(), line.price_subtotal, places=2)

    def test_02_avatax_amount_price_exclude(self):
        """Without a price included tax the reported base does not change.

        This pins backward compatibility: the value must stay equal to the
        legacy formula ``price_unit * quantity * (1 - discount / 100)``.
        """
        invoice = self._create_invoice(
            [self._line(self.tax_excluded, price_unit=340.0, quantity=3.0)]
        )
        line = invoice.invoice_line_ids
        legacy_amount = line.price_unit * line.quantity * (1 - line.discount / 100.0)
        self.assertAlmostEqual(line._get_avatax_amount(), legacy_amount, places=2)
        self.assertAlmostEqual(line._get_avatax_amount(), 1020.0, places=2)

    def test_03_avatax_amount_multi_tax(self):
        """A line mixing an included and an excluded tax reports the net base.

        This is the case that rules out deciding by a per line
        ``any(price_include)`` predicate: the predicate is true, yet part of the
        line taxes is not embedded in the price, so reporting the gross amount
        with an AvaTax ``taxIncluded`` flag would overstate the base.

        Only the included tax comes out of the base. The excluded one still
        applies on top of it, which the line total pins.
        """
        taxes = self.tax_included | self.tax_extra_excluded
        invoice = self._create_invoice([self._line(taxes)])
        line = invoice.invoice_line_ids
        base = line._get_avatax_amount()
        # 340 gross / 1.0875 = 312.64 net, the 5% excluded tax does not move it.
        self.assertAlmostEqual(base, 312.64, places=2)
        self.assertAlmostEqual(base, line.price_subtotal, places=2)
        # Adding an excluded tax to the line leaves the taxable base untouched.
        base_only_included = self._create_invoice(
            [self._line(self.tax_included)]
        ).invoice_line_ids._get_avatax_amount()
        self.assertAlmostEqual(base, base_only_included, places=2)
        # And the excluded tax is still charged on top: 312.64 + 27.36 + 15.63.
        self.assertAlmostEqual(line.price_total, 355.63, places=2)

    def test_04_avatax_amount_discount(self):
        """The net base is computed on the already discounted price."""
        invoice = self._create_invoice(
            [self._line(self.tax_included, discount=10.0)],
        )
        line = invoice.invoice_line_ids
        # 340 * 0.9 = 306 gross -> 306 / 1.0875 = 281.38 net
        self.assertAlmostEqual(line._get_avatax_amount(), 281.38, places=2)

    def test_05_avatax_amount_refund_price_include(self):
        """A credit note reports the same net base with a negative sign.

        AvaTax requires refund lines to carry a negative amount.
        """
        refund = self._create_invoice(
            [self._line(self.tax_included)], move_type="out_refund"
        )
        line = refund.invoice_line_ids
        # The net base is the same 312.64 the invoice reports, carried negative
        # because the move is outbound.
        self.assertAlmostEqual(line.price_subtotal, 312.64, places=2)
        prepared = line._avatax_prepare_line(sign=1)
        self.assertLess(prepared["amount"], 0.0)
        self.assertAlmostEqual(prepared["amount"], -312.64, places=2)

    def test_06_avatax_amount_invoice_sign_positive(self):
        """A customer invoice reports a positive amount."""
        invoice = self._create_invoice([self._line(self.tax_included)])
        prepared = invoice.invoice_line_ids._avatax_prepare_line(sign=1)
        self.assertAlmostEqual(prepared["amount"], 312.64, places=2)

    def test_07_avatax_amount_qty_one(self):
        """The documented ``qty`` argument still yields a unit net amount.

        ``_get_avatax_amount`` documents that it can be called with ``qty=1`` to
        obtain a unit price. No caller does so in this version, but the argument
        is public API and must keep working, now also net of included taxes.
        """
        invoice = self._create_invoice([self._line(self.tax_included, quantity=2.0)])
        line = invoice.invoice_line_ids
        # Whole line: 680 gross -> 625.29 net, rounded once for the line.
        self.assertAlmostEqual(line._get_avatax_amount(), 625.29, places=2)
        # Single unit: 340 gross -> 312.64 net.
        self.assertAlmostEqual(line._get_avatax_amount(qty=1), 312.64, places=2)

    def test_08_avatax_amount_no_tax(self):
        """A line without taxes keeps the plain discounted line amount."""
        invoice = self._create_invoice(
            [self._line(self.env["account.tax"], quantity=2.0, discount=25.0)]
        )
        line = invoice.invoice_line_ids
        self.assertAlmostEqual(line._get_avatax_amount(), 510.0, places=2)
        self.assertAlmostEqual(line._get_avatax_amount(qty=1), 255.0, places=2)

    def test_09_avatax_amount_zero_price_line(self):
        """A zero priced line with a 0% included tax reports 0 without failing.

        Real production shipping lines look like this, and they are the template
        ``get_avalara_tax`` copies, so the flag travels to every tax it creates.
        """
        invoice = self._create_invoice(
            [self._line(self.tax_zero_included, price_unit=0.0)]
        )
        line = invoice.invoice_line_ids
        self.assertEqual(line._get_avatax_amount(), 0.0)
        # The line is still reported, because it has a quantity.
        prepared_lines = invoice._avatax_prepare_lines()
        self.assertEqual(len(prepared_lines), 1)
        self.assertAlmostEqual(prepared_lines[0]["amount"], 0.0, places=2)

    def test_10_avatax_round_trip_stability(self):
        """The reported base converges when AvaTax writes its tax back.

        The line starts with a tax flagged as AvaTax, so ``_avatax_compute_tax``
        filters it out and the tax it stores replaces it. With
        ``invoice_calculate_tax`` the cycle reruns on every save, and the base is
        derived from whatever tax the line carries at that moment, so it must
        reach a fixed point instead of drifting.

        The AvaTax tax is modelled as price included because that is the flag of
        the 0% template it is copied from in the production configuration. See
        test_12 for what happens when the starting tax is not flagged, and is
        therefore kept alongside instead of replaced.
        """
        invoice = self._create_invoice([self._line(self.tax_included_avatax)])
        line = invoice.invoice_line_ids
        bases = []
        for iteration in range(4):
            base = line._get_avatax_amount()
            bases.append(invoice.currency_id.round(base))
            # AvaTax answers with the tax for that base, and the module derives
            # the rate as taxCalculated / taxableAmount before storing the tax.
            tax_calculated = invoice.currency_id.round(base * 0.0875)
            rate = round(tax_calculated / base * 100, 4) if base else 0.0
            avatax_tax = self.env["account.tax"].create(
                {
                    "name": "AvaTax %s%% (%s)" % (rate, iteration),
                    "amount_type": "percent",
                    "amount": rate,
                    "price_include": True,
                    "type_tax_use": "sale",
                    "company_id": self.env.company.id,
                    "is_avatax": True,
                }
            )
            # price_subtotal depends on tax_ids, so it recomputes on read.
            line.tax_ids = [Command.set(avatax_tax.ids)]
        # Once the rate settles the base must stop moving.
        self.assertEqual(
            bases[-1],
            bases[-2],
            "The taxable base keeps drifting across round trips: %s" % bases,
        )
        # And it must stay net, never fall back to the gross amount.
        self.assertLess(bases[-1], 340.0)

    def test_11_avatax_amount_negative_quantity(self):
        """A negative quantity line reports a positive amount.

        ``_avatax_prepare_line`` flips the sign explicitly for negative
        quantities, so the reported amount must stay positive on a customer
        invoice even though price_subtotal is negative.
        """
        invoice = self._create_invoice([self._line(self.tax_included, quantity=-1.0)])
        line = invoice.invoice_line_ids
        self.assertLess(line.price_subtotal, 0.0)
        prepared = line._avatax_prepare_line(sign=1)
        self.assertGreater(prepared["amount"], 0.0)
        self.assertAlmostEqual(prepared["amount"], 312.64, places=2)

    def test_12_round_trip_with_accumulated_taxes(self):
        """Known risk: when the AvaTax tax is added next to a price included
        one, the reported base drifts downwards on every recomputation.

        The invoice path only filters out the taxes flagged as AvaTax before
        storing its own (see ``account.move._avatax_compute_tax``), so a tax that
        is not flagged is kept and the new one lands next to it. If the tax
        AvaTax creates is price included too -- it inherits that flag from the 0%
        template it is copied from -- the line ends up with two price included
        taxes, and Odoo strips both from the base.

        The base then no longer converges: it falls below the correct net amount
        and keeps falling. This test pins that behaviour so it stays a known
        limitation of the configuration rather than a surprise. The healthy
        configurations are covered by test_10.
        """
        invoice = self._create_invoice([self._line(self.tax_included)])
        line = invoice.invoice_line_ids
        first_base = line._get_avatax_amount()
        self.assertAlmostEqual(first_base, 312.64, places=2)

        # AvaTax answers for that base, and the module stores its tax alongside
        # the existing one because the latter is not flagged as AvaTax.
        rate = round(
            invoice.currency_id.round(first_base * 0.0875) / first_base * 100, 4
        )
        avatax_tax = self.env["account.tax"].create(
            {
                "name": "AvaTax %s%%" % rate,
                "amount_type": "percent",
                "amount": rate,
                "price_include": True,
                "type_tax_use": "sale",
                "company_id": self.env.company.id,
                "is_avatax": True,
            }
        )
        line.tax_ids = [Command.set((self.tax_included | avatax_tax).ids)]

        second_base = line._get_avatax_amount()
        # Both taxes are stripped, so the base drops well below the correct one
        # (roughly 340 / (1 + 0.0875 + 0.087513)).
        self.assertLess(second_base, first_base)
        self.assertNotAlmostEqual(second_base, 312.64, places=2)
