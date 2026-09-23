"""Focused tests for the independent Wave 13 n3=45 replay."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parent / "n3-45-equality" / "verify.py"
SPEC = importlib.util.spec_from_file_location("n3_45_audit_verify", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)


class Wave13N345AuditTests(unittest.TestCase):
    def test_exact_nine_profiles(self):
        self.assertEqual(VERIFY.active_profiles(), VERIFY.EXPECTED_PROFILES)

    def test_no_singleton_and_degree_three_filters(self):
        survivors = VERIFY.profiles_after_non_singleton_filter()
        self.assertEqual([profile[0] for profile in survivors], [15, 14, 13])
        closure = VERIFY.degree_three_closure()
        self.assertEqual(
            closure["berge_triangle_intersections"], ["a", "b", "c"]
        )

    def test_flower_bounds(self):
        self.assertEqual(VERIFY.minimum_singleton_petals(14, 4), 6)
        self.assertEqual(VERIFY.minimum_singleton_petals(15, 5), 10)
        self.assertEqual(VERIFY.minimum_singleton_petals(15, 4), 5)
        audit = VERIFY.large_point_flower_audit()
        self.assertGreater(
            audit["r15_size4"]["h5_witness_root_K_degree"],
            audit["r15_size4"]["available_K_degree"],
        )

    def test_mixed_modes_and_distinct_forcing(self):
        modes = VERIFY.mixed_flower_modes()
        self.assertEqual(modes, ((2, 2, 2), (2, 3, 3)))
        for mode in modes:
            forced = VERIFY.explicit_forced_u_sets(mode, (0, 0, 0))
            self.assertEqual(len(forced), 3)
            expected = tuple(
                sum(3 - mode[base] for base in range(3) if base != root)
                for root in range(3)
            )
            self.assertEqual(tuple(len(edge_set) for edge_set in forced), expected)
        local = VERIFY.mixed_profile_local_audit()
        self.assertEqual(
            local["special_size3"]["surviving_other_t_pair_before_second_contradiction"],
            [(3, 3)],
        )
        self.assertGreater(
            local["mode233"]["distinct_actual_neighbour_contribution"],
            local["mode233"]["fixed_point_sum"],
        )

    def test_mixed_small_intersection_census(self):
        census = VERIFY.mixed_intersection_graph_census()
        self.assertEqual(census["order4_labeled_survivors"], 0)
        self.assertEqual(census["order6_labeled_survivors"], 10)
        self.assertEqual(census["order6_open_twin_counts"], [(0, 10)])

    def test_exact_r15_modes(self):
        self.assertEqual(
            VERIFY.canonical_r15_modes(), VERIFY.EXPECTED_R15_MODES
        )

    def test_two_sided_crossings(self):
        self.assertEqual(
            VERIFY.bipartite_crossing_distribution(1, 2), {0: 1}
        )
        self.assertEqual(
            VERIFY.bipartite_crossing_distribution(2, 3), {0: 1, 4: 3}
        )
        self.assertEqual(
            VERIFY.bipartite_crossing_distribution(3, 3),
            {0: 1, 4: 9, 6: 6},
        )

    def test_t3_odd_parity(self):
        self.assertEqual(VERIFY.symmetric_degree_one_graphs_on_three(), ())

    def test_mode111_all_actual_neighbour_classes(self):
        audit = VERIFY.mode111_saturation_audit()
        self.assertEqual(audit["valid_disjoint_crossing_sizes"], [0])
        self.assertEqual(audit["root_K_degree"], 8)
        self.assertEqual(audit["overlapping_petals_checked"], 6)
        self.assertEqual(audit["inactive_crossing_size"], 0)

    def test_final_degree_and_handshake(self):
        audit = VERIFY.final_degree_audit()
        self.assertEqual(audit["surviving_H_degrees"], [0, 4])
        self.assertEqual(audit["H_edges"], 45)
        self.assertEqual(audit["handshake_sum"], 90)
        self.assertEqual(audit["handshake_mod_4"], 2)

    def test_adversarial_mutations_have_witnesses(self):
        mutations = VERIFY.adversarial_mutations()
        self.assertTrue(mutations["reuse_forced_U_neighbours_extra_mixed_modes"])
        self.assertTrue(
            mutations["count_one_U_neighbour_per_empty_crossing_extra_modes"]
        )
        self.assertTrue(
            mutations["drop_fixed_point_full_crossing_limit_extra_modes"]
        )
        self.assertIn(
            2, mutations["one_sided_singleton_crossing_distribution"]
        )
        self.assertEqual(
            sum(mutations["allow_degree_six_handshake_witness"]), 90
        )
        self.assertEqual(mutations["double_count_H_edges_handshake_sum"], 180)

    def test_full_replay(self):
        result = VERIFY.run_all(include_mutations=True)
        self.assertEqual(result["verdict"], "PASS")
        self.assertEqual(result["target_result"], "UNKNOWN")
        self.assertEqual(result["novelty_status"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
