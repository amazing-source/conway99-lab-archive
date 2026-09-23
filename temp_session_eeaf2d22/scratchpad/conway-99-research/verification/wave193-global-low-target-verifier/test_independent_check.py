from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave193_global_low_target_independent", HERE / "independent_check.py"
)
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class Wave193GlobalLowTargetIndependentTests(unittest.TestCase):
    def test_raw_split(self) -> None:
        result = CHECK.raw_split_certificate()
        self.assertEqual(result["type1"], "a1+a2+a3=n1")
        self.assertEqual(result["type2"], "b1+b3=2p2")
        self.assertEqual(result["type3"], "c1+c2=p3")
        self.assertIn("b2", result["excluded_splits"])
        self.assertIn("c3", result["excluded_splits"])

    def test_type1_exact2_residual(self) -> None:
        result = CHECK.type1_exact2_residual_certificate()
        self.assertEqual(result["axis_profiles"], [[6, 2], [6, 2]])
        self.assertTrue(result["axis_supports_incomparable"])
        self.assertEqual(result["a2_and_c2_residual_multiplicities"], [1, 3])

    def test_residual_capacity(self) -> None:
        result = CHECK.residual_capacity_certificate()
        self.assertEqual(
            result["old_exact3_unused_label_capacity"], "3h-(a3+b3)"
        )
        self.assertEqual(
            result["slack"], "SR=3h+3Y/2-(a2+a3+b3+c2)>=0"
        )
        self.assertFalse(result["raw_residual_same_label_in_orbit"])

    def test_low_target(self) -> None:
        result = CHECK.low_target_certificate()
        self.assertTrue(result["one_leaf_target_per_label"])
        self.assertEqual(result["lower_bound"], "U>=C-(n1+2n2)")
        self.assertEqual(
            result["slack"],
            "SL=2n1+4n2+r1+2r2+Y+2W-C>=0",
        )
        self.assertEqual(result["capacity_inventory"]["new_residual_pool"], "Y")

    def test_coefficient_identity(self) -> None:
        result = CHECK.coefficient_certificate()
        self.assertEqual(result["lower"], "117Q>=177C")
        self.assertEqual(result["nonedge_projective_Q"], 6291)

    def test_integer_null(self) -> None:
        result = CHECK.integer_null_control()
        self.assertEqual(result["Q0"], 6291)
        self.assertEqual(result["private_incidence_slack"], 0)
        self.assertEqual(result["twice_SR"], 0)
        self.assertFalse(result["asserted_to_be_graph_code_cover_or_circuit_family"])

    def test_scoped_result(self) -> None:
        result = CHECK.build_math_result()
        self.assertEqual(result["verdict"], "VERIFIED_WITH_SCOPE")
        self.assertEqual(result["bounds"]["all_projective_short_circuits"], 6984)
        self.assertEqual(result["bounds"]["scalar_short_circuit_words"], 13968)
        self.assertFalse(result["boundary"]["endpoint_excluded"])

    def test_frozen_integrity(self) -> None:
        result = CHECK.build_results()
        self.assertTrue(result["integrity"]["passed"])
        self.assertEqual(result["integrity"]["direct_files_checked"], 6)
        self.assertEqual(result["integrity"]["source_entries_checked"], 9)
        self.assertEqual(
            set(result["integrity"]["premise_entries_checked"]),
            {"wave181", "wave188", "wave189", "wave191"},
        )
        self.assertFalse(
            result["integrity"][
                "discovery_checker_imported_or_executed_before_independent_freeze"
            ]
        )
        self.assertTrue(result["source_comparison"]["dual_identity_matches"])
        self.assertTrue(
            result["source_comparison"]["source_integer_null"]["row_passes"]
        )
        self.assertEqual(result["verdict"], "VERIFIED_WITH_SCOPE")


if __name__ == "__main__":
    unittest.main()
