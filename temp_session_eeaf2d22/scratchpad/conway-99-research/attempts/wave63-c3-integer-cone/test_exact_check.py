#!/usr/bin/env python3
"""Tests for the Wave 63 independent certificate checker."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import unittest


PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
import exact_check as CHECK  # noqa: E402


class Wave63CheckerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        CHECK.check_frozen_inputs()
        cls.types = CHECK.load_types()

    def test_profiles_are_complete(self) -> None:
        self.assertEqual(len(CHECK.PROFILE_VALUES), 6)
        self.assertEqual(len(CHECK.PROFILE_TRIPLES), 21)
        for triple in CHECK.PROFILE_TRIPLES:
            totals = tuple(
                sum(
                    CHECK.PROFILE_VALUES[triple[component]][fibre]
                    for component in range(3)
                )
                for fibre in range(3)
            )
            self.assertEqual(totals, (2, 2, 2))

    def test_frozen_component_types(self) -> None:
        self.assertEqual(len(self.types), 18)
        for record in self.types:
            rows = CHECK.component_rows(record)
            self.assertEqual({row.bit_count() for row in rows}, {3})

    def test_global_minimum_lane_count(self) -> None:
        records = [self.types[0], self.types[0], self.types[0]]
        self.assertEqual(CHECK.candidate_count(records), 15_936)
        columns = CHECK.candidates(records)
        self.assertEqual(len(columns), 15_936)
        self.assertEqual(len(columns), len(set(columns)))

    def test_target_basic_invariants(self) -> None:
        gram = CHECK.target_gram(
            [self.types[0], self.types[0], self.types[0]]
        )
        self.assertEqual([gram[index][index] for index in range(36)], [10] * 36)
        self.assertTrue(all(
            gram[left][right] == gram[right][left]
            for left in range(36)
            for right in range(36)
        ))
        self.assertGreaterEqual(min(map(min, gram)), 0)

    def test_exact_witness_and_mutation(self) -> None:
        path = (
            PACKAGE / "exact-results.json"
            if (PACKAGE / "exact-results.json").exists()
            else PACKAGE / "smoke-results.json"
        )
        data = json.loads(path.read_text(encoding="utf-8"))
        lane = next(
            record for record in data["results"]
            if record["rational_cone"]["claim_label"] == "DERIVED"
        )
        records = [self.types[value] for value in lane["type_triple"]]
        columns = CHECK.candidates(records)
        gram = CHECK.target_gram(records)
        witness = lane["rational_cone"]["exact_witness"]
        replay = CHECK.verify_witness(witness, columns, gram, False)
        self.assertTrue(replay["all_630_pair_equations_exact"])
        changed = copy.deepcopy(witness)
        changed[0]["numerator"] += 1
        with self.assertRaises(AssertionError):
            CHECK.verify_witness(changed, columns, gram, False)

    def test_full_saved_checkpoint(self) -> None:
        path = (
            PACKAGE / "exact-results.json"
            if (PACKAGE / "exact-results.json").exists()
            else PACKAGE / "smoke-results.json"
        )
        result = CHECK.verify(path)
        self.assertEqual(result["endpoint_status"], "UNKNOWN")
        self.assertGreaterEqual(result["exact_rational_witnesses_checked"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
