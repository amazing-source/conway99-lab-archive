#!/usr/bin/env python3
"""Sparse MILP scout for the canonical mask-51739 full-B problem.

This is a construction search.  A feasible incumbent is exported only after
an exact integer recheck.  Solver infeasibility or timeout status is never
treated as a nonexistence certificate.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import coo_array

from solve_joint import (
    CANONICAL_MASK,
    CORE_EDGE_SHA256,
    FORMAT,
    SOURCE,
    SOURCE_SHA256,
    adjacency_from_edges,
    candidate_digest,
    canonical_bytes,
    components,
    enumerate_candidates,
    fibre_pairs,
    forced_gram,
    mixed_legal,
    read_source,
    sha256_bytes,
)

PAIR_ROWS = 3 * 60
CELL_ROWS = 3 * 12 * 12
ROW_COUNT = PAIR_ROWS + CELL_ROWS
FIBRE_PAIRS = ((0, 1), (0, 2), (1, 2))


def build_sparse_system(
    candidates: list[tuple[int, int, int]],
    pairs: tuple[tuple[tuple[int, int], ...], ...],
    gram: list[list[int]],
) -> tuple[coo_array, np.ndarray]:
    row_indices: list[int] = []
    column_indices: list[int] = []
    values: list[float] = []

    for variable, candidate in enumerate(candidates):
        for fibre, pair_index in enumerate(candidate):
            row_indices.append(60 * fibre + pair_index)
            column_indices.append(variable)
            values.append(1.0)

        for block, (first, second) in enumerate(FIBRE_PAIRS):
            first_pair = pairs[first][candidate[first]]
            second_pair = pairs[second][candidate[second]]
            for left in first_pair:
                for right in second_pair:
                    local_left = left - 12 * first
                    local_right = right - 12 * second
                    row_indices.append(
                        PAIR_ROWS + 144 * block + 12 * local_left + local_right
                    )
                    column_indices.append(variable)
                    values.append(1.0)

    matrix = coo_array(
        (
            np.asarray(values, dtype=np.float64),
            (
                np.asarray(row_indices, dtype=np.int32),
                np.asarray(column_indices, dtype=np.int32),
            ),
        ),
        shape=(ROW_COUNT, len(candidates)),
    ).tocsr()

    targets = np.empty(ROW_COUNT, dtype=np.float64)
    targets[:PAIR_ROWS] = 1.0
    for block, (first, second) in enumerate(FIBRE_PAIRS):
        for local_left in range(12):
            for local_right in range(12):
                left = 12 * first + local_left
                right = 12 * second + local_right
                row = PAIR_ROWS + 144 * block + 12 * local_left + local_right
                targets[row] = gram[left][right]

    if matrix.nnz != 15 * len(candidates):
        raise AssertionError("each candidate must contribute to 15 exact rows")
    return matrix, targets


def exact_certificate(
    selected: list[int],
    candidates: list[tuple[int, int, int]],
    pairs: tuple[tuple[tuple[int, int], ...], ...],
    gram: list[list[int]],
    adjacency: list[list[int]],
) -> dict[str, object]:
    if len(selected) != 60 or len(set(selected)) != 60:
        raise ValueError("an exact certificate must select 60 distinct columns")

    selected_candidates = [candidates[index] for index in selected]
    for fibre in range(3):
        inventory = sorted(candidate[fibre] for candidate in selected_candidates)
        if inventory != list(range(60)):
            raise ValueError(f"fibre {fibre} pair partition failed")

    concurrence = [
        [[0] * 12 for _ in range(12)]
        for _ in FIBRE_PAIRS
    ]
    blocks: list[list[int]] = []
    for candidate in selected_candidates:
        block_vertices = sorted(
            vertex
            for fibre in range(3)
            for vertex in pairs[fibre][candidate[fibre]]
        )
        if not mixed_legal(block_vertices, adjacency):
            raise ValueError("selected block failed the mixed local equations")
        blocks.append(block_vertices)
        for block_index, (first, second) in enumerate(FIBRE_PAIRS):
            for left in pairs[first][candidate[first]]:
                for right in pairs[second][candidate[second]]:
                    concurrence[block_index][left - 12 * first][right - 12 * second] += 1

    for block_index, (first, second) in enumerate(FIBRE_PAIRS):
        target = [
            [
                gram[12 * first + local_left][12 * second + local_right]
                for local_right in range(12)
            ]
            for local_left in range(12)
        ]
        if concurrence[block_index] != target:
            raise ValueError(f"cross-fibre Gram block {first}{second} failed")

    payload = {
        "selected_candidate_indices": selected,
        "selected_pair_triples": [list(candidate) for candidate in selected_candidates],
        "selected_blocks": blocks,
        "pair_partition_counts": [60, 60, 60],
        "cross_fibre_gram_blocks_exact": True,
        "mixed_local_equations_exact": True,
    }
    payload["certificate_sha256"] = sha256_bytes(canonical_bytes(payload))
    return payload


def solve(
    source_path: Path,
    time_limit: float,
    node_limit: int,
) -> dict[str, object]:
    source = read_source(source_path)
    witness = source["rank_identity"]["minimum_witness"]
    adjacency = adjacency_from_edges(witness["core_edges"])
    gram = forced_gram(adjacency)
    core_components = components(adjacency)
    small = frozenset(core_components[0])
    pairs = tuple(fibre_pairs(fibre, gram) for fibre in range(3))
    candidates = enumerate_candidates(pairs, gram, adjacency, small)
    matrix, targets = build_sparse_system(candidates, pairs, gram)

    started = time.perf_counter()
    result = milp(
        c=np.zeros(len(candidates), dtype=np.float64),
        integrality=np.ones(len(candidates), dtype=np.uint8),
        bounds=Bounds(0.0, 1.0),
        constraints=LinearConstraint(matrix, targets, targets),
        options={
            "disp": False,
            "presolve": True,
            "time_limit": time_limit,
            "node_limit": node_limit,
            "mip_rel_gap": 0.0,
        },
    )
    elapsed = round(time.perf_counter() - started, 6)

    certificate = None
    if result.x is not None:
        selected = [
            index
            for index, value in enumerate(result.x)
            if float(value) > 0.5
        ]
        certificate = exact_certificate(
            selected, candidates, pairs, gram, adjacency
        )

    return {
        "format": "wave43-joint-completion-milp-v1",
        "role": "construction",
        "claim_label": (
            "SAT_CANDIDATE_PENDING_INDEPENDENT_VERIFICATION"
            if certificate is not None
            else "UNKNOWN"
        ),
        "scope": (
            "Conditional canonical mask-51739 full-B problem under n3=4158, "
            "rank_F3(M)=12, and all edges type 2+2+2. No automorphism assumed."
        ),
        "inputs": {
            str(source_path).replace("\\", "/"): SOURCE_SHA256,
            "canonical_mask": CANONICAL_MASK,
            "canonical_core_edges_sha256": CORE_EDGE_SHA256,
            "retained_candidate_sha256": candidate_digest(candidates),
        },
        "model": {
            "binary_variables": len(candidates),
            "exact_pair_partition_rows": PAIR_ROWS,
            "exact_cross_fibre_gram_rows": CELL_ROWS,
            "total_exact_rows": ROW_COUNT,
            "nonzeros": int(matrix.nnz),
        },
        "bounded_run": {
            "scipy_status": int(result.status),
            "success": bool(result.success),
            "message": str(result.message),
            "elapsed_seconds": elapsed,
            "time_limit_seconds": time_limit,
            "node_limit": node_limit,
            "mip_node_count": (
                None
                if getattr(result, "mip_node_count", None) is None
                else int(result.mip_node_count)
            ),
            "mip_gap": (
                None
                if getattr(result, "mip_gap", None) is None
                else float(result.mip_gap)
            ),
            "terminal_negative_certificate": False,
        },
        "certificate": certificate,
        "status_wall": {
            "full_B": (
                "SAT_CANDIDATE_PENDING_INDEPENDENT_VERIFICATION"
                if certificate is not None
                else "NOT_CONSTRUCTED_OR_EXCLUDED"
            ),
            "compatible_H": "NOT_CONSTRUCTED_OR_EXCLUDED",
            "endpoint_excluded": False,
            "conway_99_resolved": False,
        },
        "limitations": [
            "A solver infeasibility or timeout status is not nonexistence evidence.",
            "A feasible incumbent is only a full-B candidate until independently reconstructed.",
            "Even a verified full B would not provide a compatible outside graph H.",
            "No endpoint exclusion, strict upper bound, graph, or novelty claim follows automatically.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--time-limit", type=float, default=300.0)
    parser.add_argument("--node-limit", type=int, default=1_000_000)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not 1 <= args.time_limit <= 1800:
        raise SystemExit("time limit must be between 1 and 1800 seconds")
    if not 1 <= args.node_limit <= 100_000_000:
        raise SystemExit("node limit must be between 1 and 100000000")

    result = solve(args.source, args.time_limit, args.node_limit)
    rendered = canonical_bytes(result)
    if args.output is None:
        print(rendered.decode("utf-8"), end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(rendered)
        print(
            json.dumps(
                {
                    "output": str(args.output),
                    "sha256": sha256_bytes(rendered),
                    "claim_label": result["claim_label"],
                },
                sort_keys=True,
            )
        )


if __name__ == "__main__":
    main()
