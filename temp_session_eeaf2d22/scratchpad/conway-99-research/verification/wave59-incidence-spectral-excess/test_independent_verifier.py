from __future__ import annotations

import copy
import json
import unittest
from fractions import Fraction
from pathlib import Path

import independent_verifier as verifier


class Wave59IndependentVerifierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = verifier.compute_result()

    def test_predistance_orthogonality_and_normalization(self) -> None:
        polynomials = verifier.predistance_polynomials()
        for index, polynomial in enumerate(polynomials):
            self.assertEqual(
                verifier.spectral_inner_product(polynomial, polynomial),
                verifier.polynomial_evaluate(polynomial, 18),
            )
            for prior in polynomials[:index]:
                self.assertEqual(
                    verifier.spectral_inner_product(polynomial, prior), 0
                )

    def test_exact_predistance_polynomials(self) -> None:
        self.assertEqual(
            self.result["triangle_graph_K"][
                "predistance_polynomials_low_to_high"
            ],
            [
                ["1"],
                ["0", "1"],
                ["-27/2", "-15/4", "3/4"],
                ["25/2", "19/12", "-35/36", "1/18"],
            ],
        )

    def test_relation_valencies(self) -> None:
        self.assertEqual(
            self.result["triangle_relations"]["valencies"],
            {"I": 1, "K": 18, "B": 36, "C": 144, "D": 32},
        )
        self.assertEqual(2 * 36 + 144, 216)
        self.assertEqual(1 + 18 + 36 + 144 + 32, 231)

    def test_distance_layer_bipartitions(self) -> None:
        point_layers = self.result["incidence_graph_L"]["point_root"][
            "distance_layers"
        ]
        triangle_layers = self.result["incidence_graph_L"]["triangle_root"][
            "distance_layers"
        ]
        self.assertEqual((sum(point_layers[::2]), sum(point_layers[1::2])), (99, 231))
        self.assertEqual(
            (sum(triangle_layers[::2]), sum(triangle_layers[1::2])),
            (231, 99),
        )

    def test_walk_tables(self) -> None:
        tables = self.result["triangle_graph_K"]["walk_tables"]
        self.assertEqual(
            tables["K_squared"], {"I": 18, "K": 5, "B": 2, "C": 1, "D": 0}
        )
        self.assertEqual(
            tables["K_cubed"],
            {"I": 90, "K": 59, "B": 26, "C": 22, "D": 18},
        )

    def test_defect_and_projection(self) -> None:
        triangle_graph = self.result["triangle_graph_K"]
        self.assertEqual(
            triangle_graph["defect"]["entries"],
            {"I": "0", "K": "0", "B": "-1/2", "C": "1/4", "D": "0"},
        )
        self.assertEqual(
            triangle_graph["defect"]["normalized_norm_squared"], "18"
        )
        self.assertEqual(
            triangle_graph["distance_matrix_projection"][
                "normalized_residual_norm_squared"
            ],
            "288/25",
        )

    def test_pair_neighborhood_gram(self) -> None:
        gram = self.result["triangle_graph_K"]["pair_neighborhood_gram"]
        self.assertEqual(gram["entries"], {"I": "153", "K": "10", "B": "1", "C": "0", "D": "0"})
        self.assertEqual(gram["weyl_lower_bound"], 87)
        self.assertTrue(gram["positive_definite"])
        self.assertEqual(gram["rank"], 231)
        self.assertEqual(gram["trace_square"], 5_831_595)

    def test_ihara_traces_and_cycles(self) -> None:
        bass = self.result["nonbacktracking"]
        self.assertEqual(
            bass["trace_H_powers"],
            {
                "2": 0,
                "4": 0,
                "6": 0,
                "8": 33264,
                "10": 665280,
                "12": 6020784,
                "14": 69854400,
            },
        )
        self.assertEqual(
            bass["simple_cycle_counts"],
            {"8": 2079, "10": 33264, "12": 250866, "14": 2494800},
        )

    def test_eight_cycle_independent_srg_count(self) -> None:
        nonedges = 99 * (99 - 1 - 14) // 2
        self.assertEqual(nonedges, 4158)
        self.assertEqual(nonedges // 2, 2079)

    def test_cage_arithmetic(self) -> None:
        cage = self.result["cage_comparison"]
        self.assertEqual(
            cage["biregular_girth_8_edge_root_Moore_bound"],
            {"points": 39, "lines": 91, "total": 130},
        )
        self.assertEqual(7 * 39, 3 * 91)
        self.assertEqual(cage["excess_over_bound"], 200)

    def test_relation_label_order_invariance(self) -> None:
        entries = {"C": Fraction(1, 4), "D": 0, "B": Fraction(-1, 2), "K": 0, "I": 0}
        self.assertEqual(verifier.relation_norm_squared(entries), Fraction(18))

    def test_hostile_B_valency_mutation_is_detected(self) -> None:
        mutated = copy.deepcopy(self.result)
        mutated["triangle_relations"]["valencies"]["B"] = 35
        self.assertNotEqual(
            mutated["triangle_relations"]["valencies"],
            verifier.RELATION_VALENCIES,
        )

    def test_hostile_predistance_mutation_breaks_normalization(self) -> None:
        p3 = list(verifier.predistance_polynomials()[3])
        p3[0] += 2
        self.assertNotEqual(
            verifier.spectral_inner_product(p3, p3),
            verifier.polynomial_evaluate(p3, 18),
        )

    def test_sealed_result_comparison(self) -> None:
        root = Path(__file__).resolve().parents[2]
        discovery_path = (
            root / "attempts" / "wave59-incidence-spectral-excess" / "exact-result.json"
        )
        self.assertEqual(
            verifier.sha256_file(discovery_path),
            verifier.DISCOVERY_RESULT_SHA256,
        )
        discovery = json.loads(discovery_path.read_text(encoding="utf-8"))
        self.assertEqual(verifier.compare_discovery(self.result, discovery), [])


if __name__ == "__main__":
    unittest.main()
