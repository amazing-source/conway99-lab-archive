#!/usr/bin/env python3
"""Direct exact SAT encoding of the rooted residual graph.

This is discovery code. A SAT model is decoded into a complete edge-list
certificate and must be checked by the independent validators. An UNSAT return
does not become evidence unless the exact CNF or OPB formula and a proof
artifact are checked.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
from typing import Any, Sequence

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, CNFPlus, IDPool
from pysat.solvers import Solver

from matching_orbits import (
    canonical_branch_decisions,
    n3_joint_branch_decisions,
    n3_joint_matching_orbits,
    n3_refined_branch_specification,
    n3_refined_orbits,
    parse_partition,
)
from root_model import RootModel


@dataclass
class EncodedRootModel:
    root: RootModel
    cnf: CNF | CNFPlus
    pool: IDPool
    edge_variables: dict[tuple[int, int], int]
    wedge_variables: dict[tuple[int, int, int], int]
    variant: str
    cardinality_backend: str
    matching_branch_added: bool = False
    n3_normalized: bool = False
    n3_joint_branch_number: int | None = None
    n3_refined_branch_number: int | None = None

    @classmethod
    def build(
        cls,
        pair_count: int,
        variant: str = "compact",
        cardinality_backend: str = "cnf",
    ) -> "EncodedRootModel":
        if variant not in ("compact", "direct"):
            raise ValueError("variant must be 'compact' or 'direct'")
        if cardinality_backend not in ("cnf", "native"):
            raise ValueError("cardinality_backend must be 'cnf' or 'native'")
        root = RootModel.build(pair_count)
        root.validate_fixed_identities()
        cnf = CNF() if cardinality_backend == "cnf" else CNFPlus()
        pool = IDPool()

        edge_variables: dict[tuple[int, int], int] = {}
        for first, second in combinations(range(root.residual_count), 2):
            edge_variables[(first, second)] = pool.id(("edge", first, second))

        wedge_variables: dict[tuple[int, int, int], int] = {}
        for first, second in combinations(range(root.residual_count), 2):
            for center in range(root.residual_count):
                if center in (first, second):
                    continue
                wedge_variables[(first, second, center)] = pool.id(
                    ("wedge", first, second, center)
                )

        encoded = cls(
            root,
            cnf,
            pool,
            edge_variables,
            wedge_variables,
            variant,
            cardinality_backend,
        )
        if variant == "compact":
            encoded._add_wedge_implications()
        else:
            encoded._add_wedge_definitions()
        encoded._add_coordinate_incidence_equalities()
        if variant == "compact":
            encoded._add_common_neighbor_upper_bounds()
        else:
            encoded._add_common_neighbor_equalities()
        return encoded

    def edge_literal(self, first: int, second: int) -> int:
        if first == second:
            raise ValueError("the residual graph has no loop variables")
        if first > second:
            first, second = second, first
        return self.edge_variables[(first, second)]

    def _add_wedge_definitions(self) -> None:
        # y_(p,q;r) <-> (x_(p,r) and x_(q,r)).
        for (first, second, center), wedge in self.wedge_variables.items():
            left = self.edge_literal(first, center)
            right = self.edge_literal(second, center)
            self.cnf.append([-wedge, left])
            self.cnf.append([-wedge, right])
            self.cnf.append([wedge, -left, -right])

    def _add_wedge_implications(self) -> None:
        # The compact encoding needs only (x_(p,r) and x_(q,r)) -> y_(p,q;r).
        # Global wedge counting proves that all upper bounds below become exact.
        for (first, second, center), wedge in self.wedge_variables.items():
            left = self.edge_literal(first, center)
            right = self.edge_literal(second, center)
            self.cnf.append([-left, -right, wedge])

    def _add_exactly(self, literals: list[int], bound: int) -> None:
        if self.cardinality_backend == "native":
            if not isinstance(self.cnf, CNFPlus):
                raise AssertionError("native cardinality requires CNFPlus")
            self.cnf.append([literals, bound], is_atmost=True)
            self.cnf.append(
                [[-literal for literal in literals], len(literals) - bound],
                is_atmost=True,
            )
            return
        encoding = CardEnc.equals(
            lits=literals,
            bound=bound,
            vpool=self.pool,
            encoding=EncType.seqcounter,
        )
        self.cnf.extend(encoding.clauses)

    def _add_at_most(self, literals: list[int], bound: int) -> None:
        if self.cardinality_backend == "native":
            if not isinstance(self.cnf, CNFPlus):
                raise AssertionError("native cardinality requires CNFPlus")
            self.cnf.append([literals, bound], is_atmost=True)
            return
        encoding = CardEnc.atmost(
            lits=literals,
            bound=bound,
            vpool=self.pool,
            encoding=EncType.seqcounter,
        )
        self.cnf.extend(encoding.clauses)

    def _add_coordinate_incidence_equalities(self) -> None:
        # This is the scalar form of M B + B X = 2J-B in CONJECTURE.md.
        for label_index in range(self.root.residual_count):
            for coordinate in range(self.root.coordinate_count):
                literals = [
                    self.edge_literal(label_index, other)
                    for other in self.root.containing(coordinate)
                    if other != label_index
                ]
                target = self.root.coordinate_neighbor_target(coordinate, label_index)
                self._add_exactly(literals, target)

    def _add_common_neighbor_equalities(self) -> None:
        # sum_r y_(p,q;r) + x_(p,q) = 2-|label(p) intersection label(q)|.
        for first, second in combinations(range(self.root.residual_count), 2):
            intersection = len(
                set(self.root.labels[first]).intersection(self.root.labels[second])
            )
            literals = [
                self.wedge_variables[(first, second, center)]
                for center in range(self.root.residual_count)
                if center not in (first, second)
            ]
            literals.append(self.edge_literal(first, second))
            self._add_exactly(literals, 2 - intersection)

    def _add_common_neighbor_upper_bounds(self) -> None:
        # Profile equalities force degree 2m-2. For m=7 the total number of
        # actual wedges equals the sum of these upper bounds, making the
        # one-way wedge encoding exact. The same identity holds for every m.
        for first, second in combinations(range(self.root.residual_count), 2):
            intersection = len(
                set(self.root.labels[first]).intersection(self.root.labels[second])
            )
            literals = [
                self.wedge_variables[(first, second, center)]
                for center in range(self.root.residual_count)
                if center not in (first, second)
            ]
            literals.append(self.edge_literal(first, second))
            self._add_at_most(literals, 2 - intersection)

    @staticmethod
    def _opb_literal(literal: int) -> str:
        if literal == 0:
            raise ValueError("OPB literals cannot be zero")
        variable = f"x{abs(literal)}"
        return variable if literal > 0 else f"~{variable}"

    @classmethod
    def _opb_lower_bound(cls, literals: Sequence[int], bound: int) -> str:
        terms = " ".join(f"+1 {cls._opb_literal(literal)}" for literal in literals)
        prefix = f"{terms} " if terms else ""
        return f"{prefix}>= {bound} ;"

    def opb_text(self) -> str:
        """Render a native-cardinality formula as unit-weight OPB inequalities.

        A clause is the lower bound that at least one of its literals is true.
        An AtMost constraint ``sum(lits) <= k`` is rendered equivalently as
        ``sum(complement(lits)) >= len(lits) - k``.  This preserves the native
        cardinalities instead of expanding them into auxiliary-variable CNF.
        """

        if not isinstance(self.cnf, CNFPlus):
            raise ValueError("OPB export requires the native-cardinality formula")

        constraints = [self._opb_lower_bound(clause, 1) for clause in self.cnf.clauses]
        for atmost in self.cnf.atmosts:
            if len(atmost) != 2:
                raise ValueError("weighted native constraints are not supported")
            raw_literals, raw_bound = atmost
            literals = list(raw_literals)
            bound = int(raw_bound)
            constraints.append(
                self._opb_lower_bound(
                    [-literal for literal in literals],
                    len(literals) - bound,
                )
            )

        header = f"* #variable= {self.cnf.nv} #constraint= {len(constraints)}"
        return "\n".join([header, *constraints, ""])

    def statistics(self) -> dict[str, Any]:
        native_atmost = (
            len(self.cnf.atmosts) if isinstance(self.cnf, CNFPlus) else 0
        )
        return {
            "variant": self.variant,
            "cardinality_backend": self.cardinality_backend,
            "pair_count": self.root.pair_count,
            "full_vertex_count": 2 * self.root.pair_count**2 + 1,
            "residual_vertex_count": self.root.residual_count,
            "named_edge_variables": len(self.edge_variables),
            "named_wedge_variables": len(self.wedge_variables),
            "total_variables": self.cnf.nv,
            "clauses": len(self.cnf.clauses),
            "native_atmost_constraints": native_atmost,
        }

    def residual_edges_from_model(self, model: Sequence[int]) -> list[tuple[int, int]]:
        positive = {literal for literal in model if literal > 0}
        return [
            edge for edge, variable in self.edge_variables.items() if variable in positive
        ]

    def add_matching_branch(self, coordinate: int, partition: Sequence[int]) -> None:
        if self.n3_normalized:
            raise ValueError(
                "the N3 normalization cannot be combined with legacy matching "
                "representatives; use the verified N3 joint cover"
            )
        decisions = canonical_branch_decisions(self.root, coordinate, partition)
        for edge, present in decisions.items():
            literal = self.edge_variables[edge]
            self.cnf.append([literal if present else -literal])
        self.matching_branch_added = True

    def add_n3_normalization(self) -> int:
        """Fix the cited-and-derived target N3 using only global relabeling.

        With root-neighbor coordinates normalized to matched pairs (0,1),
        (2,3), and (4,5), the two residual vertices are labels (0,2) and
        (2,4).  Their edge is the only N3 adjacency not already fixed by the
        rooted incidence scaffold.
        """

        if self.root.pair_count != 7:
            raise ValueError("the target N3 normalization applies only to pair_count 7")
        if self.matching_branch_added:
            raise ValueError(
                "the N3 normalization cannot be combined with legacy matching "
                "representatives; use the verified N3 joint cover"
            )
        if self.n3_normalized:
            raise ValueError("the N3 normalization has already been added")
        indices = self.root.label_index()
        first = indices[(0, 2)]
        second = indices[(2, 4)]
        literal = self.edge_literal(first, second)
        self.cnf.append([literal])
        self.n3_normalized = True
        return literal

    def add_n3_joint_branch(self, branch_number: int) -> tuple[int, ...]:
        """Fix one of the 12 complete matching orbits after N3 normalization."""

        if self.root.pair_count != 7:
            raise ValueError("the N3 joint cover applies only to pair_count 7")
        if not self.n3_normalized:
            raise ValueError("the N3 joint branch requires the N3 normalization first")
        if self.matching_branch_added:
            raise ValueError("the N3 joint cover cannot follow a legacy matching branch")
        if self.n3_joint_branch_number is not None:
            raise ValueError("an N3 joint branch has already been added")

        decisions = n3_joint_branch_decisions(self.root, branch_number)
        indices = self.root.label_index()
        fixed_edge = tuple(sorted((indices[(0, 2)], indices[(2, 4)])))
        positive_literals = tuple(
            sorted(
                self.edge_variables[edge]
                for edge, present in decisions.items()
                if present
            )
        )
        if self.edge_variables[fixed_edge] != 24 or 24 not in positive_literals:
            raise AssertionError("N3 joint branch does not contain the normalized unit")

        for edge, present in decisions.items():
            if edge == fixed_edge:
                continue
            literal = self.edge_variables[edge]
            self.cnf.append([literal if present else -literal])
        self.n3_joint_branch_number = branch_number
        return positive_literals

    def add_n3_refined_branch(self, branch_number: int) -> tuple[int, ...]:
        """Fix one of 78 oriented common-neighbor refinement orbits."""

        if self.root.pair_count != 7:
            raise ValueError("the refined N3 cover applies only to pair_count 7")
        if not self.n3_normalized:
            raise ValueError("the refined N3 branch requires N3 normalization first")
        if self.matching_branch_added:
            raise ValueError("the refined N3 cover cannot follow a legacy branch")
        if self.n3_refined_branch_number is not None:
            raise ValueError("a refined N3 branch has already been added")
        if self.n3_joint_branch_number is not None:
            raise ValueError("the refined N3 branch cannot follow an N3 joint branch")

        _, refinement_edge, first_branch = n3_refined_branch_specification(
            self.root, branch_number
        )
        matching_literals = self.add_n3_joint_branch(first_branch)
        indices = self.root.label_index()
        first_label = indices[(0, 2)]
        fixed_neighbor = indices[(2, 4)]
        fixed_edge = tuple(sorted((first_label, fixed_neighbor)))
        if self.edge_variables[fixed_edge] != 24:
            raise AssertionError("the refined N3 cover lost the normalized unit")
        if self.root.coordinate_neighbor_target(4, first_label) != 2:
            raise AssertionError("unexpected coordinate-4 neighbor target")

        refinement_literal = self.edge_variables[refinement_edge]
        if refinement_literal in matching_literals:
            raise AssertionError("refinement literal duplicates a matching literal")
        self.cnf.append([refinement_literal])
        self.n3_refined_branch_number = branch_number
        return tuple(sorted((*matching_literals, refinement_literal)))

    def full_certificate(self, model: Sequence[int]) -> dict[str, Any]:
        """Decode a SAT assignment into the complete normalized graph."""

        coordinate_offset = 1
        residual_offset = 1 + self.root.coordinate_count
        full_edges: list[tuple[int, int]] = []

        for coordinate in range(self.root.coordinate_count):
            full_edges.append((0, coordinate_offset + coordinate))

        for pair in range(self.root.pair_count):
            full_edges.append(
                (coordinate_offset + 2 * pair, coordinate_offset + 2 * pair + 1)
            )

        for label_index, label in enumerate(self.root.labels):
            residual_vertex = residual_offset + label_index
            for coordinate in label:
                full_edges.append((coordinate_offset + coordinate, residual_vertex))

        for first, second in self.residual_edges_from_model(model):
            full_edges.append((residual_offset + first, residual_offset + second))

        full_edges = [tuple(sorted(edge)) for edge in full_edges]
        full_edges.sort()
        return {
            "format": "srg-edge-list-v1",
            "vertices": 2 * self.root.pair_count**2 + 1,
            "edges": [list(edge) for edge in full_edges],
        }


def solve_model(
    encoded: EncodedRootModel,
    solver_name: str,
    conflict_budget: int | None = None,
) -> tuple[bool | None, list[int] | None, dict[str, Any]]:
    if encoded.cardinality_backend == "native" and solver_name != "minicard":
        raise ValueError("native cardinality is supported only with solver 'minicard'")
    bootstrap = (
        encoded.cnf
        if encoded.cardinality_backend == "native"
        else encoded.cnf.clauses
    )
    with Solver(
        name=solver_name,
        bootstrap_with=bootstrap,
        use_timer=True,
    ) as solver:
        if conflict_budget is None:
            satisfiable = solver.solve()
        else:
            solver.conf_budget(conflict_budget)
            satisfiable = solver.solve_limited()
        model = solver.get_model() if satisfiable is True else None
        statistics = {
            "solver": solver_name,
            "conflict_budget": conflict_budget,
            "solver_time_seconds": solver.time_accum(),
            "accumulated_stats": solver.accum_stats(),
        }
    return satisfiable, model, statistics


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pair-count", type=int, default=2)
    parser.add_argument("--variant", choices=("compact", "direct"), default="compact")
    parser.add_argument(
        "--cardinality",
        choices=("cnf", "native"),
        default="cnf",
        help="sequential-counter CNF or MiniCard native AtMost constraints",
    )
    parser.add_argument(
        "--branch",
        help="canonical fiber-matching partition, e.g. 6 or 3+2+1",
    )
    parser.add_argument("--branch-coordinate", type=int, default=0)
    parser.add_argument(
        "--n3",
        action="store_true",
        help="fix one target-specific cited-and-derived N3 by global relabeling",
    )
    parser.add_argument(
        "--n3-branch",
        type=int,
        metavar="1..12",
        help="select one branch of the verified N3-stabilized shared-fiber cover",
    )
    parser.add_argument(
        "--n3-refined-branch",
        type=int,
        metavar="1..78",
        help="select one orbit of the oriented common-neighbor refinement",
    )
    parser.add_argument("--solve", action="store_true")
    parser.add_argument(
        "--solver",
        help="defaults to cadical300 for CNF and minicard for native cardinality",
    )
    parser.add_argument(
        "--conflict-budget",
        type=int,
        help="return UNKNOWN after this many conflicts instead of running unbounded",
    )
    parser.add_argument("--cnf", type=Path, help="optional DIMACS output")
    parser.add_argument(
        "--opb",
        type=Path,
        help="optional OPB formula for a proof-logging solver (requires native cardinality)",
    )
    parser.add_argument("--candidate", type=Path, help="decoded SAT certificate output")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.candidate and not args.solve:
        raise SystemExit("--candidate requires --solve")
    if args.conflict_budget is not None and args.conflict_budget < 1:
        raise SystemExit("--conflict-budget must be positive")
    if args.cnf and args.opb:
        raise SystemExit("--cnf and --opb are mutually exclusive")
    if args.cnf and args.cardinality == "native":
        raise SystemExit(
            "--cnf requires --cardinality cnf; native AtMost constraints are not DIMACS"
        )
    if args.opb and args.cardinality != "native":
        raise SystemExit("--opb requires --cardinality native")
    if args.n3 and args.pair_count != 7:
        raise SystemExit("--n3 applies only to the target --pair-count 7")
    if args.n3 and args.branch:
        raise SystemExit(
            "--n3 cannot be combined with the legacy --branch representatives; "
            "use --n3-branch or --n3-refined-branch"
        )
    if args.n3_branch is not None and args.n3_refined_branch is not None:
        raise SystemExit("--n3-branch and --n3-refined-branch are mutually exclusive")
    if args.n3_branch is not None and not args.n3:
        raise SystemExit("--n3-branch requires --n3")
    if args.n3_refined_branch is not None and not args.n3:
        raise SystemExit("--n3-refined-branch requires --n3")
    n3_branch_count = (
        len(n3_joint_matching_orbits()) if args.n3_branch is not None else 0
    )
    if args.n3_branch is not None and not 1 <= args.n3_branch <= n3_branch_count:
        raise SystemExit(f"--n3-branch must be in 1..{n3_branch_count}")
    n3_refined_branch_count = (
        len(n3_refined_orbits()) if args.n3_refined_branch is not None else 0
    )
    if (
        args.n3_refined_branch is not None
        and not 1 <= args.n3_refined_branch <= n3_refined_branch_count
    ):
        raise SystemExit(
            f"--n3-refined-branch must be in 1..{n3_refined_branch_count}"
        )
    if args.n3_branch is not None and args.branch_coordinate != 0:
        raise SystemExit(
            "--branch-coordinate applies only to legacy --branch; the N3 joint "
            "cover uses shared coordinate 2"
        )
    if args.n3_refined_branch is not None and args.branch_coordinate != 0:
        raise SystemExit(
            "--branch-coordinate applies only to legacy --branch; the refined "
            "N3 cover uses fixed internal coordinates 0, 2, and 4"
        )

    encoded = EncodedRootModel.build(
        args.pair_count,
        args.variant,
        args.cardinality,
    )
    if args.branch:
        partition = parse_partition(args.branch, args.pair_count - 1)
        encoded.add_matching_branch(args.branch_coordinate, partition)
    n3_literal = encoded.add_n3_normalization() if args.n3 else None
    n3_positive_literals = (
        encoded.add_n3_joint_branch(args.n3_branch)
        if args.n3_branch is not None
        else None
    )
    n3_refined_positive_literals = (
        encoded.add_n3_refined_branch(args.n3_refined_branch)
        if args.n3_refined_branch is not None
        else None
    )
    report: dict[str, Any] = {"encoding": encoded.statistics()}
    if args.branch:
        report["branch"] = {
            "coordinate": args.branch_coordinate,
            "partition": list(partition),
        }
    if n3_literal is not None:
        report["n3_normalization"] = {
            "residual_labels": [[0, 2], [2, 4]],
            "edge_literal": n3_literal,
            "completed_graph_automorphism_assumed": False,
        }
    if args.n3_branch is not None:
        representative, orbit_size = n3_joint_matching_orbits()[args.n3_branch - 1]
        report["n3_joint_branch"] = {
            "branch": args.n3_branch,
            "cover_branch_count": n3_branch_count,
            "fiber_coordinate": 2,
            "representative_endpoint_matching": [
                list(edge) for edge in representative
            ],
            "orbit_size": orbit_size,
            "stabilizer_size": 768 // orbit_size,
            "positive_edge_literals": list(n3_positive_literals or ()),
            "added_unit_clauses": 65,
            "completed_graph_automorphism_assumed": False,
        }
    if args.n3_refined_branch is not None:
        representative, endpoint, orbit_size = n3_refined_orbits()[
            args.n3_refined_branch - 1
        ]
        _, refinement_edge, first_branch = n3_refined_branch_specification(
            encoded.root, args.n3_refined_branch
        )
        refinement_literal = encoded.edge_variables[refinement_edge]
        report["n3_refined_branch"] = {
            "branch": args.n3_refined_branch,
            "cover_branch_count": n3_refined_branch_count,
            "first_matching_branch": first_branch,
            "matching_coordinate": 2,
            "representative_endpoint_matching": [
                list(edge) for edge in representative
            ],
            "oriented_nonadjacent_pair": [[0, 2], 4],
            "additional_common_neighbor_label": sorted((4, endpoint)),
            "additional_common_neighbor_literal": refinement_literal,
            "orbit_size": orbit_size,
            "stabilizer_size": 384 // orbit_size,
            "positive_edge_literals": list(n3_refined_positive_literals or ()),
            "added_unit_clauses": 66,
            "completed_graph_automorphism_assumed": False,
        }

    if args.cnf:
        args.cnf.parent.mkdir(parents=True, exist_ok=True)
        encoded.cnf.to_file(str(args.cnf))
        report["cnf"] = str(args.cnf)

    if args.opb:
        args.opb.parent.mkdir(parents=True, exist_ok=True)
        args.opb.write_text(encoded.opb_text(), encoding="ascii", newline="\n")
        report["opb"] = str(args.opb)

    if args.solve:
        solver_name = args.solver or (
            "minicard" if args.cardinality == "native" else "cadical300"
        )
        satisfiable, model, solver_statistics = solve_model(
            encoded,
            solver_name,
            args.conflict_budget,
        )
        report["result"] = (
            "SAT_MODEL"
            if satisfiable is True
            else "UNSAT_UNVERIFIED"
            if satisfiable is False
            else "UNKNOWN"
        )
        report["solver"] = solver_statistics

        if satisfiable is True and model is not None and args.candidate:
            candidate = encoded.full_certificate(model)
            args.candidate.parent.mkdir(parents=True, exist_ok=True)
            args.candidate.write_text(
                json.dumps(candidate, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            report["candidate"] = str(args.candidate)

    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
