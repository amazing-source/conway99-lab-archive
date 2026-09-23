#!/usr/bin/env python3
"""Focused independent assertions over the emitted exact-check artifact."""

from __future__ import annotations

import argparse
import json
import unittest
from pathlib import Path


class ExactChecksTest(unittest.TestCase):
    data = None

    def test_profile_counts_and_boundary(self):
        p = self.data["profile_reduction"]
        self.assertEqual(p["identity"], "sum_T q(T)=2*n3/3=36")
        self.assertEqual(p["raw_profile_count"], 23)
        self.assertEqual(p["dK_ge_4_survivor_count"], 6)
        survivors = {(x["r"], x["q"]) for x in p["survivors"]}
        self.assertEqual(
            survivors,
            {
                (14, "2^6 3^8"),
                (15, "2^9 3^6"),
                (16, "2^12 3^4"),
                (17, "2^16 4^1"),
                (17, "2^15 3^2"),
                (18, "2^18"),
            },
        )

    def test_size_two_endpoint_arithmetic(self):
        rows = {
            tuple(x["q_pair"]): x
            for x in self.data["profile_reduction"]["size_two_endpoint_table"]
        }
        self.assertEqual(rows[(2, 2)]["positive_support_neighbors"], 2)
        self.assertFalse(rows[(2, 3)]["possible_size_two_point"])
        self.assertEqual(rows[(2, 4)]["positive_support_neighbors"], 3)
        self.assertEqual(rows[(3, 3)]["positive_support_neighbors"], 3)
        self.assertFalse(rows[(3, 4)]["possible_size_two_point"])
        self.assertEqual(rows[(4, 4)]["positive_support_neighbors"], 4)

    def test_equality_boundary(self):
        e = self.data["equality_boundary"]
        self.assertEqual(e["active_incidence_sum"], 54)
        self.assertEqual(e["no_singleton_active_vertex_cap"], 27)
        self.assertEqual(e["forced_internal_edges"], 81)
        self.assertEqual(e["forced_internal_regular_degree"], 6)
        self.assertEqual(e["forced_outside_X_degree"], 3)
        self.assertEqual(e["quotient_matrix"], [[6, 8], [3, 11]])

    def test_mod2_cycle_restriction(self):
        rows = {
            x["F_component_count"]: x
            for x in self.data["mod2_active_support_constraint"][
                "cycle_partition_counts"
            ]
        }
        self.assertEqual(rows[1]["required_R_radical_nullity"], 7)
        self.assertEqual(rows[1]["minimum_R_cycle_count_among_allowed"], 4)
        self.assertEqual(rows[2]["minimum_R_cycle_count_among_allowed"], 3)
        self.assertEqual(rows[3]["minimum_R_cycle_count_among_allowed"], 2)
        self.assertTrue(all(x["hamiltonian_R_rejected"] for x in rows.values()))

    def test_hamming_relaxation_scope(self):
        h = self.data["hamming_relaxation"]["checks"]
        self.assertEqual(h["quotient_matrix"], [[6, 8], [3, 11]])
        self.assertEqual(h["XX_block_identity_max_abs_defect"], 0)
        self.assertGreater(h["cross_block_identity_max_abs_defect"], 0)
        self.assertGreater(h["YY_block_identity_max_abs_defect"], 0)
        self.assertEqual(h["duplicate_outside_neighborhood_pairs"], 36)
        self.assertEqual(h["max_distinct_outside_column_intersection"], 3)
        self.assertNotEqual(
            set(map(int, h["support_coverage_HRHt_histogram"])), {0, 2}
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", type=Path)
    args, remaining = parser.parse_known_args()
    ExactChecksTest.data = json.loads(args.artifact.read_text(encoding="utf-8"))
    unittest.main(argv=[__file__] + remaining)


if __name__ == "__main__":
    main()
