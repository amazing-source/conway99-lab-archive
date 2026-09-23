#!/usr/bin/env python3
"""Hostile and regression tests for the independent Wave 61 verifier."""

from __future__ import annotations

import copy
import importlib.util
import json
import math
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave61_independent", HERE / "independent_check.py"
)
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class IndependentWave61Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        CHECK.require_headroom()
        CHECK.verify_frozen_inputs()
        cls.types = CHECK.load_and_validate_types()

    def test_component_and_triple_census(self) -> None:
        self.assertEqual(len(self.types), 18)
        self.assertEqual(
            len(list(__import__("itertools").combinations_with_replacement(
                range(18), 3
            ))),
            1140,
        )

    def test_hostile_component_edge_deletion_is_rejected(self) -> None:
        mutant = copy.deepcopy(self.types[0])
        mutant["edges"].pop()
        with self.assertRaises(AssertionError):
            CHECK.validate_component(mutant)

    def test_partition_indicators_and_alternating_form(self) -> None:
        gram = CHECK.target_gram(
            [self.types[0], self.types[7], self.types[17]]
        )
        data = CHECK.binary_form_data(gram)
        self.assertEqual(len(CHECK.partition_indicators()), 6)
        self.assertEqual(
            len(CHECK.binary_basis(CHECK.partition_indicators())), 5
        )
        self.assertEqual(data["rank"] % 2, 0)
        self.assertLessEqual(data["rank"], 30)
        self.assertGreaterEqual(data["even_ambient_adjusted_slack"], 0)

    def test_odd_prime_congruence_on_hyperbolic_plane(self) -> None:
        matrix = ((0, 1), (1, 0))
        for prime in CHECK.ODD_PRIMES:
            rank, legendre, anisotropic = CHECK.congruence_invariants(
                matrix, prime
            )
            self.assertEqual(rank, 2)
            expected = (
                1
                if pow((-1) % prime, (prime - 1) // 2, prime) == 1
                else -1
            )
            self.assertEqual(legendre, expected)
            self.assertEqual(anisotropic, 0)

    def test_even_weight_gauss_sum_has_minus_type(self) -> None:
        gauss_sum = sum(
            math.comb(60, weight) * (-1) ** (weight // 2)
            for weight in range(0, 61, 2)
        )
        self.assertEqual(gauss_sum, -(1 << 30))

    def test_patterns_are_complete_and_moment_rank_is_eleven(self) -> None:
        self.assertEqual(len(CHECK.PATTERNS), 21)
        images = {value ^ (1 << 81) for value in CHECK.PATTERN_VECTORS}
        self.assertEqual(len(images), 16)
        self.assertEqual(
            CHECK.PATTERN_WEIGHTS,
            __import__("collections").Counter({0: 6, 4: 9, 6: 6}),
        )
        self.assertEqual(len(CHECK.PATTERN_BASIS), 11)

    def test_pair_inventory_and_hostile_rhs_mutation(self) -> None:
        chosen = [self.types[0], self.types[0], self.types[0]]
        gram = CHECK.target_gram(chosen)
        data = CHECK.pair_inventory_data(chosen, gram)
        self.assertEqual(data["candidate_count"], 15936)
        self.assertEqual(data["local_rank"], 140)
        self.assertEqual(data["full_rank"], 438)
        self.assertTrue(data["local_consistent"])
        self.assertTrue(data["full_consistent"])
        local_bad = next(
            bit
            for bit in range(198)
            if not CHECK.in_binary_span(data["_local_basis"], 1 << bit)
        )
        full_bad = next(
            bit
            for bit in range(630)
            if not CHECK.in_binary_span(data["_full_basis"], 1 << bit)
        )
        self.assertFalse(
            CHECK.in_binary_span(
                data["_local_basis"], data["_local_rhs"] ^ (1 << local_bad)
            )
        )
        self.assertFalse(
            CHECK.in_binary_span(
                data["_full_basis"], data["_full_rhs"] ^ (1 << full_bad)
            )
        )

    def test_pattern_hostile_rhs_mutation(self) -> None:
        gram = CHECK.target_gram(
            [self.types[2], self.types[9], self.types[16]]
        )
        target = CHECK.pattern_target(gram)
        self.assertTrue(CHECK.in_binary_span(CHECK.PATTERN_BASIS, target))
        bad = next(
            bit
            for bit in range(82)
            if not CHECK.in_binary_span(CHECK.PATTERN_BASIS, 1 << bit)
        )
        self.assertFalse(
            CHECK.in_binary_span(CHECK.PATTERN_BASIS, target ^ (1 << bad))
        )

    def test_cubic_claim_is_margin_only(self) -> None:
        gram = CHECK.target_gram(
            [self.types[1], self.types[10], self.types[17]]
        )
        cubic = CHECK.cubic_data(gram)
        self.assertEqual(cubic["triples_through_each_row"], 100)
        self.assertEqual(cubic["total_triple_incidence"], 1200)
        self.assertFalse(cubic["tensor_feasibility_tested"])

    def test_frozen_byte_mutation_is_detected_by_hash(self) -> None:
        original = b"frozen bytes"
        changed = b"frozen byteS"
        self.assertNotEqual(
            __import__("hashlib").sha256(original).hexdigest(),
            __import__("hashlib").sha256(changed).hexdigest(),
        )

    def test_saved_result_boundary_when_present(self) -> None:
        path = HERE / "independent-results.json"
        if not path.exists():
            self.skipTest("full independent result is still running")
        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(payload["claim_label"], "VERIFIED")
        self.assertEqual(payload["verdict"], "VERIFIED_WITH_CORRECTION")
        self.assertEqual(
            payload["component_and_triple_reconstruction"][
                "unordered_triples_with_repetition"
            ],
            1140,
        )
        self.assertEqual(
            payload["pair_inventory_F2"]["full_eliminated_targets"], 0
        )
        self.assertEqual(
            payload["status_boundary"]["endpoint_status"], "UNKNOWN"
        )


if __name__ == "__main__":
    unittest.main()
