from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SPEC = importlib.util.spec_from_file_location(
    "wave43_rank28_independent", HERE / "independent_check.py"
)
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)
RESULT = json.loads(
    (HERE / "independent-results.json").read_text(encoding="utf-8")
)


class IndependentRank28Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contexts = {
            "2+2+2": CHECK.partition_context((2, 2, 2)),
            "4+2": CHECK.partition_context((4, 2)),
            "6": CHECK.partition_context((6,)),
            "3+3": CHECK.partition_context((3, 3)),
        }

    def test_frozen_inputs(self) -> None:
        self.assertEqual(CHECK.sha256_file(CHECK.WAVE41), CHECK.WAVE41_SHA)
        self.assertEqual(CHECK.sha256_file(CHECK.WAVE42), CHECK.WAVE42_SHA)

    def test_result_schema_and_scope(self) -> None:
        CHECK.validate_result(RESULT)
        wall = RESULT["status_wall"]
        self.assertEqual(wall["conditional_endpoint_rank_F7_floor"], 28)
        self.assertFalse(wall["endpoint_excluded"])
        self.assertFalse(wall["strict_general_upper_bound_improved"])
        self.assertFalse(wall["graph_constructed"])
        self.assertFalse(wall["conway_99_resolved"])

    def test_rank27_dichotomy(self) -> None:
        self.assertEqual(CHECK.rank27_mechanisms(1), [[1, 2], [2, 0]])
        self.assertEqual(CHECK.rank27_mechanisms(2), [[2, 2], [3, 0]])
        self.assertEqual(CHECK.rank27_mechanisms(3), [[3, 2], [4, 0]])
        self.assertNotEqual(
            RESULT["controls"]["rank_formula_hostile"][
                "mutated_constant_24_mechanisms"
            ],
            CHECK.rank27_mechanisms(1),
        )

    def test_local_matrix_ranks_and_type33_zero_border(self) -> None:
        self.assertEqual(
            {
                key: context["rank_S"]
                for key, context in self.contexts.items()
            },
            {"2+2+2": 19, "4+2": 21, "6": 23, "3+3": 25},
        )
        self.assertTrue(
            all(
                not any(vector)
                for vector in self.contexts["3+3"]["signatures"]
            )
        )

    def test_exact_rank_formula_on_independent_full_blocks(self) -> None:
        examples = {
            "2+2+2": ((2, 2, 2), RESULT["even_types"]["2+2+2"][
                "bounded_rank"
            ]["first_20"][0]),
            "4+2": ((4, 2), RESULT["even_types"]["4+2"]["bounded_rank"][
                "first_20"
            ][0]),
            "6": ((6,), RESULT["even_types"]["6"]["bounded_rank"][
                "first_20"
            ][0]),
            "3+3": ((3, 3), list(range(1, 12)) + [0]),
        }
        for key, (parts, permutation) in examples.items():
            with self.subTest(key=key):
                data = CHECK.quotient(self.contexts[key], permutation)
                residual = CHECK.schur_residual(
                    self.contexts[key], permutation, CHECK.PAIRINGS[0]
                )
                predicted = (
                    self.contexts[key]["rank_S"]
                    + 2 * data["F_rank"]
                    + CHECK.rank(residual)
                )
                actual = CHECK.rank(
                    CHECK.full_block(parts, permutation, CHECK.PAIRINGS[0])
                )
                self.assertEqual(actual, predicted)

    def test_direct_type6_derangement_enumeration(self) -> None:
        values, _ = CHECK.bounded_rank_derangements(
            self.contexts["6"], 1, CHECK.MemoryGuard()
        )
        self.assertEqual(len(values), 288)
        self.assertEqual(
            CHECK.permutation_stream_hash(values),
            RESULT["even_types"]["6"]["bounded_rank"]["stream_sha256"],
        )
        self.assertTrue(
            all(
                permutation[left] != left
                for permutation in values
                for left in range(CHECK.SIDE)
            )
        )

    def test_batched_rank_controls_include_nonprincipal_hostile(self) -> None:
        controls = np.asarray(
            [
                np.zeros((4, 4), dtype=np.int16),
                np.diag([1, 0, 0, 0]),
                np.diag([1, 1, 0, 0]),
                np.diag([1, 1, 1, 0]),
                [
                    [0, 1, 0, 0],
                    [1, 0, 0, 0],
                    [0, 0, 0, 1],
                    [0, 0, 1, 0],
                ],
            ],
            dtype=np.int16,
        )
        self.assertEqual(
            CHECK.batch_ranks_capped(controls, cap=3).tolist(),
            [0, 1, 2, 3, 3],
        )

    def test_matching_universe_and_hostile_degree(self) -> None:
        self.assertEqual(len(CHECK.PAIRINGS), 10_395)
        matrix = CHECK.pair_matrix(CHECK.PAIRINGS[0])
        self.assertEqual(matrix[0][1], 6)
        self.assertEqual(matrix[0][2], 1)
        with self.assertRaises(AssertionError):
            CHECK.pair_matrix(
                ((0, 1), (0, 2), (3, 4), (5, 6), (7, 8), (9, 10))
            )

    def test_matching_form_positive_and_perturbation_controls(self) -> None:
        for key in ("2+2+2", "4+2"):
            record = RESULT["even_types"][key]["zero_residual_scan"]
            self.assertTrue(record["planted_matching_form_accepted"])
            self.assertTrue(record["perturbed_matching_form_rejected"])

    def test_even_type_zero_results(self) -> None:
        self.assertEqual(
            RESULT["even_types"]["2+2+2"]["zero_residual_scan"][
                "pairs_tested"
            ],
            332 * 10_395,
        )
        self.assertEqual(
            RESULT["even_types"]["4+2"]["zero_residual_scan"][
                "pairs_tested"
            ],
            1_352 * 10_395,
        )
        self.assertEqual(
            RESULT["even_types"]["6"]["minimum_scan"]["pairs_tested"],
            288 * 10_395,
        )
        self.assertEqual(
            RESULT["even_types"]["6"]["minimum_scan"][
                "rank_at_most_two_pairs"
            ],
            0,
        )

    def test_type6_csp_counts_and_nonvacuous_plant(self) -> None:
        record = RESULT["even_types"]["6"]["higher_F_CSP"]
        self.assertEqual(record["pivot_assignment_branches"], 1_014)
        self.assertEqual(record["pivot_mate_branches"], 92_274)
        self.assertEqual(record["unary_viable_branches"], 488)
        self.assertEqual(record["backtrack_nodes"], 1_058)
        self.assertEqual(record["complete_leaves"], 0)
        planted = RESULT["controls"]["type6_planted_zero_residual_CSP"]
        self.assertTrue(planted["accepted"])
        self.assertEqual(planted["backtrack_nodes_until_leaf"], 11)

    def test_type33_counts_and_principal_pivot_control(self) -> None:
        record = RESULT["type33"]
        self.assertEqual(record["branches_visited"], 666_666)
        self.assertEqual(record["invertible_pivot_branches"], 491_220)
        self.assertEqual(record["nonempty_unary_branches"], 60_306)
        self.assertEqual(record["backtrack_nodes"], 122_922)
        self.assertEqual(record["complete_leaves"], 0)
        planted = RESULT["controls"]["type33_planted_rank_two"]
        self.assertEqual(planted["rank"], 2)
        self.assertNotEqual(planted["invertible_principal_minor"], 0)
        self.assertTrue(planted["accepted_by_rank_and_pivot_predicates"])
        csp_plant = RESULT["controls"]["type33_planted_rank_two_CSP"]
        self.assertTrue(csp_plant["accepted"])
        self.assertEqual(csp_plant["residual_rank"], 2)
        self.assertEqual(csp_plant["backtrack_nodes_until_leaf"], 11)


if __name__ == "__main__":
    unittest.main()
