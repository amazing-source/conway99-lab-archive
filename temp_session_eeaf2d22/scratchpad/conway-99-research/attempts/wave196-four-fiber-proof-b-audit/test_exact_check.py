from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("wave196_b", HERE / "exact_check.py")
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Wave196ProofBAuditTests(unittest.TestCase):
    def test_frozen_result(self) -> None:
        expected = json.loads((HERE / "exact-results.json").read_text(encoding="utf-8"))
        self.assertEqual(MODULE.derive(), expected)

    def test_four_fibers(self) -> None:
        geometry = MODULE.local_geometry()
        self.assertEqual(geometry["fiber_size"], 4)
        self.assertEqual(geometry["partitioned_nonneighbors"], 84)

    def test_hilton_milner_templates(self) -> None:
        for template in MODULE.local_geometry()["templates"].values():
            self.assertEqual(template["members"], 13)
            self.assertEqual(template["pair_types_of_degree_five"], 3)
            self.assertLessEqual(template["leaf_union_cap"], 36)

    def test_common_star(self) -> None:
        geometry = MODULE.local_geometry()
        self.assertEqual(geometry["common_star_flag_cap"], 12)
        self.assertEqual(geometry["universal_label_cap"], 36)

    def test_global_caps(self) -> None:
        geometry = MODULE.local_geometry()
        self.assertEqual(geometry["global_flag_cap"], 1287)
        self.assertEqual(geometry["global_label_cap"], 3564)

    def test_certificate(self) -> None:
        cert = MODULE.certificate()
        self.assertEqual(cert["reduced_difference"], {})
        self.assertEqual(cert["target"], "7029")
        self.assertEqual(cert["integer_Q_lower_bound"], 7029)
        self.assertFalse(cert["null_control"]["asserted_object"])


if __name__ == "__main__":
    unittest.main()
