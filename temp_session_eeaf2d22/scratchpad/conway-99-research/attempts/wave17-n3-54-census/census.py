"""Exact fixed-F census for the frozen Wave 17 n3=54 structural residual.

The two official House of Graphs catalogs are fetched and validated entirely
in memory.  No catalog bytes are written to disk.

For each of the 457 residual point graphs F, the SAT layer searches for a
2-factor R on E(F) satisfying exact twofold rectangle coverage.  It then
progressively applies:

1. the independent N3 cross-edge matching rule;
2. common-neighbor caps in C=line(F) union R;
3. the exact spectral interval [-4,3] off the all-ones direction; and
4. the binary component/nullity restrictions.

Every SAT row carries a concrete R-edge witness.  A raw solver UNSAT is
reported only as UNSAT_UNVERIFIED because this scout emits no checked proof
trace.
"""

from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import platform
import sys
import time
from typing import Iterable, Iterator
import urllib.request

import pysat
from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver


CATALOGS = {
    18: {
        "url": "https://houseofgraphs.org/data/cubics/cub18-gir5.g6.gz",
        "compressed_bytes": 2470,
        "compressed_sha256": (
            "95ff5ca833f3a1361d652e8f585d8aed21af61d73d135abf366570dcbddfcf7e"
        ),
        "decompressed_bytes": 12740,
        "decompressed_sha256": (
            "39fb8633418927da9f5e3bd9fe81c83070a05ff65bfc532719618471a267f7fd"
        ),
        "records": 455,
    },
    12: {
        "url": "https://houseofgraphs.org/data/cubics/cub12-gir5.g6.gz",
        "compressed_bytes": 55,
        "compressed_sha256": (
            "c63e83c1b6c27af375c1f44f4dedfb5aa3f4f2abf01b6e68ba131942f72a6226"
        ),
        "decompressed_bytes": 26,
        "decompressed_sha256": (
            "ddf1582755db62e06d8072b7dfffb48357b56c677c11890eb14d9aeeb1ba55d4"
        ),
        "records": 2,
    },
}


Edge = tuple[int, int]


def edge(left: int, right: int) -> Edge:
    if left == right:
        raise ValueError("loop")
    return (left, right) if left < right else (right, left)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch_catalog(order: int, timeout: float = 30.0) -> tuple[bytes, ...]:
    metadata = CATALOGS[order]
    request = urllib.request.Request(
        str(metadata["url"]),
        headers={"User-Agent": "Conway99-Wave17-exact-census/1"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        compressed = response.read()
    if len(compressed) != metadata["compressed_bytes"]:
        raise AssertionError(f"order-{order} compressed byte count changed")
    if sha256_bytes(compressed) != metadata["compressed_sha256"]:
        raise AssertionError(f"order-{order} compressed hash changed")
    decompressed = gzip.decompress(compressed)
    if len(decompressed) != metadata["decompressed_bytes"]:
        raise AssertionError(f"order-{order} decompressed byte count changed")
    if sha256_bytes(decompressed) != metadata["decompressed_sha256"]:
        raise AssertionError(f"order-{order} decompressed hash changed")
    records = tuple(line for line in decompressed.splitlines() if line)
    if len(records) != metadata["records"]:
        raise AssertionError(f"order-{order} record count changed")
    if len(records) != len(set(records)):
        raise AssertionError(f"order-{order} catalog has duplicate records")
    return records


def decode_graph6(record: bytes) -> tuple[int, frozenset[Edge]]:
    if not record or record.startswith(b">>graph6<<"):
        raise ValueError("bare short graph6 record required")
    order = record[0] - 63
    if not 0 <= order <= 62:
        raise ValueError("short graph6 order required")
    bits: list[int] = []
    for raw in record[1:]:
        value = raw - 63
        if not 0 <= value <= 63:
            raise ValueError("bad graph6 byte")
        bits.extend((value >> shift) & 1 for shift in range(5, -1, -1))
    needed = order * (order - 1) // 2
    if len(bits) < needed:
        raise ValueError("truncated graph6 record")
    edges: set[Edge] = set()
    offset = 0
    for right in range(1, order):
        for left in range(right):
            if bits[offset]:
                edges.add((left, right))
            offset += 1
    return order, frozenset(edges)


def adjacency(order: int, edges: Iterable[Edge]) -> tuple[frozenset[int], ...]:
    rows = [set() for _ in range(order)]
    for left, right in edges:
        if not 0 <= left < right < order:
            raise AssertionError("edge outside graph order")
        rows[left].add(right)
        rows[right].add(left)
    return tuple(frozenset(row) for row in rows)


def is_connected(rows: tuple[frozenset[int], ...]) -> bool:
    seen = {0}
    frontier = [0]
    while frontier:
        root = frontier.pop()
        for neighbor in rows[root]:
            if neighbor not in seen:
                seen.add(neighbor)
                frontier.append(neighbor)
    return len(seen) == len(rows)


def validate_connected_cubic_girth5(
    order: int, edges: frozenset[Edge]
) -> None:
    if len(edges) != 3 * order // 2:
        raise AssertionError("wrong cubic edge count")
    rows = adjacency(order, edges)
    if any(len(row) != 3 for row in rows):
        raise AssertionError("graph is not cubic")
    if not is_connected(rows):
        raise AssertionError("catalog record is disconnected")
    for left, right in edges:
        if rows[left] & rows[right]:
            raise AssertionError("triangle found")
    for left, right in itertools.combinations(range(order), 2):
        if len(rows[left] & rows[right]) >= 2:
            raise AssertionError("4-cycle found")


def k33_edges(offset: int = 0) -> frozenset[Edge]:
    return frozenset(
        (offset + left, offset + right)
        for left in range(3)
        for right in range(3, 6)
    )


def shifted_edges(edges: Iterable[Edge], offset: int) -> frozenset[Edge]:
    return frozenset((left + offset, right + offset) for left, right in edges)


def build_cases() -> tuple[list[dict[str, object]], dict[str, object]]:
    records18 = fetch_catalog(18)
    records12 = fetch_catalog(12)
    cases: list[dict[str, object]] = []
    for index, record in enumerate(records18):
        order, edges = decode_graph6(record)
        if order != 18:
            raise AssertionError("order-18 catalog record changed order")
        validate_connected_cubic_girth5(order, edges)
        cases.append(
            {
                "case_id": f"connected18-{index:03d}",
                "family": "connected_cubic_girth5_order18",
                "catalog_order": 18,
                "catalog_index": index,
                "record_sha256": sha256_bytes(record),
                "F_edges": edges,
                "F_component_count": 1,
            }
        )
    for index, record in enumerate(records12):
        order, edges12 = decode_graph6(record)
        if order != 12:
            raise AssertionError("order-12 catalog record changed order")
        validate_connected_cubic_girth5(order, edges12)
        combined = k33_edges() | shifted_edges(edges12, 6)
        rows = adjacency(18, combined)
        if any(len(row) != 3 for row in rows):
            raise AssertionError("bad K3,3 plus order-12 union")
        cases.append(
            {
                "case_id": f"k33-plus-connected12-{index:03d}",
                "family": "K3,3_plus_connected_cubic_girth5_order12",
                "catalog_order": 12,
                "catalog_index": index,
                "record_sha256": sha256_bytes(record),
                "F_edges": frozenset(combined),
                "F_component_count": 2,
            }
        )
    metadata = {
        str(order): {
            key: value
            for key, value in CATALOGS[order].items()
        }
        for order in sorted(CATALOGS)
    }
    return cases, metadata


def mandatory_k(order: int, f_edges: frozenset[Edge]) -> frozenset[Edge]:
    rows = adjacency(order, f_edges)
    result = set(f_edges)
    for row in rows:
        result.update(edge(left, right) for left, right in itertools.combinations(row, 2))
    return frozenset(result)


def line_graph_edges(points: tuple[Edge, ...]) -> frozenset[Edge]:
    return frozenset(
        (left, right)
        for left, right in itertools.combinations(range(len(points)), 2)
        if set(points[left]) & set(points[right])
    )


def compatible_supports(
    points: tuple[Edge, ...], forbidden_label_pairs: frozenset[Edge]
) -> tuple[tuple[int, int, tuple[Edge, ...]], ...]:
    result = []
    for left, right in itertools.combinations(range(len(points)), 2):
        if set(points[left]) & set(points[right]):
            continue
        rectangle = tuple(
            sorted(
                edge(a, b)
                for a in points[left]
                for b in points[right]
            )
        )
        if any(item in forbidden_label_pairs for item in rectangle):
            continue
        result.append((left, right, rectangle))
    return tuple(result)


def add_at_most(
    cnf: CNF, pool: IDPool, literals: Iterable[int], bound: int
) -> None:
    literal_list = list(literals)
    if bound < 0:
        contradiction = pool.id(("forced_unsat", len(cnf.clauses)))
        cnf.append([contradiction])
        cnf.append([-contradiction])
        return
    if bound >= len(literal_list):
        return
    cnf.extend(
        CardEnc.atmost(
            literal_list,
            bound,
            vpool=pool,
            encoding=EncType.seqcounter,
        )
    )


def add_equals(
    cnf: CNF, pool: IDPool, literals: Iterable[int], bound: int
) -> None:
    literal_list = list(literals)
    if bound < 0 or bound > len(literal_list):
        contradiction = pool.id(("forced_unsat", len(cnf.clauses)))
        cnf.append([contradiction])
        cnf.append([-contradiction])
        return
    if bound == 0:
        cnf.extend([[-literal] for literal in literal_list])
        return
    if bound == len(literal_list):
        cnf.extend([[literal] for literal in literal_list])
        return
    cnf.extend(
        CardEnc.equals(
            literal_list,
            bound,
            vpool=pool,
            encoding=EncType.seqcounter,
        )
    )


def build_instance(
    f_edges: frozenset[Edge], *, enforce_matching: bool
) -> dict[str, object]:
    points = tuple(sorted(f_edges))
    if len(points) != 27:
        raise AssertionError("point graph must have 27 edges")
    forbidden = mandatory_k(18, f_edges)
    candidates = compatible_supports(points, forbidden)
    pool = IDPool()
    variables = {
        index: pool.id(("R", index)) for index in range(len(candidates))
    }
    cnf = CNF()

    for point in range(27):
        add_equals(
            cnf,
            pool,
            (
                variables[index]
                for index, (left, right, _) in enumerate(candidates)
                if point in (left, right)
            ),
            2,
        )

    for label_pair in itertools.combinations(range(18), 2):
        cover_indices = [
            index
            for index, (_, _, rectangle) in enumerate(candidates)
            if label_pair in rectangle
        ]
        covers = [variables[index] for index in cover_indices]
        add_at_most(cnf, pool, covers, 2)
        for index in cover_indices:
            cnf.append(
                [
                    -variables[index],
                    *(
                        variables[other]
                        for other in cover_indices
                        if other != index
                    ),
                ]
            )
        if enforce_matching:
            for side_label in label_pair:
                for point, point_edge in enumerate(points):
                    if side_label not in point_edge:
                        continue
                    same_point = [
                        variables[index]
                        for index in cover_indices
                        if point in candidates[index][:2]
                    ]
                    add_at_most(cnf, pool, same_point, 1)

    return {
        "points": points,
        "forbidden": forbidden,
        "candidates": candidates,
        "variables": variables,
        "cnf": cnf,
        "pool_top": pool.top,
    }


def selected_from_model(
    instance: dict[str, object], model: list[int]
) -> tuple[Edge, ...]:
    positive = {literal for literal in model if literal > 0}
    candidates = instance["candidates"]
    variables = instance["variables"]
    return tuple(
        (left, right)
        for index, (left, right, _) in enumerate(candidates)
        if variables[index] in positive
    )


def witness_record(selected: tuple[Edge, ...]) -> dict[str, object]:
    return {"R_edges": [list(item) for item in selected]}


def support_edge_to_variable(
    instance: dict[str, object],
) -> dict[Edge, int]:
    candidates = instance["candidates"]
    variables = instance["variables"]
    return {
        (left, right): variables[index]
        for index, (left, right, _) in enumerate(candidates)
    }


def active_graph_rows(
    line_edges: frozenset[Edge], selected: tuple[Edge, ...]
) -> tuple[frozenset[int], ...]:
    return adjacency(27, line_edges | frozenset(selected))


def first_cap_violation(
    line_edges: frozenset[Edge],
    selected: tuple[Edge, ...],
    variable_for_edge: dict[Edge, int],
) -> tuple[bool, list[int], dict[str, object] | None]:
    selected_set = frozenset(selected)
    graph_edges = line_edges | selected_set
    rows = active_graph_rows(line_edges, selected)
    for left, right in itertools.combinations(range(27), 2):
        common = sorted(rows[left] & rows[right])
        adjacent = (left, right) in graph_edges
        limit = 1 if adjacent else 2
        if len(common) <= limit:
            continue
        required: set[int] = set()
        if adjacent and (left, right) in selected_set:
            required.add(variable_for_edge[(left, right)])
        for middle in common[: limit + 1]:
            for pair in (edge(left, middle), edge(right, middle)):
                if pair in selected_set:
                    required.add(variable_for_edge[pair])
        clause = sorted(-literal for literal in required)
        return (
            False,
            clause,
            {
                "pair": [left, right],
                "adjacent": adjacent,
                "common_count": len(common),
                "limit": limit,
            },
        )
    return True, [], None


def is_psd_exact(matrix: list[list[int]]) -> bool:
    work = [[Fraction(value) for value in row] for row in matrix]
    order = len(work)
    for pivot_index in range(order):
        for row in range(pivot_index, order):
            if work[row][row] < 0:
                return False
            if work[row][row] == 0 and any(
                work[row][column] != 0
                for column in range(pivot_index, order)
                if column != row
            ):
                return False
        pivot = next(
            (
                row
                for row in range(pivot_index, order)
                if work[row][row] > 0
            ),
            None,
        )
        if pivot is None:
            return all(
                work[row][column] == 0
                for row in range(pivot_index, order)
                for column in range(pivot_index, order)
            )
        if pivot != pivot_index:
            work[pivot_index], work[pivot] = work[pivot], work[pivot_index]
            for row in range(order):
                work[row][pivot_index], work[row][pivot] = (
                    work[row][pivot],
                    work[row][pivot_index],
                )
        pivot_value = work[pivot_index][pivot_index]
        for row in range(pivot_index + 1, order):
            for column in range(row, order):
                value = (
                    work[row][column]
                    - work[row][pivot_index]
                    * work[pivot_index][column]
                    / pivot_value
                )
                work[row][column] = value
                work[column][row] = value
        for row in range(pivot_index + 1, order):
            work[row][pivot_index] = Fraction(0)
            work[pivot_index][row] = Fraction(0)
    return True


def spectral_interval_ok(rows: tuple[frozenset[int], ...]) -> bool:
    if any(len(row) != 6 for row in rows):
        return False
    order = len(rows)
    upper = []
    lower = []
    for left in range(order):
        upper_row = []
        lower_row = []
        for right in range(order):
            adjacent = int(right in rows[left])
            upper_row.append(
                27 * int(left == right) - 9 * adjacent + 1
            )
            lower_row.append(
                27 * adjacent + 108 * int(left == right) - 10
            )
        upper.append(upper_row)
        lower.append(lower_row)
    return is_psd_exact(upper) and is_psd_exact(lower)


def cycle_lengths(
    order: int, selected: tuple[Edge, ...]
) -> tuple[int, ...]:
    rows = adjacency(order, selected)
    if any(len(row) != 2 for row in rows):
        raise AssertionError("R is not a 2-factor")
    unseen = set(range(order))
    lengths = []
    while unseen:
        root = min(unseen)
        component = {root}
        frontier = [root]
        unseen.remove(root)
        while frontier:
            current = frontier.pop()
            for neighbor in rows[current]:
                if neighbor in unseen:
                    unseen.remove(neighbor)
                    component.add(neighbor)
                    frontier.append(neighbor)
        lengths.append(len(component))
    return tuple(sorted(lengths))


def binary_restrictions_ok(
    selected: tuple[Edge, ...], f_component_count: int
) -> tuple[bool, dict[str, object]]:
    lengths = cycle_lengths(27, selected)
    odd = sum(length % 2 for length in lengths)
    even = len(lengths) - odd
    nullity = odd + 2 * even
    result = {
        "R_cycle_lengths": list(lengths),
        "R_component_count": len(lengths),
        "R_adjacency_nullity_mod2": nullity,
        "required_component_count": 5 - f_component_count,
        "required_nullity": 9 - 2 * f_component_count,
    }
    ok = (
        len(lengths) >= 5 - f_component_count
        and nullity >= 9 - 2 * f_component_count
    )
    return ok, result


def solve_once(instance: dict[str, object]) -> tuple[str, tuple[Edge, ...] | None]:
    with Solver(name="cadical195", bootstrap_with=instance["cnf"]) as solver:
        satisfiable = solver.solve()
        if satisfiable is not True:
            return "UNSAT_UNVERIFIED", None
        selected = selected_from_model(instance, solver.get_model())
        return "SAT_CANDIDATE", selected


def solve_progressive(
    instance: dict[str, object],
    line_edges: frozenset[Edge],
    f_component_count: int,
    model_limit: int,
) -> dict[str, object]:
    stages: dict[str, dict[str, object]] = {
        "matching": {"status": "NOT_REACHED"},
        "common_neighbor_caps": {"status": "NOT_REACHED"},
        "spectrum": {"status": "NOT_REACHED"},
        "binary_restrictions": {"status": "NOT_REACHED"},
    }
    variable_for_edge = support_edge_to_variable(instance)
    models = 0
    cap_rejections = 0
    spectral_rejections = 0
    binary_rejections = 0
    with Solver(name="cadical195", bootstrap_with=instance["cnf"]) as solver:
        while True:
            satisfiable = solver.solve()
            if satisfiable is not True:
                if stages["matching"]["status"] == "NOT_REACHED":
                    stages["matching"] = {"status": "UNSAT_UNVERIFIED"}
                elif stages["common_neighbor_caps"]["status"] == "NOT_REACHED":
                    stages["common_neighbor_caps"] = {
                        "status": "UNSAT_UNVERIFIED"
                    }
                elif stages["spectrum"]["status"] == "NOT_REACHED":
                    stages["spectrum"] = {"status": "UNSAT_UNVERIFIED"}
                elif stages["binary_restrictions"]["status"] == "NOT_REACHED":
                    stages["binary_restrictions"] = {
                        "status": "UNSAT_UNVERIFIED"
                    }
                break
            models += 1
            if models > model_limit:
                first_unreached = next(
                    name
                    for name in (
                        "matching",
                        "common_neighbor_caps",
                        "spectrum",
                        "binary_restrictions",
                    )
                    if stages[name]["status"] == "NOT_REACHED"
                )
                stages[first_unreached] = {
                    "status": "MODEL_LIMIT",
                    "model_limit": model_limit,
                }
                break
            selected = selected_from_model(instance, solver.get_model())
            if stages["matching"]["status"] == "NOT_REACHED":
                stages["matching"] = {
                    "status": "SAT_CANDIDATE",
                    "witness": witness_record(selected),
                }

            cap_ok, clause, violation = first_cap_violation(
                line_edges, selected, variable_for_edge
            )
            if not cap_ok:
                cap_rejections += 1
                solver.add_clause(clause)
                continue
            if stages["common_neighbor_caps"]["status"] == "NOT_REACHED":
                stages["common_neighbor_caps"] = {
                    "status": "SAT_CANDIDATE",
                    "witness": witness_record(selected),
                }

            rows = active_graph_rows(line_edges, selected)
            if not spectral_interval_ok(rows):
                spectral_rejections += 1
                solver.add_clause(
                    [
                        -variable_for_edge[item]
                        for item in selected
                    ]
                )
                continue
            if stages["spectrum"]["status"] == "NOT_REACHED":
                stages["spectrum"] = {
                    "status": "SAT_CANDIDATE",
                    "witness": witness_record(selected),
                }

            binary_ok, binary_data = binary_restrictions_ok(
                selected, f_component_count
            )
            if not binary_ok:
                binary_rejections += 1
                solver.add_clause(
                    [
                        -variable_for_edge[item]
                        for item in selected
                    ]
                )
                continue
            stages["binary_restrictions"] = {
                "status": "SAT_CANDIDATE",
                "witness": witness_record(selected),
                "binary_data": binary_data,
            }
            break
    return {
        "stages": stages,
        "search_statistics": {
            "models_examined": models,
            "common_cap_rejections": cap_rejections,
            "spectral_rejections": spectral_rejections,
            "binary_rejections": binary_rejections,
        },
    }


def summarize_cases(cases: list[dict[str, object]]) -> dict[str, object]:
    stage_names = (
        "exact_coverage",
        "matching",
        "common_neighbor_caps",
        "spectrum",
        "binary_restrictions",
    )
    status_counts = {
        stage: dict(
            sorted(
                Counter(
                    case["stages"][stage]["status"] for case in cases
                ).items()
            )
        )
        for stage in stage_names
    }
    family_counts = dict(sorted(Counter(case["family"] for case in cases).items()))
    return {
        "case_count": len(cases),
        "family_counts": family_counts,
        "stage_status_counts": status_counts,
        "total_models_examined": sum(
            case["search_statistics"]["models_examined"] for case in cases
        ),
        "total_common_cap_rejections": sum(
            case["search_statistics"]["common_cap_rejections"] for case in cases
        ),
        "total_spectral_rejections": sum(
            case["search_statistics"]["spectral_rejections"] for case in cases
        ),
        "total_binary_rejections": sum(
            case["search_statistics"]["binary_rejections"] for case in cases
        ),
    }


def run(start: int, limit: int | None, model_limit: int) -> dict[str, object]:
    all_cases, catalog_metadata = build_cases()
    stop = len(all_cases) if limit is None else min(len(all_cases), start + limit)
    selected_cases = all_cases[start:stop]
    outputs = []
    started = time.perf_counter()
    for offset, case in enumerate(selected_cases):
        f_edges = case["F_edges"]
        points = tuple(sorted(f_edges))
        line_edges = line_graph_edges(points)
        base = build_instance(f_edges, enforce_matching=False)
        base_status, base_witness = solve_once(base)
        stages: dict[str, dict[str, object]] = {
            "exact_coverage": {"status": base_status},
            "matching": {"status": "NOT_REACHED"},
            "common_neighbor_caps": {"status": "NOT_REACHED"},
            "spectrum": {"status": "NOT_REACHED"},
            "binary_restrictions": {"status": "NOT_REACHED"},
        }
        statistics = {
            "models_examined": 0,
            "common_cap_rejections": 0,
            "spectral_rejections": 0,
            "binary_rejections": 0,
        }
        if base_witness is not None:
            stages["exact_coverage"]["witness"] = witness_record(base_witness)
            matched = build_instance(f_edges, enforce_matching=True)
            progressive = solve_progressive(
                matched,
                line_edges,
                int(case["F_component_count"]),
                model_limit,
            )
            stages.update(progressive["stages"])
            statistics = progressive["search_statistics"]
        output_case = {
            key: case[key]
            for key in (
                "case_id",
                "family",
                "catalog_order",
                "catalog_index",
                "record_sha256",
                "F_component_count",
            )
        }
        output_case.update(
            {
                "mandatory_K_edge_count": len(mandatory_k(18, f_edges)),
                "compatible_support_count": len(base["candidates"]),
                "base_variables": base["pool_top"],
                "base_clauses": len(base["cnf"].clauses),
                "stages": stages,
                "search_statistics": statistics,
            }
        )
        outputs.append(output_case)
        completed = offset + 1
        if completed % 25 == 0 or completed == len(selected_cases):
            print(
                f"processed {completed}/{len(selected_cases)} cases",
                file=sys.stderr,
                flush=True,
            )
    _elapsed = time.perf_counter() - started
    result = {
        "schema_version": 1,
        "scope": "fixed-F census of the frozen Wave17 n3=54 F/R residual",
        "catalogs": catalog_metadata,
        "catalog_redistributed": False,
        "catalog_fetch_mode": "HTTPS into memory with exact compressed and decompressed validation",
        "full_case_count": len(all_cases),
        "slice": {"start": start, "stop": stop, "count": len(outputs)},
        "model_limit_per_case": model_limit,
        "solver_status_boundary": (
            "SAT rows carry witnesses; UNSAT has no checked proof trace and "
            "is labeled UNSAT_UNVERIFIED"
        ),
        "tool_versions": {
            "python": platform.python_version(),
            "python_implementation": platform.python_implementation(),
            "python_sat": pysat.__version__,
            "solver": "cadical195 via python-sat",
        },
        "summary": summarize_cases(outputs),
        "cases": outputs,
        "claim_status": "CANDIDATE_CENSUS_PENDING_INDEPENDENT_VALIDATION",
        "conditional_n3_54": "UNKNOWN",
        "conway_99": "UNKNOWN",
        "novelty": "UNKNOWN",
    }
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--model-limit", type=int, default=100_000)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.start < 0:
        raise SystemExit("--start must be nonnegative")
    if args.limit is not None and args.limit <= 0:
        raise SystemExit("--limit must be positive")
    if args.model_limit <= 0:
        raise SystemExit("--model-limit must be positive")
    result = run(args.start, args.limit, args.model_limit)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
