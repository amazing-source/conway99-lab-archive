from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave102_exact_check", HERE / "exact_check.py"
)
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class Wave102ExactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = CHECK.exact_result()

    def test_archived_result(self) -> None:
        archived = json.loads(
            (HERE / "exact-results.json").read_text(encoding="utf-8")
        )
        self.assertEqual(archived, self.result)

    def test_binary_adjacency_and_triangle_code_ranks(self) -> None:
        code = self.result["theorems"]["binary_incidence_code"]
        self.assertEqual(code["rank_F2_A"], 54)
        self.assertEqual(code["rank_F2_I_plus_A"], 45)
        self.assertEqual(code["rank_F2_B_range"], [45, 99])
        self.assertEqual(code["dimension_C0_range"], [44, 98])

    def test_prism_incidence_factors_through_triangle_boundary(self) -> None:
        code = self.result["theorems"]["binary_incidence_code"]
        self.assertIn("H=B*D", code["prism_factorization"])
        self.assertIn("lies in C0", code["parity_vector"])
        self.assertIn("odd-degree boundary", code["cycle_space_boundary"])

    def test_triangle_parity_checks_are_global(self) -> None:
        code = self.result["theorems"]["binary_incidence_code"]
        check = code["triangle_even_check_support"]
        self.assertEqual(check["induced_degree_on_support"], 7)
        self.assertEqual(check["nonzero_weight_range"], [36, 60])
        self.assertEqual(code["dual_minimum_distance_lower_bound"], 36)

    def test_vector_refined_floor_identity(self) -> None:
        bound = self.result["theorems"]["vector_refined_N14_bound"]
        self.assertEqual(
            bound["exact_floor_sum_identity"],
            "sum_v floor(5*f_v/2)=15P-O/2",
        )
        self.assertIn("-O/2", bound["refined_incidence_inequality"])

    def test_one_prism_strictly_improves_wave100(self) -> None:
        row = self.result["theorems"]["vector_refined_N14_bound"][
            "low_prism_rows"
        ]["P=1_exact_O=6"]
        self.assertEqual(row["n3"], 4155)
        self.assertEqual(row["O"], 6)
        self.assertEqual(row["N14_even_upper"], 4950)

    def test_odd_root_count_must_be_even(self) -> None:
        with self.assertRaises(AssertionError):
            CHECK.refined_n14_bound(4155, 5)

    def test_distinct_prisms_cannot_share_five_vertices(self) -> None:
        overlap = self.result["theorems"]["distinct_prism_overlap"]
        self.assertEqual(
            overlap["maximum_intersection_of_distinct_prism_supports"], 4
        )
        self.assertEqual(
            overlap["overlap_five_cap_compatible_gluings"], 0
        )
        self.assertGreater(
            overlap["overlap_four_cap_compatible_gluings"], 0
        )

    def test_two_prisms_force_four_odd_roots(self) -> None:
        row = self.result["theorems"]["vector_refined_N14_bound"][
            "low_prism_rows"
        ]["P=2_O_at_least_4"]
        self.assertEqual(row["O"], 4)
        self.assertEqual(row["seven_N14_refined_numerator"], 34678)

    def test_three_prism_even_branch_forces_rook_and_six_prisms(self) -> None:
        branch = self.result["theorems"]["three_prism_parity_branch"]
        self.assertEqual(branch["labelled_cap_compatible_unions"], 36)
        self.assertTrue(branch["all_unions_isomorphic_to_rook_3_by_3"])
        self.assertEqual(branch["induced_prisms_forced_inside_union"], [6])
        self.assertIn("cannot vanish", branch["consequence_for_total_P_3"])

    def test_rook_branch_is_spectrally_compatible(self) -> None:
        branch = self.result["theorems"]["three_prism_parity_branch"]
        self.assertEqual(branch["equitable_quotient"], [[4, 10], [1, 13]])
        self.assertEqual(branch["quotient_eigenvalues"], [14, 3])

    def test_four_prism_parity_cancellation_control(self) -> None:
        control = self.result["controls_and_boundaries"][
            "four_prism_parity_cancellation"
        ]
        self.assertEqual(control["induced_prisms"], 4)
        self.assertEqual(control["prisms_through_each_motif_vertex"], [2])
        self.assertEqual(control["rooted_parity_vector_on_motif"], "zero")
        self.assertEqual(
            control["maximum_internal_common_neighbors_adjacent"], 1
        )
        self.assertEqual(
            control["maximum_internal_common_neighbors_nonadjacent"], 2
        )

    def test_adjacency_polynomial_boundary(self) -> None:
        boundary = self.result["controls_and_boundaries"][
            "ordinary_adjacency_polynomials"
        ]
        self.assertEqual(
            boundary["ordinary_polynomial_diagonal"],
            "constant on all 99 vertices",
        )
        self.assertIn("incidence tensors", boundary["needed_extension"])

    def test_status_stays_unknown(self) -> None:
        status = self.result["status"]
        self.assertEqual(status["general_strict_n3_upper_bound"], "NOT_PROVED")
        self.assertFalse(status["full_graph_constructed"])
        self.assertEqual(status["Conway_99"], "UNKNOWN")
        self.assertEqual(self.result["claim_label"], "DERIVED")


if __name__ == "__main__":
    unittest.main()
