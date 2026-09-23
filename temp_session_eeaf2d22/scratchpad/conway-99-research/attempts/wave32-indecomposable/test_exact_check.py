#!/usr/bin/env python3
"""Hostile tests for the Wave 32 indecomposable-branch reductions."""

from __future__ import annotations

import hashlib
import importlib.util
import tempfile
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave32_indecomposable_exact", HERE / "exact_check.py"
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load exact_check.py")
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class Wave32IndecomposableTests(unittest.TestCase):
    def test_frozen_inputs(self) -> None:
        self.assertEqual(CHECK.validate_inputs(), CHECK.FROZEN_INPUTS)

    def test_rootless_block_support_and_coordinate_sizes(self) -> None:
        result = CHECK.block_support_arithmetic()
        self.assertEqual(
            result["coordinate_block_divisibility"][
                "simultaneous_sizes_between_0_and_231"
            ],
            [0, 231],
        )
        self.assertFalse(result["uses_h_729"])

    def test_endpoint_pair_counts(self) -> None:
        result = CHECK.endpoint_pair_counts(708)
        self.assertEqual(result["sum_q"], 472)
        self.assertEqual(
            result["all_unordered_M_pair_counts"],
            {"+1": 2546, "0": 22161, "-1": 708, "-2": 1150},
        )

    def test_unique_three_row_root_motif(self) -> None:
        result = CHECK.three_row_motif()
        self.assertEqual(result["unique_norm_two_edge_multiset"], [-2, -2, -1])
        self.assertEqual(result["canonical_sum_vector_norm"], 2)
        self.assertEqual(result["canonical_leading_principal_minors"], [4, 12, 20])

    def test_mutating_minus_one_to_plus_one_removes_root(self) -> None:
        gram = [[4, -2, -2], [-2, 4, 1], [-2, 1, 4]]
        norm = sum(gram[i][j] for i in range(3) for j in range(3))
        self.assertEqual(norm, 6)

    def test_trace_detector_normalization(self) -> None:
        result = CHECK.motif_trace_detector()
        self.assertEqual(result["one_motif_hostile_example_trace"], 2)
        self.assertEqual(result["actual_target_value"], "UNKNOWN")

    def test_full_size_binary_hostile_control(self) -> None:
        result = CHECK.binary_hostile_control()
        self.assertEqual(result["row_count"], 231)
        self.assertEqual(result["rank_X"], 44)
        self.assertEqual(result["projector_rank"], 44)
        self.assertTrue(result["projector_idempotent"])
        self.assertTrue(result["all_rows_quadratically_singular"])

    def test_primitivity_is_active(self) -> None:
        result = CHECK.hostile_premise_controls()
        self.assertEqual(result["drop_primitivity"]["row_lattice"], "2Z, not Z")

    def test_status_wall(self) -> None:
        status = CHECK.build_result()["status"]
        self.assertEqual(
            status["surviving_rootless_endpoint_must_be_indecomposable"],
            "DERIVED",
        )
        self.assertEqual(
            status["actual_incidence_forces_forbidden_motif"], "UNKNOWN"
        )
        self.assertEqual(status["n3_708"], "UNKNOWN")
        self.assertEqual(status["Conway_99"], "UNKNOWN")

    def test_deterministic_json(self) -> None:
        value = CHECK.build_result()
        expected = CHECK.render(value).encode("utf-8")
        self.assertEqual((HERE / "exact-results.json").read_bytes(), expected)
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "result.json"
            CHECK.write_json(target, value)
            actual = target.read_bytes()
        self.assertEqual(actual, expected)
        self.assertEqual(
            hashlib.sha256(actual).hexdigest(),
            hashlib.sha256(expected).hexdigest(),
        )


if __name__ == "__main__":
    unittest.main()
