from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).with_name("exact_check.py")
SPEC = importlib.util.spec_from_file_location("wave39_edge_local_rank", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class EdgeLocalRankTests(unittest.TestCase):
    def test_all_partitions_of_six_are_present(self) -> None:
        partitions = list(MODULE.integer_partitions(6))
        self.assertEqual(len(partitions), 11)
        self.assertEqual(partitions[0], (1, 1, 1, 1, 1, 1))
        self.assertEqual(partitions[-1], (6,))

    def test_every_normal_form_has_forced_local_degrees(self) -> None:
        for partition in MODULE.integer_partitions(6):
            adjacency = MODULE.canonical_edge_local_graph(partition)
            axioms = MODULE.local_axioms(adjacency)
            self.assertEqual(axioms["vertex_count"], 27)
            self.assertEqual(axioms["edge_count"], 51)
            self.assertEqual(axioms["degree_sequence"], [2] + [3] * 24 + [14, 14])
            self.assertEqual(
                axioms["cycle_component_sizes"],
                sorted(4 * part for part in partition),
            )

    def test_rank_formula_matches_exact_elimination(self) -> None:
        for partition in MODULE.integer_partitions(6):
            adjacency = MODULE.canonical_edge_local_graph(partition)
            block = MODULE.incidence_transport_block(adjacency)
            self.assertEqual(
                MODULE.rank_mod_prime(block, 7),
                MODULE.rank_formula(partition),
            )

    def test_universal_rank_floor_is_nineteen(self) -> None:
        ranks = []
        for partition in MODULE.integer_partitions(6):
            block = MODULE.incidence_transport_block(
                MODULE.canonical_edge_local_graph(partition)
            )
            ranks.append(MODULE.rank_mod_prime(block, 7))
        self.assertEqual(min(ranks), 19)
        self.assertLessEqual(max(ranks), 25)

    def test_prism_free_normal_forms_are_exact(self) -> None:
        forms = [
            list(partition)
            for partition in MODULE.integer_partitions(6)
            if 1 not in partition
        ]
        self.assertEqual(forms, [[2, 2, 2], [2, 4], [3, 3], [6]])

    def test_endpoint_rank_table(self) -> None:
        expected = {
            (2, 2, 2): 19,
            (2, 4): 21,
            (3, 3): 25,
            (6,): 23,
        }
        for partition, wanted in expected.items():
            block = MODULE.incidence_transport_block(
                MODULE.canonical_edge_local_graph(partition)
            )
            self.assertEqual(MODULE.rank_mod_prime(block, 7), wanted)

    def test_updated_arithmetic_survivor_count(self) -> None:
        pairs = MODULE.admissible_endpoint_pairs()
        self.assertEqual(len(pairs), 429)
        self.assertEqual(
            [r7 for r3, r7 in pairs if r3 == 12],
            list(range(20, 45, 2)),
        )

    def test_status_wall_is_conservative(self) -> None:
        record = MODULE.exact_record()
        self.assertEqual(record["claim_label"], "CANDIDATE")
        self.assertFalse(record["endpoint_result"]["endpoint_excluded"])
        self.assertFalse(
            record["endpoint_result"]["upper_bound_improved_below_4158"]
        )
        self.assertEqual(record["target_status"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
