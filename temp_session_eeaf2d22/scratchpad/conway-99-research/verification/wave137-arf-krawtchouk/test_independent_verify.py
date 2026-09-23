"""Hostile tests for the clean-room Wave137 verifier."""

from __future__ import annotations

import copy
import json
import unittest
from fractions import Fraction
from pathlib import Path

import independent_verify as verify


ROOT = Path(__file__).resolve().parents[2]
DISCOVERY = ROOT / "attempts/wave137-z4-arf-branches"


class Wave137CleanRoomTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plus_path = DISCOVERY / "binary-shadow1-plus.json"
        cls.plus_payload = json.loads(
            cls.plus_path.read_text(encoding="utf-8")
        )

    def test_signed_constants_t0_t4_are_reconstructed(self) -> None:
        result = verify.independent_constant_derivation()
        self.assertEqual(
            result["derived_constants_t0_t4"],
            {
                "0": 1,
                "1": -99,
                "2": 3465,
                "3": -56595,
                "4": 462924,
            },
        )
        self.assertEqual(result["frozen_exact_t5"], -1821204)

    def test_each_signed_row_raises_rank_once(self) -> None:
        result = verify.ordinary_model_ranks()
        self.assertEqual(result["ordinary_equality_rank"], 16)
        self.assertEqual(
            [
                row["rank"]
                for row in result["cumulative_signed_ranks"]
            ],
            [17, 18, 19, 20, 21, 22],
        )
        for row in result["cumulative_signed_ranks"]:
            self.assertEqual(row["rank_increment"], 1)
            self.assertEqual(row["rank"], row["augmented_rank_plus"])
            self.assertEqual(row["rank"], row["augmented_rank_minus"])

    def test_all_fourteen_exact_witnesses_replay(self) -> None:
        paths = verify.find_exact_witnesses(DISCOVERY)
        self.assertEqual(len(paths), 14)
        self.assertTrue(all(verify.audit_witness(path)["pass"] for path in paths))

    def test_terminal_plus_replays_every_signed_row(self) -> None:
        result = verify.audit_witness(self.plus_path)
        self.assertTrue(result["pass"])
        signed = result["signed_krawtchouk"]
        self.assertEqual(signed["epsilon"], 1)
        self.assertEqual(signed["max_moment"], 5)
        self.assertTrue(all(row["pass"] for row in signed["rows"].values()))
        self.assertEqual(set(signed["shadow_rows"]), {"6", "93"})
        self.assertTrue(
            all(row["pass"] for row in signed["shadow_rows"].values())
        )
        self.assertTrue(
            signed["all_shadow_degrees_6_through_99_checked"]
        )
        self.assertFalse(signed["all_shadow_violations"])

    def test_ordinary_mutation_is_caught(self) -> None:
        image, dual = verify.coefficient_arrays(self.plus_payload)
        image[0] += 1
        result = verify.audit_ordinary(image, dual)
        self.assertFalse(result["pass"])
        self.assertIn("A_0 != 1", result["failures"])

    def test_signed_branch_mutation_is_caught(self) -> None:
        image, dual = verify.coefficient_arrays(self.plus_payload)
        image[14] += 1
        result = verify.audit_signed_rows(
            image, dual, self.plus_payload
        )
        self.assertFalse(result["pass"])

    def test_split_mutation_is_caught(self) -> None:
        payload = copy.deepcopy(self.plus_payload)
        system = payload["split_enumerators"]["image_vs_neighborhood"]
        shell = next(weight for weight in system if weight != "0")
        level = next(iter(system[shell]))
        system[shell][level] = str(
            Fraction(system[shell][level]) + 1
        )
        image, dual = verify.coefficient_arrays(payload)
        result = verify.audit_split_systems(payload, image, dual)
        self.assertFalse(result["pass"])

    def test_pair_table_mutation_is_caught(self) -> None:
        payload = copy.deepcopy(self.plus_payload)
        payload["distinguished_pair_tables"][
            "image_neighborhood_rows"
        ]["ordered_distinct"]["intersection_1"] += 1
        self.assertFalse(verify.audit_pair_tables(payload)["pass"])

    def test_manifest_replays(self) -> None:
        result = verify.audit_discovery_manifest(DISCOVERY)
        self.assertTrue(result["pass"])
        self.assertEqual(result["entry_count"], 33)
        self.assertEqual(
            result["manifest_sha256"],
            "2175aad6a21216db67b668a3450855592405f584f2490c58b1d21ce6983da02c",
        )

    def test_z4_numerical_status_is_not_evidence(self) -> None:
        result = verify.audit_z4_outputs(DISCOVERY)
        self.assertFalse(result["mathematical_inference_from_numerical_status"])
        self.assertFalse(result["exact_z4_branch_certificate_found"])
        self.assertEqual(len(result["artifacts"]), 4)

    def test_full_verification_preserves_unknown_status(self) -> None:
        result = verify.verify(DISCOVERY)
        self.assertEqual(result["claim_label"], "VERIFIED")
        self.assertFalse(result["failures"])
        self.assertEqual(result["status"]["Conway_99"], "UNKNOWN")
        self.assertFalse(result["status"]["binary_code_constructed"])
        self.assertFalse(result["status"]["graph_constructed"])


if __name__ == "__main__":
    unittest.main()
