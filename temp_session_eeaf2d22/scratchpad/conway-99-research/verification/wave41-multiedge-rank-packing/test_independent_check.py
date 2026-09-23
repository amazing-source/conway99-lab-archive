from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent


def load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {filename}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ind = load("wave41_independent_tests", "independent_check.py")
comparison = load("wave41_comparison_tests", "comparison_check.py")


class Wave41MultiedgeIndependentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = json.loads(
            (HERE / "independent-results.json").read_text(encoding="utf-8")
        )
        cls.comparison = json.loads(
            (HERE / "discovery-comparison.json").read_text(encoding="utf-8")
        )

    def test_frozen_inputs(self) -> None:
        self.assertEqual(ind.check_frozen_inputs(), ind.FROZEN_INPUTS)

    def test_all_labelled_matchings_are_unique_and_complete(self) -> None:
        matchings = list(ind.all_matchings())
        self.assertEqual(len(matchings), 10_395)
        self.assertEqual(len(set(matchings)), 10_395)
        for matching in (matchings[0], matchings[-1]):
            ind.audit_matching(matching)

    def test_all_four_odd_types_and_only_those_types(self) -> None:
        self.assertEqual(
            set(self.result["type_results"]),
            {"1^6", "1^3+3", "1+5", "3+3"},
        )
        self.assertTrue(
            all(
                all(part % 2 for part in record["partition"])
                for record in self.result["type_results"].values()
            )
        )

    def test_exact_diagonal_matching_numbers(self) -> None:
        expected = {"1^6": 0, "1^3+3": 6, "1+5": 10, "3+3": 12}
        self.assertEqual(
            {
                label: record["zero_diagonal_matching_number"]
                for label, record in self.result["type_results"].items()
            },
            expected,
        )

    def test_konig_certificates_cover_every_zero_edge(self) -> None:
        for label, parts in ind.ALL_ODD_TYPES.items():
            s = ind.local_s(parts)
            edges = []
            for i in range(12):
                for j in range(12):
                    u = ind.border_column(i, j)
                    if ind.dot(u, ind.solve_consistent(s, u)) == 0:
                        edges.append((i, j))
            size, witness, cover = ind.maximum_bipartite_matching(edges)
            self.assertEqual(
                size, self.result["type_results"][label]["zero_diagonal_matching_number"]
            )
            self.assertEqual(size, len(witness))
            self.assertEqual(
                size, len(cover["left_vertices"]) + len(cover["right_vertices"])
            )
            self.assertTrue(
                all(
                    i in cover["left_vertices"] or j in cover["right_vertices"]
                    for i, j in edges
                )
            )

    def test_three_plus_three_unique_candidate_is_not_a_Z_matching(self) -> None:
        record = self.result["type_results"]["3+3"]
        self.assertEqual(record["rank_25_candidate_permutations"], 1)
        candidate = record["rank_25_candidate_records"][0]
        self.assertFalse(candidate["target_decodes_as_internal_perfect_matching"])
        self.assertTrue(set(candidate["target_values"]) - {0, 1, 6})

    def test_all_dense_sample_censuses_have_10395_matchings(self) -> None:
        for record in self.result["type_results"].values():
            self.assertEqual(
                sum(record["identity_permutation_full_Z_rank_distribution"].values()),
                10_395,
            )
            self.assertGreaterEqual(
                min(
                    int(value)
                    for value in record[
                        "identity_permutation_full_Z_rank_distribution"
                    ]
                ),
                26,
            )

    def test_direct_schur_and_core_identity_crosschecks(self) -> None:
        for record in self.result["type_results"].values():
            self.assertEqual(record["K39_identity_crosschecks"], 3)
            for witness in record["sample_exact_identity_crosschecks"]:
                self.assertEqual(
                    witness["rank_F7_K39"],
                    25 + witness["residual_rank"],
                )
                self.assertEqual(
                    witness["rank_F7_K39"],
                    1 + witness["rank_F7_3I_minus_A_core"],
                )

    def test_compact_kernel_has_dimension_three(self) -> None:
        basis = ind.compact_kernel_vectors()
        self.assertEqual(ind.rank(basis), 3)
        graph = ind.complete_graph(
            ind.ALL_ODD_TYPES["3+3"],
            tuple(range(12)),
            ind.standard_matching(),
        )
        block = ind.transported_block(graph)
        self.assertTrue(
            all(not any(ind.dot(row, vector) for row in block) for vector in basis)
        )

    def test_rank_28_positive_control_replayed(self) -> None:
        record = self.comparison["low_rank_controls_replayed"]["rank_28_generic"]
        self.assertEqual(record["rank_F7_K39"], 28)
        self.assertEqual(record["rank_F7_3I_minus_A_core"], 27)

    def test_rank_29_triangle_free_positive_control_replayed(self) -> None:
        record = self.comparison["low_rank_controls_replayed"][
            "rank_29_triangle_free"
        ]
        self.assertEqual(record["rank_F7_K39"], 29)
        self.assertEqual(record["rank_F7_3I_minus_A_core"], 28)
        self.assertEqual(record["core_triangle_count"], 0)

    def test_rank_transport_field_arithmetic(self) -> None:
        record = self.result["rank_transport"]
        self.assertEqual(record["inverse_of_3"], 5)
        self.assertEqual(3 * record["inverse_of_3"] % 7, 1)
        self.assertEqual(record["conclusion"], "rank_F7(N M N^T)=rank_F7(M)")

    def test_hostile_universal_floor_inflation_is_rejected(self) -> None:
        hostile = copy.deepcopy(self.result)
        hostile["deduction"]["universal_rank_F7_M_lower_bound"] = 26
        with self.assertRaises(ValueError):
            ind.validate(hostile)

    def test_hostile_even_type_promotion_is_rejected(self) -> None:
        hostile = copy.deepcopy(self.result)
        first = next(iter(hostile["status_wall"]["seven_even_part_types"]))
        hostile["status_wall"]["seven_even_part_types"][first] = "VERIFIED"
        with self.assertRaises(ValueError):
            ind.validate(hostile)

    def test_hostile_matching_and_permutation_inputs_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            ind.audit_matching(((0, 1),) * 6)
        with self.assertRaises(ValueError):
            ind.complete_graph(
                ind.ALL_ODD_TYPES["1^6"],
                (0,) * 12,
                ind.standard_matching(),
            )

    def test_discovery_five_type_count_is_explicitly_refuted(self) -> None:
        self.assertEqual(
            self.comparison["verdict"]["discovery_five_even_part_count"],
            "REFUTED",
        )
        self.assertEqual(
            self.comparison["verdict"]["seven_even_part_types"], "UNKNOWN"
        )
        self.assertEqual(len(self.comparison["discrepancies"]), 1)


if __name__ == "__main__":
    unittest.main()
