from __future__ import annotations

import copy
import json
import unittest

import independent_check as check


class Wave63HostileMutationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = json.loads(check.RESULT_PATH.read_text(encoding="utf-8"))
        type_data = json.loads(check.TYPE_PATH.read_text(encoding="utf-8"))
        cls.types = check.load_types(type_data)
        cls.allowed = tuple(
            check.allowed_pairs_by_profile(record) for record in cls.types
        )
        cls.triple = (0, 0, 0)
        cls.target = check.target_pair_values([cls.types[0]] * 3)
        cls.candidates = check.candidate_columns(
            cls.triple, cls.allowed, cls.target
        )
        cls.witness = cls.result["results"][0]["rational_cone"]["exact_witness"]

    def test_positive_first_lane(self) -> None:
        replay = check.verify_witness(
            self.witness, self.candidates, self.target
        )
        self.assertEqual(replay["support_size"], 438)
        self.assertEqual(replay["total_weight"], "60")

    def test_mutated_coefficient_rejected(self) -> None:
        witness = copy.deepcopy(self.witness)
        witness[0]["numerator"] += 1
        with self.assertRaisesRegex(check.VerificationError, "pair equation"):
            check.verify_witness(witness, self.candidates, self.target)

    def test_mutated_denominator_sign_rejected(self) -> None:
        witness = copy.deepcopy(self.witness)
        witness[0]["denominator"] *= -1
        with self.assertRaisesRegex(check.VerificationError, "denominator"):
            check.verify_witness(witness, self.candidates, self.target)

    def test_out_of_range_candidate_index_rejected(self) -> None:
        witness = copy.deepcopy(self.witness)
        witness[0]["candidate_index"] = len(self.candidates)
        with self.assertRaisesRegex(check.VerificationError, "out of range"):
            check.verify_witness(witness, self.candidates, self.target)

    def test_duplicate_candidate_index_rejected(self) -> None:
        witness = copy.deepcopy(self.witness)
        witness[1]["candidate_index"] = witness[0]["candidate_index"]
        with self.assertRaisesRegex(check.VerificationError, "duplicate"):
            check.verify_witness(witness, self.candidates, self.target)

    def test_mutated_target_equation_rejected(self) -> None:
        target = list(self.target)
        target[0] += 1
        with self.assertRaisesRegex(check.VerificationError, "pair equation"):
            check.verify_witness(self.witness, self.candidates, target)

    def test_mutated_lane_selection_rejected(self) -> None:
        wave61 = json.loads(check.WAVE61_PATH.read_text(encoding="utf-8"))
        result = dict(self.result)
        result["results"] = self.result["results"][:-1]
        with self.assertRaisesRegex(check.VerificationError, "selection"):
            check.verify_selection(
                result, wave61["triple_census"]["records"], 15936, 27200
            )

    def test_milp_nonhit_stays_unknown(self) -> None:
        summary = check.verify_milp_metadata(self.result["results"])
        self.assertEqual(summary["status"], "UNKNOWN")
        self.assertEqual(summary["proof_certificates"], 0)


if __name__ == "__main__":
    unittest.main()
