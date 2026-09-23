#!/usr/bin/env python3
"""Tests for the m=30 rectangle-identity audit."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "rectangle_probe", HERE / "rectangle_identity_probe.py"
)
assert SPEC is not None and SPEC.loader is not None
PROBE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = PROBE
SPEC.loader.exec_module(PROBE)


class RectangleIdentityTests(unittest.TestCase):
    def test_inputs(self) -> None:
        self.assertEqual(PROBE.authenticate(), PROBE.INPUTS)

    def test_hostile_F(self) -> None:
        edges = PROBE.generalized_petersen_10_2()
        self.assertEqual(len(edges), 30)
        self.assertEqual(PROBE.degree_sequence(20, edges), (3,) * 20)
        self.assertEqual(PROBE.triangle_count(edges, 20), 0)

    def test_hostile_R_has_coarse_candidate_properties(self) -> None:
        edges = PROBE.generalized_petersen_10_2()
        cycle = PROBE.disjoint_edge_hamilton_cycle(edges)
        self.assertEqual(len(cycle), 30)
        self.assertEqual(len(set(cycle)), 30)
        self.assertTrue(all(
            set(edges[cycle[index]]).isdisjoint(edges[cycle[(index + 1) % 30]])
            for index in range(30)
        ))

    def test_coarse_pair_fails_exact_rectangle_identity(self) -> None:
        result = PROBE.build_results()
        hostile = result["hostile_coarse_pair"]
        self.assertTrue(hostile["F_connected_cubic_triangle_free"])
        self.assertTrue(hostile["R_simple_spanning_2factor"])
        self.assertTrue(hostile["R_disjoint_from_line_graph_F"])
        self.assertEqual(hostile["rectangle_identity"], "FAIL")
        self.assertTrue(
            any(key not in ("0", "2") for key in hostile["off_diagonal_value_counts"])
        )

    def test_zero_crossing_Z_is_excluded_from_identity(self) -> None:
        derivation = " ".join(PROBE.build_results()["first_principles_derivation"])
        self.assertIn("Z edges have zero crossing", derivation)
        self.assertIn("do not occur in A_R", derivation)

    def test_mod2_cycle_nullity_formula(self) -> None:
        for partition in PROBE.cycle_partitions(30):
            direct = 30 - PROBE.gf2_rank(PROBE.cycle_adjacency(partition))
            self.assertEqual(PROBE.cycle_nullity(partition), direct)

    def test_mod2_rank_reduces_abstract_cycle_types(self) -> None:
        result = PROBE.mod2_cycle_restriction()
        self.assertEqual(
            result["surviving_cycle_partition_count_by_F_component_count"],
            {"1": 147, "2": 263, "3": 323},
        )
        self.assertEqual(
            result["universally_excluded_cycle_partitions"],
            [
                [3, 27], [5, 25], [7, 23], [9, 21],
                [11, 19], [13, 17], [15, 15], [30],
            ],
        )

    def test_status_does_not_close(self) -> None:
        status = PROBE.build_results()["status_boundary"]
        self.assertEqual(status["conditional_n3_60"], "UNKNOWN_FINITE_RESIDUAL")
        self.assertEqual(status["conway_99_target"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
