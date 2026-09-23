#!/usr/bin/env python3
"""Focused tests for the Wave51 exact rank-one cut probe."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


class RankOneProbeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = (HERE / "exact-result.json").read_bytes()
        cls.result = json.loads(cls.payload)

    def test_sealed_result_hash(self) -> None:
        self.assertEqual(
            hashlib.sha256(self.payload).hexdigest(),
            "527656f5d2d6a03d71234dc0fb110422ddfade1ac8b5a1d175168e857073edfc",
        )

    def test_exact_scope_and_census(self) -> None:
        self.assertEqual(self.result["claim_label"], "VERIFIED_SCOPED")
        self.assertEqual(self.result["wave44"]["equations"], 170)
        self.assertEqual(self.result["cut_bundle"]["total"], 174)
        self.assertEqual(
            self.result["cut_bundle"]["layers"],
            {"wave45": 17, "wave47": 136, "wave49": 21},
        )
        self.assertEqual(
            self.result["cut_bundle"]["wave49_reconstruction"]["status"],
            "PASS_EXACT",
        )

    def test_exact_certificate_summary(self) -> None:
        certificate = self.result["exact_certificate"]
        self.assertTrue(certificate["all_170_wave44_equations"])
        self.assertTrue(certificate["all_174_rank_one_cuts_nonnegative"])
        self.assertTrue(certificate["all_208_counts_nonnegative"])
        self.assertEqual(certificate["support_size"], 136)
        self.assertEqual(certificate["y_h11_over_4"], "4158")
        self.assertEqual(certificate["zero_cut_slacks"], 66)
        self.assertEqual(certificate["strictly_positive_cut_slacks"], 108)
        self.assertEqual(
            certificate["minimum_strictly_positive_cut_slack"], "133056"
        )

    def test_status_wall(self) -> None:
        conclusion = self.result["conclusion"]
        self.assertEqual(
            conclusion["fixed_174_cut_real_relaxation"], "EXACTLY_FEASIBLE"
        )
        self.assertEqual(
            conclusion["farkas_contradiction_from_this_bundle"], "REFUTED"
        )
        self.assertEqual(conclusion["full_psd_constrained_region"], "UNKNOWN")
        self.assertEqual(conclusion["integer_count_feasibility"], "UNKNOWN")
        self.assertEqual(conclusion["endpoint_n3_4158"], "UNKNOWN")
        self.assertFalse(conclusion["graph_constructed"])

    def test_exact_replay_command(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(HERE / "probe.py"), "--validate"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("PASS_EXACT_REPLAY", completed.stdout)

    def test_package_manifest(self) -> None:
        for line in (HERE / "package-manifest.sha256").read_text().splitlines():
            expected, relative = line.split("  ", 1)
            self.assertEqual(
                hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(),
                expected,
                relative,
            )


if __name__ == "__main__":
    unittest.main()
