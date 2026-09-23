#!/usr/bin/env python3
"""Wave 63 rational-cone and distinct-column screens.

This is discovery code.  A floating-point solver result is never promoted to
an exact claim.  Feasible results are retained only when rationalization of
every coefficient replays all 630 pair equations exactly.  Infeasible solver
statuses remain numerical UNKNOWN unless an explicit Farkas certificate is
present and replayed (this version emits no such certificate).
"""

from __future__ import annotations

import argparse
import ctypes
from dataclasses import dataclass
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
import time
from typing import Iterable, Sequence

import numpy as np
from flint import fmpq_mat
from scipy.linalg import qr
from scipy.optimize import Bounds, LinearConstraint, linprog, milp
from scipy.sparse import csc_matrix


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
INPUT = ROOT / "attempts/wave60-c3-incidence-design/component-census.json"
WAVE60_RESULTS = ROOT / "attempts/wave60-c3-incidence-design/exact-results.json"
WAVE61_RESULTS = ROOT / "attempts/wave61-c3-finite-field/exact-results.json"
FROZEN = {
    INPUT: "16e124587df5b37b3f4735e14894982750c60a303043125985383101331eb4de",
    WAVE60_RESULTS:
        "35b6436c7ba5619fcf7e3840cbdacd594461c01df8758686450f5d8eea8e36f3",
    WAVE61_RESULTS:
        "936c76b7487d713421ef663aae4cc591f9bcf93f5d6a11f4aae3c0b5d4aa52f6",
}
MEMORY_FLOOR_PERCENT = 20.0
PAIR_LIST_12 = tuple(itertools.combinations(range(12), 2))
PAIR_LIST_36 = tuple(itertools.combinations(range(36), 2))
PAIR_INDEX_36 = {pair: index for index, pair in enumerate(PAIR_LIST_36)}


class MemoryStatusEx(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_ulong),
        ("dwMemoryLoad", ctypes.c_ulong),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]


def free_memory_percent() -> float:
    status = MemoryStatusEx()
    status.dwLength = ctypes.sizeof(status)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise OSError("GlobalMemoryStatusEx failed")
    return 100.0 * status.ullAvailPhys / status.ullTotalPhys


def require_memory() -> float:
    free = free_memory_percent()
    if free < MEMORY_FLOOR_PERCENT:
        raise MemoryError(
            f"free physical memory {free:.2f}% is below "
            f"the {MEMORY_FLOOR_PERCENT:.2f}% Wave 63 floor"
        )
    return free


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def check_frozen_inputs() -> None:
    for path, expected in FROZEN.items():
        actual = sha256(path)
        if actual != expected:
            raise AssertionError(
                f"frozen input changed: {path.relative_to(ROOT)} "
                f"expected {expected}, got {actual}"
            )


def global_vertex(component: int, local_vertex: int) -> int:
    fibre, local_index = divmod(local_vertex, 4)
    return fibre * 12 + component * 4 + local_index


def validate_component(record: dict) -> tuple[int, ...]:
    rows = [0] * 12
    for edge in record["edges"]:
        if not (
            isinstance(edge, list)
            and len(edge) == 2
            and 0 <= edge[0] < edge[1] < 12
        ):
            raise AssertionError("malformed component edge")
        left, right = edge
        if rows[left] >> right & 1:
            raise AssertionError("duplicate component edge")
        rows[left] |= 1 << right
        rows[right] |= 1 << left
    if {row.bit_count() for row in rows} != {3}:
        raise AssertionError("component is not cubic")
    reached = 1
    frontier = 1
    while frontier:
        next_frontier = 0
        for vertex in range(12):
            if frontier >> vertex & 1:
                next_frontier |= rows[vertex]
        next_frontier &= ~reached
        reached |= next_frontier
        frontier = next_frontier
    if reached != (1 << 12) - 1:
        raise AssertionError("component is disconnected")
    for fibre in range(3):
        vertices = range(4 * fibre, 4 * fibre + 4)
        if {
            sum(rows[left] >> right & 1 for right in vertices)
            for left in vertices
        } != {1}:
            raise AssertionError("fibre does not induce a perfect matching")
    for first, second in itertools.combinations(range(3), 2):
        right_vertices = range(4 * second, 4 * second + 4)
        if {
            sum(rows[left] >> right & 1 for right in right_vertices)
            for left in range(4 * first, 4 * first + 4)
        } != {1}:
            raise AssertionError("cross-fibre edges are not a perfect matching")
    if any(
        (rows[left] & rows[right]).bit_count()
        for left, right in itertools.combinations(range(12), 2)
        if rows[left] >> right & 1
    ):
        raise AssertionError("component has a triangle")
    for left, right in itertools.combinations(range(12), 2):
        if rows[left] >> right & 1:
            continue
        cap = 1 if left // 4 == right // 4 else 2
        if (rows[left] & rows[right]).bit_count() > cap:
            raise AssertionError("component violates sector codegree cap")
    return tuple(rows)


def load_types() -> list[dict]:
    data = json.loads(INPUT.read_text(encoding="utf-8"))
    census = data["component_census"]
    records = census["types"]
    if len(records) != 18:
        raise AssertionError("expected 18 frozen fibre-preserving types")
    if [record["type_index"] for record in records] != list(range(18)):
        raise AssertionError("component type indices are not canonical 0..17")
    for record in records:
        validate_component(record)
    return records


def union_rows(records: Sequence[dict]) -> tuple[int, ...]:
    rows = [0] * 36
    for component, record in enumerate(records):
        local = validate_component(record)
        for left in range(12):
            global_left = global_vertex(component, left)
            for right in range(left + 1, 12):
                if local[left] >> right & 1:
                    global_right = global_vertex(component, right)
                    rows[global_left] |= 1 << global_right
                    rows[global_right] |= 1 << global_left
    if {row.bit_count() for row in rows} != {3}:
        raise AssertionError("union core is not cubic")
    return tuple(rows)


def target_gram(records: Sequence[dict]) -> tuple[tuple[int, ...], ...]:
    adjacency = union_rows(records)
    matrix: list[tuple[int, ...]] = []
    for left in range(36):
        row = []
        for right in range(36):
            common = (adjacency[left] & adjacency[right]).bit_count()
            value = (
                (12 if left == right else 0)
                - (1 if adjacency[left] >> right & 1 else 0)
                + 2
                - (1 if left // 12 == right // 12 else 0)
                - common
            )
            if value < 0:
                raise AssertionError("negative Gram target")
            row.append(value)
        matrix.append(tuple(row))
    if [matrix[index][index] for index in range(36)] != [10] * 36:
        raise AssertionError("unexpected Gram diagonal")
    return tuple(matrix)


def pair_profile(pair: tuple[int, int]) -> tuple[int, int, int]:
    result = [0, 0, 0]
    result[pair[0] // 4] += 1
    result[pair[1] // 4] += 1
    return tuple(result)


PROFILE_VALUES = tuple(sorted({pair_profile(pair) for pair in PAIR_LIST_12}))
PROFILE_TRIPLES = tuple(
    indices
    for indices in itertools.product(range(len(PROFILE_VALUES)), repeat=3)
    if tuple(
        sum(PROFILE_VALUES[index][fibre] for index in indices)
        for fibre in range(3)
    ) == (2, 2, 2)
)
if len(PROFILE_TRIPLES) != 21:
    raise AssertionError("expected 21 fibre/component profiles")


def local_gram(record: dict) -> tuple[tuple[int, ...], ...]:
    adjacency = validate_component(record)
    matrix = []
    for left in range(12):
        row = []
        for right in range(12):
            value = (
                (12 if left == right else 0)
                - (1 if adjacency[left] >> right & 1 else 0)
                + 2
                - (1 if left // 4 == right // 4 else 0)
                - (adjacency[left] & adjacency[right]).bit_count()
            )
            if value < 0:
                raise AssertionError("negative local Gram target")
            row.append(value)
        matrix.append(tuple(row))
    return tuple(matrix)


def allowed_pairs(record: dict) -> tuple[tuple[int, ...], ...]:
    gram = local_gram(record)
    output = [[] for _ in PROFILE_VALUES]
    for index, pair in enumerate(PAIR_LIST_12):
        if gram[pair[0]][pair[1]] > 0:
            output[PROFILE_VALUES.index(pair_profile(pair))].append(index)
    return tuple(tuple(values) for values in output)


def candidate_columns(records: Sequence[dict]) -> list[tuple[int, ...]]:
    local = [allowed_pairs(record) for record in records]
    candidates = []
    seen = set()
    for profiles in PROFILE_TRIPLES:
        choices = [
            local[component][profiles[component]]
            for component in range(3)
        ]
        for pair_indices in itertools.product(*choices):
            vertices = tuple(sorted(
                global_vertex(component, vertex)
                for component, pair_index in enumerate(pair_indices)
                for vertex in PAIR_LIST_12[pair_index]
            ))
            if len(vertices) != 6 or len(set(vertices)) != 6:
                raise AssertionError("candidate is not a distinct six-set")
            if tuple(
                sum(vertex // 12 == fibre for vertex in vertices)
                for fibre in range(3)
            ) != (2, 2, 2):
                raise AssertionError("candidate has wrong fibre profile")
            if vertices in seen:
                raise AssertionError("duplicate candidate")
            seen.add(vertices)
            candidates.append(vertices)
    return candidates


def candidate_count(records: Sequence[dict]) -> int:
    """Count the same Cartesian products without materializing six-sets."""
    local = [allowed_pairs(record) for record in records]
    return sum(
        len(local[0][profiles[0]])
        * len(local[1][profiles[1]])
        * len(local[2][profiles[2]])
        for profiles in PROFILE_TRIPLES
    )


@dataclass(frozen=True)
class PairSystem:
    active_pairs: tuple[tuple[int, int], ...]
    rhs: tuple[int, ...]
    matrix: csc_matrix


def pair_system(
    candidates: Sequence[tuple[int, ...]],
    gram: Sequence[Sequence[int]],
) -> PairSystem:
    active_pairs = tuple(
        pair for pair in PAIR_LIST_36 if gram[pair[0]][pair[1]] > 0
    )
    active_index = {pair: index for index, pair in enumerate(active_pairs)}
    rows: list[int] = []
    columns: list[int] = []
    for column, candidate in enumerate(candidates):
        for pair in itertools.combinations(candidate, 2):
            if pair not in active_index:
                raise AssertionError("candidate contains zero-target pair")
            rows.append(active_index[pair])
            columns.append(column)
    values = np.ones(len(rows), dtype=np.float64)
    matrix = csc_matrix(
        (values, (rows, columns)),
        shape=(len(active_pairs), len(candidates)),
    )
    if set(np.diff(matrix.indptr)) != {15}:
        raise AssertionError("candidate matrix columns do not have weight 15")
    rhs = tuple(gram[left][right] for left, right in active_pairs)
    return PairSystem(active_pairs, rhs, matrix)


def replay_fraction_witness(
    candidates: Sequence[tuple[int, ...]],
    gram: Sequence[Sequence[int]],
    witness: Sequence[tuple[int, Fraction]],
    upper_bound_one: bool,
) -> dict:
    totals = [Fraction(0) for _ in PAIR_LIST_36]
    total_weight = Fraction(0)
    for index, coefficient in witness:
        if not 0 <= index < len(candidates):
            raise AssertionError("witness candidate index out of range")
        if coefficient < 0:
            raise AssertionError("negative witness coefficient")
        if upper_bound_one and coefficient > 1:
            raise AssertionError("witness violates x<=1")
        total_weight += coefficient
        for pair in itertools.combinations(candidates[index], 2):
            totals[PAIR_INDEX_36[pair]] += coefficient
    expected = [
        Fraction(gram[left][right])
        for left, right in PAIR_LIST_36
    ]
    if totals != expected:
        mismatches = sum(left != right for left, right in zip(totals, expected))
        raise AssertionError(f"exact witness has {mismatches} pair mismatches")
    if total_weight != 60:
        raise AssertionError(f"witness total is {total_weight}, not 60")
    return {
        "coefficient_count": len(witness),
        "total_weight": str(total_weight),
        "maximum_denominator": max(
            (coefficient.denominator for _, coefficient in witness),
            default=1,
        ),
        "maximum_coefficient": str(
            max((coefficient for _, coefficient in witness), default=Fraction(0))
        ),
        "all_630_pair_equations_exact": True,
        "distinct_column_upper_bound_exact": upper_bound_one,
    }


def rationalize_solution(
    values: np.ndarray,
    system: PairSystem,
    candidates: Sequence[tuple[int, ...]],
    gram: Sequence[Sequence[int]],
    upper_bound_one: bool,
    max_denominator: int = 1_000_000,
    threshold: float = 1e-9,
) -> tuple[list[tuple[int, Fraction]], dict] | None:
    witness = [
        (index, Fraction(float(value)).limit_denominator(max_denominator))
        for index, value in enumerate(values)
        if value > threshold
    ]
    witness = [(index, value) for index, value in witness if value]
    try:
        replay = replay_fraction_witness(
            candidates, gram, witness, upper_bound_one
        )
        replay["exactification_method"] = (
            f"independent coefficient rounding with denominator <= "
            f"{max_denominator}"
        )
        return witness, replay
    except AssertionError:
        pass

    # A HiGHS dual-simplex basic feasible solution normally has linearly
    # independent positive columns.  Select an independent square row minor
    # numerically, then solve that integer minor exactly with FLINT/Dixon and
    # replay all 630 equations.  The numerical row choice makes no claim:
    # exact solve plus full replay is the certificate gate.
    support = [
        index for index, value in enumerate(values) if value > threshold
    ]
    if not support or len(support) > len(system.active_pairs):
        return None
    dense = system.matrix[:, support].toarray().astype(np.int64)
    _, triangular, row_pivots = qr(
        dense.T.astype(np.float64),
        mode="economic",
        pivoting=True,
        check_finite=False,
    )
    diagonal = np.abs(np.diag(triangular))
    if len(diagonal) < len(support) or np.count_nonzero(diagonal > 1e-9) < len(support):
        return None
    selected_rows = [int(value) for value in row_pivots[:len(support)]]
    square_values = dense[selected_rows, :].reshape(-1).tolist()
    exact_matrix = fmpq_mat(len(support), len(support), square_values)
    exact_rhs = fmpq_mat(
        len(support),
        1,
        [system.rhs[row] for row in selected_rows],
    )
    try:
        exact_solution = exact_matrix.solve(exact_rhs, algorithm="dixon")
    except ZeroDivisionError:
        return None
    witness = [
        (
            candidate_index,
            Fraction(
                int(exact_solution[position, 0].p),
                int(exact_solution[position, 0].q),
            ),
        )
        for position, candidate_index in enumerate(support)
        if exact_solution[position, 0]
    ]
    try:
        replay = replay_fraction_witness(
            candidates, gram, witness, upper_bound_one
        )
    except AssertionError:
        return None
    replay["exactification_method"] = (
        "FLINT fmpq Dixon solve on a QR-selected square row minor, followed "
        "by independent exact replay of all 630 pair equations"
    )
    replay["square_minor_order"] = len(support)
    return witness, replay


def encode_witness(
    witness: Sequence[tuple[int, Fraction]]
) -> list[dict[str, int]]:
    return [
        {
            "candidate_index": index,
            "numerator": value.numerator,
            "denominator": value.denominator,
        }
        for index, value in witness
    ]


def solve_rational_cone(
    system: PairSystem,
    candidates: Sequence[tuple[int, ...]],
    gram: Sequence[Sequence[int]],
    time_limit: float,
) -> dict:
    require_memory()
    start = time.monotonic()
    result = linprog(
        np.zeros(len(candidates)),
        A_eq=system.matrix,
        b_eq=np.asarray(system.rhs, dtype=np.float64),
        bounds=(0, None),
        method="highs-ds",
        options={"time_limit": time_limit, "presolve": True},
    )
    elapsed = time.monotonic() - start
    output: dict = {
        "solver": "scipy.optimize.linprog highs-ds",
        "solver_status": int(result.status),
        "solver_message": str(result.message),
        "elapsed_seconds": round(elapsed, 6),
        "floating_only": True,
        "claim_label": "UNKNOWN",
    }
    if result.x is not None:
        residual = system.matrix @ result.x - np.asarray(system.rhs)
        output["floating_max_abs_residual"] = float(
            np.max(np.abs(residual), initial=0.0)
        )
        output["floating_positive_support"] = int(
            np.count_nonzero(result.x > 1e-9)
        )
        exact = rationalize_solution(
            result.x, system, candidates, gram, False
        )
        if exact is not None:
            witness, replay = exact
            output.update({
                "floating_only": False,
                "claim_label": "DERIVED",
                "exact_witness": encode_witness(witness),
                "exact_replay": replay,
            })
    if not result.success and output["claim_label"] == "UNKNOWN":
        output["interpretation"] = (
            "numerical non-success only; no Farkas certificate, so no "
            "infeasibility claim"
        )
    return output


def solve_distinct_milp(
    system: PairSystem,
    candidates: Sequence[tuple[int, ...]],
    gram: Sequence[Sequence[int]],
    time_limit: float,
) -> dict:
    require_memory()
    start = time.monotonic()
    constraints = LinearConstraint(
        system.matrix,
        np.asarray(system.rhs, dtype=np.float64),
        np.asarray(system.rhs, dtype=np.float64),
    )
    result = milp(
        np.zeros(len(candidates)),
        integrality=np.ones(len(candidates), dtype=np.uint8),
        bounds=Bounds(0, 1),
        constraints=constraints,
        options={
            "time_limit": time_limit,
            "mip_rel_gap": 0.0,
            "presolve": True,
        },
    )
    elapsed = time.monotonic() - start
    output: dict = {
        "solver": "scipy.optimize.milp highs",
        "solver_status": int(result.status),
        "solver_message": str(result.message),
        "elapsed_seconds": round(elapsed, 6),
        "proof_certificate_supplied": False,
        "claim_label": "UNKNOWN",
    }
    if result.x is not None:
        rounded = np.rint(result.x)
        if (
            np.max(np.abs(result.x - rounded), initial=0.0) <= 1e-7
            and np.max(
                np.abs(system.matrix @ rounded - np.asarray(system.rhs)),
                initial=0.0,
            ) <= 1e-7
        ):
            witness = [
                (index, Fraction(int(value)))
                for index, value in enumerate(rounded)
                if value
            ]
            replay = replay_fraction_witness(
                candidates, gram, witness, True
            )
            output.update({
                "claim_label": "CANDIDATE",
                "exact_witness": encode_witness(witness),
                "exact_replay": replay,
            })
    if output["claim_label"] == "UNKNOWN":
        output["interpretation"] = (
            "bounded solver nonhit/non-certifying status; no nonexistence "
            "evidence"
        )
    return output


def independently_validate_imported_counts(types: Sequence[dict]) -> dict:
    triples = list(itertools.combinations_with_replacement(range(18), 3))
    count_histogram: dict[int, int] = {}
    minimum_records = []
    maximum_records = []
    minimum = None
    maximum = None
    records = []
    for triple_index, triple in enumerate(triples):
        count = candidate_count([types[index] for index in triple])
        count_histogram[count] = count_histogram.get(count, 0) + 1
        records.append((triple_index, triple, count))
        if minimum is None or count < minimum:
            minimum = count
            minimum_records = [(triple_index, triple)]
        elif count == minimum:
            minimum_records.append((triple_index, triple))
        if maximum is None or count > maximum:
            maximum = count
            maximum_records = [(triple_index, triple)]
        elif count == maximum:
            maximum_records.append((triple_index, triple))
    upstream60 = json.loads(WAVE60_RESULTS.read_text(encoding="utf-8"))
    upstream61 = json.loads(WAVE61_RESULTS.read_text(encoding="utf-8"))
    imported_minimum = upstream60["individual_column_support"]["minimum_over_triples"]
    imported_maximum = upstream60["individual_column_support"]["maximum_over_triples"]
    imported_records = upstream61["triple_census"]["records"]
    imported_counts = [
        record["pair_inventory_F2"][
            "candidate_count_before_exact_multiplicities"
        ]
        for record in imported_records
    ]
    if len(imported_counts) != 1140:
        raise AssertionError("Wave 61 does not contain 1,140 records")
    if [count for _, _, count in records] != imported_counts:
        raise AssertionError("independent candidate counts disagree with Wave 61")
    if minimum != imported_minimum or maximum != imported_maximum:
        raise AssertionError("independent extrema disagree with Wave 60")
    return {
        "triple_count": len(triples),
        "minimum": minimum,
        "maximum": maximum,
        "minimum_records": [
            {"triple_index": index, "type_triple": list(triple)}
            for index, triple in minimum_records
        ],
        "maximum_records": [
            {"triple_index": index, "type_triple": list(triple)}
            for index, triple in maximum_records
        ],
        "count_histogram": {
            str(key): count_histogram[key] for key in sorted(count_histogram)
        },
        "agrees_exactly_with_wave61_all_1140": True,
        "agrees_with_wave60_extrema": True,
    }


def select_principled_lanes(types: Sequence[dict], validation: dict) -> list[dict]:
    """Choose fixed falsifiable lanes without using target automorphisms.

    Include every minimum-support triple, every diagonal triple (t,t,t), both
    support extrema, and one first triple for each Wave 61 full-pair F2 rank.
    """
    wave61 = json.loads(WAVE61_RESULTS.read_text(encoding="utf-8"))
    selected: dict[int, dict] = {}
    reasons: dict[int, set[str]] = {}

    def add(index: int, reason: str) -> None:
        record = wave61["triple_census"]["records"][index]
        selected[index] = record
        reasons.setdefault(index, set()).add(reason)

    for record in validation["minimum_records"]:
        add(record["triple_index"], "global minimum candidate support")
    for record in validation["maximum_records"]:
        add(record["triple_index"], "global maximum candidate support")
    for record in wave61["triple_census"]["records"]:
        triple = record["type_triple"]
        if triple[0] == triple[1] == triple[2]:
            add(record["triple_index"], "diagonal component triple")
    seen_rank = set()
    for record in wave61["triple_census"]["records"]:
        rank = record["pair_inventory_F2"]["full_630_rank"]
        if rank not in seen_rank:
            add(record["triple_index"], f"first full-pair F2 rank {rank}")
            seen_rank.add(rank)
    output = []
    for index in sorted(selected):
        record = selected[index]
        output.append({
            "triple_index": index,
            "type_triple": record["type_triple"],
            "candidate_count": record["pair_inventory_F2"][
                "candidate_count_before_exact_multiplicities"
            ],
            "full_pair_F2_rank": record["pair_inventory_F2"]["full_630_rank"],
            "selection_reasons": sorted(reasons[index]),
        })
    return output


def canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode("utf-8")


def run(
    output_path: Path,
    lane_limit: int | None,
    lp_time_limit: float,
    milp_time_limit: float,
    milp_lane_count: int,
) -> dict:
    check_frozen_inputs()
    start_memory = require_memory()
    types = load_types()
    validation = independently_validate_imported_counts(types)
    lanes = select_principled_lanes(types, validation)
    if lane_limit is not None:
        lanes = lanes[:lane_limit]
    results = []
    for lane_number, lane in enumerate(lanes):
        require_memory()
        triple = tuple(lane["type_triple"])
        records = [types[index] for index in triple]
        gram = target_gram(records)
        candidates = candidate_columns(records)
        if len(candidates) != lane["candidate_count"]:
            raise AssertionError("lane candidate count changed")
        system = pair_system(candidates, gram)
        cone = solve_rational_cone(
            system, candidates, gram, lp_time_limit
        )
        result = {
            **lane,
            "active_positive_pair_equations": len(system.active_pairs),
            "all_pair_equations": 630,
            "rational_cone": cone,
        }
        if lane_number < milp_lane_count and cone["claim_label"] == "DERIVED":
            result["distinct_column_milp"] = solve_distinct_milp(
                system, candidates, gram, milp_time_limit
            )
        else:
            result["distinct_column_milp"] = {
                "claim_label": "UNKNOWN",
                "status": "NOT_RUN",
                "reason": (
                    "outside the fixed bounded MILP subset or no exact "
                    "rational-cone witness"
                ),
            }
        results.append(result)
    finish_memory = require_memory()
    exact_cone = sum(
        result["rational_cone"]["claim_label"] == "DERIVED"
        for result in results
    )
    candidate_designs = sum(
        result["distinct_column_milp"]["claim_label"] == "CANDIDATE"
        for result in results
    )
    output = {
        "schema_version": 1,
        "claim_label": "DERIVED" if exact_cone else "UNKNOWN",
        "scope": (
            "conditional prism-free endpoint kappa=3; exact rational-cone "
            "screens on a fixed principled subset and bounded "
            "distinct-column MILP probes"
        ),
        "input_validation": validation,
        "lane_selection": {
            "rule": (
                "all global minimum/maximum-support triples, all 18 diagonal "
                "triples, and the first triple in each Wave 61 full-pair F2 "
                "rank stratum; overlaps removed; no target automorphism used"
            ),
            "available_lane_count": len(select_principled_lanes(types, validation)),
            "executed_lane_count": len(results),
            "lane_limit": lane_limit,
        },
        "results": results,
        "summary": {
            "exact_rational_cone_witnesses": exact_cone,
            "numerical_or_unknown_cone_lanes": len(results) - exact_cone,
            "exact_distinct_column_candidates": candidate_designs,
            "distinct_column_lanes_without_candidate":
                len(results) - candidate_designs,
            "endpoint_status": "UNKNOWN",
            "conway_99_status": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "resource_guard": {
            "minimum_free_physical_memory_percent": MEMORY_FLOOR_PERCENT,
            "start_free_physical_memory_percent": round(start_memory, 2),
            "finish_free_physical_memory_percent": round(finish_memory, 2),
            "parallel_solver_processes": 1,
        },
        "limitations": [
            "Discovery cannot verify itself.",
            "The principled subset is not all 275 safe coordinate orbits and "
            "not all 1,140 unordered triples.",
            "No target-graph automorphism is assumed.",
            "Floating LP outcomes without an exact replayed rational witness "
            "remain UNKNOWN.",
            "No infeasibility is claimed without an exact Farkas certificate.",
            "Bounded MILP nonhits remain UNKNOWN.",
            "A rational cone witness does not imply an integer distinct-column "
            "incidence design.",
            "A candidate incidence design would still require independent "
            "verification and compatibility with the remaining graph.",
        ],
    }
    output_path.write_bytes(canonical_bytes(output))
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=PACKAGE / "exact-results.json",
    )
    parser.add_argument("--lane-limit", type=int)
    parser.add_argument("--lp-time-limit", type=float, default=60.0)
    parser.add_argument("--milp-time-limit", type=float, default=30.0)
    parser.add_argument("--milp-lane-count", type=int, default=1)
    arguments = parser.parse_args()
    result = run(
        arguments.output,
        arguments.lane_limit,
        arguments.lp_time_limit,
        arguments.milp_time_limit,
        arguments.milp_lane_count,
    )
    print(json.dumps(result["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
