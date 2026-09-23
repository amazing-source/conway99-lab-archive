"""Focused exact tests for Wave 81."""

from __future__ import annotations

import importlib.util
import itertools
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("exact_check.py")
SPEC = importlib.util.spec_from_file_location("wave81_exact_check", MODULE_PATH)
assert SPEC and SPEC.loader
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class Wave81Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.results = CHECK.build_results()

    def test_support_orbit_census(self) -> None:
        census = self.results["support_enumeration"]
        self.assertEqual(census["anchored_row_sorted_matrix_count"], 1800)
        self.assertEqual(
            census["isomorphism_orbit_count_under_independent_side_relabelling"],
            5,
        )
        self.assertFalse(census["coverage_uses_target_automorphism"])

    def test_every_support_record_has_exact_local_parameters(self) -> None:
        for record in self.results["support_records"]:
            rows = tuple(int(row, 16) for row in record["rows_hex"])
            columns = CHECK.columns_of(rows)
            self.assertEqual([row.bit_count() for row in rows], [4] * 8)
            self.assertEqual([column.bit_count() for column in columns], [4] * 8)
            for blocks in (rows, columns):
                self.assertTrue(
                    all(
                        (blocks[i] & blocks[j]).bit_count() <= 2
                        for i, j in itertools.combinations(range(8), 2)
                    )
                )
                pairs = CHECK.deficiency_pairs(blocks)
                self.assertEqual(len(pairs), 8)
                degrees = [sum(vertex in pair for pair in pairs) for vertex in range(8)]
                self.assertEqual(degrees, [2] * 8)

    def test_canonical_key_is_relabelling_invariant(self) -> None:
        rows = tuple(
            int(row, 16) for row in self.results["support_records"][4]["rows_hex"]
        )
        old_at_new = (6, 1, 4, 0, 7, 2, 5, 3)
        transformed = CHECK.transform_rows(tuple(reversed(rows)), old_at_new)
        self.assertEqual(
            CHECK.canonical_support(rows),
            CHECK.canonical_support(transformed),
        )

    def test_all_basic_couplings_pass_the_recorded_local_flow(self) -> None:
        coupling = self.results["deficiency_couplings"]
        self.assertEqual(
            coupling["coupling_multiset_count_across_orbit_representatives"],
            4985,
        )
        self.assertEqual(
            coupling[
                "locally_closed_coupling_count_across_orbit_representatives"
            ],
            4985,
        )
        self.assertEqual(coupling["support_orbits_with_locally_closed_coupling"], 5)

    def test_type_degree_closure_leaves_only_zero_or_one_x2_edge(self) -> None:
        closure = self.results["outside_type_degree_closure"]
        self.assertEqual(closure["surviving_t"], [0, 1])
        self.assertEqual(closure["histogram_counts_by_t"]["0"], 43)
        self.assertEqual(closure["histogram_counts_by_t"]["1"], 7)
        self.assertTrue(
            all(
                closure["histogram_counts_by_t"][str(t)] == 0
                for t in range(2, 13)
            )
        )

    def test_principal_minor_spectral_certificates(self) -> None:
        spectra = [
            record["outside_spectrum"] for record in self.results["support_records"]
        ]
        self.assertTrue(
            all(
                spectrum["trace_powers_1_through_4"][:3] == [0, 1002, 906]
                for spectrum in spectra
            )
        )
        self.assertEqual(
            [spectrum["outside_four_cycles"] for spectrum in spectra],
            [1135, 1133, 1132, 1131, 1131],
        )
        self.assertTrue(
            all(
                len(spectrum["q_H_coefficients_descending"]) == 16
                and spectrum["q_H_coefficients_descending"][0] == 1
                for spectrum in spectra
            )
        )
        self.assertEqual(spectra[2]["determinant"], 0)

    def test_contingency_positive_and_negative_controls(self) -> None:
        identity = [[int(i == j) for j in range(8)] for i in range(8)]
        self.assertTrue(CHECK.contingency_feasible(identity, [1] * 8, [1] * 8))
        identity[0][0] = 0
        self.assertFalse(CHECK.contingency_feasible(identity, [1] * 8, [1] * 8))

    def test_hostile_duplicate_blocks_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            CHECK.deficiency_pairs((15, 15, 51, 85, 105, 150, 170, 204))


if __name__ == "__main__":
    unittest.main()
