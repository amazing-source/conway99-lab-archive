from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "wave39_independent_check", ROOT / "independent_check.py"
)
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load independent checker")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class IndependentCheckTests(unittest.TestCase):
    def test_full_static_verification(self):
        result = checker.verify(False)
        self.assertEqual(result["generalized_unit_argument"], "PASS")
        self.assertEqual(result["closed_endpoint_cases"], 0)
        self.assertEqual(result["branch_15_status"], "UNKNOWN")

    def test_capacity_has_negated_x2_and_exact_range(self):
        _, lines = checker.load_source()
        literals, bound = checker.parse(lines[571132])
        self.assertEqual(literals[:-1], [(x, False) for x in range(3569, 3651)])
        self.assertEqual(literals[-1], (2, False))
        self.assertEqual(bound, 82)

    def test_wrong_x2_polarity_breaks_tightness(self):
        _, lines = checker.load_source()
        mutated = dict(lines)
        mutated[571132] = mutated[571132].replace("+1 ~x2", "+1 x2")
        with self.assertRaises(ValueError):
            checker.check_local_argument(mutated)

    def test_wrong_wedge_polarity_rejected(self):
        _, lines = checker.load_source()
        mutated = dict(lines)
        mutated[106] = mutated[106].replace("+1 x3591", "+1 ~x3591")
        with self.assertRaises(ValueError):
            checker.check_local_argument(mutated)

    def test_shard_must_be_exact_append_unit_transform(self):
        source, _ = checker.load_source()
        with mock.patch.object(checker, "SHARD_RAW_SHA", "0" * 64):
            with self.assertRaises(ValueError):
                checker.check_shard_transform(source)

    def test_proof_hash_mutation_rejected(self):
        with mock.patch.object(checker, "RAW_PROOF_SHA", "0" * 64):
            with self.assertRaises(ValueError):
                checker.check_proof_artifacts()


if __name__ == "__main__":
    unittest.main()
