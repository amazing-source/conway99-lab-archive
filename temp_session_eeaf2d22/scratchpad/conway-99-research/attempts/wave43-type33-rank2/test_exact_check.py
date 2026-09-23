from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "attempts/wave43-type33-rank2/exact_check.py"
RESULT = ROOT / "attempts/wave43-type33-rank2/exact-results.json"


def load_module():
    spec = importlib.util.spec_from_file_location("wave43_type33", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Type33RankTwoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_module()
        cls.result = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_frozen_source(self) -> None:
        self.assertEqual(
            self.module.sha256_bytes(self.module.WAVE41.read_bytes()),
            self.module.WAVE41_SHA256,
        )

    def test_branch_census(self) -> None:
        search = self.result["search"]
        self.assertEqual(search["branches_visited"], 666666)
        self.assertEqual(search["invertible_pivot_branches"], 491220)
        self.assertEqual(search["nonempty_unary_branches"], 60306)
        self.assertEqual(search["backtrack_nodes"], 122922)
        self.assertEqual(search["complete_leaves"], 0)

    def test_no_rank_two_solution(self) -> None:
        self.assertEqual(self.result["solutions"], [])
        self.assertEqual(
            self.result["claim_label"],
            "DERIVED_PENDING_INDEPENDENT_VERIFICATION",
        )
        self.assertEqual(
            self.result["conclusion"],
            "No endpoint type-3+3 rank-two residual exists.",
        )

    def test_matching_matrix_alphabet(self) -> None:
        matching = [(0, 1), (2, 3), (4, 5), (6, 7), (8, 9), (10, 11)]
        matrix = self.module.pair_matrix(matching)
        self.assertEqual({matrix[i][i] for i in range(12)}, {0})
        self.assertEqual(
            {matrix[i][j] for i in range(12) for j in range(i)}, {1, 6}
        )
        self.assertTrue(all(matrix[i][j] == matrix[j][i] for i in range(12) for j in range(12)))

    def test_type33_interaction_and_planted_rank_two_control(self) -> None:
        wave41 = self.module.load_wave41()
        context = wave41.partition_context((3, 3))
        self.assertTrue(all(not any(vector) for vector in context["signatures"]))
        interaction = context["interaction"]
        self.assertEqual(interaction, [list(row) for row in zip(*interaction)])

        # X^T H X with rank(X)=rank(H)=2 is a generic planted symmetric
        # rank-two control and has an invertible principal 2x2 pivot.
        x = [[1, 0, 1], [0, 1, 1]]
        h = [[1, 2], [2, 3]]
        planted = wave41.matmul(
            wave41.transpose(x), wave41.matmul(h, x)
        )
        self.assertEqual(wave41.rank(planted), 2)
        self.assertNotEqual(
            (planted[0][0] * planted[1][1] - planted[0][1] ** 2) % 7,
            0,
        )

        with self.assertRaises(AssertionError):
            self.module.pair_matrix(
                [(0, 1), (0, 2), (3, 4), (5, 6), (7, 8), (9, 10)]
            )

    def test_scope_wall(self) -> None:
        wall = self.result["status_wall"]
        self.assertFalse(wall["endpoint_excluded"])
        self.assertFalse(wall["conway_99_resolved"])


if __name__ == "__main__":
    unittest.main()
