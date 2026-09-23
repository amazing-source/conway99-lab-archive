#!/usr/bin/env python3
"""Exact bounded rational column-polytope census for Wave153."""

from __future__ import annotations

import argparse
import ctypes
import gzip
import hashlib
import itertools
import json
import math
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Sequence

import numpy as np
from flint import fmpq_mat
from scipy.linalg import qr
from scipy.optimize import linprog
from scipy.sparse import csc_matrix


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
COMPONENTS = (
    ROOT / "attempts" / "wave60-c3-incidence-design"
    / "component-census.json"
)
INVARIANTS = (
    ROOT / "attempts" / "wave60-c3-incidence-design"
    / "invariant-results.json"
)
WAVE63 = ROOT / "attempts" / "wave63-c3-integer-cone" / "exact-results.json"
INPUT_FREEZE = HERE / "input-freeze.sha256"
MEMORY_FLOOR_PERCENT = 20.0
PAIR12 = tuple(itertools.combinations(range(12), 2))
PAIR36 = tuple(itertools.combinations(range(36), 2))
PAIR36_INDEX = {pair: index for index, pair in enumerate(PAIR36)}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode(
        "ascii"
    )


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_gzip(path: Path, value: object) -> None:
    raw = canonical_bytes(value)
    path.write_bytes(gzip.compress(raw, compresslevel=9, mtime=0))


def read_gzip(path: Path) -> dict:
    raw = gzip.decompress(path.read_bytes())
    value = json.loads(raw.decode("ascii"))
    require(canonical_bytes(value) == raw, f"noncanonical gzip JSON: {path}")
    return value


def verify_input_freeze() -> dict:
    failures = []
    rows = []
    for line in INPUT_FREEZE.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, relative = line.split(maxsplit=1)
        path = (ROOT / relative).resolve()
        path.relative_to(ROOT.resolve())
        actual = sha256(path)
        rows.append(
            {
                "path": relative,
                "expected_sha256": expected,
                "actual_sha256": actual,
                "pass": actual == expected,
            }
        )
        if actual != expected:
            failures.append(relative)
    require(not failures, f"input freeze failures: {failures}")
    return {
        "entry_count": len(rows),
        "all_entries_pass": True,
        "input_freeze_sha256": sha256(INPUT_FREEZE),
    }


def free_memory_percent() -> float:
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

    status = MemoryStatusEx()
    status.dwLength = ctypes.sizeof(status)
    require(
        bool(ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status))),
        "GlobalMemoryStatusEx failed",
    )
    return 100.0 * status.ullAvailPhys / status.ullTotalPhys


def require_memory() -> float:
    free = free_memory_percent()
    require(
        free >= MEMORY_FLOOR_PERCENT,
        f"free memory {free:.2f}% below {MEMORY_FLOOR_PERCENT:.2f}% floor",
    )
    return free


def global_vertex(component: int, local_vertex: int) -> int:
    fibre, local_index = divmod(local_vertex, 4)
    return fibre * 12 + component * 4 + local_index


def component_rows(record: dict) -> tuple[int, ...]:
    rows = [0] * 12
    for left, right in record["edges"]:
        require(0 <= left < right < 12, "bad component edge")
        require(not (rows[left] >> right) & 1, "duplicate component edge")
        rows[left] |= 1 << right
        rows[right] |= 1 << left
    require({row.bit_count() for row in rows} == {3}, "component degree")
    require(
        all(
            sum(bool(rows[vertex] & (1 << other)) for other in range(4 * fibre, 4 * fibre + 4))
            == 1
            for fibre in range(3)
            for vertex in range(4 * fibre, 4 * fibre + 4)
        ),
        "fibre matching",
    )
    return tuple(rows)


def load_inputs() -> tuple[list[dict], list[dict], set[int], dict]:
    freeze = verify_input_freeze()
    component_payload = read_json(COMPONENTS)
    types = component_payload["component_census"]["types"]
    require(len(types) == 18, "component type count")
    for index, record in enumerate(types):
        require(record["type_index"] == index, "component type order")
        component_rows(record)

    invariant_payload = read_json(INVARIANTS)
    representatives = invariant_payload[
        "safe_triple_orbit_reduction"
    ]["representatives"]
    require(len(representatives) == 275, "safe orbit count")
    survivor_by_index = {
        row["triple_index"]: row
        for row in invariant_payload["survivors"]
    }
    require(len(survivor_by_index) == 1140, "survivor index")
    prior = read_json(WAVE63)
    prior_indices = {row["triple_index"] for row in prior["results"]}
    require(len(prior_indices) == 74, "Wave63 prior lane count")
    return types, representatives, prior_indices, {
        "freeze": freeze,
        "survivor_by_index": survivor_by_index,
    }


def union_rows(records: Sequence[dict]) -> tuple[int, ...]:
    rows = [0] * 36
    for component, record in enumerate(records):
        local = component_rows(record)
        for left in range(12):
            for right in range(left + 1, 12):
                if (local[left] >> right) & 1:
                    global_left = global_vertex(component, left)
                    global_right = global_vertex(component, right)
                    rows[global_left] |= 1 << global_right
                    rows[global_right] |= 1 << global_left
    require({row.bit_count() for row in rows} == {3}, "union degree")
    return tuple(rows)


def target_gram(records: Sequence[dict]) -> tuple[tuple[int, ...], ...]:
    adjacency = union_rows(records)
    matrix = []
    for left in range(36):
        row = []
        for right in range(36):
            value = (
                (12 if left == right else 0)
                - int(bool((adjacency[left] >> right) & 1))
                + 2
                - int(left // 12 == right // 12)
                - (adjacency[left] & adjacency[right]).bit_count()
            )
            require(value >= 0, "negative Gram target")
            row.append(value)
        matrix.append(tuple(row))
    require(
        [matrix[index][index] for index in range(36)] == [10] * 36,
        "Gram diagonal",
    )
    return tuple(matrix)


def pair_profile(pair: tuple[int, int]) -> tuple[int, int, int]:
    value = [0, 0, 0]
    value[pair[0] // 4] += 1
    value[pair[1] // 4] += 1
    return tuple(value)


PROFILE_VALUES = tuple(sorted({pair_profile(pair) for pair in PAIR12}))
PROFILE_TRIPLES = tuple(
    profiles
    for profiles in itertools.product(range(len(PROFILE_VALUES)), repeat=3)
    if tuple(
        sum(PROFILE_VALUES[profiles[component]][fibre] for component in range(3))
        for fibre in range(3)
    )
    == (2, 2, 2)
)
require(len(PROFILE_TRIPLES) == 21, "profile count")


def local_gram(record: dict) -> tuple[tuple[int, ...], ...]:
    adjacency = component_rows(record)
    matrix = []
    for left in range(12):
        row = []
        for right in range(12):
            value = (
                (12 if left == right else 0)
                - int(bool((adjacency[left] >> right) & 1))
                + 2
                - int(left // 4 == right // 4)
                - (adjacency[left] & adjacency[right]).bit_count()
            )
            require(value >= 0, "negative local Gram target")
            row.append(value)
        matrix.append(tuple(row))
    return tuple(matrix)


def allowed_pairs(record: dict) -> tuple[tuple[int, ...], ...]:
    gram = local_gram(record)
    groups = [[] for _ in PROFILE_VALUES]
    for index, pair in enumerate(PAIR12):
        if gram[pair[0]][pair[1]] > 0:
            groups[PROFILE_VALUES.index(pair_profile(pair))].append(index)
    return tuple(tuple(group) for group in groups)


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
            vertices = tuple(
                sorted(
                    global_vertex(component, vertex)
                    for component, pair_index in enumerate(pair_indices)
                    for vertex in PAIR12[pair_index]
                )
            )
            require(
                len(vertices) == 6 and len(set(vertices)) == 6,
                "candidate distinctness",
            )
            require(
                tuple(
                    sum(vertex // 12 == fibre for vertex in vertices)
                    for fibre in range(3)
                )
                == (2, 2, 2),
                "candidate fibre profile",
            )
            require(vertices not in seen, "duplicate candidate")
            seen.add(vertices)
            candidates.append(vertices)
    return candidates


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
        pair for pair in PAIR36 if gram[pair[0]][pair[1]] > 0
    )
    index = {pair: row for row, pair in enumerate(active_pairs)}
    row_indices = []
    column_indices = []
    for column, candidate in enumerate(candidates):
        for pair in itertools.combinations(candidate, 2):
            require(pair in index, "candidate uses zero-target pair")
            row_indices.append(index[pair])
            column_indices.append(column)
    matrix = csc_matrix(
        (
            np.ones(len(row_indices), dtype=np.float64),
            (row_indices, column_indices),
        ),
        shape=(len(active_pairs), len(candidates)),
    )
    require(set(np.diff(matrix.indptr)) == {15}, "candidate column weight")
    return PairSystem(
        active_pairs,
        tuple(gram[left][right] for left, right in active_pairs),
        matrix,
    )


def replay_witness(
    candidates: Sequence[tuple[int, ...]],
    gram: Sequence[Sequence[int]],
    witness: Sequence[tuple[int, Fraction]],
) -> dict:
    totals = [Fraction(0) for _ in PAIR36]
    row_totals = [Fraction(0) for _ in range(36)]
    total_weight = Fraction(0)
    seen = set()
    for index, coefficient in witness:
        require(index not in seen, "duplicate witness candidate")
        seen.add(index)
        require(0 <= index < len(candidates), "candidate index")
        require(0 < coefficient <= 1, "coefficient outside (0,1]")
        total_weight += coefficient
        for vertex in candidates[index]:
            row_totals[vertex] += coefficient
        for pair in itertools.combinations(candidates[index], 2):
            totals[PAIR36_INDEX[pair]] += coefficient
    expected = [
        Fraction(gram[left][right]) for left, right in PAIR36
    ]
    require(totals == expected, "pair equation mismatch")
    require(row_totals == [Fraction(10)] * 36, "row margin mismatch")
    require(total_weight == 60, "total weight mismatch")
    return {
        "support": len(witness),
        "total_weight": "60",
        "maximum_denominator": max(
            coefficient.denominator for _, coefficient in witness
        ),
        "maximum_coefficient": str(
            max(coefficient for _, coefficient in witness)
        ),
        "all_630_pair_equations_exact": True,
        "all_36_row_margins_exact": True,
        "all_coefficients_in_0_1": True,
    }


def exactify(
    values: np.ndarray,
    system: PairSystem,
    candidates: Sequence[tuple[int, ...]],
    gram: Sequence[Sequence[int]],
    threshold: float = 1e-8,
) -> tuple[list[tuple[int, Fraction]], dict] | None:
    ones = [
        index for index, value in enumerate(values)
        if value >= 1.0 - threshold
    ]
    fractional = [
        index for index, value in enumerate(values)
        if threshold < value < 1.0 - threshold
    ]
    base_rhs = np.asarray(system.rhs, dtype=np.int64)
    if ones:
        base_rhs = base_rhs - np.asarray(
            system.matrix[:, ones].sum(axis=1)
        ).reshape(-1).astype(np.int64)
    require(np.all(base_rhs >= 0), "upper-bound base overshoots target")
    if not fractional:
        witness = [(index, Fraction(1)) for index in ones]
        try:
            replay = replay_witness(candidates, gram, witness)
        except AssertionError:
            return None
        replay["exactification_method"] = "integral bound-active solution"
        return witness, replay
    if len(fractional) > len(system.active_pairs):
        return None
    dense = system.matrix[:, fractional].toarray().astype(np.int64)
    _, triangular, row_pivots = qr(
        dense.T.astype(np.float64),
        mode="economic",
        pivoting=True,
        check_finite=False,
    )
    diagonal = np.abs(np.diag(triangular))
    if (
        len(diagonal) < len(fractional)
        or np.count_nonzero(diagonal > 1e-9) < len(fractional)
    ):
        return None
    selected_rows = [
        int(value) for value in row_pivots[: len(fractional)]
    ]
    exact_matrix = fmpq_mat(
        len(fractional),
        len(fractional),
        dense[selected_rows, :].reshape(-1).tolist(),
    )
    exact_rhs = fmpq_mat(
        len(fractional),
        1,
        [int(base_rhs[row]) for row in selected_rows],
    )
    try:
        solution = exact_matrix.solve(exact_rhs, algorithm="dixon")
    except ZeroDivisionError:
        return None
    witness = [(index, Fraction(1)) for index in ones]
    witness.extend(
        (
            candidate_index,
            Fraction(
                int(solution[position, 0].p),
                int(solution[position, 0].q),
            ),
        )
        for position, candidate_index in enumerate(fractional)
        if solution[position, 0]
    )
    witness.sort()
    try:
        replay = replay_witness(candidates, gram, witness)
    except AssertionError:
        return None
    replay["exactification_method"] = (
        "bound-active columns fixed exactly, then FLINT fmpq Dixon solve on "
        "a QR-selected square row minor and full rational replay"
    )
    replay["fixed_one_coordinates"] = len(ones)
    replay["square_minor_order"] = len(fractional)
    return witness, replay


def encode_witness(
    witness: Sequence[tuple[int, Fraction]]
) -> list[list[object]]:
    return [
        [index, str(coefficient)]
        for index, coefficient in witness
    ]


def solve_lane(
    orbit_position: int,
    orbit: dict,
    types: Sequence[dict],
    prior_indices: set[int],
    survivor_by_index: dict[int, dict],
) -> dict:
    require_memory()
    triple_index = int(orbit["triple_indices"][0])
    triple = tuple(int(value) for value in orbit["type_triple"])
    records = [types[index] for index in triple]
    gram = target_gram(records)
    candidates = candidate_columns(records)
    expected_count = survivor_by_index[triple_index][
        "available_distinct_column_count"
    ]
    require(len(candidates) == expected_count, "candidate count drift")
    system = pair_system(candidates, gram)
    result = linprog(
        np.zeros(len(candidates)),
        A_eq=system.matrix,
        b_eq=np.asarray(system.rhs, dtype=np.float64),
        bounds=(0.0, 1.0),
        method="highs-ds",
        options={"presolve": True, "time_limit": 60.0},
    )
    output = {
        "orbit_position": orbit_position,
        "representative_triple_index": triple_index,
        "type_triple": list(triple),
        "orbit_size": int(orbit["orbit_size"]),
        "candidate_count": len(candidates),
        "active_pair_equations": len(system.active_pairs),
        "previously_tested_exact_triple": triple_index in prior_indices,
        "claim_label": "UNKNOWN",
    }
    if result.x is None:
        output["solver_status"] = int(result.status)
        output["solver_message"] = str(result.message)
        output["limitation"] = (
            "floating non-success without an exact Farkas certificate"
        )
        return output
    residual = system.matrix @ result.x - np.asarray(system.rhs)
    output["floating_max_abs_residual"] = float(
        np.max(np.abs(residual), initial=0.0)
    )
    exact = exactify(result.x, system, candidates, gram)
    if exact is None:
        output["limitation"] = "floating point could not be exactified"
        return output
    witness, replay = exact
    output.update(
        {
            "claim_label": "CANDIDATE",
            "exact_witness": encode_witness(witness),
            "exact_replay": replay,
        }
    )
    return output


def run_batch(start: int, stop: int, output: Path) -> None:
    types, representatives, prior_indices, context = load_inputs()
    require(0 <= start < stop <= len(representatives), "batch range")
    results = []
    for position in range(start, stop):
        result = solve_lane(
            position,
            representatives[position],
            types,
            prior_indices,
            context["survivor_by_index"],
        )
        results.append(result)
        print(
            f"orbit {position:03d}: {result['claim_label']} "
            f"support={result.get('exact_replay', {}).get('support', '-')}",
            flush=True,
        )
    payload = {
        "format": "wave153-triangle-root-correlation-batch-v1",
        "claim_label": (
            "CANDIDATE"
            if all(row["claim_label"] == "CANDIDATE" for row in results)
            else "UNKNOWN"
        ),
        "range": [start, stop],
        "results": results,
    }
    write_gzip(output, payload)
    print(f"wrote {output}")


def decode_witness(rows: Sequence[Sequence[object]]) -> list[tuple[int, Fraction]]:
    witness = []
    for row in rows:
        require(
            isinstance(row, list)
            and len(row) == 2
            and type(row[0]) is int
            and type(row[1]) is str,
            "encoded witness row",
        )
        value = Fraction(row[1])
        require(str(value) == row[1], "noncanonical rational")
        witness.append((row[0], value))
    return witness


def merge_batches(inputs: Sequence[Path], output: Path) -> None:
    types, representatives, prior_indices, context = load_inputs()
    rows = []
    for path in inputs:
        payload = read_gzip(path)
        require(
            payload["format"] == "wave153-triangle-root-correlation-batch-v1",
            "batch format",
        )
        rows.extend(payload["results"])
    rows.sort(key=lambda row: row["orbit_position"])
    require(
        [row["orbit_position"] for row in rows] == list(range(275)),
        "batch coverage is not exactly 0..274",
    )
    denominator_maximum = 1
    support_minimum = math.inf
    support_maximum = 0
    coefficient_maximum = Fraction(0)
    new_representatives = 0
    transferred_triples = set()
    for row, orbit in zip(rows, representatives):
        require(row["claim_label"] == "CANDIDATE", "unexact lane")
        require(
            row["representative_triple_index"] == orbit["triple_indices"][0]
            and row["type_triple"] == orbit["type_triple"],
            "orbit identity mismatch",
        )
        records = [types[index] for index in row["type_triple"]]
        gram = target_gram(records)
        candidates = candidate_columns(records)
        require(
            len(candidates) == row["candidate_count"],
            "merge candidate count",
        )
        witness = decode_witness(row["exact_witness"])
        replay = replay_witness(candidates, gram, witness)
        require(
            replay["support"] == row["exact_replay"]["support"],
            "merge support replay",
        )
        denominator_maximum = max(
            denominator_maximum, replay["maximum_denominator"]
        )
        support_minimum = min(support_minimum, replay["support"])
        support_maximum = max(support_maximum, replay["support"])
        coefficient_maximum = max(
            coefficient_maximum,
            max(value for _, value in witness),
        )
        if row["representative_triple_index"] not in prior_indices:
            new_representatives += 1
        transferred_triples.update(orbit["triple_indices"])
    require(len(transferred_triples) == 1140, "orbit transfer coverage")
    payload = {
        "format": "wave153-triangle-root-correlation-polytope-v1",
        "claim_label": "CANDIDATE",
        "scope": (
            "conditional prism-free endpoint kappa=3; exact bounded rational "
            "pair-column polytope on every safe component-triple orbit"
        ),
        "inputs": {
            "input_freeze_sha256": sha256(INPUT_FREEZE),
            "component_census_sha256": sha256(COMPONENTS),
            "invariant_results_sha256": sha256(INVARIANTS),
            "prior_wave63_sha256": sha256(WAVE63),
        },
        "coverage": {
            "component_types": 18,
            "unordered_type_triples": 1140,
            "safe_coordinate_orbits": 275,
            "representatives_with_exact_witnesses": 275,
            "representatives_not_previously_tested_as_the_exact_triple": (
                new_representatives
            ),
            "all_1140_transferred_by_frozen_coordinate_action": True,
        },
        "polytope": {
            "equations_per_lane": 630,
            "row_margins_checked_per_lane": 36,
            "coefficient_bounds": ["0", "1"],
            "candidate_count_range": [
                min(row["candidate_count"] for row in rows),
                max(row["candidate_count"] for row in rows),
            ],
            "witness_support_range": [
                int(support_minimum),
                support_maximum,
            ],
            "maximum_denominator": denominator_maximum,
            "maximum_coefficient": str(coefficient_maximum),
            "all_pair_equations_exact": True,
            "all_row_margins_exact": True,
            "all_coefficients_in_0_1": True,
        },
        "results": rows,
        "result": {
            "disposition": (
                "EXACT_NULL_WITNESS_FOR_COMPLETE_SAFE_ORBIT_RATIONAL_PROJECTION"
            ),
            "binary_incidence_design": "UNKNOWN",
            "compatible_residual_graph": "UNKNOWN",
            "endpoint_n3_4158": "UNKNOWN",
            "strict_n3_upper_bound": "NOT_OBTAINED",
            "Conway_99": "UNKNOWN",
            "external_novelty": "UNKNOWN",
        },
        "limitations": [
            "Discovery cannot verify itself.",
            "Rational coefficients in [0,1] need not be binary.",
            "Pair-coordinate feasibility does not impose a common integral three-way coupling.",
            "A binary incidence design would still not construct the compatible 60-vertex residual graph.",
            "No endpoint existence, exclusion, strict bound, Conway-99 resolution, or novelty claim follows.",
        ],
    }
    write_gzip(output, payload)
    raw = gzip.decompress(output.read_bytes())
    print(
        json.dumps(
            {
                "output": str(output),
                "gzip_bytes": output.stat().st_size,
                "gzip_sha256": sha256(output),
                "canonical_bytes": len(raw),
                "canonical_sha256": hashlib.sha256(raw).hexdigest(),
                "representatives": len(rows),
                "transferred_triples": len(transferred_triples),
                "maximum_denominator": denominator_maximum,
            },
            sort_keys=True,
        )
    )


def verify_final(path: Path) -> None:
    payload = read_gzip(path)
    require(
        payload["format"]
        == "wave153-triangle-root-correlation-polytope-v1",
        "final format",
    )
    types, representatives, _, _ = load_inputs()
    require(len(payload["results"]) == len(representatives) == 275, "final rows")
    for position, (row, orbit) in enumerate(
        zip(payload["results"], representatives)
    ):
        require(
            type(row["orbit_position"]) is int
            and row["orbit_position"] == position,
            "final orbit position",
        )
        require(row["type_triple"] == orbit["type_triple"], "final orbit type")
        records = [types[index] for index in row["type_triple"]]
        gram = target_gram(records)
        candidates = candidate_columns(records)
        replay_witness(
            candidates, gram, decode_witness(row["exact_witness"])
        )
    print("Wave153 final exact replay: PASS_WITH_SCOPE")


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    batch = subparsers.add_parser("batch")
    batch.add_argument("--start", type=int, required=True)
    batch.add_argument("--stop", type=int, required=True)
    batch.add_argument("--output", type=Path, required=True)
    merge = subparsers.add_parser("merge")
    merge.add_argument("--inputs", type=Path, nargs="+", required=True)
    merge.add_argument("--output", type=Path, required=True)
    verify = subparsers.add_parser("verify")
    verify.add_argument("path", type=Path)
    arguments = parser.parse_args()
    if arguments.command == "batch":
        run_batch(arguments.start, arguments.stop, arguments.output)
    elif arguments.command == "merge":
        merge_batches(arguments.inputs, arguments.output)
    else:
        verify_final(arguments.path)


if __name__ == "__main__":
    main()
