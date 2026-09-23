"""Tests for the clean-room Wave 124 verifier."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave124_independent", HERE / "independent_verify.py"
)
assert SPEC is not None and SPEC.loader is not None
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)


class Wave124IndependentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = VERIFY.build_results()

    def test_frozen_inputs_and_host_budget(self) -> None:
        VERIFY.check_frozen_inputs()
        self.assertGreaterEqual(VERIFY.free_memory_percent(), 15)

    def test_primitive_markings(self) -> None:
        d = self.result["alternating_vector"]
        self.assertEqual(d["norm"], 20)
        self.assertTrue(d["primitive_in_L"])
        self.assertEqual(d["divisibility_in_L"], 1)
        markings = self.result["markings"]
        self.assertEqual(markings["K"]["norm"], 140)
        self.assertEqual(markings["K"]["Jacobi_index"], 70)
        self.assertEqual(markings["K"]["divisibility"], 7)
        self.assertEqual(markings["L"]["Jacobi_index"], 10)
        witness = d["pairing_one_witness_counts"]
        self.assertEqual(witness["external_C4_edges"], 48)
        self.assertEqual(witness["external_common_neighbor_pairs"], 4)

    def test_norm20_interpretation_is_actually_justified(self) -> None:
        coefficient = self.result["coefficient_interpretation"]
        self.assertEqual(
            coefficient["q_exponents_with_exact_alternating_interpretation"],
            [7, 8, 9, 10],
        )
        self.assertIn("Wave96", coefficient["norm20_justification"])
        self.assertEqual(coefficient["target_r"], 28)

    def test_Fricke_and_twenty_components(self) -> None:
        fricke = self.result["Fricke_Poisson"]
        self.assertEqual(fricke["rank28_q16_raw_factor"], "-7^8")
        self.assertEqual(fricke["rank30_q14_raw_factor"], "-7^7")
        theta = self.result["theta_decomposition"]
        self.assertEqual(theta["ordinary_index70_residues"], 140)
        self.assertEqual(theta["component_count"], 20)
        self.assertEqual(theta["even_component_count"], 11)
        self.assertEqual(theta["live_K_residues"], [7 * s for s in range(20)])

    def test_tight_frame_second_moment(self) -> None:
        moment = self.result["tight_frame_second_moment"]
        self.assertEqual(
            moment["C4_counts"],
            {
                "cycles_through_vertex": 84,
                "cycles_through_edge": 12,
                "cycles_with_nonedge_as_diagonal": 1,
            },
        )
        self.assertEqual(moment["coordinate_matrix"], "83I-13A+J")
        self.assertEqual(moment["minus4_eigenvalue"], 135)
        self.assertEqual(
            moment["shell_rows"]["10"]["sum_C_r_C_squared_per_vector"],
            132300,
        )
        self.assertEqual(moment["forced_L_coefficient"]["value"], 2079)
        self.assertEqual(moment["L_frame_operator"], "sum_C d_C*d_C^T=945I")

    def test_degree_eight_indicator(self) -> None:
        selector = self.result["degree_eight_indicator"]
        self.assertEqual(selector["selected_values"], [-4, 4])
        self.assertEqual(
            selector["coefficients_low_to_high"],
            [
                "0",
                "0",
                "-1/560",
                "0",
                "7/2880",
                "0",
                "-1/1440",
                "0",
                "1/20160",
            ],
        )

    def test_both_incidence_targets(self) -> None:
        targets = self.result["incidence_targets"]
        self.assertEqual(targets["rank28_q16"]["gap"], 837)
        self.assertEqual(targets["rank30_q14"]["gap"], 1419)
        self.assertFalse(targets["rank28_q16"]["cap25_proved"])
        self.assertFalse(targets["rank30_q14"]["cap24_proved"])

    def test_support_and_null_model(self) -> None:
        self.assertEqual(
            self.result["support"]["margins"],
            {"7": 1176, "8": 1456, "9": 1736, "10": 2016},
        )
        control = self.result["null_control"]
        self.assertEqual(
            sum(control["coefficients"].values()), control["row_sum"]
        )
        self.assertEqual(
            control["actual_second_moment"],
            control["required_second_moment"],
        )
        self.assertTrue(control["not_a_Jacobi_form"])

    def test_evidence_boundary(self) -> None:
        boundary = self.result["evidence_boundary"]
        self.assertFalse(boundary["complete_weight43_over2_component_basis"])
        self.assertFalse(boundary["exact_upper_dual"])
        self.assertEqual(boundary["cap25"], "UNKNOWN")
        self.assertEqual(boundary["cap24"], "UNKNOWN")
        self.assertEqual(boundary["Conway_99"], "UNKNOWN")
        self.assertEqual(boundary["novelty"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
