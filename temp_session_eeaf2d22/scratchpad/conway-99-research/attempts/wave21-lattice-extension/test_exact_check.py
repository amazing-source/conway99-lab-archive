from __future__ import annotations

import unittest
from fractions import Fraction

import exact_check as check


class Wave21LatticeExtensionTests(unittest.TestCase):
    def test_endpoint_cap(self) -> None:
        self.assertEqual(check.determinant_cap(12), 45)
        self.assertLess(
            Fraction(12, 11) ** check.RANK,
            46,
        )

    def test_smooth_indices(self) -> None:
        self.assertEqual(
            check.smooth_indices(45),
            [1, 3, 7, 9, 21, 27],
        )

    def test_weak_index_options(self) -> None:
        result = check.endpoint_index_options(
            12, even_lattice_determinant_floor=1
        )
        self.assertEqual(result["possible_h"], [1, 3, 7, 9, 21])

    def test_even_lattice_index_options(self) -> None:
        result = check.endpoint_index_options(
            12, even_lattice_determinant_floor=3
        )
        self.assertEqual(result["possible_h"], [1, 3, 7, 9])

    def test_hostile_allow_det_q_one(self) -> None:
        weak = check.endpoint_index_options(
            12, even_lattice_determinant_floor=1
        )
        strong = check.endpoint_index_options(
            12, even_lattice_determinant_floor=3
        )
        self.assertIn(21, weak["possible_h"])
        self.assertNotIn(21, strong["possible_h"])

    def test_hostile_remove_mod_four_filter(self) -> None:
        cap = check.determinant_cap(12)
        false_options = {
            (h, det_q, h * det_q)
            for h in check.smooth_indices(cap)
            for det_q in range(3, cap // h + 1, 2)
            if h * det_q <= cap
        }
        strong_options = {
            (row["h"], row["det_q"], row["det_b"])
            for row in check.endpoint_index_options(
                12, even_lattice_determinant_floor=3
            )["options"]
        }
        self.assertIn((3, 5, 15), false_options)
        self.assertNotIn(
            (3, 5, 15),
            strong_options,
        )

    def test_harmonic_entries(self) -> None:
        result = check.harmonic_cubic_data(12)
        self.assertEqual(
            result["entries"],
            {"4": 1376, "1": -1, "0": 0, "-1": 1, "-2": -136},
        )

    def test_harmonic_endpoint_cauchy(self) -> None:
        result = check.harmonic_cubic_data(12)
        self.assertEqual(result["cauchy_rejected_q"], [11, 12])
        self.assertIn(10, result["cauchy_allowed_q"])

    def test_traceless_contraction_floors(self) -> None:
        self.assertEqual(check.contraction_floor(0), 12)
        self.assertEqual(check.contraction_floor(2), 4)
        self.assertEqual(check.contraction_floor(3), 4)
        self.assertEqual(check.contraction_floor(6), 40)

    def test_endpoint_profile_dp_does_not_improve(self) -> None:
        self.assertEqual(
            check.minimum_contraction_trace(231, 470),
            924,
        )
        self.assertLess(924, 1008)

    def test_hostile_q_one_does_not_drive_result(self) -> None:
        self.assertEqual(
            check.minimum_contraction_trace(
                231, 470, forbid_q_one=False
            ),
            924,
        )

    def test_full_audit(self) -> None:
        result = check.audit()
        self.assertEqual(result["claim_label"], "UNKNOWN")
        self.assertIn(
            "No unconditional improvement",
            result["strongest_conclusion"],
        )


if __name__ == "__main__":
    unittest.main()
