from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("independent_check.py")
SPEC = importlib.util.spec_from_file_location("wave52_independent_check", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
subject = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(subject)


class IndependentWave52Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = subject.build_result()

    def test_frozen_inputs(self) -> None:
        self.assertEqual(len(self.result["input_freeze"]), 12)

    def test_rooted_arithmetic_and_global_valencies(self) -> None:
        derived = self.result["independent_derivation"]
        self.assertEqual(derived["rooted_petal_partition"], [6, 6, 6])
        self.assertEqual(derived["rooted_K_graph"], "3K6")
        self.assertEqual(
            derived["global_relation_valencies_I_K_D_C_B"], [1, 18, 32, 144, 36]
        )
        self.assertEqual(
            derived["per_petal_per_opposite_sector"], {"B": 2, "C": 4, "D": 0}
        )

    def test_partial_closure(self) -> None:
        closure = self.result["partial_19_triangle_closure"]
        self.assertEqual(closure["trajectory"], [6])
        self.assertEqual(closure["diagonal_class_sizes"], [1, 18])

    def test_constraint_template_closure(self) -> None:
        closure = self.result["completion_free_constraint_template"]
        self.assertEqual(closure["order"], 163)
        self.assertEqual(closure["trajectory"], [26, 38, 47])
        self.assertEqual(closure["diagonal_class_sizes"], [1, 18, 36, 108])
        self.assertEqual(closure["nonzero_intersection_parameters"], 1036)

    def test_all_canonical_profiles(self) -> None:
        diagnostic = self.result["canonical_completion_diagnostic"]
        self.assertEqual(diagnostic["profile_count"], 64)
        self.assertEqual(diagnostic["distinct_fingerprint_count"], 39)
        self.assertEqual(diagnostic["stable_color_count_range"], [8, 361])
        self.assertEqual(diagnostic["all_6_stable_color_count"], 13)
        self.assertEqual(diagnostic["all_222_stable_color_count"], 8)
        self.assertTrue(diagnostic["positive_integral_cap_completions"])

    def test_hostile_mutations(self) -> None:
        self.assertEqual(len(self.result["hostile_mutations_detected"]), 5)
        self.assertTrue(all(self.result["hostile_mutations_detected"].values()))

    def test_full_discovery_comparison(self) -> None:
        comparison = self.result["comparison"]
        self.assertTrue(all(comparison.values()))

    def test_status_wall(self) -> None:
        disposition = self.result["disposition"]
        self.assertEqual(self.result["claim_label"], "VERIFIED")
        self.assertEqual(disposition["prism_free_endpoint"], "UNKNOWN")
        self.assertEqual(disposition["conway_99"], "UNKNOWN")
        self.assertFalse(disposition["global_graph_constructed"])
        self.assertFalse(disposition["improved_n3_upper_bound"])


if __name__ == "__main__":
    unittest.main()
