#!/usr/bin/env python3
"""Hostile exact tests for the Wave 30 h=729 construction."""

from __future__ import annotations

import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

import exact_check as check


class Wave30H729ConstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = check.exact_result()
        cls.nb = check.load_helper(
            "wave30_test_neighbor_helper", check.NEIGHBOR_HELPER_PATH
        )

    def test_frozen_inputs(self) -> None:
        self.assertEqual(
            self.result["frozen_inputs"],
            check.FROZEN_INPUTS,
        )

    def test_root_count_chain(self) -> None:
        self.assertEqual(
            self.result["rank20_construction"]["root_count_chain"],
            list(check.EXPECTED_ROOT_COUNTS),
        )
        self.assertEqual(
            len(self.result["rank20_construction"]["neighbor_chain"]),
            5,
        )

    def test_each_neighbor_certificate_is_unimodular(self) -> None:
        for step in self.result["rank20_construction"]["neighbor_chain"]:
            self.assertIn(step["det_P"], (-1, 1))
            self.assertEqual(len(step["neighbor_basis_P"]), 20)
            self.assertEqual(len(step["exact_lll_row_transform_U"]), 20)

    def test_neighbor_divisibility_is_active(self) -> None:
        start = self.nb.block_diagonal([
            check.qmatrix(check.symmetric_from_lower(check.K12_LOWER)),
            check.qmatrix(check.e8_cartan()),
        ])
        support = tuple(i for i in check.NEIGHBOR_SUPPORTS[0] if i != 0)
        vector = [int(i in support) for i in range(20)]
        self.assertNotEqual(
            int(self.nb.quadratic(vector, start)) % 8,
            0,
        )

    def test_t20_exact_invariants(self) -> None:
        t20 = self.result["rank20_construction"]["T20"]
        self.assertEqual(t20["rank"], 20)
        self.assertEqual(t20["determinant"], 729)
        self.assertEqual(t20["minimum"], 4)
        self.assertEqual(t20["norm_two_count"], 0)
        self.assertEqual(t20["norm_four_count"], 5076)
        self.assertEqual(t20["gram_sha256"], check.EXPECTED_FINAL_T20_HASH)
        self.assertTrue(t20["three_scaled_dual_is_even_integral"])

    def test_t20_scaled_dual_identity(self) -> None:
        t20 = check.qmatrix(
            self.result["rank20_construction"]["T20"]["gram"]
        )
        g20 = check.qmatrix(
            self.result["rank20_construction"]["T20"][
                "scaled_dual_21_T20_inverse"
            ]
        )
        self.assertTrue(self.nb.is_even_integral_form(t20))
        self.assertTrue(self.nb.is_even_integral_form(g20))
        self.assertEqual(
            self.nb.matmul(t20, g20),
            self.nb.matrix_scale(21, self.nb.eye(20)),
        )

    def test_shell_enumeration_is_complete_and_exact(self) -> None:
        shell = self.result["rank20_construction"]["T20"][
            "shell_through_norm_4"
        ]
        self.assertEqual(shell["counts"], {"0": 1, "4": 5076})
        self.assertEqual(
            shell["enumeration"]["bound_method"],
            "exact reverse-LDL rational interval with integer isqrt",
        )
        self.assertGreater(shell["enumeration"]["accepted_partial_nodes"], 5076)

    def test_rank44_candidate_exact_invariants(self) -> None:
        candidate = self.result["rank44_candidate"]
        self.assertEqual(candidate["candidate_id"], "W30-H729-T20-L24-001")
        self.assertEqual(candidate["rank"], 44)
        self.assertEqual(candidate["determinant"], 729)
        self.assertEqual(candidate["minimum"], 4)
        self.assertTrue(candidate["rootless"])
        self.assertEqual(candidate["exact_level"], 3)
        self.assertTrue(candidate["three_scaled_dual_is_even_integral"])

    def test_rank44_scaled_dual_identity(self) -> None:
        candidate = self.result["rank44_candidate"]
        s44 = check.qmatrix(candidate["S"])
        g44 = check.qmatrix(candidate["G_equals_21_S_inverse"])
        self.assertTrue(self.nb.is_even_integral_form(s44))
        self.assertTrue(self.nb.is_even_integral_form(g44))
        self.assertEqual(self.nb.determinant(s44), 729)
        self.assertEqual(
            self.nb.matmul(s44, g44),
            self.nb.matrix_scale(21, self.nb.eye(44)),
        )
        self.assertTrue(
            self.nb.is_even_integral_form(
                self.nb.matrix_scale(3, self.nb.inverse(s44))
            )
        )

    def test_block_decomposition_is_literal(self) -> None:
        s44 = self.result["rank44_candidate"]["S"]
        self.assertTrue(
            all(s44[i][j] == 0 for i in range(20) for j in range(20, 44))
        )
        self.assertTrue(
            all(s44[i][j] == 0 for i in range(20, 44) for j in range(20))
        )
        self.assertEqual(
            self.result["rank44_candidate"]["decomposition"],
            [
                {"name": "T20", "rank": 20, "determinant": 729, "minimum": 4},
                {
                    "name": "LAMBDA24",
                    "rank": 24,
                    "determinant": 1,
                    "minimum": 4,
                },
            ],
        )

    def test_leech_rootlessness_is_independently_checked(self) -> None:
        leech = self.result["rank44_candidate"]["Leech"]
        self.assertEqual(leech["determinant"], 1)
        self.assertEqual(leech["minimum"], 4)
        self.assertEqual(
            leech["root_shell_through_norm_2"]["counts"],
            {"0": 1},
        )

    def test_leech_data_mutation_is_detected(self) -> None:
        mutated = [row[:] for row in check.LEECH]
        mutated[0][0] += 2
        self.assertNotEqual(
            self.nb.determinant(check.qmatrix(mutated)),
            Fraction(1),
        )

    def test_required_frame_split(self) -> None:
        split = self.result["rank44_candidate"][
            "necessary_frame_row_split_if_realized"
        ]
        self.assertEqual(split["T20_rows"], 105)
        self.assertEqual(split["LAMBDA24_rows"], 126)
        self.assertEqual(split["T20_rows"] + split["LAMBDA24_rows"], 231)
        self.assertGreaterEqual(
            self.result["rank20_construction"]["T20"]["norm_four_count"] // 2,
            split["T20_rows"],
        )

    def test_scope_wall_names_missing_bridges(self) -> None:
        missing = " ".join(self.result["rank44_candidate"]["not_constructed"])
        for required in ("determinant-five Q", "105-row tight frame", "231-row X",
                         "M=X*S*X^T", "Q=X^T*(M o M)*X", "graph"):
            self.assertIn(required, missing)
        self.assertEqual(
            self.result["rank44_candidate"]["evidence_label"],
            "FINITE_COMPUTATIONAL_EVIDENCE",
        )

    def test_no_automorphism_or_complete_search_claim(self) -> None:
        restrictions = self.result["restrictions"]
        self.assertIn("No automorphism", restrictions["automorphisms"])
        self.assertIn("not a complete enumeration", restrictions["neighbor_search"])
        self.assertIn("No subset", restrictions["frame_status"])

    def test_deterministic_serialization(self) -> None:
        rendered = check.render(self.result)
        self.assertEqual(rendered, check.render(check.exact_result()))
        self.assertEqual(
            check.DEFAULT_OUTPUT.read_bytes(),
            rendered.encode("utf-8"),
        )
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "result.json"
            output.write_text(rendered, encoding="utf-8", newline="\n")
            self.assertEqual(output.read_bytes(), rendered.encode("utf-8"))


if __name__ == "__main__":
    unittest.main()
