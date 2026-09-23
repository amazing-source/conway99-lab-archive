from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave127_wave129_independent", HERE / "independent_verify.py"
)
assert SPEC and SPEC.loader
VERIFY = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = VERIFY
SPEC.loader.exec_module(VERIFY)


class IndependentJacobiAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = VERIFY.build_results()

    def test_preinspection(self) -> None:
        self.assertEqual(
            self.data["preinspection"]["wave127-independent-jacobi-certificate"][
                "entries_checked"
            ],
            55,
        )
        self.assertEqual(
            self.data["preinspection"]["wave129-jacobi-stress"][
                "entries_checked"
            ],
            16,
        )

    def test_module_dimension_and_product_ranks(self) -> None:
        module = self.data["module_audit"]
        self.assertEqual(module["total_dimension"], 239)
        self.assertEqual(
            [row["dimension"] for row in module["rows"]],
            VERIFY.EXPECTED_DIMENSIONS,
        )
        self.assertTrue(
            all(row["product_rank"] == row["dimension"] for row in module["rows"])
        )

    def test_fricke_factor_and_cache_consistency(self) -> None:
        fricke = self.data["fricke_audit"]
        self.assertEqual(
            fricke["exponents_by_c"],
            {str(c): -3 - c for c in range(11)},
        )
        self.assertGreater(fricke["q0_exact_comparisons"], 0)
        self.assertGreater(fricke["cross_cache_exact_coefficients_compared"], 0)
        self.assertTrue(fricke["all_cache_truncations_match"])

    def test_six_exact_candidates(self) -> None:
        for cutoff, counts in VERIFY.EXPECTED_COUNTS.items():
            row = self.data["cutoffs"][str(cutoff)]
            self.assertEqual(
                row["classification"], "VERIFIED_EXACT_RATIONAL_FEASIBLE"
            )
            self.assertEqual(
                (
                    row["equalities_checked"],
                    row["inequalities_checked"],
                    row["tight_inequalities"],
                ),
                counts,
            )
            self.assertEqual(row["failed_equalities"], 0)
            self.assertEqual(row["failed_inequalities"], 0)

    def test_q28_remains_unknown(self) -> None:
        row = self.data["cutoffs"]["28"]
        self.assertEqual(row["classification"], "UNKNOWN")
        self.assertFalse(row["exact_primal_certificate"])
        self.assertFalse(row["exact_farkas_certificate"])

    def test_status_wall(self) -> None:
        status = self.data["status_wall"]
        self.assertFalse(status["rank28_excluded"])
        self.assertFalse(status["rank28_realized"])
        self.assertFalse(status["graph_constructed"])
        self.assertFalse(status["lattice_constructed"])
        self.assertEqual(status["Conway_99"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
