from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("exact_check.py")
SPEC = importlib.util.spec_from_file_location("wave180_exact_check", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Wave180ExactCheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = MODULE.analyze()
        MODULE.verify(cls.data)

    def test_projector_residue(self) -> None:
        self.assertEqual(self.data["projector_admissible_t"], [0, 3])

    def test_t0_duplicate_direction(self) -> None:
        profile = self.data["local_profiles"][0]
        self.assertEqual(profile["projective_weights"], [2, 7, 7, 8])

    def test_t3_companion_pair(self) -> None:
        profile = self.data["local_profiles"][3]
        self.assertEqual(profile["projective_weights"], [4, 5, 7, 8])
        self.assertEqual(self.data["t3_circuit_pair"]["weights"], [4, 5])

    def test_minimal_cover_amplification(self) -> None:
        cover = self.data["minimal_cover"]
        self.assertEqual(
            cover["nonedge_projective_circuit_lower_bound"],
            2079,
        )
        self.assertEqual(self.data["projective_circuit_lower_bound"], 2772)

    def test_scalar_factor(self) -> None:
        self.assertEqual(
            self.data["dual_word_lower_bound"],
            self.data["ternary_nonzero_scalars_per_projective_class"]
            * self.data["projective_circuit_lower_bound"],
        )

    def test_hostile_control(self) -> None:
        control = self.data["hostile_control_k6_6"]
        self.assertEqual(control["rank"], 11)
        self.assertEqual(control["projective_cycles_weight_4_6_8"], 18825)


if __name__ == "__main__":
    unittest.main()
