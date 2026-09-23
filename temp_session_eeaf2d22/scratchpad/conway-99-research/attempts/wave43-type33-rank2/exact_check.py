#!/usr/bin/env python3
"""Exact pivot/mate CSP for endpoint type 3+3 rank-two residuals.

For the all-odd local type (3,3), the Wave 42 border term F is zero.  Local
rank 27 is therefore equivalent to the 12-by-12 symmetric Schur residual
having rank two.  Every symmetric rank-two matrix over F_7 has an invertible
principal 2-by-2 submatrix.  Once that pivot, its two border images, and the
pivot vertices' mates in R are fixed, the zero Schur complement determines
whether every remaining pair must or must not be an R-matching edge.

This checker searches the border permutation and perfect matching jointly.
It assumes only the endpoint derangement condition; it does not impose an
automorphism of a completed graph.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from types import ModuleType
from typing import Sequence


PRIME = 7
SIDE = 12
FORMAT = "wave43-type33-rank2-v1"
FROZEN_COMMIT = "e28f90464d00b98d37672b0b2b23dba15399a6f2"
ROOT = Path(__file__).resolve().parents[2]
WAVE41 = ROOT / "verification/wave41-rank26-secondary/secondary_check.py"
WAVE41_SHA256 = (
    "3dc38b519712916bc410775c2e8c9d7099bae53268834c92fd06505a9cddb7a3"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load_wave41() -> ModuleType:
    require(sha256_bytes(WAVE41.read_bytes()) == WAVE41_SHA256, "source hash changed")
    spec = importlib.util.spec_from_file_location("wave41_type33_frozen", WAVE41)
    require(spec is not None and spec.loader is not None, "cannot load Wave 41")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.audit_frozen_inputs()
    return module


def pair_matrix(matching: Sequence[Sequence[int]]) -> list[list[int]]:
    mates: dict[int, int] = {}
    for left, right in matching:
        require(left != right, "matching loop")
        require(left not in mates and right not in mates, "matching repetition")
        mates[left] = right
        mates[right] = left
    require(len(mates) == SIDE, "matching incomplete")
    return [
        [
            (1 - int(left == right) - 2 * int(mates[left] == right)) % PRIME
            for right in range(SIDE)
        ]
        for left in range(SIDE)
    ]


def residual(
    interaction: Sequence[Sequence[int]],
    permutation: Sequence[int],
    matching: Sequence[Sequence[int]],
) -> list[list[int]]:
    w = pair_matrix(matching)
    return [
        [
            (
                w[left][right]
                - interaction[12 * left + permutation[left]][
                    12 * right + permutation[right]
                ]
            )
            % PRIME
            for right in range(SIDE)
        ]
        for left in range(SIDE)
    ]


def search(first_only: bool = True) -> dict[str, object]:
    wave41 = load_wave41()
    context = wave41.partition_context((3, 3))
    signatures = context["signatures"]
    require(
        all(not any(vector) for vector in signatures),
        "type 3+3 border F is not identically zero",
    )
    interaction = context["interaction"]
    require(
        interaction == [list(row) for row in zip(*interaction)],
        "type 3+3 interaction table is not symmetric",
    )

    branch_count = 0
    invertible_pivot_branches = 0
    nonempty_unary_branches = 0
    backtrack_nodes = 0
    complete_leaves = 0
    solutions: dict[str, dict[str, object]] = {}

    def target(i: int, image_i: int, j: int, image_j: int) -> int:
        return interaction[12 * i + image_i][12 * j + image_j] % PRIME

    for p in range(SIDE):
        for q in range(p + 1, SIDE):
            rest = tuple(vertex for vertex in range(SIDE) if vertex not in (p, q))
            mate_cases = [(q, p, "pivot_pair")]
            mate_cases.extend(
                (mate_p, mate_q, "separate")
                for mate_p in rest
                for mate_q in rest
                if mate_p != mate_q
            )
            for mate_p, mate_q, mate_case in mate_cases:
                for image_p in range(SIDE):
                    if image_p == p:
                        continue
                    for image_q in range(SIDE):
                        if image_q == q or image_q == image_p:
                            continue
                        branch_count += 1
                        w_pq = 6 if mate_case == "pivot_pair" else 1
                        d_pp = -target(p, image_p, p, image_p) % PRIME
                        d_pq = (
                            w_pq - target(p, image_p, q, image_q)
                        ) % PRIME
                        d_qq = -target(q, image_q, q, image_q) % PRIME
                        determinant = (d_pp * d_qq - d_pq * d_pq) % PRIME
                        if determinant == 0:
                            continue
                        invertible_pivot_branches += 1
                        inverse_det = pow(determinant, -1, PRIME)
                        inverse = (
                            (
                                d_qq * inverse_det % PRIME,
                                -d_pq * inverse_det % PRIME,
                            ),
                            (
                                -d_pq * inverse_det % PRIME,
                                d_pp * inverse_det % PRIME,
                            ),
                        )

                        domains: dict[int, tuple[int, ...]] = {}
                        pivot_rows: dict[tuple[int, int], tuple[int, int]] = {}
                        unary_ok = True
                        for vertex in rest:
                            values: list[int] = []
                            for image in range(SIDE):
                                if (
                                    image == vertex
                                    or image == image_p
                                    or image == image_q
                                ):
                                    continue
                                w_ip = 6 if vertex == mate_p else 1
                                w_iq = 6 if vertex == mate_q else 1
                                x = (
                                    w_ip - target(vertex, image, p, image_p)
                                ) % PRIME
                                y = (
                                    w_iq - target(vertex, image, q, image_q)
                                ) % PRIME
                                predicted_diagonal = (
                                    x * (inverse[0][0] * x + inverse[0][1] * y)
                                    + y * (inverse[1][0] * x + inverse[1][1] * y)
                                ) % PRIME
                                actual_diagonal = (
                                    -target(vertex, image, vertex, image)
                                ) % PRIME
                                if predicted_diagonal == actual_diagonal:
                                    values.append(image)
                                    pivot_rows[(vertex, image)] = (x, y)
                            if not values:
                                unary_ok = False
                                break
                            domains[vertex] = tuple(values)
                        if not unary_ok:
                            continue
                        nonempty_unary_branches += 1

                        fixed_to_pivot = (
                            frozenset()
                            if mate_case == "pivot_pair"
                            else frozenset((mate_p, mate_q))
                        )
                        target_remaining_degree = {
                            vertex: 0 if vertex in fixed_to_pivot else 1
                            for vertex in rest
                        }
                        assigned: dict[int, int] = {}
                        used_images = (1 << image_p) | (1 << image_q)
                        match_degree = {vertex: 0 for vertex in rest}
                        match_edges: set[tuple[int, int]] = set()

                        def required_match(
                            left: int,
                            left_image: int,
                            right: int,
                            right_image: int,
                        ) -> bool | None:
                            lx, ly = pivot_rows[(left, left_image)]
                            rx, ry = pivot_rows[(right, right_image)]
                            predicted = (
                                lx
                                * (inverse[0][0] * rx + inverse[0][1] * ry)
                                + ly
                                * (inverse[1][0] * rx + inverse[1][1] * ry)
                            ) % PRIME
                            needed_w = (
                                target(left, left_image, right, right_image)
                                + predicted
                            ) % PRIME
                            if needed_w == 6:
                                return True
                            if needed_w == 1:
                                return False
                            return None

                        def viable_values(vertex: int, used: int) -> list[int]:
                            result: list[int] = []
                            for image in domains[vertex]:
                                if used >> image & 1:
                                    continue
                                local_degree = match_degree[vertex]
                                valid = True
                                for other, other_image in assigned.items():
                                    relation = required_match(
                                        vertex, image, other, other_image
                                    )
                                    if relation is None:
                                        valid = False
                                        break
                                    if relation:
                                        local_degree += 1
                                        if (
                                            local_degree
                                            > target_remaining_degree[vertex]
                                            or match_degree[other] + 1
                                            > target_remaining_degree[other]
                                        ):
                                            valid = False
                                            break
                                if valid:
                                    result.append(image)
                            return result

                        def backtrack(used: int) -> bool:
                            nonlocal backtrack_nodes, complete_leaves
                            backtrack_nodes += 1
                            if len(assigned) == len(rest):
                                complete_leaves += 1
                                if any(
                                    match_degree[vertex]
                                    != target_remaining_degree[vertex]
                                    for vertex in rest
                                ):
                                    return False
                                permutation = [-1] * SIDE
                                permutation[p] = image_p
                                permutation[q] = image_q
                                for vertex, image in assigned.items():
                                    permutation[vertex] = image
                                matching: list[tuple[int, int]] = []
                                if mate_case == "pivot_pair":
                                    matching.append((p, q))
                                else:
                                    matching.extend(((p, mate_p), (q, mate_q)))
                                matching.extend(sorted(match_edges))
                                require(len(matching) == 6, "leaf matching size changed")
                                matrix = residual(interaction, permutation, matching)
                                exact_rank = wave41.rank(matrix)
                                require(exact_rank == 2, "CSP leaf is not rank two")
                                full_rank = wave41.rank(
                                    wave41.full_block((3, 3), permutation, matching)
                                )
                                require(full_rank == 25 + exact_rank, "rank formula failed")
                                payload = {
                                    "permutation": permutation,
                                    "matching": [list(edge) for edge in matching],
                                    "residual": matrix,
                                    "residual_rank_F7": exact_rank,
                                    "full_K39_rank_F7": full_rank,
                                    "pivot": [p, q],
                                    "pivot_images": [image_p, image_q],
                                    "pivot_mate_case": mate_case,
                                }
                                key = sha256_bytes(canonical_bytes(payload))
                                solutions.setdefault(key, payload)
                                return first_only

                            choices: list[tuple[int, int, list[int]]] = []
                            for vertex in rest:
                                if vertex in assigned:
                                    continue
                                values = viable_values(vertex, used)
                                if not values:
                                    return False
                                choices.append((len(values), vertex, values))
                            _, vertex, values = min(choices)
                            for image in values:
                                added_edges: list[tuple[int, int]] = []
                                touched: list[int] = []
                                valid = True
                                for other, other_image in assigned.items():
                                    relation = required_match(
                                        vertex, image, other, other_image
                                    )
                                    require(relation is not None, "viability drift")
                                    if relation:
                                        edge = tuple(sorted((vertex, other)))
                                        match_edges.add(edge)
                                        added_edges.append(edge)
                                        match_degree[vertex] += 1
                                        match_degree[other] += 1
                                        touched.append(other)
                                        if (
                                            match_degree[vertex]
                                            > target_remaining_degree[vertex]
                                            or match_degree[other]
                                            > target_remaining_degree[other]
                                        ):
                                            valid = False
                                            break
                                if valid:
                                    assigned[vertex] = image
                                    if backtrack(used | (1 << image)) and first_only:
                                        return True
                                    del assigned[vertex]
                                for edge in added_edges:
                                    match_edges.discard(edge)
                                match_degree[vertex] = 0
                                for other in touched:
                                    match_degree[other] -= 1
                            return False

                        if backtrack(used_images) and first_only:
                            return {
                                "format": FORMAT,
                                "claim_label": "CANDIDATE_LOCAL_WITNESS",
                                "git_commit": FROZEN_COMMIT,
                                "scope": (
                                    "Conditional endpoint type 3+3 local rank-two "
                                    "Schur-residual search; no completed graph or "
                                    "completed-graph automorphism."
                                ),
                                "input": {
                                    str(WAVE41.relative_to(ROOT)).replace("\\", "/"):
                                        WAVE41_SHA256,
                                },
                                "search": {
                                    "branches_visited": branch_count,
                                    "invertible_pivot_branches": invertible_pivot_branches,
                                    "nonempty_unary_branches": nonempty_unary_branches,
                                    "backtrack_nodes": backtrack_nodes,
                                    "complete_leaves": complete_leaves,
                                    "first_only": True,
                                },
                                "solutions": list(solutions.values()),
                                "conclusion": (
                                    "An exact type-3+3 local rank-27 witness survives. "
                                    "Therefore an endpoint rank-28 theorem cannot follow "
                                    "from the one-edge local relaxation alone."
                                ),
                                "status_wall": {
                                    "witness_is_99_vertex_graph": False,
                                    "endpoint_excluded": False,
                                    "conway_99_resolved": False,
                                },
                            }

    return {
        "format": FORMAT,
        "claim_label": "DERIVED_PENDING_INDEPENDENT_VERIFICATION",
        "git_commit": FROZEN_COMMIT,
        "scope": (
            "Complete endpoint type 3+3 local rank-two Schur-residual search; "
            "no completed graph or completed-graph automorphism."
        ),
        "input": {
            str(WAVE41.relative_to(ROOT)).replace("\\", "/"): WAVE41_SHA256,
        },
        "search": {
            "branches_visited": branch_count,
            "invertible_pivot_branches": invertible_pivot_branches,
            "nonempty_unary_branches": nonempty_unary_branches,
            "backtrack_nodes": backtrack_nodes,
            "complete_leaves": complete_leaves,
            "first_only": first_only,
        },
        "solutions": list(solutions.values()),
        "conclusion": (
            "No endpoint type-3+3 rank-two residual exists."
            if not solutions
            else "Endpoint type-3+3 rank-two residuals exist."
        ),
        "status_wall": {
            "endpoint_excluded": False,
            "conway_99_resolved": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()
    rendered = canonical_bytes(search(first_only=not args.all))
    if args.verify is not None:
        if args.verify.read_bytes() != rendered:
            raise SystemExit("verification mismatch")
        print("verification: PASS")
    elif args.output is not None:
        args.output.write_bytes(rendered)
    else:
        print(rendered.decode("utf-8"), end="")


if __name__ == "__main__":
    main()
