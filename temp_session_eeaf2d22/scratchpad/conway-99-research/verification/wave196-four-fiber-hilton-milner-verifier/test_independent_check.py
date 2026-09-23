from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave196_independent", HERE / "independent_check.py"
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Wave196IndependentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.math = MODULE.build_math_result()
        cls.results = MODULE.build_results()

    def test_frozen_math_replay(self) -> None:
        expected = json.loads(
            (HERE / "independent-math-result.json").read_text(encoding="utf-8")
        )
        self.assertEqual(self.math, expected)

    def test_local_two_star_types(self) -> None:
        local = self.math["local_two_star_types"]
        self.assertEqual(local["pair_types"], 21)
        self.assertEqual(local["vertices_per_type"], 4)
        self.assertEqual(local["total_nonneighbors"], 84)

    def test_flag_leaf_types(self) -> None:
        flag = self.math["flag_leaf_types"]
        self.assertEqual(flag["model_leaf_types"], [[0, 1], [0, 2], [1, 2]])
        self.assertIn("6-cycle", flag["incidence_graph"])

    def test_hilton_milner_equality_templates(self) -> None:
        hm = self.math["hilton_milner_equality"]
        self.assertFalse(hm["family_search_performed"])
        self.assertEqual(len(hm["templates"]), 2)
        for template in hm["templates"]:
            self.assertEqual(template["size"], 13)
            self.assertEqual(len(template["degree_five_pairs"]), 3)
            self.assertTrue(template["pairwise_intersecting"])
            self.assertTrue(template["empty_total_intersection"])

    def test_nontrivial_family_cap(self) -> None:
        nontrivial = self.math["nontrivial_family"]
        self.assertEqual(nontrivial["conclusion"], "j_x<=39-3=36")

    def test_common_block_injection(self) -> None:
        common = self.math["common_block_family"]
        self.assertEqual(common["c_x_upper"], 12)
        self.assertEqual(common["j_x_upper"], "j_x<=3c_x<=36")
        self.assertIn("uniquely determines", common["flag_injection"])

    def test_full_flag_pool_and_orientations(self) -> None:
        pool = self.math["flag_pools_and_orientations"]
        self.assertEqual(set(pool["flag_pools"]), {"selected", "old", "new"})
        self.assertEqual(pool["upper"], "J=sum_x j_x<=99*36=3564=6C/7")
        self.assertFalse(pool["orientation_directions_changed_from_wave195"])

    def test_coefficient_certificate(self) -> None:
        cert = self.math["coefficient_certificate"]
        self.assertEqual(cert["exact_nonedge_projective_lower"], 7029)
        self.assertEqual(cert["equivalent_target"], "Q0-(11C-3564)/6")

    def test_integral_null_is_arithmetic_only(self) -> None:
        null = self.math["integral_null"]
        self.assertEqual(null["Q0"], 7029)
        self.assertTrue(null["integral_at_C_4158"])
        self.assertFalse(null["asserted_to_be_graph_code_cover_or_flag_family"])
        self.assertTrue(
            all(value == 0 for value in null["zero_certificate_slacks"].values())
        )

    def test_integrity_and_pre_source_separation(self) -> None:
        integrity = self.results["integrity"]
        self.assertTrue(integrity["passed"])
        self.assertFalse(integrity["primary_opened_before_independent_freeze"])
        self.assertFalse(
            integrity["primary_checker_imported_or_executed_before_independent_freeze"]
        )

    def test_primary_comparison(self) -> None:
        comparison = self.results["source_comparison"]
        self.assertTrue(comparison["four_vertices_per_two_block_type_matches"])
        self.assertTrue(comparison["coefficient_identity_matches"])
        self.assertTrue(comparison["source_integer_null_replayed"])

    def test_hostile_proof_b_cross_check(self) -> None:
        proof_b = self.results["hostile_proof_b_comparison"]
        self.assertEqual(proof_b["verdict"], "ACCEPT")
        self.assertFalse(proof_b["used_as_mathematical_premise"])
        self.assertTrue(proof_b["unknown_boundary_preserved"])

    def test_verdict_and_boundary(self) -> None:
        self.assertEqual(self.results["verdict"], "VERIFIED_WITH_SCOPE")
        boundary = self.results["boundary"]
        self.assertTrue(boundary["conditional_theorem_verified"])
        self.assertEqual(boundary["conway_99"], "UNKNOWN")
        self.assertFalse(boundary["rank_11_excluded"])
        self.assertFalse(boundary["endpoint_excluded"])


if __name__ == "__main__":
    unittest.main()
