"""Hostile tests for the independent Wave 28 glue/discriminant checker."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

import independent_check as check


class IndependentGlueDiscriminantTests(unittest.TestCase):
    def test_all_eight_groups_and_exact_levels_are_hard_matched(self) -> None:
        expected = {
            9: (2, 0, 3),
            21: (1, 1, 21),
            49: (0, 2, 7),
            81: (4, 0, 3),
            189: (3, 1, 21),
            441: (2, 2, 21),
            729: (6, 0, 3),
            1029: (1, 3, 21),
        }
        observed = {}
        for h in check.H_VALUES:
            row = check.discriminant_candidates_for_h(h)
            observed[h] = (row["u"], row["v"], row["exact_level"])
            self.assertEqual(row["group_exponent"], row["exact_level"])
        self.assertEqual(observed, expected)

    def test_mixed_primary_groups_allow_cyclic_order_twenty_one(self) -> None:
        expected = {
            21: [21],
            189: [3, 3, 21],
            441: [21, 21],
            1029: [7, 7, 21],
        }
        for h, factors in expected.items():
            row = check.discriminant_candidates_for_h(h)
            self.assertEqual(row["invariant_factors"], factors)
            self.assertIn(21, row["invariant_factors"])
            product = 1
            for factor in row["invariant_factors"]:
                product *= factor
            self.assertEqual(product, h)

    def test_signature_phase_candidates_are_hard_matched(self) -> None:
        expected = {
            9: [(1, 1)],
            21: [(1, 1), (-1, -1)],
            49: [(1, 1)],
            81: [(-1, 1)],
            189: [(1, -1), (-1, 1)],
            441: [(1, -1), (-1, 1)],
            729: [(1, 1)],
            1029: [(1, -1), (-1, 1)],
        }
        observed = {}
        for h in check.H_VALUES:
            row = check.discriminant_candidates_for_h(h)
            observed[h] = [
                (candidate["delta_3"], candidate["delta_7"])
                for candidate in row["candidates"]
            ]
        self.assertEqual(observed, expected)

    def test_corrected_total_is_twelve_and_hostile_eleven_is_rejected(self) -> None:
        total = sum(
            len(check.discriminant_candidates_for_h(h)["candidates"])
            for h in check.H_VALUES
        )
        self.assertEqual(total, 12)
        self.assertNotEqual(total, 11)

    def test_local_gauss_residue_polynomials_have_opposite_signs(self) -> None:
        controls = check.local_gauss_controls()
        self.assertEqual(controls["3"]["square_counts"], [1, 2, 0])
        self.assertEqual(controls["3"]["nonsquare_counts"], [1, 0, 2])
        self.assertEqual(controls["7"]["square_counts"], [1, 2, 2, 0, 2, 0, 0])
        self.assertEqual(controls["7"]["nonsquare_counts"], [1, 0, 0, 2, 0, 2, 2])
        for prime in ("3", "7"):
            self.assertTrue(controls[prime]["nonsquare_is_negative_square_at_zeta"])
            self.assertTrue(controls[prime]["square_gauss_sum_is_pure_imaginary"])
            self.assertEqual(controls[prime]["legendre_nonsquare"], -1)

    def test_canonical_coefficients_reproduce_every_local_sign(self) -> None:
        for h in check.H_VALUES:
            row = check.discriminant_candidates_for_h(h)
            for candidate in row["candidates"]:
                for prime, dimension, key, delta_key in (
                    (3, row["u"], "coefficients_3", "delta_3"),
                    (7, row["v"], "coefficients_7", "delta_7"),
                ):
                    coefficients = candidate[key]
                    self.assertEqual(len(coefficients), dimension)
                    product = 1
                    for coefficient in coefficients:
                        product *= coefficient
                    self.assertEqual(check.legendre(product, prime), candidate[delta_key])

    def test_scaled_dual_dimensions_are_complementary(self) -> None:
        for h in check.H_VALUES:
            row = check.discriminant_candidates_for_h(h)
            self.assertEqual(row["u"] + row["g_primary_dimensions"]["3"], 44)
            self.assertEqual(row["v"] + row["g_primary_dimensions"]["7"], 44)

    def test_scaled_dual_preserves_both_signs_on_every_row(self) -> None:
        observed = {
            (h, prime): check.scaled_dual_sign_ratio(h, prime)
            for h in check.H_VALUES
            for prime in (3, 7)
        }
        self.assertEqual(set(observed.values()), {1})

    def test_single_root_complement_arithmetic_all_rows(self) -> None:
        rows = check.complement_rows()
        self.assertEqual(len(rows), 8)
        for row in rows:
            self.assertEqual(row["index"], 2)
            self.assertEqual(row["determinant_complement"], 2 * row["h"])
            self.assertEqual(row["two_primary_order"], 2)

    def test_a2_hostile_control_refutes_primitive_implies_split(self) -> None:
        control = check.a2_root_control()
        self.assertEqual(control["determinant_l"], 3)
        self.assertEqual(control["root_norm"], 2)
        self.assertEqual(control["root_divisibility"], 1)
        self.assertEqual(control["orthogonality"], 0)
        self.assertEqual(control["complement_norm_and_determinant"], 6)
        self.assertEqual(control["index"], 2)
        self.assertEqual(control["two_primary_complement_value"]["q"], "3/2")
        self.assertEqual(control["two_primary_complement_value"]["mod_2"], "-1/2")

    @staticmethod
    def brute_force_patterns() -> list[tuple[int, int, int, int, int]]:
        """A test-side enumeration not using the solved b,d,z formulas."""
        found = []
        for a in range(11):
            for e in range(11):
                for b in range(43):
                    for d in range(43):
                        z = 231 - a - b - d - e
                        if z < 0:
                            continue
                        if 2 * a + b - d - 2 * e != 0:
                            continue
                        if 4 * a + b + d + 4 * e != 42:
                            continue
                        found.append((a, b, z, d, e))
        return found

    def test_complete_second_moment_census_is_46_by_separate_enumeration(self) -> None:
        production, _ = check.pattern_census()
        production_tuples = {
            (
                row["a_plus_2"],
                row["b_plus_1"],
                row["z_zero"],
                row["d_minus_1"],
                row["e_minus_2"],
            )
            for row in production
        }
        brute = set(self.brute_force_patterns())
        self.assertEqual(production_tuples, brute)
        self.assertEqual(len(brute), 46)

    def test_complete_cubic_census_is_32_by_separate_enumeration(self) -> None:
        _, production = check.pattern_census()
        production_tuples = {
            (
                row["a_plus_2"],
                row["b_plus_1"],
                row["z_zero"],
                row["d_minus_1"],
                row["e_minus_2"],
            )
            for row in production
        }
        brute = set()
        for pattern in self.brute_force_patterns():
            a, b, z, d, e = pattern
            cubic = 8 * a + b - d - 8 * e
            if Fraction(cubic * cubic, 8) <= 60:
                brute.add(pattern)
        self.assertEqual(production_tuples, brute)
        self.assertEqual(len(brute), 32)

    def test_hostile_survivor_and_active_mutation(self) -> None:
        hostile = check.pattern_from_counts(0, 21, 189, 21, 0)
        mutation = check.pattern_from_counts(4, 9, 201, 17, 0)
        for record in (hostile, mutation):
            self.assertEqual(record["coordinate_count"], 231)
            self.assertEqual(record["sum"], 0)
            self.assertEqual(record["squared_norm"], 42)
        self.assertEqual(hostile["cubic_energy"], {"numerator": 0, "denominator": 1})
        self.assertTrue(hostile["passes_energy_at_most_60"])
        self.assertEqual(mutation["cubic_energy"], {"numerator": 72, "denominator": 1})
        self.assertFalse(mutation["passes_energy_at_most_60"])

    def test_full_cancellation_order_argument_needs_both_injections(self) -> None:
        for a_order in range(1, 65):
            for b_order in range(1, 65):
                for h_order in range(1, 65):
                    self.assertTrue(
                        check.cancellation_order_implication(a_order, b_order, h_order)
                    )
        # Self-duality alone does not force equal factors: 4^2=2*8.
        self.assertEqual(4 * 4, 2 * 8)
        self.assertGreater(4, 2)  # violates injection into the order-two factor

    def test_root_closure_hypothesis_controls_are_active(self) -> None:
        controls = check.root_closure_hypothesis_controls()
        self.assertEqual(controls["all_roots_required"]["complement_minimum"], 2)
        self.assertEqual(
            controls["primitivity_required_for_projection_injectivity"][
                "overlattice_quotient_order"
            ],
            2,
        )
        self.assertEqual(
            controls["primitivity_required_for_projection_injectivity"][
                "projection_to_complement_order"
            ],
            1,
        )
        order_control = controls["both_injections_required_for_full_cancellation"][
            "self_dual_order_example"
        ]
        self.assertEqual(
            order_control["H_order"] ** 2,
            order_control["A_order"] * order_control["B_order"],
        )
        self.assertGreater(order_control["H_order"], order_control["A_order"])

    def test_cli_output_is_deterministic_lf_json(self) -> None:
        script = Path(__file__).with_name("independent_check.py")
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first.json"
            second = Path(directory) / "second.json"
            command = [sys.executable, "-B", str(script), "--output"]
            subprocess.run(command + [str(first)], check=True)
            subprocess.run(command + [str(second)], check=True)
            first_bytes = first.read_bytes()
            self.assertEqual(first_bytes, second.read_bytes())
            self.assertNotIn(b"\r\n", first_bytes)
            payload = json.loads(first_bytes)
            self.assertEqual(payload["formal_candidate_count"], 12)
            self.assertEqual(payload["projector_patterns"]["second_moment_count"], 46)
            self.assertEqual(payload["projector_patterns"]["cubic_filtered_count"], 32)
            self.assertEqual(payload["verdict"]["scoped_claims"], "PASS_WITH_CORRECTION")
            self.assertEqual(
                payload["frozen_discovery_defects"][0]["verdict"],
                "FALSE for order 21",
            )


if __name__ == "__main__":
    unittest.main()
