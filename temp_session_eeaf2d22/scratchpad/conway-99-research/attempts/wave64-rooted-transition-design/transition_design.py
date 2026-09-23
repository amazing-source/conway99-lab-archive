#!/usr/bin/env python3
"""Exact rooted transition/design enumerator and bounded MILP scout.

The finite objects are generated from definitions.  SciPy/HiGHS is used only
to find candidate witnesses.  ``check_witness.py`` checks emitted witnesses
without trusting a solver status or floating-point residual.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import time
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import coo_array

HERE = Path(__file__).resolve().parent


def support(v: int) -> int:
    return v // 2


def mate(v: int) -> int:
    return v ^ 1


BASE = tuple(range(14))
LABELS = tuple(
    (a, b)
    for a in BASE
    for b in range(a + 1, 14)
    if support(a) != support(b)
)
LABEL_INDEX = {e: i for i, e in enumerate(LABELS)}


def label(a: int, b: int) -> tuple[int, int]:
    return (a, b) if a < b else (b, a)


def other(edge: tuple[int, int], vertex: int) -> int:
    a, b = edge
    if a == vertex:
        return b
    if b == vertex:
        return a
    raise ValueError("vertex is not in edge")


def label_relation(p: int, q: int) -> str:
    """Classify two distinct H-edges by base/support intersection."""
    ep, eq = LABELS[p], LABELS[q]
    common_vertices = len(set(ep) & set(eq))
    common_supports = len({support(x) for x in ep} & {support(x) for x in eq})
    if common_vertices:
        common = next(iter(set(ep) & set(eq)))
        a, b = other(ep, common), other(eq, common)
        return "intersect_forbidden" if mate(a) == b else "intersect_allowed"
    if common_supports == 2:
        return "disjoint_full_opposite"
    if common_supports == 1:
        return "disjoint_one_opposite"
    return "disjoint_supports"


def enumerate_blocks() -> tuple[tuple[int, int, int], ...]:
    """All 3-edge matchings of H."""
    blocks: list[tuple[int, int, int]] = []
    for triple in itertools.combinations(range(len(LABELS)), 3):
        endpoints = LABELS[triple[0]] + LABELS[triple[1]] + LABELS[triple[2]]
        if len(set(endpoints)) == 6:
            blocks.append(triple)
    return tuple(blocks)


BLOCKS = enumerate_blocks()
BLOCK_INDEX = {b: i for i, b in enumerate(BLOCKS)}


def block_type(block: tuple[int, int, int]) -> tuple[int, int, int]:
    counts = Counter(
        label_relation(p, q)
        for p, q in itertools.combinations(block, 2)
    )
    return (
        counts["disjoint_full_opposite"],
        counts["disjoint_one_opposite"],
        counts["disjoint_supports"],
    )


def doubled_supports(block: tuple[int, int, int]) -> tuple[int, ...]:
    vertices = set(sum((LABELS[p] for p in block), ()))
    return tuple(g for g in range(7) if 2 * g in vertices and 2 * g + 1 in vertices)


def transition_pairs() -> tuple[tuple[int, int, int], ...]:
    """Allowed (base vertex, H-edge, H-edge) transition variables."""
    answer: list[tuple[int, int, int]] = []
    for s in BASE:
        incident = [p for p, e in enumerate(LABELS) if s in e]
        for p, q in itertools.combinations(incident, 2):
            if label_relation(p, q) == "intersect_allowed":
                answer.append((s, p, q))
    return tuple(answer)


TRANSITIONS = transition_pairs()
TRANSITION_INDEX = {(s, p, q): i for i, (s, p, q) in enumerate(TRANSITIONS)}


def count_perfect_matchings(items: tuple[int, ...], forbidden: set[tuple[int, int]]) -> int:
    if not items:
        return 1
    a = items[0]
    total = 0
    for pos in range(1, len(items)):
        b = items[pos]
        if tuple(sorted((a, b))) in forbidden:
            continue
        total += count_perfect_matchings(items[1:pos] + items[pos + 1 :], forbidden)
    return total


def transition_matching_count_at(s: int) -> int:
    incident = tuple(p for p, e in enumerate(LABELS) if s in e)
    forbidden = {
        tuple(sorted((p, q)))
        for p, q in itertools.combinations(incident, 2)
        if label_relation(p, q) == "intersect_forbidden"
    }
    return count_perfect_matchings(incident, forbidden)


def pair_to_blocks() -> dict[tuple[int, int], list[int]]:
    result: dict[tuple[int, int], list[int]] = defaultdict(list)
    for z, block in enumerate(BLOCKS):
        for p, q in itertools.combinations(block, 2):
            result[(p, q)].append(z)
    return result


PAIR_TO_BLOCKS = pair_to_blocks()


class RowBuilder:
    def __init__(self, nvars: int) -> None:
        self.nvars = nvars
        self.i: list[int] = []
        self.j: list[int] = []
        self.v: list[float] = []
        self.lo: list[float] = []
        self.hi: list[float] = []

    def add(self, terms: dict[int, int | float], lo: float, hi: float) -> None:
        row = len(self.lo)
        for col, value in terms.items():
            if value:
                self.i.append(row)
                self.j.append(col)
                self.v.append(float(value))
        self.lo.append(float(lo))
        self.hi.append(float(hi))

    def constraint(self) -> LinearConstraint:
        matrix = coo_array(
            (
                np.asarray(self.v, dtype=float),
                (np.asarray(self.i, dtype=np.int32), np.asarray(self.j, dtype=np.int32)),
            ),
            shape=(len(self.lo), self.nvars),
        ).tocsr()
        return LinearConstraint(matrix, np.asarray(self.lo), np.asarray(self.hi))

    @property
    def nnz(self) -> int:
        return len(self.v)

    @property
    def nrows(self) -> int:
        return len(self.lo)


def block_terms_containing_label(p: int) -> dict[int, int]:
    return {z: 1 for z, block in enumerate(BLOCKS) if p in block}


def block_neighbor_terms(p: int, base_vertex: int) -> dict[int, int]:
    """Count selected block-neighbors q of p whose label contains base_vertex."""
    terms: dict[int, int] = {}
    for z, block in enumerate(BLOCKS):
        if p not in block:
            continue
        coefficient = sum(
            1 for q in block if q != p and base_vertex in LABELS[q]
        )
        if coefficient:
            terms[z] = coefficient
    return terms


def add_block_master(
    rows: RowBuilder,
    offset: int = 0,
    profile_bounds: bool = False,
    full_opposite_count: int | None = None,
) -> dict[str, int]:
    # Each residual label lies in five D-triangles.
    for p in range(84):
        rows.add({offset + z: c for z, c in block_terms_containing_label(p).items()}, 5, 5)

    # Each disjoint residual pair is used in at most one D-triangle.
    for pair, zs in PAIR_TO_BLOCKS.items():
        rows.add({offset + z: 1 for z in zs}, 0, 1)

    # Exactly twelve blocks use both signs from each root mate pair.
    for g in range(7):
        rows.add(
            {
                offset + z: 1
                for z, block in enumerate(BLOCKS)
                if g in doubled_supports(block)
            },
            12,
            12,
        )

    # Wave-3 local dichotomy, stated label by label.
    for p in range(84):
        terms: dict[int, int] = {}
        for z, block in enumerate(BLOCKS):
            if p not in block:
                continue
            coeff = 0
            for q in block:
                if q == p:
                    continue
                relation = label_relation(p, q)
                if relation == "disjoint_full_opposite":
                    coeff += 2
                elif relation == "disjoint_one_opposite":
                    coeff += 1
            if coeff:
                terms[offset + z] = coeff
        rows.add(terms, 2, 2)

    if full_opposite_count is not None:
        rows.add(
            {
                offset + z: block_type(block)[0]
                for z, block in enumerate(BLOCKS)
                if block_type(block)[0]
            },
            full_opposite_count,
            full_opposite_count,
        )

    profile_bound_rows = 0
    if profile_bounds:
        # Necessary projection of the 1,176 transition+block equations:
        # the block contribution cannot exceed its exact right-hand side.
        for p, edge in enumerate(LABELS):
            for s in BASE:
                rhs = 2 - int(s in edge) - int(mate(s) in edge)
                terms = {
                    offset + z: c
                    for z, c in block_neighbor_terms(p, s).items()
                }
                rows.add(terms, 0, rhs)
                profile_bound_rows += 1

    return {
        "label_degree_equalities": 84,
        "disjoint_pair_inequalities": len(PAIR_TO_BLOCKS),
        "support_occupancy_equalities": 7,
        "local_dichotomy_equalities": 84,
        "full_opposite_count_equalities": int(full_opposite_count is not None),
        "profile_bound_inequalities": profile_bound_rows,
    }


def transition_neighbor_terms(p: int, s: int, offset: int = 0) -> dict[int, int]:
    terms: dict[int, int] = {}
    for tid, (_common, a, b) in enumerate(TRANSITIONS):
        if a == p and s in LABELS[b]:
            terms[offset + tid] = 1
        elif b == p and s in LABELS[a]:
            terms[offset + tid] = 1
    return terms


def add_transition_constraints(
    rows: RowBuilder,
    transition_offset: int,
    block_offset: int | None,
    selected_blocks: set[int] | None = None,
) -> dict[str, int]:
    # At every base vertex, the twelve incident H-edges are perfectly matched.
    for s in BASE:
        for p, edge in enumerate(LABELS):
            if s not in edge:
                continue
            terms = {
                transition_offset + tid: 1
                for tid, (common, a, b) in enumerate(TRANSITIONS)
                if common == s and p in (a, b)
            }
            rows.add(terms, 1, 1)

    # Exact rooted endpoint common-neighbor profile.
    for p, edge in enumerate(LABELS):
        for s in BASE:
            terms = transition_neighbor_terms(p, s, transition_offset)
            fixed = 0
            if block_offset is not None:
                for z, coefficient in block_neighbor_terms(p, s).items():
                    terms[block_offset + z] = coefficient
            elif selected_blocks is not None:
                fixed = sum(
                    coefficient
                    for z, coefficient in block_neighbor_terms(p, s).items()
                    if z in selected_blocks
                )
            rhs = 2 - int(s in edge) - int(mate(s) in edge) - fixed
            rows.add(terms, rhs, rhs)

    # A transition triangle would give each of its edges a residual common
    # neighbor in addition to the shared root-neighbor.
    triangle_cuts = 0
    for vertices in itertools.combinations(BASE, 3):
        if len({support(x) for x in vertices}) < 3:
            continue
        h_edges = tuple(
            LABEL_INDEX[label(a, b)] for a, b in itertools.combinations(vertices, 2)
        )
        tids: list[int] = []
        for p, q in itertools.combinations(h_edges, 2):
            common = next(iter(set(LABELS[p]) & set(LABELS[q])))
            key = (common, min(p, q), max(p, q))
            tids.append(TRANSITION_INDEX[key])
        rows.add({transition_offset + tid: 1 for tid in tids}, 0, 2)
        triangle_cuts += 1

    return {
        "transition_matching_equalities": 168,
        "endpoint_profile_equalities": 1176,
        "transition_triangle_cuts": triangle_cuts,
    }


def solve_problem(
    rows: RowBuilder,
    nvars: int,
    time_limit: float,
    seed: int,
) -> tuple[object, float]:
    rng = np.random.default_rng(seed)
    objective = (
        np.zeros(nvars)
        if seed == 0
        else rng.uniform(0.0, 1e-7, nvars)
    )
    started = time.time()
    result = milp(
        objective,
        integrality=np.ones(nvars, dtype=np.uint8),
        bounds=Bounds(np.zeros(nvars), np.ones(nvars)),
        constraints=rows.constraint(),
        options={
            "time_limit": time_limit,
            "mip_rel_gap": 0.0,
            "presolve": True,
        },
    )
    return result, time.time() - started


def block_record(z: int) -> dict[str, object]:
    block = BLOCKS[z]
    return {
        "index": z,
        "label_indices": list(block),
        "labels": [list(LABELS[p]) for p in block],
        "type_union_2_3_4": list(block_type(block)),
        "doubled_supports": list(doubled_supports(block)),
    }


def transition_record(tid: int) -> dict[str, object]:
    s, p, q = TRANSITIONS[tid]
    return {
        "index": tid,
        "common_base_vertex": s,
        "label_indices": [p, q],
        "labels": [list(LABELS[p]), list(LABELS[q])],
    }


def emit_block_witness(selected: set[int], path: Path, metadata: dict[str, object]) -> None:
    relation_counts = Counter()
    for z in selected:
        for p, q in itertools.combinations(BLOCKS[z], 2):
            relation_counts[label_relation(p, q)] += 1
    payload = {
        "format": "wave64-rooted-block-witness-v1",
        "claim_label": "CANDIDATE",
        "scope": "block-only integer master; not a residual graph",
        "metadata": metadata,
        "selected_block_count": len(selected),
        "relation_counts_union_2_3_4": [
            relation_counts["disjoint_full_opposite"],
            relation_counts["disjoint_one_opposite"],
            relation_counts["disjoint_supports"],
        ],
        "selected_blocks": [block_record(z) for z in sorted(selected)],
        "limitations": [
            "This omits transition choices unless a transition witness is supplied.",
            "This omits residual codegree constraints beyond pair simplicity.",
            "Solver status is not evidence; use check_witness.py.",
        ],
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def emit_strong_witness(
    selected_blocks: set[int],
    selected_transitions: set[int],
    path: Path,
    metadata: dict[str, object],
) -> None:
    payload = {
        "format": "wave64-rooted-transition-block-witness-v1",
        "claim_label": "CANDIDATE",
        "scope": "linear transition+block master; not a full residual graph",
        "metadata": metadata,
        "selected_block_count": len(selected_blocks),
        "selected_transition_count": len(selected_transitions),
        "selected_blocks": [block_record(z) for z in sorted(selected_blocks)],
        "selected_transitions": [
            transition_record(tid) for tid in sorted(selected_transitions)
        ],
        "limitations": [
            "Residual common-neighbor/codegree constraints are not complete.",
            "The witness is not a 99-vertex graph.",
            "Use check_witness.py for exact integer checking.",
        ],
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def census() -> dict[str, object]:
    types = Counter(str(block_type(block)) for block in BLOCKS)
    inclusion_exclusion = sum(
        (-1) ** k
        * math.comb(7, k)
        * math.comb(14 - 2 * k, 6 - 2 * k)
        * math.prod(range(1, 7 - 2 * k, 2))
        for k in range(4)
    )
    transition_matching_counts = [transition_matching_count_at(s) for s in BASE]
    transition_triangles = sum(
        1
        for vertices in itertools.combinations(BASE, 3)
        if len({support(x) for x in vertices}) == 3
    )
    return {
        "base_vertex_count": len(BASE),
        "mate_pair_count": 7,
        "H_edge_label_count": len(LABELS),
        "H_degree": 12,
        "candidate_block_count": len(BLOCKS),
        "candidate_block_inclusion_exclusion": inclusion_exclusion,
        "candidate_block_type_counts": dict(sorted(types.items())),
        "allowed_transition_variable_count": len(TRANSITIONS),
        "allowed_transition_variables_per_base": [
            sum(1 for common, _p, _q in TRANSITIONS if common == s) for s in BASE
        ],
        "transition_perfect_matching_count_per_base": transition_matching_counts,
        "transition_triangle_cut_count": transition_triangles,
        "expected_selected_intersecting_edges": 84,
        "expected_selected_disjoint_edges": 420,
        "expected_selected_blocks": 140,
        "expected_blocks_per_label": 5,
        "expected_support_occupancy_n0_n1_n2": [32, 96, 12],
    }


def check_fractional_control() -> dict[str, object]:
    """Check an exact rational feasible point of the full linear master."""
    block_weight = {
        (0, 0, 3): Fraction(1, 120),
        (0, 1, 2): Fraction(1, 240),
    }

    def zw(z: int) -> Fraction:
        return block_weight.get(block_type(BLOCKS[z]), Fraction(0))

    tw = Fraction(1, 10)
    label_degrees = [
        sum((zw(z) for z, block in enumerate(BLOCKS) if p in block), Fraction())
        for p in range(84)
    ]
    pair_loads = {
        pair: sum((zw(z) for z in zs), Fraction())
        for pair, zs in PAIR_TO_BLOCKS.items()
    }
    support_occupancies = [
        sum(
            (
                zw(z)
                for z, block in enumerate(BLOCKS)
                if g in doubled_supports(block)
            ),
            Fraction(),
        )
        for g in range(7)
    ]
    local_values = []
    for p in range(84):
        value = Fraction()
        for z, block in enumerate(BLOCKS):
            if p not in block:
                continue
            coeff = 0
            for q in block:
                if q == p:
                    continue
                relation = label_relation(p, q)
                if relation == "disjoint_full_opposite":
                    coeff += 2
                elif relation == "disjoint_one_opposite":
                    coeff += 1
            value += coeff * zw(z)
        local_values.append(value)

    transition_degrees = []
    for s in BASE:
        for p, edge in enumerate(LABELS):
            if s in edge:
                transition_degrees.append(
                    sum(
                        (
                            tw
                            for common, a, b in TRANSITIONS
                            if common == s and p in (a, b)
                        ),
                        Fraction(),
                    )
                )

    profile_residuals: list[Fraction] = []
    profile_value_census: Counter[str] = Counter()
    for p, edge in enumerate(LABELS):
        for s in BASE:
            block_part = sum(
                (
                    coefficient * zw(z)
                    for z, coefficient in block_neighbor_terms(p, s).items()
                ),
                Fraction(),
            )
            transition_part = len(transition_neighbor_terms(p, s)) * tw
            lhs = block_part + transition_part
            rhs = Fraction(2 - int(s in edge) - int(mate(s) in edge))
            profile_residuals.append(lhs - rhs)
            profile_value_census[f"{block_part}+{transition_part}={lhs}"] += 1

    passed = (
        set(label_degrees) == {Fraction(5)}
        and max(pair_loads.values()) <= 1
        and set(support_occupancies) == {Fraction(12)}
        and set(local_values) == {Fraction(2)}
        and set(transition_degrees) == {Fraction(1)}
        and set(profile_residuals) == {Fraction(0)}
        and 3 * tw <= 2
    )
    return {
        "format": "wave64-rooted-transition-design-fractional-control-v1",
        "claim_label": "DERIVED",
        "assignment": {
            "block_type_(0,0,3)": "1/120",
            "block_type_(0,1,2)": "1/240",
            "other_block_types": "0",
            "all_allowed_transitions": "1/10",
        },
        "passed": passed,
        "label_degree_values": sorted({str(x) for x in label_degrees}),
        "max_disjoint_pair_load": str(max(pair_loads.values())),
        "disjoint_pair_load_census": dict(
            sorted(Counter(str(x) for x in pair_loads.values()).items())
        ),
        "support_occupancy_values": sorted({str(x) for x in support_occupancies}),
        "local_dichotomy_values": sorted({str(x) for x in local_values}),
        "transition_degree_values": sorted({str(x) for x in transition_degrees}),
        "endpoint_profile_residual_values": sorted(
            {str(x) for x in profile_residuals}
        ),
        "endpoint_profile_value_census": dict(sorted(profile_value_census.items())),
        "transition_triangle_lhs": str(3 * tw),
        "limitations": [
            "This is a fractional point, not an integral transition/design.",
            "It uses a scaffold-invariant assignment only as a relaxation control.",
            "It assumes no automorphism of a target graph.",
            "It proves that this linear master cannot have a Farkas infeasibility certificate.",
        ],
    }


def command_census() -> None:
    payload = {
        "format": "wave64-rooted-transition-design-census-v1",
        "claim_label": "DERIVED",
        "census": census(),
        "limitations": [
            "Finite census and necessary-condition derivations only.",
            "No graph automorphism is assumed.",
            "Conway-99 and endpoint n3=4158 remain UNKNOWN.",
        ],
    }
    (HERE / "exact-census.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    fractional = check_fractional_control()
    (HERE / "fractional-control.json").write_text(
        json.dumps(fractional, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    print(json.dumps(fractional, indent=2, sort_keys=True))


def command_solve_block(args: argparse.Namespace) -> None:
    rows = RowBuilder(len(BLOCKS))
    inventory = add_block_master(
        rows,
        profile_bounds=args.profile_bounds,
        full_opposite_count=args.full_opposite_count,
    )
    result, elapsed = solve_problem(rows, len(BLOCKS), args.time_limit, args.seed)
    summary = {
        "status": int(result.status),
        "message": str(result.message),
        "elapsed_seconds": elapsed,
        "rows": rows.nrows,
        "nonzeros": rows.nnz,
        "variables": len(BLOCKS),
        "constraint_inventory": inventory,
        "profile_bounds": bool(args.profile_bounds),
        "full_opposite_count": args.full_opposite_count,
        "seed": args.seed,
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    if result.x is None:
        return
    selected = {i for i, value in enumerate(result.x) if value > 0.5}
    emit_block_witness(selected, HERE / args.output, summary)


def load_selected_blocks(path: Path) -> set[int]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {int(item["index"]) for item in payload["selected_blocks"]}


def command_extend(args: argparse.Namespace) -> None:
    selected_blocks = load_selected_blocks(HERE / args.block_witness)
    rows = RowBuilder(len(TRANSITIONS))
    inventory = add_transition_constraints(
        rows, transition_offset=0, block_offset=None, selected_blocks=selected_blocks
    )
    result, elapsed = solve_problem(rows, len(TRANSITIONS), args.time_limit, args.seed)
    summary = {
        "status": int(result.status),
        "message": str(result.message),
        "elapsed_seconds": elapsed,
        "rows": rows.nrows,
        "nonzeros": rows.nnz,
        "variables": len(TRANSITIONS),
        "constraint_inventory": inventory,
        "seed": args.seed,
        "fixed_block_witness": args.block_witness,
        "limitations": [
            "An infeasible solver status is not an exact infeasibility certificate.",
            "This fixes one block witness and says nothing about other block witnesses.",
            "A time limit or nonhit is UNKNOWN.",
        ],
    }
    (HERE / "fixed-extension-search-result.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    if result.x is None:
        return
    selected_transitions = {i for i, value in enumerate(result.x) if value > 0.5}
    emit_strong_witness(
        selected_blocks,
        selected_transitions,
        HERE / args.output,
        summary,
    )


def command_strong(args: argparse.Namespace) -> None:
    nt = len(TRANSITIONS)
    nb = len(BLOCKS)
    rows = RowBuilder(nt + nb)
    block_inventory = add_block_master(rows, offset=nt, profile_bounds=False)
    transition_inventory = add_transition_constraints(
        rows, transition_offset=0, block_offset=nt
    )
    result, elapsed = solve_problem(rows, nt + nb, args.time_limit, args.seed)
    summary = {
        "status": int(result.status),
        "message": str(result.message),
        "elapsed_seconds": elapsed,
        "rows": rows.nrows,
        "nonzeros": rows.nnz,
        "variables": nt + nb,
        "transition_variables": nt,
        "block_variables": nb,
        "block_constraint_inventory": block_inventory,
        "transition_constraint_inventory": transition_inventory,
        "seed": args.seed,
    }
    (HERE / "strong-search-result.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    if result.x is None:
        return
    selected_transitions = {i for i, value in enumerate(result.x[:nt]) if value > 0.5}
    selected_blocks = {
        i for i, value in enumerate(result.x[nt:]) if value > 0.5
    }
    emit_strong_witness(
        selected_blocks,
        selected_transitions,
        HERE / args.output,
        summary,
    )


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    sub = result.add_subparsers(dest="command", required=True)
    sub.add_parser("census")

    block = sub.add_parser("solve-block")
    block.add_argument("--time-limit", type=float, default=60.0)
    block.add_argument("--seed", type=int, default=6401)
    block.add_argument("--profile-bounds", action="store_true")
    block.add_argument("--full-opposite-count", type=int)
    block.add_argument("--output", default="block-witness.json")

    extend = sub.add_parser("extend")
    extend.add_argument("--block-witness", default="block-witness.json")
    extend.add_argument("--time-limit", type=float, default=30.0)
    extend.add_argument("--seed", type=int, default=6402)
    extend.add_argument("--output", default="transition-block-witness.json")

    strong = sub.add_parser("strong")
    strong.add_argument("--time-limit", type=float, default=180.0)
    strong.add_argument("--seed", type=int, default=6403)
    strong.add_argument("--output", default="transition-block-witness.json")
    return result


def main() -> None:
    args = parser().parse_args()
    if args.command == "census":
        command_census()
    elif args.command == "solve-block":
        command_solve_block(args)
    elif args.command == "extend":
        command_extend(args)
    elif args.command == "strong":
        command_strong(args)
    else:
        raise AssertionError(args.command)


if __name__ == "__main__":
    main()
