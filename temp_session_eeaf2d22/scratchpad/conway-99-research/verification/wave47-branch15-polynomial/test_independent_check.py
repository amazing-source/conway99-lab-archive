from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent


def load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


V = load("wave47_independent_tests", "independent_check.py")
C = load("wave47_comparison_tests", "comparison_check.py")


class Wave47IndependentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        certificate = V.strict_json(V.CLOSURE_CERT)
        cls.assignments = {
            int(item["variable"]): bool(item["value"])
            for item in certificate["derivations"]
        }
        cls.windows = V.windows(cls.assignments)

    def test_01_frozen_results_validate(self) -> None:
        V.validate(V.strict_json(HERE / "independent-result.json"))
        C.validate(V.strict_json(HERE / "comparison.json"))

    def test_02_parser_preserves_signs_operators_and_polarities(self) -> None:
        row = V.parse_constraint(b"-2 ~x7 +3 x11 <= -4 ;\n")
        self.assertEqual(row.operator, "<=")
        self.assertEqual(row.bound, -4)
        self.assertEqual(
            [(term.coefficient, term.variable, term.positive) for term in row.terms],
            [(-2, 7, False), (3, 11, True)],
        )
        with self.assertRaises(ValueError):
            V.parse_constraint(b"+1 x7 +1 ~x7 >= 1 ;\n")

    def test_03_literal_polarity_and_affine_constant_mutations_change_rows(self) -> None:
        mapping = V.monomial_map((10, 20))
        negative = V.clause_polynomial(((10, False), (20, False)), mapping)
        flipped = V.clause_polynomial(((10, True), (20, False)), mapping)
        self.assertNotEqual(negative, flipped)
        self.assertNotEqual(negative, negative ^ 1)

    def test_04_complete_slice_and_target_mutations_are_detected(self) -> None:
        terms = V.local_terms(4)
        full = [
            V.evaluation_row(frozenset(chosen), terms)
            for chosen in __import__("itertools").combinations(range(4), 2)
        ]
        omitted = full[:-1]
        _full_rref, full_kernel = V.nullspace(full, len(terms))
        _omit_rref, omit_kernel = V.nullspace(omitted, len(terms))
        target_one = [
            V.evaluation_row(frozenset((chosen,)), terms) for chosen in range(4)
        ]
        _one_rref, one_kernel = V.nullspace(target_one, len(terms))
        self.assertNotEqual(full_kernel, omit_kernel)
        self.assertNotEqual(full_kernel, one_kernel)

    def test_05_missing_linear_multiplication_loses_a_consequence(self) -> None:
        mapping = V.monomial_map((1, 2))
        x = 1 << 1
        y = 1 << 2
        xy = 1 << mapping.pair_position[(0, 1)]
        initial = V.XorBasis((x, y ^ xy))
        self.assertEqual(len(initial.linear_rows(2)), 1)
        saturated, _history = V.saturate((x, y ^ xy), mapping)
        self.assertEqual(len(saturated.linear_rows(2)), 2)

    def test_06_cross_window_support_is_not_silently_localized(self) -> None:
        labels, _edges, variable = V.scaffold()
        first = labels.index((0, 2))
        second = labels.index((1, 3))
        edge_variable = variable[tuple(sorted((first, second)))]
        memberships = V.window_memberships((edge_variable,), self.windows)
        self.assertEqual(memberships, [0, 1])
        self.assertNotEqual(len(memberships), 1)

    def test_07_wave43_partition_and_hash_commitments_are_exact(self) -> None:
        result = V.strict_json(HERE / "independent-result.json")
        partition = result["wave43_degree_four_partition"]
        self.assertEqual(partition["active_rows"], 34_340)
        self.assertEqual(
            partition["per_window_counts"],
            [4_141, 0, 5_959, 6_060, 6_060, 6_060, 6_060],
        )
        comparison = V.strict_json(HERE / "comparison.json")
        self.assertEqual(comparison["mismatches"], [])
        for window in comparison["windows"]:
            self.assertEqual(len(window["hashes"]), 5)
            self.assertEqual(window["mismatches"], [])


if __name__ == "__main__":
    unittest.main()
