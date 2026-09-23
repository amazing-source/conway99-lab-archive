"""Unit and artifact tests for the clean-room Wave 28 theta verifier.

The full 32-dimensional replay is intentionally the separate command

    python -B independent_check.py --output independent-results.json

These tests audit its frozen result and independently exercise the small trusted
arithmetic kernels without repeating the 15-million-node traversal.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import unittest

import independent_check as check


HERE = pathlib.Path(__file__).resolve().parent
RESULT_PATH = HERE / "independent-results.json"
CATALOGUE_PATH = HERE / "catalogue-data.json"
SOURCE_MANIFEST_PATH = HERE / "source-manifest.json"
THEOREM_SOURCE_MANIFEST_PATH = HERE / "theorem-source-manifest.json"


def file_sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def recursive_keys(value):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from recursive_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from recursive_keys(child)


class FrozenArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
        cls.catalogue = json.loads(CATALOGUE_PATH.read_text(encoding="utf-8"))
        cls.sources = json.loads(SOURCE_MANIFEST_PATH.read_text(encoding="utf-8"))
        cls.theorem_sources = json.loads(
            THEOREM_SOURCE_MANIFEST_PATH.read_text(encoding="utf-8")
        )

    def test_01_public_base_and_role(self):
        self.assertEqual(self.result["public_base_commit"], check.BASE_COMMIT)
        self.assertEqual(self.result["role"], "verifier")
        self.assertEqual(self.result["claim_label"], "VERIFIED")

    def test_02_no_raw_html_is_redistributed(self):
        self.assertEqual(list(HERE.rglob("*.raw.html")), [])
        for entry in self.sources.values():
            self.assertFalse(entry["raw_html_redistributed"])
            self.assertIn("--refresh-sources", entry["replay"])

    def test_03_raw_source_hashes_are_frozen(self):
        self.assertEqual(
            self.sources["K12"]["raw_sha256"],
            "163e03dfa9a4ab07675daa6e97a371bcfdb38f6195c311c63c699872b3e486c9",
        )
        self.assertEqual(
            self.sources["LAMBDA_F"]["raw_sha256"],
            "bb1db4504d7010dc093b24a8bcb00b042ea3879a220d669e8190d02abb6468ac",
        )
        self.assertEqual(self.sources["K12"]["raw_bytes"], 8962)
        self.assertEqual(self.sources["LAMBDA_F"]["raw_bytes"], 18876)

    def test_04_derived_catalogue_hash_is_guarded(self):
        digest = file_sha256(CATALOGUE_PATH)
        for entry in self.sources.values():
            self.assertEqual(entry["derived_numeric_file"], "catalogue-data.json")
            self.assertEqual(entry["derived_numeric_file_sha256"], digest)

    def test_05_embedded_gram_hashes_are_guarded(self):
        for name in ("K12", "LAMBDA_F"):
            gram = self.catalogue[name]["gram"]
            self.assertEqual(
                check.canonical_matrix_sha256(gram),
                self.sources[name]["parsed_gram_sha256"],
            )

    def test_06_source_matrices_are_recomputed_not_trusted(self):
        audited, k12, lambda_f = check.source_lattice_audit(
            check.frozen_source_metadata()
        )
        self.assertEqual((len(k12), audited["K12"]["determinant_exact"]), (12, 729))
        self.assertEqual(
            (len(lambda_f), audited["LAMBDA_F"]["determinant_exact"]), (32, 1)
        )
        self.assertTrue(audited["K12"]["positive_definite_exact_ldl"])
        self.assertTrue(audited["LAMBDA_F"]["positive_definite_exact_ldl"])

    def test_07_endpoint_levels_characters_and_sturm_bounds(self):
        rows = check.endpoint_level_table()
        self.assertEqual(
            [row["exact_level_S"] for row in rows], [3, 21, 7, 3, 21, 21, 3, 21]
        )
        self.assertEqual(
            [row["sturm_bound_q_exponent"] for row in rows],
            [7, 58, 14, 7, 58, 58, 7, 58],
        )
        self.assertEqual(
            [row["scalar_character"] for row in rows],
            [
                "trivial",
                "chi_21(d)=(21/d)",
                "trivial",
                "trivial",
                "chi_21(d)=(21/d)",
                "trivial",
                "trivial",
                "chi_21(d)=(21/d)",
            ],
        )

    def test_08_exact_level_and_strong_modularity_vetoes(self):
        for row in self.result["endpoint_level_character_sturm"]:
            self.assertTrue(row["modularity_determinant_veto"])
            self.assertNotEqual(
                row["determinant"], row["modularity_required_determinant"]
            )
            self.assertNotEqual(row["determinant"], 21**22)

    def test_09_small_ellipsoid_enumerator_matches_brute_force(self):
        gram = [[2, -1], [-1, 2]]
        exact = check.enumerate_closed_ball(gram, 4)
        brute = {}
        for x in range(-3, 4):
            for y in range(-3, 4):
                if x == y == 0:
                    continue
                norm = 2 * x * x - 2 * x * y + 2 * y * y
                if norm <= 4:
                    brute[str(norm)] = brute.get(str(norm), 0) + 1
        self.assertEqual(exact["norm_counts"], brute)
        self.assertEqual(exact["norm_counts"], {"2": 6})

    def test_10_integerized_ldl_reconstructs_exactly(self):
        gram = [[4, 1, -1], [1, 4, 2], [-1, 2, 4]]
        lower, diagonal = check.exact_ldl(gram)
        certificate = check.integerize_ldl(gram, lower, diagonal)
        self.assertGreater(int(certificate["global_scale"]), 0)
        self.assertEqual(len(certificate["forms"]), 3)

    def test_11_all_ADE_components_and_decompositions(self):
        components = self.result["ADE_components"]
        expected = {
            "A2": (6, 0, 14),
            "A6": (42, 210, 18),
            "A20": (420, 35910, 20),
            "E6": (72, 270, 28),
            "E8": (240, 2160, 42),
        }
        for name, triple in expected.items():
            self.assertEqual(
                (
                    components[name]["roots_r2"],
                    components[name]["norm_four_r4"],
                    components[name]["twenty_one_dual_exact_minimum"],
                ),
                triple,
            )
        self.assertEqual(self.result["ADE_decomposition_count"], 17)
        self.assertEqual(len(self.result["ADE_rank44_decompositions"]), 17)

    def test_12_K12_complete_shell_certificate(self):
        enumeration = self.result["hostile_control"]["K12"]["enumeration"]
        self.assertEqual(enumeration["norm_counts"], {"4": 756})
        self.assertEqual(enumeration["total_nonzero"], 756)
        self.assertEqual(enumeration["recursion_nodes"], 3663)
        self.assertIn("complete exact", enumeration["coverage"])

    def test_13_LAMBDA_F_complete_shell_certificate(self):
        enumeration = self.result["hostile_control"]["LAMBDA_F"]["enumeration"]
        self.assertEqual(enumeration["norm_counts"], {"4": 146880})
        self.assertEqual(enumeration["total_nonzero"], 146880)
        self.assertEqual(enumeration["recursion_nodes"], 15053011)
        self.assertEqual(enumeration["integerized_ldl"]["global_scale"], "960")
        self.assertIn("complete exact", enumeration["coverage"])

    def test_14_rootless_hostile_control_scope(self):
        s0 = self.result["hostile_control"]["S0"]
        self.assertEqual(
            (
                s0["rank"],
                s0["determinant"],
                s0["root_count_r2"],
                s0["norm_four_r4"],
                s0["twenty_one_dual_exact_minimum"],
            ),
            (44, 729, 0, 147636, 28),
        )
        self.assertFalse(s0["full_endpoint_objects_supplied"])

    def test_15_K12_scaled_dual_congruence(self):
        modularity = self.result["hostile_control"]["K12"]["modularity"]
        self.assertTrue(modularity["three_dual_isometric_to_K12"])
        self.assertEqual(abs(modularity["explicit_congruence_transform_det"]), 1)
        self.assertEqual(modularity["three_dual_exact_minimum"], 4)

    def test_16_explicit_discriminant_form_isometry(self):
        finite = self.result["comparator_and_discriminant_form"][
            "finite_quadratic_module"
        ]
        left = finite["K12_scaled_bilinear_matrix_mod_3"]
        right_one = finite["E6_scaled_bilinear_matrix_mod_3"]
        right = check.direct_sum(*([right_one] * 6))
        p = finite["explicit_isometry_P_mod_3"]
        reproduced = check.mod_matmul(
            check.mod_matmul(check.transpose(p), left, 3), p, 3
        )
        self.assertEqual(reproduced, right)
        self.assertTrue(finite["same_weil_representation"])
        self.assertFalse(finite["same_zero_component_theta_series"])

    def test_17_scope_wall_remains_fail_closed(self):
        wall = self.result["scope_wall"]
        self.assertTrue(wall["bare_S_G_lattice_control_only"])
        for key in (
            "primitive_embedding",
            "X",
            "M",
            "Q",
            "B",
            "Schur_square_certificate",
            "graph",
        ):
            self.assertFalse(wall[key])
        self.assertEqual(wall["n3_equals_708"], "UNKNOWN")
        self.assertEqual(wall["Conway_99"], "UNKNOWN")
        self.assertEqual(wall["novelty"], "UNKNOWN")

    def test_18_results_are_deterministic_not_telemetry_bearing(self):
        keys = set(recursive_keys(self.result))
        self.assertNotIn("generated_utc", keys)
        self.assertNotIn("elapsed_seconds", keys)
        self.assertEqual(
            self.result["runtime"]["dependencies"], "Python standard library only"
        )

    def test_19_primary_theorem_sources_are_frozen_without_redistribution(self):
        sources = self.theorem_sources["sources"]
        self.assertGreaterEqual(sum(bool(item["primary"]) for item in sources), 3)
        self.assertTrue(all(not item["raw_redistributed"] for item in sources))
        self.assertIn(
            "10.1007/BFb0072985",
            {item.get("doi") for item in sources},
        )
        self.assertTrue(
            all(len(item["raw_sha256"]) == 64 for item in sources)
        )

    def test_20_checker_is_clean_room(self):
        source = (HERE / "independent_check.py").read_text(encoding="utf-8")
        self.assertNotIn("import exact_check", source)
        self.assertNotIn("from exact_check", source)
        self.assertNotIn("exact-results.json", source)
        self.assertNotIn("attempts/wave28-theta-modular/exact_check.py", source)


if __name__ == "__main__":
    unittest.main()
