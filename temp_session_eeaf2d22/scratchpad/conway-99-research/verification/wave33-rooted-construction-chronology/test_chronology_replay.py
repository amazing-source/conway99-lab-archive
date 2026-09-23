#!/usr/bin/env python3
"""Hostile tests for the isolated Wave 33 construction chronology replay."""

from __future__ import annotations

import ast
import copy
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import chronology_replay as chronology


def build_clean_source_fixture(source: Path, destination: Path) -> None:
    frozen = chronology.validate_frozen_packages(source)
    relative_paths = {
        "STRUCTURE.md",
        "verification/wave33-rooted-construction-candidate-freeze.sha256",
        "verification/wave33-rooted-construction/artifact-manifest.sha256",
    }
    relative_paths.update(frozen["candidate_entries"])
    relative_paths.update(
        "verification/wave33-rooted-construction/" + relative
        for relative in frozen["verifier_entries"]
    )
    destination.mkdir(parents=True)
    for relative in sorted(relative_paths):
        source_path = source.joinpath(*relative.split("/"))
        target_path = destination.joinpath(*relative.split("/"))
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_path, target_path)


class ChronologyReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.archive_bytes = chronology.ARCHIVE.read_bytes()
        cls.archive_value = json.loads(cls.archive_bytes)
        cls.archive_entries = chronology.decode_archive_bytes(cls.archive_bytes)
        cls.clean_source_directory = tempfile.TemporaryDirectory(
            prefix="wave33-clean-source-test-"
        )
        cls.clean_source_root = (
            Path(cls.clean_source_directory.name) / "clean-source"
        )
        build_clean_source_fixture(chronology.REPO, cls.clean_source_root)
        cls.materialized_directory = tempfile.TemporaryDirectory(
            prefix="wave33-chronology-test-"
        )
        cls.synthetic_root = (
            Path(cls.materialized_directory.name) / "historical-root"
        )
        chronology.materialize_historical_root(
            cls.synthetic_root,
            source_root=cls.clean_source_root,
        )
        with mock.patch.dict(
            os.environ,
            {
                "PYTHONPATH": str(cls.clean_source_root / "poison-pythonpath"),
                "VIRTUAL_ENV": str(cls.clean_source_root / ".venv"),
            },
        ):
            cls.replay_result = chronology.run_full_replay(
                source_root=cls.clean_source_root
            )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.materialized_directory.cleanup()
        cls.clean_source_directory.cleanup()

    def test_01_archive_build_is_byte_identical(self) -> None:
        rebuilt = chronology.canonical_json_bytes(
            chronology.build_archive_payload()
        )
        self.assertEqual(rebuilt, self.archive_bytes)
        self.assertEqual(
            chronology.sha256_bytes(rebuilt),
            chronology.EXPECTED_ARCHIVE_SHA256,
        )

    def test_02_archive_exact_path_hash_map(self) -> None:
        self.assertEqual(
            {
                path: chronology.sha256_bytes(data)
                for path, data in self.archive_entries.items()
            },
            chronology.HISTORICAL_INPUTS,
        )
        self.assertEqual(len(self.archive_entries), 8)

    def test_03_live_structure_drift_cannot_leak(self) -> None:
        live = chronology.sha256_path(chronology.REPO / "STRUCTURE.md")
        historical = chronology.sha256_path(
            self.synthetic_root / "STRUCTURE.md"
        )
        self.assertEqual(
            historical, chronology.HISTORICAL_STRUCTURE_SHA256
        )
        self.assertNotEqual(live, historical)

    def test_04_archive_byte_tamper_rejected(self) -> None:
        hostile = bytearray(self.archive_bytes)
        hostile[len(hostile) // 2] ^= 1
        with self.assertRaisesRegex(
            chronology.ChronologyError, "archive byte hash mismatch"
        ):
            chronology.decode_archive_bytes(bytes(hostile))

    def test_05_missing_and_extra_archive_entries_rejected(self) -> None:
        missing = copy.deepcopy(self.archive_value)
        missing["entries"].pop()
        with self.assertRaisesRegex(
            chronology.ChronologyError, "path/hash map differs"
        ):
            chronology.decode_archive_bytes(
                chronology.canonical_json_bytes(missing),
                expected_archive_sha256=None,
            )

        extra = copy.deepcopy(self.archive_value)
        duplicate = copy.deepcopy(extra["entries"][0])
        duplicate["path"] = "EXTRA.md"
        extra["entries"].append(duplicate)
        with self.assertRaisesRegex(
            chronology.ChronologyError, "path/hash map differs"
        ):
            chronology.decode_archive_bytes(
                chronology.canonical_json_bytes(extra),
                expected_archive_sha256=None,
            )

    def test_06_archived_payload_mutation_rejected(self) -> None:
        hostile = copy.deepcopy(self.archive_value)
        payload = hostile["entries"][0]["payload"]
        hostile["entries"][0]["payload"] = (
            ("0" if payload[0] != "0" else "1") + payload[1:]
        )
        with self.assertRaisesRegex(
            chronology.ChronologyError,
            "payload decode failed|entry hash mismatch|size mismatch",
        ):
            chronology.decode_archive_bytes(
                chronology.canonical_json_bytes(hostile),
                expected_archive_sha256=None,
            )

    def test_07_duplicate_json_key_rejected(self) -> None:
        hostile = self.archive_bytes.replace(
            b'{\n  "entries":',
            b'{\n  "schema_version": 1,\n  "entries":',
            1,
        )
        with self.assertRaisesRegex(
            chronology.ChronologyError, "duplicate JSON key"
        ):
            chronology.decode_archive_bytes(
                hostile, expected_archive_sha256=None
            )

    def test_08_duplicate_manifest_path_rejected(self) -> None:
        line = (
            b"0" * 64
            + b"  attempts/wave33-rooted-construction/exact_check.py\n"
        )
        with self.assertRaisesRegex(
            chronology.ChronologyError, "duplicate path"
        ):
            chronology.parse_manifest_bytes(
                line + line, label="hostile duplicate manifest"
            )

    def test_09_escaping_manifest_paths_rejected(self) -> None:
        for raw in (
            "../../STRUCTURE.md",
            "/absolute/STRUCTURE.md",
            r"C:\Users\RESEARCHER\STRUCTURE.md",
        ):
            line = ("0" * 64 + "  " + raw + "\n").encode("utf-8")
            with self.subTest(raw=raw), self.assertRaises(
                chronology.ChronologyError
            ):
                chronology.parse_manifest_bytes(
                    line, label="hostile path manifest"
                )

    def test_10_symlink_source_rejected(self) -> None:
        with mock.patch.object(Path, "is_symlink", return_value=True):
            with self.assertRaisesRegex(
                chronology.ChronologyError, "symlink is forbidden"
            ):
                chronology.require_regular_source(
                    chronology.ARCHIVE, label="hostile symlink"
                )

    def test_11_candidate_byte_mutation_rejected(self) -> None:
        target = (
            self.synthetic_root
            / "attempts"
            / "wave33-rooted-construction"
            / "exact_check.py"
        )
        original = target.read_bytes()
        try:
            target.write_bytes(original + b"\n")
            with self.assertRaisesRegex(
                chronology.ChronologyError, "entry hash mismatch"
            ):
                chronology.validate_frozen_packages(self.synthetic_root)
        finally:
            target.write_bytes(original)

    def test_12_root_manifest_mutation_rejected(self) -> None:
        raw = chronology.CANDIDATE_FREEZE.read_bytes()
        hostile = raw.replace(b"0", b"1", 1)
        with self.assertRaisesRegex(
            chronology.ChronologyError, "manifest byte hash mismatch"
        ):
            chronology.parse_manifest_bytes(
                hostile,
                label="hostile candidate freeze",
                expected_sha256=chronology.CANDIDATE_FREEZE_SHA256,
            )

    def test_13_full_historical_replay_matches_record(self) -> None:
        recorded = json.loads(
            (HERE / "chronology-results.json").read_text(encoding="utf-8")
        )
        self.assertEqual(self.replay_result, recorded)
        self.assertEqual(
            self.replay_result["replay"]["unchanged_discovery_tests_passed"],
            14,
        )
        self.assertEqual(
            self.replay_result["replay"]["unchanged_verifier_tests_passed"],
            36,
        )
        self.assertEqual(
            self.replay_result["replay"]["historical_package_tests_passed"],
            50,
        )

    def test_14_status_promotion_rejected(self) -> None:
        hostile = copy.deepcopy(self.replay_result)
        hostile["status_wall"]["complete_graph_extension"] = "VERIFIED"
        with self.assertRaisesRegex(
            chronology.ChronologyError, "status wall drift or promotion"
        ):
            chronology.assert_status_wall(hostile)

    def test_15_output_and_checkout_write_discipline(self) -> None:
        replay = self.replay_result["replay"]
        self.assertEqual(replay["checkout_outputs_written"], 0)
        self.assertTrue(replay["synthetic_tree_unchanged"])
        self.assertFalse(replay["pycache_created"])
        self.assertEqual(
            replay["exact_results_sha256"],
            chronology.EXPECTED_EXACT_RESULTS_SHA256,
        )
        self.assertEqual(
            replay["comparison_results_sha256"],
            chronology.EXPECTED_COMPARISON_RESULTS_SHA256,
        )
        self.assertEqual(
            replay["comparison_execution"]["unchanged_cli_status"],
            "NOT_RUN_BY_DESIGN",
        )
        self.assertTrue(replay["comparison_accepted_summary_core_bound"])

    def test_16_clean_source_and_synthetic_root_have_no_venv(self) -> None:
        self.assertFalse((self.clean_source_root / ".venv").exists())
        self.assertFalse((self.synthetic_root / ".venv").exists())
        self.assertEqual(
            self.replay_result["materialized"][
                "solver_provenance_files_copied"
            ],
            0,
        )
        self.assertFalse(
            self.replay_result["materialized"]["local_environment_dependency"]
        )

    def test_17_exact_test_identity_and_single_omission(self) -> None:
        replay = self.replay_result["replay"]
        self.assertEqual(
            replay["discovery_test_ids_sha256"],
            chronology.DISCOVERY_TEST_IDS_SHA256,
        )
        self.assertEqual(
            replay["full_verifier_test_ids_sha256"],
            chronology.FULL_VERIFIER_TEST_IDS_SHA256,
        )
        self.assertEqual(
            replay["included_verifier_test_ids_sha256"],
            chronology.INCLUDED_VERIFIER_TEST_IDS_SHA256,
        )
        self.assertEqual(
            replay["verifier_test_08"]["test_id"],
            chronology.OMITTED_VERIFIER_TEST,
        )

    def test_18_solver_records_are_documentary_not_observed(self) -> None:
        audit = self.replay_result["replay"]["verifier_test_08"][
            "solver_environment_file_half"
        ]["documentary_record_audit"]
        self.assertEqual(audit["documentary_hash_record_count"], 6)
        self.assertEqual(audit["observed_environment_hash_count"], 0)
        self.assertEqual(audit["local_environment_files_opened"], 0)
        self.assertEqual(
            audit["documentary_hash_records"],
            chronology.RECORDED_SOLVER_HASHES,
        )
        for relative in chronology.RECORDED_SOLVER_HASHES:
            self.assertFalse(
                self.synthetic_root.joinpath(*relative.split("/")).exists()
            )

    def test_19_solver_boundary_promotion_rejected(self) -> None:
        hostile = copy.deepcopy(self.replay_result)
        hostile["replay"]["verifier_test_08"][
            "solver_environment_file_half"
        ]["status"] = "PASS"
        with self.assertRaisesRegex(
            chronology.ChronologyError, "solver-environment boundary"
        ):
            chronology.assert_clean_clone_boundary(hostile)

    def test_20_clean_comparison_never_calls_forbidden_entrypoints(self) -> None:
        tree = ast.parse(Path(chronology.__file__).read_text(encoding="utf-8"))
        target = next(
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef)
            and node.name == "run_chronology_owned_comparison"
        )
        called_attributes = {
            node.func.attr
            for node in ast.walk(target)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
        }
        self.assertNotIn("compare", called_attributes)
        self.assertNotIn("verify_solver_environment_hashes", called_attributes)


if __name__ == "__main__":
    unittest.main(verbosity=2)
