#!/usr/bin/env python3
"""Exact Wave 60 classification and kappa=3 incidence-design search.

The component and column enumerations use only integer arithmetic.  A SAT
model is always replayed by direct multiplication.  UNSAT returned by a SAT
solver is not promoted without a separately checkable proof artifact.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import itertools
import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Sequence


MIN_FREE_PERCENT = 15.0
FIBRES = 3
M = 4
COMPONENT_SIZE = FIBRES * M
COMPONENTS = 3
X_SIZE = COMPONENT_SIZE * COMPONENTS
COLUMN_WEIGHT = 6
COLUMN_COUNT = 60
HERE = Path(__file__).resolve().parent


class MemoryStatus(ctypes.Structure):
    _fields_ = (
        ("length", ctypes.c_ulong),
        ("memory_load", ctypes.c_ulong),
        ("total_physical", ctypes.c_ulonglong),
        ("available_physical", ctypes.c_ulonglong),
        ("total_page_file", ctypes.c_ulonglong),
        ("available_page_file", ctypes.c_ulonglong),
        ("total_virtual", ctypes.c_ulonglong),
        ("available_virtual", ctypes.c_ulonglong),
        ("available_extended_virtual", ctypes.c_ulonglong),
    )


def free_memory_percent() -> float:
    if sys.platform != "win32":
        return 100.0
    status = MemoryStatus()
    status.length = ctypes.sizeof(status)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise OSError("GlobalMemoryStatusEx failed")
    return 100.0 * status.available_physical / status.total_physical


def require_memory() -> None:
    available = free_memory_percent()
    if available < MIN_FREE_PERCENT:
        raise MemoryError(
            f"{available:.2f}% free physical memory is below "
            f"{MIN_FREE_PERCENT:.2f}%"
        )


def canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def perfect_matchings(items: tuple[int, ...]) -> Iterable[tuple[tuple[int, int], ...]]:
    if not items:
        yield ()
        return
    first = items[0]
    for index in range(1, len(items)):
        second = items[index]
        rest = items[1:index] + items[index + 1 :]
        for tail in perfect_matchings(rest):
            yield tuple(sorted(((first, second), *tail)))


MATCHINGS = tuple(perfect_matchings(tuple(range(M))))
BASE_MATCHING = MATCHINGS[0]
PERMUTATIONS = tuple(itertools.permutations(range(M)))


def add_edge(adjacency: list[set[int]], left: int, right: int) -> None:
    if left == right or right in adjacency[left]:
        raise AssertionError(f"illegal edge {left},{right}")
    adjacency[left].add(right)
    adjacency[right].add(left)


def component_graph(
    matching1: Sequence[tuple[int, int]],
    matching2: Sequence[tuple[int, int]],
    cross12: Sequence[int],
) -> list[set[int]]:
    """Coordinate-normalized component.

    The fibre-0 matching and both cross matchings incident with fibre 0 are
    fixed.  This loses no fibre-labelled isomorphism type.
    """

    adjacency = [set() for _ in range(COMPONENT_SIZE)]
    for fibre, matching in enumerate((BASE_MATCHING, matching1, matching2)):
        for left, right in matching:
            add_edge(adjacency, fibre * M + left, fibre * M + right)
    for index in range(M):
        add_edge(adjacency, index, M + index)
        add_edge(adjacency, index, 2 * M + index)
        add_edge(adjacency, M + index, 2 * M + cross12[index])
    return adjacency


def connected(adjacency: Sequence[set[int]]) -> bool:
    seen = {0}
    stack = [0]
    while stack:
        vertex = stack.pop()
        for neighbor in adjacency[vertex]:
            if neighbor not in seen:
                seen.add(neighbor)
                stack.append(neighbor)
    return len(seen) == len(adjacency)


def triangle_count(adjacency: Sequence[set[int]]) -> int:
    return sum(
        1
        for left in range(len(adjacency))
        for middle in adjacency[left]
        if left < middle
        for right in adjacency[left] & adjacency[middle]
        if middle < right
    )


def four_cycle_count(adjacency: Sequence[set[int]]) -> int:
    opposite = sum(
        len(adjacency[left] & adjacency[right])
        * (len(adjacency[left] & adjacency[right]) - 1)
        // 2
        for left in range(len(adjacency))
        for right in range(left + 1, len(adjacency))
    )
    if opposite % 2:
        raise AssertionError("four-cycle opposite-pair count is odd")
    return opposite // 2


def codegree_cap_passes(adjacency: Sequence[set[int]]) -> bool:
    for left in range(COMPONENT_SIZE):
        if len(adjacency[left]) != 3:
            return False
        for right in range(left + 1, COMPONENT_SIZE):
            common = len(adjacency[left] & adjacency[right])
            if right in adjacency[left]:
                if common:
                    return False
            elif left // M == right // M:
                if common > 1:
                    return False
            elif common > 2:
                return False
    return True


PAIR_INDEX = {
    (left, right): index
    for index, (left, right) in enumerate(
        itertools.combinations(range(COMPONENT_SIZE), 2)
    )
}


def adjacency_code(
    adjacency: Sequence[set[int]],
    relabel: Sequence[int] | None = None,
) -> int:
    if relabel is None:
        relabel = tuple(range(COMPONENT_SIZE))
    code = 0
    for left in range(COMPONENT_SIZE):
        for right in adjacency[left]:
            if left < right:
                new_left, new_right = sorted((relabel[left], relabel[right]))
                code |= 1 << PAIR_INDEX[(new_left, new_right)]
    return code


def canonical_component_code(adjacency: Sequence[set[int]]) -> int:
    best: int | None = None
    for perm0 in PERMUTATIONS:
        for perm1 in PERMUTATIONS:
            for perm2 in PERMUTATIONS:
                relabel = tuple(perm0) + tuple(M + i for i in perm1) + tuple(
                    2 * M + i for i in perm2
                )
                code = adjacency_code(adjacency, relabel)
                if best is None or code < best:
                    best = code
    if best is None:
        raise AssertionError("missing canonical code")
    return best


def decode_component(code: int) -> list[set[int]]:
    adjacency = [set() for _ in range(COMPONENT_SIZE)]
    for pair, index in PAIR_INDEX.items():
        if code >> index & 1:
            left, right = pair
            adjacency[left].add(right)
            adjacency[right].add(left)
    return adjacency


def edge_list(adjacency: Sequence[set[int]]) -> list[list[int]]:
    return [
        [left, right]
        for left in range(len(adjacency))
        for right in sorted(adjacency[left])
        if left < right
    ]


def component_census() -> dict[str, object]:
    require_memory()
    raw = 0
    accepted = 0
    labelled_c4: Counter[int] = Counter()
    canonical: dict[int, list[set[int]]] = {}
    for matching1 in MATCHINGS:
        for matching2 in MATCHINGS:
            for cross12 in PERMUTATIONS:
                raw += 1
                adjacency = component_graph(matching1, matching2, cross12)
                if not connected(adjacency):
                    continue
                if triangle_count(adjacency):
                    continue
                if not codegree_cap_passes(adjacency):
                    continue
                accepted += 1
                labelled_c4[four_cycle_count(adjacency)] += 1
                code = canonical_component_code(adjacency)
                canonical.setdefault(code, decode_component(code))
    records = []
    for type_index, (code, adjacency) in enumerate(sorted(canonical.items())):
        records.append(
            {
                "type_index": type_index,
                "canonical_code_hex": f"{code:017x}",
                "edges": edge_list(adjacency),
                "C4": four_cycle_count(adjacency),
                "connected": connected(adjacency),
                "triangle_count": triangle_count(adjacency),
                "degree_set": sorted(set(map(len, adjacency))),
                "sector_codegree_cap_passes": codegree_cap_passes(adjacency),
            }
        )
    return {
        "normalization": (
            "fix fibre-0 matching and both cross matchings incident with "
            "fibre 0 by within-fibre coordinate relabeling; enumerate the "
            "two remaining within-fibre matchings and cross-12 permutation"
        ),
        "raw_coordinate_normalized_count": raw,
        "accepted_labelled_count": accepted,
        "accepted_labelled_C4_distribution": {
            str(key): labelled_c4[key] for key in sorted(labelled_c4)
        },
        "isomorphism": (
            "canonical minimum over S4 x S4 x S4 acting independently "
            "inside the three fixed fibres; fibres are not permuted"
        ),
        "fibre_preserving_type_count": len(records),
        "types": records,
    }


def global_vertex(component: int, local_vertex: int) -> int:
    fibre, local_index = divmod(local_vertex, M)
    return fibre * 12 + component * M + local_index


def union_core(type_records: Sequence[dict[str, object]]) -> list[set[int]]:
    adjacency = [set() for _ in range(X_SIZE)]
    for component, record in enumerate(type_records):
        for local_left, local_right in record["edges"]:
            left = global_vertex(component, local_left)
            right = global_vertex(component, local_right)
            adjacency[left].add(right)
            adjacency[right].add(left)
    if set(map(len, adjacency)) != {3}:
        raise AssertionError("global core is not cubic")
    return adjacency


def gram_target(adjacency: Sequence[set[int]]) -> list[list[int]]:
    gram = [[0] * X_SIZE for _ in range(X_SIZE)]
    for left in range(X_SIZE):
        for right in range(X_SIZE):
            common = len(adjacency[left] & adjacency[right])
            gram[left][right] = (
                (12 if left == right else 0)
                - (1 if right in adjacency[left] else 0)
                + 2
                - (1 if left // 12 == right // 12 else 0)
                - common
            )
            if gram[left][right] < 0:
                raise AssertionError(
                    f"negative target Gram entry {left},{right}"
                )
    return gram


def component_pairs(component: int) -> tuple[tuple[int, int], ...]:
    vertices = tuple(global_vertex(component, local) for local in range(12))
    return tuple(itertools.combinations(vertices, 2))


COMPONENT_PAIR_CHOICES = tuple(component_pairs(c) for c in range(COMPONENTS))


def pattern_matrix(mask: int) -> tuple[tuple[int, ...], ...]:
    matrix = [[0] * FIBRES for _ in range(COMPONENTS)]
    for vertex in range(X_SIZE):
        if mask >> vertex & 1:
            fibre = vertex // 12
            component = (vertex % 12) // M
            matrix[component][fibre] += 1
    return tuple(tuple(row) for row in matrix)


def candidate_columns(
    adjacency: Sequence[set[int]], gram: Sequence[Sequence[int]]
) -> tuple[list[int], dict[str, object]]:
    candidates: list[int] = []
    rejected_fibre = 0
    rejected_cut = 0
    rejected_zero_target = 0
    patterns: Counter[tuple[tuple[int, ...], ...]] = Counter()
    for pair0 in COMPONENT_PAIR_CHOICES[0]:
        for pair1 in COMPONENT_PAIR_CHOICES[1]:
            for pair2 in COMPONENT_PAIR_CHOICES[2]:
                vertices = tuple(sorted((*pair0, *pair1, *pair2)))
                if Counter(vertex // 12 for vertex in vertices) != {
                    0: 2,
                    1: 2,
                    2: 2,
                }:
                    rejected_fibre += 1
                    continue
                selected = set(vertices)
                if any(
                    (1 if vertex in selected else 0)
                    + len(adjacency[vertex] & selected)
                    > 2
                    for vertex in range(X_SIZE)
                ):
                    rejected_cut += 1
                    continue
                if any(
                    gram[left][right] == 0
                    for left, right in itertools.combinations(vertices, 2)
                ):
                    rejected_zero_target += 1
                    continue
                mask = sum(1 << vertex for vertex in vertices)
                candidates.append(mask)
                patterns[pattern_matrix(mask)] += 1
    if len(candidates) != len(set(candidates)):
        raise AssertionError("candidate enumeration produced duplicates")
    return candidates, {
        "raw_component_pair_products": 66**3,
        "rejected_wrong_fibre_totals": rejected_fibre,
        "rejected_mixed_cut": rejected_cut,
        "rejected_zero_gram_pair": rejected_zero_target,
        "candidate_count": len(candidates),
        "component_pattern_count": len(patterns),
        "component_patterns": [
            {
                "matrix": [list(row) for row in pattern],
                "candidate_count": count,
            }
            for pattern, count in sorted(patterns.items())
        ],
    }


def mask_vertices(mask: int) -> list[int]:
    return [vertex for vertex in range(X_SIZE) if mask >> vertex & 1]


def verify_design(
    adjacency: Sequence[set[int]],
    candidates: Sequence[int],
    selected_indices: Sequence[int],
) -> dict[str, object]:
    if len(selected_indices) != COLUMN_COUNT:
        raise AssertionError("design does not have 60 columns")
    if len(set(selected_indices)) != COLUMN_COUNT:
        raise AssertionError("design repeats a candidate index")
    masks = [candidates[index] for index in selected_indices]
    if len(set(masks)) != COLUMN_COUNT:
        raise AssertionError("design repeats a column")
    gram = gram_target(adjacency)
    actual = [[0] * X_SIZE for _ in range(X_SIZE)]
    for mask in masks:
        vertices = mask_vertices(mask)
        if len(vertices) != COLUMN_WEIGHT:
            raise AssertionError("column weight changed")
        if Counter(vertex // 12 for vertex in vertices) != {0: 2, 1: 2, 2: 2}:
            raise AssertionError("column fibre profile changed")
        if Counter((vertex % 12) // M for vertex in vertices) != {
            0: 2,
            1: 2,
            2: 2,
        }:
            raise AssertionError("column component profile changed")
        selected = set(vertices)
        if any(
            (1 if vertex in selected else 0)
            + len(adjacency[vertex] & selected)
            > 2
            for vertex in range(X_SIZE)
        ):
            raise AssertionError("column violates mixed cut")
        for left in vertices:
            for right in vertices:
                actual[left][right] += 1
    if actual != gram:
        raise AssertionError("B B^T does not equal the target Gram matrix")
    rows = [
        [1 if mask >> vertex & 1 else 0 for mask in masks]
        for vertex in range(X_SIZE)
    ]
    return {
        "verified": True,
        "shape": [X_SIZE, COLUMN_COUNT],
        "distinct_columns": len(set(masks)),
        "row_sums": sorted(set(map(sum, rows))),
        "column_sums": sorted(
            {
                sum(rows[row][column] for row in range(X_SIZE))
                for column in range(COLUMN_COUNT)
            }
        ),
        "matrix_rows": rows,
        "column_vertex_sets": [mask_vertices(mask) for mask in masks],
        "matrix_sha256": sha256_bytes(canonical_bytes(rows)),
    }


def native_minicard_solve(
    adjacency: Sequence[set[int]],
    candidates: Sequence[int],
    conflict_budget: int | None,
) -> dict[str, object]:
    """Solve with MiniCard's native at-most constraints.

    Equality ``sum(lits)=k`` is represented by the two native inequalities
    ``sum(lits)<=k`` and ``sum(not lits)<=n-k``.
    """

    try:
        from pysat.solvers import Solver
    except ImportError as error:
        return {
            "status": "UNAVAILABLE",
            "error": str(error),
            "hint": "run with the repository .venv containing python-sat",
        }
    require_memory()
    gram = gram_target(adjacency)
    variable_count = len(candidates)
    supports: dict[tuple[int, int], list[int]] = defaultdict(list)
    for index, mask in enumerate(candidates, start=1):
        vertices = mask_vertices(mask)
        for left, right in itertools.combinations(vertices, 2):
            supports[(left, right)].append(index)

    component_pair_target_sums = []
    component_pair_degree_sets = []
    for component in range(COMPONENTS):
        vertices = [
            global_vertex(component, local) for local in range(COMPONENT_SIZE)
        ]
        component_pair_target_sums.append(
            sum(
                gram[left][right]
                for left, right in itertools.combinations(vertices, 2)
            )
        )
        component_pair_degree_sets.append(
            sorted(
                {
                    sum(
                        gram[vertex][other]
                        for other in vertices
                        if other != vertex
                    )
                    for vertex in vertices
                }
            )
        )
    if component_pair_target_sums != [COLUMN_COUNT] * COMPONENTS:
        raise AssertionError("local pair targets do not force 60 columns")
    if component_pair_degree_sets != [[10], [10], [10]]:
        raise AssertionError("local pair targets do not force diagonal 10")

    constraints = []
    support_sizes = []
    for left in range(X_SIZE):
        for right in range(left + 1, X_SIZE):
            target = gram[left][right]
            literals = supports.get((left, right), [])
            support_sizes.append(len(literals))
            if target > len(literals):
                return {
                    "status": "TRIVIAL_UNSAT",
                    "claim_label": "UNKNOWN",
                    "reason": "target exceeds candidate support",
                    "entry": [left, right],
                    "target": target,
                    "support": len(literals),
                }
            if literals:
                constraints.append((literals, target))
            elif target:
                raise AssertionError("nonzero target has empty support")

    start = time.perf_counter()
    with Solver(name="minicard") as solver:
        for literals, target in constraints:
            solver.add_atmost(literals, target)
            solver.add_atmost(
                [-literal for literal in literals],
                len(literals) - target,
            )
        if conflict_budget is not None:
            solver.conf_budget(conflict_budget)
            satisfiable = solver.solve_limited(expect_interrupt=True)
        else:
            satisfiable = solver.solve()
        elapsed = time.perf_counter() - start
        statistics = solver.accum_stats()
        common = {
            "elapsed_seconds": elapsed,
            "solver": "minicard-native",
            "solver_statistics": statistics,
            "candidate_variable_count": variable_count,
            "native_atmost_constraint_count": 2 * len(constraints),
            "exact_cardinality_constraint_count": len(constraints),
            "redundant_diagonal_and_column_count": {
                "component_pair_target_sums": component_pair_target_sums,
                "component_pair_degree_sets": component_pair_degree_sets,
            },
            "support_size_min_max": [min(support_sizes), max(support_sizes)],
        }
        if satisfiable is True:
            model = solver.get_model()
            selected = [
                variable - 1
                for variable in model
                if 1 <= variable <= variable_count and variable > 0
            ]
            return {
                "status": "SAT",
                "claim_label": "CANDIDATE",
                **common,
                "selected_candidate_indices": selected,
                "design": verify_design(
                    adjacency, candidates, selected
                ),
            }
        return {
            "status": "UNSAT" if satisfiable is False else "UNKNOWN",
            "claim_label": "UNKNOWN",
            "proof_certificate_supplied": False,
            **common,
        }


def encode_and_solve(
    adjacency: Sequence[set[int]],
    candidates: Sequence[int],
    solver_name: str,
    conflict_budget: int | None,
    cnf_path: Path | None,
) -> dict[str, object]:
    if solver_name == "minicard":
        if cnf_path is not None:
            raise ValueError("native MiniCard mode does not emit DIMACS CNF")
        return native_minicard_solve(
            adjacency, candidates, conflict_budget
        )
    try:
        from pysat.card import CardEnc, EncType
        from pysat.formula import CNF, IDPool
        from pysat.solvers import Solver
    except ImportError as error:
        return {
            "status": "UNAVAILABLE",
            "error": str(error),
            "hint": "run with the repository .venv containing python-sat",
        }

    require_memory()
    gram = gram_target(adjacency)
    variable_count = len(candidates)
    supports: dict[tuple[int, int], list[int]] = defaultdict(list)
    for index, mask in enumerate(candidates, start=1):
        vertices = mask_vertices(mask)
        for vertex in vertices:
            supports[(vertex, vertex)].append(index)
        for left, right in itertools.combinations(vertices, 2):
            supports[(left, right)].append(index)

    cnf = CNF()
    pool = IDPool(start_from=variable_count + 1)
    constraint_count = 0
    support_sizes = []
    component_pair_target_sums = []
    component_pair_degree_sets = []
    for component in range(COMPONENTS):
        vertices = [
            global_vertex(component, local) for local in range(COMPONENT_SIZE)
        ]
        component_pair_target_sums.append(
            sum(gram[left][right] for left, right in itertools.combinations(vertices, 2))
        )
        component_pair_degree_sets.append(
            sorted(
                {
                    sum(
                        gram[vertex][other]
                        for other in vertices
                        if other != vertex
                    )
                    for vertex in vertices
                }
            )
        )
    if component_pair_target_sums != [COLUMN_COUNT] * COMPONENTS:
        raise AssertionError("local pair targets do not force 60 columns")
    if component_pair_degree_sets != [[10], [10], [10]]:
        raise AssertionError("local pair targets do not force diagonal 10")

    for left in range(X_SIZE):
        for right in range(left + 1, X_SIZE):
            target = gram[left][right]
            literals = supports.get((left, right), [])
            support_sizes.append(len(literals))
            if target > len(literals):
                return {
                    "status": "TRIVIAL_UNSAT",
                    "reason": "target exceeds candidate support",
                    "entry": [left, right],
                    "target": target,
                    "support": len(literals),
                }
            if not literals:
                if target:
                    raise AssertionError("nonzero target has empty support")
                continue
            encoded = CardEnc.equals(
                lits=literals,
                bound=target,
                vpool=pool,
                encoding=EncType.seqcounter,
            )
            cnf.extend(encoded.clauses)
            constraint_count += 1
    if cnf_path is not None:
        cnf.to_file(str(cnf_path))

    start = time.perf_counter()
    with Solver(name=solver_name, bootstrap_with=cnf.clauses) as solver:
        if conflict_budget is not None:
            solver.conf_budget(conflict_budget)
            satisfiable = solver.solve_limited(expect_interrupt=True)
        else:
            satisfiable = solver.solve()
        elapsed = time.perf_counter() - start
        statistics = solver.accum_stats()
        if satisfiable is True:
            model = solver.get_model()
            selected = [
                variable - 1
                for variable in model
                if 1 <= variable <= variable_count and variable > 0
            ]
            design = verify_design(adjacency, candidates, selected)
            return {
                "status": "SAT",
                "claim_label": "CANDIDATE",
                "elapsed_seconds": elapsed,
                "solver": solver_name,
                "solver_statistics": statistics,
                "candidate_variable_count": variable_count,
                "cnf_variable_count": cnf.nv,
                "cnf_clause_count": len(cnf.clauses),
                "exact_cardinality_constraint_count": constraint_count,
                "redundant_diagonal_and_column_count": {
                    "component_pair_target_sums": component_pair_target_sums,
                    "component_pair_degree_sets": component_pair_degree_sets,
                },
                "support_size_min_max": [min(support_sizes), max(support_sizes)],
                "selected_candidate_indices": selected,
                "design": design,
            }
        status = "UNSAT" if satisfiable is False else "UNKNOWN"
        return {
            "status": status,
            "claim_label": "UNKNOWN",
            "proof_certificate_supplied": False,
            "elapsed_seconds": elapsed,
            "solver": solver_name,
            "solver_statistics": statistics,
            "candidate_variable_count": variable_count,
            "cnf_variable_count": cnf.nv,
            "cnf_clause_count": len(cnf.clauses),
            "exact_cardinality_constraint_count": constraint_count,
            "redundant_diagonal_and_column_count": {
                "component_pair_target_sums": component_pair_target_sums,
                "component_pair_degree_sets": component_pair_degree_sets,
            },
            "support_size_min_max": [min(support_sizes), max(support_sizes)],
        }


def build_result(
    triple_index: int | None,
    solver_name: str,
    conflict_budget: int | None,
    cnf_path: Path | None,
    enumerate_only: bool = False,
) -> dict[str, object]:
    census = component_census()
    types = census["types"]
    triples = list(itertools.combinations_with_replacement(range(len(types)), 3))
    result: dict[str, object] = {
        "format": "wave60-c3-incidence-design-v1",
        "claim_label": "UNKNOWN",
        "scope": (
            "conditional kappa=3 neighbour core; component classification "
            "and exact B B^T incidence-design selection only"
        ),
        "memory_floor_percent": MIN_FREE_PERCENT,
        "free_memory_percent_at_start": free_memory_percent(),
        "component_census": census,
        "component_type_triples": [list(triple) for triple in triples],
    }
    if triple_index is None:
        return result
    if not 0 <= triple_index < len(triples):
        raise ValueError(f"triple index must be in [0,{len(triples)-1}]")
    triple = triples[triple_index]
    records = [types[index] for index in triple]
    adjacency = union_core(records)
    gram = gram_target(adjacency)
    candidates, candidate_summary = candidate_columns(adjacency, gram)
    solve = (
        {
            "status": "NOT_RUN",
            "claim_label": "UNKNOWN",
            "reason": "enumerate-only mode",
        }
        if enumerate_only
        else encode_and_solve(
            adjacency, candidates, solver_name, conflict_budget, cnf_path
        )
    )
    result["selected_triple_index"] = triple_index
    result["selected_type_triple"] = list(triple)
    result["global_core"] = {
        "edges": edge_list(adjacency),
        "C4": four_cycle_count(adjacency),
        "gram_diagonal_values": sorted({gram[i][i] for i in range(X_SIZE)}),
        "gram_offdiagonal_values": sorted(
            {
                gram[left][right]
                for left in range(X_SIZE)
                for right in range(left + 1, X_SIZE)
            }
        ),
        "gram_sha256": sha256_bytes(canonical_bytes(gram)),
    }
    result["candidate_enumeration"] = candidate_summary
    result["selection"] = solve
    if solve["status"] == "SAT":
        result["claim_label"] = "CANDIDATE"
    result["free_memory_percent_at_end"] = free_memory_percent()
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--triple-index", type=int)
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--conflict-budget", type=int)
    parser.add_argument("--cnf", type=Path)
    parser.add_argument("--enumerate-only", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = build_result(
        args.triple_index,
        args.solver,
        args.conflict_budget,
        args.cnf,
        args.enumerate_only,
    )
    payload = canonical_bytes(result)
    if args.output:
        args.output.write_bytes(payload)
    else:
        sys.stdout.buffer.write(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
