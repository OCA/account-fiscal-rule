from odoo.tests.common import TransactionCase


class TestExemption(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.exemption_type = cls.env["res.partner.exemption.type"].create(
            {"name": "Type A", "exemption_validity_duration": 30}
        )
        cls.exemption = cls.env["res.partner.exemption"].create(
            {
                "partner_id": cls.partner.id,
                "exemption_type": cls.exemption_type.id,
            }
        )

    def test_compute_display_name_basic(self):
        self.assertIn(self.partner.name, self.exemption.display_name)

    def test_compute_display_name_includes_type(self):
        self.assertIn(self.exemption_type.name, self.exemption.display_name)

    def test_compute_display_name_recomputes_on_partner_rename(self):
        self.partner.name = "Renamed Partner"
        self.assertIn("Renamed Partner", self.exemption.display_name)

    def test_compute_display_name_recomputes_on_type_rename(self):
        self.exemption_type.name = "Renamed Type"
        self.assertIn("Renamed Type", self.exemption.display_name)

    def test_compute_display_name_with_exemption_number(self):
        self.exemption.exemption_number = "EX-001"
        self.assertIn("EX-001", self.exemption.display_name)

    def test_create_exemption(self):
        exemption = self.env["res.partner.exemption"].create(
            {"partner_id": self.partner.id}
        )
        self.assertEqual(exemption.state, "draft")
        self.assertEqual(exemption.partner_id, self.partner)
