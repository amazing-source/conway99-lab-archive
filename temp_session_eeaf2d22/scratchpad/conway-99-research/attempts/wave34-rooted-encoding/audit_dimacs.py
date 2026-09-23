#!/usr/bin/env python3
"""Independent streaming audit of the emitted DIMACS and its explicit D gates.

This module does not import the formula generator.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path


def expected_gate_prefix() -> list[tuple[int, ...]]:
    def d(i: int, j: int) -> int:
        return 1 + 70 * i + j

    clauses: list[tuple[int, ...]] = []
    for i in range(70):
        clauses.append((-d(i, i),))
    for i in range(70):
        for j in range(i + 1, 70):
            clauses.append((-d(i, j), d(j, i)))
            clauses.append((d(i, j), -d(j, i)))
    return clauses


def audit(path: Path) -> dict[str, object]:
    digest = hashlib.sha256()
    header_variables: int | None = None
    header_clauses: int | None = None
    clause_count = 0
    length_histogram: Counter[int] = Counter()
    tautologies = 0
    repeated_literals = 0
    malformed: list[dict[str, object]] = []
    explicit_prefix = expected_gate_prefix()
    prefix_mismatches: list[dict[str, object]] = []
    seen: bytearray | None = None
    maximum_variable = 0

    with path.open("rb") as raw:
        for line_number, raw_line in enumerate(raw, start=1):
            digest.update(raw_line)
            try:
                line = raw_line.decode("ascii").strip()
            except UnicodeDecodeError as exc:
                malformed.append({"line": line_number, "error": str(exc)})
                continue
            if not line or line.startswith("c"):
                continue
            if header_variables is None:
                parts = line.split()
                if len(parts) != 4 or parts[:2] != ["p", "cnf"]:
                    malformed.append(
                        {"line": line_number, "error": "invalid or missing p cnf header"}
                    )
                    continue
                header_variables, header_clauses = int(parts[2]), int(parts[3])
                seen = bytearray(header_variables + 1)
                continue

            try:
                tokens = [int(token) for token in line.split()]
            except ValueError as exc:
                malformed.append({"line": line_number, "error": str(exc)})
                continue
            if not tokens or tokens[-1] != 0 or 0 in tokens[:-1]:
                malformed.append(
                    {"line": line_number, "error": "clause must have one terminal zero"}
                )
                continue
            clause = tuple(tokens[:-1])
            clause_count += 1
            length_histogram[len(clause)] += 1
            literal_set = set(clause)
            repeated_literals += len(clause) - len(literal_set)
            if any(-literal in literal_set for literal in literal_set):
                tautologies += 1
            for literal in clause:
                variable = abs(literal)
                if variable == 0 or variable > header_variables:
                    malformed.append(
                        {
                            "line": line_number,
                            "error": "literal outside declared variable range",
                            "literal": literal,
                        }
                    )
                else:
                    assert seen is not None
                    seen[variable] = 1
                    maximum_variable = max(maximum_variable, variable)
            if clause_count <= len(explicit_prefix):
                expected = explicit_prefix[clause_count - 1]
                if clause != expected and len(prefix_mismatches) < 20:
                    prefix_mismatches.append(
                        {
                            "clause": clause_count,
                            "observed": list(clause),
                            "expected": list(expected),
                        }
                    )

    if header_variables is None or header_clauses is None:
        malformed.append({"line": 0, "error": "no DIMACS header found"})
        header_variables = 0
        header_clauses = 0
        seen = bytearray(1)
    assert seen is not None
    missing_primary = [i for i in range(1, min(5950, header_variables) + 1) if not seen[i]]
    missing_any_count = sum(1 for i in range(1, header_variables + 1) if not seen[i])
    checks = {
        "header_clause_count_matches": clause_count == header_clauses,
        "maximum_variable_matches_header": maximum_variable == header_variables,
        "no_malformed_lines": not malformed,
        "no_tautological_clauses": tautologies == 0,
        "no_repeated_literals": repeated_literals == 0,
        "all_primary_variables_occur": not missing_primary,
        "all_declared_variables_occur": missing_any_count == 0,
        "explicit_D_hollow_and_symmetry_prefix": not prefix_mismatches
        and clause_count >= len(explicit_prefix),
    }
    return {
        "schema_version": 1,
        "role": "independent_formula_syntax_and_gate_auditor",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "input": str(path),
        "input_sha256": digest.hexdigest(),
        "header": {"variables": header_variables, "clauses": header_clauses},
        "observed": {
            "clauses": clause_count,
            "maximum_variable": maximum_variable,
            "clause_length_histogram": {
                str(k): length_histogram[k] for k in sorted(length_histogram)
            },
            "tautologies": tautologies,
            "repeated_literals": repeated_literals,
            "missing_primary_variables": missing_primary[:20],
            "missing_declared_variable_count": missing_any_count,
            "explicit_gate_prefix_clauses_checked": len(explicit_prefix),
        },
        "checks": checks,
        "malformed": malformed[:20],
        "prefix_mismatches": prefix_mismatches,
        "limitations": [
            "This audit checks DIMACS syntax, declared ranges/counts, variable occurrence, and the independently reconstructed explicit D gates.",
            "The semantic equation-to-CNF mapping is additionally exercised by the generator unit tests and the independent full-graph witness checker.",
            "This is not a SAT, UNSAT, or proof-checking result.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cnf", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.cnf)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
