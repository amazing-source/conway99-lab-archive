from __future__ import annotations

import importlib.util
import math
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).with_name("exact_check.py")
SPEC = importlib.util.spec_from_file_location("wave97_exact_check", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class Wave97ExactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = CHECK.build_results()

    def test_status_is_not_inflated(self) -> None:
        self.assertEqual(self.result["claim_label"], "DERIVED")
        self.assertFalse(self.result["boundary"]["rank_28_excluded"])
        self.assertEqual(self.result["boundary"]["Conway_99"], "UNKNOWN")

    def test_schur_square_is_zero_sum_hyperplane(self) -> None:
        square = self.result["schur_hilbert"]["schur_square"]
        self.assertEqual(square["dimension"], 98)
        self.assertEqual(square["multiplication_kernel_dimension"], 308)

    def test_schur_cube_is_full(self) -> None:
        cube = self.result["schur_hilbert"]["schur_cube"]
        self.assertEqual(cube["dimension"], 99)
        self.assertEqual(cube["evaluation_kernel_dimension"], 3961)

    def test_hilbert_function_and_veronese_circuit(self) -> None:
        schur = self.result["schur_hilbert"]
        self.assertEqual(
            schur["evaluation_algebra"]["hilbert_function_degrees_0_to_3"],
            [1, 28, 98, 99],
        )
        self.assertEqual(
            schur["evaluation_algebra"]["h_vector"], [1, 27, 70, 1]
        )
        self.assertTrue(
            schur["quadratic_veronese"]["every_98_images_independent"]
        )

    def test_all_exterior_rank_rows(self) -> None:
        rows = self.result["exterior_square"]["all_rank_rows"]
        self.assertEqual(
            [row["rank_F7_S"] for row in rows],
            list(range(28, 43, 2)),
        )
        for row in rows:
            self.assertEqual(row["order"], math.comb(99, 2))
            self.assertEqual(
                row["rank_F7_C2S"],
                math.comb(row["rank_F7_S"], 2),
            )
            self.assertEqual(
                sum(
                    int(exponent) * count
                    for exponent, count in row[
                        "7_adic_valuation_counts"
                    ].items()
                ),
                9702,
            )

    def test_endpoint_exterior_smith_form(self) -> None:
        endpoint = self.result["exterior_square"]["endpoint_rank_28"]
        self.assertEqual(endpoint["rank_F7_C2S"], 378)
        self.assertEqual(
            [
                (entry["factor"], entry["multiplicity"])
                for entry in endpoint["smith_normal_form"]
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

    def test_exterior_row_geometry(self) -> None:
        geometry = self.result["exterior_square"]["row_geometry"]
        self.assertEqual(geometry["distinguished_row_weight"], 1947)
        self.assertEqual(geometry["integral_row_square_norm"], 7203)
        self.assertEqual(geometry["row_square_norm_mod_7"], 0)
        self.assertEqual(
            geometry["forced_scalar_closed_weight_1947_words"], 29106
        )
        self.assertEqual(
            sum(geometry["column_counts"].values()), math.comb(99, 2)
        )

    def test_exterior_spectrum(self) -> None:
        structure = self.result["exterior_square"][
            "rational_and_integral_structure"
        ]
        self.assertEqual(structure["trace"], -4851)
        self.assertTrue(structure["mod_7_square_zero"])

    def test_generalized_weight_boundary(self) -> None:
        profile = self.result["generalized_hamming_weights"]
        self.assertEqual(profile["girth_lower_bound"], 6)
        self.assertEqual(
            profile["first_weight_boundary_after_forced_short_vector"],
            "6<=d1<=18",
        )
        self.assertFalse(profile["contradiction"])

    def test_orthogonal_point_orbits_partition(self) -> None:
        orbits = self.result["orthogonal_orbits"][
            "projective_point_orbits_in_O_minus_16_7"
        ]
        self.assertEqual(
            orbits["isotropic"]
            + orbits["square_anisotropic"]
            + orbits["nonsquare_anisotropic"],
            orbits["total"],
        )
        self.assertEqual(orbits["total"], (7**16 - 1) // 6)

    def test_norm16_and_norm18_share_an_orbit(self) -> None:
        reduction = self.result["orthogonal_orbits"][
            "short_vector_orbit_reduction"
        ]
        self.assertTrue(
            reduction["norm_16_and_18_same_projective_orthogonal_orbit"]
        )

    def test_embedding_count_is_exact(self) -> None:
        profile = self.result["orthogonal_orbits"]
        self.assertEqual(
            len(str(profile["number_of_embedded_subspaces"])), 352
        )
        self.assertTrue(profile["single_ambient_orthogonal_group_orbit"])

    def test_hostile_rank_rejected(self) -> None:
        with self.assertRaises(AssertionError):
            CHECK.exterior_smith_row(27)

    def test_hostile_orthogonal_sign_rejected(self) -> None:
        with self.assertRaises(AssertionError):
            CHECK.orthogonal_group_order("unknown", 8)


if __name__ == "__main__":
    unittest.main()
