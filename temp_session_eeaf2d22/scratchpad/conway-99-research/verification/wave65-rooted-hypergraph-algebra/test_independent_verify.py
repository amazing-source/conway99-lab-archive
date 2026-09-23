from __future__ import annotations

import unittest

import independent_verify as verify


class Wave65IndependentTests(unittest.TestCase):
    def test_rooted_scaffold(self) -> None:
        result = verify.rooted_scaffold()
        self.assertEqual(result["identity"], "B^2+B=10I+2J-Q")
        self.assertEqual(result["q_spectrum"], {"22": 1, "10": 7, "8": 6, "-2": 70})

    def test_generic_hypergraph_identities(self) -> None:
        result = verify.generic_hypergraph_identities()
        self.assertEqual(result["multiplicity_R_minus_3"], ">= 56")
        self.assertEqual(result["c4_transfer"], "c4(R)=1260+c4(D)")
        self.assertEqual(result["target_c4_R_interval"], [1260, 2331])

    def test_target_and_generic_moments(self) -> None:
        result = verify.target_and_generic_moments()
        self.assertEqual(result["target_B_c4"], 1071)
        self.assertEqual(result["target_B_moments"]["6"], 3138408)

    def test_scalar_coupling(self) -> None:
        result = verify.scalar_coupling()
        self.assertEqual(result["interval_w"], ["64/5", "16"])
        self.assertEqual(result["tr_B3T_range"], ["5376", "5712"])
        self.assertEqual(result["identity"], "tr(B^4 T)+3tr(B^3 T)=52416")

    def test_all_averaged_psd_lanes(self) -> None:
        result = verify.averaged_psd_lanes()
        self.assertEqual(result["negative_count"], 0)
        self.assertEqual(result["minimum"], "12/5")
        self.assertEqual(len(result["all_43_lane_eigenvalues"]), 43)

    def test_positive_control(self) -> None:
        result = verify.positive_control()
        self.assertEqual(result["R"]["local_graph"], "3K4")
        self.assertEqual(
            result["B"]["target_moment_deltas"],
            {"1": 0, "2": 0, "3": 0, "4": 5496, "5": -12020, "6": 239772},
        )
        self.assertEqual(result["scope"], "unlabelled local relaxation only; not a target candidate")

    def test_manifest(self) -> None:
        result = verify.manifest_audit()
        self.assertTrue(result["all_match"])


if __name__ == "__main__":
    unittest.main()
