import importlib.util
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("w43_branch_verifier", HERE / "independent_check.py")
assert SPEC and SPEC.loader
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)
RESULT = json.loads((HERE / "independent-results.json").read_text(encoding="utf-8"))


class IndependentResultTests(unittest.TestCase):
    def test_archived_result_validates(self):
        MOD.validate(RESULT)

    def test_exact_catalogue_hashes(self):
        self.assertEqual(
            RESULT["raw"]["catalog_sha256"],
            "cafd0eddbc8371d59f7fb184b51f6a6facdeee9d1a50bbea7b30b95e2fa2b462",
        )
        self.assertEqual(
            RESULT["active"]["catalog_sha256"],
            "8c8afac5833ce5a2739fa6043d255adae5e3eb52b6bc75799fcd2ce86d297bf8",
        )

    def test_complete_match_classification(self):
        census = RESULT["enumeration"]
        self.assertEqual(census["accepted"], census["accepted_mate"])
        self.assertEqual(census["accepted"], census["accepted_anchor"])
        self.assertEqual(census["matching_visits"], census["accepted"] + census["killed"])

    def test_probe_records_exact(self):
        probes = RESULT["probes"]
        self.assertTrue(probes["records_exact_match"])
        self.assertTrue(probes["selection_exact_match"])
        self.assertTrue(probes["zero_failed_polarities"])
        self.assertTrue(probes["zero_coordinate_sourced_derivations"])

    def test_status_wall(self):
        status = RESULT["result"]
        self.assertEqual(status["branch_15"], "UNKNOWN")
        self.assertFalse(status["endpoint_excluded"])
        self.assertEqual(status["strict_upper_bound"], "NOT_PROVED")
        self.assertEqual(status["conway_99"], "UNKNOWN")

    def test_parser_rejects_repeated_literal(self):
        with self.assertRaises(ValueError):
            MOD.parse_row(b"+1 ~x1 +1 ~x1 >= 1 ;\n")


if __name__ == "__main__":
    unittest.main()
