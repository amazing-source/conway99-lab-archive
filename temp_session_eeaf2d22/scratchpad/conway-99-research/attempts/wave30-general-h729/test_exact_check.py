#!/usr/bin/env python3
"""Tests for the Wave 30 decomposable h=729 exact companion."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import exact_check as check


class Wave30GeneralH729Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = check.derive()

    def test_frozen_hashes(self) -> None:
        self.assertEqual(
            self.result["frozen_input_hashes"],
            check.FROZEN_INPUTS,
        )

    def test_unique_endpoint_detq(self) -> None:
        self.assertEqual(check.unique_endpoint_detq(), [5])

    def test_even_odd_determinant_residue(self) -> None:
        self.assertEqual(check.even_odd_determinant_residue(4), 1)
        self.assertEqual(check.even_odd_determinant_residue(8), 1)
        self.assertEqual(check.even_odd_determinant_residue(6), 3)
        with self.assertRaises(ValueError):
            check.even_odd_determinant_residue(5)

    def test_exceptional_block_types(self) -> None:
        self.assertEqual(
            check.exceptional_block_types(),
            [
                (4, 2), (4, 4), (4, 6),
                (12, 2), (12, 4), (12, 6),
                (20, 2), (20, 4), (20, 6),
                (28, 2), (28, 4), (28, 6),
                (36, 2), (36, 4), (36, 6),
            ],
        )

    def test_frame_row_counts(self) -> None:
        self.assertEqual(check.frame_row_count(12), 63)
        self.assertEqual(check.frame_row_count(20), 105)
        self.assertEqual(check.frame_row_count(24), 126)
        self.assertEqual(check.frame_row_count(32), 168)
        with self.assertRaises(ValueError):
            check.frame_row_count(2)

    def test_row_alphabet_is_complete(self) -> None:
        rows = check.row_alphabet_solutions()
        self.assertEqual(len(rows), 13)
        self.assertEqual(
            [item["c_minus_two"] for item in rows],
            list(range(13)),
        )
        for item in rows:
            self.assertEqual(
                item["a_plus_one"]
                + item["b_minus_one"]
                + item["c_minus_two"]
                + item["z_zero"],
                230,
            )

    def test_trace_pairs_exact(self) -> None:
        expected = {
            (4, 2): [(12, 48)],
            (4, 4): [],
            (4, 6): [],
            (12, 2): [(18, 42)],
            (12, 4): [(24, 36)],
            (12, 6): [(24, 36)],
            (20, 2): [(30, 30)],
            (20, 4): [(30, 30)],
            (20, 6): [(36, 24)],
            (28, 2): [(36, 24)],
            (28, 4): [(36, 24)],
            (28, 6): [(42, 18)],
            (36, 2): [(42, 18)],
            (36, 4): [(48, 12)],
            (36, 6): [(48, 12)],
        }
        self.assertEqual(
            {
                key: check.trace_pairs(*key)
                for key in check.exceptional_block_types()
            },
            expected,
        )

    def test_census_counts(self) -> None:
        summary = self.result["census_summary"]
        self.assertEqual(summary["candidate_types"], 15)
        self.assertEqual(summary["excluded_types"], 14)
        self.assertEqual(summary["surviving_types"], 1)
        self.assertEqual(
            summary["obstruction_counts"],
            {
                "blockwise_AM_GM_and_trace_residue": 2,
                "exceptional_block_logarithmic_cap": 7,
                "complement_block_logarithmic_cap": 1,
                "log_equality_integral_split_signature_veto": 4,
            },
        )

    def test_wave29_type_is_strictly_excluded(self) -> None:
        item = check.classify_type(12, 6)
        self.assertEqual(item["amgm_trace_pairs"], [{"traceB_A": 24, "traceB_R": 36}])
        self.assertEqual(item["detB_A"], 3645)
        self.assertEqual(item["log_cap_A"], 729)
        self.assertEqual(
            item["first_obstruction"],
            "exceptional_block_logarithmic_cap",
        )

    def test_equality_rank_vetoes(self) -> None:
        vetoed = {
            (int(item["rank_A"]), int(item["v3_detS_A"]))
            for item in self.result["decomposition_census"]
            if item.get("first_obstruction")
            == "log_equality_integral_split_signature_veto"
        }
        self.assertEqual(vetoed, {(4, 2), (12, 4), (28, 2), (36, 4)})
        for item in self.result["decomposition_census"]:
            if (int(item["rank_A"]), int(item["v3_detS_A"])) in vetoed:
                equality = item["complement_log_equality"]
                self.assertFalse(equality["both_ranks_divisible_by_8"])
                self.assertIn(equality["image_rank"], (2, 4))

    def test_only_rank20_det729_survives(self) -> None:
        survivors = [
            item
            for item in self.result["decomposition_census"]
            if item["status"] == "SURVIVES_THIS_REDUCTION"
        ]
        self.assertEqual(len(survivors), 1)
        item = survivors[0]
        self.assertEqual(
            (
                item["rank_A"],
                item["rank_R"],
                item["v3_detS_A"],
                item["detS_R"],
            ),
            (20, 24, 6, 1),
        )

    def test_surviving_schur_blocks(self) -> None:
        blocks = self.result["surviving_boundary"]["schur_blocks"]
        self.assertEqual(
            blocks["A"],
            {"detQ": 5, "detB": 3645, "traceB": 36, "traceC": 8},
        )
        self.assertEqual(blocks["U"]["detB"], 1)
        self.assertEqual(blocks["U"]["traceB"], 24)
        self.assertTrue(blocks["U"]["B_equals_identity"])
        self.assertTrue(blocks["U"]["C_equals_zero"])

    def test_tensor_isometry_row_restriction(self) -> None:
        tensor = self.result["surviving_boundary"]["U_tensor_isometry"]
        self.assertEqual(tensor["cauchy_absolute_cubic_bound"], 8)
        self.assertEqual(tensor["allowed_c_minus_two_counts"], [9, 10, 11])
        self.assertEqual(tensor["sum_c_over_U_rows"], 1256)
        self.assertEqual(tensor["profile_count"], 62)
        self.assertEqual(
            tensor["profile_endpoints"],
            [
                {"n_c9": 4, "n_c10": 122, "n_c11": 0},
                {"n_c9": 65, "n_c10": 0, "n_c11": 61},
            ],
        )

    def test_surviving_internal_directed_counts(self) -> None:
        counts = self.result["surviving_boundary"]["U_tensor_isometry"][
            "aggregate_internal_directed_counts"
        ]
        self.assertEqual(
            counts,
            {
                "plus_one": 2776,
                "minus_one": 768,
                "minus_two": 1256,
                "zero": 10950,
            },
        )
        self.assertTrue(all(value % 2 == 0 for value in counts.values()))
        self.assertEqual(sum(counts.values()), 126 * 125)

    def test_scalar_spectrum_preserves_last_boundary(self) -> None:
        spectrum = self.result["surviving_boundary"]["scalar_spectral_control"]
        self.assertEqual(spectrum["traceC_A"], 8)
        self.assertEqual(spectrum["traceC_A_squared"], 10)
        self.assertEqual(spectrum["traceB_A"], 36)
        self.assertEqual(spectrum["detB_A"], 3645)
        self.assertIn("no lattice realization", spectrum["scope"])

    def test_lowered_minimum_hostile_control(self) -> None:
        control = self.result["hostile_controls"][
            "lower_both_block_minima_to_two"
        ]
        self.assertEqual(control["mixed_vector_norm"], 4)
        self.assertFalse(control["row_support_split_forced"])

    def test_missing_trace_residue_hostile_control(self) -> None:
        control = self.result["hostile_controls"][
            "omit_trace_multiple_of_six_in_wave29_type"
        ]
        self.assertEqual(control["trace_pair"], [28, 32])
        self.assertGreaterEqual(control["A_log_cap"], control["detB_A"])
        self.assertFalse(control["strict_contradiction"])

    def test_both_block_caps_are_active(self) -> None:
        controls = self.result["hostile_controls"]
        self.assertEqual(
            controls["use_only_exceptional_block_log_cap"][
                "surviving_type_count"
            ],
            6,
        )
        self.assertEqual(
            controls["omit_log_equality_integral_split"][
                "surviving_type_count"
            ],
            5,
        )

    def test_each_premise_deletion_fails_closed(self) -> None:
        full = set(check.ESSENTIAL_PREMISES)
        for missing in check.ESSENTIAL_PREMISES:
            with self.subTest(missing=missing):
                with self.assertRaises(check.PremiseError):
                    check.derive(full - {missing})

    def test_deterministic_lf_json(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            left = Path(directory) / "left.json"
            right = Path(directory) / "right.json"
            check.write_json(left, check.derive())
            check.write_json(right, check.derive())
            self.assertEqual(left.read_bytes(), right.read_bytes())
            data = left.read_bytes()
            self.assertTrue(data.endswith(b"\n"))
            self.assertNotIn(b"\r\n", data)
            self.assertEqual(json.loads(data), self.result)


if __name__ == "__main__":
    unittest.main()
