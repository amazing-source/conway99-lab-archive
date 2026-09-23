from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("wave133_exact_check", ROOT / "exact_check.py")
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class Wave133ExactCheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = CHECK.build_record()

    def test_opposite_local_signs(self) -> None:
        controls = self.record["local_opposite_sign_controls"]
        self.assertEqual({item["holonomy_sign"] for item in controls}, {-1, 1})
        self.assertEqual({item["holonomy_fixed_points"] for item in controls}, {0})
        self.assertEqual({item["core_triangle_count"] for item in controls}, {0})

    def test_holonomy_cycle_lift(self) -> None:
        controls = {
            item["name"]: item for item in self.record["local_opposite_sign_controls"]
        }
        self.assertEqual(
            controls["positive_six_transpositions"]["cross_two_factor_cycle_type"],
            [6, 6, 6, 6, 6, 6],
        )
        self.assertEqual(
            controls["negative_twelve_cycle"]["cross_two_factor_cycle_type"],
            [36],
        )

    def test_base_twisted_surface(self) -> None:
        base = self.record["topological_twist_control"]["base_surface"]
        self.assertEqual((base["vertices"], base["edges"], base["faces"]), (2, 6, 3))
        self.assertEqual(base["link_cycle_lengths"], [6, 6])
        self.assertEqual(base["euler_characteristic"], -1)

    def test_endpoint_scale_surface_control(self) -> None:
        quotient = self.record["topological_twist_control"]["balanced_quotient"]
        self.assertEqual(quotient["quotient_vertices"], 231)
        self.assertEqual(quotient["quotient_edges"], 4158)
        self.assertEqual(quotient["quadrilateral_faces"], 2079)
        self.assertEqual(quotient["quotient_degree"], 36)
        self.assertTrue(quotient["quotient_simple"])
        self.assertEqual(
            quotient["link_cycle_type_at_every_quotient_vertex"],
            [6, 6, 6, 6, 6, 6],
        )

    def test_surface_sign_identity_and_nonorientability(self) -> None:
        quotient = self.record["topological_twist_control"]["balanced_quotient"]
        self.assertEqual(quotient["link_component_total_H"], 1386)
        self.assertEqual(quotient["global_holonomy_sign_product"], 1)
        self.assertEqual(quotient["euler_characteristic"], -693)
        self.assertIn("NONORIENTABLE", quotient["orientability"])
        self.assertEqual(
            quotient["global_holonomy_sign_product"],
            (-1)
            ** (
                quotient["euler_characteristic"]
                + quotient["quotient_edges"]
                - quotient["quadrilateral_faces"]
            ),
        )

    def test_stored_replay(self) -> None:
        stored = json.loads((ROOT / "exact-results.json").read_text(encoding="utf-8"))
        self.assertEqual(stored, self.record)


if __name__ == "__main__":
    unittest.main()
