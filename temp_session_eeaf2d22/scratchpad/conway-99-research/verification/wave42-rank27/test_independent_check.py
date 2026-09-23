from __future__ import annotations

import copy
import importlib.util
import json
import math
import tempfile
import unittest
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave42_rank27_independent", HERE / "independent_check.py"
)
CHECK = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(CHECK)


class RankPredicateTests(unittest.TestCase):
    def test_exact_controls(self) -> None:
        controls = CHECK.predicate_controls()
        self.assertTrue(controls["zero_accepted"])
        self.assertTrue(controls["rank_one_accepted"])
        self.assertTrue(controls["hostile_mutation_rejected"])
        self.assertTrue(controls["zero_diagonal_rank_two_rejected"])
        self.assertEqual(controls["rank_one_direct_rank"], 1)
        self.assertGreaterEqual(controls["hostile_direct_rank"], 2)

    def test_nonsymmetric_matrix_rejected(self) -> None:
        self.assertFalse(CHECK.rank_at_most_one([[1, 1], [0, 1]]))

    def test_vectorized_census_matches_dense_predicate(self) -> None:
        targets = np.asarray(
            [
                [[1, 2, 0], [2, 4, 0], [0, 0, 0]],
                [[0, 1, 0], [1, 0, 0], [0, 0, 0]],
            ],
            dtype=np.int16,
        )
        cores = np.asarray(
            [
                [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
                [[1, 2, 0], [2, 4, 0], [0, 0, 0]],
            ],
            dtype=np.int16,
        )
        pairs, hits, evaluations = CHECK.vectorized_rank_one_census(
            targets, cores, batch_size=1
        )
        expected = sum(
            CHECK.rank_at_most_one(((target - core) % 7).tolist())
            for target in targets
            for core in cores
        )
        self.assertEqual(pairs, 4)
        self.assertEqual(hits, expected)
        self.assertGreater(evaluations, 0)


class EnumerationTests(unittest.TestCase):
    def test_all_labelled_matchings(self) -> None:
        matchings = list(CHECK.perfect_matchings())
        self.assertEqual(len(matchings), 10395)
        self.assertEqual(len(set(matchings)), 10395)

    def test_all_eleven_types_are_disjoint_and_complete(self) -> None:
        types = set(CHECK.EVEN_TYPES) | set(CHECK.ODD_TYPES)
        self.assertEqual(len(types), 11)
        self.assertFalse(set(CHECK.EVEN_TYPES) & set(CHECK.ODD_TYPES))
        self.assertTrue(all(sum(parts) == 6 for parts in types))

    def test_local_rank_formula_for_all_types(self) -> None:
        for parts in (*CHECK.EVEN_TYPES, *CHECK.ODD_TYPES):
            e = sum(part % 2 == 0 for part in parts)
            matrix = CHECK.transported(CHECK.local_graph(parts))
            self.assertEqual(CHECK.rank(matrix), 25 - 2 * e)

    def test_small_minimum_F_enumeration(self) -> None:
        parts = (2, 2, 2)
        matrix = CHECK.transported(CHECK.local_graph(parts))
        signatures = CHECK.projected_signatures(CHECK.nullspace(matrix))
        records, metadata = CHECK.minimum_projection_permutations(
            signatures, 3
        )
        self.assertEqual(len(records), 32)
        self.assertEqual(metadata["winning_subspaces"], 32)
        self.assertTrue(
            all(len(rowspace) == 3 for _, rowspace in records)
        )

    def test_all_odd_pivot_csp_closes_a_type(self) -> None:
        record = CHECK.all_odd_pivot_csp((3, 3))
        self.assertEqual(record["complete_candidate_leaves"], 0)
        self.assertEqual(record["dense_rank_one_hits"], 0)
        self.assertEqual(
            record["labelled_pairs_covered_by_complete_CSP"],
            math.factorial(12) * 10395,
        )


class FreezeAndResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.path = HERE / "independent-results.json"
        cls.result = (
            json.loads(cls.path.read_text(encoding="utf-8"))
            if cls.path.exists()
            else None
        )

    def require_result(self) -> dict[str, object]:
        if self.result is None:
            self.skipTest("preliminary result not generated yet")
        return self.result

    def test_frozen_inputs_match(self) -> None:
        self.assertGreaterEqual(len(CHECK.frozen_inputs()), 10)

    def test_frozen_result_validates(self) -> None:
        CHECK.validate(self.require_result())

    def test_missing_type_is_rejected(self) -> None:
        hostile = copy.deepcopy(self.require_result())
        hostile["even_types"].pop("6")
        with self.assertRaises(ValueError):
            CHECK.validate(hostile)

    def test_incomplete_even_pair_count_is_rejected(self) -> None:
        hostile = copy.deepcopy(self.require_result())
        hostile["even_types"]["4+2"]["labelled_pairs_checked"] -= 1
        with self.assertRaises(ValueError):
            CHECK.validate(hostile)

    def test_incomplete_all_odd_coverage_is_rejected(self) -> None:
        hostile = copy.deepcopy(self.require_result())
        hostile["all_odd_types"]["3+3"][
            "labelled_pairs_covered_by_complete_CSP"
        ] -= 1
        with self.assertRaises(ValueError):
            CHECK.validate(hostile)

    def test_injected_survivor_is_rejected(self) -> None:
        hostile = copy.deepcopy(self.require_result())
        hostile["even_types"]["2+2+2"]["rank_at_most_one_survivors"] = 1
        with self.assertRaises(ValueError):
            CHECK.validate(hostile)

    def test_status_inflation_is_rejected(self) -> None:
        hostile = copy.deepcopy(self.require_result())
        hostile["status_wall"]["endpoint_n3_4158_excluded"] = True
        with self.assertRaises(ValueError):
            CHECK.validate(hostile)

    def test_duplicate_json_key_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "duplicate-key-hostile.json"
            path.write_text('{"a": 1, "a": 2}\\n', encoding="utf-8")
            with self.assertRaises(ValueError):
                CHECK.strict_load(path)


if __name__ == "__main__":
    unittest.main()
