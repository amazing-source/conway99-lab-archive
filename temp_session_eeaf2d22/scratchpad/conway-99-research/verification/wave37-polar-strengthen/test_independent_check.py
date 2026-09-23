#!/usr/bin/env python3
"""Tests for the independent Wave 37 polar-strengthening audit."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


SPEC = importlib.util.spec_from_file_location(
    "wave37_polar_independent_check",
    Path(__file__).resolve().with_name("independent_check.py"),
)
assert SPEC is not None and SPEC.loader is not None
check = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(check)


class PolarStrengthenIndependentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = check.build_results()

    def test_ternary_code_consequences(self) -> None:
        package = self.result["ternary_code"]
        self.assertTrue(package["code"]["self_orthogonal"])
        self.assertTrue(package["code"]["projective"])
        self.assertEqual(package["code"]["dual_distance_lower_bound"], 3)
        self.assertEqual(
            package["distinguished_words"]["composition_n1_n2"], [36, 33]
        )
        self.assertEqual(
            package["distinguished_words"]["distinct_words_including_negatives"],
            462,
        )
        self.assertEqual(package["schur_square"]["rank_I_plus_B_ceiling"], 78)

    def test_refuted_collinearity_has_explicit_counterexample(self) -> None:
        hostile = self.result["signed_triangle_geometry"][
            "refuted_collinearity_inference"
        ]
        self.assertEqual(hostile["vector_rank"], 3)
        self.assertEqual(hostile["gram_rank"], 1)

    def test_signed_degenerate_space_floor(self) -> None:
        signed = self.result["signed_triangle_geometry"]
        self.assertEqual(signed["balanced_minus_unbalanced"], 34_034)
        self.assertEqual(signed["maximum_collinear_selected_triples"], 2_618)
        self.assertEqual(signed["minimum_independent_balanced_triples"], 31_416)
        self.assertEqual(signed["minimum_distinct_rank_one_three_spaces"], 437)

    def test_both_f7_rank_eleven_classes_survive(self) -> None:
        cases = self.result["characteristic_seven"]["rank_eleven_cases"]
        self.assertEqual(
            [case["vertex_count"] for case in cases],
            [141_229_221, 141_246_028],
        )
        self.assertTrue(all(not case["is_strongly_regular"] for case in cases))
        self.assertTrue(all(case["largest_nonprincipal_eigenvalue_at_least_4802"]
                            for case in cases))
        self.assertTrue(all(not case["excluded"] for case in cases))

    def test_survivor_controls_are_not_objects(self) -> None:
        relaxation = self.result["macwilliams_real_relaxation"]
        self.assertFalse(relaxation["formal_weight_enumerator"])
        self.assertFalse(relaxation["code_constructed"])
        self.assertFalse(self.result["ternary_oriented_scheme"]["excluded"])
        self.assertFalse(self.result["divisibility_refined_evans"]["excluded"])

    def test_status_remains_unknown(self) -> None:
        conclusion = self.result["conclusion"]
        self.assertFalse(conclusion["new_rank_lower_bound"])
        self.assertFalse(conclusion["new_determinant_class_exclusion"])
        self.assertFalse(conclusion["endpoint_excluded"])
        self.assertFalse(conclusion["upper_bound_improved_below_4158"])
        self.assertEqual(conclusion["target_status"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
