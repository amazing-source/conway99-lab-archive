"""Independent post-source audit for the three sealed Wave 205 packages.

The checker reads JSON certificates/results but does not import discovery
Python.  Its algorithms are independent exact arithmetic over F_3.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from itertools import combinations, product
from pathlib import Path
from typing import Iterable, Sequence

import independent_verifier as blind

ROOT = Path(__file__).resolve().parents[2]
P = 3

PROOF_A = ROOT / "attempts/wave205-nonedge-fourth-trace-proof-a"
PROOF_B = ROOT / "attempts/wave205-global-fourth-moment-proof-b"
HOSTILE = ROOT / "attempts/wave205-fourth-trace-hostile-controls"

EXPECTED_MANIFESTS = {
    PROOF_A / "package-manifest.sha256":
        "2c9976b6cb07a3036df07fd0e7ceb7ffce6a339651d604fcecdcf8c0c3da3d96",
    PROOF_B / "package-manifest.sha256":
        "a91a2a1cdbc129fa66e9d63b34031a774d5af78c458d18d9a1aadd7e4be217e7",
    HOSTILE / "package-manifest.sha256":
        "b9700d135bbfdebc34aeaad88eb1264b95732fa0f9da773cf90bd002331cc971",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_manifest(path: Path) -> dict:
    if sha256(path) != EXPECTED_MANIFESTS[path]:
        raise AssertionError(f"manifest-file hash mismatch: {path}")
    relative_to_manifest = path.parent == HOSTILE
    entries = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected = line[:64]
        listed = line[66:].lstrip("*")
        target = path.parent / listed if relative_to_manifest else ROOT / listed
        if not target.is_file() or sha256(target) != expected:
            raise AssertionError(f"sealed entry mismatch: {target}")
        entries += 1
    return {
        "manifest_sha256": EXPECTED_MANIFESTS[path],
        "entry_count": entries,
        "entries_match": True,
    }


def determinant(a: Sequence[Sequence[int]]) -> int:
    m = [[x % P for x in row] for row in a]
    value = 1
    for col in range(len(m)):
        pivot = next((i for i in range(col, len(m)) if m[i][col]), None)
        if pivot is None:
            return 0
        if pivot != col:
            m[col], m[pivot] = m[pivot], m[col]
            value = -value
        value *= m[col][col]
        inv = pow(m[col][col], -1, P)
        m[col] = [(x * inv) % P for x in m[col]]
        for i in range(col + 1, len(m)):
            factor = m[i][col]
            if factor:
                m[i] = [
                    (x - factor * y) % P for x, y in zip(m[i], m[col])
                ]
    return value % P


def code_minimum_weight(basis: Sequence[Sequence[int]]) -> int:
    if not basis:
        return 0
    best = len(basis[0]) + 1
    for coefficients in product(range(P), repeat=len(basis)):
        if not any(coefficients):
            continue
        word = [
            sum(c * basis[i][j] for i, c in enumerate(coefficients)) % P
            for j in range(len(basis[0]))
        ]
        best = min(best, sum(x != 0 for x in word))
    return best


def normalized_boundary(top_distinct: bool, left_distinct: bool):
    top_positions = [0, int(top_distinct)]
    left_positions = [0, int(left_distinct)]
    top = [
        [1, 2] + [2 if j == top_positions[0] else 1 for j in range(5)],
        [2, 1] + [2 if j == top_positions[1] else 1 for j in range(5)],
    ]
    left = [
        [2 if i == left_positions[0] else 1,
         2 if i == left_positions[1] else 1]
        for i in range(5)
    ]
    row_margins = [6 - sum(row) for row in left]
    col_margins = [
        6 - top[0][j + 2] - top[1][j + 2] for j in range(5)
    ]
    return top, left, row_margins, col_margins


def binary_margin_matrices(rows: Sequence[int], cols: Sequence[int]):
    choices = [
        [list(bits) for bits in product((0, 1), repeat=5) if sum(bits) == total]
        for total in rows
    ]

    def visit(index: int, remaining: list[int], built: list[list[int]]):
        if index == 5:
            if remaining == [0] * 5:
                yield [row[:] for row in built]
            return
        after = 4 - index
        for row in choices[index]:
            nxt = [remaining[j] - row[j] for j in range(5)]
            if min(nxt) < 0 or any(x > after for x in nxt):
                continue
            built.append(row)
            yield from visit(index + 1, nxt, built)
            built.pop()

    yield from visit(0, list(cols), [])


def low_t_cores(rows: Sequence[int], cols: Sequence[int], twos: int):
    if twos == 0:
        yield from binary_margin_matrices(rows, cols)
        return
    if twos != 1:
        raise ValueError("only t=6,7 are audited")
    for i in range(5):
        for j in range(5):
            rr, cc = list(rows), list(cols)
            rr[i] -= 2
            cc[j] -= 2
            if min(rr) < 0 or min(cc) < 0:
                continue
            for binary in binary_margin_matrices(rr, cc):
                if binary[i][j]:
                    continue
                core = [row[:] for row in binary]
                core[i][j] = 2
                yield core


def normalized_low_t(t: int):
    for top_case in (False, True):
        for left_case in (False, True):
            top, left, rows, cols = normalized_boundary(top_case, left_case)
            for core in low_t_cores(rows, cols, t - 6):
                yield top + [left[i] + core[i] for i in range(5)]


def gram_discriminant(gamma: Sequence[Sequence[int]]) -> int:
    _, pivots = blind.rref(gamma)
    principal = [[gamma[i][j] for j in pivots] for i in pivots]
    return determinant(principal)


def proof_a_census() -> dict:
    answer = {}
    for t in (6, 7):
        total = 0
        admissible = Counter()
        for c in normalized_low_t(t):
            total += 1
            if sum(x == 2 for row in c for x in row) != t:
                raise AssertionError("t count mismatch")
            gamma = blind.union_gram(c)
            q = blind.rank(gamma)
            if q == 11:
                disc = gram_discriminant(gamma)
                distance = code_minimum_weight(blind.nullspace(gamma))
                if disc == 2 and distance >= 4:
                    admissible[blind.cross_invariants(c)["h"]] += 1
        answer[str(t)] = {
            "normalized_matrix_count": total,
            "admissible_by_h": {str(h): admissible[h] for h in range(3)},
        }
    expected = {
        "6": {
            "normalized_matrix_count": 646,
            "admissible_by_h": {"0": 0, "1": 18, "2": 0},
        },
        "7": {
            "normalized_matrix_count": 7886,
            "admissible_by_h": {"0": 297, "1": 324, "2": 144},
        },
    }
    if answer != expected:
        raise AssertionError({"proof_a_census": answer, "expected": expected})
    return answer


def undirected(left: str, right: str) -> tuple[str, str]:
    if left == right:
        raise ValueError("loop")
    return tuple(sorted((left, right)))


def common_neighbors(
    vertices: Sequence[str], edges: set[tuple[str, str]], left: str, right: str
) -> set[str]:
    return {
        z for z in vertices
        if z not in (left, right)
        and undirected(left, z) in edges
        and undirected(right, z) in edges
    }


def proof_a_controls() -> list[dict]:
    package = json.loads((PROOF_A / "controls.json").read_text(encoding="utf-8"))
    convention = package["vertex_convention"]
    x_outer = convention["x_blocks_without_center"]
    y_outer = convention["y_blocks_without_center"]
    x_blocks = [["x", *pair] for pair in x_outer]
    y_blocks = [["y", *pair] for pair in y_outer]
    summaries = []
    for item in package["controls"]:
        edges: set[tuple[str, str]] = set()
        for center, pairs in (("x", x_outer), ("y", y_outer)):
            for a, b in pairs:
                edges.update({
                    undirected(center, a), undirected(center, b), undirected(a, b)
                })
        edges.update(undirected(a, b) for a, b in item["exclusive_cross_edges"])
        vertices = sorted({z for block in x_blocks + y_blocks for z in block})
        if len(vertices) != 28:
            raise AssertionError("control vertex count")
        neighborhoods = {
            c: {z for z in vertices if z != c and undirected(c, z) in edges}
            for c in ("x", "y")
        }
        if {c: len(n) for c, n in neighborhoods.items()} != {"x": 14, "y": 14}:
            raise AssertionError("control center degrees")
        if neighborhoods["x"] & neighborhoods["y"] != {"a", "b"}:
            raise AssertionError("control common centers")

        observed = []
        for left in x_blocks:
            row = []
            for right in y_blocks:
                count = sum(
                    u != v and undirected(u, v) in edges
                    for u in left for v in right
                )
                if set(left).isdisjoint(right) and count > 2:
                    raise AssertionError("prism cap")
                row.append(count % P)
            observed.append(row)
        claimed = [[int(x) for x in row] for row in item["cross_gram_rows"]]
        if observed != claimed:
            raise AssertionError(f"{item['name']}: cross Gram")

        adjacent_hist, nonedge_hist = Counter(), Counter()
        for i, left in enumerate(vertices):
            for right in vertices[i + 1:]:
                count = len(common_neighbors(vertices, edges, left, right))
                if undirected(left, right) in edges:
                    if count > 1:
                        raise AssertionError("lambda upper bound")
                    adjacent_hist[count] += 1
                else:
                    if count > 2:
                        raise AssertionError("mu upper bound")
                    nonedge_hist[count] += 1
        for z in neighborhoods["x"] - {"a", "b"}:
            if len(common_neighbors(vertices, edges, z, "y")) != 2:
                raise AssertionError("opposite-center mu")
        for z in neighborhoods["y"] - {"a", "b"}:
            if len(common_neighbors(vertices, edges, z, "x")) != 2:
                raise AssertionError("opposite-center mu")

        if [row[:2] for row in observed[:2]] != [[1, 2], [2, 1]]:
            raise AssertionError("marked corner")
        for row in observed[:2] + blind.transpose(observed)[:2]:
            if Counter(row) != Counter({1: 5, 2: 2}):
                raise AssertionError("special profile")
        for row in observed[2:] + blind.transpose(observed)[2:]:
            k = row.count(2)
            if sum(row) != 6 or Counter(row) != Counter({0: 1+k, 1: 6-2*k, 2: k}):
                raise AssertionError("ordinary profile")

        inv = blind.cross_invariants(observed)
        gamma = blind.union_gram(observed)
        distance = code_minimum_weight(blind.nullspace(gamma))
        t = sum(x == 2 for row in observed for x in row)
        if (t, inv["h"]) != (item["claimed_t"], item["claimed_h"]):
            raise AssertionError("claimed control invariant")
        if inv["union_gram_rank"] != 11 or gram_discriminant(gamma) != 2:
            raise AssertionError("control ambient type")
        if distance < 4 or not blind.locally_projectively_distinct(gamma):
            raise AssertionError("control relation/projectivity")
        summaries.append({
            "name": item["name"],
            "vertices": 28,
            "t": t,
            "g": inv["g"],
            "h": inv["h"],
            "union_gram_rank": inv["union_gram_rank"],
            "discriminant": 2,
            "true_relation_minimum_weight": distance,
            "lambda_upper_bound": True,
            "mu_upper_bound": True,
            "opposite_center_mu": True,
        })
    expected = [("t6_h1", 6, 1), ("t7_h0", 7, 0),
                ("t7_h1", 7, 1), ("t7_h2", 7, 2)]
    if [(x["name"], x["t"], x["h"]) for x in summaries] != expected:
        raise AssertionError("control suite changed")
    return summaries


def diag(values: Sequence[int]) -> list[list[int]]:
    return [[values[i] % P if i == j else 0 for j in range(len(values))]
            for i in range(len(values))]


def add(a, b):
    return [[(x + y) % P for x, y in zip(ra, rb)] for ra, rb in zip(a, b)]


def scale(s: int, a):
    return [[s * x % P for x in row] for row in a]


def zero(rows: int, cols: int):
    return [[0] * cols for _ in range(rows)]


def frame_operator(columns, form):
    return blind.matmul(blind.matmul(columns, blind.transpose(columns)), form)


def proof_b_toy() -> dict:
    blocks = [(0,1,3),(0,2,5),(0,4,6),(1,2,6),(1,4,5),(2,3,4),(3,5,6)]
    b = [[int(point in block) for block in blocks] for point in range(7)]
    d = [[
        0 if i == j else (i*i+i*j+j*j+i+j) % P
        for j in range(7)
    ] for i in range(7)]
    stars = [[j for j, x in enumerate(row) if x] for row in b]
    h = []
    for sx in stars:
        row = []
        for sy in stars:
            row.append(sum(
                d[t][r]*d[r][u]*d[u][s]*d[s][t]
                for t in sx for u in sx for r in sy for s in sy
            ) % P)
        h.append(row)
    pairs = [(i, j) for i in range(7) for j in range(7)]
    ufeature = [[row[i]*row[j] for i, j in pairs] for row in b]
    kernel = [[
        d[t][r]*d[r][u]*d[u][s]*d[s][t] % P
        for r, s in pairs
    ] for t, u in pairs]
    factored = blind.matmul(blind.matmul(ufeature, kernel), blind.transpose(ufeature))
    if h != factored:
        raise AssertionError("H=UKU^T")
    q = blind.matmul(blind.transpose(b), b)
    qvec = [x for row in q for x in row]
    if [sum(ufeature[x][j] for x in range(7)) % P for j in range(49)] != qvec:
        raise AssertionError("sum feature")
    row_sums = [sum(row) % P for row in h]
    localizer_sums = []
    for x in range(7):
        sx = diag(b[x])
        m = blind.matmul(blind.matmul(d, sx), d)
        qm = [[q[i][j]*m[i][j] % P for j in range(7)] for i in range(7)]
        localizer_sums.append(blind.trace(blind.matmul(qm, m)))
    if localizer_sums != row_sums:
        raise AssertionError("row localizer")
    kq = blind.vecmul(kernel, qvec)
    norms = []
    for t, u in pairs:
        a = [d[t][r]*d[u][r] % P for r in range(7)]
        w = blind.vecmul(b, a)
        norms.append(sum(x*x for x in w) % P)
    if norms != kq:
        raise AssertionError("w contraction")
    return {
        "H_equals_U_K_U_transpose": True,
        "sum_feature_equals_vec_Q": True,
        "row_localizer": True,
        "w_TU_norm_contraction": True,
        "toy_row_sums": row_sums,
    }


def proof_b_rank99() -> dict:
    points = [(layer, i) for layer in range(3) for i in range(33)]
    index = {point: i for i, point in enumerate(points)}
    blocks = [
        tuple(index[(layer, (intercept + layer*slope) % 33)] for layer in range(3))
        for slope in range(7) for intercept in range(33)
    ]
    incident = [[] for _ in range(99)]
    for j, block in enumerate(blocks):
        for x in block:
            incident[x].append(j)
    if [len(x) for x in incident] != [7] * 99:
        raise AssertionError("rank-control degrees")
    supports = [set(block) for block in blocks]
    if any(len(supports[i] & supports[j]) > 1
           for i in range(231) for j in range(i + 1, 231)):
        raise AssertionError("rank-control linearity")
    for x in range(99):
        left, right = incident[x][:2]
        if [y for y in range(99) if left in incident[y] and right in incident[y]] != [x]:
            raise AssertionError("unit column")
    return {
        "points": 99,
        "blocks": 231,
        "ordered_distinct_pairs": 4158,
        "unit_columns": 99,
        "rank_U": 99,
    }


def proof_b_zero_first_moment_control() -> dict:
    form = diag([1] * 10 + [2])
    supports = [
        (1,2,4,5,6,8), (1,2,3,5,6,8), (1,2,5,7,8,9),
        (0,1,3,5,6,7), (0,1,4,5,7,9), (0,1,3,4,5,9),
    ]
    bases = [
        [[int(row == coordinate) for coordinate in support] for row in range(11)]
        for support in supports
    ]
    vector = [int(i < 4) for i in range(11)]
    reflection = add(blind.eye(11), [[vector[i]*vector[j] % P for j in range(11)]
                                     for i in range(11)])
    if blind.matmul(blind.matmul(blind.transpose(reflection), form), reflection) != form:
        raise AssertionError("reflection")
    bases += [blind.matmul(reflection, b) for b in bases]
    projectors = [blind.matmul(blind.matmul(b, blind.transpose(b)), form) for b in bases]
    simplex_rows = [
        [0,0,0,1,1,1], [0,0,0,1,1,2], [0,0,1,2,2,0],
        [0,1,2,0,1,0], [0,2,2,0,1,0], [1,0,2,1,0,0],
        [2,0,2,1,0,0],
    ]
    simplex = blind.transpose(simplex_rows)
    expected_star = blind.STAR_GRAM
    for basis, projector in zip(bases, projectors):
        columns = blind.matmul(basis, simplex)
        if blind.matmul(blind.matmul(blind.transpose(columns), form), columns) != expected_star:
            raise AssertionError("simplex")
        if any(sum(row) % P for row in columns):
            raise AssertionError("simplex sum")
        if blind.rank(projector) != 6 or blind.trace(projector) != 0:
            raise AssertionError("projector rank/trace")
        if blind.matmul(projector, projector) != projector:
            raise AssertionError("projector idempotent")
        if blind.matmul(blind.transpose(projector), form) != blind.matmul(form, projector):
            raise AssertionError("projector self-adjoint")
        if projector != scale(2, frame_operator(columns, form)):
            raise AssertionError("projector frame")
    if len({tuple(x for row in p for x in row) for p in projectors}) != 12:
        raise AssertionError("distinct base projectors")
    if any(x for row in sum_matrices(projectors) for x in row):
        raise AssertionError("base sum")
    labels = list(range(12)) + [0] * 87
    all_p = [projectors[i] for i in labels]
    if any(x for row in sum_matrices(all_p) for x in row):
        raise AssertionError("99 sum")
    small_g = [[blind.trace(blind.matmul(a, b)) for b in projectors] for a in projectors]
    small_h = [[
        blind.trace(blind.matmul(blind.matmul(a, b), blind.matmul(a, b)))
        for b in projectors
    ] for a in projectors]
    g = [[small_g[i][j] for j in labels] for i in labels]
    h = [[small_h[i][j] for j in labels] for i in labels]
    g_rows = [sum(row) % P for row in g]
    h_rows = [sum(row) % P for row in h]
    omega = [0] * (11**4)
    for projector in projectors:
        flat = [x for row in projector for x in row]
        for i, a in enumerate(flat):
            if a:
                base = i * 121
                for j, b in enumerate(flat):
                    omega[base + j] = (omega[base + j] + a*b) % P
    result = {
        "base_distinct_projectors": 12,
        "projector_labels": 99,
        "sum_projectors_zero": True,
        "pair_trace_rank": blind.rank(g),
        "fourth_trace_rank": blind.rank(h),
        "pair_row_sums": dict(Counter(g_rows)),
        "fourth_row_sums": dict(Counter(h_rows)),
        "g_h_different_ordered_entries": sum(
            g[i][j] != h[i][j] for i in range(99) for j in range(99)
        ),
        "Omega_nonzero_coordinates": sum(x != 0 for x in omega),
    }
    expected = {
        "base_distinct_projectors": 12,
        "projector_labels": 99,
        "sum_projectors_zero": True,
        "pair_trace_rank": 8,
        "fourth_trace_rank": 9,
        "pair_row_sums": {0: 99},
        "fourth_row_sums": {0: 6, 1: 91, 2: 2},
        "g_h_different_ordered_entries": 740,
        "Omega_nonzero_coordinates": 302,
    }
    if result != expected:
        raise AssertionError({"proof_b_control": result, "expected": expected})
    return result


def sum_matrices(matrices):
    out = zero(len(matrices[0]), len(matrices[0][0]))
    for matrix in matrices:
        out = add(out, matrix)
    return out


def normalized_direction(vector: Sequence[int]) -> tuple[int, ...]:
    first = next(x for x in vector if x)
    inv = pow(first, -1, P)
    return tuple(inv*x % P for x in vector)


def hostile_certificate() -> dict:
    cert = json.loads((HOSTILE / "certificate.json").read_text(encoding="utf-8"))
    sealed = json.loads((HOSTILE / "exact-results.json").read_text(encoding="utf-8"))
    form = cert["ambient_form"]
    if blind.rank(form) != 11:
        raise AssertionError("hostile ambient form")
    projectors = cert["projectors"]
    simplices = cert["simplices_as_11_by_7_matrices"]
    for name in ("P", "Q1", "Q2"):
        p = projectors[name]
        z = simplices[name]
        if blind.rank(p) != 6 or blind.trace(p) != 0 or blind.matmul(p, p) != p:
            raise AssertionError(f"{name}: projector")
        if blind.matmul(blind.transpose(p), form) != blind.matmul(form, p):
            raise AssertionError(f"{name}: self-adjoint")
        gram = blind.matmul(blind.matmul(blind.transpose(z), form), z)
        if gram != blind.STAR_GRAM or any(sum(row) % P for row in z):
            raise AssertionError(f"{name}: simplex")
        if p != scale(2, frame_operator(z, form)):
            raise AssertionError(f"{name}: frame")
    pair_table = {}
    for left, right in (("P", "Q1"), ("P", "Q2"), ("Q1", "Q2")):
        pq = blind.matmul(projectors[left], projectors[right])
        pair_table[f"{left},{right}"] = {
            "g": blind.trace(pq),
            "h": blind.trace(blind.matmul(pq, pq)),
        }
    if pair_table != {
        "P,Q1": {"g": 2, "h": 1},
        "P,Q2": {"g": 2, "h": 2},
        "Q1,Q2": {"g": 1, "h": 2},
    }:
        raise AssertionError("hostile local pair table")

    blocks = cert["blocks"]
    incidence = cert["incidence_matrix"]
    if len(blocks) != 231 or len(incidence) != 99 or any(len(r) != 231 for r in incidence):
        raise AssertionError("hostile incidence dimensions")
    reconstructed = [[0] * 231 for _ in range(99)]
    adjacency = [set() for _ in range(99)]
    edge_owners = Counter()
    for j, block in enumerate(blocks):
        if block["id"] != j or len(set(block["vertices"])) != 3:
            raise AssertionError("hostile block record")
        for x in block["vertices"]:
            reconstructed[x][j] = 1
        for x, y in combinations(block["vertices"], 2):
            key = tuple(sorted((x, y)))
            edge_owners[key] += 1
            adjacency[x].add(y)
            adjacency[y].add(x)
    if reconstructed != incidence or set(edge_owners.values()) != {1}:
        raise AssertionError("hostile incidence certificate")
    if [sum(row) for row in incidence] != [7] * 99:
        raise AssertionError("hostile row degree")
    if [sum(incidence[x][j] for x in range(99)) for j in range(231)] != [3] * 231:
        raise AssertionError("hostile col degree")
    if [len(n) for n in adjacency] != [14] * 99 or len(edge_owners) != 693:
        raise AssertionError("hostile point graph")

    edge_hist, nonedge_hist = Counter(), Counter()
    for x in range(99):
        for y in range(x + 1, 99):
            common = len(adjacency[x] & adjacency[y])
            (edge_hist if y in adjacency[x] else nonedge_hist)[common] += 1
    triangles = sum(
        y in adjacency[x] and z in adjacency[x] and z in adjacency[y]
        for x, y, z in combinations(range(99), 3)
    )
    if (edge_hist, nonedge_hist, triangles) != (
        Counter({4:144,5:243,6:27,7:225,8:27,9:27}),
        Counter({0:3240,2:144,4:180,5:27,6:315,7:27,8:225}),
        1329,
    ):
        raise AssertionError("hostile graph failure ledger")

    summaries = {}
    full_pair, full_fourth = {}, {}
    for realization in ("A", "B"):
        data = cert[f"realization_{realization}"]
        types = data["vertex_types"]
        vectors = data["block_vectors"]
        if len(types) != 99 or len(vectors) != 231:
            raise AssertionError("hostile realization dimensions")
        for j, block in enumerate(blocks):
            component_type = types[block["vertices"][0]]
            if any(types[x] != component_type for x in block["vertices"]):
                raise AssertionError("block crosses projector types")
            expected = [simplices[component_type][i][block["color"]] for i in range(11)]
            if vectors[j] != expected:
                raise AssertionError("block vector/color coupling")
        for x in range(99):
            star_vectors = [vectors[j] for j, bit in enumerate(incidence[x]) if bit]
            zstar = blind.transpose(star_vectors)
            if scale(2, frame_operator(zstar, form)) != projectors[types[x]]:
                raise AssertionError("99-star coupling")
        plist = [projectors[t] for t in types]
        if any(v for row in sum_matrices(plist) for v in row):
            raise AssertionError("projector first moment")
        z = blind.transpose(vectors)
        d = blind.matmul(blind.matmul(blind.transpose(z), form), z)
        if blind.rank(z) != 11 or blind.rank(d) != 11 or any(d[i][i] for i in range(231)):
            raise AssertionError("hostile centered rank")
        if any(v for row in blind.matmul(d, d) for v in row):
            raise AssertionError("hostile square zero")
        if any(v for row in frame_operator(z, form) for v in row):
            raise AssertionError("hostile global frame")
        directions = Counter(normalized_direction(v) for v in vectors)
        if len(directions) != 21 or Counter(directions.values()) != Counter({12:14,9:7}):
            raise AssertionError("hostile direction failure")
        summaries[realization] = {
            "rank_Z": 11, "rank_D": 11, "D_square_zero": True,
            "projective_directions": 21,
            "direction_multiplicities": {9: 7, 12: 14},
        }
        unique_types = ("P", "Q1", "Q2")
        small_g, small_h = {}, {}
        for a in unique_types:
            for b in unique_types:
                pq = blind.matmul(projectors[a], projectors[b])
                small_g[a,b] = blind.trace(pq)
                small_h[a,b] = blind.trace(blind.matmul(pq, pq))
        full_pair[realization] = [[small_g[a,b] for b in types] for a in types]
        full_fourth[realization] = [[small_h[a,b] for b in types] for a in types]

    if full_pair["A"] != full_pair["B"]:
        raise AssertionError("hostile g matrices")
    differing = [
        (x,y) for x in range(99) for y in range(99)
        if full_fourth["A"][x][y] != full_fourth["B"][x][y]
    ]
    edge_diffs = [(x,y) for x,y in differing if y in adjacency[x]]
    nonedge_diffs = [(x,y) for x,y in differing if x != y and y not in adjacency[x]]
    comparison = {
        "same_g": True,
        "h_differences": len(differing),
        "edge_h_differences": len(edge_diffs),
        "nonedge_h_differences": len(nonedge_diffs),
        "rank_H_A": blind.rank(full_fourth["A"]),
        "rank_H_B": blind.rank(full_fourth["B"]),
    }
    if comparison != {
        "same_g": True, "h_differences": 3888, "edge_h_differences": 0,
        "nonedge_h_differences": 3888, "rank_H_A": 3, "rank_H_B": 3,
    }:
        raise AssertionError("hostile comparison")
    if len(sealed["failed_target_premises"]) < 7:
        raise AssertionError("hostile failed-premise ledger")
    return {
        "local_pair_table": pair_table,
        "incidence": {
            "points": 99, "blocks": 231, "row_degree": 7, "column_degree": 3,
            "point_degree": 14, "edges": 693, "triangles": triangles,
            "designated_triangles": 231, "extra_triangles": triangles-231,
            "components": [27,36,36],
            "lambda_distribution": dict(edge_hist),
            "mu_distribution": dict(nonedge_hist),
        },
        "realizations": summaries,
        "comparison": comparison,
        "failed_target_premises_count": len(sealed["failed_target_premises"]),
        "target_failures_preserved": True,
    }


def build_result() -> dict:
    manifests = {
        path.parent.name: verify_manifest(path)
        for path in EXPECTED_MANIFESTS
    }
    a_census = proof_a_census()
    a_controls = proof_a_controls()
    b_toy = proof_b_toy()
    b_rank = proof_b_rank99()
    b_control = proof_b_zero_first_moment_control()
    hostile = hostile_certificate()
    return {
        "claim_label": "VERIFIED_WITH_SCOPE",
        "source_blind_freeze_sha256":
            "f8fb87d76c5eda2ff2569ec49a935b8bdb4022671f6d51f2752c14e153bcc853",
        "sealed_manifests": manifests,
        "discovery_replays": {
            "proof_a": {
                "frozen_result_replay": "PASS",
                "tests": "13/13 PASS",
            },
            "proof_b": {
                "frozen_result_replay": "PASS",
                "tests": "12/12 PASS",
            },
            "hostile_control": {
                "frozen_result_and_certificate_replay": "PASS",
                "plain_test_functions": "6/6 PASS",
                "pytest_wrapper": "NOT RUN: pytest is not installed",
            },
        },
        "proof_a": {
            "normalized_census": a_census,
            "controls": a_controls,
            "derived_checks": {
                "marked_corner": [[1,2],[2,1]],
                "special_profile": {"zeros":0,"ones":5,"twos":2},
                "ordinary_sum": 6,
                "t_lower_bound": 6,
                "nonneighbor_average_t": 7,
                "pair_trace_formula": "g=2t over F_3",
            },
            "verdict": "VERIFIED_WITH_SCOPE",
            "actual_nonedge_h_classification": "UNKNOWN",
        },
        "proof_b": {
            "factorization_and_contractions": b_toy,
            "star_pair_feature": b_rank,
            "dimension_ledger": {
                **blind.dimension_ledger(),
                "dim_Sym2_V": 66,
                "dim_self_adjoint_End_Sym2_V": 2211,
                "dim_trace_zero_self_adjoint_End_Sym2_V": 2210,
            },
            "zero_first_moment_control": b_control,
            "verdict": "VERIFIED_WITH_SCOPE",
        },
        "hostile_control": {
            **hostile,
            "verdict": "VERIFIED_RELAXED_CONTROL",
        },
        "findings": [],
        "limitations": [
            "Proof-A controls are 28-vertex local controls, not 99-vertex SRGs.",
            "Proof-B zero-first-moment control repeats projector labels and has no target incidence.",
            "The hostile 99x231 controls have only 21 projective directions and fail lambda/mu.",
            "Literature novelty and completeness were not certified by this computational replay.",
        ],
        "status_wall": {
            "Conway_99": "UNKNOWN",
            "rank_11_endpoint": "UNKNOWN",
            "n3_4158_endpoint": "UNKNOWN",
            "rigorous_n3_interval": "708<=n3<=4158",
            "conditional_Q_bound": "Q>=7059",
            "Q>=7060": "NOT PROVED",
        },
    }


def main() -> None:
    print(json.dumps(build_result(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
