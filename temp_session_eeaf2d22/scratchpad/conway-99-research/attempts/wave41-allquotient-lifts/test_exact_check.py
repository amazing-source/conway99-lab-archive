#!/usr/bin/env python3
"""Hostile tests for the Wave 41 all-quotient lift discovery."""

from __future__ import annotations

import importlib.util
import json
import unittest
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave41_allquotient_lifts", HERE / "exact_check.py"
)
assert SPEC and SPEC.loader
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class AllQuotientLiftTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.stored = json.loads((HERE / "exact-results.json").read_text())
        cls.rank_distribution, cls.rank_eleven, cls.extended = (
            CHECK.enumerate_quotients()
        )

    def test_frozen_combinatorics(self) -> None:
        self.assertEqual(len(CHECK.PAIRINGS), 15)
        self.assertEqual(len(CHECK.PERMUTATIONS), 720)
        self.assertEqual(CHECK.MASK_COUNT, 262144)

    def test_normalized_rank_distribution(self) -> None:
        self.assertEqual(
            self.rank_distribution,
            Counter({11: 8, 12: 1, 13: 400, 14: 46, 15: 2616, 16: 979}),
        )
        self.assertEqual(len(self.extended), 4050)

    def test_eight_rank_eleven_cases(self) -> None:
        self.assertEqual(len(self.rank_eleven), 8)
        self.assertEqual(
            [metadata["normalized_index"] for metadata, _ in self.rank_eleven],
            [1446, 1447, 1452, 1453, 1536, 1537, 1542, 1543],
        )

    def test_every_rank_eleven_quotient_has_sixteen_triangles(self) -> None:
        self.assertEqual(
            {len(CHECK.triangle_clauses(quotient)) for _, quotient in self.rank_eleven},
            {16},
        )

    def test_all_eight_are_colour_isomorphic(self) -> None:
        canonical = self.rank_eleven[0][1]
        for _, quotient in self.rank_eleven:
            mapping = CHECK.coloured_quotient_isomorphism(quotient, canonical)
            self.assertEqual(sorted(mapping), list(range(18)))
            self.assertTrue(
                all(
                    {mapping[v] for v in quotient[u]}
                    == set(canonical[mapping[u]])
                    for u in range(18)
                )
            )

    def test_stored_affine_maps_are_bijections(self) -> None:
        cases = self.stored["rank_eleven_boundary"]["all_cases"]
        for case in cases:
            affine = case["affine_mask_transport_to_case_0"]
            self.assertEqual(
                sorted(affine["source_variable_to_target_variable"]),
                list(range(18)),
            )
            self.assertGreaterEqual(affine["constant_mask"], 0)
            self.assertLess(affine["constant_mask"], 2**18)

    def test_affine_transport_on_hostile_masks(self) -> None:
        canonical = self.rank_eleven[0][1]
        canonical_allowed = CHECK.allowed_assignment_bitset(
            CHECK.triangle_clauses(canonical)
        )
        hostile_masks = (0, 1, 2, 3, 51739, 131071, 262143)
        for case, (_, quotient) in zip(
            self.stored["rank_eleven_boundary"]["all_cases"],
            self.rank_eleven,
        ):
            mapping = case["fibre_preserving_isomorphism_to_case_0"]
            affine = case["affine_mask_transport_to_case_0"]
            source_allowed = CHECK.allowed_assignment_bitset(
                CHECK.triangle_clauses(quotient)
            )
            for mask in hostile_masks:
                target = CHECK.transform_mask(
                    mask,
                    affine["constant_mask"],
                    affine["source_variable_to_target_variable"],
                )
                self.assertEqual(
                    (source_allowed >> mask) & 1,
                    (canonical_allowed >> target) & 1,
                )
                relabelled = CHECK.relabel_lift(
                    CHECK.lifted_adjacency(quotient, mask), mapping
                )
                self.assertEqual(
                    CHECK.canonical_mask_from_lift(canonical, relabelled),
                    target,
                )

    def test_common_triangle_free_count(self) -> None:
        cases = self.stored["rank_eleven_boundary"]["all_cases"]
        self.assertEqual(
            {case["triangle_free_mask_count"] for case in cases},
            {37378},
        )

    def test_common_rank_distribution(self) -> None:
        expected = {"33": 264, "34": 7348, "35": 29766}
        for case in self.stored["rank_eleven_boundary"]["all_cases"]:
            self.assertEqual(case["rank_F7_K39_distribution"], expected)
            self.assertEqual(
                sum(case["rank_F7_K39_distribution"].values()), 37378
            )

    def test_all_source_witnesses_are_exact(self) -> None:
        for case, (_, quotient) in zip(
            self.stored["rank_eleven_boundary"]["all_cases"],
            self.rank_eleven,
        ):
            witness = case["canonical_minimum_witness"]
            adjacency = CHECK.lifted_adjacency(quotient, witness["mask"])
            self.assertEqual(CHECK.triangle_count(adjacency), 0)
            self.assertEqual(CHECK.sparse_laplacian_rank(adjacency), 32)
            self.assertEqual(CHECK.dense_laplacian_rank(adjacency), 32)
            self.assertEqual(witness["rank_F7_K39"], 33)

    def test_structural_fibre_star_kernel(self) -> None:
        vectors = CHECK.structural_fibre_star_vectors()
        self.assertEqual(CHECK.matrix_rank(vectors, 7), 3)
        for case, (_, quotient) in zip(
            self.stored["rank_eleven_boundary"]["all_cases"],
            self.rank_eleven,
        ):
            adjacency = CHECK.lifted_adjacency(
                quotient, case["canonical_minimum_witness"]["mask"]
            )
            k39 = CHECK.transported_k39(adjacency)
            self.assertTrue(
                all(
                    CHECK.matrix_vector_product(k39, vector, 7) == (0,) * 39
                    for vector in vectors
                )
            )

    def test_rank33_border_route_is_marked_failed(self) -> None:
        roadblock = self.stored["rank33_border_roadblock"]
        self.assertEqual(roadblock["kernel_dimension_supplied"], 3)
        self.assertIn("rank(H^T U)<=3", roadblock["consequence_at_local_rank_33"])
        self.assertEqual(roadblock["status"], "FAILED_ROUTE")

    def test_full_census_has_no_empty_lift_space(self) -> None:
        counts = [int(record["triangle_free_masks"]) for record in self.extended]
        self.assertEqual(min(counts), 10648)
        self.assertEqual(max(counts), 262144)
        self.assertTrue(all(count > 0 for count in counts))

    def test_nineteen_quotients_have_no_triangle_clause(self) -> None:
        empty = [record for record in self.extended if record["triangles"] == 0]
        self.assertEqual(len(empty), 19)
        self.assertEqual(
            {record["triangle_free_masks"] for record in empty}, {262144}
        )

    def test_extended_rank_twelve_record(self) -> None:
        selected = [record for record in self.extended if record["rank"] == 12]
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0]["triangles"], 24)
        self.assertEqual(selected[0]["triangle_free_masks"], 10648)

    def test_forbidden_clause_removes_exactly_one_eighth(self) -> None:
        clause = (((0, 0), (1, 1), (2, 0)),)
        allowed = CHECK.allowed_assignment_bitset(clause)
        self.assertEqual(allowed.bit_count(), 7 * (2**15))

    def test_bad_block_permutation_is_rejected(self) -> None:
        adjacency = CHECK.empty_adjacency(18)
        with self.assertRaisesRegex(AssertionError, "block permutation"):
            CHECK.add_three_squares(
                adjacency,
                0,
                1,
                CHECK.BASE_PAIRING,
                CHECK.BASE_PAIRING,
                (0, 0, 1),
            )

    def test_scope_wall_is_not_promoted(self) -> None:
        self.assertEqual(self.stored["claim_label"], "CANDIDATE")
        wall = self.stored["status_wall"]
        self.assertEqual(wall["endpoint_n3_4158"], "UNKNOWN")
        self.assertEqual(wall["general_upper_bound_below_4158"], "NOT_PROVED")
        self.assertEqual(wall["graph_or_counterexample"], "NONE")

    def test_conditional_theorem_keeps_all_hypotheses(self) -> None:
        theorem = self.stored["conditional_candidate_theorem"]
        self.assertEqual(len(theorem["assumptions"]), 3)
        self.assertIn("all 693 graph edges", theorem["assumptions"][2])
        self.assertIn("even r7>=34", theorem["statement"])
        self.assertEqual(
            theorem["status"], "CANDIDATE_PENDING_INDEPENDENT_VERIFICATION"
        )


if __name__ == "__main__":
    unittest.main()
