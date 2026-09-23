#!/usr/bin/env python3
"""Focused regression and mutation tests for Wave 14 proof-A artifacts."""

from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import build_all2_countermodel as builder
import profile_modes
import verify_all2_countermodel as validator


class ProfileTests(unittest.TestCase):
    def test_exact_profile_counts(self):
        raw, degree_feasible, surviving = profile_modes.active_profiles()
        self.assertEqual(len(raw), 12)
        self.assertEqual(len(degree_feasible), 4)
        self.assertEqual(len(surviving), 3)

    def test_surviving_profiles(self):
        _raw, _degree_feasible, surviving = profile_modes.active_profiles()
        self.assertEqual(
            {(r, q) for r, q, _dk in surviving},
            {
                (14, (2,) * 10 + (3,) * 4),
                (15, (2,) * 13 + (3,) * 2),
                (16, (2,) * 16),
            },
        )

    def test_special_r15_size_three_modes_absent(self):
        self.assertEqual(
            profile_modes.local_modes((5, 8, 8), (3, 2, 2)),
            [],
        )
        self.assertEqual(
            profile_modes.local_modes((5, 5, 8), (3, 3, 2)),
            [],
        )

    def test_r16_local_mode_count(self):
        states = profile_modes.local_modes((9, 9, 9), (2, 2, 2))
        canonical = profile_modes.canonical_modes(states, ("O", "O", "O"))
        self.assertEqual(len(states), 32)
        self.assertEqual(len(canonical), 10)

    def test_crossing_sizes(self):
        self.assertEqual(profile_modes.crossing_sizes(1, 3), (0,))
        self.assertEqual(profile_modes.crossing_sizes(2, 3), (0, 4))
        self.assertEqual(profile_modes.crossing_sizes(3, 3), (0, 4, 6))


class CountermodelTests(unittest.TestCase):
    def write_and_verify(self, data):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "candidate.json"
            path.write_text(
                json.dumps(data, sort_keys=True) + "\n",
                encoding="utf-8",
                newline="\n",
            )
            return validator.verify(path)

    def test_countermodel_passes(self):
        result = self.write_and_verify(builder.build())
        self.assertEqual(result["status"], "PASS active-relaxation countermodel")
        self.assertEqual(result["H_edges"], 48)

    def test_l_edge_mutation_fails(self):
        data = builder.build()
        data["L_edges"][0] = data["K_edges"][0]
        with self.assertRaises(AssertionError):
            self.write_and_verify(data)

    def test_support_mutation_fails(self):
        data = builder.build()
        data["positive_support_point_pairs"][0] = [0, 1]
        with self.assertRaises(AssertionError):
            self.write_and_verify(data)

    def test_h_mutation_fails(self):
        data = builder.build()
        data["H_nonisolated_edges"][0] = [0, 1]
        with self.assertRaises(AssertionError):
            self.write_and_verify(data)

    def test_q_mutation_fails(self):
        data = builder.build()
        data["q_values"][0] = 3
        with self.assertRaises(AssertionError):
            self.write_and_verify(data)


if __name__ == "__main__":
    unittest.main(verbosity=2)
