"""Hostile tests for the independent Wave 17 n3=54 structural audit."""

from __future__ import annotations

from fractions import Fraction
import importlib.util
from pathlib import Path
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave17_n3_54_independent_check",
    HERE / "independent_check.py",
)
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class ProvenanceAndStatusTests(unittest.TestCase):
    def test_all_frozen_hashes(self) -> None:
        self.assertEqual(
            CHECK.verify_provenance(),
            CHECK.EXPECTED_HASHES,
        )

    def test_status_boundary_is_conservative(self) -> None:
        self.assertTrue(all(CHECK.status_boundary().values()))
        result = CHECK.build_result()
        self.assertEqual(
            result["conditional_n3_54_exclusion"], "UNKNOWN"
        )
        self.assertEqual(result["conway_99"], "UNKNOWN")
        self.assertEqual(result["novelty"], "UNKNOWN")


class ProfileAndDegreeTests(unittest.TestCase):
    def test_independent_profile_census(self) -> None:
        self.assertEqual(len(CHECK.profiles_sum_36()), 23)
        self.assertEqual(
            CHECK.residual_profiles(), CHECK.EXPECTED_RESIDUALS
        )

    def test_q4_profile_cannot_be_silently_deleted(self) -> None:
        residuals = CHECK.residual_profiles()
        q4 = (17, (2,) * 16 + (4,))
        self.assertIn(q4, residuals)
        self.assertEqual(
            len([row for row in residuals if max(row[1]) <= 3]),
            len(residuals) - 1,
        )

    def test_endpoint_crossing_scope(self) -> None:
        self.assertEqual(
            CHECK.two_sided_crossing_counts(1, 4), (0,)
        )
        self.assertEqual(
            CHECK.two_sided_crossing_counts(2, 4), (0, 4)
        )

    def test_global_H_degree_mutation_is_rejected(self) -> None:
        self.assertIn(
            6, CHECK.two_sided_crossing_counts(3, 3)
        )

    def test_size_two_q4_types(self) -> None:
        for pair, expected in {
            (2, 2): 2,
            (2, 4): 3,
            (3, 3): 3,
            (4, 4): 4,
        }.items():
            self.assertEqual(
                CHECK.size_two_support(*pair)["support_neighbors"],
                expected,
            )
        for pair in ((2, 3), (3, 4)):
            self.assertFalse(
                CHECK.size_two_support(*pair)["compatible"]
            )

    def test_no_point_size_cap_is_needed(self) -> None:
        for point_size in range(3, 8):
            self.assertGreaterEqual(2 * point_size, 6)
        self.assertNotEqual(
            CHECK.size_two_support(2, 4)["support_neighbors"],
            2,
        )

    def test_spectral_equality_and_equitable_cut_arithmetic(self) -> None:
        equality = CHECK.equality_arithmetic()
        self.assertEqual(
            equality["twice_edges_lower"],
            equality["twice_edges_upper"],
        )
        self.assertEqual(equality["edges"], 81)
        self.assertEqual(
            equality["indicator_principal_coefficient"],
            Fraction(3, 11),
        )
        self.assertEqual(equality["Ax_constant"], 3)
        self.assertEqual(
            equality["cut_edge_count_both_sides"], (216, 216)
        )


class PointGraphAndMatrixTests(unittest.TestCase):
    def test_cubic_triangle_free_examples(self) -> None:
        for order, edges in (
            (6, CHECK.k33_edges()),
            (8, CHECK.cube_edges()),
            (10, CHECK.petersen_edges()),
        ):
            self.assertTrue(
                all(
                    len(row) == 3
                    for row in CHECK.neighbors(order, edges)
                )
            )
            self.assertTrue(CHECK.is_triangle_free(order, edges))

    def test_no_codegree_two_is_essential(self) -> None:
        self.assertFalse(
            CHECK.has_nonadjacent_codegree_two(
                6, CHECK.k33_edges()
            )
        )
        self.assertTrue(
            CHECK.has_nonadjacent_codegree_two(
                8, CHECK.cube_edges()
            )
        )
        self.assertFalse(
            CHECK.has_nonadjacent_codegree_two(
                10, CHECK.petersen_edges()
            )
        )

    def test_four_cycle_closure(self) -> None:
        self.assertTrue(
            CHECK.four_cycle_closures_are_k33(
                6, CHECK.k33_edges()
            )
        )
        self.assertFalse(
            CHECK.four_cycle_closures_are_k33(
                8, CHECK.cube_edges()
            )
        )
        self.assertEqual(
            CHECK.allowed_component_order_partitions(),
            ((18,), (6, 12), (6, 6, 6)),
        )

    def test_line_graph_and_support_neighbors_are_distinct(self) -> None:
        result = CHECK.k33_line_plus_disjoint_cycle()
        self.assertEqual(result["line_degrees"], (4,) * 9)
        self.assertEqual(result["R_degrees"], (2,) * 9)
        self.assertEqual(result["union_degrees"], (6,) * 9)
        self.assertTrue(result["edge_disjoint"])
        self.assertTrue(result["R_pairs_are_disjoint_F_edges"])

    def test_full_matrix_scope_includes_diagonal(self) -> None:
        scope = CHECK.matrix_scope_checks()
        self.assertEqual(scope["independent_pair_entry"], 2)
        self.assertTrue(scope["diagonal_zero_for_disjoint_R"])
        self.assertTrue(scope["F_edge_entries_zero"])
        self.assertEqual(scope["adjacent_R_mutation_diagonal"], 2)

    def test_matrix_identity_does_not_supply_matching(self) -> None:
        scope = CHECK.matrix_scope_checks()
        self.assertEqual(
            scope["identity_does_not_imply_matching_entry"], 2
        )
        self.assertTrue(scope["identity_does_not_imply_matching"])


class ParityRankSurfaceMomentTests(unittest.TestCase):
    def test_three_K33_human_parity_witness(self) -> None:
        parity = CHECK.parity_witness_for_k33_block()
        self.assertEqual(
            parity["forced_cross_component_edge_counts"],
            (9, 9, 9),
        )
        self.assertTrue(
            parity["all_entry_parity_is_constraint_combination"]
        )
        self.assertTrue(parity["parity_contradiction"])

    def test_graph_incidence_ranks(self) -> None:
        binary = CHECK.binary_rank_checks()
        self.assertEqual(binary["K33_incidence_rank"], 5)
        self.assertEqual(binary["Petersen_incidence_rank"], 9)
        self.assertEqual(
            binary["component_lower_bounds"],
            {
                1: {"c_R_min": 4, "adjacency_nullity_min": 7},
                2: {"c_R_min": 3, "adjacency_nullity_min": 5},
            },
        )

    def test_cycle_adjacency_nullities(self) -> None:
        for length in range(3, 28):
            self.assertEqual(
                CHECK.cycle_adjacency_nullity(length),
                1 if length % 2 else 2,
            )

    def test_surface_vertex_link_and_mutation(self) -> None:
        surface = CHECK.surface_checks()
        self.assertTrue(surface["correct_link_is_circle"])
        self.assertTrue(surface["deleted_corner_breaks_link"])
        self.assertEqual(
            surface["six_edge_side_graph_cycle_partitions"],
            ((6,),),
        )
        self.assertEqual(surface["euler_characteristic"], -9)
        self.assertTrue(surface["nonorientable_component_forced"])
        self.assertFalse(surface["orientable_total_would_be_even"])

    def test_triangle_types_and_moments(self) -> None:
        for c in range(10):
            row = CHECK.triangle_moments(c)
            self.assertEqual(row["total_triangles"], 231)
            self.assertEqual(row["inactive_count"], 213)
            self.assertEqual(row["inactive_first_moment"], 270)
            self.assertEqual(row["inactive_second_moment"], 756)
            self.assertEqual(row["all_triangle_second_moment"], 918)
            self.assertEqual(
                row["outside_triples_with_R_edge"]
                + row["outside_triples_independent"],
                72,
            )

    def test_all_precommitted_mutations_are_detected(self) -> None:
        mutations = CHECK.build_result()["hostile_mutations"]
        self.assertEqual(len(mutations), 9)
        self.assertTrue(all(mutations.values()))


if __name__ == "__main__":
    unittest.main(verbosity=2)
