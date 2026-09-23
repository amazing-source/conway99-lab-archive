#!/usr/bin/env python3
"""Tests for the independent Wave 102 verifier."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).with_name("independent_verify.py")
SPEC = importlib.util.spec_from_file_location("wave102_verify", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)


class Wave102VerifierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = VERIFY.build_independent_result()

    def test_distinct_prism_overlap_is_at_most_four(self) -> None:
        overlap = self.result["pair_overlap"]
        self.assertEqual(overlap["maximum_distinct_prism_overlap"], 4)
        self.assertGreater(
            overlap["rows"][4]["lambda_mu_cap_compatible_pairs"], 0
        )
        self.assertEqual(
            overlap["rows"][5]["lambda_mu_cap_compatible_pairs"], 0
        )
        self.assertEqual(
            overlap["rows"][6]["lambda_mu_cap_compatible_pairs"], 0
        )

    def test_three_prism_O2_is_locally_impossible(self) -> None:
        gluing = self.result["three_prism_gluing"]
        self.assertEqual(gluing["profile_count_with_O_at_most_2"], 11)
        self.assertEqual(gluing["O2_survivor_count"], 0)

    def test_three_prism_O0_is_rook_graph(self) -> None:
        gluing = self.result["three_prism_gluing"]
        self.assertEqual(gluing["O0_labelled_survivor_count"], 36)
        self.assertEqual(
            gluing["O0_motif_certificate"]["degree_multiset"], [4] * 9
        )
        self.assertEqual(
            gluing["O0_motif_certificate"]["induced_prism_count"], 6
        )

    def test_small_P_parity_defects(self) -> None:
        parity = self.result["parity_defect"]
        self.assertEqual(parity["P1_exact_O"], 6)
        self.assertEqual(parity["P2_minimum_O_from_overlap"], 4)
        self.assertEqual(
            parity["P3_minimum_O_from_exhaustive_gluing"], 4
        )

    def test_refined_inequality_and_antipodal_rounding(self) -> None:
        parity = self.result["parity_defect"]
        self.assertEqual(
            parity["refined_inequality"],
            "7*N14 <= 55440 - 5*n3 - O/2",
        )
        self.assertEqual(
            parity["antipodal_rounding"],
            "N14 <= 2*floor((55440 - 5*n3 - O/2)/14)",
        )

    def test_incidence_factorization_and_ranks(self) -> None:
        code = self.result["incidence_code"]
        self.assertEqual(code["factorization"], "f mod 2 = B*D*1 over F2")
        self.assertEqual(code["BBT"], "B*B^T = I + A over F2")
        self.assertEqual(code["rank_A_mod2"], 54)
        self.assertEqual(code["rank_I_plus_A_mod2"], 45)

    def test_triangle_parity_check_weight_candidates(self) -> None:
        code = self.result["incidence_code"]
        self.assertEqual(
            code["kernel_triangle_parity_check_weight_candidates"],
            [36, 40, 44, 48, 52, 56, 60],
        )
        self.assertEqual(
            code["constant_one_triangle_check_weight_candidates"],
            [39, 43, 47, 51, 55, 59, 63, 99],
        )
        self.assertIn("necessary", code["weight_scope"])

    def test_rook_box_local_caps_saturate(self) -> None:
        motif = self.result["P3_rook_null_branch"]
        self.assertEqual(motif["parameters"], [9, 4, 1, 2])
        self.assertEqual(motif["cross_edge_count"], 90)
        self.assertEqual(motif["outside_vertex_count"], 90)
        self.assertEqual(motif["quotient_eigenvalues"], [14, 3])

    def test_no_global_extension_claim(self) -> None:
        motif = self.result["P3_rook_null_branch"]
        self.assertTrue(
            motif["global_extension_status"].startswith("UNKNOWN")
        )

    def test_four_prism_C4_box_K3_null_motif(self) -> None:
        motif = self.result["four_prism_C4_box_K3_null_motif"]
        self.assertEqual(motif["vertices"], 12)
        self.assertEqual(motif["edges"], 24)
        self.assertEqual(motif["induced_prism_count"], 4)
        self.assertEqual(motif["prisms_through_each_vertex"], [2])
        self.assertEqual(
            motif["maximum_internal_common_neighbors_adjacent"], 1
        )
        self.assertEqual(
            motif["maximum_internal_common_neighbors_nonadjacent"], 2
        )
        self.assertTrue(
            motif["global_extension_status"].startswith("UNKNOWN")
        )


if __name__ == "__main__":
    unittest.main()
