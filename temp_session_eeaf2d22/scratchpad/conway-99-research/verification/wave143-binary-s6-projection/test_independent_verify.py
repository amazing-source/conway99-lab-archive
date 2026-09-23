"""Hostile tests for the clean-room Wave143 verifier."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave143_independent_verify",
    HERE / "independent_verify.py",
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load independent verifier")
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)


class Wave143IndependentTests(unittest.TestCase):
    def test_frozen_manifest(self) -> None:
        audit = VERIFY.audit_manifest()
        self.assertTrue(audit["pass"])
        self.assertEqual(
            audit["observed_manifest_sha256"],
            VERIFY.DISCOVERY_MANIFEST_SHA256,
        )

    def test_input_freeze(self) -> None:
        self.assertTrue(VERIFY.audit_input_freeze()["pass"])

    def test_independent_s6(self) -> None:
        result = VERIFY.independently_derive_s6()
        self.assertEqual(result["constant"], "2024484")
        self.assertEqual(result["n3_coefficient"], "512/3")
        self.assertEqual(result["class_count"], 62)

    def test_weak_projection_bounds(self) -> None:
        proof = VERIFY.weak_projection_proof()
        self.assertEqual(proof["exact_n3_min"], "0")
        self.assertEqual(proof["exact_n3_max"], "838878579/128")
        self.assertEqual(
            proof["raw_two_sided_shadow_n3_min"],
            "-841915305/128",
        )

    def test_endpoint_replay(self) -> None:
        audit = VERIFY.audit_point(
            VERIFY.DISCOVERY / "witness-plus-n3-708.json",
            1,
            Fraction(708),
        )
        self.assertTrue(audit["pass"], audit["failures"])
        self.assertEqual(audit["shadow_row_count"], 100)
        self.assertTrue(audit["split_systems"]["pass"])

    def _mutated_audit(self, mutator) -> dict:
        source = VERIFY.DISCOVERY / "witness-plus-n3-708.json"
        payload = json.loads(source.read_text(encoding="utf-8"))
        mutator(payload)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mutated.json"
            path.write_text(
                json.dumps(payload),
                encoding="utf-8",
            )
            return VERIFY.audit_point(path, 1, Fraction(708))

    def test_mutated_ordinary_coefficient_is_rejected(self) -> None:
        def mutate(payload):
            value = Fraction(
                payload["ordinary"]["image_coefficients"]["14"]
            )
            payload["ordinary"]["image_coefficients"]["14"] = str(value + 1)

        audit = self._mutated_audit(mutate)
        self.assertFalse(audit["pass"])

    def test_mutated_n3_is_rejected(self) -> None:
        audit = self._mutated_audit(
            lambda payload: payload.__setitem__("n3", "711")
        )
        self.assertFalse(audit["pass"])
        self.assertTrue(
            any("submitted n3" in failure for failure in audit["failures"])
        )

    def test_mutated_split_entry_is_rejected(self) -> None:
        def mutate(payload):
            table = payload["split_enumerators"][
                "image_vs_neighborhood"
            ]["14"]
            key = next(iter(table))
            table[key] = str(Fraction(table[key]) + 1)

        audit = self._mutated_audit(mutate)
        self.assertFalse(audit["pass"])
        self.assertFalse(audit["split_systems"]["pass"])

    def test_small_equality_projection(self) -> None:
        for sign in (-1, 1):
            result = VERIFY.integral_equality_projection(sign)
            self.assertEqual(result["exact_projection"], "n3 in 3Z")
            self.assertEqual(
                result["residue_membership_mod_3"],
                {"0": True, "1": False, "2": False},
            )

    def test_full_hnf_vectors_are_reconstructed(self) -> None:
        result = VERIFY.audit_full_lattice_certificate()
        self.assertTrue(result["submitted_hashes_critically_reconstructed"])
        self.assertEqual(result["rank"], 109)
        self.assertEqual(result["nullity"], 33)
        self.assertEqual(result["kernel_projection_gcd_in_k"], 1)
        self.assertTrue(
            result["homogeneous_steps_delta_k1"]["plus"]["replay_pass"]
        )
        self.assertTrue(
            result["homogeneous_steps_delta_k1"]["minus"]["replay_pass"]
        )

    def test_target_scope_veto_is_present(self) -> None:
        result = json.loads(
            (HERE / "verification-results.json").read_text(encoding="utf-8")
        )
        premise = result["premise_audit"]
        self.assertIn("d(ker A)>=8", " ".join(premise["target_forced"]))
        self.assertIn(
            "B_1=...=B_14=0",
            " ".join(premise["strengthened_formal_slice"]),
        )
        self.assertIn("vetoed", premise["verifier_veto"])


if __name__ == "__main__":
    unittest.main()
