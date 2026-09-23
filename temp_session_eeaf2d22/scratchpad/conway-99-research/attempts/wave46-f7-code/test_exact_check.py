#!/usr/bin/env python3
"""Discovery-side regression and hostile-control tests for Wave 46."""

from __future__ import annotations

import copy
import importlib.util
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave46_exact_check", HERE / "exact_check.py"
)
assert SPEC and SPEC.loader
CHECK = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CHECK
SPEC.loader.exec_module(CHECK)


class Wave46ExactCheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = CHECK.compute()

    def test_result_validates_without_status_inflation(self) -> None:
        CHECK.validate(self.result)
        self.assertEqual(
            self.result["claim_label"],
            "DERIVED_NULL_RESULT_PENDING_VERIFICATION",
        )
        self.assertEqual(self.result["conclusion"]["endpoint_n3_4158"], "UNKNOWN")
        self.assertEqual(self.result["conclusion"]["conway_99"], "UNKNOWN")

    def test_correct_object_and_prompt_error_are_separated(self) -> None:
        self.assertEqual(self.result["corrected_object"]["matrix"], "M=21E_0")
        quarantine = self.result["prompt_error_control"]
        self.assertEqual(quarantine["determinant_mod_7"], 3)
        self.assertFalse(quarantine["used_in_live_conclusion"])

    def test_endpoint_scalar_orbit_has_exact_congruences(self) -> None:
        compositions = CHECK.endpoint_scalar_compositions()
        self.assertEqual(len(compositions), 6)
        self.assertEqual(len(set(compositions)), 6)
        for composition in compositions:
            self.assertEqual(sum(composition), 231)
            self.assertEqual(
                sum(symbol * count for symbol, count in enumerate(composition))
                % 7,
                0,
            )
            self.assertEqual(
                sum(
                    symbol * symbol * count
                    for symbol, count in enumerate(composition)
                )
                % 7,
                0,
            )
        self.assertEqual(self.result["code"]["A69_lower_bound"], 1386)

    def test_sum_and_norm_forbid_exactly_three_weights(self) -> None:
        allowed = set(CHECK.allowed_weights())
        forbidden = [
            weight for weight in range(CHECK.N + 1) if weight not in allowed
        ]
        self.assertEqual(forbidden, [1, 2, 4])

    def test_local_positive_control_is_exact(self) -> None:
        columns = CHECK.local_affine_columns()
        self.assertEqual(len(columns), 21)
        self.assertEqual(
            CHECK.local_weight_enumerator(columns),
            {0: 1, 12: 126, 14: 18, 18: 1470, 19: 756, 21: 30},
        )

    def test_positive_controls_cover_every_endpoint_rank(self) -> None:
        controls = self.result["ordinary_enumerator_positive_controls"]
        records = controls["records"]
        self.assertEqual(
            [record["dimension"] for record in records],
            list(range(28, 45)),
        )
        self.assertEqual(controls["four_block_A69"], 668_653_683_264)
        for record in records:
            self.assertEqual(record["length"], 231)
            self.assertEqual(record["projective_columns"], 231)
            self.assertTrue(record["self_orthogonal"])
            self.assertTrue(record["all_generator_row_sums_zero"])
            self.assertEqual(
                record["projection_sha256"],
                CHECK.compact_hash(record["projection_matrix"]),
            )

    def test_complete_moments_have_strict_slack_at_rank_28(self) -> None:
        moments = self.result["complete_enumerator"][
            "degree_0_1_2_moment_check"
        ]
        self.assertEqual(moments["minimum_tested_dimension"], 28)
        self.assertGreater(moments["minimum_first_moment_slack"], 0)
        self.assertGreater(moments["minimum_second_moment_slack"], 0)
        self.assertEqual(
            moments["degree_0_1_2_complete_moments"],
            "PASS_WITH_STRICT_SLACK",
        )

    def test_schur_cube_floor_is_only_eleven(self) -> None:
        schur = self.result["schur_cube"]
        self.assertEqual(schur["row_code_third_schur_power_dimension"], 231)
        self.assertEqual(schur["derived_rank_floor"], 11)
        self.assertIn("superseded", schur["comparison_to_current_endpoint_floor"])

    def test_hostile_status_promotion_is_rejected(self) -> None:
        hostile = copy.deepcopy(self.result)
        hostile["conclusion"]["ordinary_weight_enumerator_contradiction"] = True
        with self.assertRaisesRegex(ValueError, "status inflation"):
            CHECK.validate(hostile)

    def test_hostile_projection_certificate_is_rejected(self) -> None:
        hostile = copy.deepcopy(self.result)
        hostile["ordinary_enumerator_positive_controls"]["records"][0][
            "projection_matrix"
        ][0][0] ^= 1
        with self.assertRaisesRegex(ValueError, "positive control failed"):
            CHECK.validate(hostile)

    def test_hostile_prompt_error_escape_is_rejected(self) -> None:
        hostile = copy.deepcopy(self.result)
        hostile["prompt_error_control"]["used_in_live_conclusion"] = True
        with self.assertRaisesRegex(ValueError, "escaped quarantine"):
            CHECK.validate(hostile)


if __name__ == "__main__":
    unittest.main()
