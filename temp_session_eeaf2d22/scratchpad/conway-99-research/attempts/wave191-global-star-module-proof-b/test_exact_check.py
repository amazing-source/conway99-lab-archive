from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave191_exact_check", HERE / "exact_check.py"
)
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class Wave191ExactCheckTests(unittest.TestCase):
    def test_module_arithmetic(self) -> None:
        CHECK.check_module_arithmetic()

    def test_all_rank_only_controls(self) -> None:
        CHECK.check_all_rank_only_controls()

    def test_boundary_controls(self) -> None:
        gram = CHECK.hyperbolic_gram_45()
        for d, ell in ((12, 33), (28, 17)):
            u0 = CHECK.control_u0_basis(d)
            self.assertEqual(
                CHECK.rank_mod3(CHECK.restricted_gram(u0, gram)),
                11,
            )
            line_sum = CHECK.orthogonal_complement_basis(u0, gram)
            self.assertEqual(len(line_sum), ell)
            self.assertEqual(
                CHECK.rank_mod3(CHECK.restricted_gram(line_sum, gram)),
                2 * ell - 34,
            )

    def test_frozen_results(self) -> None:
        results = json.loads(
            (HERE / "exact-results.json").read_text(encoding="utf-8")
        )
        self.assertEqual(results["claim_label"], "DERIVED")
        self.assertEqual(results["incidence_rank_min"], 66)
        self.assertEqual(results["incidence_rank_max"], 82)
        self.assertFalse(results["rank_only_endpoint_exclusion"])
        self.assertEqual(results["rank_11_status"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
