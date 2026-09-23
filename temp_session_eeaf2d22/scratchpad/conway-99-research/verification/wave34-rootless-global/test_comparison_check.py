#!/usr/bin/env python3
"""Hostile Stage-2 tests for the frozen Wave 34 candidate comparison."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from collections import Counter
from itertools import combinations
from math import comb
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave34_rootless_candidate_comparison", HERE / "comparison_check.py"
)
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CHECK
SPEC.loader.exec_module(CHECK)


class FrozenInputTests(unittest.TestCase):
    def test_candidate_release_and_both_manifests_match(self) -> None:
        result = CHECK.validate_provenance()
        self.assertTrue(result["all_released_bytes_match"], result["released_mismatches"])
        self.assertTrue(result["candidate_input_freeze_matches"])
        self.assertTrue(result["candidate_artifact_manifest_matches"])
        self.assertEqual(result["candidate_artifact_manifest_entries"], 5)
        self.assertEqual(result["released_entry_count"], 8)

    def test_stage1_precomparison_is_still_byte_exact(self) -> None:
        result = CHECK.validate_provenance()
        self.assertTrue(result["precomparison_all_match"], result["precomparison_mismatches"])
        self.assertEqual(result["precomparison_entries"], 7)
        self.assertEqual(
            result["precomparison_manifest_sha256"],
            "27c13fb233af677c1619d571bf73820cddd4451172fdd749ace1c9f65f8f3c8d",
        )

    def test_wave33_input_hash_discrepancy_is_literal_and_reproduced(self) -> None:
        discrepancy = CHECK.candidate_comparison()["provenance_discrepancy"]
        self.assertEqual(
            discrepancy["candidate_claimed_hash"],
            "8b7b27fd67f12bb82c60eb27c72a62c913d06f2d86f3eb626dcddd6ac75afeb",
        )
        self.assertEqual(
            discrepancy["stage1_frozen_hash"],
            "8b7b27fd67f12bb82cb6eebf645d0c46324d7227e51bdeb0093fbcdf9d753872",
        )
        self.assertFalse(discrepancy["hashes_match"])
        self.assertTrue(discrepancy["candidate_report_repeats_claimed_hash"])

    def test_verifier_does_not_import_candidate_checker(self) -> None:
        audit = CHECK.static_candidate_audit()
        self.assertFalse(audit["candidate_checker_imported_or_executed_by_verifier_module"])
        self.assertTrue(audit["candidate_tests_import_candidate_checker"])
        self.assertFalse(audit["random_module_used"])
        self.assertTrue(audit["scope_markers_present"])


class FactorAndFibreTests(unittest.TestCase):
    def test_factorization_partitions_k12(self) -> None:
        factors = CHECK.independent_factorization()
        self.assertEqual(len(factors), 11)
        self.assertTrue(all(len(factor) == 6 for factor in factors))
        edges = [edge for factor in factors for edge in factor]
        self.assertEqual(len(edges), comb(12, 2))
        self.assertEqual(len(set(edges)), comb(12, 2))

    def test_partner_maps_are_fixed_point_free_involutions(self) -> None:
        for partner in CHECK.partner_maps():
            self.assertEqual(sorted(partner), list(range(12)))
            for vertex, mate in enumerate(partner):
                self.assertNotEqual(vertex, mate)
                self.assertEqual(partner[mate], vertex)

    def test_candidate_sigma_has_ten_fixed_labels(self) -> None:
        sigma = CHECK.control_sigma(CHECK.load_control())
        self.assertEqual(CHECK.fixed_labels(sigma), tuple(range(2, 12)))
        self.assertEqual(12 - len(CHECK.fixed_labels(sigma)), 2)

    def test_candidate_factor_multiplicities(self) -> None:
        sigma = CHECK.control_sigma(CHECK.load_control())
        self.assertEqual(
            CHECK.fixed_pair_multiplicities((0, 1, 2), sigma),
            {0: 33, 1: 12, 2: 0, 3: 0},
        )

    def test_repeated_factor_hostile_control_has_triple_overlaps(self) -> None:
        sigma = CHECK.control_sigma(CHECK.load_control())
        self.assertEqual(
            CHECK.fixed_pair_multiplicities((0, 0, 0), sigma),
            {0: 41, 1: 0, 2: 0, 3: 4},
        )

    def test_restricted_factor_scan_counts_and_scope(self) -> None:
        scan = CHECK.restricted_factor_scan()
        self.assertEqual(
            scan,
            {
                "triples_checked": 1331,
                "cap_feasible": 1300,
                "cap_and_no_double_overlap_feasible": 1000,
            },
        )
        self.assertEqual(scan["triples_checked"], 11**3)


class LemmaAndEndpointTests(unittest.TestCase):
    def test_relation_degree_formula(self) -> None:
        for q in [0, *range(2, 13)]:
            degrees = CHECK.relation_degrees(q)
            self.assertEqual(
                degrees,
                {
                    "R0": 20 + q,
                    "R1": 180 - 3 * q,
                    "R2": 3 * q,
                    "R3": 12 - q,
                },
            )
            self.assertEqual(sum(degrees.values()), 212)

    def test_endpoint_counts(self) -> None:
        endpoint = CHECK.endpoint_arithmetic()
        self.assertEqual(endpoint["sum_q"], 472)
        self.assertEqual(endpoint["R3_degree_sum"], 2300)
        self.assertEqual(endpoint["R3_edge_count"], 1150)
        self.assertEqual(endpoint["R3_triangle_cap"], 383)
        self.assertEqual(endpoint["central_triple_overlap_cap"], 1149)

    def test_mixed_trace_counts_both_orientations(self) -> None:
        self.assertEqual(CHECK.single_motif_trace(), 2)

    def test_hostile_one_orientation_trace_is_one(self) -> None:
        directed_r2 = [[0, 1, 0], [0, 0, 0], [0, 0, 0]]
        r3 = [[0, 0, 1], [0, 0, 1], [1, 1, 0]]
        trace = CHECK.matrix_trace(
            CHECK.matrix_multiply(
                directed_r2,
                CHECK.matrix_multiply(r3, r3),
            )
        )
        self.assertEqual(trace, 1)

    def test_r3_gram_kernel_and_uniqueness(self) -> None:
        result = CHECK.r3_triangle_gram()
        self.assertEqual(result["kernel_check"], [0, 0, 0])
        gram = result["gram"]
        self.assertEqual(gram[0][0] * gram[1][1] - gram[0][1] ** 2, 12)
        self.assertTrue(
            result["marked_row_injectivity"]["distinct_rows_cannot_equal"]
        )
        self.assertLess(
            result["marked_row_injectivity"][
                "maximum_disjoint_off_diagonal_entry"
            ],
            result["marked_row_injectivity"]["diagonal_entry"],
        )

    def test_hostile_off_diagonal_minus_one_loses_dependency(self) -> None:
        hostile = [[4 if i == j else -1 for j in range(3)] for i in range(3)]
        self.assertEqual(CHECK.gram_times_vector(hostile, [1, 1, 1]), [2, 2, 2])


class PartialControlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.control = CHECK.load_control()
        cls.sigma = CHECK.control_sigma(cls.control)
        cls.indices = tuple(
            cls.control["within_fibre_matching_rule"]["factor_indices_for_X0_X1_X2"]
        )
        cls.core = CHECK.build_core(cls.indices, cls.sigma)
        cls.extended = CHECK.extend_from_certificate(cls.core, cls.control)
        cls.analysis = CHECK.local_control_analysis()

    def test_core_and_extended_counts(self) -> None:
        self.assertEqual((len(self.core), CHECK.edge_count(self.core)), (39, 93))
        self.assertEqual((len(self.extended), CHECK.edge_count(self.extended)), (45, 129))

    def test_completed_core_edges_have_exact_lambda(self) -> None:
        self.assertEqual(self.analysis["core_lambda_failures_after_completion"], [])

    def test_base_to_completion_nonedges_have_exact_mu(self) -> None:
        self.assertEqual(self.analysis["base_completion_mu_failures"], [])

    def test_current_upper_caps_and_central_motif(self) -> None:
        self.assertEqual(self.analysis["current_upper_cap_findings"], [])
        self.assertEqual(self.analysis["central_motif_closures"], [])

    def test_completion_pair_scope_split(self) -> None:
        self.assertEqual(
            self.analysis["completion_pair_common_core_histogram"],
            {"0": 1, "1": 5, "2": 9},
        )
        self.assertEqual(self.analysis["completion_pairs_forced_nonadjacent_now"], 9)
        self.assertEqual(self.analysis["completion_pairs_still_edge_undecided"], 6)

    def test_new_completion_edges_have_only_partial_lambda_support(self) -> None:
        self.assertEqual(
            self.analysis["completion_to_core_edge_lambda_histogram"],
            {"0": 24, "1": 12},
        )
        self.assertEqual(
            self.analysis["completion_to_core_nonedge_common_histogram"],
            {"0": 95, "1": 74, "2": 29},
        )

    def test_literal_45_vertex_graph_is_not_target_graph(self) -> None:
        hostile = self.analysis["as_full_45_vertex_graph"]
        self.assertFalse(hostile["is_target_graph"])
        self.assertEqual(
            hostile["degree_histogram"],
            {"4": 18, "5": 5, "6": 14, "7": 5, "14": 3},
        )
        self.assertEqual(hostile["vertices_failing_degree_14"], 42)
        self.assertEqual(hostile["lambda_failures"], 24)
        self.assertEqual(hostile["lambda_failure_common_count_histogram"], {"0": 24})
        self.assertEqual(hostile["mu_failures"], 713)
        self.assertEqual(
            hostile["mu_failure_common_count_histogram"],
            {"0": 368, "1": 345},
        )

    def test_completion_candidate_counts_and_dfs(self) -> None:
        search = self.analysis["completion_search"]
        self.assertTrue(search["found"])
        self.assertEqual(search["backtracking_nodes"], 31)
        self.assertEqual(
            search["candidate_counts"],
            {
                "x0_0|x1_0": 2345,
                "x0_0|x2_1": 2353,
                "x0_1|x1_1": 2346,
                "x0_1|x2_0": 2346,
                "x1_0|x2_0": 2346,
                "x1_1|x2_1": 2353,
            },
        )
        self.assertTrue(self.analysis["certificate_neighbourhoods_match_search_witness"])

    def test_removing_one_completion_incidence_breaks_required_mu(self) -> None:
        mutated = CHECK.copy_graph(self.extended)
        completion = sorted(self.control["completion_vertices"])[0]
        fibre_zero_neighbour = next(
            vertex for vertex in mutated[completion] if vertex.startswith("x0_")
        )
        mutated[completion].remove(fibre_zero_neighbour)
        mutated[fibre_zero_neighbour].remove(completion)
        self.assertEqual(CHECK.common_count(mutated, CHECK.t(0), completion), 1)

    def test_adding_a_forced_completion_edge_breaks_lambda_cap(self) -> None:
        completions = sorted(self.control["completion_vertices"])
        forced_pair = next(
            (u, v)
            for u, v in combinations(completions, 2)
            if CHECK.common_count(self.extended, u, v) == 2
        )
        mutated = CHECK.copy_graph(self.extended)
        CHECK.add_edge(mutated, *forced_pair)
        finding_pairs = {
            tuple(row["pair"]) for row in CHECK.cap_findings(mutated)
        }
        self.assertIn(tuple(sorted(forced_pair)), finding_pairs)


class IntegratedVerdictTests(unittest.TestCase):
    def test_every_scoped_candidate_claim_reproduces(self) -> None:
        comparison = CHECK.candidate_comparison()
        self.assertTrue(
            comparison["all_scoped_mathematical_and_control_claims_reproduce"],
            comparison["agreements"],
        )
        self.assertTrue(all(comparison["agreements"].values()))

    def test_stage1_stronger_results_remain_compatible(self) -> None:
        stronger = CHECK.candidate_comparison()["stage1_stronger_results_not_contradicted"]
        self.assertEqual(stronger["q_not_equal_1"], "DERIVED")
        self.assertEqual(
            stronger["all_relation_codegree_caps"],
            {"Gamma": 0, "R0": 5, "R1": 1, "R2": 1, "R3": 1},
        )
        self.assertEqual(stronger["R0_wedge_lower"], 6860)
        self.assertEqual(stronger["R3_four_cycle_lower"], 3041)

    def test_global_status_wall_is_preserved(self) -> None:
        result = CHECK.build_results()
        self.assertEqual(
            result["verdict"],
            "PASS_SCOPED_WITH_NONBLOCKING_PROVENANCE_AND_SCOPE_QUALIFIERS",
        )
        for key in (
            "actual_motif_forcing",
            "rootless_endpoint",
            "n3_708",
            "Conway_99",
            "novelty",
        ):
            self.assertEqual(result["status"][key], "UNKNOWN")
        self.assertEqual(result["status"]["candidate_input_provenance"], "FAIL_ONE_HASH")


if __name__ == "__main__":
    unittest.main()
