#!/usr/bin/env python3
"""Tests for the Wave 147 pair-root order-eight derivation."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("wave147_exact_check", HERE / "exact_check.py")
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CHECK
SPEC.loader.exec_module(CHECK)


class Wave147Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result, cls.coefficient_gzip = CHECK.build_artifacts()

    def test_complete_class_and_flag_censuses(self) -> None:
        self.assertEqual(self.result["class_streams"]["7"]["count"], 208)
        self.assertEqual(self.result["class_streams"]["8"]["count"], 916)
        self.assertEqual(
            self.result["class_streams"]["8"]["sha256"],
            "c2cf3604abc76a537eca21f1a8ef041697ca40d8ad41668d25eb412b9cd67337",
        )
        payload = self.result["full_coefficient_payload"]
        self.assertEqual(payload["class_matrix_records_per_family"], 1207)
        self.assertEqual(payload["total_class_matrix_records"], 2414)
        self.assertEqual(payload["total_nonzero_upper_entries"], 272054)
        self.assertEqual(payload["deletion_equations"]["rows"], 208)
        self.assertEqual(payload["deletion_equations"]["nonzero_terms"], 5333)
        self.assertEqual(self.result["families"]["ordered_edge"]["flag_count"], 66)
        self.assertEqual(
            self.result["families"]["ordered_nonedge"]["flag_count"], 87
        )

    def test_n3_and_prism_coefficients(self) -> None:
        edge = self.result["families"]["ordered_edge"]
        nonedge = self.result["families"]["ordered_nonedge"]
        self.assertEqual(edge["n3_order_six_coefficient"]["sum_all_entries"], 192)
        self.assertEqual(edge["prism_order_six_coefficient"]["sum_all_entries"], 216)
        self.assertEqual(
            nonedge["n3_order_six_coefficient"]["sum_all_entries"], 168
        )
        self.assertEqual(
            nonedge["prism_order_six_coefficient"]["sum_all_entries"], 144
        )
        self.assertEqual(edge["selected_n3_carrier"]["n3_coefficient"], 4)
        self.assertEqual(edge["selected_n3_carrier"]["prism_coefficient"], 0)
        self.assertEqual(nonedge["selected_n3_carrier"]["n3_coefficient"], 4)
        self.assertEqual(nonedge["selected_n3_carrier"]["prism_coefficient"], 0)

    def test_rook_positive_control(self) -> None:
        control = self.result["positive_control"]
        self.assertEqual(control["induced_n3_count"], 0)
        self.assertEqual(control["induced_triangular_prism_count"], 6)
        for family in ("ordered_edge", "ordered_nonedge"):
            moment = control["direct_moments"][family]
            self.assertEqual(moment["root_embeddings"], 36)
            self.assertEqual(moment["free_triples_per_root"], 35)
            self.assertEqual(moment["sum_all_entries"], 44100)
            self.assertEqual(moment["rank_over_Q"], 1)

    def test_stored_result_exact_replay(self) -> None:
        stored = json.loads((HERE / "exact-results.json").read_text(encoding="utf-8"))
        self.assertEqual(self.result, stored)
        self.assertEqual(
            self.coefficient_gzip, (HERE / "coefficients.json.gz").read_bytes()
        )

    def test_hostile_n3_edge_mutation_is_detected(self) -> None:
        stored = json.loads((HERE / "exact-results.json").read_text(encoding="utf-8"))
        stored["families"]["ordered_edge"]["selected_n3_carrier"][
            "n3_coefficient"
        ] += 1
        self.assertNotEqual(self.result, stored)


if __name__ == "__main__":
    unittest.main()
