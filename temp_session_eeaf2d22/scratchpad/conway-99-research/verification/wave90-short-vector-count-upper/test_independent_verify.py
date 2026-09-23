from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("independent_verify.py")
SPEC = importlib.util.spec_from_file_location("wave90_independent", MODULE_PATH)
assert SPEC and SPEC.loader
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)


class Wave90IndependentTests(unittest.TestCase):
    def test_rooted_scaffold(self) -> None:
        self.assertEqual(len(VERIFY.rooted_labels()), 84)
        self.assertEqual(len(VERIFY.root_seeds()), 560)

    def test_prism_free_transition_extensions(self) -> None:
        seeds = tuple(frozenset(row) for row in VERIFY.root_seeds())
        counts = {
            sum({s, a, b} <= seed for seed in seeds)
            for s, a, b in VERIFY.prism_free_transition_triples()
        }
        self.assertEqual(counts, {8})

    def test_local_matchings_and_star_cap(self) -> None:
        seed = frozenset((0, 2, 4, 6))
        for shared in seed:
            star = seed - {shared}
            for matching in VERIFY.local_prism_free_matchings(shared):
                selected = sum(
                    {left, right} <= star for left, right in matching
                )
                self.assertLessEqual(selected, 1)
        self.assertEqual(len(VERIFY.local_prism_free_matchings(0)), 6040)

    def test_fano_seed_recovers_both_sides(self) -> None:
        rows = VERIFY.fano_seed_reconstructions()
        self.assertEqual(len(rows), 7)
        self.assertTrue(all(row["six_pair_labels_distinct"] for row in rows))
        self.assertTrue(all(row["positive_side_recovered"] for row in rows))
        self.assertTrue(all(row["negative_side_recovered"] for row in rows))

    def test_sign_orientation_count(self) -> None:
        result = VERIFY.independent_result()
        count = result["global_count"]
        self.assertEqual(count["positive_coordinates_per_oriented_vector"], 7)
        self.assertEqual(count["antipodal_pair_rooted_positive_incidences"], 14)
        self.assertEqual(count["N14_upper_bound"], 5544)
        self.assertEqual(count["N14_upper_bound"] % 2, 0)

    def test_scope_does_not_import_rank_28(self) -> None:
        result = VERIFY.independent_result()
        self.assertFalse(result["scope"]["requires_rank_28"])
        self.assertTrue(result["scope"]["requires_prism_free_endpoint_P0"])
        self.assertEqual(
            result["verdict"]["N14_plus_N16_plus_N18_upper_bound"],
            "NOT_PROVED",
        )
        self.assertFalse(result["verdict"]["q16_excluded"])


if __name__ == "__main__":
    unittest.main()
