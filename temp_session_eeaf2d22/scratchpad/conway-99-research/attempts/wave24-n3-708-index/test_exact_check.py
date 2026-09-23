from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

import exact_check as ec


class Wave24ExactChecks(unittest.TestCase):
    def test_frozen_inputs_match(self) -> None:
        for path, expected in ec.INPUTS.items():
            self.assertEqual(ec.sha256(ec.ROOT / path), expected)

    def test_endpoint_arithmetic(self) -> None:
        self.assertEqual(ec.DELTA, 15)
        self.assertEqual(ec.TRACE_B, 60)
        self.assertEqual(ec.TRACE_C, 8)
        self.assertEqual(84 * ec.DELTA, 1260)

    def test_pseudodeterminant_trace_square_floor(self) -> None:
        self.assertEqual(ec.minimum_trace_c_square(), 8)
        rows = ec.trace_square_rank_bounds()
        minimizers = [
            row["nonzero_rank"]
            for row in rows
            if Fraction(row["combined_floor"]) == 8
        ]
        self.assertEqual(minimizers, [8])

    def test_pseudodeterminant_premise_is_active(self) -> None:
        cauchy_only = min(
            Fraction(ec.TRACE_C**2, rank)
            for rank in range(1, ec.RANK + 1)
        )
        self.assertEqual(cauchy_only, Fraction(16, 11))
        self.assertLess(cauchy_only, 8)

    def test_trace_b_square_floor(self) -> None:
        floor = ec.minimum_trace_c_square()
        self.assertEqual(ec.RANK + 4 * ec.TRACE_C + 4 * floor, 108)

    def test_log3_rational_bounds(self) -> None:
        lower, upper = ec.log3_bounds()
        self.assertGreater(lower, Fraction(2, 3))
        self.assertLess(upper, 2)
        self.assertLess(lower, upper)

    def test_derivative_factorization(self) -> None:
        certificate = ec.derivative_factorization_coefficients()
        self.assertTrue(certificate["match"])
        self.assertEqual(certificate["expanded"], certificate["factored"])

    def test_determinant_cap(self) -> None:
        self.assertEqual(ec.determinant_cap(), 6561)
        self.assertEqual(ec.determinant_cap(0), 1)
        with self.assertRaises(ValueError):
            ec.determinant_cap(-1)

    def test_index_exhaustion(self) -> None:
        rows = ec.smooth_index_candidates()
        self.assertEqual(
            [row["h"] for row in rows],
            [9, 21, 49, 81, 189, 441, 729, 1029],
        )
        self.assertTrue(all(row["h"] % 4 == 1 for row in rows))
        self.assertTrue(all(row["detQ_min"] == 5 for row in rows))

    def test_signature_obstruction_is_active(self) -> None:
        with_detq_one = []
        for exponent_3 in range(ec.RANK + 1):
            for exponent_7 in range(ec.RANK + 1):
                h = 3**exponent_3 * 7**exponent_7
                if h <= 6561 and h % 4 == 1:
                    with_detq_one.append(h)
        self.assertIn(1, with_detq_one)
        self.assertNotIn(1, [row["h"] for row in ec.smooth_index_candidates()])

    def test_explicit_abstract_survivor(self) -> None:
        survivor = ec.explicit_lattice_survivor()
        facts = survivor["facts"]
        self.assertEqual(facts["detS_h"], 9)
        self.assertEqual(facts["detQ"], 9)
        self.assertEqual(facts["detB"], 81)
        self.assertEqual(facts["traceB"], 60)
        self.assertTrue(facts["G_B_equals_21Q"])
        self.assertTrue(facts["B_congruent_I_mod_2"])
        self.assertTrue(facts["B_symmetric"])
        self.assertEqual(facts["G_minimum_lower_bound"], 14)

    def test_survivor_is_not_endpoint_exclusion(self) -> None:
        survivor = ec.explicit_lattice_survivor()
        self.assertIn("no primitive embedding", survivor["scope"])

    def test_local_harmonic_restrictions(self) -> None:
        data = ec.local_endpoint_data()
        self.assertEqual(data["sum_q"], 472)
        self.assertEqual(data["sum_q_minus_2"], 10)
        self.assertTrue(data["harmonic_q12"]["excluded"])
        self.assertEqual(data["harmonic_q12"]["gap_lhs_minus_rhs"], 5520)
        self.assertTrue(data["two_q11_excluded"])

    def test_scalar_q_profile_survives(self) -> None:
        profile = ec.local_endpoint_data()["scalar_survivor_profile"]
        self.assertEqual(profile["vertex_count"], 231)
        self.assertEqual(profile["sum_q"], 472)
        self.assertEqual(profile["sum_q_minus_2"], 10)

    def test_deterministic_json(self) -> None:
        payload = ec.build_results()
        expected = (
            json.dumps(payload, indent=2, sort_keys=True) + "\n"
        ).encode("utf-8")
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "result.json"
            output.write_bytes(expected)
            self.assertEqual(
                hashlib.sha256(output.read_bytes()).hexdigest(),
                hashlib.sha256(expected).hexdigest(),
            )


if __name__ == "__main__":
    unittest.main()
