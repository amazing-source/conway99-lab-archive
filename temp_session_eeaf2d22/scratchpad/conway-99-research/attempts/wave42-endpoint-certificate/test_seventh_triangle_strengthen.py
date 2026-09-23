#!/usr/bin/env python3
"""Tests for the Wave 42 branch-15 seventh-triangle strengthening."""

from __future__ import annotations

import gzip
import importlib.util
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE / "seventh_triangle_strengthen.py"
SPEC = importlib.util.spec_from_file_location("wave42_seventh_triangle", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to load Wave 42 implementation")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class SeventhTriangleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        (
            cls.result,
            cls.delta_gzip,
            cls.active_delta_gzip,
        ) = MODULE.build_artifacts()

    def test_root_label_and_variable_numbering(self) -> None:
        labels = MODULE.rooted_labels()
        variables = MODULE.residual_variable_ids()
        self.assertEqual(labels[0], (0, 2))
        self.assertEqual(labels[2], (0, 4))
        self.assertEqual(variables[(0, 2)], 2)

    def test_refinement_triangle_states(self) -> None:
        labels = MODULE.rooted_labels()
        states = tuple(
            MODULE.rooted_edge_state(labels, first, second)
            for first, second in MODULE.itertools.combinations(
                MODULE.REFINEMENT_TRIANGLE, 2
            )
        )
        self.assertEqual(states, (True, True, (0, 2)))

    def test_exact_raw_clause_census(self) -> None:
        delta = self.result["delta"]
        self.assertEqual(delta["constraints"], 64_932)
        self.assertEqual(
            delta["clause_width_histogram"],
            {"3": 132, "5": 64_800},
        )
        self.assertEqual(delta["exact_rows_already_in_source"], 0)
        self.assertEqual(delta["new_exact_rows"], 64_932)

    def test_enumeration_dimensions(self) -> None:
        enumeration = self.result["enumeration"]
        self.assertEqual(enumeration["neighbor_list_sizes"], [12, 83, 83])
        self.assertEqual(
            enumeration["matched_vertex_products_visited"],
            82_668,
        )

    def test_closure_simplification_census(self) -> None:
        simplified = self.result["wave41_closure_simplification"]
        self.assertEqual(
            simplified["satisfied_by_forced_false_variable"],
            31_154,
        )
        self.assertEqual(simplified["empty_residual_contradictions"], 0)
        self.assertEqual(simplified["distinct_active_clauses"], 33_778)
        self.assertEqual(
            simplified["active_width_histogram"],
            {"3": 91, "4": 580, "5": 33_107},
        )
        self.assertEqual(simplified["immediate_negative_units"], 0)

    def test_delta_header_and_line_count(self) -> None:
        raw = gzip.decompress(self.delta_gzip)
        lines = raw.splitlines()
        self.assertEqual(
            lines[0],
            b"* #variable= 289338 #constraint= 64932",
        )
        self.assertEqual(len(lines) - 1, 64_932)
        self.assertTrue(all(line.endswith(b" >= 1 ;") for line in lines[1:]))

    def test_active_delta_is_complete_and_retained(self) -> None:
        raw = gzip.decompress(self.active_delta_gzip)
        lines = raw.splitlines()
        self.assertEqual(
            lines[0],
            b"* #variable= 289338 #constraint= 33778",
        )
        self.assertEqual(len(lines) - 1, 33_778)
        catalog = self.result["wave41_closure_simplification"][
            "active_catalog"
        ]
        self.assertEqual(catalog["constraints"], 33_778)

    def test_delta_contains_only_negative_primary_literals(self) -> None:
        raw = gzip.decompress(self.delta_gzip)
        for line in raw.splitlines()[1:]:
            terms = MODULE.TERM_RE.findall(line + b"\n")
            self.assertTrue(terms)
            self.assertTrue(all(negated == b"~" for negated, _ in terms))
            self.assertTrue(
                all(1 <= int(variable) <= MODULE.PRIMARY_VARIABLES for _, variable in terms)
            )

    def test_committed_artifacts_replay_exactly(self) -> None:
        replay = MODULE.verify_committed()
        self.assertEqual(replay["status"], "PASS_EXACT_REPLAY")
        self.assertEqual(replay["new_branch15_constraints"], 64_932)

    def test_strict_json_loader_rejects_duplicate_keys(self) -> None:
        with self.assertRaises(ValueError):
            json.loads(
                '{"x":1,"x":2}',
                object_pairs_hook=MODULE.no_duplicate_object_keys,
            )

    def test_result_retains_unknown_status(self) -> None:
        result = self.result["result"]
        self.assertEqual(result["branch15_sat"], "UNKNOWN")
        self.assertEqual(result["branch15_unsat"], "UNKNOWN")
        self.assertEqual(result["endpoint_cases_closed"], 0)
        self.assertFalse(result["immediate_contradiction"])


if __name__ == "__main__":
    unittest.main()
