from __future__ import annotations

import importlib.util
import json
import math
import sys
import unittest
from pathlib import Path

from flint import fmpq


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class ExactRankOneWitnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.model = load_module("wave150_test_model", HERE / "endpoint_sdp.py")
        cls.exact = load_module(
            "wave150_test_exact", HERE / "exact_rank1_witness.py"
        )
        cls.inputs = cls.model.load_inputs(True)
        cls.witness = json.loads(
            (HERE / "exact-rank1-witness.json").read_text(encoding="utf-8")
        )
        cls.classes7 = tuple(int(mask) for mask in cls.inputs["classes"][7])
        cls.classes8 = tuple(int(mask) for mask in cls.inputs["classes8"])
        index7 = {mask: index for index, mask in enumerate(cls.classes7)}
        index8 = {mask: index for index, mask in enumerate(cls.classes8)}
        cls.x7 = [0] * len(cls.classes7)
        cls.x8 = [fmpq(0)] * len(cls.classes8)
        for record in cls.witness["x7_support"]:
            cls.x7[index7[int(record["canonical_mask"])]] = int(record["count"])
        for record in cls.witness["x8_support"]:
            cls.x8[index8[int(record["canonical_mask"])]] = fmpq(record["count"])
        cls.rows, cls.row_record = cls.exact.build_rows(cls.inputs, cls.x7)

    def test_exact_totals_support_and_denominators(self) -> None:
        self.assertEqual(sum(self.x7), math.comb(99, 7))
        self.assertEqual(sum(self.x8, fmpq(0)), math.comb(99, 8))
        self.assertEqual(sum(value > 0 for value in self.x7), 204)
        self.assertEqual(sum(value > 0 for value in self.x8), 874)
        self.assertTrue(all(value >= 0 for value in self.x8))
        self.assertEqual(max(int(value.q) for value in self.x8), 4)

    def test_all_exact_rows_replay(self) -> None:
        self.assertEqual(len(self.rows), 10_310)
        for row in self.rows:
            value = sum(
                (
                    fmpq(coefficient) * self.x8[column]
                    for column, coefficient in row.coefficients.items()
                ),
                fmpq(0),
            )
            self.assertEqual(value, row.rhs, row.label)

    def test_rounded_order7_replays_wave44(self) -> None:
        candidate = json.loads(
            (HERE / "marked-rank1-both-highs-explicit.json").read_text(
                encoding="utf-8"
            )
        )
        row_system = json.loads(
            (ROOT / "attempts/wave44-rooted-flags/row-system.json").read_text(
                encoding="utf-8"
            )
        )
        rounded, record = self.exact.rounded_order7(candidate, row_system)
        self.assertEqual(rounded, self.x7)
        self.assertEqual(record["wave44_rows_passed"], 170)
        self.assertEqual(record["y"], 2079)

    def test_hostile_x8_mutation_is_detected(self) -> None:
        hostile = list(self.x8)
        first = next(index for index, value in enumerate(hostile) if value > 0)
        hostile[first] += 1
        failures = 0
        for row in self.rows:
            value = sum(
                (
                    fmpq(coefficient) * hostile[column]
                    for column, coefficient in row.coefficients.items()
                ),
                fmpq(0),
            )
            failures += value != row.rhs
        self.assertGreater(failures, 0)


if __name__ == "__main__":
    unittest.main()
