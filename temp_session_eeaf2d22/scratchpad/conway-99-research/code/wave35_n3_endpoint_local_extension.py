#!/usr/bin/env python3
"""Exact local-extension relaxation for the endpoint ``n3 = 4158``.

This is construction-lane code.  It assumes a putative ``srg(99,14,1,2)``
and the endpoint consequence that the opposite-edge graph has no triangles.
Around one graph edge this leaves four canonical 27-vertex seeds.  For every
seed the program enumerates all possible neighborhoods that one of the other
72 vertices can have in the seed, then imposes the exact degree and
common-neighbor equations on the multiplicities of those neighborhood types.

An infeasible result counts only after the exported OPB instance has a checked
proof.  A feasible result is only a candidate for this necessary local
relaxation, not a Conway graph.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from collections import Counter
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
from typing import Iterable, Sequence

from pysat.formula import CNFPlus
from pysat.solvers import Solver


PARTITIONS: tuple[tuple[int, ...], ...] = (
    (2, 2, 2),
    (2, 4),
    (3, 3),
    (6,),
)
VERTEX_COUNT = 27
OUTSIDE_COUNT = 72


def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def partition_label(partition: Sequence[int]) -> str:
    return "+".join(str(part) for part in partition)


@dataclass(frozen=True)
class LocalSeed:
    partition: tuple[int, ...]
    names: tuple[str, ...]
    adjacency: tuple[frozenset[int], ...]

    @classmethod
    def build(cls, partition: Sequence[int]) -> "LocalSeed":
        normalized = tuple(partition)
        if normalized not in PARTITIONS:
            raise ValueError(f"unsupported endpoint partition: {normalized}")

        names = (
            "x",
            "y",
            "z",
            *(f"X{i}" for i in range(12)),
            *(f"Y{i}" for i in range(12)),
        )
        adjacency = [set() for _ in range(VERTEX_COUNT)]

        def add_edge(first: int, second: int) -> None:
            adjacency[first].add(second)
            adjacency[second].add(first)

        # xyz is the unique triangle on the rooted edge xy.
        for first, second in ((0, 1), (0, 2), (1, 2)):
            add_edge(first, second)

        # X and Y are the remaining neighbors of x and y.
        for vertex in range(3, 15):
            add_edge(0, vertex)
        for vertex in range(15, 27):
            add_edge(1, vertex)

        # The two common neighbors of X_i and y are x and Y_i.
        for index in range(12):
            add_edge(3 + index, 15 + index)

        # The neighborhood of x is 7K2, so X carries a fixed matching.
        for index in range(0, 12, 2):
            add_edge(3 + index, 3 + index + 1)

        # Pull the matching in Y back along X_i--Y_i.  At the endpoint it is
        # disjoint from the X matching, hence their union has even cycles of
        # half-lengths given by a partition of 6 with every part at least 2.
        offset = 0
        for part in normalized:
            matching_pairs = [
                (2 * (offset + index), 2 * (offset + index) + 1)
                for index in range(part)
            ]
            for index, (_, right) in enumerate(matching_pairs):
                next_left = matching_pairs[(index + 1) % part][0]
                add_edge(15 + right, 15 + next_left)
            offset += part

        seed = cls(
            partition=normalized,
            names=tuple(names),
            adjacency=tuple(frozenset(neighbors) for neighbors in adjacency),
        )
        seed.validate()
        return seed

    @property
    def edges(self) -> tuple[tuple[int, int], ...]:
        return tuple(
            (first, second)
            for first in range(VERTEX_COUNT)
            for second in sorted(self.adjacency[first])
            if first < second
        )

    def target_common_neighbors(self, first: int, second: int) -> int:
        return 1 if second in self.adjacency[first] else 2

    def local_common_neighbors(self, first: int, second: int) -> int:
        return len(self.adjacency[first].intersection(self.adjacency[second]))

    def pair_residual(self, first: int, second: int) -> int:
        return self.target_common_neighbors(
            first, second
        ) - self.local_common_neighbors(first, second)

    def degree_residual(self, vertex: int) -> int:
        return 14 - len(self.adjacency[vertex])

    def validate(self) -> None:
        if len(self.names) != VERTEX_COUNT:
            raise AssertionError("wrong seed order")
        if tuple(len(self.adjacency[index]) for index in range(3)) != (14, 14, 2):
            raise AssertionError("wrong rooted triangle degrees")
        if any(len(self.adjacency[index]) != 3 for index in range(3, 27)):
            raise AssertionError("wrong X/Y seed degree")
        if len(self.edges) != 51:
            raise AssertionError("wrong number of seed edges")
        for first, second in combinations(range(VERTEX_COUNT), 2):
            if self.pair_residual(first, second) < 0:
                raise AssertionError("seed already exceeds an SRG common-neighbor target")


def enumerate_neighborhood_types(seed: LocalSeed) -> tuple[int, ...]:
    """Enumerate every locally admissible ``N(w) intersect seed`` bit mask."""

    adjacency_masks = tuple(
        sum(1 << neighbor for neighbor in neighbors)
        for neighbors in seed.adjacency
    )
    forbidden_masks = [0] * VERTEX_COUNT
    for first, second in combinations(range(VERTEX_COUNT), 2):
        if seed.pair_residual(first, second) == 0:
            forbidden_masks[first] |= 1 << second
            forbidden_masks[second] |= 1 << first

    types: list[int] = []

    def visit(chosen: int, candidates: int) -> None:
        types.append(chosen)
        remaining = candidates
        while remaining:
            bit = remaining & -remaining
            vertex = bit.bit_length() - 1
            remaining ^= bit
            extended = chosen | bit

            # For the pair (w,u), the seed already supplies this many common
            # neighbors.  It may not exceed lambda=1 when wu is an edge or
            # mu=2 when it is a nonedge.
            if any(
                (extended & adjacency_masks[local]).bit_count()
                > (1 if extended & (1 << local) else 2)
                for local in range(VERTEX_COUNT)
            ):
                continue
            visit(extended, remaining & ~forbidden_masks[vertex])

    visit(0, (1 << VERTEX_COUNT) - 1)
    if len(types) != len(set(types)):
        raise AssertionError("neighborhood enumeration produced duplicates")
    return tuple(types)


@dataclass(frozen=True)
class ExtensionSystem:
    seed: LocalSeed
    all_types: tuple[int, ...]
    active_types: tuple[int, ...]

    @classmethod
    def build(cls, partition: Sequence[int]) -> "ExtensionSystem":
        seed = LocalSeed.build(partition)
        all_types = enumerate_neighborhood_types(seed)
        active_types = tuple(mask for mask in all_types if mask.bit_count() in (3, 4))
        system = cls(seed=seed, all_types=all_types, active_types=active_types)
        system.validate()
        return system

    @property
    def size_histogram(self) -> dict[int, int]:
        return dict(sorted(Counter(mask.bit_count() for mask in self.all_types).items()))

    @property
    def active_catalog_sha256(self) -> str:
        return sha256_text(canonical_json(list(self.active_types)))

    def validate(self) -> None:
        expected_histogram = {0: 1, 1: 27, 2: 288, 3: 1584, 4: 3600}
        if self.size_histogram != expected_histogram:
            raise AssertionError(
                f"unexpected type histogram: {self.size_histogram}"
            )
        if len(self.active_types) != 5184:
            raise AssertionError("wrong active type count")

        degree_sum = sum(
            self.seed.degree_residual(vertex) for vertex in range(VERTEX_COUNT)
        )
        pair_sum = sum(
            self.seed.pair_residual(first, second)
            for first, second in combinations(range(VERTEX_COUNT), 2)
        )
        if (degree_sum, pair_sum) != (276, 396):
            raise AssertionError("wrong first or second extension moment")

        # Each active type contains a pair whose residual capacity is one, so
        # its multiplicity is binary in every integer solution.
        for mask in self.active_types:
            vertices = tuple(
                vertex
                for vertex in range(VERTEX_COUNT)
                if mask & (1 << vertex)
            )
            if min(
                self.seed.pair_residual(first, second)
                for first, second in combinations(vertices, 2)
            ) != 1:
                raise AssertionError("an active type is not forced binary")

    def equation_rows(self) -> Iterable[tuple[str, tuple[int, ...], int, tuple[int, ...]]]:
        triples = tuple(
            index
            for index, mask in enumerate(self.active_types)
            if mask.bit_count() == 3
        )
        quadruples = tuple(
            index
            for index, mask in enumerate(self.active_types)
            if mask.bit_count() == 4
        )
        yield ("size3", (), 12, triples)
        yield ("size4", (), 60, quadruples)

        for vertex in range(VERTEX_COUNT):
            indices = tuple(
                index
                for index, mask in enumerate(self.active_types)
                if mask & (1 << vertex)
            )
            yield (
                "degree",
                (vertex,),
                self.seed.degree_residual(vertex),
                indices,
            )

        for first, second in combinations(range(VERTEX_COUNT), 2):
            indices = tuple(
                index
                for index, mask in enumerate(self.active_types)
                if mask & (1 << first) and mask & (1 << second)
            )
            yield (
                "common_neighbors",
                (first, second),
                self.seed.pair_residual(first, second),
                indices,
            )

    def validate_selection(self, selected_indices: Sequence[int]) -> None:
        selected = tuple(selected_indices)
        if len(selected) != len(set(selected)):
            raise ValueError("selection repeats a binary neighborhood type")
        if any(index < 0 or index >= len(self.active_types) for index in selected):
            raise ValueError("selection contains an out-of-range type index")
        chosen = set(selected)
        for label, scope, target, indices in self.equation_rows():
            actual = sum(index in chosen for index in indices)
            if actual != target:
                raise ValueError(
                    f"equation failure {label}{scope}: {actual} != {target}"
                )

    def opb_text(self) -> str:
        rows = tuple(self.equation_rows())
        lines = [
            f"* wave35 endpoint local extension partition={partition_label(self.seed.partition)}",
            "* CANDIDATE necessary relaxation; infeasibility requires a checked proof",
            f"* #variable= {len(self.active_types)} #constraint= {len(rows)}",
        ]
        for _, _, target, indices in rows:
            terms = " ".join(f"+1 x{index + 1}" for index in indices)
            lines.append(f"{terms} = {target} ;")
        return "\n".join(lines) + "\n"

    def native_formula(self) -> CNFPlus:
        formula = CNFPlus()
        for _, _, target, indices in self.equation_rows():
            literals = [index + 1 for index in indices]
            if target == 0:
                for literal in literals:
                    formula.append([-literal])
                continue
            if target == len(literals):
                for literal in literals:
                    formula.append([literal])
                continue
            formula.append([literals, target], is_atmost=True)
            formula.append(
                [[-literal for literal in literals], len(literals) - target],
                is_atmost=True,
            )
        return formula

    def solve_native(
        self, solver_name: str, conflict_budget: int | None
    ) -> tuple[str, tuple[int, ...] | None, dict[str, object]]:
        formula = self.native_formula()
        started = time.monotonic()
        with Solver(name=solver_name, bootstrap_with=formula, use_timer=True) as solver:
            if conflict_budget is None:
                result = solver.solve()
            else:
                solver.conf_budget(conflict_budget)
                result = solver.solve_limited()
            selected = None
            if result is True:
                positive = {literal for literal in solver.get_model() if literal > 0}
                selected = tuple(
                    index
                    for index in range(len(self.active_types))
                    if index + 1 in positive
                )
                self.validate_selection(selected)
            statistics: dict[str, object] = {
                "solver": solver_name,
                "conflict_budget": conflict_budget,
                "wall_seconds": time.monotonic() - started,
                "solver_seconds": solver.time_accum(),
                "accumulated_stats": solver.accum_stats(),
                "variables": formula.nv,
                "clauses": len(formula.clauses),
                "native_atmost_constraints": len(formula.atmosts),
            }
        status = (
            "SAT_CANDIDATE"
            if result is True
            else "UNSAT_UNVERIFIED"
            if result is False
            else "BUDGET_UNKNOWN"
        )
        return status, selected, statistics

    def public_record(
        self,
        *,
        status: str,
        selected_indices: Sequence[int] | None,
        statistics: dict[str, object] | None,
        opb_sha256: str,
    ) -> dict[str, object]:
        selected_masks = (
            [self.active_types[index] for index in selected_indices]
            if selected_indices is not None
            else None
        )
        return {
            "format": "wave35-n3-endpoint-local-extension-v1",
            "claim_label": "CANDIDATE",
            "scope": (
                "necessary one-vertex local extension of a putative "
                "srg(99,14,1,2) under n3=4158 (P=0)"
            ),
            "partition": list(self.seed.partition),
            "partition_label": partition_label(self.seed.partition),
            "status": status,
            "limitations": [
                "does not impose adjacencies among the 72 outside vertices",
                "SAT is not a graph certificate",
                "UNSAT is not evidence without a separately checked OPB proof",
            ],
            "seed": {
                "vertex_names": list(self.seed.names),
                "edges": [list(edge) for edge in self.seed.edges],
                "degree_residual_sum": 276,
                "pair_residual_sum": 396,
            },
            "types": {
                "all_count": len(self.all_types),
                "size_histogram": {
                    str(size): count for size, count in self.size_histogram.items()
                },
                "active_count": len(self.active_types),
                "active_catalog_sha256": self.active_catalog_sha256,
                "forced_selected_size3": 12,
                "forced_selected_size4": 60,
            },
            "formula": {
                "format": "OPB",
                "sha256": opb_sha256,
                "variables": len(self.active_types),
                "equations": sum(1 for _ in self.equation_rows()),
            },
            "solver": statistics,
            "selected_type_indices_zero_based": (
                list(selected_indices) if selected_indices is not None else None
            ),
            "selected_type_masks": selected_masks,
        }


def parse_partition(text: str) -> tuple[int, ...]:
    try:
        partition = tuple(int(part) for part in text.split("+"))
    except ValueError as error:
        raise argparse.ArgumentTypeError("partition must look like 2+4") from error
    if partition not in PARTITIONS:
        raise argparse.ArgumentTypeError(
            "partition must be one of 2+2+2, 2+4, 3+3, 6"
        )
    return partition


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--partition",
        type=parse_partition,
        help="one endpoint matching-union partition; default runs all four",
    )
    parser.add_argument(
        "--solver",
        default=None,
        choices=("minicard", "gluecard3", "gluecard4"),
        help="optional discovery-only native-cardinality solver",
    )
    parser.add_argument("--conflict-budget", type=int, default=250_000)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    partitions = (args.partition,) if args.partition else PARTITIONS
    records: list[dict[str, object]] = []

    if args.output_dir:
        args.output_dir.mkdir(parents=True, exist_ok=True)

    for partition in partitions:
        system = ExtensionSystem.build(partition)
        opb = system.opb_text()
        opb_sha256 = sha256_text(opb)
        status = "NOT_SOLVED"
        selected = None
        statistics = None
        if args.solver:
            status, selected, statistics = system.solve_native(
                args.solver, args.conflict_budget
            )
        record = system.public_record(
            status=status,
            selected_indices=selected,
            statistics=statistics,
            opb_sha256=opb_sha256,
        )
        records.append(record)

        if args.output_dir:
            stem = f"partition-{partition_label(partition).replace('+', '-')}"
            (args.output_dir / f"{stem}.opb").write_text(
                opb, encoding="utf-8", newline="\n"
            )
            (args.output_dir / f"{stem}.json").write_text(
                json.dumps(record, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
                newline="\n",
            )

    payload = {
        "format": "wave35-n3-endpoint-local-extension-run-v1",
        "records": records,
    }
    print(json.dumps(payload, indent=2 if args.json else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
