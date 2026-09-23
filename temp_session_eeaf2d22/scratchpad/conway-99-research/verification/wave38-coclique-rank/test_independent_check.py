#!/usr/bin/env python3
"""Hostile tests for the independent Wave 38 coclique/rank verifier."""

from __future__ import annotations

import copy
import unittest

import independent_check as check


class CocliqueRankVerifierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = check.compute_results()

    def test_local_structure_and_triangle_mate(self) -> None:
        local = check.local_structure()
        self.assertEqual(local["side_size"], 12)
        self.assertEqual(local["local_matching_edges_per_side"], 6)
        self.assertEqual(local["triangle_mate_extra_neighbors_per_side"], 0)
        self.assertEqual(local["cross_relation"], "perfect matching")
        with self.assertRaisesRegex(AssertionError, "triangle mate"):
            check.local_structure(triangle_mate_extra_neighbors=1)

    def test_exhaustive_even_cycle_census(self) -> None:
        census = check.cycle_partition_census()
        self.assertEqual(sum(census.values()), 10_395)
        self.assertEqual(census["24"], 3840)
        self.assertEqual(census["4+4+4+4+4+4"], 1)
        self.assertTrue(
            all(
                all(int(length) % 4 == 0 for length in partition.split("+"))
                for partition in census
            )
        )

    def test_incidence_projector_identity(self) -> None:
        identity = check.check_incidence_identity()
        self.assertEqual(identity["NMNt_eigenvalues"], [0, 0, 63])
        with self.assertRaisesRegex(AssertionError, "tampered"):
            check.check_incidence_identity((27, -8, 1))

    def test_coclique_gram_determinant_and_rank(self) -> None:
        data = check.coclique_rank_data()
        self.assertEqual(data["determinant"], 27**12 * 40)
        self.assertEqual(data["determinant_mod_7"], 5)
        self.assertEqual(data["rank_mod_7"], 13)

    def test_tampered_coclique_size_rejected(self) -> None:
        tampered = copy.deepcopy(self.result)
        tampered["coclique"]["size"] = 12
        with self.assertRaisesRegex(AssertionError, "coclique size"):
            check.validate_results(tampered)

    def test_tampered_residue_rejected(self) -> None:
        tampered = copy.deepcopy(self.result)
        tampered["coclique_gram"]["determinant_mod_7"] = 4
        with self.assertRaisesRegex(AssertionError, "residue"):
            check.validate_results(tampered)
        with self.assertRaisesRegex(AssertionError, "residue"):
            check.coclique_rank_data(residue=4)

    def test_tampered_identity_rejected(self) -> None:
        tampered = copy.deepcopy(self.result)
        tampered["incidence_projector"]["identity"] = "N M N^T = 26I - 9A + J"
        with self.assertRaisesRegex(AssertionError, "identity"):
            check.validate_results(tampered)

    def test_rank_promotion_rejected(self) -> None:
        tampered = copy.deepcopy(self.result)
        tampered["rank_transfer"]["claim_type"] = "EXACT_RANK"
        tampered["rank_transfer"]["rank_F7_M_exact"] = 13
        with self.assertRaisesRegex(AssertionError, "promoted"):
            check.validate_results(tampered)

    def test_endpoint_congruence_and_r3_boundary(self) -> None:
        endpoint = self.result["endpoint"]
        self.assertEqual(endpoint["C_mod_7"], "C=2M")
        self.assertEqual(endpoint["r7_lower_bound"], 13)
        self.assertEqual(endpoint["if_r3_equals_12"]["r7_lower_bound"], 14)
        self.assertEqual(
            endpoint["if_r3_equals_12"]["admissible_r7_values"],
            list(range(14, 45, 2)),
        )
        self.assertEqual(endpoint["admissible_rank_pair_count_after_update"], 528)

    def test_attribution_and_status_inflation_rejected(self) -> None:
        attribution = copy.deepcopy(self.result)
        attribution["attribution"]["novelty_claimed"] = True
        attribution["attribution"]["coclique_prior_public_attribution"] = "VERIFIED_NEW"
        with self.assertRaisesRegex(AssertionError, "inflated"):
            check.validate_results(attribution)

        status = copy.deepcopy(self.result)
        status["status"]["endpoint"] = "EXCLUDED"
        status["status"]["strongest_general_upper_bound_on_n3"] = 4155
        status["status"]["upper_bound_improved_below_4158"] = True
        status["status"]["novelty_status"] = "NEW"
        with self.assertRaisesRegex(AssertionError, "inflated"):
            check.validate_results(status)


if __name__ == "__main__":
    unittest.main()
