#!/usr/bin/env python3
"""Focused regression tests for the repaired Wave 13 computation lane."""

from __future__ import annotations

import copy
import itertools
import json
import unittest
from collections import Counter
from pathlib import Path

import wave13_n3_45_active_sat as SAT
import wave13_n3_45_profiles as PROFILES


ROOT = Path(__file__).resolve().parents[1]
ATTEMPTS = ROOT / "attempts" / "wave13-computation"
CANDIDATE_PATH = ATTEMPTS / "n3-45-no-common-point-m5-111.json"
SCAN_PATH = ATTEMPTS / "n3-45-active-local-sat-scan.json"
CENSUS_PATH = ATTEMPTS / "n3-45-local-census.json"
EXPECTED_POSITIVE_CNF_SHA256 = (
    "8260378538dccf0b3b3355619ceb237d7d6f89e1f3b26d86ea316f7e593df146"
)
EXPECTED_POSITIVE_CORE_SHA256 = (
    "2492601fb4dbb6dd642d73e34404f446ff8d0f1cee6edfaec7babbba39424e03"
)
EXPECTED_SCAN_FORMULAS = {
    (1, "111"): (
        13209,
        32224,
        "584e4c7b7f8d366496729dc71da3bbb207e7344fee3d9f59a59fe99fd064580d",
    ),
    (3, "111"): (
        15467,
        338785,
        "445366fc33eccbf5f86daedf6d3678c1cf64cb753f97991a7534157f018f90e0",
    ),
    (3, "122"): (
        15467,
        338792,
        "6eaabc69cae2c83f33b5f8851287527dfdbf6e9616805a74c15b399ee9c41df9",
    ),
    (5, "111"): (
        328475,
        1142251,
        "613726bf378c1c3d78abdca387e4dbdb686309b228fa3f73ca621d9a77564f34",
    ),
    (5, "122"): (
        328475,
        1142258,
        "687abee000cf9e3603ac71c1f13fc3544e8afe1af87af443b307cfbc59bd6cad",
    ),
    (5, "222"): (
        328475,
        1142262,
        "a22446e091fcd382b6089da239a5f1a5d9a7a6a048788c91ea69edaa49e329fd",
    ),
    (5, "223"): (
        328475,
        1142266,
        "b34c9a5b18f78dd3ed9d232fd150808978bea9a60d12402a2d2e151d7bbf3395",
    ),
    (7, "111"): (
        330247,
        1145795,
        "c66c51e9c27bd16a47f3c523923a4c8f84f7359b91d8495ed7140dcf3658a174",
    ),
    (7, "122"): (
        330247,
        1145802,
        "de43df31f717eedbaa566b8278c827f80e4d952fe2e72abaeb1ff0a6ec283e32",
    ),
    (7, "222"): (
        330247,
        1145806,
        "e00aaef09785d119aec27499d642437387c3e2e445c9dd19aef5e7ca2b3ddeff",
    ),
    (7, "223"): (
        330247,
        1145810,
        "ba13ba49f105d7cf2ea51ee00b68e1612f2c001c8f7a810751397a61ff0ea99f",
    ),
    (9, "111"): (
        332003,
        1149307,
        "ab5bf8a6caebd6b8b22d4e19248c884d84695436f12141cbcaab221cbba6a4a7",
    ),
    (9, "122"): (
        332003,
        1149314,
        "d7934da69aa58fe545363e7e70039f281dfcad5fbf75840e18ce873695b1ed1c",
    ),
    (9, "222"): (
        332003,
        1149318,
        "5a6ee86c4ac0354814098dd0061a59b84a42b719de1e6dcdca315369544ff8a1",
    ),
    (9, "223"): (
        332003,
        1149322,
        "de887573e63a96ec7c74b392e5f0c5a6c138c71f9f7132924fd73940ca9e075a",
    ),
    (11, "222"): (
        333743,
        1152798,
        "7d03e957abf1d2b8993a0cd7c41337b3a05abceaa9b3565947360d0c6ecf40b2",
    ),
    (11, "223"): (
        333743,
        1152802,
        "6f73c69537a1cfd57dff985a083efa4d547db1da20c8d592951babc3ff11c6a5",
    ),
}


def load_candidate() -> dict[str, object]:
    return json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))


def refresh_integrity(candidate: dict[str, object]) -> None:
    candidate["integrity_sha256"] = SAT.sha256_bytes(
        SAT.canonical_json_bytes(SAT.candidate_integrity_payload(candidate))
    )


def refresh_diagnostic_hashes(candidate: dict[str, object]) -> None:
    points = tuple(frozenset(item) for item in candidate["point_sets"])
    k_edges = frozenset(tuple(item) for item in candidate["K_edges"])
    candidate["diagnostics"] = SAT.weakened_assignment_diagnostics(
        points, k_edges
    )
    candidate["core_semantic_sha256"] = SAT.sha256_bytes(
        SAT.canonical_json_bytes(SAT.candidate_core_semantic(candidate))
    )
    refresh_integrity(candidate)


class Wave13ProfileTests(unittest.TestCase):
    def test_nine_profiles_and_two_final_arithmetic_frontiers(self) -> None:
        self.assertEqual(len(PROFILES.active_q_profiles()), 9)
        rows = PROFILES.profile_table()
        self.assertEqual(
            sum(row["survives_no_singleton_degree_filter"] for row in rows),
            3,
        )
        self.assertEqual(
            sum(row["survives_degree_three_obstruction"] for row in rows),
            2,
        )

    def test_large_point_flowers_have_no_degree_survivor(self) -> None:
        result = PROFILES.audit()
        flowers = result["flower_censuses"]
        self.assertEqual(
            {
                key: value["statistics"]["capacity_feasible"]
                for key, value in flowers.items()
            },
            {
                "order15_size5": 1,
                "order15_size4": 157,
                "order14_size4": 45,
            },
        )
        self.assertTrue(
            all(
                value["statistics"].get("k_degree_survivors", 0) == 0
                for value in flowers.values()
            )
        )

    def test_mixed_order14_checks_all_seven_ordered_q3_assignments(self) -> None:
        result = PROFILES.mixed_order14_reduction()
        expected = tuple(
            values
            for values in itertools.product((2, 3), repeat=3)
            if 3 in values
        )
        observed = tuple(
            tuple(values)
            for values in result["q3_containing_assignments_checked"]
        )
        self.assertEqual(result["q3_containing_assignment_count"], 7)
        self.assertEqual(observed, expected)
        self.assertIn((2, 3, 3), observed)
        self.assertIn((3, 2, 3), observed)
        self.assertIn((3, 3, 2), observed)
        self.assertIn((3, 3, 3), observed)
        self.assertEqual(
            {
                tuple(row["q_values"]): row["mode_count"]
                for row in result["q3_containing_mode_census"]
            },
            {assignment: 0 for assignment in expected},
        )
        self.assertEqual(result["size_three_branch_survivors"], 0)
        self.assertEqual(result["profile_survivors"], 0)
        self.assertTrue(result["all_size_two_branch"]["contradiction"])
        self.assertEqual(
            result["all_size_two_branch"]["forced_K_degree_lower_bound"],
            5,
        )
        self.assertEqual(
            result["small_cubic_census"][6][
                "labeled_triangle_free_cubic"
            ],
            10,
        )

    def test_four_order15_root_modes_and_59_signatures(self) -> None:
        modes = PROFILES.size_three_local_modes(15, (2, 2, 2))
        self.assertEqual(
            {tuple(sorted(mode["t_values"])) for mode in modes},
            {(1, 1, 1), (1, 2, 2), (2, 2, 2), (2, 2, 3)},
        )
        signatures = PROFILES.all_q2_incidence_signatures()
        self.assertEqual(len(signatures), 59)
        self.assertEqual(
            Counter(row["size3_points"] for row in signatures),
            Counter({1: 2, 3: 7, 5: 16, 7: 21, 9: 12, 11: 1}),
        )

    def test_census_is_bound_to_current_source_and_its_digest(self) -> None:
        census = json.loads(CENSUS_PATH.read_text(encoding="utf-8"))
        self.assertEqual(
            census["builder_source_sha256"], PROFILES.source_sha256()
        )
        self.assertEqual(census["claim_label"], "CANDIDATE")
        self.assertEqual(census["target_result"], "UNKNOWN")
        self.assertEqual(census["novelty_status"], "UNKNOWN")
        semantic_sha256 = census.pop("semantic_sha256")
        self.assertEqual(
            semantic_sha256,
            PROFILES.sha256_bytes(PROFILES.canonical_json_bytes(census)),
        )


class Wave13SatArtifactTests(unittest.TestCase):
    def test_scan_preserves_formula_hashes_and_unverified_boundary(self) -> None:
        scan = json.loads(SCAN_PATH.read_text(encoding="utf-8"))
        self.assertEqual(scan["branch_count"], 17)
        self.assertEqual(
            tuple(tuple(row) for row in scan["branch_cover"]),
            SAT.SCAN_BRANCHES,
        )
        self.assertEqual(
            scan["status"], "COMPLETE_BRANCH_COVER_UNSAT_UNVERIFIED"
        )
        self.assertEqual(scan["claim_label"], "CANDIDATE")
        self.assertEqual(scan["target_result"], "UNKNOWN")
        self.assertEqual(scan["novelty_status"], "UNKNOWN")
        self.assertEqual(scan["proof_trace_status"], "NOT_EMITTED")
        self.assertEqual(scan["builder_source_sha256"], SAT.source_sha256())
        observed = {}
        for row in scan["branches"]:
            self.assertEqual(row["status"], "UNSAT_UNVERIFIED")
            self.assertEqual(row["proof_trace_status"], "NOT_EMITTED")
            statistics = row["statistics"]
            observed[(row["size3_point_count"], row["root_mode"])] = (
                statistics["variables"],
                statistics["clauses"],
                statistics["cnf_sha256"],
            )
        self.assertEqual(observed, EXPECTED_SCAN_FORMULAS)

        semantic = {
            "schema": scan["schema"],
            "status": scan["status"],
            "branch_cover": scan["branch_cover"],
            "branches": [
                {
                    "size3_point_count": row["size3_point_count"],
                    "root_mode": row["root_mode"],
                    "status": row["status"],
                    "proof_trace_status": row["proof_trace_status"],
                    "variables": row["statistics"]["variables"],
                    "clauses": row["statistics"]["clauses"],
                    "cnf_sha256": row["statistics"]["cnf_sha256"],
                }
                for row in scan["branches"]
            ],
            "proof_trace_status": scan["proof_trace_status"],
            "builder_source_sha256": scan["builder_source_sha256"],
            "claim_label": scan["claim_label"],
            "target_result": scan["target_result"],
            "novelty_status": scan["novelty_status"],
        }
        self.assertEqual(
            scan["semantic_sha256"],
            SAT.sha256_bytes(SAT.canonical_json_bytes(semantic)),
        )

    def test_positive_formula_and_candidate_replay_exactly(self) -> None:
        candidate = load_candidate()
        result = SAT.validate_weakened_candidate(candidate)
        self.assertEqual(
            result["status"], "PASS weakened active-local diagnostic"
        )
        self.assertEqual(result["omitted_premise_violation_count"], 18)
        self.assertEqual(result["cnf_sha256"], EXPECTED_POSITIVE_CNF_SHA256)
        self.assertEqual(
            result["core_semantic_sha256"],
            EXPECTED_POSITIVE_CORE_SHA256,
        )
        cnf, pool, *_rest = SAT.build_instance(
            5, "111", "no_common_point"
        )
        self.assertEqual(
            SAT.cnf_sha256(cnf, pool.top), EXPECTED_POSITIVE_CNF_SHA256
        )
        self.assertEqual(
            candidate["solver_statistics"]["cnf_sha256"],
            EXPECTED_POSITIVE_CNF_SHA256,
        )
        self.assertEqual(
            candidate["builder_source_sha256"], SAT.source_sha256()
        )

    def test_positive_artifact_is_byte_and_digest_reproducible(self) -> None:
        first_status, _first_statistics, first = SAT.solve(
            5, "111", 300_000, "cadical195", "no_common_point"
        )
        second_status, _second_statistics, second = SAT.solve(
            5, "111", 300_000, "cadical195", "no_common_point"
        )
        self.assertEqual(first_status, "SAT_WEAKENED_MODEL")
        self.assertEqual(second_status, first_status)
        self.assertIsNotNone(first)
        self.assertIsNotNone(second)
        first_bytes = SAT.candidate_json_bytes(first)
        self.assertEqual(first_bytes, SAT.candidate_json_bytes(second))
        self.assertEqual(first_bytes, CANDIDATE_PATH.read_bytes())
        self.assertEqual(
            first["integrity_sha256"],
            SAT.sha256_bytes(
                SAT.canonical_json_bytes(
                    SAT.candidate_integrity_payload(first)
                )
            ),
        )

    def test_integrity_payload_binds_every_strict_schema_field(self) -> None:
        candidate = load_candidate()
        payload = SAT.candidate_integrity_payload(candidate)
        self.assertEqual(
            set(payload),
            set(SAT.DIAGNOSTIC_CANDIDATE_KEYS)
            - {"integrity_sha256"},
        )
        self.assertEqual(
            candidate["integrity_sha256"],
            SAT.sha256_bytes(SAT.canonical_json_bytes(payload)),
        )
        mutated = copy.deepcopy(candidate)
        mutated["root_mode"] = "122"
        self.assertNotEqual(
            candidate["integrity_sha256"],
            SAT.sha256_bytes(
                SAT.canonical_json_bytes(
                    SAT.candidate_integrity_payload(mutated)
                )
            ),
        )

    def test_audit_mutations_are_rejected_even_with_refreshed_integrity(
        self,
    ) -> None:
        candidate = load_candidate()
        mutations = {
            "active_order": lambda item: item.__setitem__(
                "active_order", 14
            ),
            "K_degree": lambda item: item.__setitem__("K_degree", 7),
            "size3_count": lambda item: item.__setitem__(
                "size3_point_count", 7
            ),
            "root_mode": lambda item: (
                item.__setitem__("root_mode", "122"),
                item["root_normalization"].__setitem__(
                    "local_mode", "122"
                ),
            ),
            "root_normalization": lambda item: item[
                "root_normalization"
            ].__setitem__("point", [0, 1, 3]),
            "restrictions": lambda item: item["restrictions"].append(
                "forged_restriction"
            ),
            "omitted_premise": lambda item: item.__setitem__(
                "omitted_premise", "forged premise"
            ),
            "claim_label": lambda item: item.__setitem__(
                "claim_label", "VERIFIED"
            ),
            "target_result": lambda item: item.__setitem__(
                "target_result", "COUNTEREXAMPLE"
            ),
            "novelty_status": lambda item: item.__setitem__(
                "novelty_status", "NEW"
            ),
            "proof_trace_status": lambda item: item.__setitem__(
                "proof_trace_status", "CHECKED"
            ),
            "cnf_sha256": lambda item: item["solver_statistics"].__setitem__(
                "cnf_sha256", "0" * 64
            ),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                forged = copy.deepcopy(candidate)
                mutate(forged)
                refresh_integrity(forged)
                with self.assertRaises(AssertionError):
                    SAT.validate_weakened_candidate(forged)

    def test_raw_duplicate_noncanonical_and_unknown_records_are_rejected(
        self,
    ) -> None:
        candidate = load_candidate()
        cases = {}

        removed_edge = copy.deepcopy(candidate)
        removed_edge["K_edges"].pop()
        refresh_diagnostic_hashes(removed_edge)
        cases["removed K edge"] = removed_edge

        duplicate_edge = copy.deepcopy(candidate)
        duplicate_edge["K_edges"].append(
            copy.deepcopy(duplicate_edge["K_edges"][0])
        )
        duplicate_edge["K_edges"].sort()
        refresh_integrity(duplicate_edge)
        cases["duplicate K edge"] = duplicate_edge

        reversed_edge = copy.deepcopy(candidate)
        reversed_edge["K_edges"][0].reverse()
        refresh_integrity(reversed_edge)
        cases["reversed K edge"] = reversed_edge

        duplicate_point = copy.deepcopy(candidate)
        duplicate_point["point_sets"].append(
            copy.deepcopy(duplicate_point["point_sets"][0])
        )
        duplicate_point["point_sets"].sort(key=lambda item: (len(item), item))
        refresh_integrity(duplicate_point)
        cases["duplicate point"] = duplicate_point

        reversed_point = copy.deepcopy(candidate)
        reversed_point["point_sets"][0].reverse()
        refresh_integrity(reversed_point)
        cases["reversed point"] = reversed_point

        unknown_top = copy.deepcopy(candidate)
        unknown_top["unknown"] = True
        cases["unknown top field"] = unknown_top

        unknown_root = copy.deepcopy(candidate)
        unknown_root["root_normalization"]["unknown"] = True
        refresh_integrity(unknown_root)
        cases["unknown root field"] = unknown_root

        unknown_solver = copy.deepcopy(candidate)
        unknown_solver["solver_statistics"]["unknown"] = True
        refresh_integrity(unknown_solver)
        cases["unknown solver field"] = unknown_solver

        unknown_diagnostics = copy.deepcopy(candidate)
        unknown_diagnostics["diagnostics"]["unknown"] = True
        refresh_integrity(unknown_diagnostics)
        cases["unknown diagnostics field"] = unknown_diagnostics

        altered_diagnostic = copy.deepcopy(candidate)
        altered_diagnostic["diagnostics"][
            "common_point_Berge_triangle_count"
        ] += 1
        altered_diagnostic["core_semantic_sha256"] = SAT.sha256_bytes(
            SAT.canonical_json_bytes(
                SAT.candidate_core_semantic(altered_diagnostic)
            )
        )
        refresh_integrity(altered_diagnostic)
        cases["altered diagnostic count"] = altered_diagnostic

        for name, forged in cases.items():
            with self.subTest(name=name):
                with self.assertRaises(AssertionError):
                    SAT.validate_weakened_candidate(forged)

    def test_relabelled_core_is_rejected_after_all_hashes_are_refreshed(
        self,
    ) -> None:
        candidate = load_candidate()
        permutation = {0: 3, 3: 0}

        def relabel(vertex: int) -> int:
            return permutation.get(vertex, vertex)

        candidate["point_sets"] = sorted(
            (
                sorted(relabel(vertex) for vertex in point)
                for point in candidate["point_sets"]
            ),
            key=lambda item: (len(item), item),
        )
        candidate["K_edges"] = sorted(
            (
                sorted((relabel(left), relabel(right)))
                for left, right in candidate["K_edges"]
            )
        )
        refresh_diagnostic_hashes(candidate)
        with self.assertRaisesRegex(
            AssertionError, "normalized root point is absent"
        ):
            SAT.validate_weakened_candidate(candidate)


if __name__ == "__main__":
    unittest.main()
