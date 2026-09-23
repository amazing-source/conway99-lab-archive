from __future__ import annotations

import importlib.util
import math
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


V = load("wave49_independent_tests", "independent_check.py")
C = load("wave49_comparison_tests", "comparison_check.py")


class Wave49Tests(unittest.TestCase):
    def test_01_frozen_outputs_validate(self) -> None:
        V.validate(V.strict_json(HERE / "independent-result.json"))
        C.validate(V.strict_json(HERE / "comparison.json"))

    def test_02_local_caps_reject_a_mutated_graph(self) -> None:
        cycle5 = V.mask_from_edges(5, ((0, 1), (1, 2), (2, 3), (3, 4), (4, 0)))
        complete4 = V.mask_from_edges(4, itertools_combinations(range(4), 2))
        self.assertTrue(V.locally_admissible(cycle5, 5))
        self.assertFalse(V.locally_admissible(complete4, 4))

    def test_03_edge_order_and_canonical_relabelling_are_sensitive(self) -> None:
        root = 29
        permutation = (1, 0, 2, 3, 4)
        transformed = V.transform_mask(root, V.edge_map_for_permutation(permutation))
        self.assertNotEqual(root, transformed)
        self.assertIn(transformed, range(1 << 10))
        wrong_map = tuple(reversed(V.edge_map_for_permutation(permutation)))
        self.assertNotEqual(
            V.transform_mask(root, wrong_map),
            transformed,
        )

    def test_04_attachment_map_is_a_true_bijection(self) -> None:
        root = 29
        permutation = (2, 4, 1, 0, 3)
        target = V.transform_mask(root, V.edge_map_for_permutation(permutation))
        source_flags = V.attachment_universe(root)
        mapped = [V.permute_attachment(flag, permutation) for flag in source_flags]
        self.assertEqual(set(mapped), set(V.attachment_universe(target)))
        mutated = list(mapped)
        mutated[-1] = mutated[0]
        self.assertNotEqual(len(set(mutated)), len(mutated))

    def test_05_same_and_distinct_free_conventions_are_separated(self) -> None:
        coefficients = V.strict_json(HERE / "independent-coefficients.json")
        family = next(item for item in coefficients["families"] if item["root_mask"] == 0)
        for record in family["order6"]:
            self.assertTrue(all(row == column for row, column, _value in record["upper_entries"]))
        self.assertTrue(
            any(
                row != column
                for record in family["order7"]
                for row, column, _value in record["upper_entries"]
            )
        )

    def test_06_raw_totals_exclude_automorphism_division(self) -> None:
        result = V.strict_json(HERE / "independent-result.json")
        tensor = result["families"]["tensor_summary"]
        self.assertEqual(tensor["order6_raw_total_per_class"], math.perm(6, 5))
        self.assertEqual(tensor["order7_raw_total_per_class"], 2 * math.perm(7, 5))
        self.assertEqual(tensor["automorphism_division"], "none")

    def test_07_payload_support_matrix_and_direction_mutations_change_evidence(self) -> None:
        payload = {"root": 7, "entries": [[0, 0, 3], [0, 1, 2]]}
        mutated = {"root": 7, "entries": [[0, 0, 4], [0, 1, 2]]}
        self.assertNotEqual(V.object_hash(payload), V.object_hash(mutated))
        support = [{"canonical_mask": 0, "count": 5}]
        altered_support = [{"canonical_mask": 0, "count": 6}]
        self.assertNotEqual(V.object_hash(support), V.object_hash(altered_support))
        matrix = [[1, 3], [3, 1]]
        direction = [1, -1]
        self.assertEqual(V.quadratic(matrix, direction), -4)
        self.assertNotEqual(
            V.quadratic(matrix, [1, 0]),
            V.quadratic(matrix, direction),
        )

    def test_08_numerical_sdp_is_explicitly_non_evidence(self) -> None:
        comparison = V.strict_json(HERE / "comparison.json")
        numerical = comparison["numerical_sdp"]
        self.assertFalse(numerical["opened_for_mathematical_evidence"])
        self.assertFalse(numerical["solver_status_used_as_evidence"])
        self.assertFalse(numerical["floating_duals_used_as_evidence"])
        self.assertFalse(numerical["residuals_used_as_evidence"])
        self.assertFalse(numerical["eigenvalue_margins_used_as_evidence"])


def itertools_combinations(values, size):
    import itertools

    return itertools.combinations(values, size)


if __name__ == "__main__":
    unittest.main()
