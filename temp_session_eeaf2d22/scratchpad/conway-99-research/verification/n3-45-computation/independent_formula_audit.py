#!/usr/bin/env python3
"""Independent CNF reconstruction for the Wave 13 active-local SAT scout.

The discovery module is never imported.  The clause families are rebuilt
from their stated meanings, using the same deterministic PySAT sequential
counter format only so that exact DIMACS-stream hashes can be compared.
Solver UNSAT returns are not consumed as certificates.  A solver is used
only to complete the archived positive assignment, after which every clause
of that positive formula is checked directly.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Sequence

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver


ORDER = 15
K_DEGREE = 8
ROOT = frozenset((0, 1, 2))
MODES = ("111", "122", "222", "223")
BRANCHES = (
    (1, "111"),
    (3, "111"),
    (3, "122"),
    (5, "111"),
    (5, "122"),
    (5, "222"),
    (5, "223"),
    (7, "111"),
    (7, "122"),
    (7, "222"),
    (7, "223"),
    (9, "111"),
    (9, "122"),
    (9, "222"),
    (9, "223"),
    (11, "222"),
    (11, "223"),
)


def edge(left: int, right: int) -> tuple[int, int]:
    if left == right:
        raise ValueError("loops are not graph edges")
    return (left, right) if left < right else (right, left)


def candidate_points() -> tuple[frozenset[int], ...]:
    return tuple(
        frozenset(item)
        for size in (2, 3)
        for item in itertools.combinations(range(ORDER), size)
    )


def candidate_edges() -> tuple[tuple[int, int], ...]:
    return tuple(itertools.combinations(range(ORDER), 2))


def dimacs_stream_sha256(cnf: CNF, variable_count: int) -> str:
    digest = hashlib.sha256()
    digest.update(
        f"p cnf {variable_count} {len(cnf.clauses)}\n".encode("ascii")
    )
    for clause in cnf.clauses:
        digest.update(" ".join(map(str, clause)).encode("ascii"))
        digest.update(b" 0\n")
    return digest.hexdigest()


@dataclass
class Formula:
    cnf: CNF
    pool: IDPool
    points: tuple[frozenset[int], ...]
    selected: dict[frozenset[int], int]
    k_edge: dict[tuple[int, int], int]
    f_edge: dict[tuple[int, int], int]
    overlap: dict[tuple[frozenset[int], frozenset[int]], int]
    family_clause_counts: Counter[str] = field(default_factory=Counter)


class IndependentBuilder:
    def __init__(self) -> None:
        self.cnf = CNF()
        self.pool = IDPool()
        self.family_clause_counts: Counter[str] = Counter()

    def clause(self, family: str, values: Iterable[int]) -> None:
        self.cnf.append(list(values))
        self.family_clause_counts[family] += 1

    def clauses(self, family: str, values: Iterable[Iterable[int]]) -> None:
        materialized = [list(clause) for clause in values]
        self.cnf.extend(materialized)
        self.family_clause_counts[family] += len(materialized)

    def equals(
        self,
        family: str,
        literals: Iterable[int],
        bound: int,
    ) -> None:
        encoded = CardEnc.equals(
            lits=list(literals),
            bound=bound,
            vpool=self.pool,
            encoding=EncType.seqcounter,
        )
        self.clauses(family, encoded.clauses)

    def at_most(
        self,
        family: str,
        literals: Iterable[int],
        bound: int,
    ) -> None:
        materialized = list(literals)
        if len(materialized) <= bound:
            return
        encoded = CardEnc.atmost(
            lits=materialized,
            bound=bound,
            vpool=self.pool,
            encoding=EncType.seqcounter,
        )
        self.clauses(family, encoded.clauses)


def build_formula(
    m: int,
    root_mode: str,
    variant: str = "full",
) -> Formula:
    if m not in range(1, 12, 2):
        raise ValueError("m must be one of 1,3,5,7,9,11")
    if root_mode not in MODES:
        raise ValueError("invalid root mode")
    if variant not in {
        "full",
        "no_common_point",
        "no_overlap_cap",
        "k_degree_at_most",
    }:
        raise ValueError("invalid variant")
    minimum = 1 + sum(int(value) - 1 for value in root_mode)
    if m < minimum:
        raise ValueError("root mode needs more distinct co-points")

    builder = IndependentBuilder()
    points = candidate_points()
    edges = candidate_edges()
    selected = {
        point: builder.pool.id(("point", tuple(sorted(point))))
        for point in points
    }
    k_edge = {
        item: builder.pool.id(("K", item)) for item in edges
    }
    f_edge = {
        item: builder.pool.id(("F", item)) for item in edges
    }
    overlap: dict[
        tuple[frozenset[int], frozenset[int]],
        int,
    ] = {}

    # Three selected point sets through each label and exactly m triples.
    for vertex in range(ORDER):
        builder.equals(
            "incidence_equals_3",
            (
                selected[point]
                for point in points
                if vertex in point
            ),
            3,
        )
    builder.equals(
        "size3_count_equals_m",
        (
            selected[point]
            for point in points
            if len(point) == 3
        ),
        m,
    )

    # Normalize one selected size-three point.
    builder.clause("root_normalization", [selected[ROOT]])
    if m == 1:
        for point in points:
            if len(point) == 3 and point != ROOT:
                builder.clause(
                    "root_normalization",
                    [-selected[point]],
                )
        for item in (
            (0, 3),
            (0, 4),
            (1, 5),
            (1, 6),
            (2, 7),
            (2, 8),
        ):
            builder.clause(
                "root_normalization",
                [selected[frozenset(item)]],
            )

    root_templates = {
        "111": (),
        "122": (
            ((1, 3, 4), "full_L"),
            ((2, 5, 6), "full_L"),
        ),
        "222": (
            ((0, 3, 4), "full_L"),
            ((1, 5, 6), "full_L"),
            ((2, 7, 8), "full_L"),
        ),
        "223": (
            ((0, 3, 4), "empty_L"),
            ((0, 5, 6), "full_L"),
            ((1, 7, 8), "full_L"),
            ((2, 9, 10), "full_L"),
        ),
    }
    root_copoints = {
        frozenset(point): crossing
        for point, crossing in root_templates[root_mode]
    }
    for point in root_copoints:
        builder.clause("root_mode", [selected[point]])
    for point in points:
        if (
            len(point) == 3
            and point != ROOT
            and point & ROOT
            and point not in root_copoints
        ):
            builder.clause("root_mode", [-selected[point]])
    for point, crossing in root_copoints.items():
        common = next(iter(point & ROOT))
        cross_edges = (
            edge(first, second)
            for first in point - {common}
            for second in ROOT - {common}
        )
        for item in cross_edges:
            builder.clause(
                "root_mode_crossing",
                [
                    k_edge[item]
                    if crossing == "empty_L"
                    else -k_edge[item]
                ],
            )
    if root_mode == "111" and m > 1:
        builder.clause(
            "root_mode",
            [selected[frozenset((3, 4, 5))]],
        )

    # Linearity and the exact union F of selected point-clique pairs.
    for item in edges:
        owners = [
            selected[point]
            for point in points
            if set(item) <= point
        ]
        builder.at_most("linearity", owners, 1)
        for owner in owners:
            builder.clause("F_exact_union", [-owner, f_edge[item]])
        builder.clause("F_exact_union", [-f_edge[item], *owners])

    # Every selected point is a K clique.
    for point in points:
        for item in itertools.combinations(sorted(point), 2):
            builder.clause(
                "selected_point_K_clique",
                [-selected[point], k_edge[item]],
            )

    # In a linear point hypergraph, an unowned F triangle is a Berge
    # triangle.  The selected triple is its only permitted owner.
    if variant != "no_common_point":
        for triple in itertools.combinations(range(ORDER), 3):
            ab, ac, bc = itertools.combinations(triple, 2)
            builder.clause(
                "common_point_Berge_rule",
                [
                    -f_edge[ab],
                    -f_edge[ac],
                    -f_edge[bc],
                    selected[frozenset(triple)],
                ],
            )

    triples = tuple(point for point in points if len(point) == 3)
    overlap_by_point = {point: [] for point in triples}
    interacting_points = (
        tuple(
            point
            for point in points
            if len(point) == 2 or point == ROOT
        )
        if m == 1
        else points
    )

    for left_index, left in enumerate(interacting_points):
        for right in interacting_points[left_index + 1:]:
            intersection = left & right
            if len(intersection) != 1:
                continue
            common = next(iter(intersection))
            left_external = sorted(left - {common})
            right_external = sorted(right - {common})
            crossing = [
                k_edge[edge(first, second)]
                for first in left_external
                for second in right_external
            ]
            if len(left_external) == 1 or len(right_external) == 1:
                for literal in crossing:
                    builder.clause(
                        "singleton_meeting_crossing",
                        [-selected[left], -selected[right], literal],
                    )
                continue

            first = crossing[0]
            for literal in crossing[1:]:
                builder.clause(
                    "two_by_two_meeting_crossing",
                    [
                        -selected[left],
                        -selected[right],
                        -first,
                        literal,
                    ],
                )
                builder.clause(
                    "two_by_two_meeting_crossing",
                    [
                        -selected[left],
                        -selected[right],
                        first,
                        -literal,
                    ],
                )

            if m >= 5 and variant != "no_overlap_cap":
                key = (left, right)
                witness = builder.pool.id(
                    (
                        "full_L_overlap",
                        tuple(sorted(left)),
                        tuple(sorted(right)),
                    )
                )
                overlap[key] = witness
                overlap_by_point[left].append(witness)
                overlap_by_point[right].append(witness)
                builder.clause(
                    "full_L_overlap_reification",
                    [-witness, selected[left]],
                )
                builder.clause(
                    "full_L_overlap_reification",
                    [-witness, selected[right]],
                )
                builder.clause(
                    "full_L_overlap_reification",
                    [-witness, -first],
                )
                builder.clause(
                    "full_L_overlap_reification",
                    [-selected[left], -selected[right], first, witness],
                )

    if m >= 5 and variant != "no_overlap_cap":
        for point in triples:
            builder.at_most(
                "full_L_overlap_at_most_3",
                overlap_by_point[point],
                3,
            )

    for vertex in range(ORDER):
        incident_k = [
            k_edge[edge(vertex, other)]
            for other in range(ORDER)
            if other != vertex
        ]
        if variant == "k_degree_at_most":
            builder.at_most(
                "K_degree_at_most_8",
                incident_k,
                K_DEGREE,
            )
        else:
            builder.equals(
                "K_degree_equals_8",
                incident_k,
                K_DEGREE,
            )

    assert sum(builder.family_clause_counts.values()) == len(
        builder.cnf.clauses
    )
    return Formula(
        cnf=builder.cnf,
        pool=builder.pool,
        points=points,
        selected=selected,
        k_edge=k_edge,
        f_edge=f_edge,
        overlap=overlap,
        family_clause_counts=builder.family_clause_counts,
    )


def clause_is_satisfied(
    clause: Sequence[int],
    true_variables: frozenset[int],
) -> bool:
    return any(
        (literal > 0 and literal in true_variables)
        or (literal < 0 and -literal not in true_variables)
        for literal in clause
    )


def validate_positive_model(
    formula: Formula,
    model: Sequence[int],
) -> dict[str, object]:
    by_variable = {abs(literal): literal > 0 for literal in model}
    if set(by_variable) != set(range(1, formula.pool.top + 1)):
        raise AssertionError("solver did not return a total assignment")
    true_variables = frozenset(
        variable for variable, value in by_variable.items() if value
    )
    violated = [
        index
        for index, clause in enumerate(formula.cnf.clauses)
        if not clause_is_satisfied(clause, true_variables)
    ]
    if violated:
        raise AssertionError(f"positive model violates clauses {violated[:10]}")
    return {
        "variables_assigned": len(by_variable),
        "clauses_checked": len(formula.cnf.clauses),
        "violated_clause_count": len(violated),
    }


def positive_witness_formula_check(
    repository: Path,
    solver_name: str,
) -> dict[str, object]:
    candidate = json.loads(
        (
            repository
            / "attempts"
            / "wave13-computation"
            / "n3-45-no-common-point-m5-111.json"
        ).read_text(encoding="utf-8")
    )
    points = {
        frozenset(map(int, item)) for item in candidate["point_sets"]
    }
    k_edges = {
        tuple(map(int, item)) for item in candidate["K_edges"]
    }
    formula = build_formula(5, "111", "no_common_point")
    assumptions = [
        variable if point in points else -variable
        for point, variable in formula.selected.items()
    ]
    assumptions.extend(
        variable if item in k_edges else -variable
        for item, variable in formula.k_edge.items()
    )
    with Solver(
        name=solver_name,
        bootstrap_with=formula.cnf.clauses,
    ) as solver:
        satisfiable = solver.solve(assumptions=assumptions)
        if satisfiable is not True:
            raise AssertionError(
                "the archived positive core did not extend to the "
                "independent no-common-point formula"
            )
        model = solver.get_model()
    direct_check = validate_positive_model(formula, model)

    # F is definitionally the union of point-clique pairs.  Count full-model
    # common-point clauses falsified by the archived core without asking a
    # solver about the resulting negative instance.
    f_union = {
        item
        for point in points
        for item in itertools.combinations(sorted(point), 2)
    }
    falsified_common_clauses = []
    for triple in itertools.combinations(range(ORDER), 3):
        pair_items = tuple(itertools.combinations(triple, 2))
        if all(item in f_union for item in pair_items):
            if frozenset(triple) not in points:
                falsified_common_clauses.append(list(triple))
    if len(falsified_common_clauses) != 18:
        raise AssertionError("full-formula violation count changed")
    return {
        "formula_variables": formula.pool.top,
        "formula_clauses": len(formula.cnf.clauses),
        "formula_sha256": dimacs_stream_sha256(
            formula.cnf,
            formula.pool.top,
        ),
        "assumptions": len(assumptions),
        "positive_total_assignment_check": direct_check,
        "falsified_full_common_point_clauses":
            falsified_common_clauses,
    }


def rebuild_scan_formulas(
    repository: Path,
) -> dict[str, object]:
    scan = json.loads(
        (
            repository
            / "attempts"
            / "wave13-computation"
            / "n3-45-active-local-sat-scan.json"
        ).read_text(encoding="utf-8")
    )
    archived = {
        (row["size3_point_count"], row["root_mode"]): row["statistics"]
        for row in scan["branches"]
    }
    rows = []
    for branch in BRANCHES:
        formula = build_formula(*branch, variant="full")
        observed = {
            "variables": formula.pool.top,
            "clauses": len(formula.cnf.clauses),
            "cnf_sha256": dimacs_stream_sha256(
                formula.cnf,
                formula.pool.top,
            ),
        }
        expected = {
            key: archived[branch][key]
            for key in ("variables", "clauses", "cnf_sha256")
        }
        if observed != expected:
            raise AssertionError(
                f"formula rebuild mismatch at {branch}: "
                f"{observed} != {expected}"
            )
        rows.append(
            {
                "m": branch[0],
                "root_mode": branch[1],
                **observed,
                "family_clause_counts": dict(
                    sorted(formula.family_clause_counts.items())
                ),
            }
        )
    return {
        "branch_count": len(rows),
        "all_exact_hashes_match": True,
        "distinct_hash_count": len(
            {row["cnf_sha256"] for row in rows}
        ),
        "branches": rows,
    }


def audit(
    repository: Path,
    solver_name: str,
    skip_full_rebuild: bool,
) -> dict[str, object]:
    first = build_formula(1, "111", "full")
    first_summary = {
        "variables": first.pool.top,
        "clauses": len(first.cnf.clauses),
        "cnf_sha256": dimacs_stream_sha256(first.cnf, first.pool.top),
        "family_clause_counts": dict(
            sorted(first.family_clause_counts.items())
        ),
    }
    scan = json.loads(
        (
            repository
            / "attempts"
            / "wave13-computation"
            / "n3-45-active-local-sat-scan.json"
        ).read_text(encoding="utf-8")
    )
    expected_first = scan["branches"][0]["statistics"]
    assert first_summary["variables"] == expected_first["variables"]
    assert first_summary["clauses"] == expected_first["clauses"]
    assert first_summary["cnf_sha256"] == expected_first["cnf_sha256"]
    return {
        "first_formula": first_summary,
        "scan_rebuild": (
            None
            if skip_full_rebuild
            else rebuild_scan_formulas(repository)
        ),
        "positive_witness_formula_check": positive_witness_formula_check(
            repository,
            solver_name,
        ),
        "negative_solver_boundary": "UNSAT_UNVERIFIED",
        "proof_trace_checked": False,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repository",
        type=Path,
        default=Path(__file__).resolve().parents[2],
    )
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--skip-full-rebuild", action="store_true")
    parser.add_argument("--json", action="store_true")
    arguments = parser.parse_args(argv)
    result = audit(
        arguments.repository.resolve(),
        arguments.solver,
        arguments.skip_full_rebuild,
    )
    if arguments.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("PASS independent Wave 13 CNF reconstruction")
        print(
            "first_formula_sha256",
            result["first_formula"]["cnf_sha256"],
        )
        if result["scan_rebuild"] is not None:
            print(
                "exact_scan_hashes",
                result["scan_rebuild"]["branch_count"],
            )
        print(
            "positive_clauses_checked",
            result["positive_witness_formula_check"][
                "positive_total_assignment_check"
            ]["clauses_checked"],
        )
        print("negative_solver_boundary UNSAT_UNVERIFIED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
