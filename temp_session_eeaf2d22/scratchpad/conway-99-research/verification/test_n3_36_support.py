#!/usr/bin/env python3
"""Regression and mutation tests for the Wave 10 support census."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
AUDIT_DIR = ROOT / "n3-36-equality"
CERTIFICATE_PATH = AUDIT_DIR / "n3-36-support.json"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PRIMARY = load_module("n3_36_support_primary", AUDIT_DIR / "audit_support.py")
INDEPENDENT = load_module("n3_36_support_independent", AUDIT_DIR / "verify_support.py")


class N336SupportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = json.loads(CERTIFICATE_PATH.read_text(encoding="utf-8"))
        cls.primary_masks, cls.primary_statistics = PRIMARY.enumerate_support_masks()
        cls.replay = INDEPENDENT.replay(CERTIFICATE_PATH)

    def test_certificate_scope_and_provenance(self) -> None:
        self.assertEqual(self.certificate["schema"], "conditional-n3-36-support-audit-v1")
        self.assertEqual(
            self.certificate["git_commit"],
            "2194c2b68ebd5c34491d64f15d30f1a3597baa74",
        )
        self.assertEqual(self.certificate["conclusion"]["target_result"], "UNKNOWN")

    def test_primary_support_census(self) -> None:
        self.assertEqual(len(self.primary_masks), 216)
        self.assertEqual(self.primary_statistics["eligible_first_permutations"], 230_112)
        self.assertEqual(self.primary_statistics["accepted_ordered_decompositions"], 3_456)
        self.assertEqual(
            PRIMARY.canonical_sha256(self.primary_masks),
            "6659fe1972cbacc6980a9792557714730572817b43224b5f1fac24bb0c4ca61a",
        )

    def test_resource_and_point_domains(self) -> None:
        profiles = PRIMARY.point_resource_profiles()
        families = PRIMARY.labeled_point_families()
        self.assertEqual(len(profiles), 14)
        self.assertEqual(len(families), 100)
        self.assertEqual(
            PRIMARY.canonical_sha256(families),
            "0f8da9cfa889f8e012fc6623e727df968c91341ebd65a63e160714dbc46722b9",
        )

    def test_every_abstract_support_fails_rook_saturation(self) -> None:
        diagnostics = {PRIMARY.validate_support(mask) for mask in self.primary_masks}
        self.assertEqual(diagnostics, {(True, 18, 0, 18)})
        self.assertEqual(
            self.certificate["abstract_support"]["survivors_after_original_SRG_saturation"],
            0,
        )

    def test_independent_recursive_replay(self) -> None:
        self.assertEqual(self.replay["status"], "PASS independent n3=36 support replay")
        self.assertEqual(self.replay["support_search"]["unique_support_masks"], 216)
        self.assertEqual(self.replay["final_survivors"], 0)
        self.assertEqual(self.replay["target_result"], "UNKNOWN")

    def test_mutations_are_rejected(self) -> None:
        self.assertEqual(
            self.replay["mutations_rejected"],
            [
                "drop_support",
                "alter_support_digest",
                "restore_false_survivor",
                "alter_rook_mu",
                "inflate_target_status",
            ],
        )


if __name__ == "__main__":
    unittest.main()
