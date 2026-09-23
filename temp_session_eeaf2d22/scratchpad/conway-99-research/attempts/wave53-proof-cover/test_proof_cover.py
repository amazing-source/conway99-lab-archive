from __future__ import annotations

import copy
import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def load(name: str, path: Path):
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


builder = load("wave53_test_builder", ROOT / "build_coverage.py")
checker = load("wave53_test_checker", ROOT / "check_coverage.py")
exporter = load("wave53_test_exporter", ROOT / "export_remainder.py")
recorder = load("wave53_test_recorder", ROOT / "record_bounded_run.py")


class ProofCoverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = builder.build()

    def test_exact_cover_and_zero_proof_coverage(self) -> None:
        result = checker.check(self.certificate)
        self.assertTrue(
            result["branch_cover_exhaustive_under_endpoint_assumptions"]
        )
        self.assertEqual(result["complete_case_proof_coverage"], "0/33")
        self.assertEqual(
            len(self.certificate["case_definitions"]), 33
        )
        self.assertEqual(
            sum(
                case["state_orbit_size"]
                for case in self.certificate["case_definitions"]
            ),
            6644,
        )

    def test_missing_case_is_rejected(self) -> None:
        altered = copy.deepcopy(self.certificate)
        altered["case_definitions"].pop()
        with self.assertRaises(ValueError):
            checker.check(altered)

    def test_proof_status_inflation_is_rejected(self) -> None:
        altered = copy.deepcopy(self.certificate)
        altered["proof_status"]["complete_cases_checked_unsat"] = 1
        altered["proof_status"]["complete_case_proof_coverage"] = "1/33"
        altered["case_definitions"][0]["complete_case_status"] = "UNSAT"
        with self.assertRaises(ValueError):
            checker.check(altered)

    def test_remainder_export_is_exact_and_deterministic(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as temporary:
            directory = Path(temporary)
            first_raw = directory / "first.opb"
            first_gzip = directory / "first.opb.gz"
            first_metadata = directory / "first.json"
            first = exporter.export(
                exporter.DEFAULT_SOURCE, first_raw, first_gzip, first_metadata
            )
            second_raw = directory / "second.opb"
            second_gzip = directory / "second.opb.gz"
            second_metadata = directory / "second.json"
            second = exporter.export(
                exporter.DEFAULT_SOURCE, second_raw, second_gzip, second_metadata
            )
            self.assertEqual(first["opb"]["raw_sha256"], second["opb"]["raw_sha256"])
            self.assertEqual(
                first["opb"]["gzip_sha256"], second["opb"]["gzip_sha256"]
            )
            self.assertTrue(first_raw.read_bytes().endswith(exporter.ASSUMPTION))

    def test_bounded_run_is_fail_closed(self) -> None:
        result = recorder.build()
        self.assertEqual(result["exact"]["result"], "UNKNOWN")
        self.assertEqual(
            set(result["proof_replay"].values()),
            {"VERIFIED_NO_CONCLUSION"},
        )
        self.assertEqual(result["conclusion"]["mathematical_evidence"], "NONE")
        self.assertEqual(result["conclusion"]["proof_coverage"], "0/33")


if __name__ == "__main__":
    unittest.main()
