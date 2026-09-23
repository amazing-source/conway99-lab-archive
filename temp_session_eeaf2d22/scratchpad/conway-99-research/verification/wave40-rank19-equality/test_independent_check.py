import copy
import json
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import independent_check as check  # noqa: E402


class IndependentRank22VerifierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results = check.compute_results()

    def test_stored_result_is_exact_fresh_replay(self):
        stored = json.loads((HERE / "independent-results.json").read_text(encoding="utf-8"))
        self.assertEqual(stored, self.results)

    def test_frozen_inputs_are_bound(self):
        self.assertEqual(check.check_frozen_inputs(), check.FROZEN_INPUTS)

    def test_two_needed_local_blocks_are_reconstructed(self):
        block_222 = self.results["local_blocks"]["2+2+2"]
        block_24 = self.results["local_blocks"]["2+4"]
        self.assertEqual((block_222["rank_F7"], block_222["nullity_F7"]), (19, 8))
        self.assertEqual((block_24["rank_F7"], block_24["nullity_F7"]), (21, 6))
        self.assertEqual(block_222["cycle_component_lengths"], [8, 8, 8])
        self.assertEqual(block_24["cycle_component_lengths"], [8, 16])

    def test_wrong_cross_matching_is_rejected(self):
        adjacency = check.construct_local_adjacency((2, 2, 2))
        x0, y0, y1 = check.X_VERTICES[0], check.Y_VERTICES[0], check.Y_VERTICES[1]
        adjacency[x0][y0] = adjacency[y0][x0] = 0
        adjacency[x0][y1] = adjacency[y1][x0] = 1
        with self.assertRaisesRegex(ValueError, "X--Y relation"):
            check.validate_local_geometry(adjacency, (2, 2, 2))

    def test_z_patterns_are_complete_affine_columns(self):
        block = check.transported_block(check.construct_local_adjacency((2, 2, 2)))
        patterns = check.z_patterns(check.kernel_basis(block))
        self.assertEqual(len(patterns), 144)
        self.assertEqual(len({tuple(pattern["edge"]) for pattern in patterns}), 144)
        column = check.restricted_z_column(4, 7)
        self.assertEqual((column[0], column[1], column[2]), (1, 1, 6))
        self.assertEqual(column[check.X_VERTICES[4]], 6)
        self.assertEqual(column[check.Y_VERTICES[7]], 6)

    def test_nonbijective_z_neighbor_witness_is_rejected(self):
        valid = [(index, index) for index in range(12)]
        invalid = valid[:-1] + [(11, 0)]
        self.assertTrue(check.is_perfect_pattern_matching(valid))
        self.assertFalse(check.is_perfect_pattern_matching(invalid))

    def test_all_nonzero_projective_scalars_are_included(self):
        block = check.transported_block(check.construct_local_adjacency((2, 2, 2)))
        kernel = check.kernel_basis(block)
        vector = check.z_patterns(kernel)[0]["syndrome"]
        line = check.normalize_line(vector)
        for scalar in range(1, 7):
            multiple = tuple((scalar * entry) % 7 for entry in line)
            self.assertTrue(check.in_row_space(multiple, (line,)))
        mutated = copy.deepcopy(self.results)
        mutated["local_blocks"]["2+2+2"]["projective_syndromes"][
            "nonzero_scalar_multiples_per_line"
        ] = 5
        with self.assertRaisesRegex(ValueError, "scalar closure"):
            check.validate_results(mutated)

    def test_line_census(self):
        lines = self.results["local_blocks"]["2+2+2"]["projective_syndromes"]
        self.assertEqual(lines["line_count"], 66)
        self.assertEqual(lines["line_pattern_multiplicity_distribution"], {"2": 60, "4": 6})
        self.assertEqual(lines["maximum_patterns_on_one_line"], 4)

    def test_two_space_normalization_and_matching_census(self):
        census = self.results["local_blocks"]["2+2+2"]["two_space_census"]
        self.assertEqual(census["raw_unordered_line_pairs"], 2145)
        self.assertEqual(census["distinct_generated_two_spaces"], 1923)
        self.assertEqual(census["duplicate_pair_normalizations_removed"], 222)
        self.assertEqual(census["maximum_matching_number"], 8)
        self.assertEqual(
            census["matching_number_distribution"],
            {"2": 480, "4": 1251, "6": 168, "8": 24},
        )

    def test_type_24_equality_case_has_no_zero_syndrome(self):
        block = self.results["local_blocks"]["2+4"]
        self.assertEqual(block["rank_F7"], 21)
        self.assertEqual(block["z_patterns_in_column_space"], 0)

    def test_rank22_boundary_is_positive_but_local_only(self):
        boundary = self.results["local_blocks"]["2+2+2"]["three_space_boundary"]
        self.assertEqual(boundary["raw_unordered_line_triples"], 45760)
        self.assertEqual(boundary["raw_independent_line_triples"], 45556)
        self.assertEqual(boundary["distinct_generated_three_spaces"], 25744)
        self.assertEqual(boundary["spaces_supporting_a_perfect_matching"], 32)
        self.assertTrue(
            check.is_perfect_pattern_matching(
                tuple(edge)
                for edge in boundary["canonical_first_witness"]["perfect_matching"]
            )
        )
        self.assertIn(
            "not that a global graph",
            self.results["status_wall"]["rank_22_boundary_meaning"],
        )

    def test_wrong_matching_census_is_rejected(self):
        mutated = copy.deepcopy(self.results)
        mutated["local_blocks"]["2+2+2"]["two_space_census"][
            "maximum_matching_number"
        ] = 12
        with self.assertRaisesRegex(ValueError, "two-space census"):
            check.validate_results(mutated)

    def test_endpoint_status_inflation_is_rejected(self):
        mutated = copy.deepcopy(self.results)
        mutated["status_wall"]["endpoint_excluded"] = True
        with self.assertRaisesRegex(ValueError, "endpoint status inflation"):
            check.validate_results(mutated)

    def test_general_bound_status_inflation_is_rejected(self):
        mutated = copy.deepcopy(self.results)
        mutated["status_wall"]["general_upper_bound_improved_below_4158"] = True
        mutated["status_wall"]["strongest_general_upper_bound"] = "n3<=4157"
        with self.assertRaisesRegex(ValueError, "general-bound status inflation"):
            check.validate_results(mutated)

    def test_novelty_status_inflation_is_rejected(self):
        mutated = copy.deepcopy(self.results)
        mutated["status_wall"]["literature_novelty"] = "NOVEL"
        with self.assertRaisesRegex(ValueError, "novelty status inflation"):
            check.validate_results(mutated)


if __name__ == "__main__":
    unittest.main()
