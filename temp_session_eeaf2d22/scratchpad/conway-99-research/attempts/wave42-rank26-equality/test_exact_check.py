from __future__ import annotations

import importlib.util
import itertools
import json
import random
import unittest
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


exact = load("wave42_exact", HERE / "exact_check.py")
compose = load("wave42_compose", HERE / "compose_results.py")


class RankOneTests(unittest.TestCase):
    def test_diagonal_filter_accepts_both_square_classes(self) -> None:
        diagonals = np.asarray(
            [
                [0, 1, 2, 4],
                [3, 0, 5, 6],
            ],
            dtype=np.int8,
        )
        self.assertEqual(
            exact.rank_one_diagonal_mask(diagonals).tolist(),
            [True, True],
        )

    def test_diagonal_filter_rejects_zero_and_mixed_classes(self) -> None:
        diagonals = np.asarray(
            [
                [0, 0, 0],
                [1, 3, 0],
                [2, 5, 4],
            ],
            dtype=np.int8,
        )
        self.assertEqual(
            exact.rank_one_diagonal_mask(diagonals).tolist(),
            [False, False, False],
        )

    def test_diagonal_filter_has_no_false_negative_in_dimension_three(self) -> None:
        diagonals = []
        for scale in range(1, 7):
            for vector in itertools.product(range(7), repeat=3):
                if not any(vector):
                    continue
                diagonals.append(
                    [(scale * value * value) % 7 for value in vector]
                )
        mask = exact.rank_one_diagonal_mask(
            np.asarray(diagonals, dtype=np.int8)
        )
        self.assertTrue(bool(mask.all()))

    def test_exact_rank_one_positive_and_negative_controls(self) -> None:
        wave41 = exact.load_wave41()
        vector = [1, 2, 0, 4]
        positive = [
            [(3 * left * right) % 7 for right in vector]
            for left in vector
        ]
        negative = [row[:] for row in positive]
        negative[2][2] = 1
        self.assertTrue(exact.exact_rank_one(positive, wave41))
        self.assertFalse(exact.exact_rank_one(negative, wave41))

    def test_pivot_predicate_matches_gaussian_rank(self) -> None:
        wave41 = exact.load_wave41()
        generator = random.Random(420027)
        matrices = []
        for size in (1, 2, 3, 6):
            for _ in range(40):
                matrix = [[0] * size for _ in range(size)]
                for i in range(size):
                    for j in range(i, size):
                        value = generator.randrange(7)
                        matrix[i][j] = matrix[j][i] = value
                matrices.append(matrix)
        for matrix in matrices:
            with self.subTest(size=len(matrix), matrix=matrix):
                self.assertEqual(
                    exact.exact_rank_one(matrix, wave41),
                    wave41.rank(matrix) == 1,
                )


class ProjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.wave41 = exact.load_wave41()
        cls.edges, cls.pairing_indices, _ = cls.wave41.pairing_index_data()

    def test_projected_forms_match_direct_exact_products(self) -> None:
        partition = (4, 2)
        permutation = tuple(range(12))
        data = self.wave41.quotient_data(partition, permutation)
        forms = exact.projected_matching_forms(
            data["Z"], self.edges, self.pairing_indices
        )
        pairings = tuple(self.wave41.all_pairings())
        for index in (0, 1, 10_394):
            direct = self.wave41.restricted_form(
                data["Z"], self.wave41.within_z_block(pairings[index])
            )
            self.assertEqual(forms[index].astype(int).tolist(), direct)

    def test_wave41_decomposition_control(self) -> None:
        partition = (3, 3)
        permutation = tuple(range(12))
        matching = next(self.wave41.all_pairings())
        data = self.wave41.quotient_data(partition, permutation)
        residual = self.wave41.add(
            self.wave41.restricted_form(
                data["Z"], self.wave41.within_z_block(matching)
            ),
            data["target"],
            -1,
        )
        predicted = (
            self.wave41.rank(data["S"])
            + 2 * data["F_rank"]
            + self.wave41.rank(residual)
        )
        actual = self.wave41.rank(
            self.wave41.full_block(partition, permutation, matching)
        )
        self.assertEqual(predicted, actual)


class AtomicResultTests(unittest.TestCase):
    def test_all_available_atomic_results_are_internally_valid(self) -> None:
        for path in sorted(HERE.glob("partial-*.json")):
            with self.subTest(path=path.name):
                result = json.loads(path.read_text(encoding="utf-8"))
                exact.validate(result)

    def test_completed_atomic_results_have_no_rank26_witness(self) -> None:
        for path in sorted(HERE.glob("partial-*.json")):
            result = json.loads(path.read_text(encoding="utf-8"))
            for entry in result["partitions"].values():
                with self.subTest(partition=entry["partition"]):
                    self.assertEqual(
                        entry["exact_rank_one_residual_pairs"], 0
                    )
                    self.assertFalse(entry["rank26_exists"])

    def test_composition_when_all_atomics_exist(self) -> None:
        paths = [compose.atomic_path(partition) for partition in compose.PARTITIONS]
        if not all(path.exists() for path in paths):
            self.skipTest("the two long atomic jobs have not finished")
        result = compose.compute()
        compose.validate(result)
        self.assertEqual(result["totals"]["partition_types"], 11)
        self.assertEqual(result["totals"]["exact_rank_one_residual_pairs"], 0)
        self.assertEqual(
            result["candidate_conclusion"]["global_M_rank_F7_at_least"], 27
        )


if __name__ == "__main__":
    unittest.main()
