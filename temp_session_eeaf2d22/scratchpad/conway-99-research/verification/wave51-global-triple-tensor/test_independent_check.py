from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DISCOVERY_RESULT = (
    ROOT / "attempts" / "wave51-global-triple-tensor" / "exact-result.json"
)
sys.path.insert(0, str(HERE))

import independent_check as check  # noqa: E402


def fresh_document() -> dict:
    return json.loads(DISCOVERY_RESULT.read_text(encoding="utf-8"))


class Wave51IndependentVerifierTests(unittest.TestCase):
    def test_frozen_baseline_passes(self) -> None:
        result = check.load_and_verify(DISCOVERY_RESULT)
        self.assertEqual(result["endpoint"], "UNKNOWN")
        self.assertEqual(result["association_scheme_diagnostic"]["failure_count"], 100)

    def test_rejects_negative_tensor_entry(self) -> None:
        document = fresh_document()
        document["normalized_symmetric_tensor_nonzero_entries"][5]["value"] = -90
        with self.assertRaisesRegex(check.VerificationError, "positive integer"):
            check.verify_document(document)

    def test_rejects_duplicate_canonical_entry(self) -> None:
        document = fresh_document()
        document["normalized_symmetric_tensor_nonzero_entries"].append(
            copy.deepcopy(document["normalized_symmetric_tensor_nonzero_entries"][0])
        )
        with self.assertRaisesRegex(check.VerificationError, "duplicate"):
            check.verify_document(document)

    def test_rejects_noncanonical_entry(self) -> None:
        document = fresh_document()
        document["normalized_symmetric_tensor_nonzero_entries"][5]["relations"] = [
            "K", "C", "K"
        ]
        with self.assertRaisesRegex(check.VerificationError, "not canonical"):
            check.verify_document(document)

    def test_rejects_tensor_arithmetic_mutation(self) -> None:
        document = fresh_document()
        document["normalized_symmetric_tensor_nonzero_entries"][5]["value"] += 1
        with self.assertRaises(check.VerificationError):
            check.verify_document(document)

    def test_rejects_supplied_table_mutation(self) -> None:
        document = fresh_document()
        document["local_average_tables_p_k_ij"]["B"][4][4] += 1
        with self.assertRaisesRegex(check.VerificationError, "differs"):
            check.verify_document(document)

    def test_rejects_associativity_count_mutation(self) -> None:
        document = fresh_document()
        document["associativity_diagnostic"][
            "failure_count_over_625_ordered_index_tests"
        ] = 99
        with self.assertRaisesRegex(check.VerificationError, "failure count"):
            check.verify_document(document)

    def test_rejects_spectral_mutation(self) -> None:
        document = fresh_document()
        document["endpoint_input"]["K_spectrum"]["7"] = 53
        with self.assertRaisesRegex(check.VerificationError, "K spectrum"):
            check.verify_document(document)

    def test_rejects_endpoint_status_inflation(self) -> None:
        document = fresh_document()
        document["claim_boundary"]["prism_free_endpoint"] = "VERIFIED"
        with self.assertRaisesRegex(check.VerificationError, "UNKNOWN"):
            check.verify_document(document)

    def test_rejects_conway_status_inflation(self) -> None:
        document = fresh_document()
        document["claim_boundary"]["conway_99"] = "VERIFIED"
        with self.assertRaisesRegex(check.VerificationError, "UNKNOWN"):
            check.verify_document(document)

    def test_rejects_novelty_status_inflation(self) -> None:
        document = fresh_document()
        document["claim_boundary"]["novelty"] = "VERIFIED"
        with self.assertRaisesRegex(check.VerificationError, "UNKNOWN"):
            check.verify_document(document)


if __name__ == "__main__":
    unittest.main()
