#!/usr/bin/env python3
"""Hostile tests for the independent ternary polar-graph verifier."""

from __future__ import annotations

from fractions import Fraction
import importlib.util
from pathlib import Path
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave36_ternary_polar_independent", HERE / "independent_check.py"
)
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class TernaryPolarIndependentTests(unittest.TestCase):
    def test_point_count_table_both_determinant_classes(self) -> None:
        rows = CHECK.point_count_table()
        self.assertEqual(
            [(row["square"], row["nonsquare"]) for row in rows],
            [
                (0, 1),
                (2, 1),
                (6, 3),
                (12, 15),
                (36, 45),
                (126, 117),
                (378, 351),
                (1080, 1107),
                (3240, 3321),
                (9882, 9801),
                (29646, 29403),
                (88452, 88695),
            ],
        )

    def test_recurrence_matches_direct_projective_enumeration(self) -> None:
        for dimension in range(1, 8):
            for determinant_class in (1, 2):
                self.assertEqual(
                    CHECK.norm_two_projective_count(dimension, determinant_class),
                    len(CHECK.projective_norm_two_points(dimension, determinant_class)),
                )

    def test_nonadjacent_gram_span_is_degenerate(self) -> None:
        for inner in (1, 2):
            self.assertEqual((2 * 2 - inner * inner) % 3, 0)

    def test_exhaustive_graph_parameters_through_dimension_seven(self) -> None:
        for dimension in range(4, 8):
            for determinant_class in (1, 2):
                result = CHECK.enumerated_graph_parameters(dimension, determinant_class)
                params = CHECK.exact_srg_parameters(dimension, determinant_class)
                self.assertEqual(result["all_degrees"], [params["k"]])
                self.assertEqual(
                    result["all_adjacent_common_neighbor_counts"], [params["lambda"]]
                )
                self.assertEqual(
                    result["all_nonadjacent_common_neighbor_counts"], [params["mu"]]
                )
                self.assertEqual(result["all_nonadjacent_gram_determinants"], [0])

    def test_degenerate_span_three_lift_formula_is_active(self) -> None:
        for dimension in range(7, 13):
            for determinant_class in (1, 2):
                params = CHECK.exact_srg_parameters(dimension, determinant_class)
                expected_mu = 3 * CHECK.norm_two_projective_count(
                    dimension - 3, determinant_class
                )
                self.assertEqual(params["mu"], expected_mu)
        for determinant_class in (1, 2):
            params = CHECK.exact_srg_parameters(8, determinant_class)
            wrong_codimension_two = CHECK.norm_two_projective_count(
                6, determinant_class
            )
            self.assertNotEqual(params["mu"], wrong_codimension_two)

    def test_all_srg_parameter_identities_and_spectra(self) -> None:
        for dimension in range(7, 13):
            for determinant_class in (1, 2):
                params = CHECK.exact_srg_parameters(dimension, determinant_class)
                spectrum = CHECK.eigen_data(params)
                self.assertEqual(
                    (params["v"] - params["k"] - 1) * params["mu"],
                    params["k"] * (params["k"] - params["lambda"] - 1),
                )
                self.assertEqual(
                    1 + spectrum["theta_multiplicity"] + spectrum["tau_multiplicity"],
                    params["v"],
                )

    def test_exact_boundary_table(self) -> None:
        expected = {
            (7, 1): Fraction(75),
            (7, 2): Fraction(86),
            (8, 1): Fraction(963, 10),
            (8, 2): Fraction(86),
            (9, 1): Fraction(104),
            (9, 2): Fraction(4110, 41),
            (10, 1): Fraction(104),
            (10, 2): Fraction(1710, 11),
            (11, 1): Fraction(9561, 61),
            (11, 2): Fraction(158),
            (12, 1): Fraction(4149, 13),
            (12, 2): Fraction(158),
        }
        for key, target in expected.items():
            case = CHECK.polar_case(*key)
            actual = Fraction(
                case["mixing_bound"]["numerator"],
                case["mixing_bound"]["denominator"],
            )
            self.assertEqual(actual, target)

    def test_every_rank_at_most_eleven_class_is_excluded(self) -> None:
        for dimension in range(7, 12):
            for determinant_class in (1, 2):
                self.assertTrue(CHECK.polar_case(dimension, determinant_class)["excluded"])
        for dimension in range(1, 7):
            for determinant_class in (1, 2):
                self.assertLess(
                    CHECK.norm_two_projective_count(dimension, determinant_class),
                    CHECK.SELECTED_POINTS,
                )

    def test_rank_twelve_class_boundary(self) -> None:
        square = CHECK.polar_case(12, 1)
        nonsquare = CHECK.polar_case(12, 2)
        self.assertFalse(square["excluded"])
        self.assertTrue(nonsquare["excluded"])
        self.assertGreater(Fraction(4149, 13), 162)
        self.assertLess(Fraction(158), 162)

    def test_ranks_thirteen_through_forty_four_survive_this_test(self) -> None:
        minimum = None
        for dimension in range(13, 45):
            for determinant_class in (1, 2):
                case = CHECK.polar_case(dimension, determinant_class)
                bound = Fraction(
                    case["mixing_bound"]["numerator"],
                    case["mixing_bound"]["denominator"],
                )
                self.assertGreaterEqual(bound, 162)
                if minimum is None or bound < minimum[0]:
                    minimum = (bound, dimension, determinant_class)
        self.assertEqual(minimum, (Fraction(116646, 365), 13, 2))

    def test_endpoint_distinctness_norms(self) -> None:
        result = CHECK.endpoint_distinctness_check()
        self.assertTrue(result["distinct_projective_points"])
        self.assertEqual(result["false_integer_combination_norm_squared"], 450)
        self.assertEqual(result["orthogonal_row_combination_norm_squared"], 882)

    def test_final_status_wall(self) -> None:
        result = CHECK.build_result()
        self.assertEqual(result["conclusion"]["rank_F3_M_lower_bound"], 12)
        self.assertEqual(
            result["conclusion"]["rank_twelve_surviving_determinant_classes"],
            ["square"],
        )
        self.assertFalse(result["conclusion"]["endpoint_excluded"])
        self.assertFalse(result["conclusion"]["upper_bound_improved_below_4158"])
        self.assertEqual(result["conclusion"]["conway_99"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
