from __future__ import annotations

import hashlib
import importlib.util
import json
import unittest
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VERIFIER = load_module("wave101_independent_tests", HERE / "independent_verify.py")
COMPARISON = load_module("wave101_comparison_tests", HERE / "compare_discovery.py")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Wave101IndependentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = VERIFIER.build_results()
        cls.comparison = COMPARISON.compare()

    def test_discovery_manifest_is_frozen_and_complete(self) -> None:
        package = ROOT / "attempts" / "wave101-all-rank-level7-lp"
        manifest = package / "package-manifest.sha256"
        self.assertEqual(
            sha256(manifest),
            "54d620a8644d7efe5d2e418869b035331127862c2125ef3da325272417307619",
        )
        entries = manifest.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(entries), 11)
        for line in entries:
            wanted, relative = line.split("  ", 1)
            self.assertEqual(sha256(ROOT / relative), wanted, relative)

    def test_full_modular_space_and_fricke_involution(self) -> None:
        space = self.result["modular_space"]
        self.assertEqual(space["dimension"], 15)
        self.assertEqual(space["cusp_dimension"], 13)
        self.assertEqual(space["eisenstein_dimension"], 2)
        self.assertEqual(space["sturm_bound"], 14)
        self.assertEqual(space["basis_rank_through_q14"], 15)
        self.assertTrue(space["fricke_square_is_identity"])

    def test_all_poisson_factors_have_correct_sign_and_power(self) -> None:
        self.assertEqual(
            [row["poisson_factor"] for row in self.result["rows"]],
            [str(-(7**power)) for power in range(10, 3, -1)],
        )
        self.assertEqual(
            self.result["normalizations"]["poisson_formula"],
            "Theta_L=-7^(11-q/2)*(Theta_K|_22 W_7)",
        )

    def test_total_exact_bounds_and_parity_rounding(self) -> None:
        expected = {
            2: ("717848/3971", 182),
            4: ("6286208/3971", 1584),
            6: ("45264728/3971", 11400),
            8: ("28919488/361", 80110),
            10: ("2228061848/3971", 561084),
            12: ("15580466396938/82045", 189901474),
            14: ("6793429016900/3709", 1831606638),
        }
        for row in self.result["rows"]:
            certificate = row["prefix_bounds"]["prefix14"]
            self.assertEqual(
                (
                    certificate["bound"],
                    certificate["parity_rounded_bound"],
                ),
                expected[row["q"]],
            )
            self.assertTrue(certificate["exact_strong_duality"])
            self.assertTrue(certificate["all_primal_forms_nonnegative"])
            self.assertTrue(
                certificate["all_dual_multipliers_nonnegative"]
            )

    def test_first_positive_prefix_bounds(self) -> None:
        expected = {
            2: ("prefix13", "329/2", 166),
            4: ("prefix12", "704/5", 142),
            6: ("prefix12", "6632/5", 1328),
            8: ("prefix12", "48128/5", 9626),
            10: ("prefix11", "27008/29", 932),
            12: ("prefix11", "282641/29", 9748),
            14: ("prefix10", "389888/57", 6842),
        }
        for row in self.result["rows"]:
            label, rational, even = expected[row["q"]]
            certificate = row["prefix_bounds"][label]
            self.assertEqual(certificate["bound"], rational)
            self.assertEqual(certificate["parity_rounded_bound"], even)

    def test_triangular_bounds_have_exact_certificates(self) -> None:
        for row in self.result["rows"]:
            certificate = row["triangular_weighted_bound"]
            self.assertGreater(Fraction(certificate["bound"]), 0)
            self.assertTrue(certificate["exact_strong_duality"])
            self.assertTrue(
                certificate["all_dual_multipliers_nonnegative"]
            )

    def test_crucial_short_shell_null_in_every_row(self) -> None:
        for row in self.result["rows"]:
            control = row["zero_prefix_control"]
            self.assertTrue(control["all_22_coordinates_nonnegative"])
            self.assertTrue(control["x7_x8_x9_are_zero"])
        self.assertIn(
            "Every q=2,4,...,14 row",
            self.result["boundary"]["crucial_scalar_null"],
        )

    def test_submitted_integral_even_nulls_pass_independent_forms(self) -> None:
        for row in self.comparison["row_comparisons"]:
            fields = row["zero_prefix_null"]
            self.assertTrue(all(fields.values()), (row["q"], fields))

    def test_mod7_gives_no_objective_rounding_for_these_rows(self) -> None:
        for row in self.result["mod7_scope"]["rows"]:
            self.assertEqual(
                row["affine_direction_rank_on_x7_x8_x9"], 3
            )
            self.assertTrue(row["no_affine_relation_on_x7_x8_x9"])
            self.assertTrue(
                all(
                    not objective["fixed_residue"]
                    for objective in row["objectives"].values()
                )
            )

    def test_mod2_upper_comparisons_and_sharpening(self) -> None:
        upper = self.result["mod2_lattice_upper_comparisons"]
        cosets = 2**44 - 1
        self.assertEqual(upper["prefix_x7_to_x13_upper"], 2 * cosets)
        self.assertEqual(upper["prefix_x7_to_x14_upper"], 88 * cosets)
        self.assertEqual(upper["triangular_weighted_upper"], 88 * cosets)
        comparison = self.comparison["mod2_comparison"]
        self.assertTrue(comparison["submitted_triangular_upper_valid"])
        self.assertEqual(
            comparison["submitted_triangular_upper"],
            8 * upper["prefix_x7_to_x14_upper"],
        )
        self.assertLess(
            comparison["independent_sharper_triangular_upper"],
            comparison["submitted_triangular_upper"],
        )
        largest_lower = max(
            row["triangular_weighted_bound"]["parity_rounded_bound"]
            for row in self.result["rows"]
        )
        self.assertLess(largest_lower, upper["triangular_weighted_upper"])

    def test_signed_unit_dictionary_stops_at_x9(self) -> None:
        dictionary = self.result["dictionary_scope"]
        self.assertEqual(set(dictionary["certified"]), {"x7", "x8", "x9"})
        for label in ("x10", "x11", "x12", "x13", "x14"):
            self.assertIn(label, dictionary["not_certified"])

    def test_discovery_claims_match_without_executing_discovery(self) -> None:
        self.assertTrue(
            self.comparison["all_reported_exact_certificates_match"]
        )
        self.assertTrue(self.comparison["all_zero_prefix_controls_match"])
        self.assertTrue(
            self.comparison[
                "all_mod7_nonfixed_objective_conclusions_match"
            ]
        )
        self.assertEqual(
            self.comparison["manifest_entries_matching"],
            self.comparison["manifest_entry_count"],
        )
        self.assertEqual(
            self.comparison["verdict"], "VERIFIED_WITH_SHARPENING"
        )

    def test_canonical_results_replay_byte_for_byte(self) -> None:
        expected = VERIFIER.canonical_bytes(self.result)
        self.assertEqual((HERE / "independent-results.json").read_bytes(), expected)
        comparison_expected = (
            json.dumps(self.comparison, indent=2, sort_keys=True) + "\n"
        ).encode("utf-8")
        self.assertEqual((HERE / "comparison.json").read_bytes(), comparison_expected)

    def test_no_status_inflation(self) -> None:
        self.assertFalse(self.result["boundary"]["all_rank_row_excluded"])
        self.assertFalse(self.result["boundary"]["graph_constructed"])
        self.assertFalse(self.result["boundary"]["lattice_realized"])
        self.assertEqual(self.result["boundary"]["Conway_99"], "UNKNOWN")
        self.assertEqual(
            self.comparison["boundary"]["Conway_99"], "UNKNOWN"
        )


if __name__ == "__main__":
    unittest.main()
