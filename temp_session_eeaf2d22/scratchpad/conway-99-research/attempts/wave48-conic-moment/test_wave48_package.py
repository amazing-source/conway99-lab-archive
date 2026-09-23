"""Contract tests for the sealed Wave48 conic-moment scout."""

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


class Wave48PackageTests(unittest.TestCase):
    def test_input_freeze(self) -> None:
        for line in (HERE / "input-freeze.sha256").read_text().splitlines():
            expected, relative = line.split("  ", 1)
            actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            self.assertEqual(actual, expected, relative)

    def test_exact_faces(self) -> None:
        data = json.loads((HERE / "exact-faces.json").read_text())
        self.assertEqual(data["wave44_exact_affine_rank"], 93)
        self.assertEqual(data["wave44_exact_affine_nullity"], 116)
        self.assertTrue(data["all_families_exactly_sealed"])
        self.assertEqual(len(data["families"]), 11)
        expected = [
            (1, 15),
            (1, 18),
            (12, 5),
            (58, 6),
            (50, 6),
            (50, 6),
            (36, 6),
            (50, 6),
            (36, 6),
            (36, 6),
            (17, 3),
        ]
        actual = [
            (
                family["exact_rational_active_rank_certified"],
                family["exact_rational_nullity_certified"],
            )
            for family in data["families"]
        ]
        self.assertEqual(actual, expected)
        self.assertTrue(
            all(
                family["all_kernel_vectors_exact_affine_identities"]
                for family in data["families"]
            )
        )
        self.assertTrue(
            all(
                len(set(family["modular_active_ranks"].values())) == 1
                for family in data["families"]
            )
        )

    def test_summary_status_wall(self) -> None:
        data = json.loads((HERE / "wave48-summary.json").read_text())
        conclusion = data["conclusion"]
        self.assertFalse(conclusion["exact_feasible_vector"])
        self.assertFalse(conclusion["exact_infeasibility_witness"])
        self.assertEqual(conclusion["numerical_status"], "UNKNOWN")
        self.assertEqual(conclusion["endpoint_n3_4158"], "UNKNOWN")
        self.assertEqual(
            data["model"]["h11_over_4_scaled_interval"],
            ["1/2", "1"],
        )
        self.assertTrue(
            all(
                not run["used_as_exact_evidence"]
                for run in data["numerical_runs"]
            )
        )

    def test_numerical_files_remain_non_evidentiary(self) -> None:
        for name in (
            "clarabel-result.json",
            "scs-result.json",
            "clarabel-exact-face-result.json",
        ):
            data = json.loads((HERE / name).read_text())
            self.assertEqual(data["conclusion"]["endpoint_n3_4158"], "UNKNOWN")
            for run in data["solvers"]:
                self.assertFalse(run["used_as_exact_evidence"])
                self.assertEqual(
                    run["claim_label"],
                    "CANDIDATE_NUMERICAL_ONLY",
                )

    def test_five_root_recommendation(self) -> None:
        recommendation = json.loads(
            (HERE / "wave48-summary.json").read_text()
        )["five_root_one_free_recommendation"]
        self.assertEqual(recommendation["canonical_root_family_count"], 21)
        self.assertEqual(recommendation["rooted_labelled_mask_count"], 683)
        self.assertEqual(len(recommendation["matrix_sizes"]), 21)
        self.assertEqual(min(recommendation["matrix_sizes"]), 10)
        self.assertEqual(max(recommendation["matrix_sizes"]), 32)
        self.assertEqual(recommendation["union_orders"], [6, 7])


if __name__ == "__main__":
    unittest.main()
