import json
import unittest
from pathlib import Path

import independent_check as check
import comparison_check as comparison


class IndependentCheckTests(unittest.TestCase):
    def test_seidel_square_is_rederived(self) -> None:
        self.assertEqual(
            check.seidel_square_coefficients(),
            {"I": 49, "A": 0, "J": 49},
        )

    def test_correct_rational_spectrum(self) -> None:
        result = check.rational_spectra()
        self.assertEqual(result["adjacency"], {"14": 1, "3": 54, "-4": 44})
        self.assertEqual(result["seidel"], {"-70": 1, "7": 54, "-7": 44})
        self.assertEqual(result["seidel_trace"], 0)
        self.assertEqual(int(result["absolute_determinant"]), 10 * 7**99)

    def test_discovery_spectrum_is_hostilely_rejected(self) -> None:
        claimed_trace = -70 + 44 * 7 - 54 * 7
        self.assertEqual(claimed_trace, -140)
        self.assertNotEqual(claimed_trace, 0)

    def test_I_plus_J_is_a_7_adic_unit_only_where_used(self) -> None:
        self.assertEqual(100 % 7, 2)
        self.assertNotEqual(100 % 7, 0)
        self.assertEqual(100 % 2, 0)
        self.assertEqual(100 % 5, 0)

    def test_reciprocal_pairing_uniquely_forces_each_7_profile(self) -> None:
        for rank in range(1, 50):
            with self.subTest(rank=rank):
                candidates = check.seven_exponent_candidates(rank)
                self.assertEqual(len(candidates), 1)
                self.assertEqual(
                    {exponent: candidates[0].count(exponent) for exponent in range(3)},
                    {0: rank, 1: 99 - 2 * rank, 2: rank},
                )

    def test_modular_rank_and_determinant_are_not_enough(self) -> None:
        witness = check.rank_and_determinant_only_counterexample()
        self.assertTrue(witness["same_factor_count"])
        self.assertTrue(witness["same_rank_mod_7"])
        self.assertTrue(witness["same_determinant_valuation"])
        self.assertTrue(witness["alternative_violates_reciprocal_pairing"])
        self.assertNotEqual(
            witness["canonical_counts"], witness["alternative_counts"]
        )

    def test_global_primary_alignment_forces_the_closed_form(self) -> None:
        for rank in range(1, 50):
            with self.subTest(rank=rank):
                result = check.profile(rank)
                self.assertTrue(result["matches_closed_form"])
                self.assertTrue(result["divisibility_chain"])
                self.assertEqual(int(result["absolute_product"]), 10 * 7**99)
                self.assertEqual(result["rank_mod_2"], 98)
                self.assertEqual(result["rank_mod_5"], 98)
                self.assertEqual(result["rank_mod_7"], rank)

    def test_modular_ranks_do_not_place_2_or_5_without_determinant(self) -> None:
        # Rank 98 says exactly one invariant factor is divisible by the prime,
        # but its exponent is supplied by v_p(det)=1, not by rank alone.
        factors_v1 = [1] * 98 + [2]
        factors_v3 = [1] * 98 + [8]
        self.assertEqual(check.modular_rank(factors_v1, 2), 98)
        self.assertEqual(check.modular_rank(factors_v3, 2), 98)
        self.assertNotEqual(factors_v1[-1], factors_v3[-1])

    def test_square_zero_jordan_type(self) -> None:
        for rank in range(50):
            profile = check.jordan_profile(rank)
            self.assertEqual(profile["J2_zero"], rank)
            self.assertEqual(
                2 * profile["J2_zero"] + profile["J1_zero"],
                99,
            )

    def test_symmetric_square_bound(self) -> None:
        gram_rank = check.rank_mod(check.j_minus_identity(99), 7)
        self.assertEqual(gram_rank, 98)
        self.assertEqual(check.symmetric_square_floor(gram_rank), 14)
        self.assertLess(13 * 14 // 2, gram_rank)
        self.assertGreaterEqual(14 * 15 // 2, gram_rank)

    def test_all_endpoint_ranks_survive(self) -> None:
        endpoint = check.build_result()["endpoint"]
        self.assertEqual(endpoint["surviving_ranks"], list(range(28, 45)))
        self.assertEqual(endpoint["survivor_count"], 17)
        self.assertFalse(endpoint["contradiction_found"])
        self.assertEqual(endpoint["claim_label"], "UNKNOWN")

    def test_committed_artifact_is_canonical(self) -> None:
        path = Path(__file__).with_name("independent-result.json")
        result = check.build_result()
        self.assertEqual(path.read_bytes(), check.canonical_bytes(result))
        self.assertEqual(json.loads(path.read_text(encoding="utf-8")), result)

    def test_frozen_artifact_comparison_records_the_correction(self) -> None:
        result = comparison.build_comparison()
        self.assertTrue(result["all_corrected_structural_claims_agree"])
        self.assertTrue(result["checks"]["discovery_spectrum_is_incorrect"])
        self.assertEqual(result["correction"]["claim_label"], "REFUTED")
        self.assertEqual(result["endpoint"]["claim_label"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
