#!/usr/bin/env python3
"""Small independent text-DRUP checker for calibration and audit.

This checker prioritizes clarity over performance. It validates every added
clause by reverse unit propagation, honors deletion lines, and requires a final
empty clause. It is suitable for small calibration proofs; target-scale proof
checking should additionally use a mature independently pinned checker.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


class ProofFormatError(ValueError):
    pass


Clause = tuple[int, ...]


def canonical_clause(literals: Iterable[int]) -> Clause:
    return tuple(sorted(set(literals), key=lambda literal: (abs(literal), literal < 0)))


def parse_dimacs(path: Path) -> tuple[int, list[Clause]]:
    variables: int | None = None
    declared_clauses: int | None = None
    tokens: list[int] = []

    try:
        lines = path.read_text(encoding="ascii").splitlines()
    except OSError as exc:
        raise ProofFormatError(f"cannot read CNF: {exc}") from exc

    for line_number, raw_line in enumerate(lines, 1):
        line = raw_line.strip()
        if not line or line.startswith("c"):
            continue
        if line.startswith("p"):
            parts = line.split()
            if len(parts) != 4 or parts[:2] != ["p", "cnf"]:
                raise ProofFormatError(f"invalid DIMACS header on line {line_number}")
            if variables is not None:
                raise ProofFormatError("multiple DIMACS headers")
            try:
                variables = int(parts[2])
                declared_clauses = int(parts[3])
            except ValueError as exc:
                raise ProofFormatError("noninteger DIMACS header") from exc
            continue
        try:
            tokens.extend(int(token) for token in line.split())
        except ValueError as exc:
            raise ProofFormatError(f"noninteger CNF token on line {line_number}") from exc

    if variables is None or declared_clauses is None:
        raise ProofFormatError("missing DIMACS header")
    if variables < 0 or declared_clauses < 0:
        raise ProofFormatError("negative DIMACS count")

    clauses: list[Clause] = []
    current: list[int] = []
    for token in tokens:
        if token == 0:
            clauses.append(canonical_clause(current))
            current = []
        else:
            if abs(token) > variables:
                raise ProofFormatError(f"literal {token} exceeds declared variable count")
            current.append(token)
    if current:
        raise ProofFormatError("last DIMACS clause is missing its terminating zero")
    if len(clauses) != declared_clauses:
        raise ProofFormatError(
            f"DIMACS declares {declared_clauses} clauses but contains {len(clauses)}"
        )
    return variables, clauses


def parse_proof(path: Path, variables: int) -> list[tuple[bool, Clause]]:
    operations: list[tuple[bool, Clause]] = []
    try:
        lines = path.read_text(encoding="ascii").splitlines()
    except OSError as exc:
        raise ProofFormatError(f"cannot read proof: {exc}") from exc

    for line_number, raw_line in enumerate(lines, 1):
        line = raw_line.strip()
        if not line or line.startswith("c"):
            continue
        parts = line.split()
        deletion = parts[0] == "d"
        if deletion:
            parts = parts[1:]
        try:
            literals = [int(token) for token in parts]
        except ValueError as exc:
            raise ProofFormatError(f"noninteger proof token on line {line_number}") from exc
        if not literals or literals[-1] != 0:
            raise ProofFormatError(f"proof line {line_number} is missing its terminating zero")
        if 0 in literals[:-1]:
            raise ProofFormatError(f"proof line {line_number} has an early zero")
        clause = canonical_clause(literals[:-1])
        if any(abs(literal) > variables for literal in clause):
            raise ProofFormatError(f"proof line {line_number} exceeds the CNF variable range")
        operations.append((deletion, clause))
    return operations


@dataclass
class ClauseDatabase:
    clauses: list[Clause]
    active: list[bool]

    @classmethod
    def from_clauses(cls, clauses: Sequence[Clause]) -> "ClauseDatabase":
        return cls(list(clauses), [True] * len(clauses))

    def add(self, clause: Clause) -> None:
        self.clauses.append(clause)
        self.active.append(True)

    def delete(self, clause: Clause) -> bool:
        for index in range(len(self.clauses) - 1, -1, -1):
            if self.active[index] and self.clauses[index] == clause:
                self.active[index] = False
                return True
        return False

    def active_clauses(self) -> Iterable[Clause]:
        return (
            clause
            for clause, active in zip(self.clauses, self.active)
            if active
        )


def is_rup(database: ClauseDatabase, clause: Clause, variables: int) -> bool:
    """Return true iff negating clause and unit-propagating reaches conflict."""

    assignment = [0] * (variables + 1)

    def assign(literal: int) -> int:
        """Return -1 for conflict, 0 if already assigned, and 1 if newly set."""

        variable = abs(literal)
        value = 1 if literal > 0 else -1
        if assignment[variable] == -value:
            return -1
        if assignment[variable] == value:
            return 0
        assignment[variable] = value
        return 1

    for literal in clause:
        if assign(-literal) == -1:
            return True

    changed = True
    while changed:
        changed = False
        for candidate in database.active_clauses():
            satisfied = False
            unit_literal = 0
            unassigned = 0
            for literal in candidate:
                value = assignment[abs(literal)]
                if value == (1 if literal > 0 else -1):
                    satisfied = True
                    break
                if value == 0:
                    unassigned += 1
                    unit_literal = literal
            if satisfied:
                continue
            if unassigned == 0:
                return True
            if unassigned == 1:
                assignment_result = assign(unit_literal)
                if assignment_result == -1:
                    return True
                if assignment_result == 1:
                    changed = True
    return False


def check_proof(cnf_path: Path, proof_path: Path) -> dict[str, object]:
    variables, clauses = parse_dimacs(cnf_path)
    operations = parse_proof(proof_path, variables)
    database = ClauseDatabase.from_clauses(clauses)
    additions = 0
    deletions = 0
    ignored_deletions = 0
    empty_clause_step: int | None = None

    for step, (deletion, clause) in enumerate(operations, 1):
        if deletion:
            deletions += 1
            if not database.delete(clause):
                # DRUP deletion hints are optional for correctness. A deletion
                # of an absent duplicate is harmless and is reported.
                ignored_deletions += 1
            continue

        additions += 1
        if not is_rup(database, clause, variables):
            return {
                "valid": False,
                "reason": "non-RUP addition",
                "failed_step": step,
                "failed_clause": list(clause),
                "variables": variables,
                "initial_clauses": len(clauses),
                "additions_checked": additions,
                "deletions": deletions,
                "ignored_deletions": ignored_deletions,
            }
        database.add(clause)
        if not clause:
            empty_clause_step = step
            break

    if empty_clause_step is None:
        return {
            "valid": False,
            "reason": "proof contains no checked empty clause",
            "variables": variables,
            "initial_clauses": len(clauses),
            "additions_checked": additions,
            "deletions": deletions,
            "ignored_deletions": ignored_deletions,
        }
    return {
        "valid": True,
        "variables": variables,
        "initial_clauses": len(clauses),
        "proof_operations": len(operations),
        "additions_checked": additions,
        "deletions": deletions,
        "ignored_deletions": ignored_deletions,
        "empty_clause_step": empty_clause_step,
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cnf", type=Path)
    parser.add_argument("proof", type=Path)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        report = check_proof(args.cnf, args.proof)
    except ProofFormatError as exc:
        print(f"malformed proof input: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
