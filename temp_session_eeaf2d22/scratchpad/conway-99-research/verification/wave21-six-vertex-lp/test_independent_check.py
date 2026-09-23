from __future__ import annotations

import importlib.util
import os
import unittest
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave21_independent_check", HERE / "independent_check.py"
)
assert SPEC and SPEC.loader
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)

SIX_TEX = Path(
    os.environ.get(
        "WAVE21_SIX_TEX",
        HERE / "source-cache" / "six-v2" / "The_Subgraphs_of_Order_Six.tex",
    )
)
SEVEN_TEX = Path(
    os.environ.get(
        "WAVE21_SEVEN_TEX",
        HERE / "source-cache" / "seven-v1" / "Hamiltonian_Subgraphs_of_Order_Seven.tex",
    )
)


class IndependentWave21Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        six_text, seven_text = CHECK.read_sources(SIX_TEX, SEVEN_TEX)
        cls.tables = CHECK.source_tables(six_text, seven_text)
        cls.raw, cls.corrected = CHECK.build_audit(SIX_TEX, SEVEN_TEX)

    def test_01_pinned_source_hashes(self) -> None:
        self.assertEqual(CHECK.sha256(SIX_TEX), CHECK.SIX_TEX_SHA256)
        self.assertEqual(CHECK.sha256(SEVEN_TEX), CHECK.SEVEN_TEX_SHA256)

    def test_02_primary_formula_counts(self) -> None:
        self.assertEqual(
            self.corrected["formula_counts"],
            {"four": 9, "five": 21, "six": 62, "hamiltonian_seven": 19},
        )

    def test_03_independent_local_class_census(self) -> None:
        self.assertEqual(
            self.corrected["graph_and_deck_audit"]["local_class_counts"],
            {"order4": 9, "order5": 21, "order6": 62, "order7_hamiltonian": 19},
        )

    def test_04_hamiltonian_edge_distribution(self) -> None:
        self.assertEqual(
            self.corrected["graph_and_deck_audit"]["hamiltonian7_edge_distribution"],
            {"7": 1, "8": 2, "9": 7, "10": 7, "11": 2},
        )

    def test_05_four_to_five_deck_alignment(self) -> None:
        result = self.corrected["graph_and_deck_audit"]["four_to_five"]
        self.assertEqual(result["all_column_sums"], [5])
        self.assertTrue(result["mapping_is_bijective"])
        self.assertEqual(len(result["L_source_to_local_zero_based"]), 9)
        self.assertEqual(len(result["M_source_to_local_zero_based"]), 21)

    def test_06_raw_printed_failure_is_exact(self) -> None:
        self.assertEqual(self.raw["verdict"], "FAIL_AS_PRINTED")
        self.assertEqual(self.raw["five_to_six_raw_zero_residual_count"], 20)
        self.assertEqual(
            self.raw["five_to_six_raw_nonzero_residuals"],
            [
                {
                    "row": 7,
                    "residual": {
                        "constant": "1496880",
                        "n3_coefficient": "4",
                        "h11_coefficient": "0",
                    },
                }
            ],
        )

    def test_07_n23_raw_column_has_only_five_cards(self) -> None:
        result = self.corrected["graph_and_deck_audit"]["five_to_six_raw"]
        self.assertEqual(result["column_sum_histogram"], {"5": 1, "6": 61})
        self.assertEqual(result["N23_column_sum"], 5)
        self.assertEqual(result["N23_exact_local_match_count"], 0)

    def test_08_unique_one_card_repair_is_m7(self) -> None:
        result = self.corrected["graph_and_deck_audit"]["five_to_six_correction"]
        self.assertEqual(result["one_card_repair_rows_that_match_a_local_deck"], [7])
        self.assertEqual(result["all_corrected_column_sums"], [6])
        self.assertTrue(result["mapping_is_bijective"])

    def test_09_wrong_one_card_repair_is_rejected(self) -> None:
        raw = [row[:] for row in self.tables["five_to_six_raw"]]
        raw[5][22] += 1  # Deliberately add N23 to M6 instead of M7.
        classes5 = CHECK.local_classes(5)
        classes6 = CHECK.local_classes(6)
        deck56 = CHECK.deletion_matrix(classes5, classes6)
        m_mapping = self.corrected["graph_and_deck_audit"]["four_to_five"][
            "M_source_to_local_zero_based"
        ]
        with self.assertRaises(AssertionError):
            CHECK.align_columns(raw, deck56, m_mapping)

    def test_10_n3_index_semantics(self) -> None:
        result = self.corrected["graph_and_deck_audit"]["N3_alignment"]
        self.assertEqual(result["source_index"], 3)
        self.assertEqual(result["edge_count"], 8)
        self.assertEqual(result["cross_edge_count"], 2)
        self.assertTrue(result["cross_edges_form_matching"])
        self.assertEqual(len(result["triangles"]), 2)

    def test_11_all_symbolic_supporting_identities(self) -> None:
        self.assertEqual(
            self.corrected["identity_checks"],
            {
                "four_to_five_zero_residual_count": 9,
                "five_to_six_corrected_zero_residual_count": 21,
                "seven_derivation_zero_residual_count": 18,
            },
        )

    def test_12_six_vertex_exact_feasible_set(self) -> None:
        result = self.corrected["six_feasibility"]
        self.assertEqual(result["rational_lower"], "0")
        self.assertEqual(result["rational_upper"], "4158")
        self.assertEqual(result["integrality_modulus"], 3)
        self.assertEqual(result["integrality_residues"], [0])
        self.assertEqual(
            (result["feasible_first"], result["feasible_last"], result["feasible_step"]),
            (0, 4158, 3),
        )
        self.assertEqual(result["feasible_count"], 1387)

    def test_13_hostile_n1_slope_mutation_changes_facet(self) -> None:
        mutated = dict(self.tables["six"])
        mutated[1] = CHECK.add(CHECK.constant(1386), CHECK.scale(CHECK.variable("n3"), Fraction(-1, 4)))
        result = CHECK.six_feasibility(mutated)
        self.assertEqual(result["rational_upper"], "5544")
        self.assertNotEqual(result["feasible_last"], 4158)

    def test_14_hamiltonian_integrality_and_interval(self) -> None:
        result = self.corrected["seven_feasibility"]
        self.assertEqual(result["integrality_modulus"], 4)
        self.assertTrue(result["all_six_feasible_n3_have_h11"])
        self.assertTrue(result["interval_equals_ceil4_2n3_to_4n3"])
        self.assertEqual(
            result["integrality_residues_by_n3_residue"],
            {"0": [0], "1": [0], "2": [0], "3": [0]},
        )

    def test_15_hostile_h18_denominator_mutation_breaks_interval(self) -> None:
        mutated = dict(self.tables["seven"])
        mutated[18] = CHECK.add(
            CHECK.variable("n3"),
            CHECK.scale(CHECK.variable("h11"), Fraction(-1, 5)),
        )
        six_values = list(range(0, 4159, 3))
        result = CHECK.seven_feasibility(mutated, six_values)
        self.assertFalse(result["interval_equals_ceil4_2n3_to_4n3"])

    def test_16_incumbent_frontier_is_fully_feasible(self) -> None:
        result = self.corrected["seven_feasibility"]
        self.assertEqual(
            (
                result["incumbent_n3_first"],
                result["incumbent_n3_last"],
                result["incumbent_n3_step"],
                result["incumbent_n3_count"],
            ),
            (705, 4158, 3, 1152),
        )
        self.assertEqual(
            result["checks"]["705"],
            {"h11_min": 1412, "h11_max": 2820, "feasible_h11_count": 353},
        )

    def test_17_hexagon_formula_specialization(self) -> None:
        self.assertEqual(
            self.corrected["six_specialized"]["12"],
            {
                "constant": "209286",
                "n3_coefficient": "1",
                "h11_coefficient": "0",
            },
        )

    def test_18_heptagon_formula_specialization(self) -> None:
        self.assertEqual(
            self.corrected["seven_specialized"]["0"],
            {
                "constant": "1247400",
                "n3_coefficient": "-10",
                "h11_coefficient": "-1",
            },
        )

    def test_19_six_counts_partition_all_six_subsets(self) -> None:
        self.assertEqual(
            self.corrected["aggregate"],
            {
                "sum_six": {
                    "constant": "1120529256",
                    "n3_coefficient": "0",
                    "h11_coefficient": "0",
                },
                "binomial_99_6": 1120529256,
            },
        )


if __name__ == "__main__":
    unittest.main()
