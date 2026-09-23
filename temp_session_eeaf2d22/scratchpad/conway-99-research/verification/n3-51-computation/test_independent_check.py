#!/usr/bin/env python3
"""Regression and hostile-mutation tests for the independent Wave 16 audit."""

from __future__ import annotations

import copy
import json
import unittest

import independent_check as audit


def synchronize_scan_semantic(scan: dict[str, object]) -> None:
    scan["semantic"]["results"] = [
        {
            "profile_id": row["profile_id"],
            "branch_id": row["branch"]["branch_id"],
            "status": row["status"],
            "formula_sha256": row["formula"][
                "materialized_dimacs_sha256"
            ],
            "candidate_file_sha256": row.get("candidate_file_sha256"),
            "candidate_semantic_sha256": row.get(
                "candidate_semantic_sha256"
            ),
        }
        for row in scan["results"]
    ]
    scan["semantic_sha256"] = audit.sha256_bytes(
        audit.canonical_json_bytes(scan["semantic"])
    )


def synchronize_candidate_core(candidate: dict[str, object]) -> None:
    candidate["semantic_core"] = {
        "starting_git_commit": candidate["starting_git_commit"],
        "source_provenance": candidate["source_provenance"],
        "profile_id": candidate["profile_id"],
        "q_values": candidate["q_values"],
        "branch": candidate["branch"],
        "point_sets": candidate["point_sets"],
        "K_edges": candidate["K_edges"],
        "formula_materialized_dimacs_sha256": candidate["formula"][
            "materialized_dimacs_sha256"
        ],
        "encoded_premises_sha256": candidate["formula"][
            "encoded_premises_sha256"
        ],
    }
    candidate["semantic_sha256"] = audit.sha256_bytes(
        audit.canonical_json_bytes(candidate["semantic_core"])
    )


class IndependentAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.profile = audit.read_json(audit.PROFILE_PATH)
        cls.scan = audit.read_json(audit.SCAN_PATH)
        cls.candidate = audit.read_json(audit.CANDIDATE_PATH)
        cls.failures = audit.read_json(audit.FAILURES_PATH)
        cls.result = audit.run_audit()
        cls.cover = cls.result["profile_validation"]["surviving_cover"]
        cls.formula_records = {
            (row["profile_id"], row["branch_id"]): {
                key: row[key]
                for key in (
                    "variable_count",
                    "base_clause_count",
                    "branch_unit_count",
                    "materialized_clause_count",
                    "materialized_dimacs_sha256",
                )
            }
            for row in cls.result["formula_validation"]["records"]
        }

    def test_full_independent_audit(self) -> None:
        self.assertEqual(
            self.result["verdict"],
            "PASS_FOR_CONDITIONAL_ACTIVE_LOCAL_ARCHIVE_ONLY",
        )
        self.assertTrue(
            self.result["formula_validation"][
                "all_streams_exactly_rebuilt"
            ]
        )
        self.assertTrue(
            self.result["candidate_validation"][
                "extends_independently_rebuilt_cnf"
            ]
        )
        self.assertEqual(self.result["target_result"], "UNKNOWN")
        self.assertEqual(
            self.result["conditional_n3_51_exclusion"], "UNKNOWN"
        )
        self.assertEqual(self.result["novelty"], "UNKNOWN")

    def test_exact_counts_and_status_boundaries(self) -> None:
        profile = self.result["profile_validation"]
        self.assertEqual(profile["raw_profile_count"], 16)
        self.assertEqual(profile["surviving_profile_count"], 4)
        self.assertEqual(profile["raw_branch_count"], 16)
        self.assertEqual(profile["surviving_branch_count"], 7)
        self.assertEqual(
            self.result["scan_validation"]["status_histogram"],
            {
                "SAT_CANDIDATE": 1,
                "TIMEOUT_UNKNOWN": 5,
                "UNSAT_UNVERIFIED": 1,
            },
        )
        self.assertFalse(
            self.result["scan_validation"][
                "negative_solver_results_evidentiary"
            ]
        )
        self.assertEqual(
            self.result["failure_validation"][
                "historical_budget_unknown_count"
            ],
            1,
        )

    def test_positive_candidate_reconstruction(self) -> None:
        candidate = self.result["candidate_validation"]
        self.assertEqual(candidate["point_count"], 24)
        self.assertEqual(candidate["size2_point_count"], 24)
        self.assertEqual(candidate["size3_point_count"], 0)
        self.assertEqual(candidate["k_edge_count"], 69)
        self.assertEqual(candidate["meeting_crossings_checked"], 48)

    def test_hostile_mutations(self) -> None:
        rejected: dict[str, str] = {}

        def reject(name: str, callback) -> None:
            try:
                callback()
            except (
                AssertionError,
                KeyError,
                TypeError,
                ValueError,
                StopIteration,
            ) as error:
                rejected[name] = str(error)
            else:
                self.fail(f"hostile mutation was accepted: {name}")

        def guard_candidate(changed: dict[str, object]) -> None:
            audit.validate_candidate_document(changed, self.cover)
            key = (
                str(changed["profile_id"]),
                str(changed["branch"]["branch_id"]),
            )
            expected = self.formula_records[key]
            for field, value in expected.items():
                audit.check(
                    changed["formula"][field] == value,
                    f"candidate formula {field} differs",
                )

        def candidate_mutation(
            name: str,
            mutate,
            *,
            synchronize: bool = False,
        ) -> None:
            changed = copy.deepcopy(self.candidate)
            mutate(changed)
            if synchronize:
                synchronize_candidate_core(changed)
            reject(name, lambda: guard_candidate(changed))

        candidate_mutation(
            "candidate_claim_inflation",
            lambda c: c.__setitem__("claim_label", "VERIFIED"),
        )
        candidate_mutation(
            "candidate_target_inflation",
            lambda c: c.__setitem__("target_result", "NONEXISTENT"),
        )
        candidate_mutation(
            "candidate_conditional_inflation",
            lambda c: c.__setitem__(
                "conditional_n3_51_exclusion", "PROVED"
            ),
        )
        candidate_mutation(
            "candidate_novelty_inflation",
            lambda c: c.__setitem__("novelty", "NEW"),
        )
        candidate_mutation(
            "candidate_scope_inflation",
            lambda c: c.__setitem__("scope", "complete Conway graph"),
        )
        candidate_mutation(
            "candidate_starting_commit",
            lambda c: c.__setitem__("starting_git_commit", "0" * 40),
        )
        candidate_mutation(
            "candidate_source_hash",
            lambda c: c["source_provenance"].__setitem__(
                "code/wave16_n3_51_active_sat.py", "0" * 64
            ),
        )
        candidate_mutation(
            "candidate_encoded_premise_deleted",
            lambda c: c["encoded_premises"].pop(),
        )
        candidate_mutation(
            "candidate_unencoded_premise_deleted",
            lambda c: c["unencoded_premises"].pop(),
        )
        candidate_mutation(
            "candidate_symmetry_forged",
            lambda c: c.__setitem__(
                "symmetry_boundary", "assume a graph automorphism"
            ),
        )
        candidate_mutation(
            "candidate_q_changed",
            lambda c: c["q_values"].__setitem__(0, 3),
        )
        candidate_mutation(
            "candidate_point_duplicated",
            lambda c: c["point_sets"].append(
                copy.deepcopy(c["point_sets"][0])
            ),
        )
        candidate_mutation(
            "candidate_point_deleted",
            lambda c: c["point_sets"].pop(),
        )
        candidate_mutation(
            "candidate_k_edge_duplicated",
            lambda c: c["K_edges"].append(
                copy.deepcopy(c["K_edges"][0])
            ),
        )
        candidate_mutation(
            "candidate_k_edge_deleted",
            lambda c: c["K_edges"].pop(),
        )
        candidate_mutation(
            "candidate_diagnostic_forged",
            lambda c: c["diagnostics"].__setitem__(
                "k_edge_count", c["diagnostics"]["k_edge_count"] + 1
            ),
        )
        candidate_mutation(
            "candidate_semantic_hash_forged",
            lambda c: c.__setitem__("semantic_sha256", "0" * 64),
        )
        candidate_mutation(
            "candidate_branch_normalization_forged",
            lambda c: c["branch"].__setitem__(
                "normalization", "assume a completed automorphism"
            ),
        )
        candidate_mutation(
            "candidate_formula_hash_self_consistent_but_wrong",
            lambda c: c["formula"].__setitem__(
                "materialized_dimacs_sha256", "0" * 64
            ),
            synchronize=True,
        )

        def scan_mutation(name: str, mutate, *, synchronize: bool = False) -> None:
            changed = copy.deepcopy(self.scan)
            mutate(changed)
            if synchronize:
                synchronize_scan_semantic(changed)
            reject(
                name,
                lambda: audit.validate_scan_document(
                    changed,
                    self.cover,
                    self.candidate,
                    self.formula_records,
                ),
            )

        scan_mutation(
            "scan_claim_inflation",
            lambda s: s.__setitem__("claim_label", "VERIFIED"),
        )
        scan_mutation(
            "scan_target_inflation",
            lambda s: s.__setitem__("target_result", "NONEXISTENT"),
        )

        def promote_negative(scan: dict[str, object]) -> None:
            row = next(
                item
                for item in scan["results"]
                if item["status"] != "SAT_CANDIDATE"
            )
            row["status"] = "PROVED_UNSAT"

        scan_mutation(
            "scan_negative_promotion",
            promote_negative,
            synchronize=True,
        )

        def conflate_timeout_budget(scan: dict[str, object]) -> None:
            row = next(
                item
                for item in scan["results"]
                if item["status"] == "TIMEOUT_UNKNOWN"
            )
            row["status"] = "BUDGET_UNKNOWN"

        scan_mutation(
            "scan_timeout_budget_conflation",
            conflate_timeout_budget,
            synchronize=True,
        )
        scan_mutation(
            "scan_forged_proof_check",
            lambda s: next(
                row
                for row in s["results"]
                if row["status"] != "SAT_CANDIDATE"
            )["solver"].__setitem__("proof_trace_checked", True),
        )
        scan_mutation(
            "scan_forged_proof_emission",
            lambda s: next(
                row
                for row in s["results"]
                if row["status"] != "SAT_CANDIDATE"
            )["solver"].__setitem__("proof_trace_emitted", True),
        )
        scan_mutation(
            "scan_duplicate_branch",
            lambda s: s["results"].append(
                copy.deepcopy(s["results"][0])
            ),
        )
        scan_mutation(
            "scan_candidate_redirect",
            lambda s: next(
                row
                for row in s["results"]
                if row["status"] == "SAT_CANDIDATE"
            ).__setitem__(
                "candidate_path",
                audit.PROFILE_PATH.relative_to(audit.ROOT).as_posix(),
            ),
        )

        def forge_formula_hash(scan: dict[str, object]) -> None:
            scan["results"][0]["formula"][
                "materialized_dimacs_sha256"
            ] = "0" * 64

        scan_mutation(
            "scan_formula_hash_self_consistent_but_wrong",
            forge_formula_hash,
            synchronize=True,
        )
        scan_mutation(
            "scan_scope_inflation",
            lambda s: s.__setitem__("scope", "complete SRG search"),
        )
        scan_mutation(
            "scan_branch_metadata_forged",
            lambda s: s["results"][0]["branch"].__setitem__(
                "normalization", "assume transitivity"
            ),
        )
        scan_mutation(
            "scan_source_hash_forged",
            lambda s: s["source_provenance"].__setitem__(
                "code/wave16_n3_51_active_sat.py", "0" * 64
            ),
        )

        def profile_mutation(name: str, mutate) -> None:
            changed = copy.deepcopy(self.profile)
            mutate(changed)
            changed["semantic_sha256"] = audit.sha256_bytes(
                audit.canonical_json_bytes(changed["semantic"])
            )
            reject(
                name,
                lambda: audit.validate_profile_document(changed),
            )

        profile_mutation(
            "profile_row_deleted",
            lambda p: p["semantic"]["raw_profiles"].pop(),
        )
        profile_mutation(
            "profile_local_count_forged",
            lambda p: p["semantic"]["local_size3_mode_census"][0][
                "root_compositions"
            ][0].__setitem__("labeled_state_count", 74),
        )
        profile_mutation(
            "profile_surviving_branch_deleted",
            lambda p: p["semantic"][
                "post_finite_surviving_branches"
            ].pop(),
        )

        def failure_mutation(name: str, mutate) -> None:
            changed = copy.deepcopy(self.failures)
            mutate(changed)
            reject(
                name,
                lambda: audit.validate_failure_archive(
                    changed, self.scan
                ),
            )

        failure_mutation(
            "failure_budget_promoted",
            lambda f: f["historical_probe_before_final_source_freeze"].__setitem__(
                "status", "UNSAT_UNVERIFIED"
            ),
        )
        failure_mutation(
            "failure_proof_check_forged",
            lambda f: f["historical_probe_before_final_source_freeze"].__setitem__(
                "proof_trace_checked", True
            ),
        )
        failure_mutation(
            "failure_scan_hash_forged",
            lambda f: f["final_archive"].__setitem__(
                "active_local_scan_sha256", "0" * 64
            ),
        )
        failure_mutation(
            "failure_histogram_forged",
            lambda f: f["final_archive"][
                "negative_status_histogram"
            ].__setitem__("TIMEOUT_UNKNOWN", 4),
        )

        self.assertEqual(len(rejected), 38)


if __name__ == "__main__":
    unittest.main()
