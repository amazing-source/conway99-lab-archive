"""Hostile exact tests for the Wave 26 A2 cubic obstruction."""

from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import exact_check as check


class FrozenInputTests(unittest.TestCase):
    def test_public_base_is_full_hash(self) -> None:
        self.assertEqual(len(check.PUBLIC_BASE), 40)
        int(check.PUBLIC_BASE, 16)

    def test_frozen_inputs(self) -> None:
        rows = check.validate_frozen_inputs()
        self.assertEqual(len(rows), 3)
        self.assertEqual({row["path"] for row in rows}, set(check.INPUTS))

    def test_explicit_certificate_blocks(self) -> None:
        result = check.validate_explicit_survivor()
        self.assertEqual(len(result["orthogonal_A2_blocks"]), 2)
        for block in result["orthogonal_A2_blocks"]:
            self.assertEqual(block["trace_SQ"], 10)
            self.assertEqual(block["B"], [[5, -4], [-4, 5]])


class A2ArithmeticTests(unittest.TestCase):
    def test_exact_small_vector_classification(self) -> None:
        result = check.a2_small_vector_classification()
        self.assertEqual(len(result["norm_2_vectors"]), 6)
        self.assertEqual(result["norm_4_vectors"], [])
        self.assertEqual(result["residues_of_a2_minus_ab_plus_b2_mod_3"], [0, 1])

    def test_root_line_counts(self) -> None:
        self.assertEqual(check.solve_root_line_counts(), (7, 7, 7))
        self.assertEqual(
            check.solve_root_line_counts(((12, 6), (6, 12))),
            (6, 6, 6),
        )

    def test_cubic_gram(self) -> None:
        self.assertEqual(
            check.cubic_gram(),
            [[8, -1, 1], [-1, 8, 1], [1, 1, 8]],
        )

    def test_cubic_norm_sum_of_squares_identity(self) -> None:
        for d in (
            (-7, -5, 3),
            (-1, -1, 1),
            (0, 0, 0),
            (1, 1, -1),
            (2, -4, 6),
        ):
            result = check.cubic_norm_decomposition(d)
            self.assertEqual(
                result["direct"],
                result["six_times_coordinate_norm"]
                + result["sum_of_three_squares"],
            )

    def test_odd_signed_imbalance_floor(self) -> None:
        rows = check.signed_imbalances((7, 7, 7), require_zero_sum=False)
        self.assertEqual(rows[0][0], 18)
        self.assertTrue(all(all(value % 2 for value in d) for _, d in rows))

    def test_zero_sum_signed_imbalances(self) -> None:
        rows = check.signed_imbalances((7, 7, 7), require_zero_sum=True)
        self.assertEqual(len(rows), 8)
        self.assertEqual(rows[0], (18, (-1, -1, 1)))
        self.assertEqual(rows[1], (18, (1, 1, -1)))
        for norm, (d1, d2, d3) in rows:
            self.assertEqual(d1, d2)
            self.assertEqual(d1, -d3)
            self.assertEqual(norm, 18 * d1 * d1)

    def test_general_a2_floor(self) -> None:
        result = check.prove_a2_cubic_floor()
        self.assertEqual(result["root_line_counts"], [7, 7, 7])
        self.assertEqual(result["minimum_pure_A2_cubic_norm_squared"], 18)


class FrameAndTensorTests(unittest.TestCase):
    def test_endpoint_histogram_and_moments(self) -> None:
        result = check.validate_endpoint_histogram()
        self.assertEqual(sum(result["ordered_entry_histogram"].values()), 231**2)
        self.assertEqual(
            result["ordered_entry_histogram"],
            {"4": 231, "1": 5092, "0": 44322, "-1": 1416, "-2": 2300},
        )
        self.assertEqual(
            result["moments"],
            {"1": 0, "2": 19404, "3": 60, "4": 102444},
        )

    def test_ordered_histogram_mutation_is_rejected(self) -> None:
        mutated = check.endpoint_histogram()
        mutated[-1] -= 2
        mutated[0] += 2
        with self.assertRaises(AssertionError):
            check.validate_endpoint_histogram(mutated)

    def test_tensor_bridge_has_active_schur_factorization(self) -> None:
        bridge = check.tensor_bridge()
        self.assertEqual(bridge["schur_square"], "W=M o M")
        self.assertIn("Phi^*Phi", bridge["orthogonal_schur_gram"])
        self.assertIn(">=||proj_", bridge["block_inequality"])

    def test_explicit_survivor_is_refuted_only_as_full_origin(self) -> None:
        result = check.evaluate_explicit_survivor()
        self.assertEqual(
            result["explicit_survivor_full_projector_schur_origin"],
            "REFUTED",
        )
        self.assertEqual(result["two_A2_total_compression_floor"], 36)
        for block in result["explicit_blocks"]:
            self.assertEqual(block["trace_of_K_compression"], 10)
            self.assertEqual(block["required_pure_cubic_norm_squared_floor"], 18)
            self.assertEqual(block["gap"], 8)
        guard = result["scope_guard"]
        self.assertTrue(guard["explicit_coordinate_lattice_relaxation_still_valid"])
        self.assertFalse(guard["all_h_equals_9_packages_excluded"])
        self.assertFalse(guard["n3_equals_708_excluded"])


class HostileAndSerializationTests(unittest.TestCase):
    def test_hostile_controls(self) -> None:
        controls = check.hostile_controls()
        self.assertEqual(
            controls["scale_18_even_line_counts"][
                "zero_sum_minimum_cubic_norm_squared"
            ],
            0,
        )
        self.assertEqual(
            controls["double_Q_block"]["status"],
            "TRACE_CONTRADICTION_CORRECTLY_DISAPPEARS",
        )
        self.assertEqual(
            controls["ordered_histogram_mutation"]["status"],
            "DETECTED",
        )
        self.assertTrue(
            controls["replace_A2_by_diagonal_even_gram"][
                "norm_four_vectors_exist"
            ]
        )

    def test_wrong_certificate_block_is_rejected_by_local_logic(self) -> None:
        # A direct unit-level hostile mutation: A2^2 has trace ten, while
        # changing one diagonal changes that exact invariant.
        wrong_q = [[3, -1], [-1, 2]]
        wrong_trace = check.trace(check.matmul([list(row) for row in check.A2], wrong_q))
        self.assertNotEqual(wrong_trace, 10)

    def test_build_results_is_deterministic_and_json_safe(self) -> None:
        first = check.build_results()
        second = check.build_results()
        self.assertEqual(first, second)
        encoded = check.canonical_json(first)
        self.assertEqual(json.loads(encoded), first)
        self.assertTrue(encoded.endswith("\n"))
        self.assertEqual(encoded, check.canonical_json(first))

    def test_written_output_is_byte_identical(self) -> None:
        payload = check.build_results()
        with tempfile.TemporaryDirectory() as temp:
            one = Path(temp) / "one.json"
            two = Path(temp) / "two.json"
            check.write_results(one, payload)
            check.write_results(two, payload)
            self.assertEqual(one.read_bytes(), two.read_bytes())
            self.assertEqual(
                hashlib.sha256(one.read_bytes()).hexdigest(),
                hashlib.sha256(two.read_bytes()).hexdigest(),
            )

    def test_result_scope_does_not_inflate_status(self) -> None:
        claim = check.build_results()["claim"]
        self.assertEqual(claim["label"], "DERIVED")
        self.assertEqual(claim["endpoint_status"], "UNKNOWN")
        self.assertEqual(claim["novelty_status"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
