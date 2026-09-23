from __future__ import annotations

import json
import unittest
from pathlib import Path

import exact_check as check


PACKAGE = Path(__file__).resolve().parent


class Wave90ExactCheckTests(unittest.TestCase):
    def test_rooted_scaffold_counts(self) -> None:
        self.assertEqual(len(check.residual_labels()), 84)
        self.assertEqual(len(check.seeds()), 560)
        self.assertEqual(len(check.allowed_transition_triples()), 840)

    def test_every_allowed_transition_has_eight_seed_extensions(self) -> None:
        seed_sets = [frozenset(q) for q in check.seeds()]
        multiplicities = {
            sum({s, a, b} <= q for q in seed_sets)
            for s, a, b in check.allowed_transition_triples()
        }
        self.assertEqual(multiplicities, {8})

    def test_local_matching_count(self) -> None:
        self.assertEqual(check.allowed_local_matching_count(), 6040)

    def test_fano_reconstruction_is_injective_for_every_root(self) -> None:
        rows = check.fano_reconstruction_rows()
        self.assertEqual(len(rows), 7)
        self.assertTrue(all(row["unique_reconstruction"] for row in rows))

    def test_exact_bound_arithmetic(self) -> None:
        result = check.exact_result()
        count = result["transition_double_count"]
        self.assertEqual(count["selected_transition_count"], 84)
        self.assertEqual(count["transition_seed_incidences"], 672)
        self.assertEqual(count["selected_transitions_per_seed_upper_bound"], 4)
        self.assertEqual(count["bad_seed_lower_bound"], 168)
        self.assertEqual(count["valid_seed_upper_bound"], 392)
        self.assertEqual(result["global_bound"]["N14_upper_bound"], 5544)

    def test_scope_is_fail_closed(self) -> None:
        result = check.exact_result()
        self.assertTrue(result["scope"]["requires_prism_free_endpoint"])
        self.assertEqual(result["scope"]["requires_n3"], 4158)
        self.assertTrue(result["scope"]["n14_counts_both_signs"])
        self.assertIsNone(
            result["endpoint"]["N14_plus_N16_plus_N18_upper_bound"]
        )
        self.assertFalse(result["endpoint"]["prism_free_rank_28_excluded"])

    def test_archived_result_matches_reconstruction(self) -> None:
        archived = json.loads(
            (PACKAGE / "exact-results.json").read_text(encoding="utf-8")
        )
        self.assertEqual(archived, check.exact_result())


if __name__ == "__main__":
    unittest.main()

