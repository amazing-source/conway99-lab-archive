#!/usr/bin/env python3
"""Hostile and reconstruction tests for the Wave 41 equality package."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("wave41_evenpart_check", HERE / "exact_check.py")
assert SPEC and SPEC.loader
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


EXPECTED = {
    "1+1+1+1+2": (80_640, 2, 80_038, 20_790),
    "1+1+2+2": (192, 8, 184, 83_160),
    "1+1+4": (768, 2, 736, 20_790),
    "1+2+3": (80_640, 2, 80_632, 20_790),
    "2+2+2": (32, 32, 32, 332_640),
    "2+4": (64, 4, 64, 41_580),
    "6": (2_592, 2, 2_592, 20_790),
}


class EvenPartEqualityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = CHECK.exact_record()

    def test_frozen_inputs(self) -> None:
        self.assertEqual(
            {path: CHECK.sha256_file(Path(path)) for path in CHECK.INPUTS},
            CHECK.INPUTS,
        )

    def test_labelled_matching_census(self) -> None:
        self.assertEqual(len(CHECK.all_matchings()), 10_395)
        self.assertEqual(len(set(CHECK.all_matchings())), 10_395)
        self.assertEqual(
            set(CHECK.matching_representatives()),
            set(CHECK.integer_partitions(6)),
        )

    def test_even_partition_scope_is_complete(self) -> None:
        self.assertEqual(
            set(EXPECTED),
            {"+".join(map(str, partition)) for partition in CHECK.EVEN_PARTITIONS},
        )

    def test_radical_dimension_formula(self) -> None:
        p_matrix = CHECK.permutation_matrix(CHECK.STANDARD_MATCHING)
        for partition in CHECK.EVEN_PARTITIONS:
            q_matrix = CHECK.permutation_matrix(
                CHECK.matching_representatives()[partition]
            )
            radical = CHECK.kernel_basis(CHECK.matrix_add(p_matrix, q_matrix))
            self.assertEqual(
                len(radical),
                2 * sum(part % 2 == 0 for part in partition),
            )

    def test_atomic_counts_and_no_survivor(self) -> None:
        for key, expected in EXPECTED.items():
            record = self.result["partition_results"][key]
            observed = (
                record["minimum_permutation_cover"][
                    "distinct_minimum_permutations"
                ],
                record["distinct_right_kernels"],
                record["distinct_equality_constraints"],
                record["tested_R_projection_evaluations"],
            )
            self.assertEqual(observed, expected)
            self.assertFalse(record["rank25_exists"])
            self.assertEqual(record["realized_equality_constraint_count"], 0)
            self.assertEqual(record["minimum_F_with_some_rank25_R"], 0)

    def test_every_right_kernel_gets_full_R_census(self) -> None:
        for record in self.result["partition_results"].values():
            self.assertEqual(
                record["tested_R_projection_evaluations"],
                10_395 * record["distinct_right_kernels"],
            )
            self.assertTrue(
                all(
                    kernel["realized_target_constraint_count"] == 0
                    for kernel in record["kernel_records"]
                )
            )

    def test_atomic_hashes_are_bound(self) -> None:
        for record in self.result["atomic_outputs"].values():
            self.assertEqual(CHECK.sha256_file(Path(record["path"])), record["sha256"])

    def test_elimination_rank_identity(self) -> None:
        p = CHECK.permutation_matrix(CHECK.STANDARD_MATCHING)
        q_matching = CHECK.matching_representatives()[(2, 4)]
        q = CHECK.permutation_matrix(q_matching)
        r = CHECK.permutation_matrix(CHECK.all_matchings()[137])
        column_to_y = (8, 10, 9, 11, 4, 6, 5, 7, 0, 2, 1, 3)
        yz = CHECK.inverse_permutation(column_to_y)
        f = CHECK.permutation_matrix(yz)
        three_i = [
            [3 * int(row == column) for column in range(CHECK.SIDE)]
            for row in range(CHECK.SIDE)
        ]
        d_p = CHECK.matrix_subtract(three_i, p)
        d_q = CHECK.matrix_subtract(three_i, q)
        d_r = CHECK.matrix_subtract(three_i, r)
        minus_i = [
            [(-int(row == column)) % CHECK.PRIME for column in range(CHECK.SIDE)]
            for row in range(CHECK.SIDE)
        ]
        minus_f = [
            [(-entry) % CHECK.PRIME for entry in row] for row in f
        ]
        full = [
            d_p[row] + minus_i[row] + minus_i[row]
            for row in range(CHECK.SIDE)
        ] + [
            minus_i[row] + d_q[row] + minus_f[row]
            for row in range(CHECK.SIDE)
        ] + [
            minus_i[row] + CHECK.transpose(minus_f)[row] + d_r[row]
            for row in range(CHECK.SIDE)
        ]
        h_rank, k39_rank = CHECK.full_k39_rank(
            q_matching, CHECK.all_matchings()[137], column_to_y
        )
        self.assertEqual(CHECK.rank_mod_prime(full), 12 + h_rank)
        self.assertEqual(k39_rank, 1 + CHECK.rank_mod_prime(full))

    def test_type6_boundary_constraint_has_no_R(self) -> None:
        partition = (6,)
        p = CHECK.permutation_matrix(CHECK.STANDARD_MATCHING)
        q = CHECK.permutation_matrix(CHECK.matching_representatives()[partition])
        a = CHECK.matrix_add(p, q)
        radical = CHECK.kernel_basis(a)
        column_to_y = (8, 10, 9, 11, 4, 6, 5, 7, 0, 2, 1, 3)
        f = CHECK.permutation_matrix(CHECK.inverse_permutation(column_to_y))
        t = CHECK.matrix_add(
            [[3 * entry % CHECK.PRIME for entry in row] for row in CHECK.identity(12)],
            p,
        )
        right_kernel, target, _ = CHECK.equality_constraint(
            a, CHECK.matrix_add(f, t), p, radical, 1
        )
        self.assertNotIn(
            target,
            {
                CHECK.projection_signature(right_kernel, matching)
                for matching in CHECK.all_matchings()
            },
        )

    def test_hostile_nonmatching_and_nonminimum_inputs_fail(self) -> None:
        with self.assertRaises(AssertionError):
            CHECK.matching_map(((0, 1), (0, 2)))
        partition = (6,)
        p = CHECK.permutation_matrix(CHECK.STANDARD_MATCHING)
        q = CHECK.permutation_matrix(CHECK.matching_representatives()[partition])
        a = CHECK.matrix_add(p, q)
        radical = CHECK.kernel_basis(a)
        t = CHECK.matrix_add(
            [[3 * entry % CHECK.PRIME for entry in row] for row in CHECK.identity(12)],
            p,
        )
        with self.assertRaisesRegex(AssertionError, "minimum projection"):
            CHECK.equality_constraint(a, t, p, radical, 1)

    def test_exact_result_bytes(self) -> None:
        self.assertEqual(
            (HERE / "exact-results.json").read_bytes(),
            CHECK.canonical_json(self.result),
        )

    def test_summary_stays_candidate(self) -> None:
        self.assertTrue(self.result["summary"]["universal_rank26_candidate"])
        self.assertEqual(self.result["claim_label"], "CANDIDATE")
        self.assertEqual(self.result["summary"]["global_graph_status"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
