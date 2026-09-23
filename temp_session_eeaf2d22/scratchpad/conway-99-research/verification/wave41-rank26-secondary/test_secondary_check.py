from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

import secondary_check as checker


HERE = Path(__file__).resolve().parent


class SecondaryRank26Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = json.loads(
            (HERE / "secondary-results.json").read_text(encoding="utf-8")
        )

    def test_frozen_inputs(self) -> None:
        self.assertEqual(checker.audit_frozen_inputs(), checker.FROZEN_INPUTS)

    def test_positive_partitions_are_complete(self) -> None:
        partitions = tuple(checker.positive_partitions(6))
        self.assertEqual(len(partitions), 11)
        self.assertEqual(len(set(partitions)), 11)
        self.assertTrue(all(sum(partition) == 6 for partition in partitions))

    def test_all_labelled_pairings_are_unique(self) -> None:
        pairings = list(checker.all_pairings())
        self.assertEqual(len(pairings), 10395)
        self.assertEqual(len(set(pairings)), 10395)

    def test_partition_census_is_complete(self) -> None:
        census = checker.matching_partition_census()
        self.assertEqual(sum(census.values()), 10395)
        self.assertEqual(set(census), set(self.result["local_types"]))

    def test_direct_39_block_reduction(self) -> None:
        partition = (4, 2)
        permutation = tuple(
            self.result["even_partition_audits"]["4+2"]
            ["first_canonical_right_kernel_target"]["permutation"]
        )
        matching = next(checker.all_pairings())
        data = checker.quotient_data(partition, permutation)
        residual = checker.add(
            checker.restricted_form(
                data["Z"], checker.within_z_block(matching)
            ),
            data["target"],
            -1,
        )
        predicted = (
            checker.rank(data["S"])
            + 2 * data["F_rank"]
            + checker.rank(residual)
        )
        self.assertEqual(
            checker.rank(checker.full_block(partition, permutation, matching)),
            predicted,
        )

    def test_vectorized_pairing_census_has_positive_control(self) -> None:
        edges, pairing_indices, _ = checker.pairing_index_data()
        matching = next(checker.all_pairings())
        identity = [
            [int(i == j) for j in range(12)]
            for i in range(12)
        ]
        target = checker.within_z_block(matching)
        self.assertEqual(
            checker.pairing_target_hits_numpy(
                identity, target, edges, pairing_indices
            ),
            1,
        )

    def test_vectorized_pairing_census_rejects_bad_diagonal(self) -> None:
        edges, pairing_indices, _ = checker.pairing_index_data()
        identity = [
            [int(i == j) for j in range(12)]
            for i in range(12)
        ]
        target = checker.within_z_block(next(checker.all_pairings()))
        target[0][0] = 1
        self.assertEqual(
            checker.pairing_target_hits_numpy(
                identity, target, edges, pairing_indices
            ),
            0,
        )

    def test_all_odd_three_plus_three_is_not_a_W_block(self) -> None:
        entry = self.result["all_odd_schur_obstructions"]["3+3"]
        self.assertEqual(entry["zero_diagonal_permutation_count"], 1)
        candidate = entry["zero_diagonal_candidates"][0]
        self.assertEqual(candidate["off_diagonal_values_outside_W_alphabet"], 18)
        self.assertFalse(candidate["matching_W_hit"])

    def test_no_automorphism_assumption(self) -> None:
        self.assertFalse(self.result["independence"]["automorphism_assumed"])
        self.assertEqual(
            self.result["partition_completeness"]["labelled_matching_count"],
            10395,
        )
        self.assertEqual(
            self.result["exhaustive_totals"]["minimum_F_permutations"],
            164928,
        )

    def test_validate_accepts_frozen_result(self) -> None:
        checker.validate(self.result)

    def test_validate_rejects_omitted_partition(self) -> None:
        mutated = copy.deepcopy(self.result)
        del mutated["local_types"]["6"]
        with self.assertRaises(ValueError):
            checker.validate(mutated)

    def test_validate_rejects_minimum_F_undercount(self) -> None:
        mutated = copy.deepcopy(self.result)
        mutated["even_partition_audits"]["6"]["minimum_F_permutation_count"] -= 1
        with self.assertRaises(ValueError):
            checker.validate(mutated)

    def test_validate_rejects_R_hit(self) -> None:
        mutated = copy.deepcopy(self.result)
        mutated["even_partition_audits"]["4+2"]["total_rank_25_R_hits"] = 1
        with self.assertRaises(ValueError):
            checker.validate(mutated)

    def test_validate_rejects_rank_inflation(self) -> None:
        mutated = copy.deepcopy(self.result)
        mutated["status_wall"]["universal_rank_F7_M_lower_bound"] = 27
        with self.assertRaises(ValueError):
            checker.validate(mutated)

    def test_validate_rejects_endpoint_inflation(self) -> None:
        mutated = copy.deepcopy(self.result)
        mutated["status_wall"]["endpoint_n3_4158_excluded"] = True
        with self.assertRaises(ValueError):
            checker.validate(mutated)

    def test_malformed_R_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            checker.within_z_block(((0, 1),) * 6)

    def test_nonbijective_border_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            checker.border_matrix([0] * 12)


if __name__ == "__main__":
    unittest.main()
