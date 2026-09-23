#!/usr/bin/env python3
"""Hostile tests for the independent rooted pair-census crosscheck."""

from __future__ import annotations

import ast
import importlib.util
import sys
import unittest
from math import comb, factorial
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave34_rooted_pair_census_crosscheck", HERE / "crosscheck.py"
)
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CHECK
SPEC.loader.exec_module(CHECK)


class FrozenInputTests(unittest.TestCase):
    def test_all_frozen_inputs_and_manifests_match(self) -> None:
        result = CHECK.validate_inputs()
        self.assertTrue(result["all_frozen_inputs_match"], result["mismatches"])
        self.assertTrue(result["freeze_file_matches_constants"])
        self.assertEqual(result["entry_count"], 10)
        for manifest in result["checked_manifests"].values():
            self.assertTrue(manifest["all_match"], manifest["mismatches"])

    def test_crosschecker_has_no_structural_verifier_import(self) -> None:
        tree = ast.parse((HERE / "crosscheck.py").read_text(encoding="utf-8"))
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module)
        forbidden = {
            "exact_check",
            "static_compare",
            "test_exact_check",
            "test_static_compare",
            "reduction",
            "check_results",
        }
        self.assertFalse(imported & forbidden)


class SupportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.support = CHECK.support_reconstruction()

    def test_support_incidence_degrees(self) -> None:
        self.assertEqual(self.support["incidence_shape"], [14, 70])
        self.assertEqual(self.support["row_degree_set"], [10])
        self.assertEqual(self.support["column_degree_set"], [2])
        self.assertEqual(
            self.support["type_counts"],
            {
                "support_cross_nonedge_completion": 42,
                "support_edge_completion": 28,
            },
        )

    def test_multigraph_capacities(self) -> None:
        self.assertEqual(self.support["capacity_histogram"], {"1": 28, "2": 21})
        capacities = self.support["capacities"]
        self.assertEqual({sum(row) for row in capacities}, {10})
        self.assertEqual(
            {sum(capacities[p][line] for p in range(7)) for line in range(7)},
            {10},
        )

    def test_g_profiles_are_reconstructed_from_frozen_incidence(self) -> None:
        self.assertEqual(
            self.support["g_profiles"],
            {
                "support_cross_nonedge_completion": {
                    "0": 52,
                    "1": 16,
                    "2": 1,
                },
                "support_edge_completion": {"0": 51, "1": 18},
            },
        )

    def test_diagonal_DT_is_reconstructed_from_SO_block(self) -> None:
        self.assertEqual(
            self.support["diag_DT_by_type"],
            {
                "support_cross_nonedge_completion": 2,
                "support_edge_completion": 0,
            },
        )


class PairStateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.census = CHECK.pair_census()

    def test_exactly_nine_nonnegative_states(self) -> None:
        states = CHECK.allowed_states()
        self.assertEqual(len(states), 9)
        self.assertEqual(
            [CHECK.state_name(state) for state in states],
            list(CHECK.STATE_NAMES),
        )
        for state in states:
            self.assertEqual(sum(state), 2)

    def test_support_edge_row_distribution(self) -> None:
        self.assertEqual(
            self.census["row_distribution_by_support_type"]["support_edge"],
            {
                "g0_r0_h0_c2": 15,
                "g0_r0_h1_c1": 6,
                "g0_r1_h0_c1": 24,
                "g0_r1_h1_c0": 3,
                "g0_r2_h0_c0": 3,
                "g1_r0_h0_c1": 12,
                "g1_r0_h1_c0": 0,
                "g1_r1_h0_c0": 6,
                "g2_r0_h0_c0": 0,
            },
        )

    def test_duplicate_copy_row_distribution(self) -> None:
        self.assertEqual(
            self.census["row_distribution_by_support_type"][
                "support_nonedge_copy"
            ],
            {
                "g0_r0_h0_c2": 18,
                "g0_r0_h1_c1": 4,
                "g0_r1_h0_c1": 24,
                "g0_r1_h1_c0": 3,
                "g0_r2_h0_c0": 3,
                "g1_r0_h0_c1": 8,
                "g1_r0_h1_c0": 2,
                "g1_r1_h0_c0": 6,
                "g2_r0_h0_c0": 1,
            },
        )

    def test_triangular_elimination_has_nine_pivots(self) -> None:
        order = self.census["triangular_elimination_order"]
        self.assertEqual(len(order), 9)
        self.assertEqual(set(order), set(CHECK.STATE_NAMES))
        self.assertEqual(
            self.census["constraint_uniqueness"],
            "TRIANGULAR_NINE_PIVOTS",
        )

    def test_hostile_DT_mutation_changes_the_unique_row(self) -> None:
        correct = CHECK.triangular_row_census(g1=16, g2=1, diagonal_dt=2)
        hostile = CHECK.triangular_row_census(g1=16, g2=1, diagonal_dt=1)
        self.assertNotEqual(hostile, correct)
        self.assertEqual(hostile["g1_r0_h1_c0"], 1)
        self.assertEqual(correct["g1_r0_h1_c0"], 2)

    def test_global_distribution_partitions_every_pair(self) -> None:
        expected = {
            "g0_r0_h0_c2": 588,
            "g0_r0_h1_c1": 168,
            "g0_r1_h0_c1": 840,
            "g0_r1_h1_c0": 105,
            "g0_r2_h0_c0": 105,
            "g1_r0_h0_c1": 336,
            "g1_r0_h1_c0": 42,
            "g1_r1_h0_c0": 210,
            "g2_r0_h0_c0": 21,
        }
        self.assertEqual(
            self.census["global_unordered_pair_distribution"], expected
        )
        self.assertEqual(sum(expected.values()), comb(70, 2))
        self.assertEqual(self.census["global_pair_total"], 2415)

    def test_g2_duplicate_pairs_force_all_other_coordinates_zero(self) -> None:
        duplicate = self.census["duplicate_pair_rule"]
        self.assertEqual(duplicate["state"], "g2_r0_h0_c0")
        self.assertEqual(duplicate["pairs"], 21)
        self.assertEqual(duplicate["degree"], 1)
        self.assertTrue(duplicate["matching"])
        self.assertTrue(duplicate["B_rows_disjoint"])
        self.assertTrue(duplicate["D_nonadjacent"])
        self.assertTrue(duplicate["no_common_O_neighbour"])

    def test_X11_is_forced_6_regular_210_edge_graph(self) -> None:
        graph = self.census["X11_graph"]
        self.assertEqual(graph["state"], "g1_r1_h0_c0")
        self.assertEqual((graph["vertices"], graph["degree"], graph["edges"]), (70, 6, 210))
        self.assertTrue(graph["regular"])
        self.assertTrue(graph["disjoint_from_D"])
        self.assertTrue(graph["disjoint_from_offdiagonal_support_D2"])


class PermanentEnumerationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.columns = CHECK.column_cycle_census()

    def test_permanent_sanity_controls(self) -> None:
        identity = [[int(i == j) for j in range(7)] for i in range(7)]
        ones = [[1] * 7 for _ in range(7)]
        hostile = [row[:] for row in ones]
        hostile[0] = [0] * 7
        self.assertEqual(CHECK.permanent(identity), 1)
        self.assertEqual(CHECK.permanent(ones), factorial(7))
        self.assertEqual(CHECK.permanent(hostile), 0)

    def test_cycle_type_controls(self) -> None:
        self.assertEqual(CHECK.cycle_type(tuple(range(7))), (1, 1, 1, 1, 1, 1, 1))
        self.assertEqual(CHECK.cycle_type((1, 2, 3, 4, 5, 6, 0)), (7,))
        self.assertEqual(CHECK.cycle_type((1, 0, 3, 4, 2, 6, 5)), (3, 2, 2))

    def test_all_relative_permutations_are_checked(self) -> None:
        self.assertEqual(self.columns["permutations_checked"], factorial(7))
        self.assertEqual(
            sum(self.columns["permutation_cycle_type_counts"].values()),
            factorial(7),
        )

    def test_alternating_decomposition_divisibility(self) -> None:
        for record in self.columns["decomposition_divisibility"].values():
            self.assertEqual(record["ordered_labeled_mod_2_to_cycles"], 0)
            self.assertEqual(record["ordered_underlying_mod_2_to_cycles"], 0)

    def test_full_cycle_census(self) -> None:
        self.assertEqual(
            self.columns["labeled_cycle_census"],
            CHECK.EXPECTED_CYCLE_CENSUS,
        )

    def test_full_and_underlying_totals(self) -> None:
        self.assertEqual(
            self.columns["underlying_capacity_bounded_two_factors"], 4946952
        )
        self.assertEqual(self.columns["all_labeled_Pb_columns"], 574118037)
        self.assertEqual(self.columns["raw_weight_14_columns"], comb(70, 14))

    def test_duplicate_free_total_and_types(self) -> None:
        self.assertEqual(
            self.columns["duplicate_free_types"],
            ["3+2+2", "4+3", "5+2", "7"],
        )
        self.assertEqual(self.columns["duplicate_free_Pb_columns"], 448879368)
        self.assertEqual(
            self.columns["columns_excluded_by_duplicate_pair_rule"], 125238669
        )
        self.assertEqual(448879368 + 125238669, 574118037)

    def test_hostile_reintroduction_of_one_cycles_adds_columns(self) -> None:
        with_one = sum(
            count
            for label, count in self.columns["labeled_cycle_census"].items()
            if "1" in label.split("+")
        )
        self.assertEqual(with_one, 125238669)
        self.assertGreater(with_one, 0)


class IntegratedStatusTests(unittest.TestCase):
    def test_every_scoped_claim_reproduces(self) -> None:
        result = CHECK.build_results()
        self.assertTrue(result["claim_comparison"]["all_claims_reproduce"])
        self.assertEqual(result["claim_comparison"]["discrepancies"], [])
        self.assertEqual(result["verdict"], "PASS")

    def test_all_global_walls_remain_unknown(self) -> None:
        status = CHECK.build_results()["status"]
        for key in (
            "compatible_15_column_design",
            "binary_D_B_solution",
            "rooted_graph_extension_or_exclusion",
            "rooted_endpoint",
            "n3_708",
            "Conway_99",
            "novelty",
        ):
            self.assertEqual(status[key], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
