#!/usr/bin/env python3
"""Core tests for the independent Wave 30 general-h729 verifier."""

from __future__ import annotations

import json
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

import independent_check as check


class Wave30GeneralIndependentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = check.build_result()

    def test_blind_frozen_discovery_hashes(self) -> None:
        self.assertEqual(
            self.result["blind_frozen_discovery_hashes"],
            {key: value for key, value in sorted(check.DISCOVERY_ARTIFACTS.items())},
        )

    def test_current_prior_hashes(self) -> None:
        self.assertEqual(
            self.result["current_prior_hashes"],
            {key: value for key, value in sorted(check.CURRENT_PRIOR_ARTIFACTS.items())},
        )

    def test_submitted_replay_failure_is_preserved(self) -> None:
        replay = self.result["submitted_replay_gate"]
        self.assertEqual(replay["status"], "FAIL_STALE_FROZEN_INPUT")
        self.assertEqual(replay["submitted_unittest_observation"]["tests_run"], 0)
        self.assertEqual(
            replay["current_applicable_sha256"],
            check.CURRENT_PRIOR_ARTIFACTS[
                "verification/wave29-s0-frame-exclusion/audit.md"
            ],
        )
        self.assertNotEqual(
            replay["current_applicable_sha256"],
            replay["submitted_expected_sha256"],
        )

    def test_repair_file_list_is_explicit(self) -> None:
        self.assertEqual(
            self.result["submitted_replay_gate"]["files_requiring_recorded_repair"],
            check.REPAIR_FILES,
        )
        self.assertIn(
            "attempts/wave30-general-h729/artifact-manifest.sha256",
            check.REPAIR_FILES,
        )

    def test_endpoint_detq_is_unique(self) -> None:
        self.assertEqual(check.endpoint_detq_values(), [5])
        self.assertEqual(6525 // 729, 8)

    def test_row_alphabet_complete_and_exact(self) -> None:
        rows = check.row_alphabet()
        self.assertEqual(len(rows), 13)
        self.assertEqual(
            [item["minus_two"] for item in rows],
            list(range(13)),
        )
        for item in rows:
            a = item["plus_one"]
            b = item["minus_one"]
            c = item["minus_two"]
            z = item["zero"]
            self.assertEqual(4 + a - b - 2 * c, 0)
            self.assertEqual(16 + a + b + 4 * c, 84)
            self.assertEqual(a + b + c + z, 230)
            self.assertEqual(item["cubic_sum"], 60 - 6 * c)

    def test_arbitrary_many_complement_blocks_are_covered(self) -> None:
        complements = self.result["multi_block_complements"]
        self.assertIn([8, 8, 8, 8, 8], complements["4"])
        self.assertIn([8, 16, 16], complements["4"])
        self.assertIn([24], complements["20"])
        self.assertIn([8], complements["36"])
        for partitions in complements.values():
            for partition in partitions:
                self.assertTrue(all(rank % 8 == 0 for rank in partition))

    def test_fifteen_rank_determinant_types(self) -> None:
        self.assertEqual(
            check.determinant_exponent_options(),
            [
                (4, 2), (4, 4), (4, 6),
                (12, 2), (12, 4), (12, 6),
                (20, 2), (20, 4), (20, 6),
                (28, 2), (28, 4), (28, 6),
                (36, 2), (36, 4), (36, 6),
            ],
        )

    def test_trace_pair_census(self) -> None:
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
                pair: check.possible_trace_pairs(*pair)
                for pair in check.determinant_exponent_options()
            },
            expected,
        )

    def test_amgm_is_exact_integer_arithmetic(self) -> None:
        self.assertTrue(check.amgm_exact(24, 24, 1))
        self.assertFalse(check.amgm_exact(24, 23, 1))
        self.assertTrue(check.amgm_exact(12, 24, 3645))
        self.assertFalse(check.amgm_exact(12, 18, 3645))

    def test_log_series_rational_bounds(self) -> None:
        bounds = self.result["imported_hypothesis_checks"]["logarithmic_cap"][
            "strict_rational_bounds"
        ]
        self.assertGreater(Fraction(bounds["lower"]), Fraction(2, 3))
        self.assertLess(Fraction(bounds["upper"]), 2)
        self.assertTrue(bounds["implies_log3_gt_2_over_3"])
        self.assertTrue(bounds["implies_log3_lt_2"])

    def test_log_equality_cases_split_and_four_have_forbidden_ranks(self) -> None:
        equality_items = [
            item
            for item in self.result["classification_census"]
            if "R_log_equality_split" in item
        ]
        self.assertEqual(
            {
                (item["rank_A"], item["v3_detS_A"])
                for item in equality_items
            },
            {(4, 2), (12, 4), (20, 6), (28, 2), (36, 4)},
        )
        vetoed = [
            item
            for item in equality_items
            if item["obstruction"]
            == "integral_idempotent_even_unimodular_rank_veto"
        ]
        self.assertEqual(len(vetoed), 4)
        for item in vetoed:
            split = item["R_log_equality_split"]
            self.assertIn(split["image_rank"], (2, 4))
            self.assertFalse(split["image_signature_allowed"])

    def test_obstruction_counts(self) -> None:
        self.assertEqual(
            self.result["classification_summary"]["obstruction_counts"],
            {
                "exact_AM_GM_plus_trace_residue": 2,
                "A_characteristic_pseudodeterminant_cap": 7,
                "R_characteristic_pseudodeterminant_cap": 1,
                "integral_idempotent_even_unimodular_rank_veto": 4,
            },
        )

    def test_exactly_one_type_survives(self) -> None:
        survivors = [
            item
            for item in self.result["classification_census"]
            if item["status"] == "SURVIVES_THIS_REDUCTION"
        ]
        self.assertEqual(len(survivors), 1)
        self.assertEqual(
            (
                survivors[0]["rank_A"],
                survivors[0]["rank_R"],
                survivors[0]["v3_detS_A"],
            ),
            (20, 24, 6),
        )

    def test_surviving_frame_and_schur_data(self) -> None:
        blocks = self.result["surviving_boundary"]["decomposition"]
        self.assertEqual(blocks["A"]["rows"], 105)
        self.assertEqual(blocks["U"]["rows"], 126)
        self.assertEqual(blocks["A"]["detB"], 3645)
        self.assertEqual(blocks["A"]["traceB"], 36)
        self.assertEqual(blocks["U"]["detB"], 1)
        self.assertEqual(blocks["U"]["traceB"], 24)
        self.assertTrue(blocks["U"]["B_equals_identity"])
        self.assertTrue(blocks["U"]["C_equals_zero"])

    def test_tensor_profiles_are_complete(self) -> None:
        tensor = self.result["surviving_boundary"]["tensor_isometry"]
        self.assertEqual(tensor["allowed_minus_two_counts"], [9, 10, 11])
        self.assertEqual(tensor["sum_minus_two_counts"], 1256)
        self.assertEqual(tensor["profile_count"], 62)
        self.assertEqual(
            tensor["first_profile"],
            {"n9": 4, "n10": 122, "n11": 0},
        )
        self.assertEqual(
            tensor["last_profile"],
            {"n9": 65, "n10": 0, "n11": 61},
        )

    def test_directed_counts_are_symmetric_compatible(self) -> None:
        counts = self.result["surviving_boundary"]["tensor_isometry"][
            "internal_directed_totals"
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
        self.assertEqual(sum(counts.values()), 126 * 125)
        self.assertTrue(all(value % 2 == 0 for value in counts.values()))

    def test_scalar_control_keeps_last_type_open(self) -> None:
        control = self.result["surviving_boundary"]["scalar_hostile_control"]
        self.assertEqual(control["traceC"], 8)
        self.assertEqual(control["traceC2"], 10)
        self.assertEqual(control["traceB"], 36)
        self.assertEqual(control["detB"], 3645)
        self.assertIn("not a lattice", control["scope"])

    def test_status_wall_is_fail_closed(self) -> None:
        wall = self.result["status_wall"]
        self.assertTrue(all(status == "UNKNOWN" for status in wall.values()))
        self.assertEqual(
            self.result["verdict"]["publication_gate"],
            "FAIL_RECORDED_REPAIR_AND_REVERIFICATION_REQUIRED",
        )

    def test_deterministic_lf_json(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            left = Path(directory) / "left.json"
            right = Path(directory) / "right.json"
            check.write_json(left, check.build_result())
            check.write_json(right, check.build_result())
            first = left.read_bytes()
            second = right.read_bytes()
            self.assertEqual(first, second)
            self.assertTrue(first.endswith(b"\n"))
            self.assertNotIn(b"\r\n", first)
            self.assertEqual(json.loads(first), self.result)


if __name__ == "__main__":
    unittest.main()
