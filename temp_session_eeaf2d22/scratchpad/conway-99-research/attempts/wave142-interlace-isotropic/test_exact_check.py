"""Regression tests for the bounded Wave142 exact checker."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave142_exact_check",
    HERE / "exact_check.py",
)
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CHECK
SPEC.loader.exec_module(CHECK)


class Wave142Tests(unittest.TestCase):
    def test_six_vertex_interlace_row(self) -> None:
        result = CHECK.local_interlace_rows()
        row = result["rows"]["6"]
        self.assertEqual(row["0"], {
            "constant": "45845415", "n3_coefficient": "4/3"
        })
        self.assertEqual(row["2"], {
            "constant": "470213205", "n3_coefficient": "-3"
        })
        self.assertEqual(
            result["six_set_kernel_size_moment"],
            {
                "definition": "sum_|S|=6 2^nullity(A[S])",
                "constant": "16459961595",
                "n3_coefficient": "32",
            },
        )

    def test_isotropic_toggle_bound_is_weak(self) -> None:
        result = CHECK.isotropic_toggle_rows()
        bound = result["strongest_nonnegativity_bound"]
        self.assertEqual(bound["cell_psi_count_nullity"], [3, 5])
        self.assertEqual(bound["rational_upper"], "7609140")
        self.assertFalse(bound["improves_n3_le_4158"])

    def test_small_isotropic_transversal_control(self) -> None:
        result = CHECK.small_isotropic_control()
        self.assertTrue(result["all_pass"])
        self.assertEqual(result["transversals_checked"], 8)

    def test_wave141_projection_loses_intersection_slice(self) -> None:
        result = CHECK.intersection_zero_control()
        cell = result["same_Wave141_cell"]
        self.assertEqual(cell["B_2_2_total"], 6)
        self.assertEqual(cell["intersection_0_count"], 3)
        self.assertEqual(cell["intersection_2_count"], 3)
        self.assertEqual(result["kernel_moment_identity_checks"], 5)

    def test_top_complement_band(self) -> None:
        result = CHECK.top_complement_band()
        self.assertEqual(len(result["entries"]), 14)
        self.assertEqual(result["entries"][0]["nullity"], 45)
        self.assertEqual(result["entries"][-1]["subset_size"], 86)
        self.assertTrue(all(row["rank"] == 54 for row in result["entries"]))

    def test_canonical_result(self) -> None:
        observed = (HERE / "exact-results.json").read_text(encoding="utf-8")
        expected = CHECK.canonical_json(CHECK.build_results())
        self.assertEqual(observed, expected)


if __name__ == "__main__":
    unittest.main()
