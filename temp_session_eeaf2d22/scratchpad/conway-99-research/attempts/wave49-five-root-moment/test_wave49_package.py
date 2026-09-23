#!/usr/bin/env python3
"""Lightweight integrity tests for the sealed Wave49 discovery package."""

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent


def sha256(name: str) -> str:
    return hashlib.sha256((HERE / name).read_bytes()).hexdigest()


class Wave49PackageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.coefficients = json.loads((HERE / "coefficients.json").read_text())
        cls.results = json.loads((HERE / "results.json").read_text())
        cls.scout = json.loads((HERE / "combined-sdp-result.json").read_text())
        cls.handoff = json.loads((HERE / "compact-handoff.json").read_text())

    def test_stable_artifact_hashes(self) -> None:
        expected = {
            "coefficients.json": "66aeb26175643030770c8060a0550d202c56b6a9636e245ef19866a4a9cf308d",
            "results.json": "f8604031259a92776b29cda161344fd9b2bdf3ea395c3d8ce53facb82981f8c5",
            "combined-sdp-result.json": "1e41b1fd961714b24f69d1c31474f48b91dca88d938f5c97d5aa2424b8aac152",
        }
        self.assertEqual({name: sha256(name) for name in expected}, expected)

    def test_class_and_root_census(self) -> None:
        streams = self.coefficients["class_streams"]
        self.assertEqual([streams[str(k)]["count"] for k in (5, 6, 7)], [21, 62, 208])
        labelled = self.coefficients["labelled_tensor_reconstruction"]
        self.assertEqual(labelled["labelled_root_mask_count"], 683)
        expected_sizes = {
            0: 32, 1: 32, 3: 28, 7: 22, 15: 16, 19: 16, 20: 32,
            21: 26, 23: 16, 28: 28, 29: 21, 31: 13, 54: 18, 58: 24,
            59: 16, 62: 16, 184: 16, 185: 15, 207: 10, 220: 21, 221: 12,
        }
        self.assertEqual(
            {
                int(family["root_mask"]): int(family["matrix_size"])
                for family in self.coefficients["families"].values()
            },
            expected_sizes,
        )

    def test_relabelling_controls_and_witnesses(self) -> None:
        relabel = self.results["root_relabelling"]
        self.assertEqual(relabel["status"], "PASS_EXACT")
        self.assertEqual(relabel["mapping_checks"], 2520)
        self.assertFalse(relabel["target_graph_automorphism_assumed"])
        self.assertEqual(sum(len(control["families"]) for control in self.results["controls"]), 42)
        for control in self.results["controls"]:
            self.assertTrue(
                all(item["direct_equals_expansion"] for item in control["families"].values())
            )
        summary = self.results["target_summary"]
        self.assertEqual(summary["matrix_total"], 357)
        self.assertEqual(summary["exactly_indefinite_matrices"], 357)
        for target in self.results["targets"]:
            self.assertEqual(target["exactly_indefinite_family_count"], 21)
            for family in target["family_results"].values():
                self.assertLess(
                    family["exact_negative_direction"]["quadratic_numerator"], 0
                )

    def test_numerical_boundary_is_not_promoted(self) -> None:
        self.assertEqual(len(self.scout["solvers"]), 1)
        solver = self.scout["solvers"][0]
        self.assertEqual(solver["solver"], "CLARABEL")
        self.assertEqual(solver["status"], "optimal_inaccurate")
        self.assertFalse(solver["used_as_exact_evidence"])
        self.assertEqual(self.scout["conclusion"]["endpoint_n3_4158"], "UNKNOWN")
        self.assertEqual(
            self.scout["conclusion"]["exact_rational_dual_certificate"],
            "NOT_EXTRACTED",
        )
        self.assertEqual(self.handoff["conclusion"]["endpoint_n3_4158"], "UNKNOWN")

    def test_package_manifest(self) -> None:
        root = HERE.parents[1]
        for line in (HERE / "package-manifest.sha256").read_text().splitlines():
            expected, relative = line.split("  ", 1)
            self.assertEqual(
                hashlib.sha256((root / relative).read_bytes()).hexdigest(),
                expected,
                relative,
            )


if __name__ == "__main__":
    unittest.main()
