from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("independent_verify.py")
SPEC = importlib.util.spec_from_file_location("wave105_independent_verify", MODULE_PATH)
assert SPEC and SPEC.loader
VERIFY = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = VERIFY
SPEC.loader.exec_module(VERIFY)


class Wave105IndependentVerificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = VERIFY.verify_all()

    def test_frozen_discovery_provenance(self) -> None:
        provenance = self.result["provenance"]
        self.assertEqual(
            provenance["discovery_manifest_sha256"],
            "b0fd40eda5a3677d4a835788cea20dfcb9bb3c5764719fc04536893f1b5da4a1",
        )
        self.assertEqual(provenance["discovery_files_checked"], 11)
        self.assertEqual(len(provenance["frozen_inputs_checked"]), 4)

    def test_motif_and_forced_incidence(self) -> None:
        motif = self.result["motif"]
        self.assertEqual(motif["vertices"], 12)
        self.assertEqual(motif["edges"], 24)
        self.assertEqual(motif["degrees"], [4])
        self.assertEqual(
            motif["residual_pair_capacity_histogram"],
            {"0": 42, "1": 12, "2": 12},
        )
        self.assertTrue(motif["positive_residual_support_triangle_free"])
        forced = self.result["forced_outside_incidence"]
        self.assertEqual(forced["type_counts"], {"X0": 3, "X1": 48, "X2": 36})
        self.assertEqual(forced["incidences"], 120)
        self.assertEqual(forced["pair_incidences"], 36)
        self.assertTrue(forced["top_left_block_equation_checked"])

    def test_block_equations_and_type_edges(self) -> None:
        self.assertEqual(self.result["block_equations"]["linear_rhs_entries"], 1044)
        rows = self.result["outside_type_edges"]["rows_by_t_eX0"]
        self.assertEqual(
            rows["0"],
            {"00": 0, "01": 12, "02": 30, "11": 156, "12": 300, "22": 51},
        )
        self.assertEqual(
            rows["3"],
            {"00": 3, "01": 0, "02": 36, "11": 168, "12": 288, "22": 54},
        )
        self.assertTrue(all(sum(row.values()) == 549 for row in rows.values()))

    def test_exact_moment_and_graphical_census(self) -> None:
        census = self.result["moment_census"]
        self.assertEqual(census["counts_by_t"], {"0": 18, "1": 11, "2": 5, "3": 1})
        self.assertEqual(
            census["six_graphical_filter_counts_by_t"],
            {"0": 18, "1": 11, "2": 4, "3": 1},
        )
        self.assertEqual(len(census["rejected_rows"]), 1)
        rejection = census["rejected_rows"][0]
        self.assertEqual(rejection["branch_eX0"], 2)
        self.assertEqual(
            rejection["six_type_graphical_tests"],
            [True, False, True, True, True, True],
        )

    def test_linear_witness_is_only_linear(self) -> None:
        witness = self.result["linear_witness"]
        self.assertEqual(witness["outside_edges"], 549)
        self.assertEqual(witness["degree_histogram"], {12: 36, 13: 48, 14: 3})
        self.assertEqual(witness["dp_entries_checked"], 1044)
        self.assertEqual(witness["distinct_dp_incidence_rows"], 1044)
        self.assertEqual(witness["archived_constraint_rows"], 1134)
        self.assertEqual(
            witness["upper_triangle_sha256"],
            "feb948f5d0095b4baaba139fddda02b6ededcb7898e0d1ead3d2c251c6786fde",
        )
        self.assertEqual(witness["outside_pair_equation_failures"], 2525)
        self.assertTrue(witness["linear_layer_feasible"])
        self.assertFalse(witness["full_extension_witness"])

    def test_sat_domain_and_branch_coverage(self) -> None:
        audit = self.result["sat_encoding_audit"]
        self.assertTrue(audit["conditional_domain_complete"])
        self.assertTrue(audit["no_target_graph_automorphism_assumed"])
        self.assertEqual(
            audit["counts"],
            {
                "edge_variables": 3741,
                "common_conjunction_variables": 317985,
                "total_variables": 321726,
            },
        )
        coverage = audit["branch_coverage"]
        self.assertEqual(coverage["labelled_x0_graphs_checked"], 8)
        self.assertEqual(coverage["isomorphism_branches"], [0, 1, 2, 3])
        self.assertEqual(
            coverage["labelled_assignments_by_branch"],
            {"0": 1, "1": 3, "2": 3, "3": 1},
        )
        self.assertTrue(coverage["complete_up_to_permuting_three_identical_X0_rows"])

    def test_source_encoding_and_fail_closed_status(self) -> None:
        source = self.result["sat_encoding_audit"]["source_audit"]
        self.assertTrue(source["and_gate_truth_table_complete"])
        self.assertTrue(all(source["fragment_checks"].values()))
        self.assertTrue(all(source["exact_cardinality_checks"].values()))
        status = self.result["status_wall"]
        self.assertEqual(status["linear_layer"], "FEASIBLE")
        self.assertEqual(status["motif_extension"], "UNKNOWN")
        self.assertEqual(status["Conway_99"], "UNKNOWN")
        self.assertFalse(status["motif_excluded"])
        self.assertFalse(status["global_construction"])
        self.assertFalse(status["global_nonexistence_proof"])

    def test_raw_bounded_runs_remain_unknown(self) -> None:
        bounded = self.result["bounded_runs"]
        self.assertTrue(bounded["raw_logs_available"])
        self.assertEqual(
            [row["branch_eX0"] for row in bounded["runs"]],
            [0, 1, 2, 3],
        )
        self.assertTrue(
            all(row["result"] == "UNKNOWN_TIMEOUT" for row in bounded["runs"])
        )
        self.assertTrue(
            all(row["claim_label"] == "UNKNOWN" for row in bounded["runs"])
        )


if __name__ == "__main__":
    unittest.main()
