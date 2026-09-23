#!/usr/bin/env python3
"""Integrity tests for the optional Wave 9 quartic census artifacts."""

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CENSUS_ROOT = ROOT / "n3-33-equality"
MANIFEST_PATH = CENSUS_ROOT / "n3-33-census-manifest.json"


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


class N333CensusIntegrityTests(unittest.TestCase):
    def test_manifest_and_implementation_hashes(self) -> None:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        self.assertEqual(
            manifest["schema"],
            "conditional-n3-33-census-manifest-v1",
        )
        self.assertFalse(manifest["catalog"]["redistributed_here"])
        self.assertEqual(manifest["catalog"]["total_type_count"], 266)
        self.assertEqual(manifest["enumeration"]["total_families"], 610)
        self.assertEqual(manifest["enumeration"]["surviving_families"], 0)
        self.assertEqual(
            manifest["conclusion"]["status"],
            "EXHAUSTIVE_CONTRADICTION_UNDER_PREMISES",
        )
        for implementation in manifest["implementations"].values():
            relative_path = Path(implementation["path"])
            path = ROOT.parent / relative_path
            self.assertTrue(path.is_file())
            self.assertEqual(sha256_path(path), implementation["sha256"])


if __name__ == "__main__":
    unittest.main()
