#!/usr/bin/env python3
"""Unit tests for the standard-library Wave 37 artifact tools."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from audit_opb import audit
from package_opb import package


class ArtifactToolTests(unittest.TestCase):
    def test_audit_accepts_bound_formula(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            opb = directory / "sample.opb"
            metadata = directory / "sample.json"
            payload = (
                b"* #variable= 2 #constraint= 2\n"
                b"+1 x1 +1 ~x2 >= 1 ;\n"
                b"+1 ~x1 >= 1 ;\n"
            )
            opb.write_bytes(payload)
            metadata.write_text(
                json.dumps(
                    {
                        "opb": {
                            "bytes": len(payload),
                            "constraint_count": 2,
                            "path": opb.as_posix(),
                            "sha256": (
                                __import__("hashlib")
                                .sha256(payload)
                                .hexdigest()
                            ),
                        }
                    }
                ),
                encoding="utf-8",
            )
            result = audit(opb, metadata)
            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["body"]["distinct_variables"], 2)
            self.assertEqual(
                result["body"]["term_count_histogram"],
                {"1": 1, "2": 1},
            )

    def test_audit_rejects_metadata_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            opb = directory / "sample.opb"
            metadata = directory / "sample.json"
            opb.write_bytes(
                b"* #variable= 1 #constraint= 1\n+1 x1 >= 1 ;\n"
            )
            metadata.write_text(
                json.dumps(
                    {
                        "opb": {
                            "bytes": 0,
                            "constraint_count": 1,
                            "path": opb.as_posix(),
                            "sha256": "0" * 64,
                        }
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "metadata"):
                audit(opb, metadata)

    def test_deterministic_gzip_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            source = directory / "sample.opb"
            first = directory / "first.opb.gz"
            second = directory / "second.opb.gz"
            source.write_bytes(
                b"* #variable= 1 #constraint= 1\n+1 x1 >= 1 ;\n"
            )
            first_result = package(source, first)
            second_result = package(source, second)
            self.assertTrue(first_result["round_trip"]["exact"])
            self.assertEqual(
                first_result["compressed"]["sha256"],
                second_result["compressed"]["sha256"],
            )
            self.assertEqual(first.read_bytes(), second.read_bytes())


if __name__ == "__main__":
    unittest.main()
