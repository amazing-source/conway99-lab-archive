#!/usr/bin/env python3
"""Regression and mutation tests for the Wave 11 rooted-flower replay."""

from __future__ import annotations

import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
AUDIT_DIR = ROOT / "n3-39-equality"
CERTIFICATE_PATH = Path(
    os.environ.get("N3_39_CERTIFICATE", str(AUDIT_DIR / "n3-39-local.json"))
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PRIMARY = load_module("n3_39_local_primary", AUDIT_DIR / "audit_local.py")
INDEPENDENT = load_module("n3_39_local_independent", AUDIT_DIR / "verify_local.py")


class N339LocalReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = json.loads(CERTIFICATE_PATH.read_text(encoding="utf-8"))
        cls.replay = INDEPENDENT.replay(CERTIFICATE_PATH)

    def test_certificate_scope_and_status(self) -> None:
        self.assertEqual(self.certificate["schema"], "conditional-n3-39-local-replay-v1")
        self.assertEqual(self.certificate["claim_label"], "UNKNOWN")
        self.assertEqual(self.certificate["conclusion"]["target_result"], "UNKNOWN")
        self.assertIn(
            "K_is_simple_complement_of_L_on_distinct_active_triangles",
            self.certificate["premises"],
        )
        self.assertIn(
            "every_active_point_set_is_a_clique_in_K",
            self.certificate["premises"],
        )

    def test_primary_regeneration_is_exact(self) -> None:
        regenerated = PRIMARY.build_certificate(self.certificate["git_commit"])
        self.assertEqual(regenerated, self.certificate)
        self.assertEqual(regenerated["combined"]["records"], 8_907)
        self.assertEqual(
            regenerated["combined"]["sha256"],
            "452850018ad13362694f5bfff2e4beac03288a113a0391c3456a47cd6fbfe9a1",
        )

    def test_stream_domain_counts(self) -> None:
        streams = {item["name"]: item for item in self.certificate["streams"]}
        self.assertEqual(streams["premises.jsonl"]["records"], 1)
        self.assertEqual(streams["crossing_matrices.jsonl"]["records"], 682)
        self.assertEqual(streams["collision_pairs.jsonl"]["records"], 1_546)
        self.assertEqual(streams["root4_profiles.jsonl"]["records"], 6_561)
        self.assertEqual(streams["root3_profiles.jsonl"]["records"], 64)

    def test_independent_replay_and_mutations(self) -> None:
        self.assertEqual(self.replay["status"], "PASS independent n3=39 local replay")
        self.assertEqual(
            self.replay["mutations_rejected"],
            [
                "drop_stream",
                "alter_combined_digest",
                "drop_complement_bridge",
                "drop_common_point_premise",
                "drop_point_clique_premise",
                "drop_crossing_degree_premise",
                "restore_false_survivor",
                "inflate_target_status",
            ],
        )

    def test_semantic_mutation_fixtures(self) -> None:
        checks = self.replay["semantic_checks"]
        self.assertEqual(checks["collision_histogram"], {"linearity": 90, "common_point": 1_456})
        self.assertEqual(checks["size4_feasible_budget_9_10"], [9, 45])
        self.assertEqual(checks["singleton_mask3_one_sided_two_sided"], [True, False])
        self.assertEqual(checks["complement_224_root_degree_with_without"], [7, 3])
        self.assertEqual(
            checks["common_point_disabled_collision_owner_survivors"],
            [1_456, 36],
        )
        self.assertEqual(
            checks["raw_root3_classes"],
            {"has_233": 56, "all_333": 1, "has_223_no_233": 7},
        )
        self.assertEqual(checks["old_root3_formula_differences"], 50)
        self.assertEqual(
            checks["root3_fixture_forced_u"],
            {
                "2-2-2-2-2-3": [3, 3, 4],
                "2-2-2-2-3-3": [2, 2, 4],
                "2-2-3-3-3-3": [0, 2, 2],
                "2-2-2-2-2-2": [4, 4, 4],
                "3-3-3-3-3-3": [0, 0, 0],
            },
        )
        self.assertEqual(
            checks["root3_rejection_histogram"],
            {"external_capacity": 7, "type_233_U_degree": 50, "root_U_degree": 7},
        )
        self.assertEqual(checks["root4_rejection_histogram"], {"external_capacity": 6_552, "K_degree": 9})
        self.assertEqual(checks["root4_degree_histogram"], {"capacity": 6_552, "10": 8, "11": 1})
        self.assertEqual(checks["root3_root4_crossing_extensions"], [917, 33])

    def test_optional_jsonl_dump_matches_certificate(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            dump_dir = Path(temporary)
            rebuilt = PRIMARY.build_certificate(self.certificate["git_commit"], dump_dir)
            self.assertEqual(rebuilt, self.certificate)
            self.assertEqual(
                sum((dump_dir / item["name"]).stat().st_size for item in rebuilt["streams"]),
                rebuilt["combined"]["bytes"],
            )

    def test_certificate_writer_is_canonical_lf(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "certificate.json"
            PRIMARY.write_certificate(path, self.certificate)
            payload = path.read_bytes()
            self.assertTrue(payload.endswith(b"\n"))
            self.assertNotIn(b"\r\n", payload)
            self.assertEqual(json.loads(payload), self.certificate)


if __name__ == "__main__":
    unittest.main()
