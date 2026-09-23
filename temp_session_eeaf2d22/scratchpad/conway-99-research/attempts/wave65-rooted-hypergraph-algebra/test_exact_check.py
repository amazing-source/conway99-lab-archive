import importlib.util
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("wave65_exact_check", HERE / "exact_check.py")
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Wave65ExactCheckTests(unittest.TestCase):
    def test_rooted_scaffold(self):
        result = MODULE.verify_rooted_scaffold()
        self.assertEqual(result["H_edge_count"], 84)
        self.assertEqual(result["line_graph_degree"], 22)

    def test_generic_hypergraph_consequences(self):
        result = MODULE.generic_hypergraph_consequences()
        self.assertEqual(result["R"]["minus_3_multiplicity_lower_bound"], 56)
        self.assertEqual(
            result["four_cycle_transfer"]["necessary_bounds_if_D_subset_B"]["c4(R)"],
            [1260, 2331],
        )

    def test_averaged_psd(self):
        result = MODULE.averaged_hypergraph_psd()
        self.assertEqual(result["negative_blocks"], 0)
        self.assertEqual(result["minimum_over_all_43_integer_parameters"], "12/5")

    def test_scalar_spectral_overlap(self):
        result = MODULE.spectral_overlap_control()
        self.assertEqual(
            result["necessary_interval_from_minus_2I_le_T_le_2I"],
            ["64/5", "16"],
        )

    def test_positive_control(self):
        result = MODULE.verify_positive_control()
        self.assertEqual(result["hypergraph"]["blocks"], 140)
        self.assertEqual(
            result["disposition"],
            "EXACT_POSITIVE_CONTROL_FOR_LOCAL_DECOMPOSITION_ONLY",
        )
        self.assertNotEqual(
            set(result["local_sum_B"]["target_moment_differences"].values()),
            {0},
        )

    def test_frozen_result(self):
        frozen = json.loads((HERE / "exact-results.json").read_text(encoding="utf-8"))
        self.assertEqual(MODULE.build_result(), frozen)


if __name__ == "__main__":
    unittest.main()
