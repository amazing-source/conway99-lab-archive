from __future__ import annotations

import unittest
from fractions import Fraction

import incidence_spectral as wave


class Wave59ExactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = wave.build_result()
        cls.relations = cls.result["triangle_relations"]
        cls.incidence = cls.result["incidence_graph"]
        cls.lines = cls.result["triangle_line_graph"]
        cls.nonbacktracking = cls.result["nonbacktracking"]

    def test_relation_valencies(self) -> None:
        self.assertEqual(
            self.relations["valencies"],
            {"I": 1, "K": 18, "B": 36, "C": 144, "D": 32},
        )

    def test_cross_edge_equation(self) -> None:
        values = self.relations["valencies"]
        self.assertEqual(2 * values["B"] + values["C"], 216)

    def test_no_automorphism_assumption(self) -> None:
        self.assertFalse(self.relations["automorphism_assumed"])

    def test_incidence_sizes_and_degrees(self) -> None:
        self.assertEqual(
            self.incidence["bipartition"],
            {
                "points": 99,
                "triangles": 231,
                "point_degree": 7,
                "triangle_degree": 3,
                "incidences": 693,
            },
        )

    def test_incidence_spectrum_multiplicities(self) -> None:
        self.assertEqual(
            sum(item["multiplicity"] for item in self.incidence["spectrum"]),
            330,
        )
        self.assertEqual(self.incidence["trace_square"], 1386)

    def test_girth_and_diameter(self) -> None:
        self.assertEqual(self.incidence["girth"], 8)
        self.assertEqual(self.incidence["diameter"], 6)

    def test_point_root_layers(self) -> None:
        point = self.incidence["point_root"]
        self.assertEqual(point["distance_layers"], [1, 7, 14, 84, 84, 140])
        self.assertEqual(
            point["intersection_array"],
            {"b": [7, 2, 6, 2, 5], "c": [1, 1, 1, 2, 3]},
        )
        self.assertTrue(point["distance_regular_around_every_point"])

    def test_triangle_root_layers(self) -> None:
        triangle = self.incidence["triangle_root"]
        self.assertEqual(
            triangle["distance_layers"], [1, 3, 18, 36, 180, 60, 32]
        )
        self.assertEqual(triangle["distance_4_predecessors"], {"B": 2, "C": 1})
        self.assertFalse(triangle["distance_regular_around_triangle"])

    def test_distance_biregular_case_is_not_misapplied(self) -> None:
        theorem = self.incidence["fiol_theorem_6_case"]
        self.assertEqual(theorem["case"], "c")
        self.assertEqual(theorem["m_zero"], theorem["larger_minus_smaller"])
        self.assertFalse(theorem["ordinary_regular_spectral_excess_applied_to_L"])
        self.assertFalse(self.incidence["distance_biregular"])

    def test_line_graph_spectrum(self) -> None:
        self.assertEqual(
            self.lines["spectrum"],
            [
                {"eigenvalue": 18, "multiplicity": 1},
                {"eigenvalue": 7, "multiplicity": 54},
                {"eigenvalue": 0, "multiplicity": 44},
                {"eigenvalue": -3, "multiplicity": 132},
            ],
        )

    def test_predistance_polynomial(self) -> None:
        self.assertEqual(
            self.lines["predistance_polynomials"][3]["coefficients_low_to_high"],
            ["25/2", "19/12", "-35/36", "1/18"],
        )

    def test_spectral_excess_gap(self) -> None:
        self.assertEqual(self.lines["spectral_excess"], "50")
        self.assertEqual(self.lines["actual_excess"], "32")
        self.assertEqual(self.lines["spectral_excess_gap"], "18")

    def test_walk_tables(self) -> None:
        self.assertEqual(
            self.lines["walk_tables"]["K_squared"],
            {"I": 18, "K": 5, "B": 2, "C": 1, "D": 0},
        )
        self.assertEqual(
            self.lines["walk_tables"]["K_cubed"],
            {"I": 90, "K": 59, "B": 26, "C": 22, "D": 18},
        )

    def test_p3_relation_entries(self) -> None:
        self.assertEqual(
            self.lines["p3_relation_entries"],
            {"I": "0", "K": "0", "B": "-1/2", "C": "1/4", "D": "1"},
        )

    def test_p2_relation_entries_and_defect_transfer(self) -> None:
        self.assertEqual(
            self.lines["p2_relation_entries"],
            {"I": "0", "K": "0", "B": "3/2", "C": "3/4", "D": "0"},
        )
        self.assertEqual(
            self.lines["defect"]["distance_transfer_identity"],
            "p2(K)-A_distance_2 = -(p3(K)-A_D)",
        )

    def test_defect_norm_and_row_sum(self) -> None:
        defect = self.lines["defect"]
        self.assertEqual(defect["row_sum"], "18")
        self.assertEqual(defect["normalized_frobenius_norm_squared"], "18")
        self.assertFalse(defect["signed_integral_form"]["psd"])

    def test_projection_residual(self) -> None:
        projection = self.lines["distance_matrix_projection"]
        self.assertEqual(projection["projection"], "(16/25)*p3(K)")
        self.assertEqual(projection["normalized_residual_norm_squared"], "288/25")
        self.assertEqual(projection["angle_cosine"], "4/5")

    def test_pair_neighborhood_gram_is_full_rank(self) -> None:
        gram = self.lines["gram_constraints"]
        self.assertEqual(gram["rank"], 231)
        self.assertEqual(
            gram["positive_definite_lower_bound"],
            "lambda_min >= 153 - 30 - 36 = 87",
        )
        self.assertFalse(gram["rank_or_psd_contradiction"])

    def test_nonbacktracking_girth_moments(self) -> None:
        self.assertEqual(
            self.nonbacktracking["trace_H_powers"],
            {
                "2": 0,
                "4": 0,
                "6": 0,
                "8": 33264,
                "10": 665280,
                "12": 6020784,
                "14": 69854400,
            },
        )

    def test_short_cycle_counts(self) -> None:
        self.assertEqual(
            self.nonbacktracking["simple_cycle_counts"],
            {
                "8": 2079,
                "10": 33264,
                "12": 250866,
                "14": 2494800,
            },
        )

    def test_moore_bound_is_not_a_contradiction(self) -> None:
        cage = self.result["cage_comparison"]
        self.assertEqual(
            cage["biregular_girth_8_Moore_lower_bound"]["total"], 130
        )
        self.assertEqual(cage["target_incidence_order"]["total"], 330)
        self.assertFalse(cage["contradiction"])

    def test_status_boundary(self) -> None:
        self.assertEqual(self.result["claim_label"], "DERIVED")
        self.assertFalse(self.result["status"]["endpoint_excluded"])
        self.assertEqual(self.result["status"]["conway_99"], "UNKNOWN")
        self.assertTrue(self.result["resources"]["floor_passed"])


if __name__ == "__main__":
    unittest.main()
