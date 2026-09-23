from __future__ import annotations

import cmath
import hashlib
import importlib.util
import json
import math
import unittest
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MODULE_PATH = HERE / "independent_verify.py"
SPEC = importlib.util.spec_from_file_location("wave86_independent", MODULE_PATH)
assert SPEC and SPEC.loader
VERIFIER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFIER)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Wave86IndependentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = VERIFIER.verify_exact()

    def test_sealed_discovery_manifest_and_entries(self) -> None:
        package = ROOT / "attempts" / "wave86-level7-exact"
        manifest = package / "package-manifest.sha256"
        self.assertEqual(
            sha256(manifest),
            "c6066fd10258578c15e511f3802217e4ff613ffe3d3b3b8f11e804f0316ac75d",
        )
        for line in manifest.read_text(encoding="utf-8").splitlines():
            wanted, relative = line.split("  ", 1)
            self.assertEqual(sha256(ROOT / relative), wanted, relative)

    def test_dimension_sturm_and_complete_basis(self) -> None:
        space = self.result["modular_space"]
        self.assertEqual(space["index"], 8)
        self.assertEqual(space["genus"], 0)
        self.assertEqual(space["cusp_dimension"], 13)
        self.assertEqual(space["eisenstein_dimension"], 2)
        self.assertEqual(space["dimension"], 15)
        self.assertEqual(space["sturm_bound"], 14)
        self.assertEqual(space["basis_rank_through_q14"], 15)

    def test_incomplete_basis_is_rejected(self) -> None:
        basis = VERIFIER.select_full_basis()
        incomplete = VERIFIER.coefficient_rows(basis[:-1])
        self.assertEqual(VERIFIER.matrix_rank(incomplete), 14)
        with self.assertRaises(ValueError):
            VERIFIER.inverse(incomplete)

    def test_gauss_sum_phase_directly(self) -> None:
        gauss = sum(
            VERIFIER.chi(a) * cmath.exp(2j * math.pi * a / 7)
            for a in range(1, 8)
        )
        self.assertAlmostEqual(gauss.real, 0.0, places=12)
        self.assertAlmostEqual(gauss.imag, math.sqrt(7), places=12)
        correct, _ = VERIFIER.product_fricke(((3, "C"), (19, "C")))
        omitted, _ = VERIFIER.product_fricke(
            ((3, "C"), (19, "C")), omit_gauss_phase=True
        )
        self.assertEqual(correct, -Fraction(7**10))
        self.assertEqual(omitted, Fraction(7**10))

    def test_individual_fricke_at_fixed_point(self) -> None:
        tau_imaginary = 1 / math.sqrt(7)
        q = math.exp(-2 * math.pi * tau_imaginary)
        for weight in (3, 5, 9, 19):
            c_series = VERIFIER.EISENSTEIN[weight, "C"]
            t_series = VERIFIER.EISENSTEIN[weight, "T"]
            c_value = sum(float(c_series[n]) * q**n for n in range(51))
            t_value = sum(float(t_series[n]) * q**n for n in range(51))
            left = (1j ** (-weight)) * c_value
            right = -1j * 7 ** ((weight - 1) // 2) * t_value
            scale = max(1.0, abs(left), abs(right))
            self.assertLess(abs(left - right) / scale, 2e-12)

    def test_fricke_product_is_exact_involution(self) -> None:
        basis = VERIFIER.select_full_basis()
        fricke = VERIFIER.fricke_prefix_operator(basis)
        square = VERIFIER.matrix_product(fricke, fricke)
        expected = [
            [Fraction(r == c) for c in range(15)]
            for r in range(15)
        ]
        self.assertEqual(square, expected)

    def test_poisson_sign_power_and_wrong_controls(self) -> None:
        # 7^(22/2) * i^(-22) / sqrt(7^16) = -7^3.
        self.assertEqual(VERIFIER.theta_transfer_constant(), -Fraction(7**3))
        hostile = self.result["hostile_controls"]
        self.assertEqual(hostile["wrong_theta_sign_y0"], "-1")
        self.assertEqual(hostile["wrong_theta_power_7_squared_y0"], "1/7")

    def test_positive_identity_is_derived_exactly(self) -> None:
        identity = self.result["positive_identity"]
        self.assertEqual(identity["rational_lower_bound"], "1997236/341")
        self.assertTrue(identity["all_multipliers_positive"])
        self.assertEqual(
            identity["multipliers"],
            {
                "x8": "180/217",
                "x9": "2344/2387",
                "x11": "1/2387",
                "y1": "1118523/341",
                "y2": "134113/341",
                "y3": "9604/341",
                "y4": "343/341",
            },
        )

    def test_wave71_congruence_and_norm_indexing_only(self) -> None:
        imported = json.loads(
            (
                ROOT
                / "verification/wave71-modular-theta-extension"
                / "independent-results.json"
            ).read_text(encoding="utf-8")
        )
        mod7 = imported["level_one_mod_7"]
        self.assertEqual(
            mod7["q16_relation_mod_14"],
            "N14+N16+N18=2 mod 14",
        )
        self.assertEqual(
            mod7["theta_initial_shape"],
            "1+0q+...+0q^6+N14 q^7+N16 q^8+N18 q^9+...",
        )
        identity = self.result["positive_identity"]
        self.assertEqual(identity["only_external_arithmetic_input"], "Wave71: S=2 mod 14")
        self.assertEqual(identity["forced_integer_lower_bound"], 5868)
        self.assertEqual(identity["short_vector_conclusion"], "N14+N16+N18>=5868")

    def test_scalar_control_is_only_a_finite_null(self) -> None:
        control = self.result["scalar_control"]
        self.assertEqual(control["classification"], "finite formal scalar null only")
        self.assertTrue(control["not_a_lattice_or_graph"])
        self.assertEqual(control["checked_through_q"], 50)
        self.assertTrue(control["integral_even_nonnegative"])
        self.assertEqual(sum(control["x0_to_x14"][7:10]), 5868)
        self.assertFalse(self.result["status"]["lattice_realized"])
        self.assertEqual(self.result["status"]["Conway_99"], "UNKNOWN")

    def test_discovery_claim_fields_match_without_executing_discovery(self) -> None:
        discovery = json.loads(
            (
                ROOT / "attempts/wave86-level7-exact/exact-results.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(
            discovery["coefficient_identity"]["rational_lower_bound"],
            self.result["positive_identity"]["rational_lower_bound"],
        )
        self.assertEqual(
            discovery["coefficient_identity"]["forced_integer_lower_bound"],
            self.result["positive_identity"]["forced_integer_lower_bound"],
        )
        self.assertEqual(
            discovery["formal_scalar_control"]["x0_to_x14"],
            self.result["scalar_control"]["x0_to_x14"],
        )
        self.assertEqual(
            discovery["formal_scalar_control"]["y0_to_y14"],
            self.result["scalar_control"]["y0_to_y14"],
        )

    def test_canonical_result_replays_byte_for_byte(self) -> None:
        encoded = (
            json.dumps(self.result, indent=2, sort_keys=True) + "\n"
        )
        self.assertEqual(
            (HERE / "independent-results.json").read_text(encoding="utf-8"),
            encoded,
        )


if __name__ == "__main__":
    unittest.main()
