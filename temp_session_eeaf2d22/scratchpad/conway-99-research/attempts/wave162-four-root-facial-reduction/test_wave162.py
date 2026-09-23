#!/usr/bin/env python3
"""Tests for the Wave162 exact facial-reduction audit."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE / "analyze_facial_reduction.py"
SPEC = importlib.util.spec_from_file_location("wave162_analysis", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
ANALYSIS = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = ANALYSIS
SPEC.loader.exec_module(ANALYSIS)


class Wave162Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.audit = json.loads(
            (HERE / "facial-reduction-audit.json").read_text(encoding="utf-8")
        )

    def test_fifteen_canonical_cuts(self) -> None:
        cuts = ANALYSIS.load_cuts()
        self.assertEqual(len(cuts), 15)
        self.assertEqual(len({cut["cut_sha256"] for cut in cuts}), 15)

    def test_exact_cut_replay_has_three_wave159_zeros(self) -> None:
        expected = {
            "68a099dd942bba0033af474e311d9720f6f15aaf558ee5df575edcb1d8c01240",
            "8fc952768230bd900febf656bddfa9dd6b4d4c89b5190e0b74e01e55639f525b",
            "93c3dcebda9332946cf3391812a4d1f466f7cacc6da4246bc9d625a66879f113",
        }
        self.assertEqual(set(self.audit["wave159_active_cut_hashes"]), expected)

    def test_no_cut_is_zero_on_every_stored_witness(self) -> None:
        self.assertEqual(self.audit["universal_zero_cut_hashes"], [])

    def test_wave159_active_cuts_are_not_affine_forced(self) -> None:
        records = self.audit["affine_nonforcing_certificates"]
        self.assertEqual(len(records), 3)
        for record in records:
            self.assertEqual(record["zero_value"], "0")
            self.assertNotEqual(record["comparison_value"], "0")
            self.assertEqual(
                record["conclusion"],
                "NOT_FORCED_ZERO_BY_COMMON_STORED_AFFINE_EQUALITIES",
            )

    def test_conditional_face_ranks(self) -> None:
        faces = {
            int(record["root_mask"]): record
            for record in self.audit["conditional_psd_faces"]
        }
        self.assertEqual(faces[3]["assumed_active_direction_rank"], 1)
        self.assertEqual(faces[3]["reduced_psd_cone_order"], 154)
        self.assertEqual(faces[12]["assumed_active_direction_rank"], 2)
        self.assertEqual(faces[12]["reduced_psd_cone_order"], 176)
        for record in faces.values():
            self.assertNotEqual(
                int(
                    record["independence_certificate"][
                        "exact_minor_determinant"
                    ]
                ),
                0,
            )

    def test_latest_negative_directions_escape_active_spans(self) -> None:
        records = {
            int(record["root_mask"]): record
            for record in self.audit["latest_escape_direction_certificates"]
        }
        self.assertEqual(records[3]["rank"], 2)
        self.assertEqual(records[12]["rank"], 3)
        for record in records.values():
            self.assertNotEqual(int(record["exact_minor_determinant"]), 0)

    def test_every_evaluation_has_an_exact_negative_block(self) -> None:
        evaluations = self.audit["stored_negative_blocks"]
        self.assertEqual(len(evaluations), 6)
        for blocks in evaluations.values():
            self.assertTrue(blocks)
            self.assertTrue(
                all(int(block["quadratic_value_scaled"]) < 0 for block in blocks)
            )

    def test_global_claims_remain_open(self) -> None:
        conclusion = self.audit["conclusion"]
        self.assertFalse(conclusion["unconditional_forced_four_root_face_found"])
        self.assertEqual(conclusion["endpoint_n3_4158"], "UNKNOWN")
        self.assertEqual(
            conclusion["strict_upper_bound_below_4158"], "NOT_PROVED"
        )
        self.assertEqual(conclusion["Conway_99"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
