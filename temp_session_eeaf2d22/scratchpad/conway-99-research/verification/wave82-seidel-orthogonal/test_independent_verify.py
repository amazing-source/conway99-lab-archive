from __future__ import annotations

import copy
import importlib.util
import math
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave82_independent", HERE / "independent_verify.py"
)
VERIFY = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(VERIFY)
ROOT = HERE.parents[1]


class Wave82IndependentTests(unittest.TestCase):
    def test_forward_and_converse_symbolic_coefficients(self) -> None:
        audit = VERIFY.equivalence_audit()
        self.assertEqual(audit["forward"]["square"], "3969I")
        self.assertEqual(audit["converse"]["degree"], 14)
        self.assertEqual(audit["spectrum"], {"+63": 55, "-63": 44})

    def test_three_primary_forced_profile(self) -> None:
        exponents = VERIFY.derive_three_primary_exponents()
        self.assertEqual(exponents, [0] + [2] * 97 + [4])
        self.assertEqual(sum(exponents), 198)
        self.assertTrue(
            all(exponents[i] + exponents[98 - i] == 4 for i in range(99))
        )

    def test_same_determinant_rank_minor_floor_is_not_enough(self) -> None:
        hostile = [0] + [2] * 96 + [3, 3]
        self.assertEqual(len(hostile), 99)
        self.assertEqual(sum(hostile), 198)
        self.assertEqual(sum(value == 0 for value in hostile), 1)
        self.assertGreaterEqual(hostile[0] + hostile[1], 2)
        with self.assertRaisesRegex(VERIFY.CheckError, "reciprocity"):
            VERIFY.validate_reciprocal_exponents(hostile, 4)

    def test_seven_primary_transfer_factor_is_a_unit(self) -> None:
        audit = VERIFY.seven_adic_audit()
        self.assertTrue(audit["factor_is_in_GL_99_Z7"])
        self.assertEqual(audit["factor_eigenvalues"]["one_line"], "-9/10")

    def test_all_eight_global_smith_profiles(self) -> None:
        for rank in VERIFY.RANKS:
            profile = VERIFY.validate_invariant_factors(rank)
            factors = VERIFY.invariant_factors(rank)
            self.assertEqual(len(factors), 99)
            self.assertEqual(math.prod(factors), 63**99)
            self.assertEqual(profile["rank_f3"], 1)
            self.assertEqual(
                sum(value % 7 != 0 for value in factors), rank
            )
            self.assertTrue(
                all(factors[i] * factors[98 - i] == 3969
                    for i in range(99))
            )

    def test_primary_alignment_is_not_optional(self) -> None:
        threes = VERIFY.derive_three_primary_exponents()
        sevens = list(reversed(VERIFY.seven_primary_exponents(28)))
        hostile = [3**a * 7**b for a, b in zip(threes, sevens)]
        self.assertEqual(math.prod(hostile), 63**99)
        self.assertTrue(
            any(b % a for a, b in zip(hostile, hostile[1:]))
        )

    def test_14_regular_circulant_passes_local_checks_but_not_square(self) -> None:
        adjacency = VERIFY.circulant_degree_fourteen()
        matrix = VERIFY.t_from_adjacency(adjacency)
        self.assertTrue(all(sum(row) == 63 for row in matrix))
        self.assertEqual(VERIFY.rank_mod_prime(matrix, 3), 1)
        self.assertTrue(
            all(value % 9 == 7 for row in matrix for value in row)
        )
        with self.assertRaisesRegex(VERIFY.CheckError, "T\\^2"):
            VERIFY.adjacency_from_t(matrix)

    def test_scalar_orthogonal_matrix_does_not_pass_alphabet(self) -> None:
        matrix = VERIFY.zeros(99)
        for i in range(99):
            matrix[i][i] = 63
        self.assertEqual(
            VERIFY.multiply(matrix, matrix),
            [[3969 * (i == j) for j in range(99)] for i in range(99)],
        )
        with self.assertRaisesRegex(VERIFY.CheckError, "diagonal"):
            VERIFY.adjacency_from_t(matrix)

    def test_bad_rank_and_status_mutations_are_detected(self) -> None:
        result = VERIFY.build_result(ROOT)
        hostile = copy.deepcopy(result)
        hostile["status"]["surviving_ranks"].append(44)
        self.assertNotEqual(
            hostile["status"]["surviving_ranks"], list(VERIFY.RANKS)
        )
        self.assertEqual(result["status"]["conway_99"], "UNKNOWN")
        self.assertEqual(result["status"]["novelty"], "UNKNOWN")

    def test_frozen_discovery_manifest(self) -> None:
        inputs = VERIFY.check_frozen_inputs(ROOT)
        key = "attempts/wave82-seidel-orthogonal/package-manifest.sha256"
        self.assertEqual(
            inputs[key], VERIFY.EXPECTED_DISCOVERY_MANIFEST
        )


if __name__ == "__main__":
    unittest.main()
