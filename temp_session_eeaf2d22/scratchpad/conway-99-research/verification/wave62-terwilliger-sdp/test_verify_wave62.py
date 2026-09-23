import json
import unittest
from pathlib import Path

import verify_wave62


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKAGE = ROOT / "attempts" / "wave62-terwilliger-sdp"


class IndependentWave62VerifierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = verify_wave62.build_result(PACKAGE)

    def test_frozen_independent_result(self):
        expected = json.loads(
            (HERE / "exact-verifier-result.json").read_text(encoding="utf-8")
        )
        self.assertEqual(self.result, expected)

    def test_scheme_and_tensor(self):
        scheme = self.result["signed_edge_scheme"]
        self.assertEqual(scheme["order"], 84)
        self.assertEqual(scheme["valencies"], [1, 2, 1, 20, 20, 40])
        self.assertEqual(scheme["multiplicities"], [1, 6, 7, 14, 21, 35])
        self.assertEqual(
            scheme["intersection_tensor_sha256"],
            "44574bd2abfb7a909c85b2f52aacd72e9e73c84981d9d48da112a481e299b2ff",
        )

    def test_incidence_derives_residual_spectrum(self):
        spectrum = self.result["incidence_and_residual_spectrum"][
            "residual_spectrum"
        ]
        self.assertEqual(
            spectrum, {"12": 1, "3": 40, "0": 7, "-2": 6, "-4": 30}
        )

    def test_all_endpoint_parameters_survive(self):
        audit = self.result["integer_endpoint_audit"]
        self.assertEqual(audit["surviving_integer_y"], list(range(43)))
        self.assertTrue(audit["all_real_y_feasible"])

    def test_degree_24_schur_census(self):
        scan = self.result["schur_family"]
        self.assertEqual(scan["matrix_count"], 1949)
        self.assertEqual(scan["endpoint_block_inequalities"], 23388)
        self.assertEqual(scan["positive"], 23316)
        self.assertEqual(scan["zero"], 72)
        self.assertEqual(scan["negative"], 0)

    def test_manifest_and_hostile_mutations(self):
        manifest = self.result["manifest"]
        self.assertEqual(
            manifest["manifest_sha256"],
            "d62af7171cd825001c8bce4b9b1502970718640f5c441164eb49d4e59ba26401",
        )
        self.assertEqual(manifest["mismatches"], [])
        self.assertEqual(manifest["unlisted_files"], [])
        self.assertTrue(all(self.result["hostile_mutations"].values()))

    def test_no_target_graph_automorphism_assumed(self):
        policy = self.result["automorphism_policy"]
        self.assertFalse(policy["target_graph_automorphism_assumed"])
        self.assertTrue(
            self.result["scaffold_group_generators"]["all_preserve_orbitals"]
        )

    def test_hostile_frozen_result_mutation_is_detected(self):
        mutated = json.loads(json.dumps(self.result))
        mutated["schur_family"]["zero"] += 1
        self.assertNotEqual(mutated, self.result)


if __name__ == "__main__":
    unittest.main()
