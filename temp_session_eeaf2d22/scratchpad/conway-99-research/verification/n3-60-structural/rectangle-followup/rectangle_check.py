#!/usr/bin/env python3
"""Independent checker for the m=30 rectangle identity N A_R N^T=2 A_L."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import random
from collections import Counter, deque
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT = Path(__file__).with_name("rectangle-certificate.json")

PINNED_INPUTS = {
    "verification/n3-60-structural/preinspection-freeze.md":
        "983f90c1d150c6e14e5e2bc7a010e1a3809848ddb1e4b825e5fdfac70398d6af",
    "verification/2026-07-23-wave15-global-lift-audit.md":
        "edda3785d080db464028f10c22bcae5c0bf17f1e61432a8641bfa6ffdccab036",
    "verification/2026-07-23-wave16-n3-51-structural-audit.md":
        "99203a15db2646a759edbb2241eb4bd5e6001733ac862952c9db57446c58ead6",
    "agents/2026-07-23-wave19-n3-60-structural.md":
        "b2f90af07f34a6525ea35cdf4d392d95aea10fc319633cd17037d00145690744",
}

SCOUT_F_EDGES = (
    (18, 19), (4, 12), (5, 19), (2, 15), (10, 16), (10, 18),
    (2, 17), (3, 8), (0, 1), (11, 16), (0, 13), (8, 13),
    (0, 14), (10, 17), (1, 9), (9, 19), (15, 18), (7, 11),
    (7, 13), (8, 14), (7, 12), (6, 15), (3, 17), (3, 4),
    (1, 16), (6, 9), (5, 12), (2, 14), (5, 11), (4, 6),
)


class CheckError(ValueError):
    pass


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def authenticate_inputs() -> dict[str, Any]:
    rows = []
    for relative, expected in PINNED_INPUTS.items():
        path = ROOT / relative
        actual = sha256_file(path)
        rows.append(
            {
                "path": relative,
                "bytes": path.stat().st_size,
                "sha256": actual,
                "match": actual == expected,
            }
        )
    if not all(row["match"] for row in rows):
        raise CheckError("pinned input mismatch")
    return {"all_match": True, "files": rows}


def gf2_rank_dense(rows: Sequence[Sequence[int]], columns: int | None = None) -> int:
    matrix = [[value & 1 for value in row] for row in rows]
    if columns is None:
        columns = len(matrix[0]) if matrix else 0
    rank = 0
    for column in range(columns):
        pivot = next(
            (index for index in range(rank, len(matrix)) if matrix[index][column]),
            None,
        )
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        for index in range(len(matrix)):
            if index != rank and matrix[index][column]:
                matrix[index] = [
                    first ^ second
                    for first, second in zip(matrix[index], matrix[rank])
                ]
        rank += 1
    return rank


def gf2_rank_bitsets(rows: Sequence[Sequence[int]], columns: int | None = None) -> int:
    if columns is None:
        columns = len(rows[0]) if rows else 0
    values = [
        sum((entry & 1) << column for column, entry in enumerate(row))
        for row in rows
    ]
    rank = 0
    for column in range(columns - 1, -1, -1):
        pivot = next(
            (index for index in range(rank, len(values)) if values[index] >> column & 1),
            None,
        )
        if pivot is None:
            continue
        values[rank], values[pivot] = values[pivot], values[rank]
        for index in range(len(values)):
            if index != rank and values[index] >> column & 1:
                values[index] ^= values[rank]
        rank += 1
    return rank


def checked_rank(rows: Sequence[Sequence[int]], columns: int | None = None) -> int:
    first = gf2_rank_dense(rows, columns)
    second = gf2_rank_bitsets(rows, columns)
    if first != second:
        raise CheckError("independent GF(2) rank implementations disagree")
    return first


def graph_audit(
    vertex_count: int,
    edges: Sequence[Sequence[int]],
    degree: int | None = None,
    triangle_free: bool = False,
) -> dict[str, Any]:
    canonical = []
    for edge in edges:
        if len(edge) != 2:
            raise CheckError("edge does not have two endpoints")
        first, second = edge
        if not (0 <= first < vertex_count and 0 <= second < vertex_count):
            raise CheckError("edge endpoint outside graph")
        if first == second:
            raise CheckError("loop rejected")
        canonical.append(tuple(sorted((first, second))))
    if len(canonical) != len(set(canonical)):
        raise CheckError("parallel edge rejected")
    adjacency = [set() for _ in range(vertex_count)]
    for first, second in canonical:
        adjacency[first].add(second)
        adjacency[second].add(first)
    degrees = [len(row) for row in adjacency]
    if degree is not None and any(value != degree for value in degrees):
        raise CheckError("degree condition rejected")
    triangles = [
        triple
        for triple in itertools.combinations(range(vertex_count), 3)
        if all(
            second in adjacency[first]
            for first, second in itertools.combinations(triple, 2)
        )
    ]
    if triangle_free and triangles:
        raise CheckError("triangle-free condition rejected")
    unseen = set(range(vertex_count))
    components = []
    while unseen:
        start = next(iter(unseen))
        component = {start}
        queue = deque([start])
        while queue:
            vertex = queue.popleft()
            for neighbor in adjacency[vertex]:
                if neighbor not in component:
                    component.add(neighbor)
                    queue.append(neighbor)
        unseen -= component
        components.append(component)
    colors: dict[int, int] = {}
    bipartite = True
    for start in range(vertex_count):
        if start in colors:
            continue
        colors[start] = 0
        queue = deque([start])
        while queue:
            vertex = queue.popleft()
            for neighbor in adjacency[vertex]:
                if neighbor not in colors:
                    colors[neighbor] = 1 - colors[vertex]
                    queue.append(neighbor)
                elif colors[neighbor] == colors[vertex]:
                    bipartite = False
    return {
        "vertex_count": vertex_count,
        "edge_count": len(canonical),
        "component_count": len(components),
        "component_orders": sorted(map(len, components)),
        "degree_multiset": sorted(degrees),
        "triangle_count": len(triangles),
        "bipartite": bipartite,
    }


def incidence_matrix(vertex_count: int, edges: Sequence[Sequence[int]]) -> list[list[int]]:
    matrix = [[0] * len(edges) for _ in range(vertex_count)]
    for column, edge in enumerate(edges):
        first, second = edge
        matrix[first][column] = 1
        matrix[second][column] = 1
    return matrix


def cycle_partitions(total: int, minimum: int = 3) -> Iterator[tuple[int, ...]]:
    if total == 0:
        yield ()
        return
    for first in range(minimum, total + 1):
        for tail in cycle_partitions(total - first, first):
            yield (first,) + tail


def cycle_edges_from_order(
    order: Sequence[int], lengths: Sequence[int]
) -> list[tuple[int, int]]:
    if sum(lengths) != len(order) or sorted(order) != list(range(len(order))):
        raise CheckError("cycle encoding does not partition the R vertices")
    edges = []
    offset = 0
    for length in lengths:
        if length < 3:
            raise CheckError("simple 2-factor cycle shorter than three")
        cycle = order[offset : offset + length]
        offset += length
        edges.extend(
            (cycle[index], cycle[(index + 1) % length])
            for index in range(length)
        )
    return edges


def adjacency_matrix(order: int, edges: Sequence[Sequence[int]]) -> list[list[int]]:
    audit = graph_audit(order, edges)
    matrix = [[0] * order for _ in range(order)]
    for first, second in edges:
        matrix[first][second] = matrix[second][first] = 1
    return matrix


def cycle_nullity_formula(lengths: Sequence[int]) -> int:
    return sum(1 if length % 2 else 2 for length in lengths)


def radical_basis_for_cycles(
    order: Sequence[int], lengths: Sequence[int]
) -> list[list[int]]:
    basis = []
    offset = 0
    for length in lengths:
        cycle = order[offset : offset + length]
        offset += length
        if length % 2:
            basis.append([int(index in cycle) for index in range(len(order))])
        else:
            even_positions = set(cycle[::2])
            odd_positions = set(cycle[1::2])
            basis.append(
                [int(index in even_positions) for index in range(len(order))]
            )
            basis.append(
                [int(index in odd_positions) for index in range(len(order))]
            )
    return basis


def matrix_vector_mod2(
    matrix: Sequence[Sequence[int]], vector: Sequence[int]
) -> list[int]:
    return [
        sum(value * vector[column] for column, value in enumerate(row)) & 1
        for row in matrix
    ]


def intersection_dimension(
    first_basis: Sequence[Sequence[int]],
    second_basis: Sequence[Sequence[int]],
) -> int:
    columns = (
        len(first_basis[0])
        if first_basis
        else len(second_basis[0]) if second_basis else 0
    )
    first_rank = checked_rank(first_basis, columns)
    second_rank = checked_rank(second_basis, columns)
    joined_rank = checked_rank(list(first_basis) + list(second_basis), columns)
    return first_rank + second_rank - joined_rank


def rectangle_matrix(
    f_edges: Sequence[Sequence[int]], r_edges: Sequence[Sequence[int]]
) -> list[list[int]]:
    n_matrix = incidence_matrix(20, f_edges)
    a_r = adjacency_matrix(30, r_edges)
    result = [[0] * 20 for _ in range(20)]
    for first_label in range(20):
        for second_label in range(20):
            result[first_label][second_label] = sum(
                n_matrix[first_label][left]
                * a_r[left][right]
                * n_matrix[second_label][right]
                for left in range(30)
                for right in range(30)
            )
    return result


def rectangle_audit(
    f_edges: Sequence[Sequence[int]],
    order: Sequence[int],
    lengths: Sequence[int],
) -> dict[str, Any]:
    f_audit = graph_audit(20, f_edges, degree=3, triangle_free=True)
    r_edges = cycle_edges_from_order(order, lengths)
    r_audit = graph_audit(30, r_edges, degree=2)
    n_matrix = incidence_matrix(20, f_edges)
    a_r = adjacency_matrix(30, r_edges)
    m_matrix = rectangle_matrix(f_edges, r_edges)
    if any(sum(row) != 12 for row in m_matrix):
        raise CheckError("rectangle matrix row sum is not twelve")
    diagonal_sum = sum(m_matrix[index][index] for index in range(20))
    odd_pairs = [
        [first, second, m_matrix[first][second]]
        for first in range(20)
        for second in range(first + 1, 20)
        if m_matrix[first][second] % 2
    ]
    over_two = [
        [first, second, m_matrix[first][second]]
        for first in range(20)
        for second in range(first + 1, 20)
        if m_matrix[first][second] > 2
    ]
    frobenius = sum(value * value for row in m_matrix for value in row)
    mod2_product_rank = checked_rank(
        [[value & 1 for value in row] for row in m_matrix], 20
    )
    incidence_rank = checked_rank(n_matrix, 30)
    if incidence_rank != 20 - f_audit["component_count"]:
        raise CheckError("incidence rank/component identity failed")
    radical = radical_basis_for_cycles(order, lengths)
    z_formula = cycle_nullity_formula(lengths)
    z_matrix = 30 - checked_rank(a_r, 30)
    if z_formula != z_matrix or checked_rank(radical, 30) != z_formula:
        raise CheckError("cycle radical formula failed")
    if any(any(matrix_vector_mod2(a_r, vector)) for vector in radical):
        raise CheckError("declared radical basis has a nonzero image")
    t_value = intersection_dimension(n_matrix, radical)
    c_value = f_audit["component_count"]
    isotropic_threshold = 5 - c_value + z_formula // 2
    exact = (
        diagonal_sum == 0
        and mod2_product_rank == 0
        and not over_two
        and frobenius == 480
    )
    return {
        "F": f_audit,
        "R": {
            **r_audit,
            "cycle_lengths": list(lengths),
            "nullity_formula": z_formula,
            "nullity_matrix": z_matrix,
        },
        "cut_space_dimension": incidence_rank,
        "cut_radical_intersection_dimension": t_value,
        "isotropic_intersection_threshold": isotropic_threshold,
        "diagonal_sum": diagonal_sum,
        "odd_offdiagonal_pair_count": len(odd_pairs),
        "odd_offdiagonal_pairs": odd_pairs,
        "over_two_pair_count": len(over_two),
        "over_two_pairs": over_two,
        "maximum_entry": max(map(max, m_matrix)),
        "frobenius_square": frobenius,
        "mod2_product_rank": mod2_product_rank,
        "exact_rectangle_identity": exact,
    }


def cycle_type_census() -> dict[str, Any]:
    partitions = list(cycle_partitions(30))
    if len(partitions) != 331:
        raise CheckError("cycle partition count mismatch")
    rows = []
    for lengths in partitions:
        matrix = adjacency_matrix(
            30, cycle_edges_from_order(list(range(30)), lengths)
        )
        formula = cycle_nullity_formula(lengths)
        actual = 30 - checked_rank(matrix, 30)
        if formula != actual:
            raise CheckError(f"cycle nullity mismatch: {lengths}")
        rows.append(
            {
                "cycle_lengths": list(lengths),
                "odd_cycle_count": sum(length % 2 for length in lengths),
                "even_cycle_count": sum(length % 2 == 0 for length in lengths),
                "nullity": formula,
            }
        )
    counts = {}
    nonbipartite_counts = {}
    survivors = {}
    for components in (1, 2, 3):
        threshold = 10 - 2 * components
        stronger = 12 - 2 * components
        selected = [row for row in rows if row["nullity"] >= threshold]
        selected_nonbip = [row for row in rows if row["nullity"] >= stronger]
        counts[str(components)] = len(selected)
        nonbipartite_counts[str(components)] = len(selected_nonbip)
        survivors[str(components)] = [
            row["cycle_lengths"] for row in selected
        ]
    if counts != {"1": 147, "2": 263, "3": 323}:
        raise CheckError(f"unexpected cycle census {counts}")
    if nonbipartite_counts != {"1": 55, "2": 147, "3": 263}:
        raise CheckError("unexpected nonbipartite cycle census")
    return {
        "all_cycle_length_multisets": 331,
        "necessary_nullity_threshold": {
            "formula": "z>=10-2c(F)",
            "counts_by_component_count": counts,
            "surviving_cycle_lengths": survivors,
        },
        "if_some_F_component_is_nonbipartite": {
            "formula": "z>=12-2c(F)",
            "counts_by_component_count": nonbipartite_counts,
        },
        "all_rows": rows,
    }


def component_bound() -> dict[str, Any]:
    possibilities = {
        1: [(20,)],
        2: [(6, 14), (8, 12), (10, 10)],
        3: [(6, 6, 8)],
    }
    generated = {}
    for components in range(1, 5):
        values = [
            parts
            for parts in itertools.combinations_with_replacement(
                range(6, 21, 2), components
            )
            if sum(parts) == 20
        ]
        generated[components] = values
    if any(generated[key] != possibilities[key] for key in possibilities):
        raise CheckError("component-order enumeration mismatch")
    if generated[4]:
        raise CheckError("four triangle-free cubic components fit in order 20")
    return {
        "derivation": (
            "Every simple cubic component has even order. Orders 2 and 4 "
            "are impossible under simplicity and triangle-freeness (the only "
            "cubic graph on four vertices is K4), so every component has order at least 6."
        ),
        "possible_component_orders": {
            str(key): [list(row) for row in value]
            for key, value in possibilities.items()
        },
        "maximum_component_count": 3,
    }


def exact_invariant_derivation() -> dict[str, Any]:
    return {
        "mod2": [
            "Let W=im(N^T), the binary cut space of F. Its dimension is 20-c(F).",
            "Reducing N A_R N^T=2A_L modulo two makes W totally isotropic for the alternating form A_R.",
            "Let z=nullity(A_R) and t=dim(W intersect ker A_R). Projection to the nondegenerate quotient gives 20-c-t <= (30-z)/2.",
            "Thus t>=5-c+z/2. Since t<=z, necessarily z>=10-2c.",
            "The all-one edge vector is always in ker A_R. It lies in W exactly when every F component is bipartite. If some component is nonbipartite, t<=z-1 and z>=12-2c.",
        ],
        "cycle_nullity": (
            "On a cycle, A_R x=0 gives x_(i+2)=x_i. An odd cycle has "
            "one constant null vector; an even cycle has two parity-class "
            "null vectors. Therefore z=#odd cycles+2#even cycles."
        ),
        "integer_rectangle": [
            "M=N A_R N^T has every row sum 12 because N^T1=2, A_R1=2, and N1=3.",
            "M has zero diagonal exactly when every R edge joins disjoint F edges.",
            "If M is zero modulo two, each row is a partition of 12 into nonnegative even entries, so its square sum is at least 24.",
            "Hence ||M||_F^2>=480; equality holds exactly when every entry is 0 or 2.",
            "Consequently the exact identity with a simple 6-regular A_L is equivalent to zero diagonal, M=0 mod 2, and Frobenius square 480; then A_L=M/2.",
        ],
    }


def scout_score(audit: dict[str, Any]) -> int:
    return (
        1000 * audit["diagonal_sum"]
        + 10 * audit["odd_offdiagonal_pair_count"]
        + sum(value - 2 for _, _, value in audit["over_two_pairs"])
    )


def bounded_scout(iterations: int = 3000, restarts: int = 2) -> dict[str, Any]:
    f_audit = graph_audit(20, SCOUT_F_EDGES, degree=3, triangle_free=True)
    if f_audit["component_count"] != 1 or f_audit["bipartite"]:
        raise CheckError("fixed scout graph lost its connected nonbipartite property")
    cycle_types = (
        (3,) * 10,
        (3,) * 8 + (6,),
        (4,) * 6 + (6,),
        (3,) * 6 + (4,) * 3,
    )
    rng = random.Random(19030)
    results = []
    for lengths in cycle_types:
        best_audit = None
        best_order = None
        best_score = 10**18
        evaluations = 0
        for _ in range(restarts):
            order = list(range(30))
            rng.shuffle(order)
            current = rectangle_audit(SCOUT_F_EDGES, order, lengths)
            current_score = scout_score(current)
            temperature = 8.0
            for _ in range(iterations):
                first, second = rng.sample(range(30), 2)
                order[first], order[second] = order[second], order[first]
                candidate = rectangle_audit(SCOUT_F_EDGES, order, lengths)
                candidate_score = scout_score(candidate)
                evaluations += 1
                if candidate_score < best_score:
                    best_score = candidate_score
                    best_audit = candidate
                    best_order = list(order)
                if (
                    candidate_score <= current_score
                    or rng.random()
                    < math.exp(
                        (current_score - candidate_score) / max(temperature, 0.1)
                    )
                ):
                    current = candidate
                    current_score = candidate_score
                else:
                    order[first], order[second] = order[second], order[first]
                temperature *= 0.999
        if best_audit is None or best_order is None:
            raise CheckError("scout evaluated no R encodings")
        results.append(
            {
                "cycle_lengths": list(lengths),
                "evaluations": evaluations,
                "best_order": best_order,
                "best_score": best_score,
                "best_summary": {
                    key: best_audit[key]
                    for key in (
                        "diagonal_sum",
                        "odd_offdiagonal_pair_count",
                        "over_two_pair_count",
                        "maximum_entry",
                        "frobenius_square",
                        "mod2_product_rank",
                        "cut_radical_intersection_dimension",
                        "isotropic_intersection_threshold",
                        "exact_rectangle_identity",
                    )
                },
            }
        )
    return {
        "method": (
            "Deterministic swap-based simulated annealing on one fixed "
            "connected, nonbipartite, triangle-free cubic F; four cycle "
            "types, two restarts, 3000 proposed swaps per restart."
        ),
        "F_edges": [list(edge) for edge in SCOUT_F_EDGES],
        "F_audit": f_audit,
        "results": results,
        "complete_search": False,
        "no_witness_found": not any(
            row["best_summary"]["exact_rectangle_identity"] for row in results
        ),
        "evidentiary_status": (
            "CANDIDATE scouting only. Failure to find a witness is not "
            "nonexistence evidence and no UNSAT claim is made."
        ),
    }


def hostile_checks() -> dict[str, Any]:
    rows = []
    for length in range(3, 13):
        matrix = adjacency_matrix(
            length,
            cycle_edges_from_order(list(range(length)), (length,)),
        )
        actual = length - checked_rank(matrix, length)
        wrong = 1 if length % 2 == 0 else 2
        if actual == wrong:
            raise CheckError("hostile cycle-nullity swap survived")
        rows.append(
            {
                "mutation": f"C{length} nullity set to {wrong}",
                "actual_nullity": actual,
                "result": "REJECTED_BY_TWO_RANK_IMPLEMENTATIONS",
            }
        )
    for name, edges in {
        "F_loop": list(SCOUT_F_EDGES) + [(0, 0)],
        "F_parallel": list(SCOUT_F_EDGES) + [SCOUT_F_EDGES[0]],
    }.items():
        try:
            graph_audit(20, edges)
        except CheckError as error:
            rows.append(
                {"mutation": name, "result": "REJECTED", "reason": str(error)}
            )
        else:
            raise CheckError(f"{name} survived")
    arbitrary = rectangle_audit(
        SCOUT_F_EDGES, list(range(30)), (3,) * 10
    )
    if arbitrary["exact_rectangle_identity"]:
        raise CheckError("arbitrary R unexpectedly satisfied exact identity")
    rows.append(
        {
            "mutation": "cycle type passes z bound but arbitrary edge assignment",
            "cycle_lengths": [3] * 10,
            "nullity": 10,
            "result": "REJECTED_BY_EXACT_RECTANGLE_CHECK",
            "diagnostics": {
                key: arbitrary[key]
                for key in (
                    "diagonal_sum",
                    "mod2_product_rank",
                    "odd_offdiagonal_pair_count",
                    "frobenius_square",
                )
            },
        }
    )
    return {"rows": rows, "all_expected_outcomes_observed": True}


def build_certificate(include_scout: bool = True) -> dict[str, Any]:
    census = cycle_type_census()
    payload = {
        "certificate_type": "m30_rectangle_identity_followup",
        "claim_label": "DERIVED",
        "scope": (
            "Exact invariants from N A_R N^T=2A_L, especially binary "
            "rank/nullity versus F components and R cycle types"
        ),
        "inputs": authenticate_inputs(),
        "derivation": exact_invariant_derivation(),
        "component_bound": component_bound(),
        "cycle_type_census": census,
        "independent_validation": {
            "rank_implementations": [
                "dense row-list Gaussian elimination over GF(2)",
                "integer-bitset Gaussian elimination over GF(2)",
            ],
            "all_331_cycle_matrices_match_formula": True,
            "incidence_rank_formula": "rank_GF2(N)=20-c(F)",
        },
        "hostile_checks": hostile_checks(),
        "restrictions": [
            "R is a simple spanning 2-factor on the 30 F-edges; every cycle has length at least three.",
            "The 147/263/323 census is only a cycle-type necessary filter; actual placement of F-edges around R cycles remains essential.",
            "No connectivity of F is assumed in the invariant. Connectedness is imposed only in the explicitly bounded scout.",
            "No automorphism restriction, graph catalog, SAT result, or ILP result is used.",
            "No prohibited later-wave file, result, or artifact was read, executed, cited, or imported.",
        ],
        "status_boundary": {
            "nullity_bound": "DERIVED",
            "cycle_type_counts": "DERIVED",
            "m30_residual": "UNKNOWN",
            "conditional_n3_60": "UNKNOWN_FINITE_RESIDUAL",
            "self_promotion_to_VERIFIED": False,
        },
    }
    if include_scout:
        payload["bounded_scout"] = bounded_scout()
    return payload


def canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    parser.add_argument("--no-scout", action="store_true")
    args = parser.parse_args()
    payload = build_certificate(include_scout=not args.no_scout)
    rendered = canonical_json(payload)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    if args.verify and args.verify.read_text(encoding="utf-8") != rendered:
        raise CheckError("certificate replay mismatch")
    if not args.output and not args.verify:
        print(
            json.dumps(
                {
                    "status": "PASS",
                    "claim_label": payload["claim_label"],
                    "cycle_counts": payload["cycle_type_census"][
                        "necessary_nullity_threshold"
                    ]["counts_by_component_count"],
                    "status_boundary": payload["status_boundary"],
                },
                indent=2,
                sort_keys=True,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
