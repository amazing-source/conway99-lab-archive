"""Hostile tests for the independent Wave142 verification."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import independent_verify as verify  # noqa: E402


class IndependentWave142Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = verify.build_results()

    def test_sealed_package_and_inputs(self) -> None:
        package = self.result["sealed_package"]
        self.assertEqual(package["manifest_sha256"], verify.SEALED_MANIFEST)
        self.assertEqual(package["entry_count"], 9)
        self.assertTrue(package["manifest_pass"])
        self.assertTrue(package["entries_pass"])
        self.assertTrue(self.result["frozen_inputs"]["pass"])

    def test_four_six_set_interlace_rows(self) -> None:
        row = self.result["local_interlace"]["rows"]["6"]
        self.assertEqual(
            row,
            {
                "0": {"constant": "45845415", "n3_coefficient": "4/3"},
                "2": {"constant": "470213205", "n3_coefficient": "-3"},
                "4": {"constant": "503184528", "n3_coefficient": "4/3"},
                "6": {"constant": "101286108", "n3_coefficient": "1/3"},
            },
        )
        self.assertTrue(
            self.result["local_interlace"]["alternating_parity_pass"]
        )

    def test_kernel_moment_and_ordinary_bound(self) -> None:
        local = self.result["local_interlace"]
        self.assertEqual(
            local["six_set_kernel_moment"],
            {"constant": "16459961595", "n3_coefficient": "32"},
        )
        self.assertEqual(
            local["strongest_nonnegative_upper"],
            {"source_nullity": 2, "upper": "156737735"},
        )

    def test_full_diagonal_toggle_census(self) -> None:
        toggles = self.result["diagonal_toggle_census"]
        self.assertEqual(
            toggles["strongest_nonnegative_upper"],
            {"cell": [3, 5], "upper": "7609140"},
        )
        self.assertTrue(toggles["all_cells_positive_at_4158"])
        self.assertTrue(toggles["denominators_divide_3"])
        self.assertTrue(
            self.result["comparison_with_discovery"][
                "diagonal_toggle_rows_match"
            ]
        )

    def test_all_k3_ias_transversals(self) -> None:
        control = self.result["IAS_control"]
        self.assertEqual(control["all_phi_chi_psi_transversals_checked"], 27)
        self.assertTrue(control["formula_pass"])

    def test_k3_plus_isolate_overlap_split(self) -> None:
        control = self.result["intersection_refinement"]["K3_plus_K1"]
        self.assertTrue(control["symmetric_idempotent_even_row"])
        self.assertEqual(
            control["same_B_cell"],
            {"cell": [2, 2], "h0": 3, "h2": 3, "total": 6},
        )
        self.assertTrue(all(control["kernel_moment_identity_checks"]))

    def test_general_same_B_collision_is_scoped(self) -> None:
        control = self.result["intersection_refinement"][
            "general_same_B_different_interlace_control"
        ]
        self.assertTrue(control["same_complete_B_table"])
        self.assertTrue(control["different_interlace_table"])
        self.assertEqual(control["first_different_input_size"], 3)
        self.assertEqual(control["left_size3_nullities"], [0, 18, 0, 2, 0, 0, 0])
        self.assertEqual(control["right_size3_nullities"], [0, 20, 0, 0, 0, 0, 0])
        self.assertEqual(
            self.result["status_wall"]["B_only_target_elimination"],
            "UNKNOWN",
        )

    def test_unsupported_minimum_14_is_vetoed(self) -> None:
        band = self.result["top_complement_band"]
        self.assertEqual(band["frozen_verified_image_minimum_lower"], 8)
        self.assertEqual(band["formal_rational_witness_minimum"], 14)
        self.assertFalse(band["formal_rational_witness_realized_code"])
        self.assertEqual(band["verified_target_range"], "92<=|S|<=99")
        self.assertEqual(band["vetoed_complement_sizes"], [8, 9, 10, 11, 12, 13])
        self.assertEqual(
            self.result["status_wall"]["top_band_86_through_91"],
            "VETO_UNSUPPORTED_PREMISE",
        )

    def test_corrected_top_band_has_eight_rows(self) -> None:
        entries = self.result["top_complement_band"]["verified_entries"]
        self.assertEqual(len(entries), 8)
        self.assertEqual(entries[0]["subset_size"], 99)
        self.assertEqual(entries[-1]["subset_size"], 92)
        self.assertTrue(all(entry["rank"] == 54 for entry in entries))

    def test_no_bound_or_target_resolution(self) -> None:
        self.assertFalse(self.result["bound_assessment"]["improved"])
        self.assertEqual(
            self.result["status_wall"]["formal_interlace_lift_feasibility"],
            "UNKNOWN",
        )
        self.assertEqual(self.result["status_wall"]["Conway_99"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
