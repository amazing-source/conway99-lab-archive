from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave191_exact_three_residual_independent", HERE / "independent_check.py"
)
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class Wave191ExactThreeResidualIndependentTests(unittest.TestCase):
    def test_local_exact_three_exclusion(self) -> None:
        result = CHECK.local_exact_three_exclusion()
        self.assertEqual(result["owner_triangle_membership"], "T in A_y")
        self.assertEqual(result["only_contained_target_member"], "c5")
        self.assertEqual(result["projective_nonzero_kernel_size"], 2)
        self.assertFalse(result["exact_three_type3_raw_extraction_possible"])
        self.assertEqual(result["local_branch_verdict"], "REFUTED")

    def test_orbit_closed_new_pool_capacity(self) -> None:
        result = CHECK.orbit_closed_new_pool_capacity()
        self.assertEqual(result["assignment_capacity_row"], [2, 3])
        self.assertEqual(result["twice_closed_circuit_count_row"], [2, 4])
        self.assertEqual(result["nonnegative_gap"], [0, 1])

    def test_joint_exact_one_capacity(self) -> None:
        result = CHECK.joint_exact_one_capacity()
        self.assertEqual(result["split"], "r1=t+u")
        self.assertEqual(result["first_joint_row"], "p3+u<=delta+2Y")
        self.assertEqual(result["type2_row"], "2p2<=u+3h")
        self.assertFalse(result["exact_one_slot_double_charging"])

    def test_coefficient_identity(self) -> None:
        result = CHECK.coefficient_certificate()
        self.assertEqual(result["twelve_Q_row"], [18, 12, 24, 16, 12])
        self.assertEqual(result["nine_private_I_row"], [18, 18, 27, 9, 9])
        self.assertEqual(result["nonnegative_remainder_row"], [0, -6, -3, 7, 3])
        self.assertEqual(result["nonedge_projective_circuit_lower"], 6237)

    def test_math_result_scope(self) -> None:
        result = CHECK.build_math_result()
        self.assertEqual(result["verdict"], "VERIFIED_WITH_SCOPE")
        self.assertEqual(result["bounds"]["all_projective_short_circuits"], 6930)
        self.assertEqual(result["bounds"]["scalar_short_circuit_words"], 13860)
        self.assertFalse(result["boundary"]["endpoint_excluded"])
        self.assertEqual(result["boundary"]["conway_99"], "UNKNOWN")

    def test_frozen_integrity_and_final_result(self) -> None:
        result = CHECK.build_results()
        self.assertTrue(result["integrity"]["passed"])
        self.assertEqual(result["integrity"]["direct_files_checked"], 7)
        self.assertEqual(result["integrity"]["source_entries_checked"], 9)
        self.assertEqual(
            set(result["integrity"]["premise_entries_checked"]),
            {"wave180", "wave181", "wave186", "wave189", "wave190"},
        )
        self.assertFalse(
            result["integrity"][
                "discovery_checker_imported_or_executed_before_independent_freeze"
            ]
        )
        self.assertTrue(
            result["source_comparison"]["coefficient_identity_matches"]
        )
        self.assertFalse(
            result["source_comparison"]["non_theorem_findings"][
                "affects_Q6237_theorem"
            ]
        )
        self.assertEqual(result["verdict"], "VERIFIED_WITH_SCOPE")

    def test_wave192_lever_is_not_used(self) -> None:
        result = CHECK.wave192_exact_two_residual_lever()
        self.assertEqual(
            result["conclusion"],
            "such a residual has exact multiplicity one or three",
        )
        self.assertFalse(result["used_in_Q6237_certificate"])
        self.assertEqual(result["status"], "VERIFIED_LEVER_NOT_APPLIED")


if __name__ == "__main__":
    unittest.main()
