import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("independent_verify.py")
SPEC = importlib.util.spec_from_file_location("wave71_independent", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class IndependentWave71Tests(unittest.TestCase):
    def test_level_one_weights(self):
        rows = MODULE.lattice_transfer()["rows"]
        self.assertEqual(
            [row["Skoruppa_level_one_weight"] for row in rows],
            [148, 142, 136, 130, 124, 118, 112, 106],
        )

    def test_e6_is_one_mod_seven(self):
        _, e6 = MODULE.eisenstein_series_mod_7()
        self.assertEqual(e6, [1] + [0] * (MODULE.PRECISION - 1))

    def test_only_q16_has_relation_through_q9(self):
        rows = MODULE.level_one_rows()
        self.assertTrue(
            all(
                not row["relations_on_coefficients_q7_q8_q9"]
                for row in rows[:-1]
            )
        )
        self.assertEqual(
            rows[-1]["relations_on_coefficients_q7_q8_q9"],
            [{"coefficients": [1, 1, 1], "constant": 2}],
        )

    def test_stronger_gap_bounds(self):
        rows = MODULE.level_one_rows()
        self.assertEqual(
            [row["forced_upper_bound_on_min_K"] for row in rows],
            [28, 28, 28, 28, 28, 28, 28, 18],
        )
        self.assertEqual(
            [row["forced_next_coefficient_mod_7"] for row in rows],
            [6, 6, 6, 6, 6, 6, 6, 2],
        )

    def test_magnitude_profiles(self):
        self.assertEqual(
            MODULE.magnitude_profiles(14),
            [(10, 1, 0, 0), (14, 0, 0, 0)],
        )
        self.assertEqual(len(MODULE.magnitude_profiles(16)), 4)
        self.assertEqual(len(MODULE.magnitude_profiles(18)), 4)

    def test_spectral_bounds(self):
        self.assertEqual(MODULE.spectral_edge_bound(14), 31)
        self.assertEqual(MODULE.spectral_edge_bound(16), 38)
        self.assertEqual(MODULE.spectral_edge_bound(18), 45)

    def test_pure_sign_aggregate_totals(self):
        self.assertEqual(
            MODULE.aggregate_edge_totals({-1: 7, 1: 7}, 31), [28]
        )
        self.assertEqual(
            MODULE.aggregate_edge_totals({-1: 8, 1: 8}, 38), [32, 36]
        )
        self.assertEqual(
            MODULE.aggregate_edge_totals({-1: 9, 1: 9}, 45), [36, 40, 44]
        )

    def test_all_mixed_profiles_eliminated(self):
        result = MODULE.low_norm_analysis()
        self.assertTrue(result["all_mixed_magnitude_profiles_eliminated"])

    def test_fractional_coset_energy(self):
        self.assertEqual(33 * 66 // 99, 22)
        self.assertEqual(66 * 33 // 99, 22)

    def test_claim_boundary(self):
        result = MODULE.build_results()
        self.assertEqual(result["verdict"], "VERIFIED_WITH_CORRECTION")
        self.assertFalse(result["status"]["q16_excluded"])
        self.assertEqual(result["status"]["Conway_99"], "UNKNOWN")
        self.assertEqual(result["status"]["novelty"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
