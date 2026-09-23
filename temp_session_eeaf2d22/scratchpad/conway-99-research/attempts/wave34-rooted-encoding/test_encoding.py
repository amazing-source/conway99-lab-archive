#!/usr/bin/env python3
"""Exact unit tests for the complete-domain rooted encoding."""

from __future__ import annotations

import itertools
import json
import tempfile
import unittest
from pathlib import Path

import generate_cnf as gen
import check_witness
import decode_model


def clauses_satisfied(clauses: list[tuple[int, ...]], values: dict[int, bool]) -> bool:
    return all(
        any(values[abs(lit)] == (lit > 0) for lit in clause)
        for clause in clauses
    )


class EncodingTests(unittest.TestCase):
    def test_fixed_data_and_ss_block(self) -> None:
        support, labels, incidence = gen.canonical_fixed_data()
        audit = gen.fixed_audit(support, labels, incidence)
        self.assertTrue(all(audit["checks"].values()))
        self.assertEqual(28, audit["support_edge_count"])
        self.assertEqual({"0": 1806, "1": 588, "2": 21}, audit["FTF_offdiagonal_histogram"])

    def test_o_label_multiplicity(self) -> None:
        _, labels, _ = gen.canonical_fixed_data()
        counts: dict[tuple[int, int], int] = {}
        line_sets = [set(x) for x in gen.FANO_LINES]
        for label in labels:
            key = (label["point"], label["line"])
            counts[key] = counts.get(key, 0) + 1
        for (point, line), count in counts.items():
            self.assertEqual(2 if point in line_sets[line] else 1, count)

    def test_and_gadget_truth_table(self) -> None:
        clauses: list[tuple[int, ...]] = []
        builder = gen.CnfBuilder(clauses.append)
        x = builder.new_var("test", "x")
        y = builder.new_var("test", "y")
        z = builder.and2("test", x, y, "z")
        for xv, yv, zv in itertools.product((False, True), repeat=3):
            values = {x: xv, y: yv, z: zv}
            self.assertEqual(zv == (xv and yv), clauses_satisfied(clauses, values))

    def test_exact_cardinality_exhaustive_small(self) -> None:
        # Four inputs already exercise the constant, boundary, and general
        # recurrence cases while keeping the independent extension census tiny.
        for n in range(1, 5):
            for target in range(n + 1):
                clauses: list[tuple[int, ...]] = []
                builder = gen.CnfBuilder(clauses.append)
                xs = [builder.new_var("test", "x") for _ in range(n)]
                builder.exactly("test", xs, target)
                auxiliaries = list(range(n + 1, builder.variable_count + 1))
                for primary_values in itertools.product((False, True), repeat=n):
                    expected = sum(primary_values) == target
                    extendible = False
                    for aux_values in itertools.product((False, True), repeat=len(auxiliaries)):
                        values = {
                            var: value
                            for var, value in zip(xs + auxiliaries, primary_values + aux_values)
                        }
                        if clauses_satisfied(clauses, values):
                            extendible = True
                            break
                    self.assertEqual(
                        expected,
                        extendible,
                        msg=(n, target, primary_values, builder.variable_count, clauses),
                    )

    def test_primary_ranges_and_semantic_inventory(self) -> None:
        builder, d, b, fixed = gen.build_encoding()
        mapping = gen.primary_map(d, b, fixed["O_labels"])
        self.assertEqual(1, mapping["D"]["first_variable"])
        self.assertEqual(4900, mapping["D"]["last_variable"])
        self.assertEqual(4901, mapping["B"]["first_variable"])
        self.assertEqual(5950, mapping["B"]["last_variable"])
        self.assertEqual(5950, gen.semantic_inventory()["primary_binary_variables"]["total"])
        self.assertGreater(builder.variable_count, 5950)
        self.assertGreater(builder.clause_count, builder.variable_count)

    def test_semantic_family_counts(self) -> None:
        builder, _, _, _ = gen.build_encoding()
        expected = {
            "D_hollow": 70,
            "D_symmetry": 2415,
            "D_row_weight_9": 70,
            "B_row_weight_3": 70,
            "SQ_block_FB_equals_2J": 210,
            "SO_block_ASF_plus_FD": 980,
            "OO_block_diagonal": 70,
            "OO_block_offdiagonal": 2415,
            "OQ_block_DB": 1050,
            "QQ_block_column_weight_14": 15,
            "QQ_block_pair_intersection_2": 105,
        }
        observed = {
            name: stat.constraints
            for name, stat in builder.families.items()
            if name != "primary_variables"
        }
        self.assertEqual(expected, observed)

    def test_count_and_emit_passes_identical(self) -> None:
        emitted_clause_count = 0

        def discard_clause(_clause: tuple[int, ...]) -> None:
            nonlocal emitted_clause_count
            emitted_clause_count += 1

        counted, d1, b1, fixed1 = gen.build_encoding()
        emitted, d2, b2, fixed2 = gen.build_encoding(discard_clause)
        self.assertEqual(counted.variable_count, emitted.variable_count)
        self.assertEqual(counted.clause_count, emitted.clause_count)
        self.assertEqual(emitted.clause_count, emitted_clause_count)
        self.assertEqual(d1, d2)
        self.assertEqual(b1, b2)
        self.assertEqual(fixed1, fixed2)

    def test_audit_json_roundtrip(self) -> None:
        builder, _, _, fixed = gen.build_encoding()
        audit = gen.audit_document(builder, fixed)
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "audit.json"
            gen.write_json(path, audit)
            self.assertEqual(audit, json.loads(path.read_text(encoding="utf-8")))

    def test_independent_checker_rejects_fixed_skeleton(self) -> None:
        support, incidence = check_witness.expected_fixed_cells()
        adjacency = [[0] * 99 for _ in range(99)]
        for i in range(14):
            for j in range(14):
                adjacency[i][j] = support[i][j]
            for o in range(70):
                adjacency[i][14 + o] = adjacency[14 + o][i] = incidence[i][o]
        payload = {
            "adjacency": ["".join(str(x) for x in row) for row in adjacency]
        }
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "not-a-witness.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            result = check_witness.check(path)
        self.assertEqual("FAIL", result["status"])
        self.assertNotEqual(
            0, sum(result["checks"]["block_failure_counts"].values())
        )

    def test_decoder_rejects_partial_assignment(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "partial.model"
            path.write_text("s SATISFIABLE\nv 1 -2 0\n", encoding="utf-8")
            values = decode_model.parse_assignment(path)
        self.assertEqual({1: True, 2: False}, values)
        self.assertEqual(5948, len([v for v in range(1, 5951) if v not in values]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
