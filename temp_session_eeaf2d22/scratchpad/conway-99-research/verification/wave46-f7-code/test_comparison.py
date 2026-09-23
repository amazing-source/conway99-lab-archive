from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave46_sealed_comparison_tested", HERE / "compare_sealed.py"
)
assert SPEC is not None and SPEC.loader is not None
COMPARE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = COMPARE
SPEC.loader.exec_module(COMPARE)
RESULT = json.loads(
    (HERE / "comparison-results.json").read_text(encoding="utf-8")
)


class SealedComparisonTests(unittest.TestCase):
    def test_projector_code_consequences(self) -> None:
        code = RESULT["projector_code"]
        self.assertEqual(code["conditional_identity_derivation"], "VERIFIED")
        self.assertTrue(code["self_orthogonal"])
        self.assertTrue(code["contained_in_one_perp"])
        self.assertEqual(code["projective_columns"], 231)
        self.assertEqual(code["dual_distance_lower_bound"], 3)
        self.assertEqual(code["A69_lower_bound"], 1386)
        self.assertEqual(code["excluded_weights"], [1, 2, 4])
        self.assertEqual(len(set(map(tuple, code["endpoint_scalar_compositions"]))), 6)

    def test_falling_complete_moments_and_basis_correction(self) -> None:
        moments = RESULT["complete_moments"]
        self.assertEqual(moments["rank"], 28)
        self.assertEqual(
            moments["minimum_first_slack"],
            15179555705976418712009901,
        )
        self.assertEqual(
            moments["minimum_second_slack"],
            498756830339225186222981718,
        )
        self.assertGreater(
            moments["prefreeze_raw_monomial_minimum_second_slack"],
            moments["minimum_second_slack"],
        )
        self.assertTrue(
            moments["all_56_nonconstant_symbol_and_pair_checks_strict"]
        )

    def test_schur_cube_inverse_and_floor(self) -> None:
        schur = RESULT["schur_cube"]
        self.assertEqual(schur["identity"], "VERIFIED")
        self.assertEqual(schur["inverse"], "2I+3M")
        self.assertEqual(schur["rank"], 231)
        self.assertEqual(schur["rank_floor"], 11)
        self.assertTrue(schur["superseded_by_endpoint_floor_28"])

    def test_all_seventeen_positive_controls(self) -> None:
        controls = RESULT["positive_controls"]
        self.assertEqual(controls["rank_interval"], list(range(28, 45)))
        self.assertEqual(controls["controls_checked"], 17)
        self.assertEqual(
            controls["local_columns_sha256"],
            "c663813eef11abeecae24cb3b1ac48cf774e7037b814d5333d1f307a815037a2",
        )
        self.assertEqual(
            controls["all_projection_matrices_sha256"],
            "9bc5d02ba9c4a522a1ac8355002e3229ead59e166ea7a8fccbddab8ce45342e1",
        )
        for expected_rank, record in zip(range(28, 45), controls["records"]):
            self.assertEqual(record["dimension"], expected_rank)
            self.assertEqual(record["projection_rank"], expected_rank - 16)
            self.assertEqual(record["generator_rank"], expected_rank)
            self.assertEqual(record["projective_columns"], 231)
            self.assertTrue(record["row_sums_zero"])
            self.assertTrue(record["gram_zero"])
            self.assertEqual(record["endpoint_scalar_composition_hits"], 0)

    def test_local_weight_enumerator_and_A69(self) -> None:
        controls = RESULT["positive_controls"]
        self.assertEqual(
            controls["local_weight_enumerator"],
            {
                "0": 1,
                "12": 126,
                "14": 18,
                "18": 1470,
                "19": 756,
                "21": 30,
            },
        )
        self.assertEqual(
            controls["inherited_A69_lower_bound"],
            668_653_683_264,
        )
        self.assertTrue(controls["all_endpoint_scalar_composition_hits_zero"])

    def test_prompt_error_is_correct_and_quarantined(self) -> None:
        prompt = RESULT["prompt_error_quarantine"]
        self.assertEqual(prompt["A_plus_3I_order"], 99)
        self.assertEqual(
            prompt["shifted_eigenvalues"],
            [[17, 1], [6, 54], [-1, 44]],
        )
        self.assertEqual(prompt["determinant_mod_7"], 3)
        self.assertTrue(prompt["full_F7_99_row_code"])
        self.assertFalse(prompt["used_in_live_conclusion"])
        self.assertEqual(prompt["status"], "VERIFIED_QUARANTINED")

    def test_all_hostile_mutations_are_rejected(self) -> None:
        hostile = RESULT["hostile_mutations"]
        self.assertEqual(
            hostile["single_projection_entry"]["outcome"], "REJECTED"
        )
        self.assertEqual(hostile["endpoint_row_composition"], "REJECTED")
        self.assertEqual(
            hostile["schur_inverse_M_coefficient_3_to_2"], "REJECTED"
        )
        self.assertEqual(
            hostile["prompt_quarantine_false_to_true"], "REJECTED"
        )
        self.assertEqual(hostile["rank_label_28_to_29"], "REJECTED")

    def test_status_wall(self) -> None:
        COMPARE.validate_record(RESULT)
        verdict = RESULT["verdict"]
        self.assertEqual(verdict["scoped_derivations"], "VERIFIED")
        self.assertEqual(verdict["generic_positive_controls"], "VERIFIED")
        self.assertFalse(verdict["ordinary_enumerator_contradiction"])
        self.assertFalse(verdict["low_degree_complete_enumerator_contradiction"])
        self.assertEqual(verdict["endpoint_n3_4158"], "UNKNOWN")
        self.assertEqual(verdict["Conway_99"], "UNKNOWN")
        self.assertEqual(verdict["novelty"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
