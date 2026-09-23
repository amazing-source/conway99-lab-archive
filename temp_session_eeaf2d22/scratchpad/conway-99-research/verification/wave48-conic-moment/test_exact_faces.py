#!/usr/bin/env python3
"""Focused integrity tests for the Wave48 exact-face verification."""

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent


class ExactFaceVerificationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.independent = json.loads(
            (HERE / "independent-reconstruction.json").read_text()
        )
        cls.results = json.loads(
            (HERE / "verification-results.json").read_text()
        )

    def test_sealed_independent_reconstruction(self) -> None:
        self.assertEqual(
            hashlib.sha256(
                (HERE / "independent-reconstruction.json").read_bytes()
            ).hexdigest(),
            "e2b7c1684cf4681504c303a090fe3b8f9882ddb2a6c514a973fd6686394a10e4",
        )
        self.assertFalse(self.independent["discovery_exact_faces_opened"])
        self.assertFalse(self.independent["floating_solver_artifacts_opened"])

    def test_exact_affine_certificate(self) -> None:
        affine = self.independent["affine"]
        self.assertEqual(affine["rational_rank"], 93)
        self.assertEqual(affine["affine_nullity"], 116)
        self.assertEqual(affine["exact_particular_row_checks"], 170)
        self.assertEqual(affine["exact_nullspace_row_checks"], 19720)

    def test_all_kernel_completeness_records(self) -> None:
        families = self.independent["families"]
        self.assertEqual(len(families), 11)
        expected = {
            ("wave45", "ordered_edge"): (1, 15),
            ("wave45", "ordered_nonedge"): (1, 18),
            ("wave45", "vertex"): (12, 5),
            ("wave47", "root_000"): (58, 6),
            ("wave47", "root_001"): (50, 6),
            ("wave47", "root_010"): (50, 6),
            ("wave47", "root_011"): (36, 6),
            ("wave47", "root_100"): (50, 6),
            ("wave47", "root_101"): (36, 6),
            ("wave47", "root_110"): (36, 6),
            ("wave47", "root_111"): (17, 3),
        }
        self.assertEqual(
            {
                (item["source"], item["name"]): (
                    item["exact_active_rank"],
                    item["exact_nullity"],
                )
                for item in families
            },
            expected,
        )
        for item in families:
            self.assertTrue(item["complete_common_kernel"])
            self.assertEqual(item["rank_plus_nullity"], item["matrix_size"])
            self.assertEqual(
                set(item["modular_active_ranks"].values()),
                {item["exact_active_rank"]},
            )

    def test_discovery_comparison_passed(self) -> None:
        self.assertEqual(self.results["claim_label"], "VERIFIED_SCOPED")
        self.assertEqual(self.results["families_passed"], 11)
        self.assertEqual(self.results["families_total"], 11)
        self.assertTrue(all(self.results["affine_checks"].values()))
        for family in self.results["family_comparisons"]:
            self.assertEqual(family["status"], "PASS")
            self.assertTrue(all(family["checks"].values()))
        self.assertFalse(self.results["floating_solver_artifacts_opened"])
        self.assertEqual(
            self.results["conclusion"]["endpoint_n3_4158"], "UNKNOWN"
        )

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
