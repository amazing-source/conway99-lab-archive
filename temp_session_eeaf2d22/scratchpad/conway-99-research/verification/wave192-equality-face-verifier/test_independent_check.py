from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave192_equality_face_independent", HERE / "independent_check.py"
)
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class Wave192EqualityFaceIndependentTests(unittest.TestCase):
    def test_equality_face(self) -> None:
        result = CHECK.equality_face_certificate()
        self.assertEqual(result["parameter"], "m=n3=p3")
        self.assertEqual(result["range"], [0, 2079])
        self.assertEqual(result["formulas"]["r"], "2079")
        self.assertTrue(result["all_type3_raws_exact1"])

    def test_tau_pair_saturation(self) -> None:
        result = CHECK.tau_pair_saturation_certificate()
        self.assertEqual(result["total_tau_pairs"], 2079)
        self.assertEqual(result["assignments_per_exact2_raw"], 2)
        self.assertTrue(result["complement_tau_invariant"])

    def test_affine_axis(self) -> None:
        result = CHECK.affine_axis_certificate()
        self.assertEqual(result["axis_weights"], [8, 8])
        self.assertEqual(result["axis_profiles"], [[6, 2], [6, 2]])
        self.assertTrue(result["axis_supports_incomparable"])
        self.assertEqual(result["m0_branch_verdict"], "REFUTED")

    def test_nonprivate_leaf(self) -> None:
        result = CHECK.nonprivate_leaf_certificate()
        self.assertEqual(result["leaf_word_profile"], [3, 6])
        self.assertEqual(result["leaf_word_weight"], 9)
        self.assertEqual(result["positive_m_branch_verdict"], "REFUTED")

    def test_strict_residual_capacity(self) -> None:
        result = CHECK.strict_residual_capacity_certificate()
        self.assertFalse(result["exact2_residual_possible"])
        self.assertEqual(result["strict_capacity"], "2Z<=3Y")
        self.assertEqual(result["twice_Z_capacity_row"], [2, 6])
        self.assertEqual(result["three_Y_row"], [3, 6])
        self.assertEqual(
            result["equality_consequence"],
            "Y=Z=0 and every type3 raw is exact1",
        )

    def test_scoped_result(self) -> None:
        result = CHECK.build_math_result()
        self.assertEqual(result["verdict"], "VERIFIED_WITH_SCOPE")
        self.assertEqual(result["strict_bound"]["nonedge_projective_short_circuits_Q"], 6238)
        self.assertEqual(result["boundary"]["Q6237_equality_face"], "REFUTED")
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
        self.assertTrue(result["source_comparison"]["strict_Q_bound_matches"])
        self.assertEqual(result["verdict"], "VERIFIED_WITH_SCOPE")


if __name__ == "__main__":
    unittest.main()
