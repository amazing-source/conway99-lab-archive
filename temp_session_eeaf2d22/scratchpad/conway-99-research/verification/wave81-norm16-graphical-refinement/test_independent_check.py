"""Hostile tests for the independent Wave 81 graphical refinement verifier."""

from __future__ import annotations

import importlib.util
import itertools
import unittest
from pathlib import Path


MODULE = Path(__file__).with_name("independent_check.py")
SPEC = importlib.util.spec_from_file_location("wave81_graphical_refinement", MODULE)
assert SPEC and SPEC.loader
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class GraphicalRefinementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = CHECK.build_results()

    def test_frozen_conditional_domain_is_complete_and_unique(self) -> None:
        audit = self.result["domain_audit"]
        self.assertEqual(audit["rows_by_t"], {"0": 43, "1": 7})
        self.assertEqual(audit["rows_total"], 50)
        self.assertEqual(audit["unique_histogram_triples"], 50)
        self.assertEqual(len(audit["six_type_pair_subgraphs"]), 6)
        self.assertEqual(
            [row["row_id"] for row in self.result["row_certificates"][:2]],
            ["t0-row-01", "t0-row-02"],
        )
        self.assertEqual(
            [row["row_id"] for row in self.result["row_certificates"][-2:]],
            ["t1-row-06", "t1-row-07"],
        )

    def test_every_type_pair_is_checked_for_every_row(self) -> None:
        census = self.result["pair_census"]
        self.assertEqual(set(census), set(CHECK.PAIR_NAMES))
        for name, record in census.items():
            self.assertEqual(record["checked"], 50, name)
        self.assertEqual(
            {
                name: record["nongraphical"]
                for name, record in census.items()
            },
            {
                "X0_induced": 3,
                "X0_X1": 0,
                "X0_X2": 0,
                "X1_induced": 0,
                "X1_X2": 0,
                "X2_induced": 0,
            },
        )

    def test_exact_three_rejections_and_final_counts(self) -> None:
        self.assertEqual(
            self.result["counts_after_all_six_graphical_tests"],
            {"0": 40, "1": 7},
        )
        rejected = self.result["rejections"]
        self.assertEqual(len(rejected), 3)
        self.assertTrue(
            all(row["t"] == 0 and row["failed_pairs"] == ["X0_induced"] for row in rejected)
        )
        sequences = {
            tuple(row["failed_expanded_sequences"]["X0_induced"][0])
            for row in rejected
        }
        self.assertEqual(
            sequences,
            {
                (4, 3, 1, 1, 1, 0, 0, 0, 0, 0, 0),
                (4, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0),
                (3, 3, 3, 1, 0, 0, 0, 0, 0, 0, 0),
            },
        )

    def test_rejection_witnesses_are_exact_erdos_gallai_failures(self) -> None:
        witnesses = {
            tuple(row["failed_expanded_sequences"]["X0_induced"][0]): row[
                "failure_witnesses"
            ]["X0_induced"]
            for row in self.result["rejections"]
        }
        self.assertEqual(
            witnesses[(4, 3, 1, 1, 1, 0, 0, 0, 0, 0, 0)],
            {"kind": "inequality", "k": 2, "lhs": 7, "rhs": 5},
        )
        self.assertEqual(
            witnesses[(4, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0)],
            {"kind": "inequality", "k": 1, "lhs": 4, "rhs": 3},
        )
        self.assertEqual(
            witnesses[(3, 3, 3, 1, 0, 0, 0, 0, 0, 0, 0)],
            {"kind": "inequality", "k": 2, "lhs": 6, "rhs": 5},
        )

    def test_all_simple_sequences_through_n6_against_brute_force(self) -> None:
        for n in range(1, 7):
            for ascending in itertools.combinations_with_replacement(range(n), n):
                sequence = tuple(reversed(ascending))
                brute = CHECK.brute_force_simple_graphical(sequence)
                eg, _ = CHECK.erdos_gallai(sequence)
                hh = CHECK.havel_hakimi(sequence)
                self.assertEqual(eg, brute, (n, sequence, "EG"))
                self.assertEqual(hh, brute, (n, sequence, "HH"))

    def test_all_3x3_degree_pairs_against_brute_force(self) -> None:
        sequences = tuple(
            tuple(reversed(values))
            for values in itertools.combinations_with_replacement(range(4), 3)
        )
        for left in sequences:
            for right in sequences:
                brute = CHECK.brute_force_bigraphical(left, right)
                gr, _ = CHECK.gale_ryser(left, right)
                hh = CHECK.bipartite_havel_hakimi(left, right)
                self.assertEqual(gr, brute, (left, right, "GR"))
                self.assertEqual(hh, brute, (left, right, "BHH"))

    def test_bounds_parity_and_marginal_controls(self) -> None:
        self.assertEqual(CHECK.erdos_gallai([3, 1, 1])[1], {"kind": "bounds"})
        self.assertEqual(CHECK.erdos_gallai([2, 2, 1])[1], {"kind": "parity"})
        self.assertEqual(
            CHECK.gale_ryser([2, 2], [1, 1])[1],
            {"kind": "sum", "left": 4, "right": 2},
        )
        self.assertFalse(CHECK.bipartite_havel_hakimi([2, 2], [1, 1]))
        self.assertTrue(CHECK.erdos_gallai([3, 3, 2, 2, 2])[0])

    def test_status_boundary(self) -> None:
        endpoint = self.result["endpoint"]
        self.assertTrue(endpoint["refinement_verified"])
        self.assertFalse(endpoint["norm16_excluded"])
        self.assertEqual(endpoint["conway_status"], "UNKNOWN")
        self.assertEqual(endpoint["novelty"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
