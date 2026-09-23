#!/usr/bin/env python3
"""Hostile exact tests for the independent Wave-23 endpoint synthesis."""

from __future__ import annotations

import itertools
import json
import tempfile
import unittest
from pathlib import Path

import exact_check


class EndpointCrosscheckTests(unittest.TestCase):
    def test_01_frozen_inputs_match(self) -> None:
        checked = exact_check.check_frozen_inputs()
        self.assertEqual(len(checked), 5)
        self.assertTrue(all(record["status"] == "PASS" for record in checked.values()))

    def test_02_endpoint_result_closes_705_only_conditionally(self) -> None:
        result = exact_check.build_results()
        self.assertEqual(
            result["conclusion"]["n3_705"],
            "EXCLUDED_CONDITIONALLY_ON_AUDITED_PREMISES",
        )
        self.assertEqual(result["conclusion"]["conditional_n3_lower_bound"], 708)
        self.assertEqual(result["conclusion"]["target_status"], "UNKNOWN")
        self.assertFalse(result["conclusion"]["graph_construction"])

    def test_03_even_determinant_residues(self) -> None:
        self.assertEqual(exact_check.even_odd_determinant_residue(2), 3)
        self.assertEqual(exact_check.even_odd_determinant_residue(4), 1)
        self.assertEqual(exact_check.even_odd_determinant_residue(44), 1)

    def test_04_odd_rank_rejected_for_even_determinant_lemma(self) -> None:
        with self.assertRaises(exact_check.CheckError):
            exact_check.even_odd_determinant_residue(43)

    def test_05_exhaustive_rank_two_residue(self) -> None:
        seen = 0
        for first_diagonal, second_diagonal in itertools.product((0, 2), repeat=2):
            for off_diagonal in range(4):
                matrix = [
                    [first_diagonal, off_diagonal],
                    [off_diagonal, second_diagonal],
                ]
                determinant = exact_check.determinant_bareiss(matrix)
                if determinant % 2:
                    seen += 1
                    self.assertEqual(determinant % 4, 3)
        self.assertGreater(seen, 0)

    def test_06_exhaustive_rank_four_residue(self) -> None:
        seen = 0
        edge_positions = tuple(itertools.combinations(range(4), 2))
        for diagonals in itertools.product((0, 2), repeat=4):
            for off_diagonals in itertools.product(range(4), repeat=6):
                matrix = [[0] * 4 for _ in range(4)]
                for index, value in enumerate(diagonals):
                    matrix[index][index] = value
                for (left, right), value in zip(edge_positions, off_diagonals):
                    matrix[left][right] = value
                    matrix[right][left] = value
                determinant = exact_check.determinant_bareiss(matrix)
                if determinant % 2:
                    seen += 1
                    self.assertEqual(determinant % 4, 1)
        self.assertGreater(seen, 0)

    def test_07_scaled_dual_rank_two_sanity(self) -> None:
        # G=[[2,1],[1,2]], scale=3 gives S=3G^{-1}=[[2,-1],[-1,2]].
        gram = [[2, 1], [1, 2]]
        scaled_dual = [[2, -1], [-1, 2]]
        self.assertEqual(exact_check.determinant_bareiss(gram), 3)
        self.assertEqual(exact_check.determinant_bareiss(scaled_dual), 3)
        self.assertTrue(all(scaled_dual[index][index] % 2 == 0 for index in range(2)))

    def test_08_scaled_dual_endpoint_facts(self) -> None:
        facts = exact_check.scaled_dual_facts()
        self.assertTrue(facts["integral"])
        self.assertTrue(facts["even"])
        self.assertEqual(facts["determinant"], "h")
        self.assertEqual(facts["signature_mod_8"], 4)

    def test_09_wrong_projector_scale_rejected(self) -> None:
        with self.assertRaises(exact_check.CheckError):
            exact_check.scaled_dual_facts(scale=20)

    def test_10_trace_square_floor(self) -> None:
        result = exact_check.trace_square_floor()
        self.assertEqual(result["trace_C"], 2)
        self.assertEqual(result["trace_C2_mod_2"], 0)
        self.assertEqual(result["trace_B2_mod_8"], 4)
        self.assertEqual(result["minimum_trace_B2"], 60)
        self.assertEqual(result["minimum_trace_A4_squared"], 26460)

    def test_11_trace_square_bound_is_sharp_before_lattice_factorization(self) -> None:
        # C=diag(1,1,0,...,0), B=I+2C=diag(3,3,1,...,1).
        c_diagonal = [1, 1] + [0] * 42
        b_diagonal = [1 + 2 * value for value in c_diagonal]
        self.assertEqual(sum(b_diagonal), 48)
        self.assertEqual(sum(value * value for value in b_diagonal), 60)
        self.assertEqual(math_product(b_diagonal), 9)

    def test_12_trace_parity_mutation_rejected(self) -> None:
        with self.assertRaises(exact_check.CheckError):
            exact_check.trace_square_floor(trace=47)

    def test_13_wrong_rank_mutation_rejected(self) -> None:
        with self.assertRaises(exact_check.CheckError):
            exact_check.trace_square_floor(rank=43)

    def test_14_maclaurin_endpoint_arithmetic(self) -> None:
        result = exact_check.maclaurin_bound()
        self.assertEqual(result["e2_upper"], 1122)
        self.assertEqual(result["pair_count"], 946)
        self.assertEqual(result["normalized_e2"], {"numerator": 51, "denominator": 43})
        self.assertEqual(result["integer_cap"], 42)

    def test_15_exact_power_comparison(self) -> None:
        self.assertLess(51**22, 43**23)
        result = exact_check.maclaurin_bound()
        self.assertEqual(result["exact_comparison"]["gap"], 43**23 - 51**22)

    def test_16_omitting_mod_eight_leaves_old_endpoint(self) -> None:
        relaxed = exact_check.maclaurin_bound(
            trace_square_lower=54,
            require_endpoint_values=False,
        )
        self.assertEqual(relaxed["integer_cap"], 45)
        ledger = exact_check.relaxed_route_ledger()
        self.assertEqual(
            ledger["omit_trace_B2_mod_8"]["survivor"],
            {"h": 9, "det_Q": 5, "det_B": 45},
        )

    def test_17_smooth_numbers(self) -> None:
        self.assertEqual(exact_check.smooth_numbers_at_most(8), [1, 3, 7])
        self.assertEqual(exact_check.smooth_numbers_at_most(14), [1, 3, 7, 9])

    def test_18_full_factor_pair_list_is_empty(self) -> None:
        result = exact_check.endpoint_factorization(exact_check.maclaurin_bound())
        self.assertEqual(result["h_upper"], 8)
        self.assertEqual(result["pairs_after_all_constraints"], [])

    def test_19_before_h1_obstruction_only_h1_survives(self) -> None:
        result = exact_check.endpoint_factorization(exact_check.maclaurin_bound())
        self.assertEqual(
            {pair["h"] for pair in result["pairs_before_h1_obstruction"]},
            {1},
        )

    def test_20_det_Q_one_signature_hostile_survivor(self) -> None:
        ledger = exact_check.relaxed_route_ledger()
        self.assertEqual(
            ledger["omit_det_Q_one_signature_obstruction"]["survivor"],
            {"h": 9, "det_Q": 1, "det_B": 9},
        )
        survivor = ledger["omit_det_Q_one_signature_obstruction"]["survivor"]
        self.assertEqual(survivor["det_B"] % 4, 1)
        self.assertEqual(survivor["det_Q"] % 4, 1)

    def test_21_nonsmooth_h_five_hostile_survivor(self) -> None:
        ledger = exact_check.relaxed_route_ledger()
        self.assertEqual(
            ledger["omit_3_7_smoothness"]["survivor"],
            {"h": 5, "det_Q": 5, "det_B": 25},
        )

    def test_22_h1_obstruction_is_essential(self) -> None:
        ledger = exact_check.relaxed_route_ledger()
        self.assertGreater(
            ledger["omit_scaled_dual_h1_obstruction"]["survivor_count"], 0
        )

    def test_23_modular_rank_boundary(self) -> None:
        result = exact_check.build_results()["modular_rank_boundary"]
        self.assertEqual(result["rank_F2_B"], 44)
        self.assertEqual(result["rank_F2_A4"], 44)
        self.assertEqual(
            result["claim_at_primes_3_5_7"],
            "NONE_FROM_FROZEN_RANK_DATA",
        )

    def test_24_induced_c6_translation(self) -> None:
        result = exact_check.build_results()["conclusion"]
        self.assertEqual(result["conditional_n3_lower_bound"], 708)
        self.assertEqual(result["conditional_induced_C6_lower_bound"], 209994)

    def test_25_json_writer_forces_lf(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "result.json"
            exact_check.write_json(path, exact_check.build_results())
            raw = path.read_bytes()
            self.assertNotIn(b"\r\n", raw)
            self.assertTrue(raw.endswith(b"\n"))
            parsed = json.loads(raw)
            self.assertEqual(
                parsed["claim_label"], "DERIVED_PENDING_INDEPENDENT_VERIFIER"
            )


def math_product(values) -> int:
    result = 1
    for value in values:
        result *= value
    return result


if __name__ == "__main__":
    unittest.main()
