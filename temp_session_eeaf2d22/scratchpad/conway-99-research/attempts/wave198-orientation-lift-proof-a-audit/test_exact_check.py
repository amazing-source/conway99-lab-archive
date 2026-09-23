"""Tests for the independent Wave198 hostile audit."""

from fractions import Fraction
import unittest

from .exact_check import derive, independent_remainder


class Wave198ProofAAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = derive()

    def test_verdict(self) -> None:
        self.assertEqual(self.result["verdict"], "ACCEPTED_AS_DERIVED")

    def test_orientation_row(self) -> None:
        orientation = self.result["orientation"]
        self.assertEqual(orientation["flags_per_fixed_orientation"], 5)
        self.assertEqual(orientation["selected_row"], "3*n3+4*p3<=5*T")

    def test_remainder(self) -> None:
        remainder = {k: v for k, v in independent_remainder().items() if v}
        self.assertEqual(
            remainder,
            {
                "a1": Fraction(1, 10),
                "b3": Fraction(3, 5),
                "c2": Fraction(1, 5),
                "g": Fraction(9, 40),
                "W": Fraction(2, 5),
            },
        )

    def test_bound(self) -> None:
        certificate = self.result["certificate"]
        self.assertEqual(certificate["target"], "281457/40")
        self.assertEqual(certificate["integer_Q_lower_bound"], 7037)
        self.assertEqual(certificate["edge_added_projective"], 7730)
        self.assertEqual(certificate["scalar_words"], 15460)

    def test_null(self) -> None:
        null = self.result["rational_null"]
        self.assertFalse(null["asserted_object"])
        self.assertTrue(
            all(
                value == "0"
                for name, value in null["slacks"].items()
                if name != "Q0"
            )
        )

    def test_scope(self) -> None:
        self.assertIn("no graph", self.result["search_scope"])
        self.assertIn("brute-force", self.result["search_scope"])


if __name__ == "__main__":
    unittest.main()
