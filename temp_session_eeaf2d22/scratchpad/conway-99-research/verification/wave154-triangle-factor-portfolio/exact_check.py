#!/usr/bin/env python3
"""Clean-room verifier for the sealed Wave154 finite portfolio claims.

This verifier reads only declarative JSON certificates.  It does not import
or execute any code from attempts/wave154-triangle-factor-portfolio.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path
from typing import Iterable, Sequence


ROOT = Path(__file__).resolve().parents[2]
W149_RESULTS = ROOT / "attempts/wave149-terwilliger-triple/exact-results.json"
W151_RESULTS = ROOT / "attempts/wave151-triangle-root-factor/exact-results.json"
W154_RESULTS = ROOT / "attempts/wave154-triangle-factor-portfolio/exact-results.json"
W154_MANIFEST = (
    ROOT / "attempts/wave154-triangle-factor-portfolio/package-manifest.sha256"
)

FROZEN_SHA256 = {
    "attempts/wave149-terwilliger-triple/exact-results.json":
        "6fed4da32fbeefce54d1802136dc8c9a328f112bb0f295a86230f0e6175f5ee6",
    "attempts/wave151-triangle-root-factor/exact-results.json":
        "74bc48e2dd0434f3e36a183d724a1ae4a52d7ec9a1e109c92b14f64985da37a4",
    "attempts/wave154-triangle-factor-portfolio/exact-results.json":
        "cca362e926901f626f50ed8a0868e94dd3da6cfdac1713be67a512156013a7fd",
    "attempts/wave154-triangle-factor-portfolio/package-manifest.sha256":
        "6107b22050b2f9b3a070cdb031482c67907f7a39f7fea3c08bb543572e8fb311",
}

EXPECTED_OLD_MATRIX_SHA256 = (
    "11dd68b64c237e6d45e221e8910b3da69e9492dd01aeb697555d874fdab9eed5"
)
EXPECTED_NEW_MATRIX_SHA256 = (
    "3292d6e445c168973f76a8dac1bf7bede704b141ab84388f94585c21ffac0b11"
)
EXPECTED_GRAM_SHA256 = (
    "1cfd0442e69b621c4a82fbeddeec9e7afbfcd04cd8eb458e29170cfd345c7ffc"
)
EXPECTED_ALLOWED_SHA256 = (
    "abbca3a6ffb9eb344f0ab4af16e4861aed56293464320f7d01c3fe661cd4eed1"
)
EXPECTED_OLD_ORBIT_SHA256 = (
    "68dca5883f918f25922832fde91a620fe0d51f1d750ee04e42766a63e3b4cc07"
)
EXPECTED_NEW_ORBIT_SHA256 = (
    "4daeb1f8ff6a1fcb50f1aa7010d45d7495f5fbe8bfbec78fd68bce01205c1069"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def compact_json_sha256(value: object) -> str:
    payload = json.dumps(value, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def matching(vertex: int) -> int:
    return vertex ^ 1


def shift(vertex: int) -> int:
    return (vertex + 6) % 12


def nonmatching_edges() -> tuple[tuple[int, int], ...]:
    return tuple(
        (u, v)
        for u in range(12)
        for v in range(u + 1, 12)
        if v != matching(u)
    )


def diagonal_gram() -> tuple[tuple[int, ...], ...]:
    return tuple(
        tuple(9 * (u == v) - (matching(u) == v) + 1 for v in range(12))
        for u in range(12)
    )


def cross_grams() -> tuple[
    tuple[tuple[int, ...], ...],
    tuple[tuple[int, ...], ...],
    tuple[tuple[int, ...], ...],
]:
    # For F01=F02=I, F12=P, and M0=M1=M2=M:
    # Gij = 2J-Fij-MFij-FijM-FikFkj.
    g01 = tuple(
        tuple(
            2
            - (u == v)
            - 2 * (matching(u) == v)
            - (shift(u) == v)
            for v in range(12)
        )
        for u in range(12)
    )
    g02 = g01
    g12 = tuple(
        tuple(
            2
            - (u == v)
            - (shift(u) == v)
            - 2 * (matching(shift(u)) == v)
            for v in range(12)
        )
        for u in range(12)
    )
    return g01, g02, g12


def transpose(matrix: Sequence[Sequence[int]]) -> tuple[tuple[int, ...], ...]:
    return tuple(tuple(matrix[row][col] for row in range(len(matrix)))
                 for col in range(len(matrix[0])))


def block_gram() -> tuple[tuple[int, ...], ...]:
    diagonal = diagonal_gram()
    g01, g02, g12 = cross_grams()
    blocks = (
        (diagonal, g01, g02),
        (transpose(g01), diagonal, g12),
        (transpose(g02), transpose(g12), diagonal),
    )
    rows: list[tuple[int, ...]] = []
    for block_row in range(3):
        for row in range(12):
            rows.append(
                tuple(
                    entry
                    for block_col in range(3)
                    for entry in blocks[block_row][block_col][row]
                )
            )
    return tuple(rows)


def incidence_matrix(q1: Sequence[int]) -> tuple[tuple[int, ...], ...]:
    edges = nonmatching_edges()
    if sorted(q1) != list(range(60)):
        raise ValueError("Q1 is not a permutation of the 60 nonmatching edges")
    rows = [[0] * 60 for _ in range(24)]
    for column, edge0 in enumerate(edges):
        edge1 = edges[q1[column]]
        for vertex in edge0:
            rows[vertex][column] = 1
        for vertex in edge1:
            rows[12 + vertex][column] = 1
    return tuple(tuple(row) for row in rows)


def gram(matrix: Sequence[Sequence[int]]) -> tuple[tuple[int, ...], ...]:
    return tuple(
        tuple(sum(x * y for x, y in zip(row_a, row_b)) for row_b in matrix)
        for row_a in matrix
    )


def expected_partial_gram() -> tuple[tuple[int, ...], ...]:
    diagonal = diagonal_gram()
    g01, _, _ = cross_grams()
    rows: list[tuple[int, ...]] = []
    for row in range(12):
        rows.append(diagonal[row] + g01[row])
    tg01 = transpose(g01)
    for row in range(12):
        rows.append(tg01[row] + diagonal[row])
    return tuple(rows)


def centralizer() -> tuple[tuple[int, ...], ...]:
    # <M,P> acts regularly on each of three four-point orbits.  A commuting
    # permutation chooses an S3 permutation of those orbits and an independent
    # V4 translation on each orbit: 3! * 4^3 = 384.
    permutations: list[tuple[int, ...]] = []
    for orbit_permutation in itertools.permutations(range(3)):
        for translations in itertools.product(range(4), repeat=3):
            action: list[int | None] = [None] * 12
            for source_orbit in range(3):
                target_orbit = orbit_permutation[source_orbit]
                source = (
                    2 * source_orbit,
                    2 * source_orbit + 1,
                    2 * source_orbit + 6,
                    2 * source_orbit + 7,
                )
                target = (
                    2 * target_orbit,
                    2 * target_orbit + 1,
                    2 * target_orbit + 6,
                    2 * target_orbit + 7,
                )
                translation = translations[source_orbit]
                for coordinate, vertex in enumerate(source):
                    action[vertex] = target[coordinate ^ translation]
            permutations.append(tuple(int(value) for value in action))
    return tuple(permutations)


def induced_edge_action(
    vertex_action: Sequence[int],
) -> tuple[int, ...]:
    edges = nonmatching_edges()
    edge_index = {edge: index for index, edge in enumerate(edges)}
    return tuple(
        edge_index[tuple(sorted((vertex_action[u], vertex_action[v])))]
        for u, v in edges
    )


def conjugate_edge_permutation(
    q1: Sequence[int], edge_action: Sequence[int]
) -> tuple[int, ...]:
    inverse = [0] * 60
    for source, target in enumerate(edge_action):
        inverse[target] = source
    return tuple(
        edge_action[q1[inverse[edge]]] for edge in range(60)
    )


def q1_orbit(
    q1: Sequence[int], edge_actions: Iterable[Sequence[int]]
) -> set[tuple[int, ...]]:
    return {
        conjugate_edge_permutation(q1, edge_action)
        for edge_action in edge_actions
    }


def triple_allowed(
    triple: tuple[int, int, int],
    edges: Sequence[tuple[int, int]],
    g01: Sequence[Sequence[int]],
    g02: Sequence[Sequence[int]],
    g12: Sequence[Sequence[int]],
) -> bool:
    e0, e1, e2 = (edges[index] for index in triple)
    return (
        all(g01[u][v] > 0 for u in e0 for v in e1)
        and all(g02[u][v] > 0 for u in e0 for v in e2)
        and all(g12[u][v] > 0 for u in e1 for v in e2)
    )


def allowed_triples() -> tuple[tuple[int, int, int], ...]:
    edges = nonmatching_edges()
    g01, g02, g12 = cross_grams()
    return tuple(
        triple
        for triple in itertools.product(range(60), repeat=3)
        if triple_allowed(triple, edges, g01, g02, g12)
    )


def triple_orbit_sizes(
    allowed: Sequence[tuple[int, int, int]],
    edge_actions: Sequence[Sequence[int]],
) -> Counter[int]:
    allowed_set = set(allowed)
    unseen = set(allowed)
    sizes: Counter[int] = Counter()
    while unseen:
        representative = min(unseen)
        orbit = {
            (
                edge_action[representative[0]],
                edge_action[representative[1]],
                edge_action[representative[2]],
            )
            for edge_action in edge_actions
        }
        if not orbit <= allowed_set:
            raise AssertionError("the claimed group does not preserve allowed triples")
        unseen.difference_update(orbit)
        sizes[len(orbit)] += 1
    return sizes


def verify_discovery_manifest() -> tuple[int, int]:
    passed = 0
    failed = 0
    for line in W154_MANIFEST.read_text(encoding="utf-8").splitlines():
        expected, relative = line.split("  ", 1)
        actual = sha256_file(ROOT / Path(relative))
        if actual == expected:
            passed += 1
        else:
            failed += 1
    return passed, failed


def run_checks() -> dict:
    for relative, expected in FROZEN_SHA256.items():
        actual = sha256_file(ROOT / Path(relative))
        if actual != expected:
            raise AssertionError(
                f"frozen input drift: {relative}: {actual} != {expected}"
            )

    wave149 = load_json(W149_RESULTS)
    wave151 = load_json(W151_RESULTS)
    wave154 = load_json(W154_RESULTS)
    old_q1 = tuple(wave151["exact_partial_factor"]["Q1"])
    new_q1 = tuple(wave154["second_exact_Q1_representative"]["Q1"])

    edges = nonmatching_edges()
    stored_edges = tuple(
        tuple(edge) for edge in wave151["exact_partial_factor"]["edge_columns"]
    )
    if stored_edges != edges:
        raise AssertionError("Wave151 edge order differs from independent order")

    full_gram = block_gram()
    stored_gram = tuple(
        tuple(row)
        for row in wave149["minimal_surviving_witness"]["gram_rows"]
    )
    if full_gram != stored_gram:
        raise AssertionError("independent 36x36 Gram does not match Wave149")
    if compact_json_sha256(full_gram) != EXPECTED_GRAM_SHA256:
        raise AssertionError("36x36 Gram hash mismatch")

    partial_target = expected_partial_gram()
    matrices = {
        "wave151": incidence_matrix(old_q1),
        "wave154": incidence_matrix(new_q1),
    }
    expected_hashes = {
        "wave151": EXPECTED_OLD_MATRIX_SHA256,
        "wave154": EXPECTED_NEW_MATRIX_SHA256,
    }
    for name, matrix in matrices.items():
        if gram(matrix) != partial_target:
            raise AssertionError(f"{name} does not factor the 24x24 target")
        if compact_json_sha256(matrix) != expected_hashes[name]:
            raise AssertionError(f"{name} 24x60 matrix hash mismatch")
        if any(sum(row) != 10 for row in matrix):
            raise AssertionError(f"{name} has a row sum other than 10")
        if any(
            sum(matrix[row][column] for row in range(group * 12, group * 12 + 12))
            != 2
            for group in range(2)
            for column in range(60)
        ):
            raise AssertionError(f"{name} has an invalid per-group column sum")

    group = centralizer()
    if len(group) != 384 or len(set(group)) != 384:
        raise AssertionError("centralizer construction is not 384 distinct maps")
    if any(
        sorted(action) != list(range(12))
        or any(
            action[matching(vertex)] != matching(action[vertex])
            or action[shift(vertex)] != shift(action[vertex])
            for vertex in range(12)
        )
        for action in group
    ):
        raise AssertionError("centralizer action does not commute with M and P")

    edge_actions = tuple(induced_edge_action(action) for action in group)
    if len(set(edge_actions)) != 384:
        raise AssertionError("centralizer action is not faithful on edges")
    old_orbit = q1_orbit(old_q1, edge_actions)
    new_orbit = q1_orbit(new_q1, edge_actions)
    if len(old_orbit) != 384 or len(new_orbit) != 384:
        raise AssertionError("a Q1 orbit does not have size 384")
    if old_orbit & new_orbit:
        raise AssertionError("new Q1 is in the Wave151 centralizer orbit")

    old_orbit_hash = compact_json_sha256(sorted(old_orbit))
    new_orbit_hash = compact_json_sha256(sorted(new_orbit))
    if old_orbit_hash != EXPECTED_OLD_ORBIT_SHA256:
        raise AssertionError("old Q1 orbit digest mismatch")
    if new_orbit_hash != EXPECTED_NEW_ORBIT_SHA256:
        raise AssertionError("new Q1 orbit digest mismatch")

    allowed = allowed_triples()
    if compact_json_sha256(allowed) != EXPECTED_ALLOWED_SHA256:
        raise AssertionError("allowed-triple digest mismatch")
    orbit_sizes = triple_orbit_sizes(allowed, edge_actions)
    target_cross_sums = [sum(map(sum, block)) for block in cross_grams()]
    manifest_passed, manifest_failed = verify_discovery_manifest()
    if manifest_failed:
        raise AssertionError("Wave154 discovery manifest has drifted")

    # Each retained triple has 3 edge incidences and 3*4 cross-cell
    # incidences, hence 15 integer-matrix nonzeros.
    nonzeros = 15 * len(allowed)
    return {
        "allowed_triples": len(allowed),
        "allowed_triples_sha256": compact_json_sha256(allowed),
        "centralizer_order": len(group),
        "constraint_rows": 3 * 60 + 3 * 12 * 12,
        "cross_capacity_rows": 3 * 12 * 12,
        "cross_gram_total_each": target_cross_sums,
        "discovery_manifest": {
            "failed": manifest_failed,
            "passed": manifest_passed,
        },
        "edge_capacity_rows": 3 * 60,
        "full_gram_sha256": compact_json_sha256(full_gram),
        "integer_matrix_nonzeros": nonzeros,
        "new_matrix_sha256": compact_json_sha256(matrices["wave154"]),
        "new_q1_orbit_sha256": new_orbit_hash,
        "new_q1_orbit_size": len(new_orbit),
        "old_matrix_sha256": compact_json_sha256(matrices["wave151"]),
        "old_q1_orbit_sha256": old_orbit_hash,
        "old_q1_orbit_size": len(old_orbit),
        "orbit_intersection_size": len(old_orbit & new_orbit),
        "selected_columns_required": 60,
        "triple_orbit_count": sum(orbit_sizes.values()),
        "triple_orbit_size_histogram": {
            str(size): count for size, count in sorted(orbit_sizes.items())
        },
    }


def verify_result(path: Path, computed: dict) -> None:
    expected = load_json(path)["independent_reconstruction"]
    if computed != expected:
        raise AssertionError("computed result differs from verification certificate")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", type=Path)
    parser.add_argument("--print-json", action="store_true")
    args = parser.parse_args()
    computed = run_checks()
    if args.verify:
        verify_result(args.verify, computed)
    if args.print_json:
        print(json.dumps(computed, indent=2, sort_keys=True))
    print(
        "PASS_WITH_SCOPE: exact finite portfolio claims reproduced; "
        "solver negatives excluded; full C and D remain UNKNOWN"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
