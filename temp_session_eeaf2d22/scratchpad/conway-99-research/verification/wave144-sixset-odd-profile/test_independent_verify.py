"""Hostile tests for the clean-room Wave144 verifier."""

from __future__ import annotations

import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave144_independent_verify_tested",
    HERE / "independent_verify.py",
)
assert SPEC is not None and SPEC.loader is not None
VERIFY = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = VERIFY
SPEC.loader.exec_module(VERIFY)


class Wave144IndependentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(VERIFY.RESULT_PATH.read_text(encoding="utf-8"))
        cls.report = VERIFY.verify_payload(cls.payload)

    def test_clean_room_verdict(self) -> None:
        self.assertEqual(self.report["verdict"], "PASS_NULL_BOUNDARY")
        self.assertEqual(self.report["independent_exact_supports_recomputed"], 62)
        self.assertEqual(self.report["selected_local_z_witnesses_checked"], 66)

    def test_forced_cells(self) -> None:
        self.assertEqual(
            self.report["forced_singleton_cells"],
            {"1": 66, "3": 56, "5": 46, "14": 36},
        )

    def test_gapped_support_is_preserved(self) -> None:
        class36 = self.payload["class_profiles"][35]["attainable_weights"]
        self.assertIn(64, class36)
        self.assertIn(72, class36)
        self.assertNotIn(68, class36)

    def test_bad_local_witness_is_rejected(self) -> None:
        witness = self.payload["selected_local_integer_witnesses"][0]
        sparse = copy.deepcopy(witness["z_by_subset_mask_sparse"])
        first = next(iter(sparse))
        sparse[first] += 1
        source = witness["source_class"]
        with self.assertRaises(AssertionError):
            VERIFY.check_z(
                self._mask(source),
                sparse,
                witness["output_weight"],
            )

    def test_bad_aggregate_moment_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.payload)
        mutated["aggregate_endpoint_certificate"]["nonzero_cells"][0]["count"] += 1
        with self.assertRaises(AssertionError):
            VERIFY.verify_payload(mutated)

    def test_false_support_value_is_rejected(self) -> None:
        actual = VERIFY.independently_enumerate_weights(self._mask(36))
        self.assertNotIn(68, actual)

    @staticmethod
    def _mask(source: int) -> int:
        wave21 = VERIFY.load_wave21()
        _, five = wave21.align_four_five()
        six = wave21.align_five_six(five, wave21.corrected_five_to_six())
        return wave21.locally_admissible_classes(6)[six[source - 1]]


if __name__ == "__main__":
    unittest.main()
