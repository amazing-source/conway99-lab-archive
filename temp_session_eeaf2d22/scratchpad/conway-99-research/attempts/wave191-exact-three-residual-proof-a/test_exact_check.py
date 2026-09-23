from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("wave191_proof_a", HERE / "exact_check.py")
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Wave191ProofATest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = MODULE.derive()

    def test_owner_center_excluded_profile(self) -> None:
        self.assertEqual(
            self.result["local"]["owner_center_difference_profile"], [0, 6]
        )

    def test_target_center_forces_impossible_canonical_word(self) -> None:
        self.assertEqual(
            self.result["local"]["target_c5_difference_profile"], [2, 2]
        )
        self.assertNotEqual(
            self.result["local"]["all_equal_gram_product"], [0, 0, 0, 0]
        )
        self.assertEqual(
            self.result["local"]["checkerboard_gram_product"], [0, 0, 0, 0]
        )

    def test_exact_two_control(self) -> None:
        self.assertEqual(
            self.result["local"]["checkerboard_difference_profiles"],
            [[2, 5], [2, 5]],
        )

    def test_coefficient_identity(self) -> None:
        certificate = self.result["coefficient_certificate"]
        self.assertEqual(certificate["coefficient_row"], certificate["identity_row"])
        self.assertEqual(certificate["three_C_over_two"], 6237)

    def test_global_counts(self) -> None:
        certificate = self.result["coefficient_certificate"]
        self.assertEqual(certificate["edge_added_projective"], 6930)
        self.assertEqual(certificate["circuit_scalar_words"], 13860)

    def test_null_control(self) -> None:
        control = self.result["null_control"]
        row = control["row"]
        self.assertEqual(control["I"], 8316)
        self.assertEqual(control["delta_definition"], row["delta"])
        self.assertEqual(control["raw_capacity"], control["A"])
        self.assertEqual(
            control["residual_capacity"], row["p3"] - row["r1"]
        )
        self.assertEqual(control["counted_Q"], row["Q"])


if __name__ == "__main__":
    unittest.main()
