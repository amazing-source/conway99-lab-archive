#!/usr/bin/env python3
"""Independent verifier for the Wave 39 edge-local rank claim.

This program does not import or execute the discovery implementation under
``attempts/wave39-edge-local-rank``.  It reconstructs all 10,395 normalized
matching configurations around an edge of a putative srg(99,14,1,2), builds
the corresponding 27 by 27 transported principal block, and performs exact
Gaussian elimination over F_7.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterator, Sequence


HERE = Path(__file__).resolve().parent
DEFAULT_RESULT = HERE / "independent-results.json"
PRIME = 7
TARGET = {"v": 99, "k": 14, "lambda": 1, "mu": 2}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def reject_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON constant {value!r}")


def load_json(path: Path) -> dict[str, Any]:
    result = json.loads(
        path.read_bytes(),
        object_pairs_hook=strict_object,
        parse_constant=reject_constant,
    )
    if not isinstance(result, dict):
        raise ValueError("result must be a JSON object")
    return result


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def perfect_matchings(vertices: tuple[int, ...]) -> Iterator[tuple[tuple[int, int], ...]]:
    """Generate every perfect matching, with no duplicate labelled matching."""

    if not vertices:
        yield ()
        return
    first = vertices[0]
    for position in range(1, len(vertices)):
        second = vertices[position]
        remainder = vertices[1:position] + vertices[position + 1 :]
        for tail in perfect_matchings(remainder):
            yield ((first, second),) + tail


def validate_matching(matching: Sequence[tuple[int, int]]) -> None:
    flat = [vertex for edge in matching for vertex in edge]
    require(len(matching) == 6, "a side matching must have six edges")
    require(all(left != right for left, right in matching), "matching has a loop")
    require(sorted(flat) == list(range(12)), "matching does not cover 0,...,11 once")


def local_geometry(
    *,
    k: int = 14,
    lam: int = 1,
    mu: int = 2,
) -> dict[str, Any]:
    """Derive the matching geometry from the SRG common-neighbor axioms."""

    require((k, lam, mu) == (14, 1, 2), "frozen SRG parameters changed")
    side_size = k - 2
    require(side_size == 12, "edge side has the wrong size")

    # G[N(x)] is lambda-regular: for u in N(x), its neighbors in N(x)
    # are exactly the common neighbors of the adjacent pair x,u.
    require(lam == 1, "the side is not forced to be a perfect matching")

    # If xy has unique common neighbor z, then X and Y are disjoint.  Also z
    # has no neighbor in X or Y: xz already has y as its unique common
    # neighbor, and yz already has x.
    triangle_mate_side_degree = lam - 1
    require(triangle_mate_side_degree == 0, "z is not isolated from X union Y")

    # For u in X, u and y are nonadjacent.  Their two common neighbors are x
    # and exactly one point of Y.  This makes the X--Y relation 1-regular in
    # both directions.
    cross_degree = mu - 1
    require(cross_degree == 1, "the cross relation is not a perfect matching")

    return {
        "side_size": side_size,
        "X_and_Y_disjoint": True,
        "X_internal_degree": lam,
        "Y_internal_degree": lam,
        "triangle_mate_degree_into_each_side": triangle_mate_side_degree,
        "cross_degree_each_direction": cross_degree,
        "three_relations": [
            "perfect matching on X",
            "perfect matching on Y",
            "perfect matching between X and Y",
        ],
    }


def add_edge(adjacency: list[list[int]], left: int, right: int) -> None:
    require(left != right, "loop in local graph")
    require(adjacency[left][right] == 0, "duplicate local edge")
    adjacency[left][right] = 1
    adjacency[right][left] = 1


def build_local_graph(
    y_matching: Sequence[tuple[int, int]],
) -> list[list[int]]:
    """Build the normalized 27-point graph for a pulled-back Y matching.

    X's matching is (0,1),(2,3),..., and the cross matching is X_i--Y_i.
    Relabelling X and then pulling labels through the cross matching loses no
    configurations, so Y's matching ranges over all 10,395 possibilities.
    """

    validate_matching(y_matching)
    adjacency = [[0] * 27 for _ in range(27)]
    x, y, z = 0, 1, 2
    xs = [3 + index for index in range(12)]
    ys = [15 + index for index in range(12)]

    for edge in ((x, y), (x, z), (y, z)):
        add_edge(adjacency, *edge)
    for vertex in xs:
        add_edge(adjacency, x, vertex)
    for vertex in ys:
        add_edge(adjacency, y, vertex)
    for index in range(0, 12, 2):
        add_edge(adjacency, xs[index], xs[index + 1])
    for left, right in y_matching:
        add_edge(adjacency, ys[left], ys[right])
    for index in range(12):
        add_edge(adjacency, xs[index], ys[index])

    degrees = [sum(row) for row in adjacency]
    require(degrees[:3] == [14, 14, 2], "distinguished local degrees changed")
    require(degrees[3:] == [3] * 24, "side local degrees changed")
    require(sum(degrees) // 2 == 51, "local edge count changed")
    return adjacency


def cycle_partition(adjacency: Sequence[Sequence[int]]) -> tuple[int, ...]:
    """Return positive parts m where the 24-point components have length 4m."""

    allowed = set(range(3, 27))
    unseen = set(allowed)
    component_sizes: list[int] = []
    while unseen:
        start = min(unseen)
        stack = [start]
        size = 0
        while stack:
            vertex = stack.pop()
            if vertex not in unseen:
                continue
            unseen.remove(vertex)
            size += 1
            stack.extend(
                neighbor
                for neighbor in allowed
                if adjacency[vertex][neighbor] and neighbor in unseen
            )
        require(size % 4 == 0, "a three-matching component is not a 4m-cycle")
        component_sizes.append(size)

    parts = tuple(sorted(size // 4 for size in component_sizes))
    require(sum(parts) == 6, "cycle parts do not form a partition of six")
    return parts


def transport_block_mod_7(
    adjacency: Sequence[Sequence[int]],
) -> list[list[int]]:
    """Build J-I-2A, congruent to 27I-9A+J modulo seven."""

    order = len(adjacency)
    require(order == 27 and all(len(row) == order for row in adjacency), "wrong block")
    return [
        [
            (1 - int(row == column) - 2 * adjacency[row][column]) % PRIME
            for column in range(order)
        ]
        for row in range(order)
    ]


def rank_mod_prime(matrix: Sequence[Sequence[int]], prime: int = PRIME) -> int:
    require(prime == 7, "verification field changed")
    work = [[entry % prime for entry in row] for row in matrix]
    rows = len(work)
    columns = len(work[0]) if rows else 0
    require(all(len(row) == columns for row in work), "ragged matrix")
    rank = 0
    for column in range(columns):
        pivot = next(
            (row for row in range(rank, rows) if work[row][column] != 0),
            None,
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        inverse = pow(work[rank][column], -1, prime)
        for other in range(column, columns):
            work[rank][other] = (work[rank][other] * inverse) % prime
        for row in range(rank + 1, rows):
            factor = work[row][column]
            if factor:
                for other in range(column, columns):
                    work[row][other] = (
                        work[row][other] - factor * work[rank][other]
                    ) % prime
        rank += 1
        if rank == rows:
            break
    return rank


def matrix_sha256(matrix: Sequence[Sequence[int]]) -> str:
    payload = b"".join(
        bytes(entry % PRIME for entry in row)
        for row in matrix
    )
    return hashlib.sha256(payload).hexdigest()


def rank_transfer_proof(*, scalar: int = 3, prime: int = 7) -> dict[str, Any]:
    """Record the linear-algebra proof of rank(M)=rank(NMN^T).

    From N^T N M=3M, N is injective on im(M).  Hence left multiplication by
    N preserves rank on every matrix whose columns lie in im(M), including M
    and MN^T.  Symmetry of M gives rank(MN^T)=rank(NM)=rank(M).
    """

    require(prime == 7, "rank-transfer field changed")
    require(scalar % prime != 0, "the injectivity scalar is not invertible")
    return {
        "premises": [
            "M is symmetric",
            "N^T N M = 3M",
            "3 is invertible in F_7",
        ],
        "injectivity": (
            "If v=Mw and Nv=0, then 0=N^T Nv=N^T N Mw=3Mw=3v, "
            "so v=0."
        ),
        "first_preservation": "rank(NM)=rank(M)",
        "right_preservation": (
            "rank(MN^T)=rank((MN^T)^T)=rank(NM)=rank(M), by symmetry of M"
        ),
        "second_preservation": (
            "columns of MN^T lie in im(M), so injectivity of N on im(M) "
            "gives rank(NMN^T)=rank(MN^T)"
        ),
        "conclusion": "rank_F7(M)=rank_F7(NMN^T)",
    }


@lru_cache(maxsize=1)
def exhaustive_census() -> dict[str, Any]:
    counts: Counter[tuple[int, ...]] = Counter()
    ranks_by_partition: dict[tuple[int, ...], set[int]] = defaultdict(set)
    representative_hash: dict[tuple[int, ...], str] = {}
    total = 0

    for matching in perfect_matchings(tuple(range(12))):
        adjacency = build_local_graph(matching)
        partition = cycle_partition(adjacency)
        block = transport_block_mod_7(adjacency)
        rank = rank_mod_prime(block)
        counts[partition] += 1
        ranks_by_partition[partition].add(rank)
        representative_hash.setdefault(partition, matrix_sha256(block))
        total += 1

    require(total == 10_395, "did not exhaust all (11)!! matchings")
    require(sum(counts.values()) == total, "partition census lost a matching")
    require(len(counts) == 11, "the eleven positive partitions of six are incomplete")

    table: list[dict[str, Any]] = []
    for partition in sorted(counts):
        ranks = sorted(ranks_by_partition[partition])
        require(len(ranks) == 1, f"rank is not partition-determined for {partition}")
        rank = ranks[0]
        even_parts = sum(part % 2 == 0 for part in partition)
        formula = 25 - 2 * even_parts
        require(rank == formula, f"rank formula fails for {partition}: {rank} != {formula}")
        table.append(
            {
                "partition": list(partition),
                "labelled_matching_count": counts[partition],
                "even_part_count": even_parts,
                "local_rank_F7": rank,
                "local_nullity_F7": 27 - rank,
                "contains_edge_prism": 1 in partition,
                "representative_block_sha256": representative_hash[partition],
            }
        )

    require(min(row["local_rank_F7"] for row in table) == 19, "rank floor changed")
    require(
        sum(row["labelled_matching_count"] for row in table) == 10_395,
        "table counts do not sum to (11)!!",
    )
    return {
        "normalization": (
            "Fix the X matching by relabelling X; pull Y labels through the "
            "cross matching; the remaining Y matching is arbitrary."
        ),
        "matching_count_formula": "11*9*7*5*3*1 = 10395",
        "pulled_back_matching_count": total,
        "normal_form_count": len(table),
        "normal_forms": table,
    }


def endpoint_arithmetic() -> dict[str, Any]:
    pairs = [
        [r3, r7]
        for r3 in range(12, 45)
        for r7 in range(19, 45)
        if (r3 + r7) % 2 == 0
    ]
    require(len(pairs) == 429, "updated rank-pair count changed")
    r3_twelve = [r7 for r3, r7 in pairs if r3 == 12]
    require(r3_twelve == list(range(20, 45, 2)), "r3=12 boundary changed")
    return {
        "premises": ["12<=r3<=44", "19<=r7<=44", "r3+r7 is even"],
        "count_derivation": "17*13 + 16*13 = 429",
        "admissible_pair_count": len(pairs),
        "if_r3_equals_12": {
            "r7_lower_bound": 20,
            "r7_parity": "even",
            "admissible_r7_values": r3_twelve,
        },
    }


def exact_record() -> dict[str, Any]:
    geometry = local_geometry()
    transfer = rank_transfer_proof()
    census = copy.deepcopy(exhaustive_census())
    endpoint_rows = [
        row for row in census["normal_forms"] if not row["contains_edge_prism"]
    ]
    endpoint_table = [
        {
            "partition": row["partition"],
            "local_rank_F7": row["local_rank_F7"],
        }
        for row in endpoint_rows
    ]
    require(
        endpoint_table
        == [
            {"partition": [2, 2, 2], "local_rank_F7": 19},
            {"partition": [2, 4], "local_rank_F7": 21},
            {"partition": [3, 3], "local_rank_F7": 25},
            {"partition": [6], "local_rank_F7": 23},
        ],
        "prism-free table changed",
    )

    return {
        "schema_version": 1,
        "role": "verifier",
        "claim_label": "VERIFIED",
        "scope": (
            "Universal edge-local characteristic-seven rank consequence for "
            "a hypothetical srg(99,14,1,2), with conditional prism-free "
            "endpoint refinements"
        ),
        "target_parameters": TARGET,
        "edge_local_geometry": geometry,
        "completeness": census,
        "transport": {
            "frozen_identity": "N M N^T = 27I - 9A + J",
            "modulo_seven_block": "27I-9A+J = J-I-2A in F_7",
            "rank_equality": transfer,
            "principal_block_inequality": (
                "rank_F7((NMN^T)[L,L]) <= rank_F7(NMN^T)=rank_F7(M)"
            ),
        },
        "verified_universal_result": {
            "rank_F7_M_lower_bound": 19,
            "proof": (
                "Every edge has one of the exhaustive local normal forms; "
                "each 27-point principal block has rank at least 19."
            ),
        },
        "conditional_prism_free_endpoint": {
            "condition": "n3=4158, equivalently no induced triangular prism",
            "part_one_equivalence": (
                "A part 1 is a 4-cycle in the three-matching union and, with "
                "xy, is exactly an induced triangular prism containing xy."
            ),
            "surviving_local_table": endpoint_table,
            "low_rank_edge_type_consequences": {
                "r7<=20": "every edge has type 2+2+2",
                "r7<=22": "every edge has type 2+2+2 or 2+4",
                "r7<=24": "no edge has type 3+3",
            },
            "rank_pair_arithmetic": endpoint_arithmetic(),
            "endpoint_excluded": False,
            "upper_bound_improved_below_4158": False,
        },
        "status": {
            "conway_99": "UNKNOWN",
            "endpoint": "UNKNOWN",
            "strongest_general_upper_bound_on_n3": 4158,
            "novelty": "UNKNOWN",
        },
        "limitations": [
            "This is a necessary rank condition, not a graph construction.",
            "No edge-type coupling theorem is proved.",
            "The prism-free endpoint is not excluded.",
            "The general upper bound remains n3<=4158.",
            "Literature novelty and priority are not certified.",
        ],
    }


def validate_record(record: dict[str, Any]) -> None:
    expected = exact_record()
    require(record == expected, "stored verifier result differs from independent regeneration")
    require(record["claim_label"] == "VERIFIED", "scoped verification status changed")
    require(
        record["conditional_prism_free_endpoint"]["endpoint_excluded"] is False,
        "endpoint status was inflated",
    )
    require(
        record["status"]["novelty"] == "UNKNOWN",
        "novelty status was inflated",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--output", type=Path)
    modes.add_argument("--verify", type=Path)
    args = parser.parse_args()

    record = exact_record()
    if args.verify:
        validate_record(load_json(args.verify))
        require(args.verify.read_bytes() == canonical_json(record), "JSON is not canonical")
        print(f"PASS: {args.verify} matches independent exhaustive regeneration")
        return 0
    output = args.output or DEFAULT_RESULT
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(canonical_json(record))
    print(f"WROTE: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
