#!/usr/bin/env python3
"""Focused current-tip regressions for the repaired Wave 13 bundle."""

from __future__ import annotations

import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class RepairRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.repository = Path(__file__).resolve().parents[2]
        cls.audit = load_module(
            "wave13_repair_audit_regression_helpers",
            Path(__file__).with_name("independent_repair_audit.py"),
        )
        cls.discovery = load_module(
            "wave13_repaired_discovery_regression_target",
            cls.repository / "code" / "wave13_n3_45_active_sat.py",
        )
        cls.arithmetic = load_module(
            "wave13_independent_arithmetic_regression_helper",
            cls.repository
            / "verification"
            / "n3-45-computation"
            / "independent_audit.py",
        )
        cls.candidate_path = (
            cls.repository
            / "attempts"
            / "wave13-computation"
            / "n3-45-no-common-point-m5-111.json"
        )
        cls.candidate = json.loads(
            cls.candidate_path.read_text(encoding="utf-8")
        )

    def test_exact_seven_q3_containing_rows_are_zero(self) -> None:
        census = json.loads(
            (
                self.repository
                / "attempts"
                / "wave13-computation"
                / "n3-45-local-census.json"
            ).read_text(encoding="utf-8")
        )
        reduction = census["mixed_order14_reduction"]
        expected = [
            [2, 2, 3],
            [2, 3, 2],
            [2, 3, 3],
            [3, 2, 2],
            [3, 2, 3],
            [3, 3, 2],
            [3, 3, 3],
        ]
        self.assertEqual(
            reduction["q3_containing_assignments_checked"],
            expected,
        )
        self.assertEqual(
            [row["q_values"] for row in reduction["q3_containing_mode_census"]],
            expected,
        )
        self.assertTrue(
            all(
                row["mode_count"] == 0 and row["modes"] == []
                for row in reduction["q3_containing_mode_census"]
            )
        )

    def test_scan_keeps_exact_cover_hashes_and_unverified_boundary(self) -> None:
        scan = json.loads(
            (
                self.repository
                / "attempts"
                / "wave13-computation"
                / "n3-45-active-local-sat-scan.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(
            tuple(tuple(item) for item in scan["branch_cover"]),
            self.audit.EXPECTED_BRANCHES,
        )
        observed = {
            (row["size3_point_count"], row["root_mode"]): (
                row["statistics"]["variables"],
                row["statistics"]["clauses"],
                row["statistics"]["cnf_sha256"],
            )
            for row in scan["branches"]
        }
        self.assertEqual(observed, self.audit.EXPECTED_FORMULAS)
        self.assertEqual(
            {row["status"] for row in scan["branches"]},
            {"UNSAT_UNVERIFIED"},
        )
        self.assertEqual(scan["target_result"], "UNKNOWN")
        self.assertEqual(scan["novelty_status"], "UNKNOWN")

    def test_positive_v2_candidate_replays(self) -> None:
        result = self.discovery.validate_weakened_candidate(self.candidate)
        self.assertEqual(result["status"], "PASS weakened active-local diagnostic")
        self.assertEqual(result["omitted_premise_violation_count"], 18)
        self.assertEqual(result["target_result"], "UNKNOWN")
        self.assertEqual(result["novelty_status"], "UNKNOWN")

    def test_raw_schema_and_metadata_attacks_are_rejected(self) -> None:
        cases = []
        duplicate_edge = copy.deepcopy(self.candidate)
        duplicate_edge["K_edges"].append(duplicate_edge["K_edges"][0])
        duplicate_edge["K_edges"].sort()
        self.audit.refresh_integrity(duplicate_edge)
        cases.append(duplicate_edge)

        reversed_point = copy.deepcopy(self.candidate)
        reversed_point["point_sets"][0] = list(
            reversed(reversed_point["point_sets"][0])
        )
        self.audit.refresh_integrity(reversed_point)
        cases.append(reversed_point)

        missing = copy.deepcopy(self.candidate)
        missing.pop("claim_label")
        cases.append(missing)

        unknown = copy.deepcopy(self.candidate)
        unknown["unknown"] = True
        cases.append(unknown)

        forged = copy.deepcopy(self.candidate)
        forged["builder_source_sha256"] = "0" * 64
        self.audit.refresh_integrity(forged)
        cases.append(forged)

        for case in cases:
            with self.subTest(keys=sorted(case)):
                with self.assertRaises(AssertionError):
                    self.discovery.validate_weakened_candidate(case)

    def test_full_relabel_with_all_public_digests_refreshed_is_rejected(
        self,
    ) -> None:
        changed = copy.deepcopy(self.candidate)
        permutation = {
            index: (index + 3) % self.audit.ORDER
            for index in range(self.audit.ORDER)
        }
        changed["point_sets"] = sorted(
            (
                sorted(permutation[vertex] for vertex in point)
                for point in changed["point_sets"]
            ),
            key=lambda item: (len(item), item),
        )
        changed["K_edges"] = sorted(
            sorted((permutation[left], permutation[right]))
            for left, right in changed["K_edges"]
        )
        points = tuple(tuple(item) for item in changed["point_sets"])
        edges = frozenset(tuple(item) for item in changed["K_edges"])
        diagnostics = self.arithmetic.witness_core_diagnostics(points, edges)
        changed["diagnostics"] = self.audit.project_diagnostics(
            diagnostics,
            points,
        )
        self.audit.refresh_core_and_integrity(changed)
        with self.assertRaisesRegex(AssertionError, "root point is absent"):
            self.discovery.validate_weakened_candidate(changed)

    def test_two_fresh_candidates_are_byte_identical_to_archive(self) -> None:
        archived = self.candidate_path.read_bytes()
        for name in ("candidate-generation-1.json", "candidate-generation-2.json"):
            self.assertEqual(
                archived,
                Path(__file__).with_name(name).read_bytes(),
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
