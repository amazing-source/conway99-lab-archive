from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave131_independent", HERE / "independent_verify.py"
)
assert SPEC and SPEC.loader
VERIFY = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = VERIFY
SPEC.loader.exec_module(VERIFY)


class IndependentWave131Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = VERIFY.build_results()

    def test_manifest_preinspection(self) -> None:
        self.assertEqual(self.data["preinspection"]["entries_checked"], 13)

    def test_lcd_and_injectivity(self) -> None:
        lcd = self.data["binary_lcd"]
        self.assertTrue(lcd["both_LCD"])
        self.assertEqual(lcd["image_symplectic_dimension"], 54)
        self.assertTrue(lcd["subset_map_injectivity"]["both_injective"])

    def test_forced_distributions(self) -> None:
        forced = self.data["forced_distributions"]
        self.assertEqual(
            forced["image_forced_lower"],
            {
                "14": 99,
                "24": 4158,
                "26": 693,
                "30": 70686,
                "32": 41580,
                "34": 36036,
                "36": 8547,
            },
        )
        self.assertEqual(
            forced["dual_forced_lower"],
            {
                "15": 99,
                "24": 693,
                "26": 4158,
                "31": 41580,
                "33": 79002,
                "35": 8316,
                "37": 27720,
                "39": 231,
            },
        )
        self.assertEqual(len(forced["rows_for_all_subset_types_size_at_most_3"]), 10)

    def test_rational_witness_all_rows(self) -> None:
        witness = self.data["rational_witness"]
        self.assertEqual(witness["coefficients_checked"], 200)
        self.assertEqual(witness["forward_MacWilliams_rows_checked"], 100)
        self.assertEqual(witness["inverse_MacWilliams_rows_checked"], 100)
        self.assertEqual(witness["forward_failures"], [])
        self.assertEqual(witness["inverse_failures"], [])
        self.assertEqual(witness["image_minimum_nonzero_weight"], 14)
        self.assertEqual(witness["dual_minimum_nonzero_weight"], 15)
        self.assertEqual(witness["image_fractional_coefficient_count"], 34)
        self.assertEqual(witness["dual_fractional_coefficient_count"], 32)
        self.assertFalse(witness["formal_integral_enumerator"])
        self.assertFalse(witness["realized_binary_code"])

    def test_integral_scout_unknown(self) -> None:
        scout = self.data["integral_scout"]
        self.assertEqual(scout["classification"], "UNKNOWN")
        self.assertFalse(scout["integral_solution_certificate_present"])
        self.assertFalse(scout["infeasibility_certificate_present"])
        self.assertFalse(scout["negative_inference_allowed"])

    def test_status_wall(self) -> None:
        status = self.data["status_wall"]
        self.assertEqual(status["integral_formal_enumerator"], "UNKNOWN")
        self.assertFalse(status["binary_code_constructed"])
        self.assertFalse(status["graph_constructed"])
        self.assertFalse(status["rank_excluded"])
        self.assertEqual(status["Conway_99"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
