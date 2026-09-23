#!/usr/bin/env python3
"""Regression and hostile-mutation tests for the independent Wave 13 audit."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import types
import unittest
from pathlib import Path

import independent_audit as arithmetic
import independent_formula_audit as formulas


REPOSITORY = Path(__file__).resolve().parents[2]
ATTEMPTS = REPOSITORY / "attempts" / "wave13-computation"
FROZEN_BASELINE_COMMIT = "066d9c7fcf593c3b9d35cfef1031dbd9daab4145"


def frozen_bytes(relative_path: str) -> bytes:
    """Read a baseline artifact without changing the current worktree."""

    command = [
        "git",
        "show",
        f"{FROZEN_BASELINE_COMMIT}:{relative_path}",
    ]
    completed = subprocess.run(
        command,
        cwd=REPOSITORY,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.stdout


def frozen_json(relative_path: str) -> dict[str, object]:
    return json.loads(frozen_bytes(relative_path).decode("utf-8"))


def load_discovery_validator():
    """Load the failed baseline validator, never the repaired current tip."""

    name = "_wave13_discovery_validator_under_attack"
    source_name = (
        f"{FROZEN_BASELINE_COMMIT}:code/wave13_n3_45_active_sat.py"
    )
    source = frozen_bytes("code/wave13_n3_45_active_sat.py")
    module = types.ModuleType(name)
    module.__file__ = source_name
    sys.modules[name] = module
    exec(compile(source, source_name, "exec"), module.__dict__)
    return module


class IndependentArithmeticTests(unittest.TestCase):
    def test_nine_profiles_and_two_post_obstruction_profiles(self) -> None:
        profiles = arithmetic.reconstruct_profiles()
        self.assertEqual(len(profiles), 9)
        self.assertEqual(
            sum(
                row["passes_three_distinct_nonsingleton_edges"]
                for row in profiles
            ),
            3,
        )
        self.assertEqual(
            sum(
                row["passes_frozen_degree_three_obstruction"]
                for row in profiles
            ),
            2,
        )

    def test_every_q3_containing_order14_root_is_checked(self) -> None:
        result = arithmetic.reconstruct_rooted_mode_results()
        self.assertEqual(
            len(result["order14_q3_containing_mode_counts"]),
            7,
        )
        self.assertEqual(
            set(result["order14_q3_containing_mode_counts"].values()),
            {0},
        )

    def test_flowers_and_mixed_graph_reduction(self) -> None:
        result = arithmetic.reconstruct_mixed_profile_reduction()
        self.assertEqual(result["possible_cubic_orders"], [4, 6])
        self.assertEqual(
            result["cubic_graph_censuses"][4][
                "labeled_triangle_free_cubic"
            ],
            0,
        )
        self.assertEqual(
            result["cubic_graph_censuses"][6][
                "labeled_triangle_free_cubic"
            ],
            10,
        )
        self.assertTrue(result["open_twin_injection_contradiction"])
        self.assertGreater(
            result["all_size2_forced_q3_K_degree"],
            result["q3_K_degree_capacity"],
        )

    def test_59_aggregate_signatures_and_exact_branch_cover(self) -> None:
        signatures = arithmetic.reconstruct_incidence_signatures()
        self.assertEqual(len(signatures), 59)
        self.assertEqual(
            arithmetic.reconstruct_branch_cover(signatures),
            arithmetic.EXPECTED_BRANCHES,
        )
        self.assertFalse(any(row["m"] in (13, 15) for row in signatures))
        self.assertEqual(
            arithmetic.minimum_integral_label_use(13)[
                "minimum_used_labels"
            ],
            18,
        )
        self.assertEqual(
            arithmetic.minimum_integral_label_use(15)[
                "minimum_used_labels"
            ],
            20,
        )
        m11 = [row for row in signatures if row["m"] == 11]
        self.assertEqual(len(m11), 1)
        self.assertEqual(
            m11[0]["type_counts"],
            {"111": 0, "122": 0, "222": 2, "223": 9},
        )


class IndependentFormulaTests(unittest.TestCase):
    def test_first_formula_exact_stream_hash(self) -> None:
        scan = json.loads(
            (ATTEMPTS / "n3-45-active-local-sat-scan.json").read_text(
                encoding="utf-8"
            )
        )
        formula = formulas.build_formula(1, "111", "full")
        archived = scan["branches"][0]["statistics"]
        self.assertEqual(formula.pool.top, archived["variables"])
        self.assertEqual(len(formula.cnf.clauses), archived["clauses"])
        self.assertEqual(
            formulas.dimacs_stream_sha256(formula.cnf, formula.pool.top),
            archived["cnf_sha256"],
        )

    def test_positive_formula_assignment_is_checked_clause_by_clause(self) -> None:
        result = formulas.positive_witness_formula_check(
            REPOSITORY,
            "cadical195",
        )
        self.assertEqual(
            result["positive_total_assignment_check"][
                "violated_clause_count"
            ],
            0,
        )
        self.assertEqual(
            len(result["falsified_full_common_point_clauses"]),
            18,
        )

    def test_no_frozen_proof_trace_exists(self) -> None:
        proof_suffixes = {
            ".drat",
            ".frat",
            ".lrat",
            ".grat",
            ".proof",
            ".trace",
        }
        traces = [
            path
            for path in ATTEMPTS.rglob("*")
            if path.is_file() and path.suffix.lower() in proof_suffixes
        ]
        self.assertEqual(traces, [])


class WitnessAndMutationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.candidate = frozen_json(
            "attempts/wave13-computation/"
            "n3-45-no-common-point-m5-111.json"
        )
        cls.discovery = load_discovery_validator()

    def test_strict_witness_validation_and_all_18_certificates(self) -> None:
        result = arithmetic.strict_validate_witness(self.candidate)
        self.assertEqual(result["common_point_Berge_triangle_count"], 18)
        triples = [
            row["triple"] for row in result["berge_certificates"]
        ]
        self.assertEqual(len(triples), len({tuple(row) for row in triples}))
        self.assertEqual(
            triples[-8:],
            [
                [4, 5, 7],
                [4, 5, 10],
                [4, 7, 10],
                [5, 7, 10],
                [8, 12, 13],
                [8, 12, 14],
                [8, 13, 14],
                [12, 13, 14],
            ],
        )

    def test_strict_validator_rejects_all_hostile_mutations(self) -> None:
        self.assertTrue(
            all(
                arithmetic.strict_mutation_results(
                    self.candidate
                ).values()
            )
        )

    def test_frozen_validator_rejects_core_edge_deletion(self) -> None:
        mutated = copy.deepcopy(self.candidate)
        mutated["K_edges"].pop()
        with self.assertRaises(AssertionError):
            self.discovery.validate_weakened_candidate(mutated)

    def test_frozen_validator_rejects_status_inflation(self) -> None:
        mutated = copy.deepcopy(self.candidate)
        mutated["claim_label"] = "VERIFIED"
        with self.assertRaises(AssertionError):
            self.discovery.validate_weakened_candidate(mutated)

    def test_frozen_validator_accepts_unhashed_metadata_forgery(self) -> None:
        mutated = copy.deepcopy(self.candidate)
        mutated["root_mode"] = "223"
        mutated["size3_point_count"] = 11
        mutated["active_order"] = 99
        mutated["K_degree"] = 99
        mutated["root_normalization"][
            "completed_graph_automorphism_assumed"
        ] = True
        mutated["restrictions"] = []
        mutated["omitted_premise"] = "forged"
        result = self.discovery.validate_weakened_candidate(mutated)
        self.assertEqual(
            result["status"],
            "PASS weakened active-local diagnostic",
        )

    def test_frozen_validator_accepts_duplicate_K_edge(self) -> None:
        mutated = copy.deepcopy(self.candidate)
        mutated["K_edges"].append(copy.deepcopy(mutated["K_edges"][0]))
        result = self.discovery.validate_weakened_candidate(mutated)
        self.assertEqual(
            result["status"],
            "PASS weakened active-local diagnostic",
        )

    def test_archived_candidate_statistics_are_stale_against_source(self) -> None:
        self.assertNotIn(
            "cnf_sha256",
            self.candidate["solver_statistics"],
        )
        source = frozen_bytes(
            "code/wave13_n3_45_active_sat.py"
        ).decode("utf-8")
        self.assertIn('"cnf_sha256": formula_sha256', source)
        regenerated_formula = formulas.build_formula(
            5,
            "111",
            "no_common_point",
        )
        self.assertEqual(
            formulas.dimacs_stream_sha256(
                regenerated_formula.cnf,
                regenerated_formula.pool.top,
            ),
            "8260378538dccf0b3b3355619ceb237d7d6f89e1f3b26d86ea316f7e593df146",
        )

    def test_frozen_validator_accepts_core_with_claimed_root_absent(self) -> None:
        mutated = copy.deepcopy(self.candidate)
        permutation = {vertex: vertex for vertex in range(15)}
        permutation[0], permutation[3] = 3, 0
        mutated["point_sets"] = [
            sorted(permutation[vertex] for vertex in point)
            for point in mutated["point_sets"]
        ]
        mutated["K_edges"] = [
            sorted(permutation[vertex] for vertex in item)
            for item in mutated["K_edges"]
        ]
        points = tuple(
            frozenset(point) for point in mutated["point_sets"]
        )
        self.assertNotIn(frozenset((0, 1, 2)), points)
        k_edges = frozenset(
            self.discovery.edge(*item) for item in mutated["K_edges"]
        )
        mutated["diagnostics"] = (
            self.discovery.weakened_assignment_diagnostics(
                points,
                k_edges,
            )
        )
        semantic = {
            "variant": mutated["variant"],
            "point_sets": mutated["point_sets"],
            "K_edges": [list(item) for item in sorted(k_edges)],
            "diagnostics": mutated["diagnostics"],
        }
        mutated["semantic_sha256"] = self.discovery.sha256_bytes(
            self.discovery.canonical_json_bytes(semantic)
        )
        result = self.discovery.validate_weakened_candidate(mutated)
        self.assertEqual(
            result["status"],
            "PASS weakened active-local diagnostic",
        )
        with self.assertRaises(AssertionError):
            arithmetic.strict_validate_witness(mutated)


if __name__ == "__main__":
    unittest.main()
