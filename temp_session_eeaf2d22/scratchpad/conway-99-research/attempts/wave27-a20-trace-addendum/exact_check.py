#!/usr/bin/env python3
"""Exact checks for the Wave 27 A20 trace-compression addendum."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE_COMMIT = "9cc3f1e063ef63954102908c1b852dce7948a84f"
RANK = 44
GLOBAL_TRACE = 60
A20_RANK = 20

INPUTS = {
    "agents/2026-07-23-wave27-general-root-tensor.md":
        "456a4ad6f27c1c9c09f84b2ff41796473f519b5aaabda36b71022a51bbbe7f38",
    "attempts/wave27-general-root-tensor/exact-results.json":
        "98aba5a30b2f3a83b9f6ce6fd6a20458505b668249d97b0810907de50cae678d",
    "verification/wave26-a2-frame-obstruction/2026-07-23T225015Z-audit.md":
        "5ec6b1924fb9ca2ab9295808178684751b6a90e43315d00cbf232ba8d9fe84a3",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cartan_a(rank: int) -> list[list[int]]:
    return [
        [
            2 * int(i == j) - int(abs(i - j) == 1)
            for j in range(rank)
        ]
        for i in range(rank)
    ]


def outer(vector: list[int]) -> list[list[int]]:
    return [[left * right for right in vector] for left in vector]


def add(left: list[list[int]], right: list[list[int]]) -> list[list[int]]:
    return [
        [left[i][j] + right[i][j] for j in range(len(left))]
        for i in range(len(left))
    ]


def zero_matrix(rank: int) -> list[list[int]]:
    return [[0] * rank for _ in range(rank)]


def superbase_vectors(rank: int) -> list[list[int]]:
    vectors: list[list[int]] = []
    first = [0] * rank
    first[0] = 1
    vectors.append(first)
    for index in range(rank - 1):
        vector = [0] * rank
        vector[index] = 1
        vector[index + 1] = -1
        vectors.append(vector)
    last = [0] * rank
    last[-1] = 1
    vectors.append(last)
    return vectors


def rank_one_factorization(rank: int) -> dict[str, object]:
    vectors = superbase_vectors(rank)
    reconstructed = zero_matrix(rank)
    for vector in vectors:
        reconstructed = add(reconstructed, outer(vector))
    cartan = cartan_a(rank)
    if reconstructed != cartan:
        raise AssertionError(f"A{rank} rank-one factorization failed")
    if len(vectors) != rank + 1 or any(not any(vector) for vector in vectors):
        raise AssertionError("superbase vector count/nonzero check failed")
    return {
        "rank": rank,
        "vector_count": len(vectors),
        "vectors": vectors,
        "cartan": cartan,
        "sum_outer_products_equals_cartan": True,
        "even_positive_vector_norm_floor": 2,
        "trace_pairing_floor": 2 * (rank + 1),
    }


def endpoint_compression() -> dict[str, object]:
    local = 2 * (A20_RANK + 1)
    complement_rank = RANK - A20_RANK
    complement_floor = complement_rank
    aggregate = local + complement_floor
    if (local, complement_rank, complement_floor, aggregate) != (42, 24, 24, 66):
        raise AssertionError("A20 endpoint arithmetic drifted")
    if aggregate <= GLOBAL_TRACE:
        raise AssertionError("A20 compression should contradict trace 60")
    return {
        "summand": "A20",
        "summand_rank": A20_RANK,
        "local_even_trace_floor": local,
        "complement_rank": complement_rank,
        "complement_positive_integral_determinant_floor": 1,
        "complement_AM_GM_trace_floor": complement_floor,
        "aggregate_trace_floor": aggregate,
        "endpoint_global_trace": GLOBAL_TRACE,
        "contradiction_margin": aggregate - GLOBAL_TRACE,
        "orthogonal_A20_summand": "REFUTED",
    }


def general_threshold() -> dict[str, object]:
    rows = []
    for rank in range(1, RANK + 1):
        local = 2 * (rank + 1)
        complement = RANK - rank
        aggregate = local + complement
        rows.append({
            "A_rank": rank,
            "local_floor": local,
            "complement_floor": complement,
            "aggregate_floor": aggregate,
            "excluded_by_trace_60": aggregate > GLOBAL_TRACE,
        })
    excluded = [row["A_rank"] for row in rows if row["excluded_by_trace_60"]]
    if excluded != list(range(15, 45)):
        raise AssertionError("general A_n threshold drifted")
    return {
        "identity": "2(n+1)+(44-n)=n+46",
        "sharp_first_excluded_rank": 15,
        "A14_aggregate_floor": rows[13]["aggregate_floor"],
        "A15_aggregate_floor": rows[14]["aggregate_floor"],
        "rows": rows,
    }


def full_ade_corollary() -> dict[str, object]:
    return {
        "assumption": (
            "S is an orthogonal direct sum of irreducible ADE root lattices"
        ),
        "allowed_by_21_dual_integrality": ["A2", "A6", "A20", "E6", "E8"],
        "component_dispositions": {
            "A2": "REFUTED_BY_VERIFIED_WAVE26_FRAME_CAPACITY",
            "A6": "DERIVED_REFUTED_BY_WAVE27_TENSOR_FLOOR_PENDING_VERIFIER",
            "A20": "DERIVED_REFUTED_BY_TRACE_FLOOR_42_VS_CAP_36",
            "E6": "DERIVED_REFUTED_BY_WAVE27_TENSOR_FLOOR_PENDING_VERIFIER",
            "E8": "NOT_LOCALLY_REFUTED",
        },
        "rank_44_not_sum_of_E8_only": 44 % 8 != 0,
        "conditional_full_ADE_status": "REFUTED_PENDING_IMPORTED_TENSOR_VERIFIER",
    }


def validate_inputs() -> dict[str, object]:
    rows = {}
    for path, expected in INPUTS.items():
        actual = sha256(ROOT / path)
        rows[path] = {
            "expected_sha256": expected,
            "actual_sha256": actual,
            "matches": actual == expected,
        }
    if not all(row["matches"] for row in rows.values()):
        raise AssertionError("frozen input mismatch")
    return rows


def build_results() -> dict[str, object]:
    return {
        "status": "DERIVED_PENDING_FRESH_INDEPENDENT_VERIFIER",
        "base_commit": BASE_COMMIT,
        "frozen_inputs": validate_inputs(),
        "A20_rank_one_factorization": rank_one_factorization(A20_RANK),
        "endpoint_compression": endpoint_compression(),
        "general_A_n_threshold": general_threshold(),
        "full_ADE_corollary": full_ade_corollary(),
        "scope": {
            "requires_orthogonal_integral_summand": True,
            "general_even_lattices_classified": False,
            "n3_708_excluded": False,
            "conway_99_status": "UNKNOWN",
            "novelty_status": "UNKNOWN",
        },
        "hostile_controls": {
            "drop_evenness": (
                "vector norms may be one, so the 2(n+1) floor is unavailable"
            ),
            "A14_boundary": "aggregate floor equals 60 and is not contradictory",
            "nonorthogonal_A20_subsystem": "outside the block-compression theorem",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("exact-results.json"),
    )
    args = parser.parse_args()
    payload = build_results()
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "A20": payload["endpoint_compression"]["orthogonal_A20_summand"],
        "full_ADE": payload["full_ADE_corollary"]["conditional_full_ADE_status"],
        "target": payload["scope"]["conway_99_status"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
