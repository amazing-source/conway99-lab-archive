from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent


def load(name: str, filename: str):
    path = HERE / filename
    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


class Wave146Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.aggregate = load("wave146_test_aggregate", "aggregate_coupling_scout.py")
        cls.fixed = load("wave146_test_fixed", "fixed_witness_scout.py")
        cls.support = load("wave146_test_support", "seven_extendable_support.py")
        cls.exact = load("wave146_test_exact", "exact_witness.py")
        cls.wave144 = cls.support.load_wave144()
        cls.wave21 = cls.wave144.load_wave21()
        cls.wave22 = cls.fixed.load_module(
            "wave146_test_wave22",
            cls.fixed.WAVE22_PATH,
        )
        cls.masks = cls.fixed.source_masks(cls.wave21)

    def induced_seven_mask(self, six_mask: int, pattern: int) -> int:
        six_edges, _ = self.wave22.edge_data(6)
        _, seven_positions = self.wave22.edge_data(7)
        result = 0
        for edge_index, edge in enumerate(six_edges):
            if six_mask >> edge_index & 1:
                result |= 1 << seven_positions[edge]
        for vertex in range(6):
            if pattern >> vertex & 1:
                result |= 1 << seven_positions[(vertex, 6)]
        return result

    def test_pattern_filter_equals_order_seven_local_admissibility(self) -> None:
        for mask in self.masks:
            for pattern in range(64):
                expected = self.wave22.locally_admissible(
                    self.induced_seven_mask(mask, pattern),
                    7,
                )
                actual = self.aggregate.possible_pattern(
                    self.support,
                    self.wave144,
                    mask,
                    pattern,
                )
                self.assertEqual(actual, expected, (mask, pattern))

    def test_support_reduction_and_endpoint_cell_survival(self) -> None:
        result = self.support.build_result()
        self.assertEqual(result["summary"]["classes"], 62)
        self.assertEqual(result["summary"]["classes_with_removed_weights"], 16)
        self.assertEqual(result["summary"]["total_removed_weight_cells"], 25)
        self.assertEqual(result["summary"]["wave144_endpoint_positive_cells"], 65)
        self.assertEqual(result["summary"]["wave144_endpoint_unsupported_cells"], 0)
        self.assertEqual(result["wave144_endpoint_unsupported_cells"], [])

    def test_fixed_profile_two_row_contradiction(self) -> None:
        model = self.fixed.build_model()
        left = (37, 12)
        right = (38, 8)
        for vector in model["vectors"]:
            self.assertEqual(vector.get(right, 0), 2 * vector.get(left, 0))
        self.assertEqual(model["required"][left], 324456417)
        self.assertEqual(model["required"][right], 3724939122)
        self.assertEqual(
            model["required"][right] - 2 * model["required"][left],
            3076026288,
        )

    def test_exact_rational_endpoint_witness(self) -> None:
        replay = self.exact.verify(HERE / "exact-results.json")
        self.assertEqual(replay["verification"], "PASS")
        self.assertEqual(replay["variables"], 13973)
        self.assertEqual(replay["equalities"], 8981)
        self.assertEqual(replay["matrix_nonzeros"], 110269)
        self.assertEqual(replay["positive_variables"], 2998)
        self.assertEqual(replay["maximum_denominator"], 4)
        self.assertEqual(replay["h11"], "16632")


if __name__ == "__main__":
    unittest.main()
