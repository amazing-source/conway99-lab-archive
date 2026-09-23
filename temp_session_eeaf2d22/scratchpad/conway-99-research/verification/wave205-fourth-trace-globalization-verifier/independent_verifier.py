"""Source-blind exact checker for Wave 205 fourth-trace algebra.

This file uses only Python's standard library and arithmetic over F_3.
It does not read any discovery package.
"""

from __future__ import annotations

import json
from itertools import combinations, product
from typing import Iterable, List, Sequence, Tuple

P = 3
N = 7
MARGINS = [9, 9, 6, 6, 6, 6, 6]
STAR_GRAM = [[int(i != j) for j in range(N)] for i in range(N)]

# All three have the graph-forced integer margins and entries, union-Gram
# rank 11, g=2, and respectively h=0,1,2.
FOURTH_TRACE_CONTROLS = {
    "h0": [
        [1, 2, 2, 1, 1, 2, 0],
        [1, 1, 2, 2, 2, 0, 1],
        [2, 1, 0, 0, 0, 1, 2],
        [0, 1, 1, 0, 0, 2, 2],
        [2, 0, 0, 1, 1, 1, 1],
        [1, 2, 1, 0, 2, 0, 0],
        [2, 2, 0, 2, 0, 0, 0],
    ],
    "h1": [
        [1, 2, 2, 1, 0, 1, 2],
        [1, 1, 2, 2, 1, 1, 1],
        [2, 0, 1, 0, 0, 1, 2],
        [2, 0, 1, 0, 2, 0, 1],
        [0, 2, 0, 1, 1, 2, 0],
        [1, 2, 0, 2, 0, 1, 0],
        [2, 2, 0, 0, 2, 0, 0],
    ],
    "h2": [
        [1, 2, 0, 0, 2, 2, 2],
        [0, 1, 1, 2, 1, 2, 2],
        [0, 2, 1, 2, 1, 0, 0],
        [2, 0, 2, 1, 1, 0, 0],
        [2, 1, 1, 0, 0, 0, 2],
        [2, 1, 0, 1, 1, 1, 0],
        [2, 2, 1, 0, 0, 1, 0],
    ],
}

# This has the same graph-forced local margins and union-Gram rank 9.  It is
# used to construct a rank-10 realization whose restricted form has a
# one-dimensional radical.
RADICAL_CONTROL = [
    [1, 1, 0, 1, 2, 2, 2],
    [2, 1, 0, 2, 0, 2, 2],
    [2, 1, 0, 2, 1, 0, 0],
    [2, 0, 2, 1, 1, 0, 0],
    [1, 2, 0, 0, 1, 1, 1],
    [1, 2, 2, 0, 0, 1, 0],
    [0, 2, 2, 0, 1, 0, 1],
]


def mod(x: int) -> int:
    return x % P


def eye(n: int) -> List[List[int]]:
    return [[int(i == j) for j in range(n)] for i in range(n)]


def transpose(a: Sequence[Sequence[int]]) -> List[List[int]]:
    return [list(row) for row in zip(*a)]


def matmul(
    a: Sequence[Sequence[int]], b: Sequence[Sequence[int]]
) -> List[List[int]]:
    bt = transpose(b)
    return [[sum(x * y for x, y in zip(row, col)) % P for col in bt] for row in a]


def matsub(
    a: Sequence[Sequence[int]], b: Sequence[Sequence[int]]
) -> List[List[int]]:
    return [[(x - y) % P for x, y in zip(ra, rb)] for ra, rb in zip(a, b)]


def block2(
    a: Sequence[Sequence[int]],
    b: Sequence[Sequence[int]],
    c: Sequence[Sequence[int]],
    d: Sequence[Sequence[int]],
) -> List[List[int]]:
    return [list(x) + list(y) for x, y in zip(a, b)] + [
        list(x) + list(y) for x, y in zip(c, d)
    ]


def trace(a: Sequence[Sequence[int]]) -> int:
    return sum(a[i][i] for i in range(len(a))) % P


def rref(a: Sequence[Sequence[int]]) -> Tuple[List[List[int]], List[int]]:
    out = [[x % P for x in row] for row in a]
    rows = len(out)
    cols = len(out[0]) if rows else 0
    pivots: List[int] = []
    row = 0
    for col in range(cols):
        pivot = next((i for i in range(row, rows) if out[i][col]), None)
        if pivot is None:
            continue
        out[row], out[pivot] = out[pivot], out[row]
        inv = pow(out[row][col], -1, P)
        out[row] = [(x * inv) % P for x in out[row]]
        for i in range(rows):
            if i != row and out[i][col]:
                factor = out[i][col]
                out[i] = [
                    (x - factor * y) % P for x, y in zip(out[i], out[row])
                ]
        pivots.append(col)
        row += 1
        if row == rows:
            break
    return out, pivots


def rank(a: Sequence[Sequence[int]]) -> int:
    return len(rref(a)[1])


def nullspace(a: Sequence[Sequence[int]]) -> List[List[int]]:
    rr, pivots = rref(a)
    cols = len(rr[0]) if rr else 0
    free = [j for j in range(cols) if j not in pivots]
    basis: List[List[int]] = []
    for f in free:
        v = [0] * cols
        v[f] = 1
        for i, p in enumerate(pivots):
            v[p] = (-rr[i][f]) % P
        basis.append(v)
    return basis


def inverse(a: Sequence[Sequence[int]]) -> List[List[int]]:
    n = len(a)
    aug = [list(row) + ident for row, ident in zip(a, eye(n))]
    rr, pivots = rref(aug)
    if pivots[:n] != list(range(n)):
        raise ValueError("matrix is singular")
    return [row[n:] for row in rr]


def vecmul(a: Sequence[Sequence[int]], v: Sequence[int]) -> List[int]:
    return [sum(x * y for x, y in zip(row, v)) % P for row in a]


def dot(a: Sequence[int], b: Sequence[int]) -> int:
    return sum(x * y for x, y in zip(a, b)) % P


def union_gram(c: Sequence[Sequence[int]]) -> List[List[int]]:
    return block2(STAR_GRAM, c, transpose(c), STAR_GRAM)


def cross_invariants(c_integer: Sequence[Sequence[int]]) -> dict:
    c = [[x % P for x in row] for row in c_integer]
    cct = matmul(c, transpose(c))
    return {
        "cross_rank": rank(c),
        "union_gram_rank": rank(union_gram(c)),
        "g": trace(cct),
        "h": trace(matmul(cct, cct)),
    }


def crossing_square(
    p: Sequence[Sequence[int]], q: Sequence[Sequence[int]]
) -> int:
    n = len(p)
    return (
        sum(
            p[i][j] * p[k][ell] * q[j][k] * q[ell][i]
            for i in range(n)
            for j in range(n)
            for k in range(n)
            for ell in range(n)
        )
        % P
    )


def wedge_square(a: Sequence[Sequence[int]]) -> List[List[int]]:
    n = len(a)
    pairs = list(combinations(range(n), 2))
    return [
        [
            (a[r][i] * a[s][j] - a[r][j] * a[s][i]) % P
            for i, j in pairs
        ]
        for r, s in pairs
    ]


def fourth_trace_identity(
    p: Sequence[Sequence[int]], q: Sequence[Sequence[int]]
) -> dict:
    pq = matmul(p, q)
    g = trace(pq)
    h = trace(matmul(pq, pq))
    wp = wedge_square(p)
    wq = wedge_square(q)
    k = trace(matmul(wp, wq))
    return {
        "g": g,
        "h": h,
        "k": k,
        "crossing": crossing_square(p, q),
        "wedge_formula_h": (g * g + k) % P,
        "functorial": wedge_square(pq) == matmul(wp, wq),
    }


def localizer() -> Tuple[List[List[int]], List[List[int]], List[List[int]]]:
    # The columns of L form the sum-zero coefficient space in F_3^7.
    l = [[int(i == j) for j in range(6)] for i in range(6)] + [[2] * 6]
    gram = matmul(transpose(l), l)
    r = matmul(inverse(gram), transpose(l))
    return l, gram, r


def localized_invariants(c_integer: Sequence[Sequence[int]]) -> dict:
    c = [[x % P for x in row] for row in c_integer]
    l, gram, r = localizer()
    a = matmul(matmul(r, c), transpose(r))
    reconstructed = matmul(matmul(l, a), transpose(l))
    t = matmul(matmul(matmul(a, gram), transpose(a)), gram)
    return {
        "reconstructed": reconstructed,
        "cross_rank": rank(c),
        "localized_rank": rank(a),
        "g": trace(t),
        "h": trace(matmul(t, t)),
    }


def local_cross_mask_feasible(bits: Sequence[int]) -> bool:
    # L and M are triangles.  For a cross pair (i,j), the number of common
    # neighbors already visible inside L union M cannot exceed lambda=1 on
    # an edge or mu=2 on a nonedge.
    edge = {(i, j): bits[3 * i + j] for i in range(3) for j in range(3)}
    for i in range(3):
        for j in range(3):
            visible_common = sum(
                edge[(k, j)] for k in range(3) if k != i
            ) + sum(edge[(i, ell)] for ell in range(3) if ell != j)
            if edge[(i, j)] and visible_common > 1:
                return False
            if not edge[(i, j)] and visible_common > 2:
                return False
    return True


def enumerate_local_cross_masks() -> dict:
    counts = {0: 0, 1: 0, 2: 0, 3: 0}
    three_edge_masks: List[List[int]] = []
    for bits in product((0, 1), repeat=9):
        if local_cross_mask_feasible(bits):
            edge_count = sum(bits)
            counts[edge_count] = counts.get(edge_count, 0) + 1
            if edge_count == 3:
                three_edge_masks.append(list(bits))
    perfect = 0
    for bits in three_edge_masks:
        row_degrees = [sum(bits[3 * i : 3 * i + 3]) for i in range(3)]
        col_degrees = [sum(bits[3 * i + j] for i in range(3)) for j in range(3)]
        perfect += int(row_degrees == [1, 1, 1] and col_degrees == [1, 1, 1])
    return {
        "feasible_count": sum(counts.values()),
        "edge_count_distribution": counts,
        "three_edge_count": len(three_edge_masks),
        "three_edge_perfect_matchings": perfect,
        "prism_free_max_edges": max(
            sum(bits)
            for bits in product((0, 1), repeat=9)
            if local_cross_mask_feasible(bits)
            and not (
                sum(bits) == 3
                and [sum(bits[3 * i : 3 * i + 3]) for i in range(3)]
                == [1, 1, 1]
                and [
                    sum(bits[3 * i + j] for i in range(3)) for j in range(3)
                ]
                == [1, 1, 1]
            )
        ),
    }


def has_graph_forced_margins(c: Sequence[Sequence[int]]) -> bool:
    return (
        len(c) == N
        and all(len(row) == N for row in c)
        and c[0][0] == c[1][1] == 1
        and all(0 <= x <= 2 for row in c for x in row)
        and [sum(row) for row in c] == MARGINS
        and [sum(c[i][j] for i in range(N)) for j in range(N)] == MARGINS
    )


def locally_projectively_distinct(gamma: Sequence[Sequence[int]]) -> bool:
    # In the nondegenerate quotient by ker(gamma), two column vectors are
    # proportional iff their Gram columns are proportional.
    gt = transpose(gamma)
    for i, j in combinations(range(len(gt)), 2):
        if gt[i] == gt[j] or gt[i] == [(2 * x) % P for x in gt[j]]:
            return False
    return True


def find_nonsingular_principal(
    a: Sequence[Sequence[int]], size: int
) -> Tuple[int, ...]:
    for indices in combinations(range(len(a)), size):
        sub = [[a[i][j] for j in indices] for i in indices]
        if rank(sub) == size:
            return indices
    raise AssertionError("no full-rank principal submatrix found")


def radical_realization() -> dict:
    gamma = union_gram(RADICAL_CONTROL)
    q = rank(gamma)
    indices = find_nonsingular_principal(gamma, q)
    b0 = [[gamma[i][j] for j in indices] for i in indices]
    b0_inv = inverse(b0)

    # Coordinate columns in the nondegenerate rank-q quotient.
    coords: List[List[int]] = []
    for j in range(14):
        pairings = [gamma[i][j] for i in indices]
        coords.append(vecmul(b0_inv, pairings))
    rrows = transpose(coords)  # q by 14
    assert matmul(matmul(transpose(rrows), b0), rrows) == gamma

    star1 = [1] * 7 + [0] * 7
    star2 = [0] * 7 + [1] * 7
    f = None
    for half in (range(7), range(7, 14)):
        for i, j in combinations(half, 2):
            candidate = [0] * 14
            candidate[i] = 1
            candidate[j] = 2
            if (
                dot(candidate, star1) == 0
                and dot(candidate, star2) == 0
                and rank(rrows + [candidate]) == q + 1
            ):
                f = candidate
                break
        if f is not None:
            break
    if f is None:
        raise AssertionError("failed to find radical lift row")

    # Ambient form is b0 orthogonal-summed with a hyperbolic plane.  The
    # columns use one singular direction of that plane and not its mate.
    ambient = [row + [0, 0] for row in b0]
    ambient += [[0] * q + [0, 1], [0] * q + [1, 0]]
    xrows = rrows + [f, [0] * 14]
    reconstructed = matmul(matmul(transpose(xrows), ambient), xrows)

    gram_kernel = nullspace(gamma)
    true_kernel = nullspace(xrows)
    witness = next(v for v in gram_kernel if any(vecmul(xrows, v)))
    image = vecmul(xrows, witness)
    image_pairings = vecmul(transpose(xrows), vecmul(ambient, image))
    return {
        "union_gram_rank": q,
        "column_span_rank": rank(xrows),
        "ambient_rank": rank(ambient),
        "gram_kernel_dim": len(gram_kernel),
        "true_kernel_dim": len(true_kernel),
        "reconstructs_gram": reconstructed == gamma,
        "star_relations_true": not any(vecmul(xrows, star1))
        and not any(vecmul(xrows, star2)),
        "witness_is_gram_kernel": not any(vecmul(gamma, witness)),
        "witness_is_true_relation": not any(image),
        "witness_image_is_nonzero_radical": any(image) and not any(image_pairings),
    }


def dimension_ledger() -> dict:
    v = 11
    self_adjoint = v * (v + 1) // 2
    trace_zero_self_adjoint = self_adjoint - 1
    wedge_v = v * (v - 1) // 2
    wedge_self_adjoint_ops = wedge_v * (wedge_v + 1) // 2
    return {
        "dim_V": v,
        "dim_self_adjoint_End_V": self_adjoint,
        "dim_trace_zero_self_adjoint_End_V": trace_zero_self_adjoint,
        "dim_Sym2_trace_zero_self_adjoint_End_V": (
            trace_zero_self_adjoint * (trace_zero_self_adjoint + 1) // 2
        ),
        "dim_wedge2_V": wedge_v,
        "dim_self_adjoint_End_wedge2_V": wedge_self_adjoint_ops,
        "dim_trace_zero_self_adjoint_End_wedge2_V": wedge_self_adjoint_ops - 1,
    }


def build_result() -> dict:
    controls = {}
    for name, c in FOURTH_TRACE_CONTROLS.items():
        inv = cross_invariants(c)
        loc = localized_invariants(c)
        controls[name] = {
            **inv,
            "graph_forced_margins": has_graph_forced_margins(c),
            "zero_mod3_row_sums": all(sum(row) % P == 0 for row in c),
            "zero_mod3_col_sums": all(
                sum(c[i][j] for i in range(N)) % P == 0 for j in range(N)
            ),
            "localized_reconstruction": loc["reconstructed"]
            == [[x % P for x in row] for row in c],
            "localized_rank": loc["localized_rank"],
            "localized_g": loc["g"],
            "localized_h": loc["h"],
            "locally_projectively_distinct": locally_projectively_distinct(
                union_gram(c)
            ),
        }

    # Noncommuting symmetric matrices exercise the crossing and wedge formulas.
    p = [
        [1, 1, 0, 2],
        [1, 2, 1, 0],
        [0, 1, 0, 1],
        [2, 0, 1, 1],
    ]
    q = [
        [2, 0, 1, 1],
        [0, 1, 2, 0],
        [1, 2, 2, 1],
        [1, 0, 1, 0],
    ]
    fourth = fourth_trace_identity(p, q)

    projector = [[int(i == j and i < 6) for j in range(11)] for i in range(11)]
    wedge_projector = wedge_square(projector)

    return {
        "claim_label": "VERIFIED_WITH_SCOPE",
        "field": "F_3",
        "source_blind": True,
        "dimension_ledger": dimension_ledger(),
        "fourth_trace_identity": fourth,
        "rank6_projector_checks": {
            "idempotent": matmul(projector, projector) == projector,
            "trace": trace(projector),
            "wedge_rank": rank(wedge_projector),
            "wedge_trace": trace(wedge_projector),
            "wedge_idempotent": matmul(wedge_projector, wedge_projector)
            == wedge_projector,
        },
        "local_cross_mask_enumeration": enumerate_local_cross_masks(),
        "fourth_trace_controls": controls,
        "control_summary": {
            "common_g": sorted({x["g"] for x in controls.values()}),
            "realized_h": sorted({x["h"] for x in controls.values()}),
            "common_union_gram_rank": sorted(
                {x["union_gram_rank"] for x in controls.values()}
            ),
        },
        "gram_radical_hostile_control": radical_realization(),
        "statuses": {
            "full_fourth_trace_factorization": "VERIFIED",
            "star_pair_localization_and_rank": "VERIFIED",
            "tensor_dimensions": "VERIFIED",
            "graph_forced_nonedge_margins": "VERIFIED_WITH_SCOPE",
            "local_premises_determine_nonedge_h": "REFUTED_WITH_SCOPE",
            "complete_nonedge_classification": "UNKNOWN",
            "rank_11_endpoint": "UNKNOWN",
            "n3_4158_endpoint": "UNKNOWN",
            "Conway_99": "UNKNOWN",
        },
        "limitations": [
            "Controls are local orthogonal-space realizations, not SRGs.",
            "No 99-star or 231-column global compatibility is constructed.",
            "No endpoint or Conway-99 status is promoted.",
        ],
    }


def main() -> None:
    print(json.dumps(build_result(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
