from __future__ import annotations

import importlib.util
import json
import unittest
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave36_ternary_polar_exact_check", HERE / "exact_check.py"
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load exact checker")
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class TernaryPolarBoundTests(unittest.TestCase):
    def test_vector_counts_partition_the_space(self) -> None:
        for dimension in range(1, 13):
            for determinant_class in (1, 2):
                counts = CHECK.norm_residue_counts(
                    dimension, determinant_class
                )
                self.assertEqual(sum(counts), 3**dimension)

    def test_known_low_dimensional_point_counts(self) -> None:
        expected = {
            1: (0, 1),
            2: (2, 1),
            3: (6, 3),
            4: (12, 15),
            5: (36, 45),
            6: (126, 117),
            7: (378, 351),
        }
        for dimension, pair in expected.items():
            self.assertEqual(
                (
                    CHECK.norm_two_projective_points(dimension, 1),
                    CHECK.norm_two_projective_points(dimension, 2),
                ),
                pair,
            )

    def test_rank_eight_srg_parameters(self) -> None:
        square = CHECK.polar_graph_parameters(8, 1)
        nonsquare = CHECK.polar_graph_parameters(8, 2)
        self.assertEqual(
            (
                square["vertex_count"],
                square["degree"],
                square["lambda"],
                square["mu"],
                square["positive_eigenvalue"],
                square["negative_eigenvalue"],
            ),
            (1080, 351, 126, 108, 27, -9),
        )
        self.assertEqual(
            (
                nonsquare["vertex_count"],
                nonsquare["degree"],
                nonsquare["lambda"],
                nonsquare["mu"],
                nonsquare["positive_eigenvalue"],
                nonsquare["negative_eigenvalue"],
            ),
            (1107, 378, 117, 135, 9, -27),
        )

    def test_srg_parameter_identity(self) -> None:
        for dimension in range(7, 13):
            for determinant_class in (1, 2):
                case = CHECK.polar_graph_parameters(
                    dimension, determinant_class
                )
                self.assertEqual(
                    (case["vertex_count"] - case["degree"] - 1)
                    * case["mu"],
                    case["degree"]
                    * (case["degree"] - case["lambda"] - 1),
                )

    def test_eigenvalue_multiplicities(self) -> None:
        for dimension in range(7, 13):
            for determinant_class in (1, 2):
                case = CHECK.polar_graph_parameters(
                    dimension, determinant_class
                )
                self.assertEqual(
                    1
                    + case["positive_multiplicity"]
                    + case["negative_multiplicity"],
                    case["vertex_count"],
                )
                self.assertEqual(
                    case["degree"]
                    + case["positive_multiplicity"]
                    * case["positive_eigenvalue"]
                    + case["negative_multiplicity"]
                    * case["negative_eigenvalue"],
                    0,
                )

    def test_all_dimensions_through_eleven_are_excluded(self) -> None:
        result = CHECK.build_result()
        relevant = [
            case
            for case in result["polar_graph_cases"]
            if case["dimension"] <= 11
        ]
        self.assertEqual(len(relevant), 10)
        self.assertTrue(all(case["excluded"] for case in relevant))

    def test_exact_rank_eleven_extrema(self) -> None:
        square = CHECK.mixing_upper_bound(
            CHECK.polar_graph_parameters(11, 1)
        )
        nonsquare = CHECK.mixing_upper_bound(
            CHECK.polar_graph_parameters(11, 2)
        )
        self.assertEqual(square, Fraction(9561, 61))
        self.assertEqual(nonsquare, Fraction(158, 1))
        self.assertLess(square, 162)
        self.assertLess(nonsquare, 162)

    def test_rank_twelve_determinant_split(self) -> None:
        square = CHECK.mixing_upper_bound(
            CHECK.polar_graph_parameters(12, 1)
        )
        nonsquare = CHECK.mixing_upper_bound(
            CHECK.polar_graph_parameters(12, 2)
        )
        self.assertEqual(square, Fraction(4149, 13))
        self.assertEqual(nonsquare, Fraction(158, 1))
        self.assertGreaterEqual(square, 162)
        self.assertLess(nonsquare, 162)

    def test_distinctness_norm_gap(self) -> None:
        result = CHECK.build_result()
        norms = result["distinctness_norm_check"]
        self.assertEqual(
            norms["congruent_or_antipodal_integer_combination_norm_squared"],
            2 * 15**2,
        )
        self.assertEqual(
            norms["orthogonal_endpoint_row_combination_norm_squared"],
            2 * 441,
        )
        self.assertNotEqual(2 * 15**2, 2 * 441)

    def test_committed_result_matches_regeneration(self) -> None:
        expected = CHECK.canonical_bytes(CHECK.build_result())
        actual = (HERE / "exact-results.json").read_bytes()
        self.assertEqual(actual, expected)
        parsed = json.loads(actual)
        self.assertEqual(parsed["derived_rank_floor"], 12)
        self.assertFalse(parsed["endpoint_excluded"])


if __name__ == "__main__":
    unittest.main()
