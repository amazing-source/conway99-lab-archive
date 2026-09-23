import copy
import json
import unittest

import independent_check as check


class IndependentJointIncidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = check.load_frozen_input()
        cls.results, cls.certificate = check.build_results()

    def test_reconstructs_canonical_rank_33_block(self):
        reconstruction = self.results["reconstruction"]
        self.assertEqual(reconstruction["rank_F7_3I_minus_A_core"], 32)
        self.assertEqual(reconstruction["rank_F7_K39"], 33)
        self.assertEqual(reconstruction["component_orders"], [12, 24])
        self.assertEqual(reconstruction["component_fibre_balances"], [[4, 4, 4], [8, 8, 8]])

    def test_exact_gram_and_cauchy_equality(self):
        gram = self.results["gram"]
        self.assertEqual(gram["diagonal_set"], [10])
        self.assertEqual(gram["row_sum_set"], [60])
        forced = [
            item["forced_component_vertices_per_column"]
            for item in self.results["component_cauchy"]["components"]
        ]
        self.assertEqual(forced, [2, 4])

    def test_pair_inventory_and_patterns(self):
        inventory = self.results["pair_inventory"]
        self.assertEqual(inventory["allowed_pair_count_per_fibre"], [60, 60, 60])
        self.assertEqual(
            sorted(inventory["forced_column_component_patterns"].values()),
            [4, 4, 4, 16, 16, 16],
        )

    def test_exhaustive_six_set_filters(self):
        self.assertEqual(
            self.results["six_set_census"]["counts"],
            [216000, 118718, 49736, 45032],
        )
        self.assertIsNotNone(
            self.results["six_set_census"]["first_hostile_local_rejection"]
        )

    def test_positive_two_fibre_certificate(self):
        check.verify_two_fibre_payload(self.certificate)
        self.assertEqual(
            len(self.certificate["right_pair_index_for_each_left_pair"]), 60
        )

    def test_hostile_duplicate_pair_assignment_is_rejected(self):
        hostile = copy.deepcopy(self.certificate)
        hostile["right_pair_index_for_each_left_pair"][1] = hostile[
            "right_pair_index_for_each_left_pair"
        ][0]
        with self.assertRaises(ValueError):
            check.verify_two_fibre_payload(hostile)

    def test_hostile_core_edge_mutation_is_rejected(self):
        edges = copy.deepcopy(check.witness_record(self.data)["core_edges"])
        edges.pop()
        with self.assertRaises(ValueError):
            check.reconstruct_core(self.data, edges_override=edges)

    def test_hostile_input_hash_is_rejected(self):
        with self.assertRaises(ValueError):
            check.load_frozen_input(check.HERE / "protocol-freeze.md")

    def test_conditional_overlap_and_H_counts(self):
        counts = self.results["conditional_outside_counts"]
        self.assertEqual(counts["column_pair_overlap_0_1_2"], [458, 1004, 308])
        self.assertEqual(counts["H_edges_by_column_overlap_0_1_2"], [96, 144, 0])
        self.assertEqual(counts["H_triangle_count"], 32)
        self.assertEqual(counts["H_four_cycle_count"], 181)

    def test_scope_wall_blocks_status_inflation(self):
        wall = self.results["status_wall"]
        self.assertEqual(wall["full_60_column_B"], "NOT_CONSTRUCTED_OR_EXCLUDED")
        self.assertFalse(wall["endpoint_excluded"])
        self.assertEqual(wall["graph_or_counterexample"], "NONE")
        self.assertEqual(wall["novelty_or_priority"], "UNKNOWN")

    def test_json_roundtrip_is_stable(self):
        encoded = json.dumps(self.results, sort_keys=True)
        self.assertEqual(json.loads(encoded), self.results)


if __name__ == "__main__":
    unittest.main()
