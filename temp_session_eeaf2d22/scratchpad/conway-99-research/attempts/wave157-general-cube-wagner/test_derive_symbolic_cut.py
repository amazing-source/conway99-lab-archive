"""Regression tests for the Wave157 symbolic covariance derivation."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "derive_symbolic_cut.py"
RESULT = HERE / "exact-results.json"

SPEC = importlib.util.spec_from_file_location("wave157_symbolic", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class SymbolicCutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.regenerated = MODULE.derive()
        cls.stored = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_fixed_srg_and_six_set_data(self) -> None:
        roots = MODULE.root_embedding_derivation()
        self.assertEqual(roots["ordered_first_edges"], 1386)
        self.assertEqual(roots["ordered_second_edges_per_first_edge"], 732)
        self.assertEqual(roots["root_embedding_count"], 1_014_552)
        n9 = MODULE.static_n9_formula_check()
        self.assertEqual(n9["canonical_mask"], 1884)
        self.assertEqual(n9["expanded_formula"], "41580 - n3")

    def test_named_graph_masks(self) -> None:
        self.assertEqual(
            MODULE.named_order8_masks(),
            {"cube": 2022000, "wagner_mobius_ladder": 5683824},
        )

    def test_exhausted_union_coefficients(self) -> None:
        self.assertEqual(MODULE.candidate_classes(6), (1884,))
        self.assertEqual(MODULE.candidate_classes(7), ())
        self.assertEqual(MODULE.candidate_classes(8), (2022000, 5683824))
        self.assertEqual(MODULE.class_coefficients(1884, 6), (0, 8))
        self.assertEqual(MODULE.class_coefficients(2022000, 8), (0, 96))
        self.assertEqual(MODULE.class_coefficients(5683824, 8), (0, -32))

    def test_symbolic_and_endpoint_forms(self) -> None:
        symbolic = self.regenerated["symbolic_inequality"]
        self.assertEqual(
            symbolic["integer_form"],
            "41580 - n3 + 12*cube8 - 4*wagner8 >= 0",
        )
        self.assertEqual(
            self.regenerated["endpoint_specialization"]["primitive_form"],
            "18711 + 6*cube8 - 2*wagner8 >= 0",
        )
        self.assertFalse(
            self.regenerated["strict_upper_bound_analysis"][
                "implies_strict_bound_below_4158"
            ]
        )
        self.assertEqual(
            self.regenerated["strict_upper_bound_analysis"][
                "endpoint_zero_assignment_lhs"
            ],
            37422,
        )

    def test_sealed_mathematical_certificate(self) -> None:
        self.assertEqual(
            self.regenerated["mathematical_certificate_sha256"],
            self.stored["mathematical_certificate_sha256"],
        )
        for key in (
            "root_embedding_derivation",
            "six_set_formula",
            "candidate_union_masks",
            "first_moment_nonzeros",
            "quadratic_coefficients_before_division",
            "named_order8_masks",
            "symbolic_inequality",
            "endpoint_specialization",
            "strict_upper_bound_analysis",
            "conclusion",
        ):
            self.assertEqual(self.regenerated[key], self.stored[key])


if __name__ == "__main__":
    unittest.main()
