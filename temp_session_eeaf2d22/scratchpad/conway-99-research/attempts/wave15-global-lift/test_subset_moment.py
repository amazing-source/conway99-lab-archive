#!/usr/bin/env python3
"""Focused tests for the Wave 15 global-lift obstruction."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent


def load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


builder = load_module("wave15_builder", "build_subset_moment_certificate.py")
verifier = load_module("wave15_verifier", "verify_subset_moment_certificate.py")


class SubsetMomentTests(unittest.TestCase):
    def write(self, payload: dict[str, object], directory: Path) -> Path:
        path = directory / "certificate.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def test_all_nine_point_size_profiles_have_negative_defect(self) -> None:
        rows = builder.size_profile_rows()
        self.assertEqual(len(rows), 9)
        self.assertEqual(
            [(row["x2"], row["x3"]) for row in rows],
            [(24, 0), (21, 2), (18, 4), (15, 6), (12, 8),
             (9, 10), (6, 12), (3, 14), (0, 16)],
        )
        self.assertTrue(all(row["defect_at_T0_U0"] < 0 for row in rows))
        self.assertTrue(all(row["T_coefficient"] < 0 for row in rows))
        self.assertTrue(
            all(
                row["spectral_min_degree_gap_numerator_over_99"] > 0
                for row in rows
            )
        )

    def test_minimum_six_is_the_critical_input(self) -> None:
        # At m=24 and baseline five, the same Cauchy expression is positive;
        # the proof must therefore retain the support-derived sixth neighbor.
        m = 24
        d = 5
        outside_square_sum = 2 * m * m + 12 * m - m * (d * d + d)
        outside_incidence_sum = (14 - d) * m
        defect = (99 - m) * outside_square_sum - outside_incidence_sum**2
        self.assertGreater(defect, 0)

    def test_hostile_srg_parameter_mutation_is_rejected(self) -> None:
        payload = builder.build(None)
        payload["srg_parameters"]["mu"] = 3
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(payload, Path(tmp))
            with self.assertRaises(AssertionError):
                verifier.verify(path)

    def test_hostile_degree_bound_mutation_is_rejected(self) -> None:
        payload = builder.build(None)
        payload["mandatory_internal_degree"]["lower_bound"] = 5
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(payload, Path(tmp))
            with self.assertRaises(AssertionError):
                verifier.verify(path)

    def test_hostile_defect_mutation_is_rejected(self) -> None:
        payload = builder.build(None)
        payload["size_profile_rows"][0]["defect_at_T0_U0"] += 1
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(payload, Path(tmp))
            with self.assertRaises(AssertionError):
                verifier.verify(path)


if __name__ == "__main__":
    unittest.main()
