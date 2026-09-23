#!/usr/bin/env python3
"""Exact lightweight tests for the Wave 38 all-prism schema and oracle."""

from __future__ import annotations

import copy
import itertools
import unittest

from audit_package import audit
from complete_endpoint import (
    MATCHING_PERMUTATIONS,
    PrismWitness,
    adjacent_pair_lambda_at_most_one,
    build_cut_pool,
    cut_catalog,
    endpoint_refined_cases,
    find_induced_prisms,
    potential_triangles,
    prism_required_edges,
    prism_variable_keys,
    residual_variable_ids,
    rooted_edge_state,
    static_size_inventory,
    triangles_in_graph,
    validate_cut_catalog,
    validate_cut_pool,
)
from root_model import RootModel


def prism_edges() -> set[tuple[int, int]]:
    return set(
        prism_required_edges(
            (0, 1, 2),
            (3, 4, 5),
            (0, 1, 2),
        )
    )


class CompleteEndpointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = RootModel.build(7)

    def test_exact_33_case_cover(self) -> None:
        cases = endpoint_refined_cases(self.root)
        self.assertEqual(len(cases), 33)
        by_parent = {
            parent: [
                case["refined_branch"]
                for case in cases
                if case["parent_branch"] == parent
            ]
            for parent in (4, 5, 8, 10, 12)
        }
        self.assertEqual(
            by_parent,
            {
                4: [15, 16, 17, 18],
                5: [19, 20, 21, 22],
                8: [36, 37, 38, 39, 40, 41],
                10: [50, 51, 52, 53, 54, 55, 56, 57],
                12: [68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78],
            },
        )

    def test_target_triangle_inventory_is_frozen(self) -> None:
        triangles = potential_triangles(self.root)
        self.assertEqual(len(triangles), 96_215)
        result = static_size_inventory(self.root)
        self.assertEqual(
            result["candidate_triangle_variable_edge_histogram"],
            {"0": 7, "1": 924, "3": 95_284},
        )
        self.assertEqual(
            result["candidate_triangle_type_histogram"],
            {
                "coordinate_residual_residual": 924,
                "residual_only": 95_284,
                "root_triangle": 7,
            },
        )
        self.assertEqual(
            result["exact_residual_only_prism_embeddings"],
            24_388_892_640,
        )
        self.assertEqual(
            result["naive_all_triangle_pair_matching_upper"],
            27_771_690_030,
        )

    def test_residual_variable_numbering_matches_lexicographic_block(self) -> None:
        variables = residual_variable_ids()
        self.assertEqual(len(variables), 3_486)
        self.assertEqual(variables[(0, 1)], 1)
        self.assertEqual(variables[(0, 2)], 2)
        self.assertEqual(variables[(82, 83)], 3_486)

    def test_rooted_scaffold_state_classes(self) -> None:
        self.assertIs(rooted_edge_state(self.root, 0, 1), True)
        self.assertIs(rooted_edge_state(self.root, 0, 15), False)
        self.assertIs(rooted_edge_state(self.root, 1, 2), True)
        self.assertIs(rooted_edge_state(self.root, 1, 3), False)
        label = self.root.labels[0]
        self.assertIs(
            rooted_edge_state(self.root, 1 + label[0], 15),
            True,
        )
        absent_coordinate = next(c for c in range(14) if c not in label)
        self.assertIs(
            rooted_edge_state(self.root, 1 + absent_coordinate, 15),
            False,
        )
        self.assertEqual(rooted_edge_state(self.root, 15, 16), (0, 1))

    def test_root_triangle_prisms_reproduce_all_84_endpoint_units(self) -> None:
        indices = self.root.label_index()
        derived = set()
        for pair in range(7):
            left_coordinate = 2 * pair
            right_coordinate = left_coordinate + 1
            first_triangle = (
                0,
                1 + left_coordinate,
                1 + right_coordinate,
            )
            for other in range(14):
                if other in (left_coordinate, right_coordinate):
                    continue
                left_label = indices[tuple(sorted((left_coordinate, other)))]
                right_label = indices[tuple(sorted((right_coordinate, other)))]
                second_triangle = (
                    1 + other,
                    15 + left_label,
                    15 + right_label,
                )
                # Sorted first/second positions match root--other,
                # left-coordinate--left-label, right-coordinate--right-label.
                keys = prism_variable_keys(
                    self.root,
                    first_triangle,
                    second_triangle,
                    (0, 1, 2),
                )
                self.assertIsNotNone(keys)
                self.assertEqual(len(keys), 1)
                derived.add(keys[0])
        self.assertEqual(len(derived), 84)

    def test_prism_oracle_is_induced_and_canonical(self) -> None:
        edges = prism_edges()
        witnesses = find_induced_prisms(6, edges)
        self.assertEqual(len(witnesses), 1)
        self.assertEqual(witnesses[0].vertices, tuple(range(6)))
        self.assertEqual(len(witnesses[0].required_edges), 9)
        self.assertEqual(len(triangles_in_graph(6, edges)), 2)

        # An extra cross edge destroys inducedness.
        self.assertEqual(find_induced_prisms(6, edges | {(0, 4)}), ())

    def test_every_matching_on_two_fixed_triples_is_visited(self) -> None:
        edge_sets = {
            prism_required_edges((0, 1, 2), (3, 4, 5), permutation)
            for permutation in MATCHING_PERMUTATIONS
        }
        self.assertEqual(len(edge_sets), 6)
        self.assertTrue(all(len(edges) == 9 for edges in edge_sets))

    def test_lambda_one_makes_positive_prism_pattern_induced(self) -> None:
        required = prism_edges()
        all_edges = tuple(itertools.combinations(range(6), 2))
        optional = tuple(edge for edge in all_edges if edge not in required)
        surviving = []
        for mask in range(1 << len(optional)):
            edges = set(required)
            edges.update(
                edge
                for index, edge in enumerate(optional)
                if mask & (1 << index)
            )
            if adjacent_pair_lambda_at_most_one(6, edges):
                surviving.append(edges)
        self.assertEqual(surviving, [required])

    def test_cut_catalog_rederives_and_rejects_tampering(self) -> None:
        # Embed a prism entirely among residual full vertices 15..20.
        shifted = {(a + 15, b + 15) for a, b in prism_edges()}
        catalog = cut_catalog(99, shifted, self.root)
        self.assertEqual(catalog["prism_witness_count"], 1)
        self.assertEqual(catalog["deduplicated_cut_count"], 1)
        cuts = validate_cut_catalog(
            catalog,
            self.root,
            candidate_edges=shifted,
            require_complete=True,
        )
        self.assertEqual(len(cuts), 1)
        self.assertEqual(len(cuts[0]), 9)

        altered = copy.deepcopy(catalog)
        altered["entries"][0]["negative_literals"][0] -= 1
        with self.assertRaisesRegex(ValueError, "wrong literals"):
            validate_cut_catalog(altered, self.root)

        omitted = copy.deepcopy(catalog)
        omitted["entries"] = []
        omitted["deduplicated_cut_count"] = 0
        omitted["prism_witness_count"] = 0
        omitted["claim_label"] = "CANDIDATE_PRISM_FREE_ONLY"
        with self.assertRaisesRegex(ValueError, "complete canonical catalog"):
            validate_cut_catalog(
                omitted,
                self.root,
                candidate_edges=shifted,
                require_complete=True,
            )

        bool_alias = copy.deepcopy(catalog)
        bool_alias["entries"][0]["witness"]["triangles"][0][0] = True
        with self.assertRaisesRegex(ValueError, "dimensions are invalid"):
            validate_cut_catalog(bool_alias, self.root)

    def test_cut_pool_is_order_independent_and_deduplicates(self) -> None:
        shifted = {(a + 15, b + 15) for a, b in prism_edges()}
        catalog = cut_catalog(99, shifted, self.root)
        first = build_cut_pool(
            [
                ("b" * 64, catalog),
                ("a" * 64, catalog),
            ],
            self.root,
        )
        second = build_cut_pool(
            [
                ("a" * 64, catalog),
                ("b" * 64, catalog),
            ],
            self.root,
        )
        self.assertEqual(first, second)
        self.assertEqual(first["deduplicated_cut_count"], 1)
        sources = [("a" * 64, catalog), ("b" * 64, catalog)]
        self.assertEqual(
            len(
                validate_cut_pool(
                    first,
                    self.root,
                    source_catalogs=sources,
                    require_sources=True,
                )
            ),
            1,
        )

        forged = copy.deepcopy(first)
        forged["source_catalogs"][0]["sha256"] = "c" * 64
        with self.assertRaisesRegex(
            ValueError,
            "source hashes|canonical merge",
        ):
            validate_cut_pool(
                forged,
                self.root,
                source_catalogs=sources,
                require_sources=True,
            )

    def test_prism_witness_rejects_wrong_matching_via_catalog(self) -> None:
        with self.assertRaisesRegex(ValueError, "perfect matching"):
            PrismWitness(
                triangles=((15, 16, 17), (18, 19, 20)),
                matching=((15, 18), (15, 19), (17, 20)),
            )

    def test_package_artifacts_replay(self) -> None:
        result = audit()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(
            result["checks"],
            {
                "endpoint_refined_case_count": 33,
                "fixture_catalog_byte_identical": True,
                "fixture_exact_cuts": 1,
                "fixture_pool_byte_identical": True,
                "fixture_prism_witnesses": 1,
                "frozen_input_count": 6,
                "static_inventory_byte_identical": True,
            },
        )


if __name__ == "__main__":
    unittest.main()
