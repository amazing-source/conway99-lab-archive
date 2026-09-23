from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave190_residual_stability_independent", HERE / "independent_check.py"
)
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class Wave190ResidualStabilityIndependentTests(unittest.TestCase):
    def test_frozen_inputs(self) -> None:
        result = CHECK.verify_frozen_inputs()
        self.assertTrue(result["passed"])
        self.assertEqual(result["direct_files_checked"], 5)
        self.assertEqual(
            result["nested_entries_checked"],
            {"wave190_source": 9, "wave189_verifier": 8},
        )
        self.assertFalse(
            result["discovery_checker_imported_or_executed_by_verifier"]
        )

    def test_orbit_label_capacity(self) -> None:
        result = CHECK.orbit_label_capacity_certificate()
        self.assertEqual(result["three_label_state_rows_checked"], 27)
        self.assertEqual(result["maximum_combined_raw_residual_uses_per_orbit"], 3)
        self.assertTrue(result["raw_and_residual_mutually_exclusive_per_label"])
        self.assertTrue(result["two_type2_raw_extractions_cannot_be_orbit_mates"])

    def test_residual_slack_identity(self) -> None:
        result = CHECK.residual_slack_certificate()
        self.assertEqual(
            result["equivalent_master_inequality"], "delta+3h+3Y>=p3"
        )
        rows = list(result["nonnegative_slacks"].values())
        self.assertEqual(CHECK.add_rows(*map(tuple, rows)), tuple(result["sum_row"]))
        self.assertTrue(
            result["selected_and_selected_companion_collisions_excluded_by_privacy"]
        )

    def test_final_coefficient_identity(self) -> None:
        result = CHECK.coefficient_certificate()
        self.assertEqual(result["six_Q_row"], [9, 6, 12, 6, 4])
        self.assertEqual(result["nonnegative_remainder_row"], [1, -2, 0, 2, 0])
        self.assertEqual(
            result["final_inequality"],
            "6Q>=4I+n1+2*(p2-n2)>=8C",
        )
        self.assertEqual(result["nonedge_projective_circuit_lower"], 5544)

    def test_sharp_control_is_only_arithmetic(self) -> None:
        result = CHECK.sharp_control_certificate()
        self.assertEqual(result["Q"], 5544)
        self.assertEqual(result["h"], 1386)
        self.assertEqual(result["aH"], 4158)
        self.assertTrue(result["all_displayed_scalar_rows_saturated"])
        self.assertFalse(result["asserted_to_be_cover_or_graph"])

    def test_scoped_verdict(self) -> None:
        result = CHECK.build_results()
        self.assertEqual(result["verdict"], "VERIFIED_WITH_SCOPE")
        self.assertEqual(result["bounds"]["all_projective_short_circuits"], 6237)
        self.assertEqual(result["bounds"]["scalar_short_circuit_words"], 12474)
        self.assertTrue(result["boundary"]["conditional_theorem_verified"])
        self.assertFalse(result["boundary"]["endpoint_excluded"])
        self.assertEqual(result["boundary"]["conway_99"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
