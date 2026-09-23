import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("independent_check.py")
SPEC = importlib.util.spec_from_file_location("wave54_independent", MODULE_PATH)
assert SPEC and SPEC.loader
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)

AUDIT_PATH = Path(__file__).with_name("audit_discovery.py")
AUDIT_SPEC = importlib.util.spec_from_file_location("wave54_audit", AUDIT_PATH)
assert AUDIT_SPEC and AUDIT_SPEC.loader
AUDIT = importlib.util.module_from_spec(AUDIT_SPEC)
AUDIT_SPEC.loader.exec_module(AUDIT)


def polynomial_krawtchouk(j: int, i: int, q: int, n: int) -> int:
    """Independent coefficient extraction from (1+(q-1)z)^(n-i)(1-z)^i."""

    coefficients = [1]
    for factor in [q - 1] * (n - i) + [-1] * i:
        nxt = coefficients + [0]
        for degree, value in enumerate(coefficients):
            nxt[degree + 1] += factor * value
        coefficients = nxt
    return coefficients[j]


class DirectFormulaTests(unittest.TestCase):
    def test_direct_formula_against_polynomial_expansion(self):
        for n in range(0, 10):
            for q in (2, 3, 4, 5):
                for i in range(n + 1):
                    for j in range(n + 1):
                        self.assertEqual(
                            CHECK.krawtchouk_direct(j, i, q=q, n=n),
                            polynomial_krawtchouk(j, i, q, n),
                        )

    def test_candidate_transform_and_sizes(self):
        a = CHECK.dense_candidate()
        b, numerators = CHECK.macwilliams_direct(a)
        self.assertEqual(len(b), 232)
        self.assertEqual(sum(a), 3**11)
        self.assertEqual(sum(b), 3**220)
        self.assertTrue(all(value % 3**11 == 0 for value in numerators))
        self.assertEqual(CHECK.condition_failures(a, b), [])
        self.assertTrue(all(value % 2 == 0 for value in b[1:]))
        self.assertTrue(
            all((b[i] - a[i]) % 2 == 0 for i in range(1, 232))
        )
        self.assertGreaterEqual(b[231], 2)

    def test_resource_floor(self):
        self.assertGreaterEqual(
            CHECK.enforce_memory_floor(), CHECK.MIN_FREE_MEMORY_PERCENT
        )


class HostileMutationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a = CHECK.dense_candidate()
        cls.b, _ = CHECK.macwilliams_direct(cls.a)

    def assert_mutation_caught(self, a, b, label):
        self.assertIn(label, CHECK.condition_failures(a, b))

    def test_A0_mutation(self):
        a = self.a.copy()
        a[0] = 0
        self.assert_mutation_caught(a, self.b, "A0")

    def test_total_size_mutation(self):
        a = self.a.copy()
        a[18] += 2
        self.assert_mutation_caught(a, self.b, "A size")

    def test_support_divisibility_mutation(self):
        a = self.a.copy()
        a[18] -= 2
        a[19] += 2
        self.assert_mutation_caught(a, self.b, "A support divisible by 3")

    def test_evenness_mutation(self):
        a = self.a.copy()
        a[144] -= 1
        a[153] += 1
        self.assert_mutation_caught(a, self.b, "nonzero A even")

    def test_A198_floor_mutation(self):
        a = self.a.copy()
        a[198] -= 2
        a[162] += 2
        self.assert_mutation_caught(a, self.b, "A198 lower bound")

    def test_B_integrality_mutation(self):
        b = self.b.copy()
        b[0] = 0.5
        self.assert_mutation_caught(self.a, b, "B integral")

    def test_B_nonnegative_mutation(self):
        b = self.b.copy()
        b[100] = -1
        self.assert_mutation_caught(self.a, b, "B nonnegative")

    def test_projectivity_mutation(self):
        b = self.b.copy()
        b[1] = 1
        self.assert_mutation_caught(self.a, b, "projectivity B1=B2=0")

    def test_formal_dominance_mutation(self):
        b = self.b.copy()
        b[198] = self.a[198] - 1
        self.assert_mutation_caught(
            self.a, b, "formal self-orthogonal dominance"
        )

    def test_each_dual_lower_bound_mutation(self):
        for weight, lower in CHECK.DUAL_LOWER_BOUNDS.items():
            with self.subTest(weight=weight):
                b = self.b.copy()
                b[weight] = lower - 1
                self.assert_mutation_caught(
                    self.a, b, f"B{weight} lower bound"
                )

    def test_dual_size_mutation(self):
        b = self.b.copy()
        b[231] -= 1
        self.assert_mutation_caught(self.a, b, "dual size")

    def test_macwilliams_equality_mutation(self):
        b = self.b.copy()
        b[100] += 1
        self.assert_mutation_caught(self.a, b, "MacWilliams equality")

    def test_macwilliams_integrality_mutation(self):
        a = self.a.copy()
        a[18] += 2
        failures = CHECK.condition_failures(a, self.b)
        self.assertIn("MacWilliams integrality", failures)

    def test_candidate_document_round_trip(self):
        first = CHECK.build_result()
        second = CHECK.build_result()
        self.assertEqual(first, second)


class DiscoveryAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.independent = json.loads(
            AUDIT.INDEPENDENT.read_text(encoding="utf-8")
        )
        cls.discovery = json.loads(AUDIT.DISCOVERY.read_text(encoding="utf-8"))

    def test_live_discovery_audit(self):
        self.assertTrue(AUDIT.build_audit()["all_checks_pass"])

    def test_hostile_discovery_A_mutation(self):
        mutated = copy.deepcopy(self.discovery)
        mutated["primal_enumerator_nonzero"]["18"] += 2
        compared = AUDIT.compare_payloads(self.independent, mutated)
        self.assertFalse(compared["all_232_A_coefficients_equal"])

    def test_hostile_discovery_B_mutation(self):
        mutated = copy.deepcopy(self.discovery)
        mutated["dual_enumerator_nonzero"]["100"] += 1
        compared = AUDIT.compare_payloads(self.independent, mutated)
        self.assertFalse(compared["all_232_B_coefficients_equal"])

    def test_hostile_expected_hash_mutation(self):
        actual = AUDIT.sha256_path(AUDIT.DISCOVERY)
        self.assertNotEqual("0" * 64, actual)

    def test_every_discovery_manifest_entry(self):
        for path in (AUDIT.INPUT_MANIFEST, AUDIT.PACKAGE_MANIFEST):
            with self.subTest(path=path):
                result = AUDIT.validate_manifest(path)
                self.assertTrue(result["all_entries_pass"])


if __name__ == "__main__":
    unittest.main()
