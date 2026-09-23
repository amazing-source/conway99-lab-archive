"""Hostile and exact tests for the Wave 204 proof-B package."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("exact_check.py")
SPEC = importlib.util.spec_from_file_location("wave204_exact_check", MODULE_PATH)
assert SPEC and SPEC.loader
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class Wave204Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = CHECK.analyze()
        CHECK.verify(cls.data)

    def test_frozen_inputs(self) -> None:
        self.assertEqual(CHECK.verify_inputs(), CHECK.EXPECTED_INPUTS)

    def test_symbolic_compression_equals_direct_gram_reduction(self) -> None:
        for parts in ((6,), (4, 2), (3, 3), (2, 2, 2)):
            incidence = CHECK.cycle_biadjacency(parts)
            expected = CHECK.matrix_multiply(incidence, CHECK.transpose(incidence))
            self.assertEqual(CHECK.pair_compression(parts), expected)

    def test_full_trace_detector(self) -> None:
        types = self.data["adjacent_pair_reduction"]["cycle_types"]
        self.assertEqual(
            {
                name: value["alternating_fourth_trace"]
                for name, value in types.items()
            },
            {"6": 0, "4+2": 1, "3+3": 0, "2+2+2": 0},
        )

    def test_exterior_and_symmetric_square_traces(self) -> None:
        types = self.data["adjacent_pair_reduction"]["cycle_types"]
        self.assertEqual(
            {name: value["exterior_square_trace"] for name, value in types.items()},
            {"6": 0, "4+2": 1, "3+3": 0, "2+2+2": 0},
        )
        self.assertEqual(
            {name: value["symmetric_square_trace"] for name, value in types.items()},
            {"6": 0, "4+2": 2, "3+3": 0, "2+2+2": 0},
        )

    def test_characteristic_and_minimal_modules(self) -> None:
        types = self.data["adjacent_pair_reduction"]["cycle_types"]
        self.assertEqual(
            types["4+2"]["minimal_polynomial_low_to_high"],
            [0, 2, 0, 1],
        )
        self.assertNotEqual(
            types["6"]["minimal_polynomial_low_to_high"],
            types["2+2+2"]["minimal_polynomial_low_to_high"],
        )

    def test_local_positive_control_separates_fourth_trace(self) -> None:
        pairs = self.data["positive_controls"]["local"]["pair_data"]
        self.assertEqual(pairs["P,Q1"]["pair_trace"], pairs["P,Q2"]["pair_trace"])
        self.assertEqual(
            pairs["P,Q1"]["intersection_dimension"],
            pairs["P,Q2"]["intersection_dimension"],
        )
        self.assertNotEqual(
            pairs["P,Q1"]["alternating_fourth_trace"],
            pairs["P,Q2"]["alternating_fourth_trace"],
        )

    def test_global_controls_have_same_second_but_different_fourth_order(self) -> None:
        controls = self.data["positive_controls"][
            "global_99_projector_231_column"
        ]
        self.assertTrue(controls["same_pairwise_projector_trace_gram"])
        self.assertTrue(controls["different_fourth_trace_matrices"])
        self.assertEqual(controls["different_ordered_fourth_trace_entries"], 3888)
        for control in controls["controls"].values():
            self.assertEqual(control["projector_count"], 99)
            self.assertEqual(control["column_label_count"], 231)
            self.assertEqual(control["centered_gram_rank"], 11)
            self.assertTrue(control["centered_gram_square_zero_via_zero_frame"])

    def test_failed_graph_premises_are_explicit(self) -> None:
        failed = self.data["positive_controls"][
            "global_99_projector_231_column"
        ]["failed_target_premises"]
        self.assertGreaterEqual(len(failed), 7)
        self.assertTrue(any("not projectively distinct" in item for item in failed))
        self.assertTrue(any("BB^T" in item for item in failed))

    def test_hostile_cycle_mutations_rejected(self) -> None:
        with self.assertRaises(ValueError):
            CHECK.cycle_biadjacency((5,))
        with self.assertRaises(ValueError):
            CHECK.cycle_biadjacency((4, 1, 1))
        mutated = CHECK.cycle_biadjacency((6,))
        mutated[0][0] = 0
        self.assertNotEqual(
            [sum(row) for row in mutated],
            [2] * 6,
        )

    def test_hostile_status_mutation_rejected(self) -> None:
        mutated = json.loads(json.dumps(self.data))
        mutated["conclusions"]["endpoint_excluded"] = True
        with self.assertRaises(AssertionError):
            CHECK.verify(mutated)


if __name__ == "__main__":
    unittest.main()
