#!/usr/bin/env python3
"""Focused hostile tests for the independent Wave51 replay."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
VERIFY_PATH = HERE / "verify.py"
SPEC = importlib.util.spec_from_file_location("wave51_independent_verify", VERIFY_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load independent verifier")
VERIFY = importlib.util.module_from_spec(SPEC)
sys.modules["wave51_independent_verify"] = VERIFY
SPEC.loader.exec_module(VERIFY)


class IndependentWave51Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = (HERE / "verification-result.json").read_bytes()
        cls.result = json.loads(cls.payload)

    def test_result_hash_and_allowed_label(self) -> None:
        self.assertEqual(
            hashlib.sha256(self.payload).hexdigest(),
            "24cd2316c20beabe9ecd4e143eb310f8a200f45e49dda189e12d38bc46de1452",
        )
        self.assertEqual(self.result["claim_label"], "VERIFIED")
        self.assertEqual(self.result["role"], "verifier")

    def test_source_status_defect_is_not_silently_repaired(self) -> None:
        audit = self.result["source_status_audit"]
        self.assertTrue(audit["separation_violation_found"])
        self.assertEqual(
            audit["effective_source_label_before_independent_replay"], "CANDIDATE"
        )
        self.assertEqual(
            audit["independent_label_after_clean_room_replay"], "VERIFIED"
        )
        self.assertFalse(audit["source_files_modified"])

    def test_exact_census_and_witness(self) -> None:
        self.assertEqual(self.result["wave44"]["equations"], 170)
        self.assertEqual(
            self.result["cuts"]["layers"],
            {"wave45": 17, "wave47": 136, "wave49": 21},
        )
        witness = self.result["exact_witness"]
        self.assertTrue(witness["all_equation_residuals_zero"])
        self.assertTrue(witness["all_cut_slacks_nonnegative"])
        self.assertTrue(witness["all_208_counts_nonnegative"])
        self.assertEqual(witness["support_size"], 136)
        self.assertEqual(witness["y_h11_over_4"], "4158")
        self.assertEqual(witness["tight_cuts_by_layer"], {
            "wave45": 5,
            "wave47": 46,
            "wave49": 15,
        })
        self.assertEqual(witness["minimum_strictly_positive_slack"], "133056")
        self.assertEqual(witness["maximum_denominator_digits"], 272)

    def test_selection_and_reconstruction_attacks(self) -> None:
        wave47 = self.result["cuts"]["wave47"]
        self.assertTrue(wave47["all_2657_cut_self_hashes_valid"])
        self.assertTrue(wave47["all_2657_cut_hashes_unique"])
        self.assertEqual(wave47["source_family_pairs"], 136)
        self.assertEqual(wave47["selected_index_zero_cuts"], 136)
        wave49 = self.result["cuts"]["wave49"]
        self.assertTrue(wave49["all_21_family_self_hashes_valid"])
        self.assertTrue(wave49["all_21_direction_self_hashes_valid"])
        self.assertEqual(wave49["exact_reconstruction_checks"], 5691)
        self.assertEqual(len(VERIFY.admissible_five_root_masks()), 21)
        self.assertNotIn(126, VERIFY.admissible_five_root_masks())

    def test_rank_certificate_and_scope_wall(self) -> None:
        rank = self.result["active_constraint_rank"]
        self.assertEqual(rank["rank"], 209)
        self.assertEqual(rank["columns"], 209)
        self.assertEqual(rank["pivot_columns"], list(range(209)))
        conclusion = self.result["conclusion"]
        self.assertEqual(
            conclusion["fixed_174_cut_rational_relaxation"], "EXACTLY_FEASIBLE"
        )
        self.assertEqual(
            conclusion["farkas_infeasibility_certificate_for_this_fixed_bundle"],
            "REFUTED",
        )
        self.assertEqual(conclusion["full_psd_system_feasibility"], "UNKNOWN")
        self.assertEqual(conclusion["endpoint_n3_4158"], "UNKNOWN")
        self.assertFalse(conclusion["graph_constructed"])

    def test_modular_rank_hostile_dependency(self) -> None:
        rank, pivots = VERIFY.rank_mod_prime(
            [{0: 1, 1: 2}, {0: 2, 1: 4}, {2: 1}], 3, 2_147_483_647
        )
        self.assertEqual(rank, 2)
        self.assertEqual(pivots, [0, 2])

    def test_fresh_clean_room_replay(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(VERIFY_PATH), "--validate"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=60,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("PASS_CLEAN_ROOM_REPLAY", completed.stdout)

    def test_input_freeze_matches_verifier_constants(self) -> None:
        recorded = {}
        for line in (HERE / "input-freeze.sha256").read_text().splitlines():
            digest, relative = line.split("  ", 1)
            recorded[(ROOT / relative).resolve()] = digest
        self.assertEqual(recorded, {path.resolve(): digest for path, digest in VERIFY.EXPECTED.items()})

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
