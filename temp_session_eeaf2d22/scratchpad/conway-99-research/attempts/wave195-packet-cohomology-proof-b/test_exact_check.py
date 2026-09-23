from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("wave195_exact_check", HERE / "exact_check.py")
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Wave195ExactCheckTests(unittest.TestCase):
    def test_frozen_result(self) -> None:
        expected = json.loads((HERE / "exact-results.json").read_text(encoding="utf-8"))
        self.assertEqual(MODULE.derive(), expected)

    def test_local_coefficient_obstructions(self) -> None:
        local = MODULE.derive()["local_coefficients"]
        self.assertEqual(local["equal_A_difference_weight"], 2)
        self.assertEqual(local["disjoint_A_plus_star_weight"], 3)

    def test_fixed_center_cap(self) -> None:
        theorem = MODULE.derive()["fixed_center_theorem"]
        self.assertEqual(theorem["hilton_milner_nontrivial_cap"], 13)
        self.assertEqual(theorem["erdos_ko_rado_trivial_cap"], 15)
        self.assertEqual(theorem["trivial_common_block_neighbor_base"], 12)
        self.assertEqual(
            theorem["universal_oriented_label_cap"],
            "j_x<=39",
        )

    def test_global_row(self) -> None:
        row = MODULE.derive()["global_row"]
        self.assertEqual(row["K"], 3861)
        self.assertIn("a3+b3", row["lower"])
        self.assertEqual(row["upper"], "J<=K")

    def test_exact_certificate(self) -> None:
        certificate = MODULE.derive()["certificate"]
        self.assertEqual(certificate["reduced_difference"], {})
        self.assertEqual(certificate["rational_Q_target"], "13959/2")
        self.assertEqual(certificate["integer_Q_lower_bound"], 6980)
        self.assertEqual(certificate["edge_added_projective"], 7673)
        self.assertEqual(certificate["circuit_scalar_words"], 15346)

    def test_rational_null(self) -> None:
        null = MODULE.derive()["certificate"]["rational_null"]
        self.assertTrue(null["all_six_slacks_zero"])
        self.assertFalse(null["asserted_object"])


if __name__ == "__main__":
    unittest.main()
