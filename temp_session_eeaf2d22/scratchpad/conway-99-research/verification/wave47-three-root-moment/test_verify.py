#!/usr/bin/env python3
"""Fast tests for the independent Wave 47 verifier."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("wave47_verify", HERE / "verify.py")
assert SPEC is not None and SPEC.loader is not None
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)


class VerifierTests(unittest.TestCase):
    def test_internal_hostile_examples(self) -> None:
        self.assertEqual(
            VERIFY.self_tests(),
            {
                "edge_order_root_bits": "PASS",
                "free_vertex_swap_canonicalization": "PASS",
                "local_cap_hostile_examples": "PASS",
            },
        )

    def test_root_embedding_partition(self) -> None:
        values = [VERIFY.root_embeddings_at_n99(pattern) for pattern in range(8)]
        self.assertEqual(
            values,
            [590436, 99792, 99792, 16632, 99792, 16632, 16632, 1386],
        )
        self.assertEqual(sum(values), 99 * 98 * 97)

    def test_flag_census(self) -> None:
        self.assertEqual(
            [len(VERIFY.flag_universe(pattern)) for pattern in range(8)],
            [64, 56, 56, 42, 56, 42, 42, 20],
        )

    def test_handoff_hash(self) -> None:
        path = VERIFY.ATTEMPT / "compact-handoff.json"
        self.assertEqual(
            VERIFY.sha256_file(path), VERIFY.EXPECTED_HANDOFF_SHA256
        )
        handoff = VERIFY.read_json(path)
        payload = {
            key: value
            for key, value in handoff.items()
            if key != "payload_sha256_without_this_field"
        }
        self.assertEqual(
            VERIFY.sha256_compact(payload),
            handoff["payload_sha256_without_this_field"],
        )

    def test_cut_hash_contract(self) -> None:
        cuts = VERIFY.read_json(VERIFY.ATTEMPT / "cuts.json")["cuts"]
        sample = cuts[0]
        payload = {
            key: sample[key]
            for key in (
                "coefficients",
                "constant",
                "family",
                "primitive_divisor",
                "root_pattern",
                "vector",
            )
        }
        self.assertEqual(VERIFY.sha256_compact(payload), sample["cut_sha256"])

    def test_existing_full_record_if_present(self) -> None:
        path = HERE / "verification-results.json"
        if not path.exists():
            self.skipTest("full replay record not generated yet")
        record = json.loads(path.read_text(encoding="utf-8"))
        VERIFY.validate_summary(record)
        self.assertEqual(record["claim_label"], "VERIFIED_SCOPED")
        self.assertEqual(record["cuts"]["unique_primitive_cuts"], 2657)


if __name__ == "__main__":
    unittest.main(verbosity=2)
