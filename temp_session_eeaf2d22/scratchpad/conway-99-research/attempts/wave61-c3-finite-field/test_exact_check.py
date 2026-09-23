#!/usr/bin/env python3
"""Focused unit and regression tests for the Wave 61 checker."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave61_exact_check", HERE / "exact_check.py"
)
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class Wave61Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        CHECK.check_frozen_inputs()
        cls.types = CHECK.load_types()

    def test_frozen_component_census_shape(self) -> None:
        self.assertEqual(len(self.types), 18)
        for record in self.types:
            rows = CHECK.local_rows(record)
            self.assertEqual({row.bit_count() for row in rows}, {3})
            gram = CHECK.local_gram(record)
            self.assertEqual([gram[i][i] for i in range(12)], [10] * 12)
            self.assertEqual(
                sum(gram[i][j] for i in range(12) for j in range(i + 1, 12)),
                60,
            )

    def test_partition_indicators_have_one_relation(self) -> None:
        indicators = CHECK.parity_indicators()
        self.assertEqual(len(indicators), 6)
        self.assertEqual(CHECK.bit_span_rank(indicators), 5)
        gram = CHECK.target_gram(
            [self.types[0], self.types[7], self.types[17]]
        )
        for indicator in indicators:
            self.assertEqual(
                CHECK.matrix_times_mask_f2(gram, indicator), 0
            )
            self.assertEqual(
                CHECK.half_weight_quadratic(gram, indicator), 0
            )

    def test_odd_congruence_handles_zero_diagonal_hyperbolic_block(self) -> None:
        hyperbolic = ((0, 1), (1, 0))
        for prime in CHECK.PRIMES:
            invariant = CHECK.odd_form_invariants(hyperbolic, prime)
            self.assertEqual(invariant["rank"], 2)
            expected_legendre = (
                1
                if pow((-1) % prime, (prime - 1) // 2, prime) == 1
                else -1
            )
            self.assertEqual(
                invariant["discriminant_legendre"], expected_legendre
            )
            self.assertEqual(invariant["anisotropic_dimension"], 0)

    def test_full_pair_filter_strictly_extends_local_coordinates(self) -> None:
        selected = [self.types[0], self.types[0], self.types[0]]
        gram = CHECK.target_gram(selected)
        result = CHECK.pair_inventory_parity_filter(selected, gram)
        self.assertTrue(result["local_198_rhs_consistent"])
        self.assertTrue(result["full_630_rhs_consistent"])
        self.assertEqual(result["local_198_rank"], 140)
        self.assertEqual(result["full_630_rank"], 438)
        self.assertGreater(
            result["candidate_count_before_exact_multiplicities"], 0
        )

    def test_component_patterns_and_cubic_margins(self) -> None:
        self.assertEqual(len(CHECK.PROFILE_TRIPLES), 21)
        images = []
        for triple in CHECK.PROFILE_TRIPLES:
            mask = 0
            for component, profile_index in enumerate(triple):
                for fibre, count in enumerate(
                    CHECK.PROFILE_VALUES[profile_index]
                ):
                    if count & 1:
                        mask |= 1 << (3 * component + fibre)
            images.append(mask)
        self.assertEqual(len(set(images)), 16)
        self.assertEqual(
            {weight: sum(value.bit_count() == weight for value in images)
             for weight in (0, 4, 6)},
            {0: 6, 4: 9, 6: 6},
        )
        gram = CHECK.target_gram(
            [self.types[2], self.types[9], self.types[16]]
        )
        cubic = CHECK.cubic_moment_boundary(gram)
        self.assertTrue(cubic["identity_consistent"])
        self.assertFalse(cubic["obstruction_found"])
        self.assertEqual(cubic["derived_triples_through_each_row"], 100)
        self.assertEqual(cubic["derived_total_triple_incidence"], 1200)

    def test_saved_census_regression(self) -> None:
        saved = json.loads(
            (HERE / "exact-results.json").read_text(encoding="utf-8")
        )
        census = saved["triple_census"]
        self.assertEqual(
            census["rank_F2_G_histogram"],
            {"14": 67, "16": 415, "18": 412,
             "20": 185, "22": 51, "24": 10},
        )
        self.assertEqual(
            census["full_pair_inventory_F2_consistency"], {"true": 1140}
        )
        self.assertEqual(
            saved["disposition"][
                "triples_eliminated_by_full_pair_inventory_F2"
            ],
            0,
        )
        self.assertEqual(saved["disposition"]["endpoint_status"], "UNKNOWN")

    def test_countercontrols(self) -> None:
        controls = CHECK.small_countermodels()
        self.assertEqual(controls["rank_equality_false"]["rank_B"], 2)
        self.assertEqual(controls["rank_equality_false"]["rank_BBt"], 0)


if __name__ == "__main__":
    unittest.main()
