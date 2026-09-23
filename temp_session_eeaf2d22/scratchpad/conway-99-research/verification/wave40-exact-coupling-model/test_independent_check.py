import copy
import json
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import independent_check as verify  # noqa: E402


class UniversalRank25IndependentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = verify.compute()

    def test_stored_result_replays_exactly(self):
        stored = json.loads((HERE / "independent-results.json").read_text(encoding="utf-8"))
        self.assertEqual(stored, self.result)

    def test_only_frozen_wave39_inputs_are_bound(self):
        self.assertEqual(verify.freeze_inputs(), verify.INPUT_HASHES)
        source = (HERE / "independent_check.py").read_text(encoding="utf-8")
        forbidden = "attempts/" + "wave40-exact-coupling-model"
        self.assertNotIn(forbidden, source)

    def test_all_eleven_partition_values(self):
        expected = {
            "6": (23, 4, 1),
            "5+1": (25, 2, 0),
            "4+2": (21, 6, 2),
            "4+1+1": (23, 4, 1),
            "3+3": (25, 2, 0),
            "3+2+1": (23, 4, 1),
            "3+1+1+1": (25, 2, 0),
            "2+2+2": (19, 8, 3),
            "2+2+1+1": (21, 6, 2),
            "2+1+1+1+1": (23, 4, 1),
            "1+1+1+1+1+1": (25, 2, 0),
        }
        self.assertEqual(set(self.result["partition_results"]), set(expected))
        for name, values in expected.items():
            entry = self.result["partition_results"][name]
            actual = (
                entry["local_rank_F7"],
                entry["kernel_dimension"],
                entry["projection_search"][
                    "minimum_over_all_12_factorial_permutations"
                ],
            )
            self.assertEqual(actual, values)
            self.assertEqual(entry["bordered_principal_rank_lower_bound"], 25)

    def test_wrong_local_cross_matching_is_rejected(self):
        graph = verify.local_graph((4, 2))
        x0, y0, y1 = verify.XV[0], verify.YV[0], verify.YV[1]
        graph[x0][y0] = graph[y0][x0] = 0
        graph[x0][y1] = graph[y1][x0] = 1
        with self.assertRaisesRegex(ValueError, "perfect matching"):
            verify.audit_local_graph(graph, (4, 2))

    def test_all_144_border_signatures_are_present(self):
        for parts in verify.PARTITIONS:
            block = verify.transported_principal_block(verify.local_graph(parts))
            signatures = verify.projected_signatures(verify.nullspace(block))
            self.assertEqual(len(signatures), 144)
            self.assertEqual(set(signatures), set((i, j) for i in range(12) for j in range(12)))
        column = verify.border_column(3, 8)
        self.assertEqual((column[0], column[1], column[2]), (1, 1, 6))
        self.assertEqual(column[verify.XV[3]], 6)
        self.assertEqual(column[verify.YV[8]], 6)

    def test_nonbijective_third_fibre_is_rejected(self):
        good = [(index, index) for index in range(12)]
        duplicate_y = good[:-1] + [(11, 0)]
        duplicate_x = good[:-1] + [(10, 11)]
        self.assertTrue(verify.valid_permutation(good))
        self.assertFalse(verify.valid_permutation(duplicate_y))
        self.assertFalse(verify.valid_permutation(duplicate_x))

    def test_projective_subspaces_include_all_scalars(self):
        block = verify.transported_principal_block(verify.local_graph((2, 2, 2)))
        signatures = verify.projected_signatures(verify.nullspace(block))
        vector = next(value for value in signatures.values() if any(value))
        line = verify.projective_representative(vector)
        for scalar in range(1, 7):
            multiple = tuple((scalar * value) % 7 for value in line)
            self.assertTrue(verify.belongs(multiple, (line,)))

    def test_subspace_search_is_complete_through_the_minimum(self):
        expected_counts = {
            0: [1],
            1: [1, 6],
            2: [1, 28, 290],
            3: [1, 66, 1923, 25744],
        }
        for entry in self.result["partition_results"].values():
            minimum = entry["even_part_count"]
            search = entry["projection_search"]
            self.assertEqual(search["dimensions_exhausted_through"], minimum)
            counts = [
                search["dimension_censuses"][str(dimension)]["subspaces"]
                for dimension in range(minimum + 1)
            ]
            self.assertEqual(counts, expected_counts[minimum])
            for dimension in range(minimum):
                census = search["dimension_censuses"][str(dimension)]
                self.assertEqual(census["subspaces_supporting_a_permutation"], 0)
                self.assertLess(census["maximum_matching_number"], 12)
            winning = search["dimension_censuses"][str(minimum)]
            self.assertGreater(winning["subspaces_supporting_a_permutation"], 0)
            self.assertEqual(winning["maximum_matching_number"], 12)

    def test_arbitrary_W_border_rank_lemma(self):
        block = verify.transported_principal_block(verify.local_graph((2, 2, 2)))
        witness = self.result["partition_results"]["2+2+2"]["projection_search"][
            "canonical_witness"
        ]["permutation"]
        permutation = [tuple(edge) for edge in witness]
        columns = [verify.border_column(*edge) for edge in permutation]
        border = [[columns[column][row] for column in range(12)] for row in range(27)]
        rank_s, projected_rank = verify.border_lemma_terms(block, border)
        self.assertEqual((rank_s, projected_rank), (19, 3))
        candidates = [
            [[0] * 12 for _ in range(12)],
            [[int(i == j) for j in range(12)] for i in range(12)],
            [[(3 * i + 5 * j + i * j) % 7 for j in range(12)] for i in range(12)],
        ]
        for arbitrary_w in candidates:
            full = verify.block_matrix(block, border, arbitrary_w)
            self.assertGreaterEqual(
                verify.matrix_rank(full), rank_s + 2 * projected_rank
            )
        self.assertEqual(
            self.result["border_rank_lemma"]["W_restrictions_used"], "none"
        )

    def test_small_tight_border_lemma_example(self):
        s = [[1, 0], [0, 0]]
        u = [[2], [1]]
        w = [[4]]
        rank_s, projected_rank = verify.border_lemma_terms(s, u)
        full_rank = verify.matrix_rank(verify.block_matrix(s, u, w))
        self.assertEqual((rank_s, projected_rank, full_rank), (1, 1, 3))

    def test_omitted_partition_is_rejected(self):
        mutated = copy.deepcopy(self.result)
        del mutated["partition_results"]["6"]
        with self.assertRaisesRegex(ValueError, "eleven partitions"):
            verify.validate(mutated)

    def test_false_projection_minimum_is_rejected(self):
        mutated = copy.deepcopy(self.result)
        mutated["partition_results"]["2+2+2"]["projection_search"][
            "minimum_over_all_12_factorial_permutations"
        ] = 2
        with self.assertRaisesRegex(ValueError, "minimum projection"):
            verify.validate(mutated)

    def test_omitted_two_space_is_rejected(self):
        mutated = copy.deepcopy(self.result)
        census = mutated["partition_results"]["2+2+2"]["projection_search"][
            "dimension_censuses"
        ]["2"]
        census["subspaces"] = 1922
        with self.assertRaisesRegex(ValueError, "dimension-2 coverage"):
            verify.validate(mutated)

    def test_nonpermutation_witness_is_rejected(self):
        mutated = copy.deepcopy(self.result)
        witness = mutated["partition_results"]["4+2"]["projection_search"][
            "canonical_witness"
        ]["permutation"]
        witness[-1][1] = witness[0][1]
        with self.assertRaisesRegex(ValueError, "non-bijective witness"):
            verify.validate(mutated)

    def test_universal_deduction_and_endpoint_arithmetic(self):
        self.assertEqual(
            self.result["universal_deduction"]["minimum_bordered_principal_rank"], 25
        )
        self.assertEqual(self.result["universal_deduction"]["all_partition_lower_bounds"], [25])
        self.assertEqual(verify.endpoint_rank_pair_count(), 330)
        self.assertEqual(self.result["endpoint_arithmetic"]["remaining_rank_pairs"], 330)
        self.assertEqual(
            self.result["endpoint_arithmetic"]["if_r3_equals_12"],
            "r7 is even and at least 26",
        )

    def test_status_inflation_is_rejected(self):
        for field, value, message in (
            ("endpoint_excluded", True, "endpoint status inflation"),
            (
                "general_upper_bound_improved_below_4158",
                True,
                "general-bound status inflation",
            ),
            ("conway_99_status", "SOLVED", "problem-status inflation"),
            ("literature_novelty", "NOVEL", "novelty inflation"),
            ("construction_produced", True, "construction status inflation"),
        ):
            mutated = copy.deepcopy(self.result)
            mutated["status_wall"][field] = value
            with self.assertRaisesRegex(ValueError, message):
                verify.validate(mutated)


if __name__ == "__main__":
    unittest.main()
