from __future__ import annotations

import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path


PACKAGE = Path(__file__).resolve().parent
MODULE_PATH = PACKAGE / "endpoint_deck.py"
SPEC = importlib.util.spec_from_file_location("wave43_endpoint_deck", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("could not load endpoint-deck module")
CHECK = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CHECK
SPEC.loader.exec_module(CHECK)


class EndpointDeckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.path = PACKAGE / "exact-results.json"
        cls.record = json.loads(cls.path.read_text(encoding="utf-8"))
        cls.model = CHECK.build_endpoint_model()

    def test_exact_stored_certificate(self) -> None:
        replay = CHECK.verify_record(self.path)
        self.assertEqual(replay["verification"], "PASS")
        self.assertEqual(replay["support_size"], 99)
        self.assertEqual(replay["h11"], 16632)

    def test_endpoint_model_census(self) -> None:
        self.assertEqual(len(self.model["classes"]), 208)
        self.assertEqual(len(self.model["matrix_rows"]), 62)
        self.assertEqual(len(self.model["h_equations"]), 19)
        self.assertEqual(self.model["six_counts"][0], 0)
        self.assertEqual(sum(self.model["six_counts"]), 1120529256)

    def test_prism_zero_forces_all_containing_classes_zero(self) -> None:
        certificate = self.record["certificate"]
        self.assertEqual(certificate["prism_containing_class_count"], 3)
        self.assertTrue(certificate["all_prism_containing_classes_zero"])

    def test_mutated_support_is_rejected(self) -> None:
        certificate = copy.deepcopy(self.record["certificate"])
        certificate["support"][0]["count"] += 1
        index = {
            mask: position
            for position, mask in enumerate(self.model["classes"])
        }
        counts = [0] * len(self.model["classes"])
        for record in certificate["support"]:
            counts[index[record["canonical_mask"]]] = record["count"]
        with self.assertRaisesRegex(ValueError, "deletion row|seven-subset"):
            CHECK.validate_candidate(
                self.model,
                counts,
                certificate["h11"] // 4,
            )

    def test_status_wall(self) -> None:
        conclusion = self.record["conclusion"]
        self.assertEqual(conclusion["order_seven_count_system"], "FEASIBLE")
        self.assertEqual(conclusion["endpoint_n3_4158"], "UNKNOWN")
        self.assertEqual(conclusion["upper_bound_below_4158"], "NOT_PROVED")
        self.assertFalse(conclusion["graph_construction"])
        self.assertEqual(conclusion["conway_99"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
