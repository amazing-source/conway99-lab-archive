from __future__ import annotations

import copy
import gzip
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ATTEMPT_ROOT = Path(__file__).resolve().parent


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


generator = load_module(
    "wave39_generate_certificate", ATTEMPT_ROOT / "generate_certificate.py"
)
checker = load_module(
    "wave39_verify_certificate", ATTEMPT_ROOT / "verify_certificate.py"
)
exporter = load_module(
    "wave39_export_shard_opb", ATTEMPT_ROOT / "export_shard_opb.py"
)


class CertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.certificate = generator.build_certificate(generator.DEFAULT_SOURCE)

    def assert_rejected(self, candidate):
        with self.assertRaises(ValueError):
            checker.validate_certificate(candidate)

    def test_generator_and_checker_agree(self):
        result = checker.validate_certificate(copy.deepcopy(self.certificate))
        self.assertEqual(result["status"], "PASS_GENERALIZED_UNIT_SHARD_REPLAY")
        self.assertEqual(result["entailed_literal"], "x187=0")
        self.assertEqual(result["closed_endpoint_cases"], 0)

    def test_certificate_is_canonical_json_round_trip(self):
        payload = generator.canonical_payload(self.certificate)
        reparsed = json.loads(payload)
        self.assertEqual(generator.canonical_payload(reparsed), payload)

    def test_wrong_assumption_rejected(self):
        candidate = copy.deepcopy(self.certificate)
        candidate["branch"]["assumption"]["value"] = False
        self.assert_rejected(candidate)

    def test_wrong_complement_rejected(self):
        candidate = copy.deepcopy(self.certificate)
        candidate["branch"]["complementary_open_shard"]["value"] = True
        self.assert_rejected(candidate)

    def test_mutated_source_line_hash_rejected(self):
        candidate = copy.deepcopy(self.certificate)
        candidate["source_constraints"]["106"]["sha256"] = "0" * 64
        self.assert_rejected(candidate)

    def test_unforced_literal_rejected(self):
        candidate = copy.deepcopy(self.certificate)
        candidate["trace"][2]["derive"] = {"variable": 3591, "value": True}
        self.assert_rejected(candidate)

    def test_missing_derivation_rejected(self):
        candidate = copy.deepcopy(self.certificate)
        del candidate["trace"][2]
        candidate["source_constraints"].pop("571132")
        self.assert_rejected(candidate)

    def test_false_contradiction_rejected(self):
        candidate = copy.deepcopy(self.certificate)
        candidate["trace"][-1]["source_line"] = 285938
        candidate["source_constraints"].pop("106")
        self.assert_rejected(candidate)

    def test_inflated_coverage_rejected(self):
        candidate = copy.deepcopy(self.certificate)
        candidate["coverage"]["closed_endpoint_cases"] = 1
        self.assert_rejected(candidate)

    def test_duplicate_json_key_rejected(self):
        with self.assertRaises(ValueError):
            json.loads(
                '{"format":"a","format":"b"}',
                object_pairs_hook=checker.no_duplicate_object_keys,
            )

    def test_source_byte_mutation_rejected(self):
        raw = gzip.decompress(generator.DEFAULT_SOURCE.read_bytes())
        mutated = bytearray(raw)
        mutated[-2] = ord("0") if mutated[-2] != ord("0") else ord("1")
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "mutated.opb.gz"
            path.write_bytes(gzip.compress(bytes(mutated), mtime=0))
            with self.assertRaises(ValueError):
                generator.read_source(path)

    def test_all_source_line_bindings_are_distinct(self):
        hashes = [
            record["sha256"]
            for record in self.certificate["source_constraints"].values()
        ]
        self.assertEqual(len(hashes), len(set(hashes)))
        self.assertTrue(all(len(digest) == 64 for digest in hashes))

    def test_streaming_shard_export_is_deterministic_and_exact(self):
        with tempfile.TemporaryDirectory(dir=ATTEMPT_ROOT) as temporary:
            root = Path(temporary)
            raw = root / "shard.opb"
            compressed = root / "shard.opb.gz"
            metadata = root / "shard.json"
            first = exporter.export_shard(
                exporter.DEFAULT_SOURCE, raw, compressed, metadata
            )
            first_gzip = compressed.read_bytes()
            first_metadata = metadata.read_bytes()
            raw_second = root / "shard-second.opb"
            compressed_second = root / "shard-second.opb.gz"
            metadata_second = root / "shard-second.json"
            second = exporter.export_shard(
                exporter.DEFAULT_SOURCE,
                raw_second,
                compressed_second,
                metadata_second,
            )
            self.assertEqual(
                first["opb"]["raw_sha256"], second["opb"]["raw_sha256"]
            )
            self.assertEqual(
                first["opb"]["gzip_sha256"], second["opb"]["gzip_sha256"]
            )
            self.assertEqual(compressed_second.read_bytes(), first_gzip)
            first_data = json.loads(first_metadata)
            second_data = json.loads(metadata_second.read_bytes())
            first_data["opb"]["raw_path"] = second_data["opb"]["raw_path"]
            first_data["opb"]["gzip_path"] = second_data["opb"]["gzip_path"]
            self.assertEqual(first_data, second_data)
            with raw.open("rb") as stream:
                self.assertEqual(stream.readline(), exporter.SHARD_HEADER)
                lines = stream.readlines()
            self.assertEqual(lines[-1], exporter.ASSUMPTION)
            self.assertEqual(len(lines), 574616)

    def test_shard_export_rejects_output_escape(self):
        with tempfile.TemporaryDirectory() as temporary:
            outside = Path(temporary)
            with self.assertRaises(ValueError):
                exporter.export_shard(
                    exporter.DEFAULT_SOURCE,
                    outside / "shard.opb",
                    ATTEMPT_ROOT / "inside.opb.gz",
                    ATTEMPT_ROOT / "inside.json",
                )


if __name__ == "__main__":
    unittest.main()
