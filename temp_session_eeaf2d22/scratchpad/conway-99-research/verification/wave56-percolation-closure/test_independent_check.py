from __future__ import annotations

import unittest

import independent_check as check


class IndependentWave56Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tip = check.rooted_tip_census()
        cls.endpoint = check.endpoint_census()
        cls.controls = check.control_graph_census()
        cls.parameters = check.target_parameter_census()
        cls.incidence = check.incidence_arithmetic()

    def test_target_arithmetic(self) -> None:
        self.assertEqual(
            self.incidence["target"],
            {
                "v": 99,
                "k": 14,
                "lambda": 1,
                "mu": 2,
                "edges": 693,
                "nonedges": 4158,
                "triangles": 231,
            },
        )

    def test_parameter_census(self) -> None:
        self.assertEqual(self.parameters["feasible_degrees"], [2, 4, 14])

    def test_all_tip_graphs_are_visited(self) -> None:
        self.assertEqual(self.tip["all_count"], 64)

    def test_four_tip_graphs_pass_caps(self) -> None:
        self.assertEqual(self.tip["valid_count"], 4)

    def test_valid_tip_channel_pairs(self) -> None:
        self.assertCountEqual(
            self.tip["valid_channel_pairs"],
            [[2, 0], [1, 1], [1, 1], [0, 2]],
        )

    def test_only_one_prism_free_tip_graph(self) -> None:
        self.assertEqual(self.tip["prism_free_count"], 1)
        self.assertEqual(self.tip["prism_free_masks"], [0])

    def test_endpoint_pair_deficits(self) -> None:
        self.assertEqual(
            self.endpoint["pair_deficit_histogram"],
            {"0": 14, "1": 12, "2": 2},
        )
        self.assertEqual(self.endpoint["pair_deficit_sum"], 16)

    def test_endpoint_masks(self) -> None:
        self.assertEqual(self.endpoint["allowed_mask_count"], 23)
        self.assertEqual(
            self.endpoint["allowed_mask_size_histogram"],
            {"2": 14, "3": 8, "4": 1},
        )

    def test_endpoint_profile_count(self) -> None:
        self.assertEqual(self.endpoint["profile_count"], 35)

    def test_endpoint_arity_histogram(self) -> None:
        self.assertEqual(
            self.endpoint["arity_triple_histogram"],
            {
                "10,0,1": 1,
                "10,2,0": 16,
                "13,1,0": 8,
                "16,0,0": 1,
                "4,4,0": 1,
                "7,3,0": 8,
            },
        )

    def test_endpoint_wave_histogram(self) -> None:
        self.assertEqual(
            self.endpoint["wave_size_histogram"],
            {"8": 1, "10": 8, "11": 1, "12": 16, "14": 8, "16": 1},
        )

    def test_pair_deficit_equation(self) -> None:
        self.assertEqual(self.endpoint["equation_failure_count"], 0)

    def test_profile_level_visible_caps(self) -> None:
        self.assertEqual(self.endpoint["new_pair_visible_cap_failure_count"], 0)
        self.assertEqual(self.endpoint["base_degree_cap_failure_count"], 0)

    def test_formal_d4_only(self) -> None:
        self.assertEqual(self.endpoint["formal_d4_group_order"], 8)
        self.assertEqual(self.endpoint["formal_d4_orbit_count"], 11)
        self.assertFalse(self.endpoint["target_graph_automorphism_assumed"])

    def test_profiles_are_not_completions(self) -> None:
        self.assertFalse(self.endpoint["completability_claimed"])

    def test_n3_central_nonedges(self) -> None:
        self.assertEqual(self.controls["n3_central_channel_nonedges"], 2)
        self.assertEqual(self.controls["n3_internal_percolating_nonedges"], 6)

    def test_prism_central_nonedges(self) -> None:
        self.assertEqual(self.controls["prism_central_channel_nonedges"], 6)
        self.assertEqual(self.controls["prism_internal_percolating_nonedges"], 6)

    def test_rook_parameters(self) -> None:
        rook = self.controls["rook"]
        self.assertEqual(rook["vertices"], 9)
        self.assertEqual(rook["edges"], 18)
        self.assertEqual(rook["nonedges"], 18)
        self.assertEqual(rook["degree_values"], [4])
        self.assertEqual(rook["adjacent_common_neighbor_values"], [1])
        self.assertEqual(rook["nonadjacent_common_neighbor_values"], [2])

    def test_rook_small_graph_census(self) -> None:
        rook = self.controls["rook"]
        self.assertEqual(rook["n3_count"], 0)
        self.assertEqual(rook["prism_count"], 6)
        self.assertEqual(rook["nonedge_closure_size_histogram"], {"9": 18})

    def test_hostile_multiplicity_changes_fail(self) -> None:
        self.assertTrue(all(self.incidence["hostile_factor_rejections"].values()))

    def test_endpoint_implication(self) -> None:
        self.assertEqual(
            self.incidence["endpoint"],
            {
                "n3": 4158,
                "P": 0,
                "H": 0,
                "R": 0,
                "S": 4158,
                "every_nonedge_percolates": True,
            },
        )


if __name__ == "__main__":
    unittest.main()
