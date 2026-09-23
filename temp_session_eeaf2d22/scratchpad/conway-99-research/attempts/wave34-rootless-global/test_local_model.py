from __future__ import annotations

import json
import unittest
from itertools import combinations
from pathlib import Path

import check_local_model as model


EXPECTED_COMPLETION = {
    ("x0_0", "x1_0"): ("x0_0", "x0_1", "x1_0", "x1_3", "x2_2", "x2_5"),
    ("x0_0", "x2_1"): ("x0_0", "x0_2", "x1_3", "x1_4", "x2_1", "x2_7"),
    ("x0_1", "x1_1"): ("x0_1", "x0_2", "x1_1", "x1_3", "x2_4", "x2_6"),
    ("x0_1", "x2_0"): ("x0_1", "x0_3", "x1_2", "x1_4", "x2_0", "x2_1"),
    ("x1_0", "x2_0"): ("x0_2", "x0_3", "x1_0", "x1_1", "x2_0", "x2_5"),
    ("x1_1", "x2_1"): ("x0_4", "x0_5", "x1_1", "x1_2", "x2_1", "x2_6"),
}


class FactorizationTests(unittest.TestCase):
    def test_factorization_is_exact(self) -> None:
        all_edges = [
            edge
            for factor in model.FACTORS
            for edge in factor
        ]
        self.assertEqual(len(all_edges), 66)
        self.assertEqual(len(set(all_edges)), 66)
        self.assertEqual(
            set(all_edges),
            set(combinations(range(model.N), 2)),
        )


class FixedPointCoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.adjacency = model.build_core((0, 0, 0))

    def test_core_size_and_caps(self) -> None:
        self.assertEqual(len(self.adjacency), 39)
        self.assertEqual(sum(map(len, self.adjacency.values())) // 2, 93)
        self.assertEqual(model.cap_findings(self.adjacency), [])

    def test_q2_relation_counts(self) -> None:
        self.assertEqual(len(model.fixed_transversals()), 10)
        self.assertEqual(len(model.moved_cross_edges()), 6)
        self.assertEqual(
            model.fixed_pair_multiplicities((0, 0, 0)),
            {0: 41, 1: 0, 2: 0, 3: 4},
        )

    def test_all_core_edges_except_defects_have_exact_lambda(self) -> None:
        defects = set(model.moved_cross_edges())
        for left, neighbors in self.adjacency.items():
            for right in neighbors:
                if left >= right:
                    continue
                common = len(self.adjacency[left] & self.adjacency[right])
                if model.pair_key(left, right) in defects:
                    self.assertEqual(common, 0)
                else:
                    self.assertEqual(common, 1)


class CompletionLayerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.core = model.build_core(model.COMPLETION_FACTOR_INDICES)
        self.extended = {vertex: set(neighbors) for vertex, neighbors in self.core.items()}
        for index, edge in enumerate(model.moved_cross_edges()):
            y_vertex = f"y{index}"
            self.extended[y_vertex] = set()
            for neighbor in EXPECTED_COMPLETION[edge]:
                model.add_edge(self.extended, y_vertex, neighbor)

    def test_completion_search_reproduces_witness(self) -> None:
        result = model.search_completion_layer(self.core)
        self.assertTrue(result["completion_layer_found"])
        self.assertEqual(result["backtracking_nodes"], 31)
        self.assertEqual(
            result["candidate_counts_by_nonclosed_edge"],
            {
                "x0_0|x1_0": 2345,
                "x0_0|x2_1": 2353,
                "x0_1|x1_1": 2346,
                "x0_1|x2_0": 2346,
                "x1_0|x2_0": 2346,
                "x1_1|x2_1": 2353,
            },
        )

    def test_static_control_certificate_matches(self) -> None:
        certificate_path = Path(__file__).with_name("local-control.json")
        certificate = json.loads(certificate_path.read_text(encoding="utf-8"))
        self.assertEqual(
            certificate["within_fibre_matching_rule"]["factor_indices_for_X0_X1_X2"],
            list(model.COMPLETION_FACTOR_INDICES),
        )
        certified = {
            tuple(value["assigned_nonclosed_edge"]): tuple(value["core_neighbours"])
            for value in certificate["completion_vertices"].values()
        }
        self.assertEqual(certified, EXPECTED_COMPLETION)

    def test_completion_core_has_no_double_or_triple_overlap(self) -> None:
        self.assertEqual(
            model.fixed_pair_multiplicities(model.COMPLETION_FACTOR_INDICES),
            {0: 33, 1: 12, 2: 0, 3: 0},
        )

    def test_extended_counts_and_caps(self) -> None:
        self.assertEqual(len(self.extended), 45)
        self.assertEqual(sum(map(len, self.extended.values())) // 2, 129)
        self.assertEqual(model.cap_findings(self.extended), [])

    def test_every_core_edge_now_has_exact_lambda(self) -> None:
        for left, neighbors in self.core.items():
            for right in neighbors:
                if left >= right:
                    continue
                self.assertEqual(
                    len(self.extended[left] & self.extended[right]),
                    1,
                )

    def test_base_triangle_to_completion_pairs_have_exact_mu(self) -> None:
        y_vertices = sorted(vertex for vertex in self.extended if vertex.startswith("y"))
        for t_index in range(3):
            t_vertex = model.t_vertex(t_index)
            for y_vertex in y_vertices:
                self.assertNotIn(y_vertex, self.extended[t_vertex])
                self.assertEqual(
                    len(self.extended[t_vertex] & self.extended[y_vertex]),
                    2,
                )

    def test_six_R2_triangles_are_closed(self) -> None:
        for index, edge in enumerate(model.moved_cross_edges()):
            y_vertex = f"y{index}"
            left, right = edge
            self.assertIn(right, self.extended[left])
            self.assertIn(y_vertex, self.extended[left])
            self.assertIn(y_vertex, self.extended[right])

    def test_no_known_R2_R3_R3_closure_about_T(self) -> None:
        for index, edge in enumerate(model.moved_cross_edges()):
            r2_triangle = set(edge) | {f"y{index}"}
            for transversal in model.fixed_transversals():
                cross_edges = sum(
                    right in self.extended[left]
                    for left in r2_triangle
                    for right in transversal
                )
                self.assertLess(cross_edges, 3)


if __name__ == "__main__":
    unittest.main()
