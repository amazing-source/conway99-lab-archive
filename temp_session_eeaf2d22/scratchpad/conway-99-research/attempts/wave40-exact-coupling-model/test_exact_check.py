#!/usr/bin/env python3
"""Focused and hostile tests for the Wave 40 exact coupling census."""

from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave40_exact_coupling", HERE / "exact_check.py"
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load exact_check.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


EXPECTED = {
    "1+1+1+1+1+1": (1, 25, 0, 25),
    "1+1+1+1+2": (30, 23, 1, 25),
    "1+1+1+3": (160, 25, 0, 25),
    "1+1+2+2": (180, 21, 2, 25),
    "1+1+4": (720, 23, 1, 25),
    "1+2+3": (960, 23, 1, 25),
    "1+5": (2304, 25, 0, 25),
    "2+2+2": (120, 19, 3, 25),
    "2+4": (1440, 21, 2, 25),
    "3+3": (640, 25, 0, 25),
    "6": (3840, 23, 1, 25),
}


class ExactCouplingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result, cls.certificate = MODULE.derive()

    def records(self) -> dict[str, dict[str, object]]:
        return {
            record["partition_key"]: record
            for record in self.result["finite_census"]["types"]
        }

    def test_all_10395_matchings_and_eleven_types(self) -> None:
        records = self.records()
        self.assertEqual(set(records), set(EXPECTED))
        self.assertEqual(
            sum(record["labelled_pulled_matching_count"] for record in records.values()),
            10_395,
        )
        self.assertEqual(
            sum(
                record["explicit_partition_conjugacy_checks"]
                for record in records.values()
            ),
            10_395,
        )

    def test_per_type_rank_table(self) -> None:
        for key, (count, base_rank, projection_rank, coupled_floor) in EXPECTED.items():
            record = self.records()[key]
            self.assertEqual(record["labelled_pulled_matching_count"], count)
            self.assertEqual(record["base_27_rank_F7"], base_rank)
            self.assertEqual(
                record["projection_census"][
                    "minimum_projection_rank_over_permutations"
                ],
                projection_rank,
            )
            self.assertEqual(
                record["coupled_39_rank_lower_bound_F7"], coupled_floor
            )

    def test_hard_222_subspace_boundary(self) -> None:
        record = self.records()["2+2+2"]
        levels = record["projection_census"]["levels_through_first_success"]
        self.assertEqual(
            [
                (
                    level["dimension"],
                    level["subspace_count"],
                    level["maximum_support_matching"],
                )
                for level in levels
            ],
            [(0, 1, 0), (1, 66, 4), (2, 1923, 8), (3, 25744, 12)],
        )

    def test_rank_congruence_positive_controls(self) -> None:
        for record in self.records().values():
            self.assertGreaterEqual(
                record["canonical_local_control_rank_F7"],
                record["coupled_39_rank_lower_bound_F7"],
            )
            witness = record["projection_census"]["witness"]
            self.assertEqual(sorted(witness["permutation"]), list(range(12)))
            self.assertEqual(
                witness["projection_rank"],
                record["projection_census"][
                    "minimum_projection_rank_over_permutations"
                ],
            )

    def test_candidate_status_wall(self) -> None:
        self.assertEqual(self.result["claim_label"], "CANDIDATE")
        self.assertEqual(
            self.result["candidate_universal_result"]["rank_F7_M_lower_bound"], 25
        )
        self.assertFalse(
            self.result["conditional_endpoint_arithmetic"]["endpoint_excluded"]
        )
        self.assertFalse(
            self.result["conditional_endpoint_arithmetic"][
                "upper_bound_improved_below_4158"
            ]
        )
        self.assertEqual(self.result["status"]["conway_99"], "UNKNOWN")
        self.assertEqual(self.result["status"]["novelty"], "UNKNOWN")

    def test_endpoint_pair_arithmetic(self) -> None:
        endpoint = self.result["conditional_endpoint_arithmetic"]
        self.assertEqual(endpoint["admissible_rank_pair_count_after_candidate"], 330)
        self.assertEqual(
            endpoint["if_r3_equals_12"]["admissible_r7_values"],
            list(range(26, 45, 2)),
        )

    def test_certificate_binds_result(self) -> None:
        digest = MODULE.sha256_bytes(MODULE.canonical_json(self.certificate))
        self.assertEqual(
            digest, self.result["finite_census"]["certificate_sha256"]
        )
        self.assertEqual(
            self.certificate["completeness"]["pulled_perfect_matchings"], 10_395
        )
        self.assertEqual(len(self.certificate["types"]), 11)

    def test_committed_documents_match_regeneration(self) -> None:
        self.assertEqual(
            (HERE / "exact-results.json").read_bytes(),
            MODULE.canonical_json(self.result),
        )
        self.assertEqual(
            (HERE / "subspace-certificate.json").read_bytes(),
            MODULE.canonical_json(self.certificate),
        )

    def test_hostile_rank_floor_mutation_is_detected(self) -> None:
        mutated = copy.deepcopy(self.result)
        mutated["candidate_universal_result"]["rank_F7_M_lower_bound"] = 26
        self.assertNotEqual(
            MODULE.canonical_json(mutated), MODULE.canonical_json(self.result)
        )

    def test_hostile_subspace_basis_mutation_is_detected(self) -> None:
        mutated = copy.deepcopy(self.certificate)
        rejected = mutated["types"]["2+2+2"][
            "projection_subspace_certificate"
        ]["rejected_subspaces"]
        rejected[-1]["basis"][0][0] = (
            rejected[-1]["basis"][0][0] + 1
        ) % 7
        self.assertNotEqual(
            MODULE.sha256_bytes(MODULE.canonical_json(mutated)),
            self.result["finite_census"]["certificate_sha256"],
        )

    def test_hostile_nonpermutation_witness_is_detected(self) -> None:
        mutated = copy.deepcopy(self.certificate)
        witness = mutated["types"]["2+2+2"][
            "projection_subspace_certificate"
        ]["witness"]
        witness["permutation"][1] = witness["permutation"][0]
        self.assertNotEqual(
            MODULE.canonical_json(mutated), MODULE.canonical_json(self.certificate)
        )

    def test_hostile_input_hash_mutation_is_detected(self) -> None:
        mutated = copy.deepcopy(self.result)
        mutated["inputs"]["CONJECTURE.md"] = "0" * 64
        self.assertNotEqual(
            MODULE.canonical_json(mutated), MODULE.canonical_json(self.result)
        )

    def test_hostile_endpoint_promotion_is_detected(self) -> None:
        mutated = copy.deepcopy(self.result)
        mutated["conditional_endpoint_arithmetic"]["endpoint_excluded"] = True
        mutated["status"]["strongest_general_upper_bound_on_n3"] = 4155
        self.assertNotEqual(
            MODULE.canonical_json(mutated), MODULE.canonical_json(self.result)
        )

    def test_json_round_trip_is_canonical(self) -> None:
        raw = MODULE.canonical_json(self.result)
        self.assertEqual(MODULE.canonical_json(json.loads(raw)), raw)


if __name__ == "__main__":
    unittest.main()
