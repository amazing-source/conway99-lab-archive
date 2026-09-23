#!/usr/bin/env python3
"""Hostile and deterministic tests for the Wave 31 commutator theorem."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import exact_check as check


class Wave31ProjectorBlockTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = check.derive()

    def test_frozen_inputs(self) -> None:
        self.assertEqual(
            self.result["frozen_input_hashes"],
            check.FROZEN_INPUTS,
        )

    def test_minus_four_projector(self) -> None:
        self.assertEqual(
            check.minus_four_projector_values(),
            {14: 0, 3: 0, -4: 1},
        )

    def test_incidence_dimensions_and_scale(self) -> None:
        transport = self.result["projector_transport"]
        self.assertEqual(transport["imE_dimension"], 44)
        self.assertEqual(transport["V_dimension"], 44)
        self.assertEqual(transport["norm_identity"], "||Nu||^2=3||u||^2 for u in im(E)")

    def test_commutator_coefficients(self) -> None:
        self.assertEqual(
            check.transport_coefficients(),
            {
                "projector_A_coefficient": 9,
                "K_one_coefficient": 3,
                "reduced_commutator_coefficient": 3,
            },
        )

    def test_same_triangle_edge_signs_cancel(self) -> None:
        control = check.local_signed_edge_cancellation(-1, -1)
        self.assertEqual(control["ZA_minus_AZ_xy"], 0)
        self.assertTrue(control["cancels"])

    def test_mutated_edge_signs_do_not_cancel(self) -> None:
        control = self.result["hostile_controls"][
            "different_signs_on_edges_of_one_graph_triangle"
        ]
        self.assertEqual(control["local"]["ZA_minus_AZ_xy"], 2)
        self.assertFalse(control["local"]["cancels"])
        self.assertEqual(control["adjacent_difference_permitted"], -3)

    def test_signed_block_sizes(self) -> None:
        self.assertEqual(
            [item["block_size"] for item in check.signed_block_sizes()],
            [0, 33, 66, 99, 132, 165, 198, 231],
        )

    def test_all_proper_rootless_block_ranks_fail(self) -> None:
        census = check.rootless_block_census()
        self.assertEqual(
            [item["block_rank"] for item in census],
            list(range(4, 44, 4)),
        )
        self.assertTrue(
            all(item["status"] == "EXCLUDED_DERIVED" for item in census)
        )
        self.assertTrue(all(item["rows_mod_33"] for item in census))

    def test_wave30_split_fails_both_sides(self) -> None:
        boundary = self.result["wave30_boundary"]
        self.assertEqual(
            boundary["rows"],
            {"rank20_A_rows": 105, "rank24_U_rows": 126},
        )
        self.assertEqual(
            boundary["rows_mod_33"],
            {"rank20_A_rows": 6, "rank24_U_rows": 27},
        )

    def test_superseded_u_tensor_profile(self) -> None:
        side = self.result["superseded_tensor_side_route"]
        self.assertEqual(side["q_before_graph_gap"], [1, 2, 3])
        self.assertEqual(side["q_after_graph_gap"], [2, 3])
        self.assertEqual(side["unique_U_profile"], {"n_q2": 122, "n_q3": 4})
        self.assertEqual(
            side["equivalent_c_profile"],
            {"n_c9": 4, "n_c10": 122, "n_c11": 0},
        )

    def test_full_rank_control_is_allowed(self) -> None:
        self.assertIn(
            {"constant_signed_degree": 7, "block_size": 231},
            check.signed_block_sizes(),
        )
        self.assertEqual(21 * 44 // 4, 231)

    def test_no_h_or_n3_value_enters_divisibility(self) -> None:
        serialized = str(self.result["divisibility"]) + str(
            self.result["rootless_block_trace"]
        )
        self.assertNotIn("729", serialized)
        self.assertNotIn("708", serialized)

    def test_every_named_premise_is_active(self) -> None:
        for premise in check.ESSENTIAL_PREMISES:
            enabled = set(check.ESSENTIAL_PREMISES)
            enabled.remove(premise)
            with self.subTest(premise=premise):
                with self.assertRaises(check.PremiseError):
                    check.derive(enabled)

    def test_scope_wall(self) -> None:
        conclusions = self.result["conclusions"]
        self.assertEqual(
            conclusions["nontrivial_rootless_integrally_decomposable_endpoint_S"],
            "REFUTED_DERIVED",
        )
        self.assertEqual(conclusions["rooted_endpoint_forms"], "UNKNOWN")
        self.assertEqual(
            conclusions["rootless_indecomposable_endpoint_forms"],
            "UNKNOWN",
        )
        self.assertEqual(conclusions["n3_708"], "UNKNOWN")
        self.assertEqual(conclusions["Conway_99"], "UNKNOWN")

    def test_deterministic_lf_json(self) -> None:
        candidate = Path(__file__).with_name("exact-results.json")
        with tempfile.TemporaryDirectory() as directory:
            generated = Path(directory) / "exact-results.json"
            check.write_json(generated, self.result)
            self.assertEqual(generated.read_bytes(), candidate.read_bytes())
            self.assertTrue(generated.read_bytes().endswith(b"\n"))
            self.assertNotIn(b"\r", generated.read_bytes())


if __name__ == "__main__":
    unittest.main()
