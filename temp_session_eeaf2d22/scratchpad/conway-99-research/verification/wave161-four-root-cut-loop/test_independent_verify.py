from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "independent_verify.py"
RESULT = HERE / "exact-results.json"
spec = importlib.util.spec_from_file_location("wave161_independent", SCRIPT)
assert spec is not None and spec.loader is not None
VERIFY = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = VERIFY
spec.loader.exec_module(VERIFY)


class Wave161Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_self_test(self) -> None:
        self.assertEqual(
            VERIFY.self_test(),
            {
                "dense_direction": "PASS",
                "graph_flag_semantics": "PASS",
                "fraction_arithmetic": "PASS",
            },
        )

    def test_separation(self) -> None:
        separation = self.result["separation"]
        self.assertFalse(separation["wave159_discovery_python_imported"])
        self.assertFalse(separation["wave159_discovery_python_executed"])
        self.assertFalse(separation["solver_status_used_as_certificate"])

    def test_inventory_and_preservation(self) -> None:
        freeze = self.result["freeze"]
        self.assertEqual(freeze["wave159_package"]["entries"], 16)
        self.assertTrue(freeze["wave159_package"]["all_entries_match"])
        preserved = freeze["wave152_preservation"]
        self.assertTrue(preserved["inventories_byte_identical"])
        self.assertEqual(preserved["entries"], 42)

    def test_exact_witness(self) -> None:
        witness = self.result["witness"]
        self.assertEqual((witness["x7_support"], witness["x8_support"]), (204, 887))
        self.assertEqual(witness["all_equalities"], 10313)
        self.assertEqual(witness["restricted_equalities"], 10274)
        self.assertTrue(witness["nonnegative_coordinates"])

    def test_modular_rank(self) -> None:
        rank = self.result["witness"]["modular_rank"]
        self.assertEqual(rank["modulus"], 1000003)
        self.assertEqual((rank["rank"], rank["variables"]), (887, 887))
        self.assertTrue(rank["full_column_rank"])

    def test_fifteen_cuts(self) -> None:
        values = self.result["witness"]["exact_cut_values"]
        self.assertEqual(len(values), 15)
        self.assertEqual(
            sum(record["active"] for record in values.values()), 3
        )
        self.assertTrue(
            all(VERIFY.BASE.fraction(record["value"]) >= 0
                for record in values.values())
        )

    def test_fresh_cuts(self) -> None:
        cuts = self.result["fresh_cuts"]
        self.assertEqual([cut["root_mask"] for cut in cuts], [3, 12])
        self.assertTrue(
            all(cut["coefficients_reconstructed_exactly"] for cut in cuts)
        )
        self.assertTrue(
            all(cut["strictly_negative_on_thirteen_cut_witness"] for cut in cuts)
        )

    def test_negative_certificates(self) -> None:
        feedback = self.result["four_root_feedback"]
        self.assertEqual(feedback["stored_exact_negative_certificate_blocks"], [3, 12])
        self.assertTrue(
            all(record["strictly_negative"]
                for record in feedback["independently_replayed_negative_certificates"])
        )
        self.assertFalse(feedback["remaining_blocks_proved_psd"])

    def test_global_status_stays_unknown(self) -> None:
        verdict = self.result["verdict"]
        self.assertEqual(verdict["endpoint_n3_4158"], "UNKNOWN")
        self.assertEqual(verdict["strict_upper_bound_below_4158"], "NOT_PROVED")
        self.assertEqual(verdict["Conway_99"], "UNKNOWN")
        self.assertFalse(verdict["graph_constructed"])

    def test_memory_floor(self) -> None:
        resource = self.result["resource_report"]
        self.assertGreaterEqual(resource["minimum_free_physical_memory_percent"], 15)
        self.assertTrue(resource["floor_respected"])


if __name__ == "__main__":
    unittest.main()
