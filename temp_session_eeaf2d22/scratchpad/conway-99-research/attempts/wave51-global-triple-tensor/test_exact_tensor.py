#!/usr/bin/env python3
"""Hostile and exact tests for the Wave 51 tensor certificate."""

from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import exact_tensor as target  # noqa: E402


class ExactTensorTests(unittest.TestCase):
    def test_exact_certificate(self) -> None:
        checks = target.verify_certificate()
        self.assertTrue(checks["tensor_nonnegative"])
        self.assertTrue(checks["slices_integral"])
        self.assertEqual(checks["global_balance_equations_checked"], 125)

    def test_displayed_tables_and_margins(self) -> None:
        certificate = target.certificate_dict()
        tables = target.build_tables(certificate)
        self.assertEqual(tables[1][1], (1, 5, 0, 8, 4))
        self.assertEqual(tables[2][1][1], 0)
        self.assertEqual(tables[3][1][1], 1)
        self.assertEqual(tables[4][1][1], 2)
        for table in tables:
            self.assertEqual(tuple(map(sum, table)), target.VALENCIES)

    def test_hostile_tensor_mutation_is_rejected(self) -> None:
        entries = list(copy.deepcopy(target.CERTIFICATE_ENTRIES))
        location = next(
            index for index, (key, _) in enumerate(entries)
            if key == (4, 4, 4)
        )
        entries[location] = ((4, 4, 4), 109)
        with self.assertRaises(AssertionError):
            target.verify_certificate(entries)

    def test_hostile_balance_mutation_is_rejected(self) -> None:
        entries = list(copy.deepcopy(target.CERTIFICATE_ENTRIES))
        location = next(
            index for index, (key, _) in enumerate(entries)
            if key == (1, 2, 2)
        )
        entries[location] = ((1, 2, 2), 287)
        with self.assertRaises(AssertionError):
            target.verify_certificate(entries)

    def test_associativity_failure_is_retained(self) -> None:
        tables = target.build_tables(target.certificate_dict())
        failures = target.associativity_failures(tables)
        self.assertEqual(len(failures), 100)
        self.assertEqual(
            failures[0],
            {
                "indices_i_j_m_k": [1, 1, 2, 2],
                "left_association": 81,
                "right_association": 153,
            },
        )

    def test_result_boundary(self) -> None:
        payload = target.build_results()
        self.assertTrue(payload["result"]["positive_aggregate_control"])
        self.assertFalse(payload["result"]["exact_contradiction"])
        self.assertEqual(
            payload["claim_boundary"]["prism_free_endpoint"], "UNKNOWN"
        )
        self.assertEqual(payload["claim_boundary"]["conway_99"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
