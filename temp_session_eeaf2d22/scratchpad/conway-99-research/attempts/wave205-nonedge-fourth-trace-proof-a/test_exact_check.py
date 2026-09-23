from __future__ import annotations

import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave205_nonedge_exact_check", HERE / "exact_check.py"
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to load checker")
CHECK = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CHECK
SPEC.loader.exec_module(CHECK)
RESULT = CHECK.analyze()


class NonedgeFourthTraceTests(unittest.TestCase):
    def test_frozen_inputs(self) -> None:
        self.assertEqual(RESULT["inputs"], CHECK.EXPECTED_INPUTS)

    def test_exact_geometry_corner_and_profiles(self) -> None:
        geometry = RESULT["derived_nonedge_geometry"]
        self.assertEqual(
            geometry["distinguished_cross_gram_corner"], [[1, 2], [2, 1]]
        )
        self.assertEqual(
            geometry["each_special_row_and_column_profile"],
            {"zeros": 0, "ones": 5, "twos": 2},
        )

    def test_all_field_values_realized(self) -> None:
        self.assertEqual(
            [
                (
                    control["claimed_and_recomputed_t"],
                    control["claimed_and_recomputed_h"],
                )
                for control in RESULT["controls"]
            ],
            [(6, 1), (7, 0), (7, 1), (7, 2)],
        )

    def test_complete_low_t_census(self) -> None:
        census = RESULT["complete_normalized_low_t_census"]
        self.assertEqual(census["6"]["normalized_matrix_count"], 646)
        self.assertEqual(census["7"]["normalized_matrix_count"], 7886)
        self.assertEqual(
            census["6"]["rank11_nonsquare_true_distance_at_least_4_by_h"],
            {"0": 0, "1": 18, "2": 0},
        )
        self.assertEqual(
            census["7"]["rank11_nonsquare_true_distance_at_least_4_by_h"],
            {"0": 297, "1": 324, "2": 144},
        )

    def test_local_graph_certificates(self) -> None:
        for control in RESULT["controls"]:
            local = control["local_graph"]
            self.assertEqual(local["vertex_count"], 28)
            self.assertEqual(local["center_degrees"], {"x": 14, "y": 14})
            self.assertEqual(local["center_common_neighbors"], ["a", "b"])
            self.assertTrue(
                local["all_edges_have_at_most_one_local_common_neighbor"]
            )
            self.assertTrue(
                local["all_nonedges_have_at_most_two_local_common_neighbors"]
            )
            self.assertTrue(
                local["opposite_center_mu_two_for_all_exclusive_neighbors"]
            )
            self.assertTrue(
                local["endpoint_cross_edge_cap_on_selected_disjoint_blocks"]
            )
            self.assertTrue(
                local["full_local_B_transpose_A_B_reproduces_two_star_gram"]
            )

    def test_two_star_gram_and_embedding(self) -> None:
        for control in RESULT["controls"]:
            gram = control["two_star_gram"]
            self.assertEqual(gram["rank"], 11)
            self.assertEqual(gram["kernel_nullity"], 3)
            self.assertGreaterEqual(gram["kernel_minimum_nonzero_weight"], 4)
            self.assertEqual(gram["local_projective_direction_count"], 14)
            self.assertTrue(
                gram["kernel_is_true_relation_code_because_rank_is_11"]
            )
            self.assertEqual(
                gram["embedding"]["principal_determinant"], 2
            )
            self.assertEqual(
                gram["embedding"]["ambient_form_diagonal"], [1] * 10 + [2]
            )

    def test_projector_reconstruction(self) -> None:
        for control in RESULT["controls"]:
            projectors = control["projectors"]
            self.assertEqual(projectors["ambient_dimension"], 11)
            self.assertEqual(projectors["each_rank"], 6)
            self.assertEqual(projectors["each_trace"], 0)
            self.assertTrue(projectors["each_idempotent"])
            self.assertTrue(projectors["each_self_adjoint"])
            self.assertEqual(
                projectors["fourth_trace"],
                control["claimed_and_recomputed_h"],
            )

    def test_strong_h0_h2_separation(self) -> None:
        separation = RESULT["strong_separation"]
        self.assertEqual(separation["same_two_entry_count"], 7)
        self.assertEqual(separation["same_pair_trace"], 2)
        self.assertEqual(separation["same_intersection_dimension"], 1)
        self.assertEqual(separation["same_full_gram_rank"], 11)
        self.assertEqual(separation["different_fourth_traces"], [0, 1, 2])

    def test_t6_refutes_local_lower_bound(self) -> None:
        control = RESULT["controls"][0]
        self.assertEqual(control["name"], "t6_h1")
        self.assertEqual(control["claimed_and_recomputed_t"], 6)
        self.assertEqual(
            control["two_star_gram"]["kernel_minimum_nonzero_weight"], 6
        )
        self.assertFalse(RESULT["conclusions"]["t_at_least_7_from_local_projectivity"])

    def test_cross_edge_mutation_rejected(self) -> None:
        controls = json.loads((HERE / "controls.json").read_text(encoding="utf-8"))
        bad = copy.deepcopy(controls["controls"][0])
        bad["exclusive_cross_edges"][0] = ["alpha", "y21"]
        with self.assertRaises(AssertionError):
            CHECK.analyze_control(controls["vertex_convention"], bad)

    def test_cross_gram_mutation_rejected(self) -> None:
        controls = json.loads((HERE / "controls.json").read_text(encoding="utf-8"))
        bad = copy.deepcopy(controls["controls"][2])
        bad["cross_gram_rows"][3] = "1100122"
        with self.assertRaises(AssertionError):
            CHECK.analyze_control(controls["vertex_convention"], bad)

    def test_h_mutation_rejected(self) -> None:
        controls = json.loads((HERE / "controls.json").read_text(encoding="utf-8"))
        bad = copy.deepcopy(controls["controls"][3])
        bad["claimed_h"] = 1
        with self.assertRaises(AssertionError):
            CHECK.analyze_control(controls["vertex_convention"], bad)

    def test_status_wall(self) -> None:
        conclusions = RESULT["conclusions"]
        self.assertFalse(conclusions["actual_endpoint_nonedge_h_classified"])
        self.assertFalse(conclusions["rank_11_endpoint_excluded"])
        self.assertEqual(conclusions["conway_99_status"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
