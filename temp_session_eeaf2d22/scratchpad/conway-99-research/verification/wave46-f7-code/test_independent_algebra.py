from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave46_independent_algebra_tested", HERE / "independent_algebra.py"
)
assert SPEC is not None and SPEC.loader is not None
ALGEBRA = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ALGEBRA)
RESULT = json.loads(
    (HERE / "independent-results.json").read_text(encoding="utf-8")
)


class IndependentAlgebraTests(unittest.TestCase):
    def test_rref_and_rank_are_over_f7(self) -> None:
        matrix = ((1, 2, 3), (2, 4, 6), (0, 1, 1))
        rref, pivots = ALGEBRA.rref_mod7(matrix)
        self.assertEqual(pivots, (0, 1))
        self.assertEqual(ALGEBRA.rank_mod7(matrix), 2)
        self.assertEqual(rref[0], (1, 0, 1))
        self.assertEqual(rref[1], (0, 1, 1))

    def test_endpoint_scalar_compositions(self) -> None:
        compositions = ALGEBRA.endpoint_scalar_compositions()
        self.assertEqual(len(compositions), 6)
        self.assertEqual(len(set(compositions)), 6)
        self.assertTrue(all(sum(record) == 231 for record in compositions))
        self.assertTrue(all(sum(record[1:]) == 69 for record in compositions))
        self.assertEqual(compositions[0], (162, 32, 0, 0, 1, 0, 36))
        self.assertEqual(
            RESULT["projector_consequences"][
                "certified_distinct_weight_69_words"
            ],
            1386,
        )

    def test_composition_mutation_is_detected(self) -> None:
        hostile = list(ALGEBRA.ENDPOINT_ROW_COMPOSITION)
        hostile[0] += 1
        with self.assertRaises(AssertionError):
            ALGEBRA.scale_composition(hostile, 1)
            ALGEBRA.require(sum(hostile) == 231, "composition total changed")

    def test_weight_compatibility_excludes_exactly_1_2_4(self) -> None:
        record = ALGEBRA.compatible_weights()
        self.assertEqual(record["excluded_positive"], [1, 2, 4])
        self.assertIn(3, record["compatible"])
        self.assertTrue(all(weight in record["compatible"] for weight in range(5, 232)))
        self.assertEqual(record["state_counts_by_weight"][-1], 49)

    def test_complete_moment_formulas_and_strict_slack(self) -> None:
        moments = ALGEBRA.theoretical_complete_moments(28)
        self.assertEqual(moments["degree_0"], 7**28)
        self.assertEqual(moments["degree_1"], [231 * 7**27] * 7)
        self.assertEqual(
            moments["degree_2"][0][1],
            231 * 230 * 7**26,
        )
        self.assertEqual(
            moments["degree_2"][0][0],
            231 * 7**27 + 231 * 230 * 7**26,
        )
        slack = ALGEBRA.moment_slack(28)
        self.assertGreater(slack["degree_0"], 0)
        self.assertGreater(slack["minimum_degree_1"], 0)
        self.assertGreater(slack["minimum_degree_2"], 0)

    def test_schur_cube_inverse_and_rank_floor(self) -> None:
        record = ALGEBRA.schur_cube_formal_record()
        self.assertEqual(record["claimed_inverse"], "2I+3M")
        self.assertEqual(
            record["formal_product_coefficients_mod7"],
            {"I": 1, "M": 0, "M_squared": 3},
        )
        self.assertEqual(record["symmetric_cube_dimensions"][10], 220)
        self.assertEqual(record["symmetric_cube_dimensions"][11], 286)
        self.assertEqual(record["minimum_code_rank"], 11)
        hostile_m_coefficient = (1 * 2 + 4 * 2) % 7
        self.assertNotEqual(hostile_m_coefficient, 0)

    def test_matrix_and_column_hostile_inputs(self) -> None:
        with self.assertRaises(AssertionError):
            ALGEBRA.validate_matrix([[0, 7]], canonical_entries=True)
        with self.assertRaises(AssertionError):
            ALGEBRA.validate_matrix([[1, 2], [3]], canonical_entries=True)
        with self.assertRaises(AssertionError):
            ALGEBRA.normalize_projective_column((0, 0, 0))
        first = ALGEBRA.normalize_projective_column((2, 4, 0))
        second = ALGEBRA.normalize_projective_column((1, 2, 0))
        self.assertEqual(first, second)

    def test_prompt_quarantine_and_status_wall(self) -> None:
        hostile = copy.deepcopy(RESULT)
        hostile["prompt_error_quarantine"]["accepted_as_assumption"] = True
        self.assertFalse(
            RESULT["prompt_error_quarantine"]["accepted_as_assumption"]
        )
        with self.assertRaises(AssertionError):
            ALGEBRA.validate_record(hostile)
        ALGEBRA.validate_record(RESULT)
        self.assertEqual(RESULT["status"]["endpoint_n3_4158"], "UNKNOWN")
        self.assertEqual(RESULT["status"]["Conway_99"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
