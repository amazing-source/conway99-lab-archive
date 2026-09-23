#!/usr/bin/env python3
"""Tests for the independent Wave 26 A2 cubic checker."""

from __future__ import annotations

import json
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

import independent_check as check


class PublicInputTests(unittest.TestCase):
    def test_all_frozen_hashes_match(self) -> None:
        results = check.verify_public_hashes()
        self.assertEqual(set(results), set(check.PUBLIC_INPUTS))
        self.assertTrue(all(item["match"] for item in results.values()))

    def test_checker_does_not_name_discovery_paths(self) -> None:
        source = Path(check.__file__).read_text(encoding="utf-8")
        self.assertNotIn("agents/2026-07-23-wave26-a2-cubic-obstruction.md", source)
        self.assertNotIn("attempts/wave26-a2-cubic-obstruction/", source)


class A2ArithmeticTests(unittest.TestCase):
    def test_roots_and_no_norm_four(self) -> None:
        result = check.root_enumeration()
        self.assertEqual(len(result["norm_two_roots"]), 6)
        self.assertEqual(result["norm_four_vectors"], [])
        self.assertEqual(
            sorted(check.a2_norm(root) for root in result["norm_two_roots"]),
            [2] * 6,
        )

    def test_frame_forces_seven_per_unoriented_line(self) -> None:
        result = check.frame_line_counts()
        self.assertEqual(result["frame_block"], [[14, 7], [7, 14]])
        self.assertEqual(result["unique_unoriented_line_counts"], [7, 7, 7])
        self.assertEqual(result["total_nonzero_a2_rows"], 21)

    def test_wrong_covariant_frame_block_is_rejected(self) -> None:
        correct = check.frame_line_counts()["frame_block"]
        wrong = [[21 * entry for entry in row] for row in check.A2]
        self.assertNotEqual(correct, wrong)


class CubicFloorTests(unittest.TestCase):
    def test_exact_cubic_gram_and_floor(self) -> None:
        result = check.imbalance_floor()
        self.assertEqual(
            result["cubic_root_line_gram"],
            [[8, -1, 1], [-1, 8, 1], [1, 1, 8]],
        )
        self.assertEqual(result["exact_eigenvalues"], [6, 9, 9])
        self.assertEqual(result["minimum_without_M1_zero"], 18)
        self.assertEqual(
            result["minimizers_without_M1_zero"],
            [[-1, -1, 1], [1, 1, -1]],
        )

    def test_M1_zero_is_redundant_for_numeric_floor(self) -> None:
        result = check.imbalance_floor()
        self.assertFalse(result["M1_zero_required_for_bound"])
        self.assertEqual(result["minimum_with_M1_zero"], 18)
        self.assertEqual(result["dropped_M1_example"]["pure_cubic_norm"], 26)
        self.assertNotEqual(result["dropped_M1_example"]["first_moment"], [0, 0])

    def test_odd_line_counts_are_active(self) -> None:
        gram = check.cubic_gram()
        self.assertEqual(check.cubic_value((0, 0, 0), gram), 0)
        self.assertEqual(check.cubic_value((1, 1, -1), gram), 18)


class TensorConventionTests(unittest.TestCase):
    def test_ordered_tensor_factorization_and_compression(self) -> None:
        result = check.tensor_and_basis_checks()
        compression = result["orthogonal_compression"]
        self.assertEqual(
            compression["full_norm"],
            compression["AAA_norm"]
            + compression["AAR_norm"]
            + compression["ARA_norm"]
            + compression["ARR_norm"],
        )
        self.assertEqual(compression["AAR_norm"], compression["ARA_norm"])
        self.assertGreater(compression["AAR_norm"], 0)
        self.assertGreaterEqual(compression["full_norm"], compression["AAA_norm"])

    def test_basis_covariance_and_trace_invariance(self) -> None:
        result = check.tensor_and_basis_checks()["basis_covariance"]
        self.assertTrue(result["M_unchanged"])
        self.assertTrue(result["trace_unchanged"])
        self.assertEqual(result["Q_rule"], "Q'=P^-1 Q P^-T")

    def test_direct_trace_uses_A2_not_inverse_A2(self) -> None:
        scaled_dual = check.block_diagonal(check.A2, ((3,),))
        rows = [[1, 0, 1], [0, 1, -1], [1, 1, 0], [-1, 0, 1]]
        data = check.projector_data(rows, scaled_dual)
        q_block = check.submatrix(data["Q"], [0, 1], [0, 1])
        correct = check.trace_product(check.A2, q_block)
        wrong = check.trace_product(check.inverse(check.A2), q_block)
        self.assertNotEqual(correct, wrong)

    def test_ordered_tensor_kronecker_identity(self) -> None:
        s = check.block_diagonal(check.A2, ((3,),))
        x = [1, -2, 3]
        y = [-1, 1, 2]
        left = [a * b for a in x for b in x]
        right = [a * b for a in y for b in y]
        self.assertEqual(
            check.quadratic(left, check.kronecker(s, s), right),
            check.quadratic(x, s, y) ** 2,
        )


class HostileControlTests(unittest.TestCase):
    def test_dropping_frame_can_destroy_floor_even_with_M1_zero(self) -> None:
        result = check.dropped_frame_control()
        self.assertEqual(result["column_rank"], 4)
        self.assertEqual(result["all_row_norms"], 4)
        self.assertTrue(result["M1_zero"])
        self.assertFalse(result["tight_frame_holds"])
        self.assertEqual(result["trace_A2_Q_AA"], 0)
        self.assertTrue(result["also_violates_public_off_diagonal_alphabet"])


class SurvivorTests(unittest.TestCase):
    def test_both_survivor_A2_blocks_have_trace_ten(self) -> None:
        result = check.survivor_check()
        self.assertEqual(result["orthogonal_A2_block_starts_zero_based"], [40, 42])
        self.assertEqual(result["trace_A2_Q_AA"], [10, 10])
        self.assertEqual(result["deficit_per_block"], [8, 8])
        self.assertFalse(result["full_projector_Schur_origin_for_this_survivor"])

    def test_trace_A2_squared_is_ten(self) -> None:
        self.assertEqual(check.trace_product(check.A2, check.A2), Fraction(10))


class OutputTests(unittest.TestCase):
    def test_full_result_has_scope_walls(self) -> None:
        result = check.build_result()
        self.assertEqual(result["claim_label"], "VERIFIED")
        conclusions = result["conclusions"]
        self.assertEqual(conclusions["trace_A2_Q_AA_minimum"], 18)
        self.assertEqual(conclusions["wave24_survivor_trace"], 10)
        self.assertFalse(conclusions["all_h9_forms_excluded"])
        self.assertFalse(conclusions["n3_708_excluded"])
        self.assertFalse(conclusions["Conway_99_resolved"])

    def test_json_is_deterministic_and_LF_only(self) -> None:
        result = check.build_result()
        with tempfile.TemporaryDirectory() as temporary:
            first = Path(temporary) / "first.json"
            second = Path(temporary) / "second.json"
            check.write_json(first, result)
            check.write_json(second, result)
            first_bytes = first.read_bytes()
            self.assertEqual(first_bytes, second.read_bytes())
            self.assertNotIn(b"\r", first_bytes)
            parsed = json.loads(first_bytes)
            self.assertEqual(parsed["verdict"], "PASS_SCOPED_A2_CUBIC_OBSTRUCTION")


if __name__ == "__main__":
    unittest.main()
