import copy
import unittest

import coherent_closure as subject


class CoherentClosureTests(unittest.TestCase):
    def test_partial_root_is_exactly_three_k6(self):
        labels, colors = subject.partial_triangle_structure()
        self.assertEqual(len(labels), 19)
        root = labels.index("root")
        self.assertEqual(colors[root].count("K_root_to_petal"), 18)
        for row, label in enumerate(labels):
            if label != "root":
                self.assertEqual(colors[row].count("K_same_sector"), 5)
                self.assertEqual(colors[row].count("U"), 12)

    def test_constraint_template_degrees(self):
        labels, tokens = subject.constraint_template_structure()
        checks = subject.validate_constraint_template(labels, tokens)
        self.assertEqual(
            checks["node_counts"],
            {"candidate_B": 108, "cap_exactly_2": 36, "petal": 18, "root": 1},
        )

    def test_all_four_bipartite_cycle_types(self):
        for partition in subject.CYCLE_PARTITIONS:
            edges = subject.bipartite_two_factor(partition)
            subject.verify_two_factor(edges)

    def test_bad_cycle_partitions_fail_closed(self):
        for partition in ((5, 1), (3, 2), (2, 2, 1, 1), (2, 4)):
            with self.assertRaises(ValueError):
                subject.bipartite_two_factor(partition)

    def test_bad_two_factor_fails_closed(self):
        edges = set(subject.bipartite_two_factor((6,)))
        edges.remove(next(iter(edges)))
        with self.assertRaises(AssertionError):
            subject.verify_two_factor(edges)

    def test_completed_rows_have_forced_caps(self):
        completion = subject.completion_from_profile(((6,), (4, 2), (3, 3)))
        labels, colors = subject.completed_triangle_structure(completion)
        subject.verify_completed_triangle_relations(labels, colors)

    def test_mutated_completion_fails_closed(self):
        completion = subject.completion_from_profile(((6,), (6,), (6,)))
        damaged = copy.deepcopy(completion)
        damaged[(0, 1)] = frozenset(set(damaged[(0, 1)]) - {(0, 0)})
        with self.assertRaises(AssertionError):
            subject.completed_triangle_structure(damaged)

    def test_2wl_certificate_is_coherent(self):
        _, tokens = subject.partial_triangle_structure()
        closure = subject.wl2(tokens)
        self.assertGreaterEqual(
            closure["stable_color_count"], closure["initial_color_count"]
        )
        subject.coherent_certificate(closure["pair_color_matrix"])

    def test_completion_examples_have_different_closures(self):
        fingerprints = []
        for profile in ((((6,),) * 3), (((2, 2, 2),) * 3)):
            completion = subject.completion_from_profile(profile)
            _, tokens = subject.completed_triangle_structure(completion)
            fingerprints.append(
                subject.wl2(tokens)["invariant_fingerprint_sha256"]
            )
        self.assertNotEqual(*fingerprints)

    def test_full_result_keeps_status_wall(self):
        result = subject.build_results()
        self.assertFalse(result["result"]["exact_contradiction"])
        self.assertFalse(result["result"]["new_forced_color_obstruction"])
        self.assertEqual(result["claim_boundary"]["conway_99"], "UNKNOWN")
        self.assertEqual(
            result["canonical_completion_diagnostic"]["profile_count"], 64
        )
        self.assertEqual(
            result["completion_free_constraint_template"]["diagonal_class_sizes"],
            [1, 18, 36, 108],
        )


if __name__ == "__main__":
    unittest.main()
