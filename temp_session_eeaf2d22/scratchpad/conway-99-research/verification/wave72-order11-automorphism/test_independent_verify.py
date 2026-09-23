"""Hostile tests for the independent Wave 72 verifier."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("independent_verify.py")
SPEC = importlib.util.spec_from_file_location("wave72_independent", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class IndependentOrder11Tests(unittest.TestCase):
    def test_orbit_congruence_is_exhaustive(self) -> None:
        self.assertEqual(
            MODULE.fixed_count_candidates(),
            [0, 11, 22, 33, 44, 55, 66, 77, 88, 99],
        )

    def test_fixed_degree_options_are_exact(self) -> None:
        self.assertEqual(MODULE.fixed_degree_options(), [3, 14])

    def test_common_neighbor_closure_uses_strict_prime_bound(self) -> None:
        self.assertTrue(MODULE.invariant_small_set_is_pointwise_fixed(1))
        self.assertTrue(MODULE.invariant_small_set_is_pointwise_fixed(2))
        with self.assertRaises(ValueError):
            MODULE.invariant_small_set_is_pointwise_fixed(11)

    def test_row_sum_identity_values(self) -> None:
        self.assertEqual(MODULE.row_sum_rhs(11), 20)
        self.assertEqual(MODULE.row_sum_rhs(22), 42)
        self.assertEqual(MODULE.row_sum_rhs(99), 196)

    def test_f11_is_impossible(self) -> None:
        audit = MODULE.case_audit()["f11"]
        self.assertFalse(audit["degree14_possible_in_simple_graph"])
        self.assertEqual(audit["all_degree3_lhs"], 9)
        self.assertEqual(audit["required_rhs"], 20)
        self.assertTrue(audit["contradiction"])

    def test_f22_forces_bipartite_degree_types(self) -> None:
        audit = MODULE.case_audit()["f22"]
        self.assertEqual(audit["degree14_neighbors_of_degree3"], 3)
        self.assertEqual(audit["degree14_neighbors_of_degree14"], 0)
        self.assertEqual(audit["integer_partition_solutions"], [])

    def test_relaxation_keeps_only_empty_and_identity(self) -> None:
        models = MODULE.enumerate_fixed_graph_relaxation()
        self.assertEqual([model["f"] for model in models], [0, 99])
        self.assertEqual(models[-1]["degree14_vertices"], 99)
        self.assertEqual(models[-1]["degree14_neighbors_of_degree14_vertex"], 14)

    def test_exact_order_scope_excludes_identity_only_at_end(self) -> None:
        result = MODULE.build_result()
        self.assertTrue(result["identity_scope"]["identity_satisfies_g_to_11_equals_identity"])
        self.assertEqual(result["identity_scope"]["identity_order"], 1)
        self.assertTrue(result["identity_scope"]["identity_not_covered_by_primary_theorem"])
        self.assertEqual(result["positive_nonidentity_models"], [])

    def test_fixed_free_action_has_nine_orbits(self) -> None:
        result = MODULE.build_result()
        self.assertEqual(result["fixed_free_orbit_count"], 9)
        self.assertEqual(MODULE.V % MODULE.P, 0)

    def test_conditional_implication_stays_conditional(self) -> None:
        result = MODULE.build_result()
        conditional = result["conditional_implication"]
        self.assertEqual(
            conditional["premise"],
            "separate_complete_semiregular_C11_exclusion",
        )
        self.assertTrue(conditional["no_order11_automorphism"])
        self.assertTrue(conditional["no_vertex_transitive_realization"])
        self.assertIn("wave69_not_verified_here", result["limitations"])

    def test_semantic_hash_detects_mutation(self) -> None:
        result = MODULE.build_result()
        original = result["semantic_sha256"]
        result["fixed_free_orbit_count"] = 8
        self.assertNotEqual(MODULE.semantic_sha256(result), original)

    def test_discovery_comparison_rejects_changed_mathematics(self) -> None:
        independent = MODULE.build_result()
        discovery = {
            "parameters": independent["parameters"],
            "fixed_count_candidates": independent["fixed_count_candidates"],
            "fixed_degree_options": [3],
            "two_step_identity": independent["two_step_identity"],
            "feasible_fixed_degree_models": independent["feasible_fixed_degree_models"],
            "fixed_free_orbit_count": independent["fixed_free_orbit_count"],
        }
        with self.assertRaises(AssertionError):
            MODULE.compare_discovery(independent, discovery)

    def test_inventory_detects_byte_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "artifact.txt"
            target.write_bytes(b"frozen")
            digest = MODULE.hashlib.sha256(b"frozen").hexdigest()
            inventory = root / "inventory.tsv"
            inventory.write_text(
                f"path\tbytes\tsha256\nartifact.txt\t6\t{digest}\n",
                encoding="utf-8",
            )
            self.assertEqual(len(MODULE.verify_inventory(root, inventory)), 1)
            target.write_bytes(b"changed")
            with self.assertRaises(AssertionError):
                MODULE.verify_inventory(root, inventory)

    def test_canonical_result_verifies(self) -> None:
        payload = json.loads(
            Path(__file__).with_name("independent-results.json").read_text(
                encoding="utf-8"
            )
        )
        MODULE.verify_result(payload)


if __name__ == "__main__":
    unittest.main()

