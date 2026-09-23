"""Tests for the independent q^3 full-level Jacobi reconstruction."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave124_jacobi_audit", HERE / "independent_jacobi_audit.py"
)
assert SPEC is not None and SPEC.loader is not None
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)

COMPARE_SPEC = importlib.util.spec_from_file_location(
    "wave124_compare", HERE / "compare_sealed.py"
)
assert COMPARE_SPEC is not None and COMPARE_SPEC.loader is not None
COMPARE = importlib.util.module_from_spec(COMPARE_SPEC)
COMPARE_SPEC.loader.exec_module(COMPARE)


class Wave124JacobiAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = AUDIT.audit()

    def test_generator_normalizations(self) -> None:
        aa, bb = AUDIT.generator_a(), AUDIT.generator_b()
        self.assertEqual([aa.get((0, r), 0) for r in (-1, 0, 1)], [1, -2, 1])
        self.assertEqual([bb.get((0, r), 0) for r in (-1, 0, 1)], [1, 10, 1])

    def test_full_level_dimensions(self) -> None:
        self.assertEqual(self.result["weak_monomial_count"], 34)
        self.assertEqual(self.result["holomorphic_dimension"], 18)
        self.assertEqual(self.result["cusp_dimension"], 17)

    def test_q3_replay(self) -> None:
        stored = json.loads(
            (HERE / "independent-jacobi-results.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(self.result, stored)

    def test_A_power_directions(self) -> None:
        rows = self.result["A_power_cusp_directions"]
        self.assertEqual([row["cusp_dimension"] for row in rows], [16, 14, 13, 11, 9])
        self.assertTrue(all(int(row["target_q1_r4"]) != 0 for row in rows))

    def test_support_clean_degree_eight_threshold_is_candidate(self) -> None:
        candidate = self.result["support_clean_threshold_candidate"]
        self.assertEqual(candidate["claim_label"], "CANDIDATE")
        self.assertEqual(
            [row["q1_r4_functional_nonzero"] for row in candidate["rows"]],
            [True, True, True, True, False],
        )

    def test_sealed_comparison(self) -> None:
        comparison = COMPARE.build_comparison()
        self.assertEqual(comparison["verdict"], "VERIFIED_WITH_CLARIFICATIONS")
        self.assertTrue(
            comparison["agreement"]["full_level_basis_vectors_exactly_equal"]
        )
        self.assertEqual(comparison["sealed_inventory_files_checked"], 12)


if __name__ == "__main__":
    unittest.main()
