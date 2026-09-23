#!/usr/bin/env python3
"""Clean-room verifier for every canonical Wave 43 rank-33 lift.

The frozen Wave 41 implementation is hash-bound as a protocol input but is
never imported.  Quotients, endpoint lifts, dense modular ranks, forced Gram
matrices, and all six-set candidate censuses are reconstructed independently.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
W41_CODE = ROOT / "attempts/wave41-allquotient-lifts/exact_check.py"
W41_MANIFEST = ROOT / "attempts/wave41-allquotient-lifts/package-manifest.sha256"
DISCOVERY = ROOT / "attempts/wave43-all-rank33-lifts/exact-results.json"
W41_CODE_SHA = "9a94a08dfec20a72c335168714a047f92e1aff09ac05bdd827a78ce2deb45e76"
W41_MANIFEST_SHA = "7b3ec7e2745e15f9d18e0439ebde72e289a9264cb81af364dd9bf29c4bae23ac"

Pairing = tuple[tuple[int, int], ...]
Quotient = tuple[tuple[int, ...], ...]
BASE_PAIRING: Pairing = ((0, 1), (2, 3), (4, 5))
RELATIVES: tuple[tuple[str, Pairing], ...] = (
    ("aligned_222", BASE_PAIRING),
    ("share_one_24", ((0, 1), (2, 4), (3, 5))),
    ("six_cycle_6", ((0, 2), (1, 4), (3, 5))),
)


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def strict_json(path: Path) -> dict[str, object]:
    def unique(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique)
    if not isinstance(value, dict):
        raise ValueError("JSON top level must be an object")
    return value


def all_matchings(items: tuple[int, ...]) -> Iterable[Pairing]:
    if not items:
        yield ()
        return
    first = items[0]
    for index in range(1, len(items)):
        rest = items[1:index] + items[index + 1 :]
        for tail in all_matchings(rest):
            yield tuple(sorted(((first, items[index]),) + tail))


PAIRINGS = tuple(sorted(set(all_matchings(tuple(range(6))))))


def quotient_graph(
    relative_name: str,
    final_left: Pairing,
    final_right: Pairing,
    block_map: Sequence[int],
) -> Quotient:
    graph = [set() for _ in range(18)]

    def squares(
        fibre_a: int, fibre_b: int, pairing_a: Pairing,
        pairing_b: Pairing, permutation: Sequence[int],
    ) -> None:
        for block_a, block_b in enumerate(permutation):
            for a in pairing_a[block_a]:
                for b in pairing_b[block_b]:
                    u, v = 6 * fibre_a + a, 6 * fibre_b + b
                    if v in graph[u]:
                        raise AssertionError("parallel quotient edge")
                    graph[u].add(v)
                    graph[v].add(u)

    relative = dict(RELATIVES)[relative_name]
    squares(0, 1, BASE_PAIRING, BASE_PAIRING, (0, 1, 2))
    squares(1, 2, relative, BASE_PAIRING, (0, 1, 2))
    squares(2, 0, final_left, final_right, block_map)
    if set(map(len, graph)) != {4}:
        raise AssertionError("quotient is not four-regular")
    return tuple(tuple(sorted(row)) for row in graph)


def modular_rank(matrix: Sequence[Sequence[int]] | np.ndarray, prime: int) -> int:
    rows = [[int(x) % prime for x in row] for row in matrix]
    rank = 0
    for column in range(len(rows[0])):
        pivot = next((r for r in range(rank, len(rows)) if rows[r][column]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = pow(rows[rank][column], -1, prime)
        rows[rank] = [(scale * x) % prime for x in rows[rank]]
        for row in range(len(rows)):
            if row == rank:
                continue
            factor = rows[row][column]
            if factor:
                rows[row] = [
                    (left - factor * right) % prime
                    for left, right in zip(rows[row], rows[rank])
                ]
        rank += 1
        if rank == len(rows):
            break
    return rank


def quotient_rank(graph: Quotient) -> int:
    matrix = [[int(v in graph[u]) for v in range(18)] for u in range(18)]
    for i in range(18):
        matrix[i][i] = 2
    return modular_rank(matrix, 3)


def enumerate_canonical() -> tuple[Quotient, dict[str, object], dict[int, int]]:
    distribution: Counter[int] = Counter()
    rank11: list[tuple[dict[str, object], Quotient]] = []
    index = 0
    for relative, _ in RELATIVES:
        for left in PAIRINGS:
            for right in PAIRINGS:
                for block_map in itertools.permutations(range(3)):
                    graph = quotient_graph(relative, left, right, block_map)
                    rank = quotient_rank(graph)
                    distribution[rank] += 1
                    if rank == 11:
                        rank11.append(({
                            "normalized_index": index, "relative_orbit": relative,
                            "fibre2_pairing": [list(x) for x in left],
                            "fibre0_pairing": [list(x) for x in right],
                            "block_permutation": list(block_map),
                        }, graph))
                    index += 1
    expected = {11: 8, 12: 1, 13: 400, 14: 46, 15: 2616, 16: 979}
    if index != 4050 or dict(sorted(distribution.items())) != expected or len(rank11) != 8:
        raise ValueError("independent quotient census mismatch")
    return rank11[0][1], rank11[0][0], expected


def half_edge_rules(graph: Quotient) -> dict[tuple[int, int], tuple[int, int]]:
    rules: dict[tuple[int, int], tuple[int, int]] = {}
    for vertex, neighbors in enumerate(graph):
        other_fibres = sorted({neighbor // 6 for neighbor in neighbors})
        if len(other_fibres) != 2:
            raise AssertionError("bad quotient fibre degree")
        for coefficient, fibre in enumerate(other_fibres):
            selected = sorted(n for n in neighbors if n // 6 == fibre)
            if len(selected) != 2:
                raise AssertionError("bad quotient bidegree")
            for constant, neighbor in enumerate(selected):
                rules[(vertex, neighbor)] = (constant, coefficient)
    return rules


def forbidden_triangle_assignments(
    graph: Quotient,
) -> tuple[tuple[tuple[int, int], ...], ...]:
    rules = half_edge_rules(graph)
    clauses: list[tuple[tuple[int, int], ...]] = []
    for a, b, c in itertools.combinations(range(18), 3):
        if b not in graph[a] or c not in graph[a] or c not in graph[b]:
            continue
        requirement: list[tuple[int, int]] = []
        for vertex, left, right in ((a, b, c), (b, a, c), (c, a, b)):
            const_l, coeff_l = rules[(vertex, left)]
            const_r, coeff_r = rules[(vertex, right)]
            if coeff_l == coeff_r:
                raise AssertionError("triangle does not use both other fibres")
            requirement.append((vertex, const_l ^ const_r))
        clauses.append(tuple(requirement))
    if len(clauses) != 16:
        raise ValueError(f"canonical quotient has {len(clauses)} triangles, not 16")
    return tuple(clauses)


def triangle_free_masks(graph: Quotient) -> np.ndarray:
    masks = np.arange(1 << 18, dtype=np.uint32)
    allowed = np.ones(len(masks), dtype=bool)
    for clause in forbidden_triangle_assignments(graph):
        forbidden = np.ones(len(masks), dtype=bool)
        for variable, value in clause:
            forbidden &= ((masks >> variable) & 1) == value
        allowed &= ~forbidden
    result = masks[allowed]
    if len(result) != 37_378:
        raise ValueError("triangle-free mask count mismatch")
    return result


def lift_matrices(graph: Quotient, masks: np.ndarray) -> np.ndarray:
    batch = len(masks)
    matrices = np.zeros((batch, 36, 36), dtype=np.int16)
    diagonal = np.arange(36)
    matrices[:, diagonal, diagonal] = 3
    for pair in range(18):
        u, v = 2 * pair, 2 * pair + 1
        matrices[:, u, v] = matrices[:, v, u] = 6
    rules = half_edge_rules(graph)
    batch_index = np.arange(batch)
    for left in range(18):
        for right in graph[left]:
            if left >= right:
                continue
            lc, la = rules[(left, right)]
            rc, ra = rules[(right, left)]
            lu = lc ^ (((masks >> left) & 1) if la else np.zeros(batch, dtype=np.uint32))
            rv = rc ^ (((masks >> right) & 1) if ra else np.zeros(batch, dtype=np.uint32))
            u = 2 * left + lu.astype(np.int16)
            v = 2 * right + rv.astype(np.int16)
            matrices[batch_index, u, v] = 6
            matrices[batch_index, v, u] = 6
    return matrices


def batched_rank_mod7(matrices: np.ndarray) -> np.ndarray:
    work = matrices.copy()
    batch, size, _ = work.shape
    ranks = np.zeros(batch, dtype=np.int16)
    inverses = np.array([0, 1, 4, 5, 2, 3, 6], dtype=np.int16)
    offsets = np.arange(size, dtype=np.int16)
    for column in range(size):
        rows = ranks[:, None] + offsets[None, :]
        valid = rows < size
        clipped = np.minimum(rows, size - 1)
        values = work[np.arange(batch)[:, None], clipped, column]
        choices = valid & (values != 0)
        has = choices.any(axis=1)
        if not has.any():
            continue
        first = choices.argmax(axis=1)
        pivot = ranks + first
        selected = np.flatnonzero(has)
        target_rows = ranks[selected].copy()
        pivot_rows = pivot[selected].copy()
        saved = work[selected, target_rows, :].copy()
        work[selected, target_rows, :] = work[selected, pivot_rows, :]
        work[selected, pivot_rows, :] = saved
        scale = inverses[work[selected, target_rows, column]]
        work[selected, target_rows, :] = (
            work[selected, target_rows, :] * scale[:, None]
        ) % 7
        pivot_vectors = work[selected, target_rows, :].copy()
        factors = work[selected, :, column].copy()
        factors[np.arange(len(selected)), target_rows] = 0
        work[selected] = (
            work[selected] - factors[:, :, None] * pivot_vectors[:, None, :]
        ) % 7
        ranks[selected] += 1
    return ranks


def independent_rank33_masks(graph: Quotient) -> tuple[list[int], dict[int, int]]:
    allowed = triangle_free_masks(graph)
    distribution: Counter[int] = Counter()
    selected: list[int] = []
    chunk = 256
    for start in range(0, len(allowed), chunk):
        masks = allowed[start:start + chunk]
        ranks = batched_rank_mod7(lift_matrices(graph, masks))
        for mask, rank in zip(masks.tolist(), ranks.tolist()):
            distribution[int(rank)] += 1
            if rank == 32:
                selected.append(int(mask))
    expected = {32: 264, 33: 7348, 34: 29766}
    if dict(sorted(distribution.items())) != expected:
        raise ValueError(f"dense lift-rank distribution mismatch: {distribution}")
    return selected, expected


def lift_adjacency(graph: Quotient, mask: int) -> np.ndarray:
    adjacency = np.zeros((36, 36), dtype=np.int64)
    for pair in range(18):
        adjacency[2 * pair, 2 * pair + 1] = 1
        adjacency[2 * pair + 1, 2 * pair] = 1
    rules = half_edge_rules(graph)
    for left in range(18):
        for right in graph[left]:
            if left >= right:
                continue
            lc, la = rules[(left, right)]
            rc, ra = rules[(right, left)]
            u = 2 * left + (lc ^ (((mask >> left) & 1) if la else 0))
            v = 2 * right + (rc ^ (((mask >> right) & 1) if ra else 0))
            adjacency[u, v] = adjacency[v, u] = 1
    if set(adjacency.sum(axis=1).tolist()) != {3}:
        raise AssertionError("lift not cubic")
    return adjacency


def components(adjacency: np.ndarray) -> tuple[tuple[int, ...], ...]:
    unseen = set(range(36))
    result: list[tuple[int, ...]] = []
    while unseen:
        todo = [min(unseen)]
        seen = set(todo)
        while todo:
            vertex = todo.pop()
            for neighbor in np.flatnonzero(adjacency[vertex]):
                if int(neighbor) not in seen:
                    seen.add(int(neighbor))
                    todo.append(int(neighbor))
        unseen -= seen
        result.append(tuple(sorted(seen)))
    return tuple(sorted(result, key=lambda part: (len(part), part)))


def forced_gram(adjacency: np.ndarray) -> np.ndarray:
    same_fibre = np.fromfunction(lambda i, j: (i // 12) == (j // 12), (36, 36), dtype=int)
    return (
        12 * np.eye(36, dtype=np.int64) - adjacency + 2
        - same_fibre.astype(np.int64) - adjacency @ adjacency
    )


def component_record(component: Sequence[int], gram: np.ndarray) -> dict[str, object]:
    indicator = np.zeros(36, dtype=np.int64)
    indicator[list(component)] = 1
    size = len(component)
    first = 10 * size
    second = int(indicator @ gram @ indicator)
    return {
        "size": size,
        "fibre_balance": [
            sum(vertex // 12 == fibre for vertex in component) for fibre in range(3)
        ],
        "intersection_first_moment": first,
        "intersection_second_moment": second,
        "cauchy_floor": (first * first + 59) // 60,
        "cauchy_equality": second * 60 == first * first,
        "forced_integer_intersection": first // 60 if first % 60 == 0 else None,
    }


TRIPLE_I, TRIPLE_J, TRIPLE_K = np.indices((60, 60, 60), dtype=np.int16).reshape(3, -1)


def legal_pairs(fibre: int, gram: np.ndarray) -> np.ndarray:
    start = 12 * fibre
    pairs = [
        pair for pair in itertools.combinations(range(start, start + 12), 2)
        if int(gram[pair]) == 1
    ]
    if len(pairs) != 60:
        raise ValueError("legal-pair count differs from 60")
    return np.asarray(pairs, dtype=np.int16)


def cross_table(left: np.ndarray, right: np.ndarray, gram: np.ndarray) -> np.ndarray:
    table = np.ones((len(left), len(right)), dtype=bool)
    for a in range(2):
        for b in range(2):
            table &= gram[left[:, a, None], right[None, :, b]] > 0
    return table


def candidate_census(
    adjacency: np.ndarray, gram: np.ndarray, small: frozenset[int]
) -> dict[str, object]:
    pairs = tuple(legal_pairs(fibre, gram) for fibre in range(3))
    c01 = cross_table(pairs[0], pairs[1], gram)
    c02 = cross_table(pairs[0], pairs[2], gram)
    c12 = cross_table(pairs[1], pairs[2], gram)
    support = c01[TRIPLE_I, TRIPLE_J] & c02[TRIPLE_I, TRIPLE_K] & c12[TRIPLE_J, TRIPLE_K]
    support_count = int(support.sum())
    small_counts = tuple(
        np.array([sum(int(v) in small for v in pair) for pair in fibre_pairs], dtype=np.int8)
        for fibre_pairs in pairs
    )
    component_ok = support & (
        small_counts[0][TRIPLE_I] + small_counts[1][TRIPLE_J]
        + small_counts[2][TRIPLE_K] == 2
    )
    chosen = np.flatnonzero(component_ok)
    component_count = int(len(chosen))
    pair_masks = tuple(
        np.array([(1 << int(a)) | (1 << int(b)) for a, b in fibre_pairs], dtype=np.uint64)
        for fibre_pairs in pairs
    )
    block_masks = (
        pair_masks[0][TRIPLE_I[chosen]] | pair_masks[1][TRIPLE_J[chosen]]
        | pair_masks[2][TRIPLE_K[chosen]]
    )
    mixed_ok = np.ones(len(chosen), dtype=bool)
    neighbor_masks = np.array([
        sum(1 << int(v) for v in np.flatnonzero(adjacency[u])) for u in range(36)
    ], dtype=np.uint64)
    for vertex in range(36):
        neighbor_count = np.bitwise_count(block_masks & neighbor_masks[vertex])
        selected_vertex = ((block_masks >> np.uint64(vertex)) & np.uint64(1)).astype(bool)
        mixed_ok &= neighbor_count <= np.where(selected_vertex, 1, 2)
    survivors = chosen[mixed_ok]
    patterns: Counter[tuple[int, int, int]] = Counter(
        zip(
            small_counts[0][TRIPLE_I[survivors]].tolist(),
            small_counts[1][TRIPLE_J[survivors]].tolist(),
            small_counts[2][TRIPLE_K[survivors]].tolist(),
        )
    )
    return {
        "raw_pair_triples": 216000,
        "gram_support_legal": support_count,
        "after_forced_component_equality": component_count,
        "after_mixed_BH_nonnegativity": int(len(survivors)),
        "mixed_legal_by_component_pattern": {
            str(pattern): count for pattern, count in sorted(patterns.items())
        },
    }


def four_cycles(adjacency: np.ndarray) -> int:
    common = adjacency @ adjacency
    opposite = sum(
        int(common[u, v]) * (int(common[u, v]) - 1) // 2
        for u, v in itertools.combinations(range(36), 2)
    )
    if opposite % 2:
        raise AssertionError("four-cycle parity failed")
    return opposite // 2


def per_mask_record(graph: Quotient, mask: int) -> dict[str, object]:
    adjacency = lift_adjacency(graph, mask)
    gram = forced_gram(adjacency)
    parts = components(adjacency)
    records = [component_record(part, gram) for part in parts]
    small = frozenset(parts[0])
    kernel = [
        [int(v // 12 == 0) - int(v // 12 == 1) for v in range(36)],
        [int(v // 12 == 0) - int(v // 12 == 2) for v in range(36)],
        [2 if v in small else -1 for v in range(36)],
    ]
    if modular_rank(kernel, 1_000_003) != 3:
        raise AssertionError("structural kernel vectors dependent")
    for vector in kernel:
        if np.any(gram @ np.asarray(vector, dtype=np.int64)):
            raise AssertionError("structural kernel vector failed over integers")
    gram_rank = modular_rank(gram, 1_000_003)
    distribution = Counter(int(x) for x in gram.reshape(-1))
    return {
        "mask": mask,
        "component_sizes": [len(part) for part in parts],
        "component_fibre_balances": [
            [sum(v // 12 == fibre for v in part) for fibre in range(3)]
            for part in parts
        ],
        "component_moments": records,
        "four_cycle_count": four_cycles(adjacency),
        "forced_gram_minimum": int(gram.min()),
        "forced_gram_entry_distribution": {
            str(value): count for value, count in sorted(distribution.items())
        },
        "forced_gram_rank_mod_1000003": gram_rank,
        "structural_kernel_dimension": 3,
        "candidate_census": candidate_census(adjacency, gram, small),
    }


def compute() -> dict[str, object]:
    if sha256(W41_CODE.read_bytes()) != W41_CODE_SHA:
        raise ValueError("frozen Wave 41 source hash mismatch")
    if sha256(W41_MANIFEST.read_bytes()) != W41_MANIFEST_SHA:
        raise ValueError("frozen Wave 41 manifest hash mismatch")
    graph, metadata, quotient_distribution = enumerate_canonical()
    masks, lift_distribution = independent_rank33_masks(graph)
    records = [per_mask_record(graph, mask) for mask in masks]
    discovery = strict_json(DISCOVERY)
    discovery_hash = sha256(DISCOVERY.read_bytes())
    exact_per_mask = records == discovery.get("per_mask")
    result = {
        "format": "wave43-all-rank33-lifts-independent-v1",
        "role": "verifier",
        "claim_label": "VERIFIED_SCOPED",
        "scope": "all 264 canonical triangle-free rank-33 lifts under n3=4158, r3=12, and all edges type 222",
        "inputs": {
            "wave41_source_sha256": W41_CODE_SHA,
            "wave41_manifest_sha256": W41_MANIFEST_SHA,
            "discovery_result_sha256": discovery_hash,
        },
        "canonical_quotient": {
            "metadata": metadata,
            "rank_distribution_all_4050": {str(k): v for k, v in quotient_distribution.items()},
            "triangle_count": len(forbidden_triangle_assignments(graph)),
        },
        "lift_census": {
            "all_masks": 262144, "triangle_free_masks": 37378,
            "rank_F7_3I_minus_A_distribution": {str(k): v for k, v in lift_distribution.items()},
            "rank33_mask_count": len(masks), "rank33_masks": masks,
            "rank33_masks_sha256": sha256(canonical(masks)),
        },
        "per_mask": records,
        "comparison": {
            "rank33_masks_exact_match": masks == discovery.get("rank33_masks"),
            "rank33_mask_hash_exact_match": sha256(canonical(masks)) == discovery.get("rank33_masks_sha256"),
            "all_264_per_mask_records_exact_match": exact_per_mask,
        },
        "aggregate": {
            "component_partitions": dict(Counter(str(tuple(x["component_sizes"])) for x in records)),
            "component_fibre_balances": dict(Counter(str(tuple(tuple(y) for y in x["component_fibre_balances"])) for x in records)),
            "gram_minima": dict(Counter(str(x["forced_gram_minimum"]) for x in records)),
            "gram_ranks": dict(Counter(str(x["forced_gram_rank_mod_1000003"]) for x in records)),
            "candidate_census": dict(Counter(str((
                x["candidate_census"]["gram_support_legal"],
                x["candidate_census"]["after_forced_component_equality"],
                x["candidate_census"]["after_mixed_BH_nonnegativity"],
            )) for x in records)),
        },
        "status_wall": {
            "every_lift_survives_necessary_filters": True,
            "full_B": "UNKNOWN", "compatible_H": "UNKNOWN",
            "endpoint_excluded": False, "strict_upper_bound": "NOT_PROVED",
            "conway_99": "UNKNOWN", "automorphism_assumed": False,
        },
        "limitations": [
            "The result is conditional on n3=4158, r3=12, all edges type 222, and the canonical rank-33 lift lane.",
            "The 264 masks are labelled cases; five numerical census rows are not asserted to be isomorphism classes.",
            "Necessary six-set filters do not construct a simultaneous 60-column B or compatible outside graph H.",
            "No endpoint exclusion, strict upper bound, graph, or Conway-99 solution follows.",
        ],
    }
    validate(result)
    return result


def validate(value: dict[str, object]) -> None:
    quotient = value["canonical_quotient"]
    if quotient["metadata"] != {
        "normalized_index": 1446, "relative_orbit": "share_one_24",
        "fibre2_pairing": [[0, 1], [2, 4], [3, 5]],
        "fibre0_pairing": [[0, 1], [2, 4], [3, 5]],
        "block_permutation": [0, 1, 2],
    }:
        raise ValueError("canonical quotient metadata mismatch")
    lift = value["lift_census"]
    if lift["rank33_mask_count"] != 264 or lift["rank33_masks_sha256"] != "167ba5c0a4b40fb3711fbc861a03a853a125651f4c569dfd5688dd0cca90b130":
        raise ValueError("rank-33 mask regeneration mismatch")
    if not all(value["comparison"].values()):
        raise ValueError(f"discovery comparison failed: {value['comparison']}")
    expected = {
        "(118718, 49736, 45032)": 48,
        "(131908, 54560, 49328)": 48,
        "(132196, 54736, 49520)": 24,
        "(132250, 54560, 49328)": 48,
        "(132402, 54648, 49424)": 96,
    }
    if value["aggregate"]["candidate_census"] != expected:
        raise ValueError("candidate-census distribution mismatch")
    wall = value["status_wall"]
    if wall["endpoint_excluded"] or wall["strict_upper_bound"] != "NOT_PROVED" or wall["conway_99"] != "UNKNOWN" or wall["automorphism_assumed"]:
        raise ValueError("status wall inflation")


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--output", type=Path)
    group.add_argument("--verify", type=Path)
    args = parser.parse_args()
    observed = compute()
    payload = canonical(observed)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(payload)
    else:
        expected = strict_json(args.verify)
        validate(expected)
        if payload != canonical(expected):
            raise ValueError("live rank-33 replay differs from archived result")
    print("PASS: 264 clean-room rank-33 lift records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
