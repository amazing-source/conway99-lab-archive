from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from collections import Counter
from itertools import combinations
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave56_percolation", HERE / "percolation_closure.py"
)
assert SPEC and SPEC.loader
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class SourceAndResourceTests(unittest.TestCase):
    def test_primary_source_metadata(self):
        metadata = json.loads(
            (HERE / "source-metadata.json").read_text(encoding="utf-8")
        )
        self.assertEqual(metadata["publication"]["volume"], "93")
        self.assertEqual(metadata["publication"]["year"], 2025)
        self.assertEqual(
            {record["result"] for record in metadata["relevant_results"]},
            {"Theorem 4.8", "Lemma 4.9", "Theorem 4.19"},
        )
        self.assertTrue(metadata["primary_url"].endswith("ajc_v93_p060.pdf"))

    def test_memory_floor(self):
        self.assertGreaterEqual(
            CHECK.free_memory_percent(), CHECK.MIN_FREE_MEMORY_PERCENT
        )


class TipRelationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = CHECK.tip_graph_records()

    def test_all_64_labeled_tip_graphs_are_considered(self):
        all_bits = set(range(64))
        accepted = {record["bits"] for record in self.records}
        rejected = all_bits - accepted
        self.assertEqual(accepted, {0, 2, 16, 18})
        self.assertEqual(len(rejected), 60)

    def test_exact_four_admissible_tip_graphs(self):
        self.assertEqual(len(self.records), 4)
        self.assertEqual(
            [record["opposite_tip_edge_count"] for record in self.records],
            [0, 1, 1, 2],
        )

    def test_endpoint_has_unique_empty_tip_graph(self):
        endpoint = [
            record
            for record in self.records
            if record["prism_free_endpoint_admissible"]
        ]
        self.assertEqual(len(endpoint), 1)
        self.assertEqual(endpoint[0]["bits"], 0)
        self.assertEqual(endpoint[0]["tip_edges"], [])

    def test_each_opposite_tip_edge_is_one_prism_channel(self):
        for record in self.records:
            self.assertEqual(
                len(record["internal_prisms"]),
                record["opposite_tip_edge_count"],
            )
            self.assertEqual(
                record["central_n3_channels"]
                + record["central_prism_channels"],
                2,
            )

    def test_hostile_adjacent_tip_edge_violates_lambda_cap(self):
        edges = CHECK.base_edges()
        edges.add(CHECK.edge(4, 5))
        self.assertFalse(CHECK.local_pair_caps_pass(edges))
        self.assertEqual(
            CHECK.internal_common_neighbors(edges, 1, 4), 2
        )


class NextWaveProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packages = [
            CHECK.tip_profile_package(record)
            for record in CHECK.tip_graph_records()
        ]
        cls.endpoint = next(
            record
            for record in cls.packages
            if record["prism_free_endpoint_admissible"]
        )

    def test_profile_counts_for_all_four_tip_relations(self):
        self.assertEqual(
            {
                record["bits"]: record["next_wave_profile_count"]
                for record in self.packages
            },
            {0: 35, 2: 7, 16: 7, 18: 6},
        )

    def test_profile_size_histograms(self):
        expected = {
            0: {"8": 1, "10": 8, "11": 1, "12": 16, "14": 8, "16": 1},
            2: {"6": 1, "7": 1, "9": 4, "11": 1},
            16: {"6": 1, "7": 1, "9": 4, "11": 1},
            18: {"1": 1, "4": 4, "6": 1},
        }
        self.assertEqual(
            {
                record["bits"]: record["next_wave_size_histogram"]
                for record in self.packages
            },
            expected,
        )

    def test_endpoint_mask_and_profile_counts(self):
        self.assertEqual(self.endpoint["allowed_outside_mask_count"], 23)
        self.assertEqual(
            self.endpoint["allowed_outside_mask_arity_histogram"],
            {"2": 14, "3": 8, "4": 1},
        )
        self.assertEqual(self.endpoint["next_wave_profile_count"], 35)

    def test_endpoint_exact_arity_triples(self):
        self.assertEqual(
            self.endpoint["next_wave_arity_triple_histogram"],
            {
                "4,4,0": 1,
                "7,3,0": 8,
                "10,2,0": 16,
                "13,1,0": 8,
                "16,0,0": 1,
                "10,0,1": 1,
            },
        )

    def test_every_endpoint_profile_exactly_covers_deficits(self):
        edges = CHECK.base_edges()
        deficits = CHECK.pair_deficits(edges)
        for profile in self.endpoint["next_wave_profiles"]:
            with self.subTest(profile=profile):
                covered = [0] * len(CHECK.PAIRS)
                for entry in profile["multiplicities"]:
                    mask = entry["mask"]
                    for pair_index, pair in enumerate(CHECK.PAIRS):
                        if all((mask >> vertex) & 1 for vertex in pair):
                            covered[pair_index] += entry["count"]
                self.assertEqual(tuple(covered), deficits)
                arities = profile["arity_counts"]
                self.assertEqual(
                    int(arities["2"])
                    + 3 * int(arities["3"])
                    + 6 * int(arities["4"]),
                    16,
                )

    def test_hostile_profile_mutation_breaks_pair_deficit(self):
        profile = copy.deepcopy(self.endpoint["next_wave_profiles"][0])
        profile["multiplicities"][0]["count"] -= 1
        covered = [0] * len(CHECK.PAIRS)
        for entry in profile["multiplicities"]:
            for pair_index, pair in enumerate(CHECK.PAIRS):
                if all((entry["mask"] >> vertex) & 1 for vertex in pair):
                    covered[pair_index] += entry["count"]
        self.assertNotEqual(tuple(covered), CHECK.pair_deficits(CHECK.base_edges()))

    def test_formal_D4_orbits_retain_all_labeled_profiles(self):
        orbits = self.endpoint["formal_D4_orbits"]
        self.assertEqual(len(orbits), 11)
        self.assertEqual(sum(orbit["labeled_size"] for orbit in orbits), 35)
        self.assertEqual(
            Counter(orbit["labeled_size"] for orbit in orbits),
            Counter({4: 5, 1: 3, 2: 2, 8: 1}),
        )


class ClosureAndGlobalRelationTests(unittest.TestCase):
    def test_closure_parameter_census(self):
        census = CHECK.closure_parameter_census()
        feasible = [
            (record["degree"], record["order"])
            for record in census
            if record["parameter_feasible"]
        ]
        self.assertEqual(feasible, [(2, 3), (4, 9), (14, 99)])

    def test_forced_nine_vertex_graph_has_exact_parameters(self):
        parameters = CHECK.exact_pair_parameters(
            CHECK.forced_nine_vertex_closure(), range(9)
        )
        self.assertEqual(parameters["degree_values"], [4])
        self.assertEqual(parameters["adjacent_common_neighbor_values"], [1])
        self.assertEqual(
            parameters["nonadjacent_common_neighbor_values"], [2]
        )

    def test_rook_graph_control(self):
        _, edges = CHECK.rook_graph_3x3()
        vertices = tuple(range(9))
        self.assertEqual(len(edges), 18)
        self.assertEqual(len(CHECK.induced_prisms(edges, vertices)), 6)
        self.assertEqual(len(CHECK.induced_n3s(edges, vertices)), 0)
        self.assertEqual(CHECK.induced_triangle_count(edges, vertices), 6)

    def test_every_rook_nonedge_closes_all_nine_vertices(self):
        _, edges = CHECK.rook_graph_3x3()
        vertices = tuple(range(9))
        nonedges = [
            pair
            for pair in combinations(vertices, 2)
            if CHECK.edge(*pair) not in edges
        ]
        self.assertEqual(len(nonedges), 18)
        self.assertTrue(
            all(
                len(CHECK.bootstrap_closure(vertices, edges, pair)) == 9
                for pair in nonedges
            )
        )

    def test_global_count_relations_have_no_unproved_equality(self):
        result = CHECK.build_result()
        relations = result["global_exact_relations"]
        self.assertEqual(
            relations["proved_inequalities"],
            [
                "H <= 231",
                "6*H <= P",
                "R <= 3*P = 4158 - n3",
                "S >= n3",
            ],
        )
        self.assertIn("iff every induced triangular prism", relations["equality_condition"])
        self.assertEqual(relations["percolation_number"]["range"], [2, 3])
        self.assertEqual(
            relations["percolation_number"]["m_equals_3_iff"],
            "H=231 (equivalently R=4158)",
        )

    def test_endpoint_status_is_not_promoted(self):
        result = CHECK.build_result()
        self.assertEqual(result["claim_label"], "DERIVED")
        self.assertEqual(result["status"]["conway_99"], "UNKNOWN")
        self.assertFalse(result["status"]["endpoint_excluded"])
        self.assertEqual(
            result["status"]["local_tip_and_profile_census"],
            "DERIVED_PENDING_VERIFIER",
        )

    def test_exact_result_round_trip(self):
        expected = (HERE / "exact-results.json").read_text(encoding="utf-8")
        self.assertEqual(expected, CHECK.canonical_json(CHECK.build_result()))


if __name__ == "__main__":
    unittest.main()
