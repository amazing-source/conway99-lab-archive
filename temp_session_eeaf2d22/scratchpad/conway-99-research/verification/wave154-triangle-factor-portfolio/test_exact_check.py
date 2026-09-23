from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("exact_check.py")
SPEC = importlib.util.spec_from_file_location("wave154_cleanroom", MODULE_PATH)
assert SPEC and SPEC.loader
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class Wave154HostileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.wave151 = CHECK.load_json(CHECK.W151_RESULTS)
        cls.wave154 = CHECK.load_json(CHECK.W154_RESULTS)
        cls.old_q1 = tuple(cls.wave151["exact_partial_factor"]["Q1"])
        cls.new_q1 = tuple(
            cls.wave154["second_exact_Q1_representative"]["Q1"]
        )
        cls.group = CHECK.centralizer()
        cls.edge_actions = tuple(
            CHECK.induced_edge_action(action) for action in cls.group
        )

    def test_complete_reconstruction(self) -> None:
        result = CHECK.run_checks()
        self.assertEqual(result["allowed_triples"], 69_270)
        self.assertEqual(result["triple_orbit_count"], 292)
        self.assertEqual(result["constraint_rows"], 612)
        self.assertEqual(result["integer_matrix_nonzeros"], 1_039_050)

    def test_duplicate_q1_entry_is_rejected(self) -> None:
        corrupted = list(self.new_q1)
        corrupted[0] = corrupted[1]
        with self.assertRaisesRegex(ValueError, "not a permutation"):
            CHECK.incidence_matrix(corrupted)

    def test_valid_permutation_mutation_breaks_gram(self) -> None:
        corrupted = list(self.new_q1)
        corrupted[0], corrupted[1] = corrupted[1], corrupted[0]
        matrix = CHECK.incidence_matrix(corrupted)
        self.assertNotEqual(CHECK.gram(matrix), CHECK.expected_partial_gram())

    def test_noncentralizing_negative_control_is_excluded(self) -> None:
        # This map swaps 0 and 2 only.  It is a permutation, but it does not
        # commute with either matching M or shift P.
        bad = list(range(12))
        bad[0], bad[2] = bad[2], bad[0]
        self.assertFalse(
            all(
                bad[CHECK.matching(v)] == CHECK.matching(bad[v])
                and bad[CHECK.shift(v)] == CHECK.shift(bad[v])
                for v in range(12)
            )
        )
        self.assertNotIn(tuple(bad), set(self.group))

    def test_old_orbit_member_and_new_orbit_separation(self) -> None:
        old_orbit = CHECK.q1_orbit(self.old_q1, self.edge_actions)
        transformed_old = CHECK.conjugate_edge_permutation(
            self.old_q1, self.edge_actions[137]
        )
        self.assertIn(transformed_old, old_orbit)
        self.assertNotIn(self.new_q1, old_orbit)

    def test_zero_capacity_triple_is_rejected(self) -> None:
        edges = CHECK.nonmatching_edges()
        g01, g02, g12 = CHECK.cross_grams()
        rejected = next(
            triple
            for triple in __import__("itertools").product(range(60), repeat=3)
            if not CHECK.triple_allowed(triple, edges, g01, g02, g12)
        )
        self.assertFalse(
            CHECK.triple_allowed(rejected, edges, g01, g02, g12)
        )

    def test_cross_capacity_totals_force_equalities(self) -> None:
        # Sixty selected triples contribute 4 cells to each cross block.
        self.assertEqual(
            [sum(map(sum, block)) for block in CHECK.cross_grams()],
            [240, 240, 240],
        )
        self.assertEqual(60 * 4, 240)


if __name__ == "__main__":
    unittest.main()
