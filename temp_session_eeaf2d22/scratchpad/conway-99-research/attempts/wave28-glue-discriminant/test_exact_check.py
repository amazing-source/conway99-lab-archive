#!/usr/bin/env python3

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import exact_check as check


class Wave28GlueDiscriminantTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = check.build_results()

    def test_01_frozen_inputs(self) -> None:
        self.assertEqual(
            self.payload["public_head"],
            "d76d030f6d74e2e1b7ca2b2f0f97536241b3a10b",
        )
        self.assertEqual(
            self.payload["frozen_inputs"],
            check.INPUT_HASHES,
        )

    def test_02_eight_determinant_rows_and_exact_levels(self) -> None:
        expected = {
            9: (2, 0, 3),
            21: (1, 1, 21),
            49: (0, 2, 7),
            81: (4, 0, 3),
            189: (3, 1, 21),
            441: (2, 2, 21),
            729: (6, 0, 3),
            1029: (1, 3, 21),
        }
        for h, (u, v, level) in expected.items():
            self.assertEqual(check.exponents(h), (u, v))
            self.assertEqual(check.radical_level(h), level)

    def test_03_legendre_controls(self) -> None:
        self.assertEqual(check.legendre(1, 3), 1)
        self.assertEqual(check.legendre(2, 3), -1)
        self.assertEqual(check.legendre(2, 7), 1)
        self.assertEqual(check.legendre(3, 7), -1)

    def test_04_milgram_sign_formula(self) -> None:
        expected = {
            9: 1,
            21: 1,
            49: 1,
            81: -1,
            189: -1,
            441: -1,
            729: 1,
            1029: -1,
        }
        for h, sign in expected.items():
            self.assertEqual(
                check.required_delta_product(*check.exponents(h)),
                sign,
            )

    def test_05_exactly_twelve_discriminant_forms(self) -> None:
        rows = self.payload["discriminant_form_census"]["rows"]
        self.assertEqual(len(rows), 12)
        counts: dict[int, int] = {}
        for row in rows:
            counts[row["h"]] = counts.get(row["h"], 0) + 1
        self.assertEqual(
            counts,
            {9: 1, 21: 2, 49: 1, 81: 1, 189: 2, 441: 2, 729: 1, 1029: 2},
        )

    def test_05b_hostile_eleven_count_is_rejected(self) -> None:
        census = self.payload["discriminant_form_census"]
        self.assertEqual(census["correction"]["rejected_count"], 11)
        self.assertNotEqual(census["count"], census["correction"]["rejected_count"])
        pure_rows = (9, 49, 81, 729)
        mixed_rows = (21, 189, 441, 1029)
        rows = census["rows"]
        self.assertEqual(sum(row["h"] in pure_rows for row in rows), 4)
        self.assertEqual(sum(row["h"] in mixed_rows for row in rows), 8)
        self.assertIn("exactly these twelve", census["theorem"])
        self.assertNotIn("exactly these eleven", census["theorem"])

    def test_06_every_gauss_phase_is_signature_44(self) -> None:
        for row in self.payload["discriminant_form_census"]["rows"]:
            self.assertEqual(
                row["milgram_phase"],
                {"real": -1, "imaginary": 0},
            )

    def test_07_scaled_dual_dimensions_and_signs(self) -> None:
        for row in self.payload["discriminant_form_census"]["rows"]:
            u, v = row["v3_h"], row["v7_h"]
            self.assertEqual(row["rank_mod_3_S"] + row["rank_mod_3_G"], 44)
            self.assertEqual(row["rank_mod_7_S"] + row["rank_mod_7_G"], 44)
            self.assertEqual(row["A_S"]["delta_3"], row["A_G"]["delta_3"])
            self.assertEqual(row["A_S"]["delta_7"], row["A_G"]["delta_7"])
            self.assertEqual(check.scaled_dual_delta_ratio(3, u, v), 1)
            self.assertEqual(check.scaled_dual_delta_ratio(7, u, v), 1)

    def test_08_single_root_glue_wall(self) -> None:
        glue = self.payload["single_root_glue"]
        self.assertTrue(glue["root_is_primitive"])
        self.assertEqual(glue["root_divisibility"], 1)
        self.assertFalse(glue["orthogonal_A1_summand"])
        self.assertEqual(glue["index_of_A1_plus_complement"], 2)
        self.assertEqual(glue["complement_2_primary_form"], "<-1/2>")
        reduction = self.payload["root_sublattice_reduction"]
        self.assertIn("graph of an anti-isometry", reduction["H1"])
        self.assertIn(
            "p-adic determinant valuations agree",
            reduction["prime_to_21_cancellation"],
        )

    def test_09_root_distribution_counts_and_identities(self) -> None:
        all_rows = check.root_projection_distributions(False)
        filtered = check.root_projection_distributions(True)
        self.assertEqual(len(all_rows), 46)
        self.assertEqual(len(filtered), 32)
        for row in filtered:
            total = (
                2 * row["plus_2"]
                + row["plus_1"]
                - row["minus_1"]
                - 2 * row["minus_2"]
            )
            norm = (
                4 * row["plus_2"]
                + row["plus_1"]
                + row["minus_1"]
                + 4 * row["minus_2"]
            )
            self.assertEqual(total, 0)
            self.assertEqual(norm, 42)
            self.assertLessEqual(abs(row["plus_2"] - row["minus_2"]), 3)

    def test_10_surviving_hostile_control(self) -> None:
        row = self.payload["single_root_projector_image"][
            "surviving_hostile_control"
        ]
        self.assertEqual(
            (
                row["plus_2"],
                row["plus_1"],
                row["zero"],
                row["minus_1"],
                row["minus_2"],
            ),
            (0, 21, 189, 21, 0),
        )
        self.assertEqual(row["pure_line_cubic_energy"], "0/1")

    def test_11_active_cubic_rejection(self) -> None:
        mutation = self.payload["single_root_projector_image"][
            "active_rejected_mutation"
        ]
        self.assertEqual(mutation["coordinate_sum"], 0)
        self.assertEqual(mutation["squared_norm"], 42)
        self.assertEqual(mutation["pure_line_cubic_energy"], "72/1")

    def test_12_deterministic_lf_json_and_scope(self) -> None:
        rendered = check.canonical_json(self.payload)
        self.assertNotIn("\r", rendered)
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "result.json"
            target.write_text(rendered, encoding="utf-8", newline="\n")
            replay = json.loads(target.read_text(encoding="utf-8"))
        self.assertEqual(replay, self.payload)
        scope = replay["scope"]
        self.assertEqual(scope["excluded_h_rows"], [])
        self.assertEqual(scope["general_even_rank_44_forms"], "UNKNOWN")
        self.assertEqual(scope["n3_708"], "UNKNOWN")
        self.assertEqual(scope["Conway_99"], "UNKNOWN")
        self.assertEqual(scope["novelty"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main(verbosity=2)
