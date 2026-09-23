#!/usr/bin/env python3
"""Exact rooted-pair flag relaxation at the prism-free endpoint.

The Wave 43 unrooted endpoint system has one variable for each of 208
locally admissible seven-vertex graph types, plus y=h11/4.  This file adds
the smallest overlap equations obtained by distinguishing an ordered pair of
root vertices.

For an adjacent ordered pair in an srg(99,14,1,2), the 97 other vertices
split by adjacency to the roots as

    common, first-only, second-only, neither = 1,12,12,72.

For a nonadjacent ordered pair the split is 2,12,12,71.  Choosing five
vertices from these categories gives exact rooted seven-vertex flag counts.
There are 36 adjacent and 46 nonadjacent signatures.

The code checks exact row-rank increments, evaluates the frozen unrooted
witness against every new row, and can search the augmented integer
relaxation.  A feasible vector is only a necessary-count positive control;
a negative solver status is not a proof.
"""

from __future__ import annotations

import argparse
import functools
import hashlib
import importlib.util
import itertools
import json
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import coo_array


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
ENDPOINT_PATH = ROOT / "attempts/wave43-seven-deck-endpoint/endpoint_deck.py"
ENDPOINT_RESULT = (
    ROOT / "attempts/wave43-seven-deck-endpoint/exact-results.json"
)
ROOTED_WITNESS = HERE / "rooted-witness.json"
ROW_SYSTEM = HERE / "row-system.json"
N = 99
K = 14
LAMBDA = 1
MU = 2
N3 = 4158


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, indent=2, separators=(",", ": "))
        + "\n"
    ).encode("utf-8")


def compact_json(value: object) -> bytes:
    """Canonical bytes used for all row/RHS SHA-256 commitments."""

    return json.dumps(
        value, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def load_module(name: str, path: Path) -> Any:
    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


def edge_index(left: int, right: int, order: int = 7) -> int:
    require(0 <= left < right < order, "bad edge")
    return sum(order - 1 - first for first in range(left)) + right - left - 1


def adjacent(mask: int, left: int, right: int) -> bool:
    if left > right:
        left, right = right, left
    return bool(mask >> edge_index(left, right) & 1)


def pair_signature(mask: int, first: int, second: int) -> tuple[int, int, int, int]:
    """Counts common, first-only, second-only, neither among five vertices."""

    counts = [0, 0, 0, 0]
    for vertex in range(7):
        if vertex in (first, second):
            continue
        to_first = adjacent(mask, vertex, first)
        to_second = adjacent(mask, vertex, second)
        if to_first and to_second:
            counts[0] += 1
        elif to_first:
            counts[1] += 1
        elif to_second:
            counts[2] += 1
        else:
            counts[3] += 1
    require(sum(counts) == 5, "pair signature lost a vertex")
    return tuple(counts)


def weak_compositions(total: int, parts: int) -> Iterable[tuple[int, ...]]:
    if parts == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for tail in weak_compositions(total - first, parts - 1):
            yield (first, *tail)


def signature_universe(common_neighbors: int) -> tuple[tuple[int, int, int, int], ...]:
    return tuple(
        value
        for value in weak_compositions(5, 4)
        if value[0] <= common_neighbors
    )


def rooted_rows(
    classes: Sequence[int],
    relation: str,
) -> tuple[
    tuple[tuple[int, int, int, int], ...],
    tuple[tuple[int, ...], ...],
    tuple[int, ...],
]:
    if relation == "edge":
        universe = signature_universe(LAMBDA)
        category_sizes = (LAMBDA, K - 1 - LAMBDA, K - 1 - LAMBDA, 72)
        ordered_roots = N * K
        root_relation = True
    elif relation == "nonedge":
        universe = signature_universe(MU)
        category_sizes = (MU, K - MU, K - MU, 71)
        ordered_roots = N * (N - 1 - K)
        root_relation = False
    else:
        raise ValueError("unknown rooted relation")

    index = {signature: position for position, signature in enumerate(universe)}
    rows = [[0] * len(classes) for _ in universe]
    for column, mask in enumerate(classes):
        for first in range(7):
            for second in range(7):
                if first == second or adjacent(mask, first, second) != root_relation:
                    continue
                signature = pair_signature(mask, first, second)
                require(signature in index, "local common-neighbor cap failed")
                rows[index[signature]][column] += 1

    rhs = tuple(
        ordered_roots
        * math.prod(
            math.comb(category_size, selected)
            for category_size, selected in zip(category_sizes, signature)
        )
        for signature in universe
    )
    return universe, tuple(tuple(row) for row in rows), rhs


def vertex_rows(
    classes: Sequence[int],
) -> tuple[tuple[int, ...], tuple[tuple[int, ...], ...], tuple[int, ...]]:
    universe = tuple(range(7))
    rows = [[0] * len(classes) for _ in universe]
    for column, mask in enumerate(classes):
        for root in range(7):
            degree = sum(
                adjacent(mask, root, other)
                for other in range(7)
                if other != root
            )
            rows[degree][column] += 1
    rhs = tuple(
        N * math.comb(K, degree) * math.comb(N - 1 - K, 6 - degree)
        for degree in universe
    )
    return universe, tuple(tuple(row) for row in rows), rhs


def rank_mod_prime(matrix: Sequence[Sequence[int]], prime: int) -> int:
    if not matrix:
        return 0
    work = [[value % prime for value in row] for row in matrix]
    row = 0
    for column in range(len(work[0])):
        pivot = next(
            (candidate for candidate in range(row, len(work)) if work[candidate][column]),
            None,
        )
        if pivot is None:
            continue
        work[row], work[pivot] = work[pivot], work[row]
        inverse = pow(work[row][column], -1, prime)
        work[row] = [value * inverse % prime for value in work[row]]
        for other in range(len(work)):
            if other == row or not work[other][column]:
                continue
            factor = work[other][column]
            work[other] = [
                (value - factor * pivot_value) % prime
                for value, pivot_value in zip(work[other], work[row])
            ]
        row += 1
        if row == len(work):
            break
    return row


@functools.lru_cache(maxsize=1)
def endpoint_system() -> dict[str, Any]:
    endpoint = load_module("wave44_endpoint_frozen", ENDPOINT_PATH)
    base = endpoint.build_endpoint_model()
    classes = tuple(base["classes"])
    variable_count = len(classes) + 1

    base_rows: list[tuple[int, ...]] = []
    base_rhs: list[int] = []
    for row, target in zip(base["matrix_rows"], base["deck_rhs"]):
        base_rows.append(tuple(row) + (0,))
        base_rhs.append(int(target))
    for equation in base["h_equations"]:
        row = [0] * variable_count
        row[equation["class_index"]] = 1
        row[-1] = -equation["y_coefficient"]
        base_rows.append(tuple(row))
        base_rhs.append(equation["constant"])

    vertex_universe, vertex_coefficients, vertex_rhs = vertex_rows(classes)
    edge_universe, edge_coefficients, edge_rhs = rooted_rows(classes, "edge")
    nonedge_universe, nonedge_coefficients, nonedge_rhs = rooted_rows(
        classes, "nonedge"
    )

    def extend(rows: Sequence[Sequence[int]]) -> tuple[tuple[int, ...], ...]:
        return tuple(tuple(row) + (0,) for row in rows)

    return {
        "endpoint": endpoint,
        "classes": classes,
        "base_rows": tuple(base_rows),
        "base_rhs": tuple(base_rhs),
        "vertex_universe": vertex_universe,
        "vertex_rows": extend(vertex_coefficients),
        "vertex_rhs": vertex_rhs,
        "edge_universe": edge_universe,
        "edge_rows": extend(edge_coefficients),
        "edge_rhs": edge_rhs,
        "nonedge_universe": nonedge_universe,
        "nonedge_rows": extend(nonedge_coefficients),
        "nonedge_rhs": nonedge_rhs,
    }


def row_rhs_payload(system: dict[str, Any]) -> dict[str, dict[str, object]]:
    """Return the four ordered equation families in their committed form."""

    return {
        family: {
            "rows": system[f"{family}_rows"],
            "rhs": system[f"{family}_rhs"],
        }
        for family in ("base", "vertex", "edge", "nonedge")
    }


def row_rhs_hashes(system: dict[str, Any]) -> dict[str, str]:
    families = row_rhs_payload(system)
    hashes = {
        family: hashlib.sha256(compact_json(payload)).hexdigest()
        for family, payload in families.items()
    }
    hashes["combined"] = hashlib.sha256(compact_json(families)).hexdigest()
    return hashes


def row_system_record(system: dict[str, Any]) -> dict[str, Any]:
    """Freeze all coefficients for solver-free, standard-library replay."""

    families = row_rhs_payload(system)
    return {
        "format": "wave44-rooted-row-system-v1",
        "canonical_hash_encoding": (
            "UTF-8 compact JSON with sort_keys=True and separators=(',',':')"
        ),
        "classes": system["classes"],
        "families": families,
        "row_rhs_sha256": row_rhs_hashes(system),
    }


def stored_unrooted_vector(system: dict[str, Any]) -> tuple[int, ...]:
    result = json.loads(ENDPOINT_RESULT.read_text(encoding="utf-8"))
    support = result["certificate"]["support"]
    counts = {record["canonical_mask"]: record["count"] for record in support}
    y_value = result["certificate"]["h11"] // 4
    return tuple(counts.get(mask, 0) for mask in system["classes"]) + (y_value,)


def validate_rooted_witness(
    system: dict[str, Any],
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if payload is None:
        payload = json.loads(ROOTED_WITNESS.read_text(encoding="utf-8"))
    require(
        payload.get("format") == "wave44-rooted-flags-witness-v1",
        "witness format changed",
    )
    support = payload.get("support")
    require(isinstance(support, list), "witness support missing")
    class_index = {mask: index for index, mask in enumerate(system["classes"])}
    counts = [0] * len(system["classes"])
    seen: set[int] = set()
    for record in support:
        require(
            isinstance(record, dict)
            and set(record) == {"canonical_mask", "count"},
            "malformed support record",
        )
        mask = record["canonical_mask"]
        count = record["count"]
        require(
            type(mask) is int and type(count) is int and count > 0,
            "support values must be positive integers",
        )
        require(mask in class_index and mask not in seen, "unknown/duplicate class")
        seen.add(mask)
        counts[class_index[mask]] = count
    h11 = payload.get("h11")
    require(type(h11) is int and h11 % 4 == 0, "bad h11")
    y_value = h11 // 4
    require(2079 <= y_value <= 4158, "h11 outside endpoint interval")
    vector = tuple(counts) + (y_value,)
    rows = (
        system["base_rows"]
        + system["vertex_rows"]
        + system["edge_rows"]
        + system["nonedge_rows"]
    )
    rhs = (
        system["base_rhs"]
        + system["vertex_rhs"]
        + system["edge_rhs"]
        + system["nonedge_rhs"]
    )
    exact_residuals = residuals(rows, rhs, vector)
    require(not any(exact_residuals), "rooted witness has a nonzero residual")
    require(sum(counts) == math.comb(N, 7), "seven-subset total changed")
    canonical_support = json.dumps(
        support, sort_keys=True, separators=(",", ":")
    ).encode("ascii")
    support_digest = hashlib.sha256(canonical_support).hexdigest()
    require(
        payload["support_sha256"] == support_digest,
        "witness support digest changed",
    )
    require(payload["support_size"] == len(support), "support size changed")
    require(
        payload["zero_classes"] == len(system["classes"]) - len(support),
        "zero class count changed",
    )
    require(payload["maximum_count"] == max(counts), "maximum count changed")
    return {
        "h11": h11,
        "support_size": len(support),
        "zero_classes": len(system["classes"]) - len(support),
        "maximum_count": max(counts),
        "support_sha256": support_digest,
        "witness_file_sha256": sha256_file(ROOTED_WITNESS),
        "all_170_exact_integer_rows": "PASS",
        "seven_subset_total": sum(counts),
        "vector": vector,
    }


def residuals(
    rows: Sequence[Sequence[int]],
    rhs: Sequence[int],
    vector: Sequence[int],
) -> tuple[int, ...]:
    return tuple(
        sum(coefficient * value for coefficient, value in zip(row, vector))
        - target
        for row, target in zip(rows, rhs)
    )


def sparse_system(
    rows: Sequence[Sequence[int]],
) -> coo_array:
    row_indices: list[int] = []
    column_indices: list[int] = []
    values: list[float] = []
    for row_index, row in enumerate(rows):
        for column_index, value in enumerate(row):
            if value:
                row_indices.append(row_index)
                column_indices.append(column_index)
                values.append(float(value))
    return coo_array(
        (
            np.asarray(values, dtype=np.float64),
            (
                np.asarray(row_indices, dtype=np.int32),
                np.asarray(column_indices, dtype=np.int32),
            ),
        ),
        shape=(len(rows), len(rows[0])),
    ).tocsr()


def solve_augmented(
    system: dict[str, Any],
    time_limit: float,
) -> dict[str, Any]:
    rows = (
        system["base_rows"]
        + system["vertex_rows"]
        + system["edge_rows"]
        + system["nonedge_rows"]
    )
    rhs = (
        system["base_rhs"]
        + system["vertex_rhs"]
        + system["edge_rhs"]
        + system["nonedge_rhs"]
    )
    matrix = sparse_system(rows)
    variable_count = len(rows[0])
    lower = np.zeros(variable_count, dtype=np.float64)
    upper = np.full(variable_count, np.inf, dtype=np.float64)
    lower[-1] = math.ceil(2 * N3 / 4)
    upper[-1] = N3
    result = milp(
        c=np.zeros(variable_count, dtype=np.float64),
        integrality=np.ones(variable_count, dtype=np.uint8),
        bounds=Bounds(lower, upper),
        constraints=LinearConstraint(
            matrix,
            np.asarray(rhs, dtype=np.float64),
            np.asarray(rhs, dtype=np.float64),
        ),
        options={
            "disp": False,
            "presolve": True,
            "time_limit": time_limit,
            "mip_rel_gap": 0.0,
        },
    )
    candidate = None
    maximum_rounding_error = None
    if result.x is not None:
        rounded = tuple(int(round(float(value))) for value in result.x)
        maximum_rounding_error = max(
            abs(float(value) - integer)
            for value, integer in zip(result.x, rounded)
        )
        exact_residuals = residuals(rows, rhs, rounded)
        if any(exact_residuals):
            raise ValueError("solver candidate failed exact rooted equations")
        require(min(rounded) >= 0, "solver candidate is negative")
        support = [
            {"canonical_mask": mask, "count": count}
            for mask, count in zip(system["classes"], rounded[:-1])
            if count
        ]
        candidate = {
            "h11": 4 * rounded[-1],
            "support_size": len(support),
            "support": support,
            "support_sha256": hashlib.sha256(
                json.dumps(
                    support, sort_keys=True, separators=(",", ":")
                ).encode("ascii")
            ).hexdigest(),
        }
    return {
        "status": int(result.status),
        "message": str(result.message),
        "success": bool(result.success),
        "time_limit_seconds": time_limit,
        "maximum_rounding_error": maximum_rounding_error,
        "candidate": candidate,
        "negative_status_is_not_certificate": True,
    }


def compute() -> dict[str, Any]:
    system = endpoint_system()
    expected_row_record = canonical_json(row_system_record(system))
    require(ROW_SYSTEM.is_file(), "frozen row-system.json is missing")
    require(
        ROW_SYSTEM.read_bytes() == expected_row_record,
        "frozen row-system.json differs from reconstructed rows",
    )
    base = system["base_rows"]
    vertex = system["vertex_rows"]
    edge = system["edge_rows"]
    nonedge = system["nonedge_rows"]
    primes = (101, 103, 107)
    rank_table: dict[str, dict[str, int]] = {}
    for prime in primes:
        rank_table[str(prime)] = {
            "base": rank_mod_prime(base, prime),
            "base_plus_vertex": rank_mod_prime(base + vertex, prime),
            "base_plus_vertex_edge": rank_mod_prime(
                base + vertex + edge, prime
            ),
            "all_rooted": rank_mod_prime(
                base + vertex + edge + nonedge, prime
            ),
        }

    vector = stored_unrooted_vector(system)
    base_residual = residuals(base, system["base_rhs"], vector)
    require(not any(base_residual), "stored unrooted witness no longer fits base")
    vertex_residual = residuals(vertex, system["vertex_rhs"], vector)
    edge_residual = residuals(edge, system["edge_rhs"], vector)
    nonedge_residual = residuals(nonedge, system["nonedge_rhs"], vector)
    rooted_certificate = validate_rooted_witness(system)
    return {
        "format": "wave44-rooted-flags-v1",
        "role": "proof_a",
        "claim_label": (
            "EXACTLY_VALIDATED_ROOTED_COUNT_WITNESS"
        ),
        "git_commit": "e28f90464d00b98d37672b0b2b23dba15399a6f2",
        "scope": (
            "Conditional endpoint n3=4158: the 208-class order-seven deck "
            "augmented by all ordered vertex-, edge-, and nonedge-rooted "
            "neighborhood-category equations."
        ),
        "inputs": {
            "attempts/wave43-seven-deck-endpoint/endpoint_deck.py":
                sha256_file(ENDPOINT_PATH),
            "attempts/wave43-seven-deck-endpoint/exact-results.json":
                sha256_file(ENDPOINT_RESULT),
            "attempts/wave44-rooted-flags/rooted-witness.json":
                sha256_file(ROOTED_WITNESS),
            "attempts/wave44-rooted-flags/row-system.json":
                sha256_file(ROW_SYSTEM),
        },
        "assumptions": {
            "srg_parameters": [N, K, LAMBDA, MU],
            "n3": N3,
            "endpoint_equivalence": "n3=4158 iff no induced triangular prism",
            "automorphism_assumption": "none",
        },
        "rooted_system": {
            "variables_including_h11_over_4": len(system["classes"]) + 1,
            "unrooted_rows": len(base),
            "vertex_root_rows": len(vertex),
            "edge_root_rows": len(edge),
            "nonedge_root_rows": len(nonedge),
            "total_rows": len(base) + len(vertex) + len(edge) + len(nonedge),
            "edge_category_sizes": [1, 12, 12, 72],
            "nonedge_category_sizes": [2, 12, 12, 71],
            "row_rhs_sha256": row_rhs_hashes(system),
            "finite_field_rank_table": rank_table,
        },
        "stored_unrooted_witness_attack": {
            "vertex_nonzero_residual_rows": sum(value != 0 for value in vertex_residual),
            "edge_nonzero_residual_rows": sum(value != 0 for value in edge_residual),
            "nonedge_nonzero_residual_rows": sum(
                value != 0 for value in nonedge_residual
            ),
            "vertex_max_abs_residual": max(map(abs, vertex_residual)),
            "edge_max_abs_residual": max(map(abs, edge_residual)),
            "nonedge_max_abs_residual": max(map(abs, nonedge_residual)),
            "strictly_stronger_than_stored_witness": any(
                (*vertex_residual, *edge_residual, *nonedge_residual)
            ),
        },
        "exact_positive_control": {
            key: value
            for key, value in rooted_certificate.items()
            if key != "vector"
        },
        "solver_diagnostics": {
            "exact_discovery": {
                "engine": "Z3 5.0.0",
                "status": "sat",
                "used_for_certificate_checking": False,
            },
            "superseded_scipy_milp": {
                "reported_status": "infeasible",
                "classification": "FALSE_NEGATIVE_REFUTED_BY_EXACT_WITNESS",
                "cause_assessment": "large-scale floating numerical instability",
                "used_as_evidence": False,
            },
            "continuous_LP": {
                "status": "numerically feasible",
                "used_as_evidence": False,
            },
        },
        "conclusion": {
            "rooted_count_system": "EXACT_FEASIBLE",
            "strictly_stronger_than_unrooted_rows": all(
                values["all_rooted"] > values["base"]
                for values in rank_table.values()
            ),
            "endpoint_n3_4158": "UNKNOWN",
            "upper_bound_below_4158": "NOT_PROVED",
            "graph_constructed": False,
            "Conway_99": "UNKNOWN",
        },
        "limitations": [
            "Aggregate rooted counts still do not assign compatible types to "
            "individual overlapping seven-subsets.",
            "A feasible rooted count vector is not a graph or evidence of one.",
            "A negative solver status is not a proof without an exact Farkas "
            "or branch certificate.",
            "No positive-semidefinite flag moment matrix is imposed yet.",
            "No endpoint exclusion, upper-bound improvement, novelty, or "
            "priority claim is made.",
        ],
    }


def validate_record(result: dict[str, Any]) -> None:
    require(result["format"] == "wave44-rooted-flags-v1", "format changed")
    require(
        result["rooted_system"]["edge_root_rows"] == 36,
        "edge signature census changed",
    )
    require(
        result["rooted_system"]["nonedge_root_rows"] == 46,
        "nonedge signature census changed",
    )
    require(
        result["conclusion"]["endpoint_n3_4158"] == "UNKNOWN",
        "status inflation",
    )
    require(
        result["conclusion"]["Conway_99"] == "UNKNOWN",
        "status inflation",
    )
    require(
        result["claim_label"] == "EXACTLY_VALIDATED_ROOTED_COUNT_WITNESS",
        "claim label changed",
    )
    require(
        result["conclusion"]["strictly_stronger_than_unrooted_rows"],
        "rank increment disappeared",
    )
    system = endpoint_system()
    require(
        ROW_SYSTEM.read_bytes() == canonical_json(row_system_record(system)),
        "frozen row-system.json changed",
    )
    require(
        result["rooted_system"]["row_rhs_sha256"] == row_rhs_hashes(system),
        "row/RHS hash commitment changed",
    )
    require(
        result["inputs"]["attempts/wave44-rooted-flags/row-system.json"]
        == sha256_file(ROW_SYSTEM),
        "row-system file hash changed",
    )
    certificate = validate_rooted_witness(system)
    require(
        result["exact_positive_control"]
        == {key: value for key, value in certificate.items() if key != "vector"},
        "stored certificate summary changed",
    )
    require(
        result["conclusion"]["rooted_count_system"] == "EXACT_FEASIBLE",
        "feasible conclusion changed",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    parser.add_argument("--write-row-system", type=Path)
    arguments = parser.parse_args()
    if arguments.write_row_system:
        require(
            arguments.output is None and arguments.verify is None,
            "--write-row-system cannot be combined with other modes",
        )
        payload = canonical_json(row_system_record(endpoint_system()))
        arguments.write_row_system.parent.mkdir(parents=True, exist_ok=True)
        arguments.write_row_system.write_bytes(payload)
        print(
            f"WROTE {arguments.write_row_system} "
            f"sha256={hashlib.sha256(payload).hexdigest()}"
        )
        return 0
    if arguments.verify:
        stored_payload = arguments.verify.read_bytes()
        result = json.loads(stored_payload)
        validate_record(result)
        require(
            canonical_json(compute()) == stored_payload,
            "full exact result replay differs from frozen result",
        )
        print(
            f"PASS {arguments.verify} "
            f"sha256={hashlib.sha256(arguments.verify.read_bytes()).hexdigest()}"
        )
        return 0
    result = compute()
    validate_record(result)
    payload = canonical_json(result)
    if arguments.output:
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_bytes(payload)
        print(
            f"WROTE {arguments.output} "
            f"sha256={hashlib.sha256(payload).hexdigest()}"
        )
    else:
        print(payload.decode("utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
