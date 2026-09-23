from __future__ import annotations

import importlib.util
from fractions import Fraction
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).with_name("independent_verify.py")
SPEC = importlib.util.spec_from_file_location(
    "wave100_independent_verify", MODULE_PATH
)
assert SPEC is not None and SPEC.loader is not None
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)


class Wave100IndependentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = VERIFY.independent_result()

    def test_n3_prism_and_six_root_identities(self) -> None:
        prism = self.result["prism_identity"]
        self.assertEqual(prism["n3_plus_3P"], 4158)
        self.assertEqual(prism["roots_per_prism"], 6)
        self.assertEqual(prism["rooted_identity"], "sum_o f_o=6P")

    def test_general_local_scaffold_and_mate_multiplicities(self) -> None:
        local = self.result["local_applicability"]
        self.assertEqual(local["seed_count"], 560)
        self.assertEqual(local["transition_candidate_count"], 924)
        self.assertEqual(local["mate_forbidden_candidate_count"], 84)
        self.assertEqual(local["seed_eligible_candidate_count"], 840)
        self.assertEqual(local["mate_transition_seed_multiplicities"], [0])
        self.assertEqual(
            local["eligible_transition_seed_multiplicities"], [8]
        )
        self.assertEqual(local["local_perfect_matching_count"], 10395)

    def test_cap_18_survives_mate_transitions(self) -> None:
        local = self.result["local_applicability"]
        self.assertEqual(
            local["original_center_max_without_lambda_guard"], 16
        )
        self.assertEqual(
            local["original_center_max_with_lambda_guard"], 10
        )
        self.assertEqual(local["fourth_center_sum_of_maxima"], 8)
        self.assertEqual(local["per_transition_coincidence_cap"], 18)

    def test_rootwise_ceiling_floor_for_every_f(self) -> None:
        for forbidden in range(85):
            row = VERIFY.rooted_row(forbidden)
            expected_bad = VERIFY.ceil_fraction(
                Fraction(5 * (84 - forbidden), 2)
            )
            self.assertEqual(row["bad_seed_integer_lower"], expected_bad)
            self.assertEqual(
                row["transition_free_seed_upper"],
                (700 + 5 * forbidden) // 2,
            )

    def test_odd_root_row_rounds_in_correct_direction(self) -> None:
        row = VERIFY.rooted_row(1)
        self.assertEqual(row["bad_seed_rational_lower"], "415/2")
        self.assertEqual(row["bad_seed_integer_lower"], 208)
        self.assertEqual(row["transition_free_seed_upper"], 352)

    def test_pair_moment_uses_unordered_multiplicity(self) -> None:
        row = VERIFY.rooted_row(0)
        self.assertEqual(row["first_moment"], 672)
        self.assertEqual(row["unordered_pair_moment_upper"], 756)

    def test_floor_sum_direction(self) -> None:
        result = self.result["floor_sum"]
        self.assertEqual(result["direction"], "UPPER")
        for prisms in range(1387):
            row = VERIFY.floor_sum_certificate(prisms)
            self.assertEqual(
                row["global_rooted_incidence_upper"],
                34650 + 15 * prisms,
            )

    def test_floor_sum_parity_defect(self) -> None:
        values = [1, 1] + [0] * 97
        actual = sum((700 + 5 * value) // 2 for value in values)
        scalar_upper = 99 * 350 + 5
        self.assertEqual(actual, scalar_upper - 1)

    def test_substitution_has_coefficient_minus_five(self) -> None:
        bound = self.result["global_bound"]
        self.assertEqual(bound["coefficient_of_n3"], -5)
        for row in VERIFY.compatible_rows():
            self.assertEqual(
                row["rooted_numerator"], 55440 - 5 * row["n3"]
            )

    def test_all_compatible_rows_get_strongest_even_bound(self) -> None:
        rows = VERIFY.compatible_rows()
        self.assertEqual(len(rows), 1387)
        for row in rows:
            bound = row["even_N14_upper"]
            rational = Fraction(row["rooted_numerator"], 7)
            self.assertEqual(bound % 2, 0)
            self.assertLessEqual(bound, rational)
            self.assertGreater(bound + 2, rational)

    def test_even_rounding_is_sometimes_strict(self) -> None:
        bound = self.result["global_bound"]
        self.assertGreater(
            bound["rows_tightened_by_antipodal_even_rounding"], 0
        )
        self.assertLess(
            bound["rows_tightened_by_antipodal_even_rounding"], 1387
        )

    def test_endpoint_rows(self) -> None:
        endpoints = self.result["global_bound"]["endpoint_rows"]
        self.assertEqual(endpoints["4158"]["even_N14_upper"], 4950)
        self.assertEqual(endpoints["4155"]["even_N14_upper"], 4952)
        self.assertEqual(endpoints["708"]["even_N14_upper"], 7414)
        self.assertEqual(endpoints["0"]["even_N14_upper"], 7920)

    def test_scope_and_status_fail_closed(self) -> None:
        scope = self.result["scope"]
        self.assertFalse(scope["requires_P0"])
        self.assertFalse(scope["requires_rank_28"])
        status = self.result["status"]
        self.assertEqual(status["strict_n3_upper_bound"], "NOT_PROVED")
        self.assertEqual(status["graph_nonexistence"], "NOT_PROVED")
        self.assertEqual(status["Conway_99"], "UNKNOWN")

    def test_precomparison_status_is_not_promoted(self) -> None:
        self.assertEqual(
            self.result["claim_label"], "PENDING_DISCOVERY_COMPARISON"
        )


if __name__ == "__main__":
    unittest.main()
