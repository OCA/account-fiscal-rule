# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from .common import TestCommon


class TestAccountTax(TestCommon):

    def test_get_by_group(self):
        """It should return the taxes by group."""
        group_1 = self._create_tax_group('Group1')
        group_1_taxes = self._create_tax(tax_group=group_1)
        group_1_taxes += self._create_tax(tax_group=group_1)
        group_2 = self._create_tax_group('Group2')
        group_2_taxes = self._create_tax(tax_group=group_2)
        group_2_taxes += self._create_tax(tax_group=group_2)
        taxes_by_group = (group_1_taxes + group_2_taxes)._get_by_group()
        self.assertEqual(len(taxes_by_group), 2)
        self.assertItemsEqual(taxes_by_group.keys(), [group_1, group_2])
        self.assertItemsEqual(taxes_by_group.values(),
                              [group_1_taxes, group_2_taxes])
