from __future__ import annotations

import importlib.util
import math
import unittest
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave135_independent_face",
    HERE / "independent_face.py",
)
assert SPEC is not None and SPEC.loader is not None
FACE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(FACE)


def direct_expanded_coefficient(source, target):
    """Independent small-target multinomial expansion."""

    zeros, odd, twos = source
    _target_zeros, target_odd, target_twos = target
    total = 0
    for y_from_zero in range(target_odd + 1):
        y_from_two = target_odd - y_from_zero
        if y_from_zero > zeros or y_from_two > twos:
            continue
        for z_from_zero in range(target_twos + 1):
            for z_from_odd in range(target_twos - z_from_zero + 1):
                z_from_two = target_twos - z_from_zero - z_from_odd
                if (
                    y_from_zero + z_from_zero > zeros
                    or z_from_odd > odd
                    or y_from_two + z_from_two > twos
                ):
                    continue
                zero_factor = (
                    math.factorial(zeros)
                    // (
                        math.factorial(zeros - y_from_zero - z_from_zero)
                        * math.factorial(y_from_zero)
                        * math.factorial(z_from_zero)
                    )
                    * 2**y_from_zero
                )
                odd_factor = (
                    math.comb(odd, z_from_odd) * (-1) ** z_from_odd
                )
                two_factor = (
                    math.factorial(twos)
                    // (
                        math.factorial(twos - y_from_two - z_from_two)
                        * math.factorial(y_from_two)
                        * math.factorial(z_from_two)
                    )
                    * (-2) ** y_from_two
                )
                total += zero_factor * odd_factor * two_factor
    return total


class Wave135IndependentFaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = FACE.build_result()

    def test_no_wave135_discovery_import(self) -> None:
        source = (HERE / "independent_face.py").read_text(encoding="utf-8")
        self.assertNotIn("import face_rank", source)
        self.assertNotIn("import row_generate", source)

    def test_sealed_discovery_bind(self) -> None:
        self.assertEqual(self.result["claim_label"], "VERIFIED")
        self.assertEqual(
            self.result["sealed_discovery"]["entries_checked"], 16
        )
        audit = self.result["sealed_discovery_audit"]
        self.assertTrue(audit["exact_dimensions_match"])
        self.assertEqual(
            audit["dependency_artifact"]["primitive_dependencies_checked"],
            18,
        )
        self.assertEqual(
            audit["dependency_artifact"]["independent_row_rank"], 143
        )
        self.assertEqual(audit["rational_feasibility"], "UNKNOWN_WALL")

    def test_frozen_orbit_partition(self) -> None:
        self.assertEqual(len(FACE.all_orbit_representatives()), 1_275)
        self.assertEqual(len(FACE.primal_orbits()), 1_119)
        self.assertEqual(len(FACE.dual_orbits(allowed=True)), 1_114)
        self.assertEqual(len(FACE.dual_orbits(allowed=False)), 161)

    def test_exact_zero_row_rank_and_nullity(self) -> None:
        face = self.result["zero_row_face"]
        self.assertEqual(face["rank_over_Q"], 143)
        self.assertEqual(face["linear_nullity"], 976)
        self.assertEqual(face["row_dependencies"], 18)
        self.assertNotEqual(
            self.result["certificate"]["zero_row_face"][
                "minor_determinant_mod_prime"
            ],
            0,
        )

    def test_shell_upper_bound_is_exact(self) -> None:
        records = self.result["zero_row_face"]["block_records"]
        self.assertEqual(
            [record["target_odd_count"] for record in records],
            [0, 2, 4, 6, 92, 94, 96, 98],
        )
        self.assertEqual(
            [record["dependency_lower_bound"] for record in records],
            [0, 5, 4, 3, 3, 2, 1, 0],
        )
        self.assertEqual(
            sum(record["rank_upper_bound"] for record in records),
            143,
        )

    def test_affine_and_torsion_tightened_ranks(self) -> None:
        affine = self.result["affine_identity_and_size_slice"]
        torsion = self.result["torsion_size_tightening"]
        self.assertEqual((affine["rank_over_Q"], affine["affine_dimension"]),
                         (145, 974))
        self.assertEqual((torsion["rank_over_Q"], torsion["affine_dimension"]),
                         (146, 973))

    def test_dual_torsion_shell_is_redundant(self) -> None:
        audit = self.result["shell_fibre_audit"]
        dual = audit["dual_zero_residue_orbit_sum"]
        self.assertFalse(dual["independent_after_primal_equality"])
        self.assertEqual(audit["rank_with_primal_torsion"], 146)
        self.assertEqual(audit["rank_with_both_torsion_equalities"], 146)
        fibres = audit["constant_fibre_consequences"]
        self.assertEqual(
            fibres["additional_numeric_equalities_over_Q"], "NONE"
        )
        self.assertEqual(
            fibres["integer_divisibility_separate_from_rational_face"][
                "primal_orbit_shell_multiple"
            ],
            2**54,
        )
        self.assertEqual(
            fibres["integer_divisibility_separate_from_rational_face"][
                "dual_orbit_shell_multiple"
            ],
            2**44,
        )

    def test_reduced_transform_against_multinomial_expansion(self) -> None:
        samples = (
            ((85, 14, 0), (98, 0, 1)),
            ((73, 24, 2), (96, 2, 1)),
            ((63, 30, 6), (90, 6, 3)),
        )
        for source, target in samples:
            full_orbit = (
                direct_expanded_coefficient(source, target)
                + direct_expanded_coefficient(
                    FACE.swap_zero_two(source), target
                )
            )
            reduced = FACE.reduced_face_entry(source, target)
            self.assertEqual(
                full_orbit,
                2 ** (target[1] + 1) * reduced,
            )

    def test_frozen_forced_bound_tables(self) -> None:
        primal, dual = FACE.frozen_lower_bounds()
        self.assertEqual(len(primal), 42)
        self.assertEqual(len(dual), 22)
        self.assertEqual(primal[(85, 14, 0)], 198)
        self.assertEqual(dual[(72, 24, 3)], 1_386)
        self.assertEqual(dual[(75, 24, 0)], 1_386)

    def test_rational_primal_contract_is_dense_and_exact(self) -> None:
        keys = [
            FACE.composition_key(source) for source in FACE.primal_orbits()
        ]
        candidate = {
            "format": "wave135-z4-rational-primal-v1",
            "model": FACE.MODEL_TORSION,
            "coefficients": {key: 0 for key in keys},
        }
        model, coefficients = FACE.load_dense_primal(candidate)
        self.assertEqual(model, FACE.MODEL_TORSION)
        self.assertEqual(len(coefficients), 1_119)

        missing = {
            **candidate,
            "coefficients": dict(candidate["coefficients"]),
        }
        missing["coefficients"].pop(keys[-1])
        with self.assertRaises(AssertionError):
            FACE.load_dense_primal(missing)

        floating = {
            **candidate,
            "coefficients": dict(candidate["coefficients"]),
        }
        floating["coefficients"][keys[0]] = 0.0
        with self.assertRaises(AssertionError):
            FACE.load_dense_primal(floating)

        with self.assertRaises(AssertionError):
            FACE.verify_rational_primal(candidate)

    def test_generic_farkas_sign_convention(self) -> None:
        margin = FACE.verify_farkas_arrays(
            equality_rows=[[1]],
            equality_rhs=[0],
            equality_multipliers=[Fraction(-1)],
            inequality_rows=[[1]],
            inequality_lower=[1],
            inequality_multipliers=[Fraction(1)],
        )
        self.assertEqual(margin, 1)
        with self.assertRaises(AssertionError):
            FACE.verify_farkas_arrays(
                equality_rows=[[1]],
                equality_rhs=[0],
                equality_multipliers=[Fraction(1)],
                inequality_rows=[[1]],
                inequality_lower=[1],
                inequality_multipliers=[Fraction(-1)],
            )

    def test_full_farkas_contract_rejects_unknown_or_zero(self) -> None:
        unknown = {
            "format": "wave135-z4-farkas-v1",
            "model": FACE.MODEL_BASE,
            "equality_multipliers": {"not_a_row": 1},
            "inequality_multipliers": {},
        }
        with self.assertRaises(AssertionError):
            FACE.verify_farkas_candidate(unknown)

        zero = {
            "format": "wave135-z4-farkas-v1",
            "model": FACE.MODEL_BASE,
            "equality_multipliers": {},
            "inequality_multipliers": {},
        }
        with self.assertRaises(AssertionError):
            FACE.verify_farkas_candidate(zero)

        negative = {
            "format": "wave135-z4-farkas-v1",
            "model": FACE.MODEL_BASE,
            "equality_multipliers": {},
            "inequality_multipliers": {"primal:99,0,0": -1},
        }
        with self.assertRaises(AssertionError):
            FACE.verify_farkas_candidate(negative)

    def test_unknown_wall(self) -> None:
        wall = self.result["status_wall"]
        self.assertEqual(wall["rational_feasibility"], "UNKNOWN_WALL")
        self.assertEqual(wall["integral_feasibility"], "UNKNOWN")
        self.assertEqual(wall["Conway_99"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
