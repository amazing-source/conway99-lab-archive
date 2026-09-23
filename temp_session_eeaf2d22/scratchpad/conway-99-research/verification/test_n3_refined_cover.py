#!/usr/bin/env python3
"""Regression tests for the standalone refined N3-cover verifier."""

from __future__ import annotations

import importlib.util
import json
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parent
VERIFIER_PATH = ROOT / "n3-refined-cover" / "verify.py"
CERTIFICATE_PATH = ROOT / "n3-refined-cover" / "n3-refined-cover.json"

SPEC = importlib.util.spec_from_file_location("n3_refined_cover_verifier", VERIFIER_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("could not load the refined N3-cover verifier")
VERIFIER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFIER)


class N3RefinedCoverVerifierTests(unittest.TestCase):
    def verify_mutation(self, mutation: object, message: str) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "mutant.json"
            path.write_text(
                json.dumps(mutation, indent=2) + "\n",
                encoding="utf-8",
                newline="\n",
            )
            with self.assertRaisesRegex(ValueError, message):
                VERIFIER.verify(path)

    def test_committed_certificate_passes(self) -> None:
        self.assertEqual(VERIFIER.parse_args([]).certificate, CERTIFICATE_PATH)
        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(VERIFIER.main([str(CERTIFICATE_PATH)]), 0)
        self.assertIn("PASS refined N3 78-branch cover", output.getvalue())

    def test_booleans_cannot_impersonate_integers(self) -> None:
        mutations = (
            ("candidate_endpoints", None),
            ("candidate_endpoint", 0),
            ("positive_edge_literals", 0),
            ("representative", 0),
        )
        for field, index in mutations:
            with self.subTest(field=field):
                certificate = json.loads(CERTIFICATE_PATH.read_text(encoding="utf-8"))
                if field == "candidate_endpoints":
                    certificate[field][0] = False
                elif field == "candidate_endpoint":
                    certificate["orbits"][index][field] = False
                elif field == "positive_edge_literals":
                    certificate["orbits"][index][field][0] = True
                else:
                    certificate["orbits"][index][field][0][0] = False
                self.verify_mutation(certificate, field)

    def test_nonstandard_json_constant_and_duplicate_key_are_rejected(self) -> None:
        original = CERTIFICATE_PATH.read_text(encoding="utf-8")
        mutations = (
            (original.replace('"pair_count": 7', '"pair_count": NaN', 1), "constant"),
            (original.replace("{", '{\n  "format": "duplicate",', 1), "duplicate"),
        )
        with TemporaryDirectory() as directory:
            for index, (rendered, message) in enumerate(mutations):
                with self.subTest(message=message):
                    path = Path(directory) / f"mutant-{index}.json"
                    path.write_text(rendered, encoding="utf-8", newline="\n")
                    with self.assertRaisesRegex(ValueError, message):
                        VERIFIER.verify(path)


if __name__ == "__main__":
    unittest.main()
