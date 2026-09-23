from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("wave192_exact_check", HERE / "exact_check.py")
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Wave192ExactCheckTests(unittest.TestCase):
    def test_frozen_result(self) -> None:
        expected = json.loads((HERE / "exact-results.json").read_text(encoding="utf-8"))
        self.assertEqual(MODULE.derive(), expected)

    def test_axis_coset(self) -> None:
        result = MODULE.derive()["axis_coset"]
        self.assertEqual(result["plus_profile"], [6, 2])
        self.assertEqual(result["minus_profile"], [6, 2])
        self.assertNotEqual(result["plus_support"], result["minus_support"])

    def test_all_type_three_face(self) -> None:
        face = MODULE.derive()["all_type3_face"]
        self.assertEqual(face["n3"], 2079)
        self.assertEqual(face["private_labels"], 2079)
        self.assertEqual(face["shared_labels"], 2079)
        self.assertEqual(face["shared_label_multiplicity"], 2)

    def test_strict_integral_consequence(self) -> None:
        constants = MODULE.derive()["constants"]
        self.assertEqual(constants["strict_Q"], constants["wave191_Q"] + 1)
        self.assertEqual(constants["all_projective_short_circuits"], 6931)
        self.assertEqual(constants["scalar_short_circuit_words"], 13862)


if __name__ == "__main__":
    unittest.main()

