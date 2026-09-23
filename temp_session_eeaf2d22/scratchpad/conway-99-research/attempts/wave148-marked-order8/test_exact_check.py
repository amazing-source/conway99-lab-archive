#!/usr/bin/env python3
"""Focused tests for the Wave148 marked consistency rows."""

from __future__ import annotations

import gzip
import importlib.util
import json
import sys
import unittest
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("wave148_exact_check", HERE / "exact_check.py")
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CHECK
SPEC.loader.exec_module(CHECK)


class Wave148Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result, cls.row_gzip = CHECK.build_artifacts()
        cls.payload = json.loads(gzip.decompress(cls.row_gzip))

    def test_row_censuses_and_status(self) -> None:
        self.assertEqual(self.result["class_streams"]["7"]["count"], 208)
        self.assertEqual(self.result["class_streams"]["8"]["count"], 916)
        self.assertEqual(self.result["vertex_rows"]["rows"], 944)
        self.assertEqual(self.result["vertex_rows"]["nonzero_terms"], 10872)
        self.assertEqual(self.result["ordered_pair_rows"]["rows"], 4440)
        self.assertEqual(self.result["ordered_pair_rows"]["nonzero_terms"], 17782)
        self.assertEqual(self.result["ordered_pair_rows"]["zero_lhs_rows"], 893)
        self.assertEqual(self.result["ordered_pair_rows"]["zero_rhs_rows"], 893)
        self.assertEqual(self.result["status"]["solver_run"], "NOT_RUN")
        self.assertEqual(self.result["status"]["strict_n3_upper_bound"], "UNKNOWN")

    def test_each_row_has_declared_left_semantics(self) -> None:
        for row in self.payload["vertex_rows"]:
            self.assertEqual(
                row["lhs_coefficient"],
                row["orbit_multiplicity"] * row["outside_neighbor_count"],
            )
            self.assertEqual(
                row["outside_neighbor_count"], 14 - row["internal_degree"]
            )
        for row in self.payload["ordered_pair_rows"]:
            expected_target = 1 if row["root_relation"] == "edge" else 2
            self.assertEqual(row["target_common_neighbors"], expected_target)
            self.assertEqual(
                row["outside_common_neighbor_count"],
                expected_target - row["internal_common_neighbors"],
            )
            self.assertEqual(
                row["lhs_coefficient"],
                row["orbit_multiplicity"]
                * row["outside_common_neighbor_count"],
            )
            if row["lhs_coefficient"] == 0:
                self.assertEqual(row["terms_order8_mask_coefficient"], [])

    def test_independent_order_eight_column_aggregates(self) -> None:
        vertex_totals: Counter[int] = Counter()
        pair_totals: Counter[int] = Counter()
        for row in self.payload["vertex_rows"]:
            for mask8, coefficient in row["terms_order8_mask_coefficient"]:
                vertex_totals[mask8] += coefficient
        for row in self.payload["ordered_pair_rows"]:
            for mask8, coefficient in row["terms_order8_mask_coefficient"]:
                pair_totals[mask8] += coefficient

        classes8 = json.loads(CHECK.W147_RESULTS.read_text(encoding="utf-8"))[
            "class_streams"
        ]["8"]["canonical_masks"]
        self.assertTrue(set(vertex_totals).issubset(set(classes8)))
        self.assertTrue(set(pair_totals).issubset(set(classes8)))
        for mask8 in classes8:
            rows = CHECK.W147.adjacency_rows(mask8, 8)
            degrees = [row.bit_count() for row in rows]
            self.assertEqual(vertex_totals.get(mask8, 0), sum(degrees))
            self.assertEqual(
                pair_totals.get(mask8, 0),
                sum(degree * (degree - 1) for degree in degrees),
            )

    def test_hostile_coefficient_mutation_breaks_column_control(self) -> None:
        rows = json.loads(json.dumps(self.payload["vertex_rows"]))
        source = next(row for row in rows if row["terms_order8_mask_coefficient"])
        source["terms_order8_mask_coefficient"][0][1] += 1
        totals: Counter[int] = Counter()
        for row in rows:
            for mask8, coefficient in row["terms_order8_mask_coefficient"]:
                totals[mask8] += coefficient
        mutated_mask = source["terms_order8_mask_coefficient"][0][0]
        degrees = [
            row.bit_count()
            for row in CHECK.W147.adjacency_rows(mutated_mask, 8)
        ]
        self.assertNotEqual(totals[mutated_mask], sum(degrees))

    def test_stored_artifacts_exact_replay(self) -> None:
        stored = json.loads((HERE / "exact-results.json").read_text(encoding="utf-8"))
        self.assertEqual(self.result, stored)
        self.assertEqual(self.row_gzip, (HERE / "marked-rows.json.gz").read_bytes())


if __name__ == "__main__":
    unittest.main()
