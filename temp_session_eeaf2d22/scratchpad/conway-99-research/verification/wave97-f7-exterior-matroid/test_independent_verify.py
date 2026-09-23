from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave97_independent",
    HERE / "independent_verify.py",
)
assert SPEC and SPEC.loader
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)


class Wave97IndependentTests(unittest.TestCase):
    def test_frozen_inputs(self) -> None:
        result = VERIFY.verify_inputs()
        self.assertTrue(result["passed"], result["failures"])
        self.assertEqual(result["discovery_files"], 11)
        self.assertEqual(result["discovery_manifest_entries"], 10)

    def test_schur_square_cube_and_hilbert(self) -> None:
        result = VERIFY.schur_profile()
        self.assertTrue(result["passed"])
        self.assertEqual(result["rank_J_minus_I"], 98)
        self.assertEqual(
            result["hilbert_function_degrees_0_to_3"],
            [1, 28, 98, 99],
        )
        self.assertEqual(result["first_differences"], [1, 27, 70, 1])
        self.assertEqual(result["symmetric_square_kernel"], 308)
        self.assertEqual(result["symmetric_cube_kernel"], 3961)

    def test_hostile_order_change_breaks_quadratic_relation(self) -> None:
        order = 98
        matrix = [
            [0 if row == column else 1 for column in range(order)]
            for row in range(order)
        ]
        self.assertEqual(VERIFY.rank_mod(matrix, 7), 98)
        self.assertNotEqual(VERIFY.rank_mod(matrix, 7), order - 1)

    def test_compound_rank_and_cauchy_binet_controls(self) -> None:
        result = VERIFY.exterior_rank_controls()
        self.assertTrue(result["passed"])
        self.assertTrue(result["Cauchy_Binet_small_control"])
        self.assertEqual(
            [row["compound_rank"] for row in result["rank_controls"]],
            [0, 0, 1, 3, 6],
        )

    def test_all_live_smith_rows(self) -> None:
        for rank in VERIFY.LIVE_RANKS:
            result = VERIFY.exterior_smith(rank)
            self.assertTrue(result["passed"])
            self.assertEqual(result["rank_F7_C2S"], rank * (rank - 1) // 2)
            self.assertEqual(result["determinant_valuations"], {
                "2": 98,
                "5": 98,
                "7": 9702,
            })

    def test_endpoint_smith_and_24010(self) -> None:
        endpoint = VERIFY.exterior_smith(28)
        self.assertEqual(
            [
                (row["factor"], row["multiplicity"])
                for row in endpoint["smith_normal_form"]
            ],
            [
                (1, 378),
                (7, 1204),
                (49, 1687),
                (343, 1204),
                (2401, 280),
                (24010, 98),
            ],
        )
        audit = endpoint["factor_24010_audit"]
        self.assertEqual(audit["raw_pair_products_equal_24010"], 27)
        self.assertEqual(audit["smith_invariant_factors_equal_24010"], 98)
        self.assertGreaterEqual(audit["terminal_7_power_4_slots"], 98)

    def test_24010_toy_determinantal_divisors(self) -> None:
        result = VERIFY.factor_24010_hostile_control()
        self.assertTrue(result["passed"])
        self.assertTrue(result["raw_products_are_not_the_smith_chain"])
        self.assertTrue(result["determinantal_divisors_match"])
        self.assertEqual(
            result["toy_actual_smith"],
            [7, 49, 49, 3430, 3430, 24010],
        )
        self.assertEqual(
            result["hostile_rank_14"]["factor_24010_count"],
            91,
        )

    def test_row_weight_and_spectrum(self) -> None:
        row = VERIFY.exterior_row_geometry()
        spectrum = VERIFY.exterior_spectrum()
        self.assertTrue(row["passed"])
        self.assertEqual(row["distinguished_row_weight"], 1947)
        self.assertEqual(row["integral_row_square_norm"], 7203)
        self.assertTrue(spectrum["passed"])
        self.assertEqual(spectrum["trace"], -4851)

    def test_compound_projectivity(self) -> None:
        result = VERIFY.projectivity_profile()
        self.assertTrue(result["passed"])
        self.assertTrue(result["compound_columns_nonzero"])
        self.assertTrue(result["compound_columns_pairwise_nonproportional"])
        self.assertEqual(result["dual_distance_compound_lower_bound"], 3)

    def test_generalized_weight_bounds(self) -> None:
        result = VERIFY.generalized_weights()
        self.assertTrue(result["passed"])
        self.assertEqual(result["first_weight_refinement"], "6<=d_1(R^perp)<=18")
        self.assertTrue(
            all(row["lower"] <= row["singleton_upper"] for row in result["rows"])
        )

    def test_orthogonal_point_counts_and_embedding(self) -> None:
        result = VERIFY.orthogonal_profile()
        self.assertTrue(result["passed"])
        self.assertEqual(result["embedding_count_decimal_digits"], 352)
        self.assertEqual(
            result["small_dimension_formula_control"],
            result["small_dimension_bruteforce_control"],
        )
        self.assertTrue(
            result["hostile_sign_controls"]["plus_ambient_ratio_integral"]
        )
        self.assertTrue(
            result["hostile_sign_controls"]["minus_complement_ratio_integral"]
        )
        self.assertTrue(
            result["hostile_sign_controls"]["plus_ambient_ratio_differs"]
        )
        self.assertTrue(
            result["hostile_sign_controls"]["minus_complement_ratio_differs"]
        )

    def test_norm16_norm18_same_orbit_but_norm14_separate(self) -> None:
        classes = VERIFY.orthogonal_profile()["short_classes"]
        self.assertTrue(classes["ratio_is_square_mod_7"])
        self.assertTrue(classes["norm16_and_norm18_same_projective_orbit"])
        self.assertIn("isotropic", classes["norm14_self_dot_0"])

    def test_provenance_correction(self) -> None:
        provenance = VERIFY.provenance_profile()
        self.assertTrue(provenance["provenance_correction_required"])
        prior = provenance["already_implied_by_Wave51_not_new_to_repository"]
        self.assertTrue(any("R*R=1_perp" in row for row in prior))
        self.assertTrue(any("circuit" in row for row in prior))
        new = provenance["new_to_repository_Wave97_consequences"]
        self.assertTrue(any("R*R*R" in row for row in new))

    def test_discovery_comparison_and_fail_closed_status(self) -> None:
        result = VERIFY.build_results()
        self.assertEqual(
            result["verdict"],
            "VERIFIED_WITH_PROVENANCE_CORRECTION",
        )
        self.assertTrue(result["discovery_comparison"]["passed"])
        self.assertFalse(result["status"]["rank_28_excluded"])
        self.assertFalse(result["status"]["strict_n3_upper_bound_below_4158"])
        self.assertEqual(result["status"]["Conway_99"], "UNKNOWN")

    def test_canonical_replay(self) -> None:
        canonical = HERE / "independent-results.json"
        expected = VERIFY.canonical_bytes(VERIFY.build_results())
        self.assertEqual(canonical.read_bytes(), expected)
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "result.json"
            path.write_bytes(expected)
            self.assertEqual(
                json.loads(path.read_text(encoding="utf-8"))["claim_label"],
                "VERIFIED",
            )


if __name__ == "__main__":
    unittest.main()
