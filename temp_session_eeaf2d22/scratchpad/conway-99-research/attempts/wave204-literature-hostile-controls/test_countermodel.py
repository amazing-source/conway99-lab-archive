"""Focused exact tests for the Wave 204 hostile b=0 skeleton."""

from __future__ import annotations

import itertools
import unittest
from collections import Counter, defaultdict

from .build_countermodel import (
    BASELINE_PAIRS,
    HM_FAMILY,
    N,
    build_certificate,
    complement_neighbors,
    graph_neighbors,
)


class Wave204CountermodelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = build_certificate()
        cls.summary = cls.certificate["summary"]

    def test_scope_is_fail_closed(self) -> None:
        scope = self.certificate["scope"]
        self.assertTrue(scope["is_99_center_global_skeleton"])
        self.assertTrue(scope["is_wave203_slot_certificate"])
        self.assertFalse(scope["is_strongly_regular_graph"])
        self.assertFalse(scope["is_ternary_column_realization"])
        self.assertFalse(scope["is_rank_11_code"])
        self.assertFalse(scope["is_endpoint_existence_evidence"])

    def test_circulant_degree_and_complement(self) -> None:
        for center in range(N):
            self.assertEqual(len(graph_neighbors(center)), 14)
            self.assertEqual(len(complement_neighbors(center)), 84)
            self.assertFalse(set(graph_neighbors(center)) & set(complement_neighbors(center)))
        self.assertEqual(
            self.summary["graph"]["common_neighbor_count_profiles_from_vertex_0"],
            {
                "adjacent": {
                    "6": 2,
                    "7": 2,
                    "8": 2,
                    "9": 2,
                    "10": 2,
                    "11": 2,
                    "12": 2,
                },
                "nonadjacent": {
                    "0": 70,
                    "1": 2,
                    "2": 2,
                    "3": 2,
                    "4": 2,
                    "5": 2,
                    "6": 2,
                    "7": 2,
                },
            },
        )

    def test_hilton_milner_family(self) -> None:
        family = [set(triple) for triple in HM_FAMILY]
        self.assertEqual(len(family), 13)
        self.assertTrue(all(left & right for left, right in itertools.combinations(family, 2)))
        self.assertFalse(set.intersection(*family))
        degrees: Counter[tuple[int, int]] = Counter()
        for triple in family:
            for pair in itertools.combinations(sorted(triple), 2):
                degrees[pair] += 1
        self.assertEqual(
            sorted(pair for pair, degree in degrees.items() if degree == 5),
            list(BASELINE_PAIRS),
        )
        self.assertLessEqual(max(degree for pair, degree in degrees.items() if pair not in BASELINE_PAIRS), 4)

    def test_pair_fibers_partition_complement(self) -> None:
        for center_data in self.certificate["centers"]:
            center = center_data["center"]
            fibers = center_data["pair_fibers"]
            self.assertEqual(len(fibers), 21)
            self.assertTrue(all(len(fiber["targets"]) == 4 for fiber in fibers))
            targets = [target for fiber in fibers for target in fiber["targets"]]
            self.assertEqual(sorted(targets), list(complement_neighbors(center)))

    def test_slots_are_true_third_blocks_and_injective(self) -> None:
        full_labels: dict[tuple[int, int], list[int]] = defaultdict(list)
        for center_data in self.certificate["centers"]:
            center = center_data["center"]
            for flag in center_data["flags"]:
                A = set(flag["A"])
                for leaf in flag["leaves"]:
                    pair = set(leaf["pair"])
                    self.assertEqual(len(pair), 2)
                    self.assertTrue(pair < A)
                    self.assertEqual(A - pair, {leaf["wave203_slot"]})
                    full_labels[(center, leaf["target"])].append(leaf["wave203_slot"])
        for slots in full_labels.values():
            self.assertEqual(len(slots), len(set(slots)))
            self.assertLessEqual(len(slots), 5)

    def test_selected_exact_counts(self) -> None:
        selected = self.summary["selected_pool"]
        self.assertEqual(selected["n3_flags"], 1200)
        self.assertEqual(selected["selected_incidence_3n3"], 3600)
        self.assertEqual(selected["directed_label_union"], 3360)
        self.assertEqual(selected["private_p3"], 3123)
        self.assertEqual(selected["nonprivate_q"], 237)
        self.assertEqual(selected["multiplicity_profile"], {"1": 3123, "2": 234, "3": 3})
        self.assertEqual(selected["nonprivate_tail_count_profile"], {"0": 20, "3": 79})

    def test_wave201_and_wave203_equalities(self) -> None:
        full = self.summary["full_pool"]
        selected = self.summary["selected_pool"]
        self.assertEqual(full["flags"], 1287)
        self.assertEqual(full["directed_label_union_J"], 3561)
        self.assertEqual(full["delta_3564_minus_J"], 3)
        self.assertEqual(selected["epsilon"], 708)
        self.assertEqual(selected["wave201_L_delta_minus_3q_plus_epsilon"], 0)
        self.assertEqual(selected["capacity_slack"], 708)
        self.assertEqual(full["max_combined_two_orientation_multiplicity"], 3)

    def test_no_reverse_occupancy(self) -> None:
        full_directed: set[tuple[int, int]] = set()
        selected_directed: set[tuple[int, int]] = set()
        for center_data in self.certificate["centers"]:
            center = center_data["center"]
            for flag in center_data["flags"]:
                for leaf in flag["leaves"]:
                    key = (center, leaf["target"])
                    full_directed.add(key)
                    if flag["selected"]:
                        selected_directed.add(key)
        self.assertTrue(all((target, source) not in full_directed for source, target in full_directed))
        self.assertTrue(all((target, source) not in selected_directed for source, target in selected_directed))
        self.assertEqual(self.summary["full_pool"]["bidirectional_labels"], 0)
        self.assertEqual(self.summary["selected_pool"]["b_bidirectional_nonprivate"], 0)


if __name__ == "__main__":
    unittest.main()
