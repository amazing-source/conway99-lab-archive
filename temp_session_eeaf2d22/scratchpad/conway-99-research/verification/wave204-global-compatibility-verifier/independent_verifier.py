#!/usr/bin/env python3
"""Independent, exact Wave204 V1/V2/V3 verifier.

This file was written and frozen before opening the submitted Wave204 sources.
It intentionally reconstructs only the scoped models in BLIND_PROTOCOL.md.
"""

from __future__ import annotations

import copy
import hashlib
import json
from itertools import combinations
from pathlib import Path
from typing import Any


MOD = 3
HERE = Path(__file__).resolve().parent


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        + "\n"
    ).encode("ascii")


def sha256_value(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def vadd(x: list[int], y: list[int]) -> list[int]:
    return [(a + b) % MOD for a, b in zip(x, y)]


def vsub(x: list[int], y: list[int]) -> list[int]:
    return [(a - b) % MOD for a, b in zip(x, y)]


def vscale(a: int, x: list[int]) -> list[int]:
    return [(a * b) % MOD for b in x]


def zero_vector(n: int) -> list[int]:
    return [0] * n


def transpose(a: list[list[int]]) -> list[list[int]]:
    return [list(row) for row in zip(*a)]


def identity(n: int) -> list[list[int]]:
    return [[int(i == j) for j in range(n)] for i in range(n)]


def mat_add(a: list[list[int]], b: list[list[int]]) -> list[list[int]]:
    return [
        [(a[i][j] + b[i][j]) % MOD for j in range(len(a[0]))]
        for i in range(len(a))
    ]


def mat_sub(a: list[list[int]], b: list[list[int]]) -> list[list[int]]:
    return [
        [(a[i][j] - b[i][j]) % MOD for j in range(len(a[0]))]
        for i in range(len(a))
    ]


def mat_mul(a: list[list[int]], b: list[list[int]]) -> list[list[int]]:
    assert a and b and len(a[0]) == len(b)
    return [
        [
            sum(a[i][k] * b[k][j] for k in range(len(b))) % MOD
            for j in range(len(b[0]))
        ]
        for i in range(len(a))
    ]


def trace(a: list[list[int]]) -> int:
    return sum(a[i][i] for i in range(len(a))) % MOD


def matrix_rank(a: list[list[int]]) -> int:
    m = [row[:] for row in a]
    rows = len(m)
    cols = len(m[0]) if rows else 0
    rank = 0
    for col in range(cols):
        pivot = next((r for r in range(rank, rows) if m[r][col] % MOD), None)
        if pivot is None:
            continue
        m[rank], m[pivot] = m[pivot], m[rank]
        scale = pow(m[rank][col] % MOD, -1, MOD)
        m[rank] = [(scale * value) % MOD for value in m[rank]]
        for row in range(rows):
            if row == rank or not m[row][col] % MOD:
                continue
            factor = m[row][col] % MOD
            m[row] = [
                (m[row][j] - factor * m[rank][j]) % MOD
                for j in range(cols)
            ]
        rank += 1
    return rank


def matrix_inverse(a: list[list[int]]) -> list[list[int]]:
    n = len(a)
    if n == 0 or any(len(row) != n for row in a):
        raise ValueError("matrix is not nonempty square")
    m = [
        [value % MOD for value in row] + identity(n)[i]
        for i, row in enumerate(a)
    ]
    for col in range(n):
        pivot = next((r for r in range(col, n) if m[r][col] % MOD), None)
        if pivot is None:
            raise ValueError("singular matrix")
        m[col], m[pivot] = m[pivot], m[col]
        scale = pow(m[col][col] % MOD, -1, MOD)
        m[col] = [(scale * value) % MOD for value in m[col]]
        for row in range(n):
            if row == col or not m[row][col] % MOD:
                continue
            factor = m[row][col] % MOD
            m[row] = [
                (m[row][j] - factor * m[col][j]) % MOD
                for j in range(2 * n)
            ]
    return [row[n:] for row in m]


def determinant(a: list[list[int]]) -> int:
    n = len(a)
    m = [row[:] for row in a]
    det = 1
    for col in range(n):
        pivot = next((r for r in range(col, n) if m[r][col] % MOD), None)
        if pivot is None:
            return 0
        if pivot != col:
            m[col], m[pivot] = m[pivot], m[col]
            det = -det
        pivot_value = m[col][col] % MOD
        det = (det * pivot_value) % MOD
        inv_pivot = pow(pivot_value, -1, MOD)
        for row in range(col + 1, n):
            if not m[row][col] % MOD:
                continue
            factor = m[row][col] * inv_pivot % MOD
            for j in range(col, n):
                m[row][j] = (m[row][j] - factor * m[col][j]) % MOD
    return det % MOD


def bilinear(x: list[int], gram: list[list[int]], y: list[int]) -> int:
    return mat_mul([x], mat_mul(gram, transpose([y])))[0][0]


def build_v1_model() -> dict[str, Any]:
    n = 99
    edges: list[list[int]] = []
    for center in range(n):
        for offset in range(1, 8):
            other = (center + offset) % n
            edges.append([min(center, other), max(center, other)])
    edges = sorted({tuple(edge) for edge in edges})

    triple_template = [[1, 2, 3]]
    triple_template.extend(
        [0, a, b]
        for a, b in combinations(range(1, 7), 2)
        if {a, b} & {1, 2, 3}
    )
    triple_template = sorted(triple_template)

    degree_blocks: dict[str, list[list[int]]] = {}
    pair_fibers: dict[str, list[dict[str, Any]]] = {}
    all_vertices = set(range(n))
    edge_set = set(edges)
    for center in range(n):
        blocks = [
            sorted([(center - offset) % n, (center + offset) % n])
            for offset in range(1, 8)
        ]
        degree_blocks[str(center)] = blocks
        graph_neighbors = {
            v for v in range(n) if tuple(sorted((center, v))) in edge_set
        }
        complement_neighbors = sorted(all_vertices - graph_neighbors - {center})
        fiber_keys = [
            (left, right, leaf_value)
            for left, right in combinations(range(7), 2)
            for leaf_value in range(4)
        ]
        pair_fibers[str(center)] = [
            {
                "block_pair": [left, right],
                "leaf_value": leaf_value,
                "leaf": leaf,
            }
            for (left, right, leaf_value), leaf in zip(
                fiber_keys, complement_neighbors, strict=True
            )
        ]

    q = 237
    nonprivate_labels = []
    for label in range(q):
        primary = label // 3
        occurrences = [primary, (primary + 1 + (label % 19)) % n]
        if label >= 234:
            occurrences.append((primary + 40) % n)
        nonprivate_labels.append(
            {
                "label": label,
                "multiplicity": len(occurrences),
                "occurrence_centers": occurrences,
                "orientation_a": [0, 1, 2],
                "orientation_b": [2, 1, 0],
            }
        )

    oriented_centers = {
        str(center): ([3 * center + i for i in range(3)] if center < 79 else [])
        for center in range(n)
    }

    slot_rows: list[dict[str, Any]] = []
    cursor = 0
    for kind, count, width in (("n3", 1200, 3), ("p3", 3123, 4)):
        for index in range(count):
            positions = list(range(cursor, cursor + width))
            cursor += width
            slot_rows.append(
                {
                    "kind": kind,
                    "index": index,
                    "positions": positions,
                }
            )

    return {
        "schema": "wave204-independent-relaxed-expanded-v1",
        "centers": list(range(n)),
        "degree_edges": [list(edge) for edge in edges],
        "degree_blocks": degree_blocks,
        "pair_fibers": pair_fibers,
        "triple_families": {
            str(center): copy.deepcopy(triple_template) for center in range(n)
        },
        "aggregate": {
            "universe_size": 3360,
            "J": 3561,
            "delta": 3,
            "n3": 1200,
            "p3": 3123,
            "q": q,
            "epsilon": 708,
            "L": 0,
            "b": 0,
        },
        "nonprivate_labels": nonprivate_labels,
        "oriented_centers": oriented_centers,
        "slot_rows": slot_rows,
    }


def verify_v1(model: dict[str, Any] | None = None) -> dict[str, Any]:
    model = build_v1_model() if model is None else model
    n = 99
    assert model["centers"] == list(range(n))

    edges = [tuple(edge) for edge in model["degree_edges"]]
    assert len(edges) == len(set(edges)) == n * 14 // 2
    degrees = [0] * n
    neighbors = [set() for _ in range(n)]
    for left, right in edges:
        assert 0 <= left < right < n
        degrees[left] += 1
        degrees[right] += 1
        neighbors[left].add(right)
        neighbors[right].add(left)
    assert set(degrees) == {14}
    complement_degrees = [n - 1 - degree for degree in degrees]
    assert set(complement_degrees) == {84}

    for center in range(n):
        blocks = model["degree_blocks"][str(center)]
        assert len(blocks) == 7
        flattened = [v for block in blocks for v in block]
        assert len(flattened) == len(set(flattened)) == 14
        assert set(flattened) == neighbors[center]

        fibers = model["pair_fibers"][str(center)]
        assert len(fibers) == 84
        by_pair: dict[tuple[int, int], list[int]] = {}
        leaves = []
        for record in fibers:
            pair = tuple(record["block_pair"])
            assert len(pair) == 2 and pair[0] < pair[1]
            assert 0 <= record["leaf_value"] < 4
            by_pair.setdefault(pair, []).append(record["leaf_value"])
            leaves.append(record["leaf"])
        assert set(by_pair) == set(combinations(range(7), 2))
        assert all(sorted(values) == [0, 1, 2, 3] for values in by_pair.values())
        assert len(leaves) == len(set(leaves)) == 84
        assert set(leaves) == set(range(n)) - neighbors[center] - {center}

        triples = [set(triple) for triple in model["triple_families"][str(center)]]
        assert len(triples) == 13
        assert len({tuple(sorted(triple)) for triple in triples}) == 13
        assert all(len(triple) == 3 and triple <= set(range(7)) for triple in triples)
        assert all(a & b for a, b in combinations(triples, 2))
        assert not set.intersection(*triples)

    aggregate = model["aggregate"]
    expected = {
        "universe_size": 3360,
        "J": 3561,
        "delta": 3,
        "n3": 1200,
        "p3": 3123,
        "q": 237,
        "epsilon": 708,
        "L": 0,
        "b": 0,
    }
    assert aggregate == expected
    assert aggregate["L"] == (
        aggregate["delta"] - 3 * aggregate["q"] + aggregate["epsilon"]
    )
    assert aggregate["J"] == 3 * aggregate["n3"] - 13 * aggregate["delta"]

    labels = model["nonprivate_labels"]
    assert len(labels) == aggregate["q"]
    multiplicity_histogram = {2: 0, 3: 0}
    max_combined_occupancy = 0
    full_occupancy_count = 0
    for expected_label, label in enumerate(labels):
        assert label["label"] == expected_label
        occurrences = label["occurrence_centers"]
        assert label["multiplicity"] == len(occurrences)
        assert len(occurrences) == len(set(occurrences))
        assert all(0 <= center < n for center in occurrences)
        multiplicity_histogram[len(occurrences)] += 1
        for orientation in ("orientation_a", "orientation_b"):
            image = label[orientation]
            assert len(image) == len(set(image))
            assert set(image) <= set(range(5))
        combined = set(label["orientation_a"]) | set(label["orientation_b"])
        max_combined_occupancy = max(max_combined_occupancy, len(combined))
        full_occupancy_count += int(len(combined) == 5)
    assert multiplicity_histogram == {2: 234, 3: 3}
    assert max_combined_occupancy == 3
    assert full_occupancy_count == aggregate["b"] == 0

    oriented = model["oriented_centers"]
    assert len(oriented) == n
    assert sum(len(labels_here) == 3 for labels_here in oriented.values()) == 79
    assert sum(len(labels_here) == 0 for labels_here in oriented.values()) == 20
    oriented_labels = [label for values in oriented.values() for label in values]
    assert sorted(oriented_labels) == list(range(aggregate["q"]))

    carrier_positions = 5 * aggregate["universe_size"]
    used_positions: list[int] = []
    row_histogram = {"n3": 0, "p3": 0}
    for row in model["slot_rows"]:
        expected_width = 3 if row["kind"] == "n3" else 4
        assert len(row["positions"]) == expected_width
        assert len(set(row["positions"])) == expected_width
        assert all(0 <= position < carrier_positions for position in row["positions"])
        row_histogram[row["kind"]] += 1
        used_positions.extend(row["positions"])
    assert row_histogram == {"n3": 1200, "p3": 3123}
    assert len(used_positions) == len(set(used_positions))
    deficit = carrier_positions - len(used_positions)
    assert deficit == 708
    assert deficit == 5 * aggregate["universe_size"] - (
        3 * aggregate["n3"] + 4 * aggregate["p3"]
    )

    return {
        "claim_label": "VERIFIED_SCOPED_RELAXED",
        "centers": n,
        "degree": 14,
        "complement_degree": 84,
        "degree_edges": len(edges),
        "local_triples_per_center": 13,
        "leaf_values_per_pair": 4,
        "nonprivate_multiplicity_histogram": {"2": 234, "3": 3},
        "max_combined_two_orientation_occupancy": max_combined_occupancy,
        "slot_deficit": deficit,
        "expanded_model_sha256": sha256_value(model),
    }


def build_simplex(sign: int = 1) -> list[list[int]]:
    total = [1 if i < 7 else 0 for i in range(11)]
    vectors = []
    for i in range(7):
        basis = [0] * 11
        basis[i] = 1
        vectors.append(vscale(sign, vsub(basis, total)))
    return vectors


def build_v2_model() -> dict[str, Any]:
    form = identity(11)
    form[10][10] = 2
    plus = build_simplex(1)
    minus = build_simplex(2)
    sign_patterns = {
        3: [1, 1, 2],
        4: [1, 1, 1, 2],
        5: [1, 1, 1, 2, 2],
    }
    cycles = []
    for length, signs in sign_patterns.items():
        blocks = [
            {
                "block": f"cycle-{length}-block-{i}",
                "sign": sign,
                "columns": plus if sign == 1 else minus,
            }
            for i, sign in enumerate(signs)
        ]
        cycles.append(
            {
                "length": length,
                "blocks": blocks,
                "arrows": [
                    {
                        "source": i,
                        "target": (i + 1) % length,
                        "partial_injection": {"0": 0},
                    }
                    for i in range(length)
                ],
                "incoming_leaf_slot": 0,
                "next_outgoing_third_block_slot": 1,
            }
        )
    return {
        "schema": "wave204-independent-coboundary-control-v2",
        "form": form,
        "simplex_plus": plus,
        "simplex_minus": minus,
        "cycles": cycles,
        "extensions": {
            "identity": [0, 1, 2, 3, 4],
            "transposition_1_2": [0, 2, 1, 3, 4],
        },
    }


def verify_v2(model: dict[str, Any] | None = None) -> dict[str, Any]:
    model = build_v2_model() if model is None else model
    form = model["form"]
    assert len(form) == 11 and all(len(row) == 11 for row in form)
    assert determinant(form) == 2
    assert {x * x % MOD for x in range(1, MOD)} == {1}

    plus = model["simplex_plus"]
    minus = model["simplex_minus"]
    assert len(plus) == len(minus) == 7
    assert len({tuple(vector) for vector in plus}) == 7
    assert len({tuple(vector) for vector in minus}) == 7
    assert {tuple(vector) for vector in plus}.isdisjoint(
        {tuple(vector) for vector in minus}
    )
    assert minus == [vscale(2, vector) for vector in plus]
    for simplex in (plus, minus):
        assert [sum(column[i] for column in simplex) % MOD for i in range(11)] == [
            0
        ] * 11
        for i, column in enumerate(simplex):
            assert bilinear(column, form, column) == 0
            for j, other in enumerate(simplex):
                if i != j:
                    assert bilinear(column, form, other) == 2

    cycle_results = []
    for cycle in model["cycles"]:
        length = cycle["length"]
        assert length in {3, 4, 5}
        assert len(cycle["blocks"]) == len(cycle["arrows"]) == length
        assert {block["sign"] for block in cycle["blocks"]} == {1, 2}
        for arrow in cycle["arrows"]:
            assert arrow["partial_injection"] == {"0": 0}
            assert arrow["target"] == (arrow["source"] + 1) % length

        true_sums = []
        for slot in range(7):
            total = zero_vector(11)
            for arrow in cycle["arrows"]:
                source = cycle["blocks"][arrow["source"]]["columns"][slot]
                target = cycle["blocks"][arrow["target"]]["columns"][slot]
                total = vadd(total, vsub(target, source))
            assert total == zero_vector(11)
            true_sums.append(total)

        incoming = cycle["incoming_leaf_slot"]
        outgoing = cycle["next_outgoing_third_block_slot"]
        assert incoming == 0 and outgoing == 1 and incoming != outgoing
        projected = zero_vector(11)
        for arrow in cycle["arrows"]:
            source = cycle["blocks"][arrow["source"]]["columns"][outgoing]
            target = cycle["blocks"][arrow["target"]]["columns"][incoming]
            projected = vadd(projected, vsub(target, source))
        assert projected != zero_vector(11)
        cycle_results.append(
            {
                "length": length,
                "true_fixed_column_sum": true_sums[0],
                "projected_nonmatching_defect": projected,
            }
        )

    extensions = model["extensions"]
    identity_extension = extensions["identity"]
    transposition_extension = extensions["transposition_1_2"]
    assert sorted(identity_extension) == list(range(5))
    assert sorted(transposition_extension) == list(range(5))
    assert identity_extension[0] == transposition_extension[0] == 0
    assert identity_extension != transposition_extension

    return {
        "coboundary_claim_label": "VERIFIED",
        "edgewise_chaining_implication": "REFUTED_WITH_SCOPE",
        "determined_total_S5_implication": "REFUTED_WITH_SCOPE",
        "global_relevance_label": "CANDIDATE_ONLY",
        "form_determinant": determinant(form),
        "simplex_count": 2,
        "b": 0,
        "cycles": cycle_results,
        "partial_extension_count_exhibited": 2,
        "model_sha256": sha256_value(model),
    }


def build_cycle_biadjacency(parts: list[int]) -> list[list[int]]:
    size = sum(parts)
    n = [[0 for _ in range(size)] for _ in range(size)]
    start = 0
    for length in parts:
        for i in range(length):
            n[start + i][start + i] = 1
            n[start + i][start + ((i + 1) % length)] = 1
        start += length
    return n


Y_WITNESS_1 = [
    [0, 2, 0, 1, 1, 1],
    [2, 0, 0, 2, 0, 2],
    [1, 2, 1, 0, 1, 2],
    [0, 0, 2, 1, 1, 2],
    [1, 2, 0, 0, 0, 2],
    [0, 0, 1, 2, 0, 2],
    [0, 1, 1, 2, 1, 0],
    [1, 2, 1, 1, 2, 0],
    [1, 2, 0, 2, 1, 2],
    [0, 2, 0, 1, 2, 0],
    [0, 2, 2, 1, 2, 2],
]

Y_WITNESS_2 = [
    [1, 2, 1, 0, 1, 0],
    [2, 1, 2, 0, 0, 2],
    [1, 2, 1, 2, 2, 0],
    [1, 1, 0, 0, 2, 1],
    [1, 0, 2, 2, 0, 2],
    [2, 2, 2, 2, 2, 1],
    [0, 0, 2, 2, 1, 0],
    [1, 2, 2, 1, 2, 1],
    [1, 0, 0, 1, 2, 1],
    [1, 0, 0, 1, 0, 0],
    [2, 2, 1, 1, 2, 0],
]


def orthogonal_projector(
    columns: list[list[int]], form: list[list[int]]
) -> list[list[int]]:
    gram = mat_mul(transpose(columns), mat_mul(form, columns))
    gram_inverse = matrix_inverse(gram)
    return mat_mul(mat_mul(columns, gram_inverse), mat_mul(transpose(columns), form))


def intersection_dimension(
    left: list[list[int]], right: list[list[int]]
) -> int:
    concatenated = [left[i] + right[i] for i in range(len(left))]
    return matrix_rank(left) + matrix_rank(right) - matrix_rank(concatenated)


def verify_v3(
    expected_h: dict[tuple[int, ...], int] | None = None,
    witnesses: tuple[list[list[int]], list[list[int]]] | None = None,
) -> dict[str, Any]:
    expected_h = expected_h or {
        (6,): 0,
        (4, 2): 1,
        (3, 3): 0,
        (2, 2, 2): 0,
    }
    witnesses = witnesses or (Y_WITNESS_1, Y_WITNESS_2)

    j6 = [[1] * 6 for _ in range(6)]
    g = mat_sub(j6, identity(6))
    h_inverse = matrix_inverse(g)
    assert mat_mul(g, h_inverse) == identity(6)

    local_results = []
    for parts in ([6], [4, 2], [3, 3], [2, 2, 2]):
        n = build_cycle_biadjacency(parts)
        assert all(sum(row) == 2 for row in n)
        assert all(sum(row) == 2 for row in transpose(n))
        c = mat_add(j6, n)
        compression = mat_mul(
            mat_mul(mat_mul(h_inverse, c), h_inverse), transpose(c)
        )
        nn_t = mat_mul(n, transpose(n))
        assert compression == nn_t
        pair_trace = trace(nn_t)
        fourth_trace = trace(mat_mul(nn_t, nn_t))
        assert pair_trace == 0
        assert fourth_trace == expected_h[tuple(parts)]
        inv_two = pow(2, -1, MOD)
        wedge_trace = (
            (pair_trace * pair_trace - fourth_trace) * inv_two
        ) % MOD
        symmetric_trace = (
            (pair_trace * pair_trace + fourth_trace) * inv_two
        ) % MOD
        assert wedge_trace == fourth_trace
        assert symmetric_trace == 2 * fourth_trace % MOD
        local_results.append(
            {
                "cycle_half_lengths": parts,
                "pair_trace": pair_trace,
                "h": fourth_trace,
                "wedge2_trace": wedge_trace,
                "sym2_trace": symmetric_trace,
            }
        )

    form = identity(11)
    form[10][10] = 2
    p = [[0] * 11 for _ in range(11)]
    for i in range(6):
        p[i][i] = 1
    u = [[int(i == j) for j in range(6)] for i in range(11)]
    witness_results = []
    for y in witnesses:
        assert len(y) == 11 and all(len(row) == 6 for row in y)
        assert matrix_rank(y) == 6
        y_gram = mat_mul(transpose(y), mat_mul(form, y))
        assert determinant(y_gram) != 0
        q = orthogonal_projector(y, form)
        assert mat_mul(q, q) == q
        assert matrix_rank(q) == 6
        assert mat_mul(transpose(q), form) == mat_mul(form, q)
        pq = mat_mul(p, q)
        pair_trace = trace(pq)
        fourth_trace = trace(mat_mul(pq, pq))
        dimension = intersection_dimension(u, y)
        assert pair_trace == 0
        assert dimension == 1
        witness_results.append(
            {
                "pair_trace": pair_trace,
                "intersection_dimension": dimension,
                "fourth_trace": fourth_trace,
                "span_sha256": sha256_value(y),
                "projector_sha256": sha256_value(q),
            }
        )
    assert [item["fourth_trace"] for item in witness_results] == [2, 0]

    return {
        "local_detector_claim_label": "VERIFIED",
        "pair_trace_intersection_determines_h": "REFUTED_WITH_SCOPE",
        "local_cycle_types": local_results,
        "rank11_counterexample": witness_results,
        "global_controls_label": "NOT_TESTED_PRE_SOURCE",
    }


def run_all() -> dict[str, Any]:
    with (HERE / "certificate_parameters.json").open(
        "r", encoding="utf-8", newline=""
    ) as handle:
        parameters = json.load(handle)
    return {
        "schema": "wave204-independent-source-blind-result-v1",
        "parameters_sha256": sha256_value(parameters),
        "v1": verify_v1(),
        "v2": verify_v2(),
        "v3": verify_v3(),
        "limitations": [
            "V1 is only the explicitly formalized relaxed certificate semantics.",
            "V2 controls omit 99 stars, 231 columns, global frame, SRG incidence, cover totals, and endpoint realization.",
            "V3 local identities are conditional on the stated Gram blocks.",
            "No submitted Wave204 source was used to construct this result.",
        ],
    }


def main() -> None:
    print(json.dumps(run_all(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

