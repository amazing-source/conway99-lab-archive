"""Tests for the Wave 110 lex symmetry breaker and domain audit."""

from __future__ import annotations

import itertools
import json
import unittest

import symmetry_sat as subject


def literal_value(literal: int, assignment: dict[int, bool]) -> bool:
    value = assignment[abs(literal)]
    return value if literal > 0 else not value


class LexEncodingTests(unittest.TestCase):
    def test_truth_table_exhaustive_through_length_four(self) -> None:
        for length in range(5):
            left_ids = tuple(range(1, length + 1))
            right_ids = tuple(range(length + 1, 2 * length + 1))
            next_id = 2 * length + 1
            clauses: list[list[int]] = []

            def new_variable(_key: tuple[object, ...]) -> int:
                nonlocal next_id
                value = next_id
                next_id += 1
                return value

            auxiliary_count, _ = subject.add_lex_leq(
                left_ids,
                right_ids,
                new_variable,
                clauses.append,
                ("truth-table", length),
            )
            auxiliary_ids = tuple(range(2 * length + 1, next_id))
            self.assertEqual(len(auxiliary_ids), auxiliary_count)

            for left in itertools.product((False, True), repeat=length):
                for right in itertools.product((False, True), repeat=length):
                    base = {
                        variable: value
                        for variable, value in zip(left_ids + right_ids, left + right)
                    }
                    satisfiable = False
                    for auxiliary in itertools.product(
                        (False, True), repeat=auxiliary_count
                    ):
                        assignment = base | dict(zip(auxiliary_ids, auxiliary))
                        if all(
                            any(literal_value(literal, assignment) for literal in row)
                            for row in clauses
                        ):
                            satisfiable = True
                            break
                    self.assertEqual(
                        satisfiable,
                        left <= right,
                        (length, left, right, clauses),
                    )

    def test_small_clause_and_auxiliary_formula(self) -> None:
        for length in range(1, 8):
            next_id = 2 * length + 1
            clauses: list[list[int]] = []

            def new_variable(_key: tuple[object, ...]) -> int:
                nonlocal next_id
                value = next_id
                next_id += 1
                return value

            auxiliaries, clause_count = subject.add_lex_leq(
                tuple(range(1, length + 1)),
                tuple(range(length + 1, 2 * length + 1)),
                new_variable,
                clauses.append,
                ("counts", length),
            )
            self.assertEqual(auxiliaries, max(0, length - 1))
            self.assertEqual(
                clause_count,
                1 if length == 1 else 6 * length - 6,
            )
            self.assertEqual(len(clauses), clause_count)


class DomainAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.audit = subject.symmetry_domain_audit()

    def test_wave105_domain_counts(self) -> None:
        self.assertEqual(self.audit["wave105_domain"]["outside_vertices"], 87)
        self.assertEqual(self.audit["wave105_domain"]["edge_variables"], 3741)
        self.assertEqual(
            self.audit["wave105_domain"]["common_conjunction_variables"],
            317985,
        )
        self.assertEqual(
            self.audit["wave105_domain"]["distinct_linear_incidence_rows"],
            1044,
        )

    def test_pattern_class_census(self) -> None:
        classes = self.audit["fixed_pattern_classes"]
        self.assertEqual(classes["count"], 37)
        self.assertEqual(
            classes["multiplicity_histogram"],
            {"1": 12, "2": 12, "3": 1, "4": 12},
        )
        vertices = [
            vertex
            for row in classes["rows"]
            for vertex in row["vertices"]
        ]
        self.assertEqual(sorted(vertices), list(range(87)))

    def test_lex_domain_counts(self) -> None:
        lex = self.audit["lex_encoding"]
        self.assertEqual(lex["comparisons"], 50)
        self.assertEqual(lex["compared_bit_positions"], 4176)
        self.assertEqual(lex["auxiliary_variables"], 4126)
        self.assertEqual(lex["cnf_clauses"], 24756)

    def test_full_submission_counts(self) -> None:
        full = self.audit["full_solver_submission"]
        self.assertEqual(full["total_variables"], 325852)
        self.assertEqual(full["total_cnf_clauses"], 978711)
        self.assertEqual(full["exact_cardinality_rows"], 4873)
        self.assertEqual(full["native_atmost_constraints"], 9746)

    def test_x0_branch_is_label_invariant(self) -> None:
        branch = self.audit["branch_partition"]
        self.assertEqual(branch["values"], [0, 1, 2, 3])
        self.assertIn("no labelled representative", branch["implementation"])


class ArchivedRunTests(unittest.TestCase):
    def test_all_bounded_runs_fail_closed_and_preserve_ram(self) -> None:
        expected = subject.symmetry_domain_audit()["full_solver_submission"]
        for branch in range(4):
            path = (
                subject.PACKAGE
                / "raw-logs"
                / f"wave110-branch{branch}-45s.json"
            )
            row = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(row["branch_eX0"], branch)
            self.assertEqual(row["claim_label"], "UNKNOWN")
            self.assertEqual(row["result"], "UNKNOWN_TIMEOUT")
            self.assertTrue(row["timed_out"])
            self.assertTrue(row["reserve_preserved_after_run"])
            self.assertGreaterEqual(
                row["free_memory_fraction_before"],
                row["ram_build_floor"],
            )
            self.assertGreaterEqual(
                row["free_memory_fraction_after"],
                row["ram_required_reserve"],
            )
            self.assertEqual(row["total_variables"], expected["total_variables"])
            self.assertEqual(
                row["total_cnf_clauses_submitted"],
                expected["total_cnf_clauses"],
            )
            self.assertEqual(
                row["native_atmost_constraints_submitted"],
                expected["native_atmost_constraints"],
            )


if __name__ == "__main__":
    unittest.main()
