from __future__ import annotations

import importlib.util
import itertools
import json
import math
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave43_seven_deck_independent",
    HERE / "independent_check.py",
)
assert SPEC is not None and SPEC.loader is not None
CHECKER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CHECKER
SPEC.loader.exec_module(CHECKER)


class IndependentVerifierTests(unittest.TestCase):
    def test_small_complete_catalogue(self) -> None:
        catalogue = CHECKER.build_complete_catalogue(3)
        self.assertEqual(catalogue.classes, (0, 1, 3, 7))
        self.assertEqual(sum(catalogue.orbit_sizes), 8)
        self.assertEqual(set(catalogue.canonical_by_labelled_mask), set(catalogue.classes))

    def test_local_admissibility_hostiles(self) -> None:
        k4 = CHECKER.mask_from_edges(4, itertools.combinations(range(4), 2))
        k23 = CHECKER.mask_from_edges(
            5,
            ((left, right) for left in (0, 1) for right in (2, 3, 4)),
        )
        self.assertFalse(CHECKER.locally_admissible(k4, 4))
        self.assertFalse(CHECKER.locally_admissible(k23, 5))
        self.assertTrue(CHECKER.locally_admissible(0, 7))

    def test_endpoint_formulae(self) -> None:
        six = CHECKER.evaluate_integral(CHECKER.six_formulae(), CHECKER.N3)
        seven = CHECKER.evaluate_integral(
            CHECKER.seven_formulae(), CHECKER.N3, CHECKER.H11
        )
        self.assertEqual(len(six), 62)
        self.assertEqual(len(seven), 19)
        self.assertEqual(sum(six), math.comb(99, 6))
        self.assertEqual(six[:4], (0, 8316, 4158, 8316))
        self.assertEqual(seven[0], 1189188)
        self.assertEqual(seven[11], 16632)
        self.assertEqual(seven[17:], (0, 0))

    def test_frozen_result_scope_and_controls(self) -> None:
        result = json.loads((HERE / "independent-result.json").read_text(encoding="utf-8"))
        self.assertEqual(result["claim_label"], "VERIFIED")
        self.assertEqual(result["catalogues"]["order_6"]["all_unlabeled_classes"], 156)
        self.assertEqual(result["catalogues"]["order_7"]["all_unlabeled_classes"], 1044)
        self.assertEqual(result["model"]["seven_vertex_classes"], 208)
        self.assertEqual(result["certificate"]["support_size"], 99)
        self.assertTrue(result["certificate"]["all_deck_residuals_zero"])
        self.assertTrue(result["certificate"]["all_hamiltonian_residuals_zero"])
        self.assertTrue(result["certificate"]["all_prism_containing_classes_zero"])
        self.assertFalse(result["conclusion"]["graph_construction"])
        self.assertEqual(result["conclusion"]["endpoint_n3_4158"], "UNKNOWN")
        self.assertTrue(
            all(record["outcome"] == "REJECTED" for record in result["controls"]["hostile"])
        )


if __name__ == "__main__":
    unittest.main()
