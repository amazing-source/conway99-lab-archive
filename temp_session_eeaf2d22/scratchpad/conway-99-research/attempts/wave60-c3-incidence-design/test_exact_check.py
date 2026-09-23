#!/usr/bin/env python3
"""Independent unit checks for the Wave 60 discovery package."""

from __future__ import annotations

import importlib.util
import itertools
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CHECK = load_module("wave60_exact", HERE / "exact_check.py")
SCAN = load_module("wave60_scan", HERE / "invariant_scan.py")
SEARCH = load_module("wave60_search", HERE / "constructive_search.py")


class Wave60ExactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.census = CHECK.component_census()
        cls.scan = SCAN.scan()

    def test_component_census(self) -> None:
        self.assertEqual(
            self.census["raw_coordinate_normalized_count"], 216
        )
        self.assertEqual(self.census["accepted_labelled_count"], 50)
        self.assertEqual(
            self.census["accepted_labelled_C4_distribution"],
            {"2": 6, "4": 30, "6": 14},
        )
        self.assertEqual(self.census["fibre_preserving_type_count"], 18)

    def test_component_representatives(self) -> None:
        codes = []
        for record in self.census["types"]:
            adjacency = CHECK.decode_component(
                int(record["canonical_code_hex"], 16)
            )
            self.assertTrue(CHECK.connected(adjacency))
            self.assertEqual(CHECK.triangle_count(adjacency), 0)
            self.assertTrue(CHECK.codegree_cap_passes(adjacency))
            self.assertEqual(set(map(len, adjacency)), {3})
            codes.append(record["canonical_code_hex"])
        self.assertEqual(len(codes), len(set(codes)))

    def test_f2_scan_and_safe_orbits(self) -> None:
        self.assertEqual(self.scan["triple_count"], 1140)
        self.assertEqual(self.scan["survivor_count"], 1140)
        self.assertEqual(self.scan["rejected_count"], 0)
        self.assertEqual(
            self.scan["target_gram_rank_F2_distribution"],
            {"14": 67, "16": 415, "18": 412, "20": 185, "22": 51, "24": 10},
        )
        self.assertEqual(
            self.scan["safe_triple_orbit_reduction"]["orbit_count"], 275
        )
        actions = self.scan["simultaneous_fibre_permutation_action"]
        self.assertEqual(len(actions), 6)
        for action in actions:
            self.assertEqual(
                sorted(action["type_mapping"]), list(range(18))
            )

    def test_candidate_availability_formula(self) -> None:
        summary = self.scan["available_distinct_column_count"]
        self.assertEqual(summary["minimum"], 15936)
        self.assertEqual(summary["maximum"], 27200)
        self.assertEqual(summary["zero_candidate_triples"], 0)
        self.assertEqual(summary["aligned_type_4_triple"], 20928)

    def test_aligned_type_four_enumeration(self) -> None:
        record = self.census["types"][4]
        adjacency = CHECK.union_core((record, record, record))
        gram = CHECK.gram_target(adjacency)
        candidates, summary = CHECK.candidate_columns(adjacency, gram)
        self.assertEqual(len(candidates), 20928)
        self.assertEqual(summary["component_pattern_count"], 21)
        self.assertEqual(summary["rejected_mixed_cut"], 0)
        for component in range(3):
            vertices = [
                CHECK.global_vertex(component, local)
                for local in range(12)
            ]
            self.assertEqual(
                sum(
                    gram[left][right]
                    for left, right in itertools.combinations(vertices, 2)
                ),
                60,
            )
            self.assertEqual(
                {
                    sum(
                        gram[vertex][other]
                        for other in vertices
                        if other != vertex
                    )
                    for vertex in vertices
                },
                {10},
            )

    def test_symmetric_pattern_ledgers(self) -> None:
        for x_aaa in (0, 6, 12):
            slots, groups = SEARCH.build_slots(x_aaa)
            self.assertEqual(len(slots), 60)
            for component in range(3):
                self.assertEqual(
                    {key: len(value) for key, value in groups[component].items()},
                    {
                        ("A", 0): 4,
                        ("A", 1): 4,
                        ("A", 2): 4,
                        ("B", 0): 16,
                        ("B", 1): 16,
                        ("B", 2): 16,
                    },
                )

    def test_design_checker_rejects_short_selection(self) -> None:
        record = self.census["types"][4]
        adjacency = CHECK.union_core((record, record, record))
        gram = CHECK.gram_target(adjacency)
        candidates, _ = CHECK.candidate_columns(adjacency, gram)
        with self.assertRaisesRegex(AssertionError, "60 columns"):
            CHECK.verify_design(adjacency, candidates, tuple(range(59)))


if __name__ == "__main__":
    unittest.main()
