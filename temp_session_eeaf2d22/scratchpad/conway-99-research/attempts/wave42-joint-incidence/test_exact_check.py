from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("wave42_joint_check", HERE / "exact_check.py")
CHECK = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(CHECK)


class Wave42JointIncidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = CHECK.build_results()
        cls.source = CHECK.read_source(CHECK.SOURCE)
        cls.witness = cls.source["rank_identity"]["minimum_witness"]
        cls.adjacency = CHECK.adjacency_from_edges(cls.witness["core_edges"])
        cls.gram = CHECK.forced_gram(cls.adjacency)
        cls.pairs = tuple(CHECK.allowed_pairs(fibre, cls.gram) for fibre in range(3))

    def test_frozen_core_and_components(self) -> None:
        core = self.result["canonical_core"]
        self.assertEqual(core["component_sizes"], [12, 24])
        self.assertEqual(core["component_fibre_balances"], [[4, 4, 4], [8, 8, 8]])
        self.assertEqual(core["four_cycle_count"], 10)

    def test_complete_pair_reduction(self) -> None:
        reduction = self.result["exhaustive_B_reduction"]
        self.assertEqual(reduction["nonmatching_pairs_per_fibre"], [60, 60, 60])
        self.assertEqual(
            reduction["pair_small_component_count_distribution_per_fibre"],
            [{0: 24, 1: 32, 2: 4}] * 3,
        )
        self.assertEqual(
            reduction["required_60_block_component_patterns"],
            {
                "(0, 0, 2)": 4,
                "(0, 1, 1)": 16,
                "(0, 2, 0)": 4,
                "(1, 0, 1)": 16,
                "(1, 1, 0)": 16,
                "(2, 0, 0)": 4,
            },
        )

    def test_candidate_census(self) -> None:
        census = self.result["exhaustive_B_reduction"]["candidate_census"]
        self.assertEqual(census["raw_pair_triples"], 216000)
        self.assertEqual(census["gram_support_legal"], 118718)
        self.assertEqual(census["after_forced_component_equality"], 49736)
        self.assertEqual(census["after_mixed_BH_nonnegativity"], 45032)

    def test_two_fibre_certificate(self) -> None:
        actual = CHECK.pair_concurrence(
            self.pairs[0], self.pairs[1], CHECK.PAIR_01_CERTIFICATE
        )
        expected = [row[12:24] for row in self.gram[:12]]
        self.assertEqual(actual, expected)
        self.assertTrue(self.result["two_fibre_positive_control"]["realizes_exact_Q01"])

    def test_mutated_certificate_is_rejected(self) -> None:
        mutated = list(CHECK.PAIR_01_CERTIFICATE)
        mutated[0], mutated[1] = mutated[1], mutated[0]
        actual = CHECK.pair_concurrence(self.pairs[0], self.pairs[1], mutated)
        expected = [row[12:24] for row in self.gram[:12]]
        self.assertNotEqual(actual, expected)

    def test_nonpermutation_certificate_is_rejected(self) -> None:
        mutated = list(CHECK.PAIR_01_CERTIFICATE)
        mutated[0] = mutated[1]
        with self.assertRaisesRegex(AssertionError, "not a permutation"):
            CHECK.pair_concurrence(self.pairs[0], self.pairs[1], mutated)

    def test_removed_core_edge_is_rejected(self) -> None:
        with self.assertRaisesRegex(AssertionError, "not cubic"):
            CHECK.adjacency_from_edges(self.witness["core_edges"][:-1])

    def test_H_counts_and_status_wall(self) -> None:
        boundary = self.result["forced_H_boundary_if_B_exists"]
        self.assertEqual(
            boundary["block_overlap_pair_counts_0_1_2"],
            {"0": 458, "1": 1004, "2": 308},
        )
        self.assertEqual(boundary["H_edges_by_block_overlap"], {"0": 96, "1": 144, "2": 0})
        self.assertEqual(boundary["H_triangles"], 32)
        self.assertEqual(boundary["H_four_cycles"], 181)
        wall = self.result["status_wall"]
        self.assertEqual(wall["canonical_full_B"], "UNKNOWN")
        self.assertFalse(wall["endpoint_excluded"])
        self.assertFalse(wall["conway_99_resolved"])

    def test_frozen_result_bytes(self) -> None:
        self.assertEqual(
            (HERE / "exact-results.json").read_bytes(),
            CHECK.canonical_bytes(self.result),
        )


if __name__ == "__main__":
    unittest.main()
