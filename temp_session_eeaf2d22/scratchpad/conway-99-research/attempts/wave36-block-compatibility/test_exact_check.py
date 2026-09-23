"""Independent unit checks for the Wave 36 exact checker."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


DIRECTORY = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave36_block_compatibility_exact_check",
    DIRECTORY / "exact_check.py",
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("could not load exact_check.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ExactCheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.results = MODULE.build_results()

    def test_k12_factorization(self) -> None:
        edges = tuple(edge for factor in MODULE.FACTORS for edge in factor)
        self.assertEqual(len(edges), 66)
        self.assertEqual(len(set(edges)), 66)

    def test_restricted_core(self) -> None:
        core = self.results["restricted_core"]
        self.assertEqual(core["vertex_count"], 36)
        self.assertEqual(core["edge_count"], 54)
        self.assertEqual(core["degree_set"], [3])
        self.assertEqual(core["triangle_count"], 0)
        self.assertEqual(core["four_cycle_count"], 0)
        self.assertEqual(core["connected_component_count"], 1)

    def test_gram_kernel_and_rank(self) -> None:
        adjacency = MODULE.build_restricted_x_adjacency()
        gram = MODULE.required_xy_gram(adjacency)
        self.assertEqual(MODULE.rational_rank(gram), 34)
        self.assertEqual(set(map(sum, gram)), {60})
        for vector in (
            [1] * 12 + [-1] * 12 + [0] * 12,
            [1] * 12 + [0] * 12 + [-1] * 12,
        ):
            self.assertEqual(
                [
                    sum(row[column] * vector[column] for column in range(36))
                    for row in gram
                ],
                [0] * 36,
            )

    def test_new_cut_strictly_strengthens_old_cut(self) -> None:
        census = self.results["restricted_core"]["individual_block_census"]
        self.assertEqual(census["old_induced_matching_count"], 183980)
        self.assertEqual(census["mixed_equation_survivor_count"], 151712)
        self.assertEqual(census["removed_by_mixed_equation"], 32268)

    def test_survivor_internal_edge_histogram(self) -> None:
        census = self.results["restricted_core"]["individual_block_census"]
        self.assertEqual(
            census["survivors_by_internal_X_edges"],
            {"0": 52868, "1": 76036, "2": 22104, "3": 704},
        )
        self.assertEqual(
            sum(census["survivors_by_internal_X_edges"].values()),
            151712,
        )

    def test_every_survivor_has_nonnegative_transfer_target(self) -> None:
        adjacency = MODULE.build_restricted_x_adjacency()
        neighbors = tuple(
            tuple(
                neighbor
                for neighbor, value in enumerate(adjacency[point])
                if value
            )
            for point in range(36)
        )
        pair_sets = tuple(
            MODULE.allowed_pairs(index)
            for index in MODULE.WITHIN_FACTOR_INDICES
        )
        survivor_count = 0
        for pairs in __import__("itertools").product(*pair_sets):
            block = MODULE.block_vector(pairs)
            target = MODULE.transfer_target(adjacency, block, neighbors)
            if min(target) < 0:
                continue
            survivor_count += 1
            self.assertEqual(sum(target), 48)
            self.assertTrue(set(target) <= {0, 1, 2})
            self.assertTrue(MODULE.old_matching_cut(adjacency, block))
        self.assertEqual(survivor_count, 151712)

    def test_required_H_moments(self) -> None:
        core = self.results["restricted_core"]
        self.assertEqual(
            core["required_H_power_traces_1_to_4"],
            {"1": 0, "2": 480, "3": 192, "4": 8568},
        )
        self.assertEqual(core["required_H_triangle_count"], 32)
        self.assertEqual(core["required_H_four_cycle_count"], 171)

    def test_component_partition_reduction(self) -> None:
        self.assertEqual(
            MODULE.endpoint_component_partitions(),
            ((4, 4, 4), (4, 8), (6, 6), (12,)),
        )
        theorem = self.results["general_core_theorem"]["component_balance"]
        self.assertEqual(
            theorem["surviving_component_partitions_of_12"],
            [[4, 4, 4], [4, 8], [6, 6], [12]],
        )

    def test_disconnected_component_pattern_moments(self) -> None:
        patterns = MODULE.component_pattern_constraints()
        for m in (4, 6, 8, 12):
            n0, n1, n2 = patterns[str(m)][
                "per_fibre_counts_z0_z1_z2"
            ]
            self.assertEqual(n0 + n1 + n2, 60)
            self.assertEqual(n1 + 2 * n2, 10 * m)
            self.assertEqual(n1 + 4 * n2, m * m + 8 * m)
        self.assertEqual(
            patterns["4"]["total_pattern_counts"],
            {
                "permutations_of_2_0_0": 12,
                "permutations_of_1_1_0": 48,
            },
        )
        self.assertEqual(
            patterns["6"]["total_pattern_counts"],
            {"1_1_1": 24, "permutations_of_2_1_0": 36},
        )
        self.assertEqual(
            patterns["8"]["total_pattern_counts"],
            {
                "permutations_of_2_2_0": 12,
                "permutations_of_2_1_1": 48,
            },
        )

    def test_frozen_result_file(self) -> None:
        expected = (
            json.dumps(
                self.results,
                indent=2,
                sort_keys=True,
                ensure_ascii=True,
            )
            + "\n"
        ).encode("utf-8")
        self.assertEqual(
            (DIRECTORY / "exact-results.json").read_bytes(),
            expected,
        )


if __name__ == "__main__":
    unittest.main()
