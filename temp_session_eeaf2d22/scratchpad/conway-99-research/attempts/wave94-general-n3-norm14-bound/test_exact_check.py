from __future__ import annotations

import json
import unittest
from pathlib import Path

import exact_check as check


PACKAGE = Path(__file__).resolve().parent


class Wave94ExactTests(unittest.TestCase):
    def test_seed_count(self) -> None:
        self.assertEqual(len(check.seeds()), 560)

    def test_mate_and_nonmate_seed_multiplicities(self) -> None:
        rows = check.candidate_transition_rows()
        mate_rows = [r for r in rows if r["other_endpoints_are_mates"]]
        nonmate_rows = [r for r in rows if not r["other_endpoints_are_mates"]]
        self.assertEqual(len(mate_rows), 84)
        self.assertEqual(len(nonmate_rows), 840)
        self.assertEqual({r["seed_multiplicity"] for r in mate_rows}, {0})
        self.assertEqual({r["seed_multiplicity"] for r in nonmate_rows}, {8})

    def test_endpoint_values(self) -> None:
        self.assertEqual(check.upper_from_prisms(0), 5544)
        self.assertEqual(check.upper_from_prisms(1), 5545)
        self.assertEqual(check.upper_from_prisms(1150), 7515)
        self.assertEqual(check.upper_from_prisms(1386), 7920)

    def test_p_and_n3_forms_agree_on_full_domain(self) -> None:
        for prisms in range(1387):
            n3 = 4158 - 3 * prisms
            self.assertEqual(
                check.upper_from_prisms(prisms),
                check.upper_from_n3(n3),
            )

    def test_monotone_integer_slope(self) -> None:
        rows = [check.upper_from_prisms(p) for p in range(1387)]
        self.assertTrue(all(b >= a for a, b in zip(rows, rows[1:])))
        self.assertEqual({b - a for a, b in zip(rows, rows[1:])}, {1, 2})

    def test_fail_closed_scope(self) -> None:
        result = check.exact_result()
        self.assertFalse(result["scope"]["requires_prism_free_endpoint"])
        self.assertFalse(result["scope"]["requires_rank_28"])
        self.assertTrue(result["scope"]["N14_counts_both_signs"])
        self.assertIsNone(result["endpoint"]["N16_upper_bound"])
        self.assertIsNone(result["endpoint"]["strict_n3_upper_bound"])

    def test_archived_result(self) -> None:
        observed = json.loads(
            (PACKAGE / "exact-results.json").read_text(encoding="utf-8")
        )
        self.assertEqual(observed, check.exact_result())


if __name__ == "__main__":
    unittest.main()

