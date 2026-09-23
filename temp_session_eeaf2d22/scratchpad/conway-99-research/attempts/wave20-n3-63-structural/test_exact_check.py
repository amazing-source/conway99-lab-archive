from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("wave20_exact_check", HERE / "exact_check.py")
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class Wave20ExactCheckTests(unittest.TestCase):
    def test_frozen_inputs_authenticate(self) -> None:
        self.assertEqual(CHECK.authenticate_inputs(), CHECK.FROZEN_INPUTS)

    def test_q_profiles_are_complete_18_row_census(self) -> None:
        rows = CHECK.q_profiles()
        self.assertEqual(
            CHECK.Counter(row["r"] for row in rows),
            CHECK.Counter({14: 1, 15: 1, 16: 1, 17: 5, 18: 4, 19: 3, 20: 2, 21: 1}),
        )
        self.assertEqual(len(rows), 18)
        self.assertEqual(rows[0]["q"], (3,) * 14)
        self.assertEqual(rows[-1]["q"], (2,) * 21)

    def test_dk_four_is_substantive(self) -> None:
        strict = CHECK.q_profiles(minimum_dk=4)
        weak = CHECK.q_profiles(minimum_dk=3)
        self.assertGreater(len(weak), len(strict))

    def test_point_partition_counts(self) -> None:
        self.assertEqual(
            {
                m: len(CHECK.point_size_profiles(m, 63))
                for m in range(27, 32)
            },
            {27: 30, 28: 15, 29: 7, 30: 3, 31: 1},
        )
        self.assertEqual(
            {
                m: len(CHECK.point_size_profiles(m, 60))
                for m in range(27, 31)
            },
            {27: 11, 28: 5, 29: 2, 30: 1},
        )

    def test_crossing_weight_boundary(self) -> None:
        self.assertEqual(CHECK.crossing_weights(2, 7, False), (0, 4))
        self.assertEqual(CHECK.crossing_weights(2, 7, True), (0,))
        self.assertEqual(CHECK.crossing_weights(3, 2, False), (0, 4))
        self.assertEqual(CHECK.crossing_weights(3, 2, True), (0,))
        self.assertEqual(CHECK.crossing_weights(3, 3, False), (0, 4, 6))
        self.assertEqual(CHECK.crossing_weights(3, 3, True), (0, 4))

    def test_fixed_twelve_weight_solutions(self) -> None:
        self.assertEqual(CHECK.positive_weight_solutions(3), [(0, 2), (3, 0)])

    def test_exact_integer_square_minimum(self) -> None:
        self.assertEqual(CHECK.integer_square_minimum(72, 216), 648)
        self.assertEqual(CHECK.integer_square_minimum(71, 224), 716)
        self.assertEqual(CHECK.integer_square_minimum(69, 234), 810)

    def test_m27_through_m29_moment_boundary(self) -> None:
        survivors = {}
        for r in range(18, 22):
            incidence = 3 * r
            for m in range(27, 3 * r // 2 + 1):
                survivors[(incidence, m)] = CHECK.moment_survivors(m, incidence)
        CHECK.verify_expected_moment_boundary(survivors)

    def test_outside_moments_remove_second_m28_profile(self) -> None:
        all_profiles = CHECK.point_size_profiles(28, 63)
        upper = CHECK.spectral_degree_sum_upper(28)
        maximum_sum = upper.numerator // upper.denominator
        spectral_only = [
            sizes
            for sizes in all_profiles
            if CHECK.possible_degree_histograms(sizes, maximum_sum)
        ]
        moment_profiles = CHECK.moment_survivors(28, 63)
        self.assertEqual(len(spectral_only), 2)
        self.assertEqual(len(moment_profiles), 1)
        self.assertEqual(
            CHECK.profile_key(moment_profiles[0]["sizes"]), "2^21 3^7"
        )

    def test_m29_high_degree_cap(self) -> None:
        rows = CHECK.moment_survivors(29, 63)
        target = next(
            row for row in rows if CHECK.profile_key(row["sizes"]) == "2^24 3^5"
        )
        cap = max(
            sum(
                count
                for degree, count in (
                    (int(k), v) for k, v in state["degree_histogram"].items()
                )
                if degree >= 8
            )
            for state in target["degree_moment_states"]
        )
        self.assertEqual(cap, 1)

    def test_projector_contradiction_is_strict(self) -> None:
        row = CHECK.projector_contradiction_m30()
        self.assertEqual(row["zMz"], "4")
        self.assertEqual(row["oneMone_upper"], "4")
        self.assertEqual(row["zMone_upper"], "-5")
        self.assertEqual(row["cauchy_lhs_lower"], "25")
        self.assertEqual(row["cauchy_rhs_upper"], "16")
        self.assertTrue(row["contradiction"])

    def test_repaired_r18_through_r20_cases_are_present(self) -> None:
        payload = CHECK.build_result()
        cases = payload["finite_contradictions"]
        self.assertEqual(cases["r18"]["q_profile_count"], 4)
        self.assertEqual(cases["r19"]["q_profile_count"], 3)
        self.assertEqual(cases["r20"]["q_profiles"], ["2^19 4", "2^18 3^2"])
        self.assertEqual(
            payload["q_profile_census"]["rejected_initial_census"]["status"],
            "REJECTED",
        )

    def test_all_finite_cases_close(self) -> None:
        payload = CHECK.build_result()
        self.assertEqual(
            payload["conditional_n3_63"],
            "EXCLUDED_DERIVED_PENDING_INDEPENDENT_AUDIT",
        )
        self.assertEqual(payload["conway_99_target"], "UNKNOWN")
        self.assertEqual(payload["novelty"], "UNKNOWN")

    def test_canonical_payload_round_trip(self) -> None:
        payload = CHECK.build_result()
        encoded = CHECK.canonical_json_bytes(payload)
        self.assertEqual(CHECK.canonical_json_bytes(json.loads(encoded)), encoded)


if __name__ == "__main__":
    unittest.main()
