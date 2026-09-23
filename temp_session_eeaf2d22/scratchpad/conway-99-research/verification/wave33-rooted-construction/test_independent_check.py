#!/usr/bin/env python3
"""Adversarial tests for the precomparison Wave 33 rooted checker."""

from __future__ import annotations

import copy
import io
import json
import unittest
from pathlib import Path

import independent_check as check


HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "precomparison-fixture.json"
RESULTS = HERE / "precomparison-results.json"


class IndependentCheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = check.load_json(FIXTURE)
        cls.result = check.verify_payload(
            cls.payload, input_sha256=check.sha256_path(FIXTURE)
        )

    def mutated(self) -> dict:
        return copy.deepcopy(self.payload)

    def assert_rejected(self, payload: dict, pattern: str | None = None) -> None:
        with self.assertRaises(check.VerificationError) as caught:
            check.verify_payload(payload)
        if pattern is not None:
            self.assertIn(pattern, str(caught.exception))

    def test_01_public_support_reconstruction(self) -> None:
        public = self.result["public_support"]
        self.assertEqual(public["B_row_sums"], {"10": 14})
        self.assertEqual(public["B_column_sums"], {"2": 70})
        self.assertEqual(public["support_block_identity"], "PASS")

    def test_02_fixed_design_exact(self) -> None:
        design = self.result["hostile_partial"]["fixed_design"]
        self.assertEqual(design["block_count"], 70)
        self.assertTrue(design["simple"])
        self.assertEqual(design["point_degree_histogram"], {"14": 15})
        self.assertEqual(design["pair_intersection_histogram"], {"2": 105})

    def test_03_assignment_is_all_seventy_blocks(self) -> None:
        self.assertEqual(
            self.result["search_encoding"]["encoded_block_to_O_bijection_count"],
            str(check.math.factorial(70)),
        )
        self.assertEqual(
            self.result["hostile_partial"]["fixed_design"][
                "canonical_block_set_sha256"
            ],
            self.result["hostile_partial"]["assigned_design"][
                "canonical_block_set_sha256"
            ],
        )

    def test_04_duplicate_assignment_rejected(self) -> None:
        payload = self.mutated()
        payload["hostile_partial"]["assignment"][-1] = 0
        self.assert_rejected(payload, "not a bijection")

    def test_05_assignment_boolean_rejected(self) -> None:
        payload = self.mutated()
        payload["hostile_partial"]["assignment"][0] = False
        self.assert_rejected(payload, "must be an integer")

    def test_06_out_of_domain_point_rejected(self) -> None:
        payload = self.mutated()
        payload["hostile_partial"]["fixed_design_blocks"][0][0] = 15
        self.assert_rejected(payload, "outside 0..14")

    def test_07_repeated_point_in_block_rejected(self) -> None:
        payload = self.mutated()
        payload["hostile_partial"]["fixed_design_blocks"][0][1] = payload[
            "hostile_partial"
        ]["fixed_design_blocks"][0][0]
        self.assert_rejected(payload, "repeats a point")

    def test_08_duplicate_block_rejected(self) -> None:
        payload = self.mutated()
        payload["hostile_partial"]["fixed_design_blocks"][-1] = copy.deepcopy(
            payload["hostile_partial"]["fixed_design_blocks"][0]
        )
        self.assert_rejected(payload, "not simple")

    def test_09_pair_intersection_tamper_rejected(self) -> None:
        payload = self.mutated()
        block = payload["hostile_partial"]["fixed_design_blocks"][0]
        replacement = next(
            q for q in range(15) if q not in block and q not in block[1:]
        )
        block[0] = replacement
        self.assert_rejected(payload)

    def test_10_hostile_f_design_survives_but_balance_fails(self) -> None:
        partial = self.result["hostile_partial"]
        self.assertEqual(partial["F_row_degree_histogram"], {"3": 70})
        self.assertEqual(partial["F_column_degree_histogram"], {"14": 15})
        self.assertEqual(
            partial["assigned_design"]["pair_intersection_histogram"], {"2": 105}
        )
        self.assertGreater(partial["BF"]["violation_count"], 0)
        self.assertEqual(partial["BF"]["status"], "FAIL")

    def test_11_claimed_bf_violation_count_is_recomputed(self) -> None:
        payload = self.mutated()
        payload["hostile_partial"]["expected"]["bf_violation_count"] += 1
        self.assert_rejected(payload, "do not match recomputation")

    def test_12_claimed_bf_squared_defect_is_recomputed(self) -> None:
        payload = self.mutated()
        payload["hostile_partial"]["expected"]["bf_squared_defect"] += 1
        self.assert_rejected(payload, "do not match recomputation")

    def test_13_nonempty_d_rejected_for_hostile_partial(self) -> None:
        payload = self.mutated()
        payload["hostile_partial"]["empty_d_control_edges"] = [[0, 1]]
        self.assert_rejected(payload, "must use empty D")

    def test_14_empty_d_fails_full_graph_identity(self) -> None:
        graph = self.result["hostile_partial"]["empty_D_control_full_graph_check"]
        self.assertFalse(graph["is_conway_graph"])
        self.assertEqual(graph["degree_histogram"], {"5": 70, "14": 29})
        self.assertGreater(graph["identity_violation_count"], 0)

    def test_14b_unsupplied_o_o_layer_is_not_empty_search_restriction(self) -> None:
        partial = self.result["hostile_partial"]
        self.assertEqual(partial["O_O_layer_certificate_status"], "UNSUPPLIED")
        self.assertEqual(partial["empty_D_control_edge_count"], 0)
        self.assertEqual(
            self.result["search_encoding"]["active_O_O_layer_status"],
            "UNSUPPLIED_NO_PRIMAL_FOR_F",
        )

    def test_15_exclusion_status_inflation_rejected(self) -> None:
        payload = self.mutated()
        payload["search_report"]["claimed_exclusion"] = True
        self.assert_rejected(payload, "claimed_exclusion")

    def test_16_global_status_inflation_rejected(self) -> None:
        payload = self.mutated()
        payload["global_status"]["Conway_99"] = "NONEXISTENT"
        self.assert_rejected(payload, "global_status")

    def test_17_partial_graph_status_inflation_rejected(self) -> None:
        payload = self.mutated()
        payload["hostile_partial"]["claimed_full_graph"] = True
        self.assert_rejected(payload, "may not claim a full graph")

    def test_18_scope_inflation_rejected(self) -> None:
        payload = self.mutated()
        payload["search_report"]["scope"] = "ALL_SIMPLE_2_15_3_2_DESIGNS"
        self.assert_rejected(payload, "search_report.scope")

    def test_19_timeout_with_primal_inconsistency_rejected(self) -> None:
        payload = self.mutated()
        payload["search_report"]["primal_found"] = True
        self.assert_rejected(payload, "primal_found")

    def test_20_milp_census_tamper_rejected(self) -> None:
        payload = self.mutated()
        payload["search_report"]["assignment_binary_count"] = 4899
        self.assert_rejected(payload, "assignment_binary_count")

    def test_21_active_phase_status_tamper_rejected(self) -> None:
        payload = self.mutated()
        payload["search_report"]["active_graph_phase_entered"] = True
        self.assert_rejected(payload, "active_graph_phase_entered")

    def test_22_o_label_duplicate_rejected(self) -> None:
        payload = self.mutated()
        payload["o_labels"][-1] = copy.deepcopy(payload["o_labels"][0])
        self.assert_rejected(payload, "duplicates")

    def test_23_cross_incidence_tamper_rejected(self) -> None:
        payload = self.mutated()
        payload["support_cross_incidence"][0][0] ^= 1
        self.assert_rejected(payload, "not canonical")

    def test_24_duplicate_json_key_rejected(self) -> None:
        with self.assertRaises(check.VerificationError):
            json.load(
                io.StringIO('{"schema_version":1,"schema_version":2}'),
                object_pairs_hook=check.no_duplicate_object,
            )

    def test_25_output_is_deterministic(self) -> None:
        first = check.verify_payload(
            copy.deepcopy(self.payload), input_sha256=check.sha256_path(FIXTURE)
        )
        second = check.verify_payload(
            copy.deepcopy(self.payload), input_sha256=check.sha256_path(FIXTURE)
        )
        self.assertEqual(check.canonical_json_bytes(first), check.canonical_json_bytes(second))

    def test_26_frozen_first_results_match_recomputation(self) -> None:
        recorded = check.load_json(RESULTS)
        self.assertEqual(
            check.canonical_json_bytes(recorded),
            check.canonical_json_bytes(self.result),
        )


if __name__ == "__main__":
    unittest.main()
