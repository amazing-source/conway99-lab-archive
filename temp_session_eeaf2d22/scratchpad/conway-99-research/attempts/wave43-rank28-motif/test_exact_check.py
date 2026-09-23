from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SPEC = importlib.util.spec_from_file_location(
    "wave43_rank28_motif", HERE / "exact_check.py"
)
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)
RESULT = json.loads((HERE / "exact-results.json").read_text(encoding="utf-8"))


class Rank28MotifTests(unittest.TestCase):
    def test_exact_result_schema_and_scope_wall(self) -> None:
        CHECK.validate(RESULT)
        conclusion = RESULT["conclusion"]
        self.assertEqual(conclusion["unresolved_endpoint_type"], "3+3")
        self.assertEqual(conclusion["universal_rank28"], "NOT_PROVED")
        self.assertEqual(
            conclusion["prism_free_rank28_universal"], "NOT_PROVED"
        )
        self.assertEqual(conclusion["Conway_99"], "UNKNOWN")

    def test_frozen_inputs(self) -> None:
        self.assertEqual(
            RESULT["inputs"][
                "verification/wave41-rank26-secondary/secondary_check.py"
            ],
            CHECK.sha256_file(CHECK.WAVE41),
        )
        self.assertEqual(
            RESULT["inputs"][
                "verification/wave42-rank27/independent-results.json"
            ],
            CHECK.sha256_file(CHECK.WAVE42_RESULT),
        )

    def test_rank_at_most_two_predicate(self) -> None:
        zero = np.zeros((4, 4), dtype=np.int16)
        rank_one = np.asarray(
            [[1, 2, 0, 1], [2, 4, 0, 2], [0, 0, 0, 0], [1, 2, 0, 1]],
            dtype=np.int16,
        )
        rank_two_diagonal = np.diag([1, 1, 0, 0]).astype(np.int16)
        rank_two_hyperbolic = np.asarray(
            [[0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
            dtype=np.int16,
        )
        rank_three = np.diag([1, 1, 1, 0]).astype(np.int16)
        # This rank-four control has every principal 3-minor zero.  It proves
        # the checker must inspect general, not only principal, 3-minors.
        rank_four_hyperbolic = np.asarray(
            [[0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]],
            dtype=np.int16,
        )
        batch = np.stack(
            (
                zero,
                rank_one,
                rank_two_diagonal,
                rank_two_hyperbolic,
                rank_three,
                rank_four_hyperbolic,
            )
        )
        self.assertEqual(
            CHECK.rank_at_most_two_mask(batch).tolist(),
            [True, True, True, True, False, False],
        )

    def test_derangement_cover_counts(self) -> None:
        covers = RESULT["low_F_derangement_covers"]
        self.assertEqual(
            covers["2+2+2"]["low_F_derangement_permutation_count"], 332
        )
        self.assertEqual(
            covers["4+2"]["low_F_derangement_permutation_count"], 1_352
        )
        self.assertEqual(
            covers["2+2+2"]["low_F_derangement_rank_histogram"], {"4": 332}
        )
        self.assertEqual(
            covers["4+2"]["low_F_derangement_rank_histogram"], {"3": 1_352}
        )
        for record in covers.values():
            self.assertTrue(
                all(
                    CHECK.is_derangement(permutation)
                    for permutation in record["low_F_derangements_first_20"]
                )
            )

    def test_explicit_zero_residual_coverage(self) -> None:
        records = RESULT["higher_F_zero_residual_explicit"]
        self.assertEqual(
            records["2+2+2"]["tested_derangement_R_pairs"], 332 * 10_395
        )
        self.assertEqual(
            records["4+2"]["tested_derangement_R_pairs"], 1_352 * 10_395
        )
        self.assertEqual(records["2+2+2"]["zero_residual_pairs"], 0)
        self.assertEqual(records["4+2"]["zero_residual_pairs"], 0)

    def test_type6_minimum_pair_coverage(self) -> None:
        record = RESULT["type6_minimum_F_rank2_residual"]
        self.assertEqual(record["minimum_F_derangements"], 288)
        self.assertEqual(
            record["tested_minimum_F_derangement_R_pairs"], 288 * 10_395
        )
        self.assertEqual(record["rank_at_most_two_residual_pairs"], 0)

    def test_type6_higher_rank_csp_boundary(self) -> None:
        record = RESULT["type6_next_F_zero_residual"]
        self.assertEqual(record["pivot_assignment_branches"], 1_014)
        self.assertEqual(record["pivot_mate_branches"], 92_274)
        self.assertEqual(record["unary_viable_branches"], 488)
        self.assertEqual(record["backtrack_nodes"], 1_058)
        self.assertEqual(record["residual_zero_pairs"], 0)

    def test_two_coefficient_solver(self) -> None:
        first = (1, 0, 2, 4)
        second = (0, 1, 3, 5)
        for left in range(7):
            for right in range(7):
                vector = tuple(
                    (left * a + right * b) % 7
                    for a, b in zip(first, second)
                )
                self.assertEqual(
                    CHECK.solve_two_coefficients(vector, first, second),
                    (left, right),
                )

    def test_result_hash(self) -> None:
        self.assertEqual(
            CHECK.sha256_file(HERE / "exact-results.json"),
            "8878b40898ba9577ef01fb51ab5631632fb0e6bca3394c594b9c399d51385230",
        )


if __name__ == "__main__":
    unittest.main()
