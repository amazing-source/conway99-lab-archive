#!/usr/bin/env python3
"""Exact Wave 30 construction of a rootless h=729 lattice beyond S0.

The construction starts from K12 orthogonal-sum E8 in rank 20 and follows
five explicitly frozen two-neighbors.  After every neighbor, a deterministic
exact LLL basis reduction is applied only to keep the next enumeration small.
All acceptance checks use integers or ``fractions.Fraction``.

The resulting rootless rank-20 determinant-729 lattice is then summed with an
embedded, attributed Leech Gram matrix.  The rank-44 output satisfies the bare
S/G endpoint lattice conditions.  It does *not* supply Q, B, a 231-row frame,
the Schur-square identity, or a graph.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Any, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE / "exact-results.json"

FROZEN_INPUTS = {
    "agents/2026-07-24-wave28-orchestrator-brief.md":
        "6a15446551b78822706a8e005bef49a411b904cf05f9459b6b3350239839ee1e",
    "verification/wave28-simultaneous-neighbor/independent_check.py":
        "2c8021769d47faebbcd544b364649a2cb93c066a369f76f725cffab1588982db",
    "verification/wave28-theta-modular/independent_check.py":
        "513efd1a915bc14adc3003c41e6758839375d9a36a0055f08faa56417c942b18",
}

NEIGHBOR_HELPER_PATH = (
    REPO_ROOT / "verification" / "wave28-simultaneous-neighbor"
    / "independent_check.py"
)
LLL_HELPER_PATH = (
    REPO_ROOT / "verification" / "wave28-theta-modular"
    / "independent_check.py"
)

K12_SOURCE = {
    "name": "K12 (Coxeter-Todd lattice)",
    "url": "https://www.math.rwth-aachen.de/~Gabriele.Nebe/LATTICES/K12.html",
    "frozen_response_sha256":
        "163e03dfa9a4ab07675daa6e97a371bcfdb38f6195c311c63c699872b3e486c9",
    "access_date_utc": "2026-07-24",
}

LEECH_SOURCE = {
    "name": "LAMBDA24 (Leech lattice)",
    "url": "https://www.math.rwth-aachen.de/~Gabriele.Nebe/LATTICES/Leech.html",
    "frozen_response_sha256":
        "0d5967713c09e2fda1ba06fc183ca376eccc73b9e4612e88d36c5fe70d13479c",
    "access_date_utc": "2026-07-24",
}

# Catalogued lower-triangular Gram data from the K12 source above.
K12_LOWER = [
    [4],
    [0, 4],
    [0, 0, 4],
    [-2, 0, 0, 4],
    [0, -2, 0, 0, 4],
    [0, 0, -2, 0, 0, 4],
    [2, 2, 2, -1, -1, -1, 4],
    [-1, -1, 2, -1, 2, -1, 0, 4],
    [-1, -1, 2, 2, -1, -1, 0, 0, 4],
    [-1, -1, -1, 2, 2, 2, -2, 0, 0, 4],
    [2, -1, -1, -1, -1, 2, 0, -2, 0, 0, 4],
    [-1, 2, -1, -1, -1, 2, 0, 0, -2, 0, 0, 4],
]

# Catalogued 24-by-24 Gram matrix from the Leech source above.  The response
# body is not retained.  The matrix is independently checked below.
LEECH = [
    [8, 4, 4, 4, 4, 4, 4, 2, 4, 4, 4, 2, 4, 2, 2, 2, 4, 2, 2, 2, 0, 0, 0, -3],
    [4, 4, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 2, 1, 1, 2, 1, 0, 0, -1],
    [4, 2, 4, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 1, 2, 2, 1, 1, 1, 0, 0, -1],
    [4, 2, 2, 4, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 2, 2, 1, 2, 1, 1, 0, 0, -1],
    [4, 2, 2, 2, 4, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 1, 0, 0, -1],
    [4, 2, 2, 2, 2, 4, 2, 2, 2, 2, 2, 1, 2, 2, 1, 1, 2, 1, 2, 1, 0, 0, 0, -1],
    [4, 2, 2, 2, 2, 2, 4, 2, 2, 2, 2, 1, 2, 1, 2, 1, 2, 1, 1, 2, 0, 0, 0, -1],
    [2, 2, 2, 2, 2, 2, 2, 4, 1, 1, 1, 2, 1, 2, 2, 2, 1, 2, 2, 2, 2, 0, 0, 1],
    [4, 2, 2, 2, 2, 2, 2, 1, 4, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, -1],
    [4, 2, 2, 2, 2, 2, 2, 1, 2, 4, 2, 2, 2, 2, 1, 1, 2, 2, 1, 1, 0, 1, 0, -1],
    [4, 2, 2, 2, 2, 2, 2, 1, 2, 2, 4, 2, 2, 1, 2, 1, 2, 1, 2, 1, 0, 0, 1, -1],
    [2, 2, 2, 2, 1, 1, 1, 2, 2, 2, 2, 4, 1, 2, 2, 2, 1, 2, 2, 2, 2, 1, 1, 1],
    [4, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 1, 4, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, -1],
    [2, 2, 1, 1, 2, 2, 1, 2, 2, 2, 1, 2, 2, 4, 2, 2, 1, 2, 2, 2, 2, 2, 1, 1],
    [2, 1, 2, 1, 2, 1, 2, 2, 2, 1, 2, 2, 2, 2, 4, 2, 1, 2, 2, 2, 2, 1, 2, 1],
    [2, 1, 1, 2, 2, 1, 1, 2, 2, 1, 1, 2, 2, 2, 2, 4, 1, 2, 2, 2, 2, 1, 1, 1],
    [4, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 1, 2, 1, 1, 1, 4, 2, 2, 2, 1, 1, 1, -1],
    [2, 1, 2, 1, 2, 1, 1, 2, 2, 2, 1, 2, 1, 2, 2, 2, 2, 4, 2, 2, 2, 2, 1, 1],
    [2, 1, 1, 2, 2, 2, 1, 2, 2, 1, 2, 2, 1, 2, 2, 2, 2, 2, 4, 2, 2, 1, 2, 1],
    [2, 2, 1, 1, 2, 1, 2, 2, 2, 1, 1, 2, 1, 2, 2, 2, 2, 2, 2, 4, 2, 1, 1, 1],
    [0, 1, 1, 1, 1, 0, 0, 2, 1, 0, 0, 2, 1, 2, 2, 2, 1, 2, 2, 2, 4, 2, 2, 2],
    [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 2, 1, 1, 1, 2, 1, 1, 2, 4, 2, 2],
    [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 2, 1, 1, 1, 2, 1, 2, 2, 4, 2],
    [-3, -1, -1, -1, -1, -1, -1, 1, -1, -1, -1, 1, -1, 1, 1, 1, -1, 1, 1, 1, 2, 2, 2, 4],
]

E8_EDGES = ((0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (2, 7))

NEIGHBOR_SUPPORTS = (
    (0, 1, 2, 5, 11, 13, 14, 17, 18),
    (5, 7, 8, 9, 10, 11, 12, 13, 14, 19),
    (1, 4, 6, 10, 11, 14, 16, 17, 19),
    (3, 4, 5, 6, 7, 8, 10, 12, 14, 15, 17, 19),
    (0, 5, 6, 8, 9, 10, 13, 14, 15, 16, 17, 18, 19),
)

EXPECTED_ROOT_COUNTS = (240, 112, 48, 20, 6, 0)
EXPECTED_FINAL_T20_HASH = (
    "1890fe1973eed47850c307d0975ae393f2a8ab32a9d0b16b35ebcab7012445d6"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def canonical_hash(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def load_helper(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"cannot load helper {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def symmetric_from_lower(rows: Sequence[Sequence[int]]) -> list[list[int]]:
    n = len(rows)
    if any(len(row) != i + 1 for i, row in enumerate(rows)):
        raise AssertionError("malformed lower triangle")
    matrix = [[0 for _ in range(n)] for _ in range(n)]
    for i, row in enumerate(rows):
        for j, value in enumerate(row):
            matrix[i][j] = int(value)
            matrix[j][i] = int(value)
    return matrix


def e8_cartan() -> list[list[int]]:
    matrix = [[2 if i == j else 0 for j in range(8)] for i in range(8)]
    for i, j in E8_EDGES:
        matrix[i][j] = -1
        matrix[j][i] = -1
    return matrix


def qmatrix(matrix: Sequence[Sequence[int | Fraction]]) -> list[list[Fraction]]:
    return [[Fraction(value) for value in row] for row in matrix]


def imatrix(matrix: Sequence[Sequence[int | Fraction]]) -> list[list[int]]:
    output: list[list[int]] = []
    for row in matrix:
        converted = []
        for value in row:
            fraction = Fraction(value)
            if fraction.denominator != 1:
                raise AssertionError("matrix is not integral")
            converted.append(fraction.numerator)
        output.append(converted)
    return output


def json_scalar(value: int | Fraction) -> int | str:
    fraction = Fraction(value)
    if fraction.denominator == 1:
        return fraction.numerator
    return f"{fraction.numerator}/{fraction.denominator}"


def json_matrix(
    matrix: Sequence[Sequence[int | Fraction]],
) -> list[list[int | str]]:
    return [[json_scalar(value) for value in row] for row in matrix]


def root_shell(
    nb: Any,
    gram: list[list[Fraction]],
    cap: int,
) -> dict[str, Any]:
    vectors, stats = nb.enumerate_vectors(gram, cap)
    counts = Counter(int(norm) for _vector, norm in vectors)
    by_norm = {
        str(norm): [
            list(vector)
            for vector, vector_norm in vectors
            if int(vector_norm) == norm
        ]
        for norm in sorted(counts)
        if norm
    }
    return {
        "counts": {str(norm): counts[norm] for norm in sorted(counts)},
        "vector_hashes": {
            norm: canonical_hash(vectors_at_norm)
            for norm, vectors_at_norm in by_norm.items()
        },
        "enumeration": stats,
    }


def validate_inputs() -> dict[str, str]:
    actual = {}
    for relative, expected in FROZEN_INPUTS.items():
        digest = sha256_file(REPO_ROOT / relative)
        if digest != expected:
            raise AssertionError(
                f"frozen input changed: {relative}: {digest} != {expected}"
            )
        actual[relative] = digest
    return actual


def construct_t20(nb: Any, tv: Any) -> dict[str, Any]:
    k12 = symmetric_from_lower(K12_LOWER)
    e8 = e8_cartan()
    current = nb.block_diagonal([qmatrix(k12), qmatrix(e8)])

    if nb.determinant(current) != 729:
        raise AssertionError("starting determinant drifted")
    if not nb.is_even_integral_form(current):
        raise AssertionError("starting form is not even integral")
    starting_g = nb.matrix_scale(21, nb.inverse(current))
    if not nb.is_even_integral_form(starting_g):
        raise AssertionError("starting scaled dual is not even integral")

    initial_shell = root_shell(nb, current, 2)
    if initial_shell["counts"] != {"0": 1, "2": EXPECTED_ROOT_COUNTS[0]}:
        raise AssertionError(f"starting root count drifted: {initial_shell}")

    steps = []
    root_counts = [EXPECTED_ROOT_COUNTS[0]]
    for step_index, support in enumerate(NEIGHBOR_SUPPORTS, start=1):
        dimension = len(current)
        v = tuple(int(i in set(support)) for i in range(dimension))
        neighbor_norm = nb.quadratic(v, current)
        if neighbor_norm.denominator != 1 or neighbor_norm.numerator % 8:
            raise AssertionError(
                f"step {step_index}: neighbor norm is not divisible by 8"
            )

        old_g = nb.matrix_scale(21, nb.inverse(current))
        basis = nb.construct_neighbor_basis(current, support)
        p = basis["P"]
        p_inverse = basis["P_inverse"]
        raw_next = nb.matmul(nb.matmul(nb.transpose(p), current), p)
        transformed_g = nb.matmul(
            nb.matmul(p_inverse, old_g), nb.transpose(p_inverse)
        )
        if transformed_g != nb.matrix_scale(21, nb.inverse(raw_next)):
            raise AssertionError(f"step {step_index}: scaled-dual transform")
        if not nb.is_even_integral_form(raw_next):
            raise AssertionError(f"step {step_index}: S neighbor not even")
        if not nb.is_even_integral_form(transformed_g):
            raise AssertionError(f"step {step_index}: G neighbor not even")
        if nb.determinant(raw_next) != 729:
            raise AssertionError(f"step {step_index}: determinant changed")

        raw_integer = imatrix(raw_next)
        lll_rows, lll_stats = tv.exact_lll_transform(raw_integer)
        if abs(nb.determinant(qmatrix(lll_rows))) != 1:
            raise AssertionError(f"step {step_index}: LLL not unimodular")
        reduced_integer = tv.matmul(
            tv.matmul(lll_rows, raw_integer), tv.transpose(lll_rows)
        )
        reduced = qmatrix(reduced_integer)
        reduced_g = nb.matrix_scale(21, nb.inverse(reduced))
        if not nb.is_even_integral_form(reduced):
            raise AssertionError(f"step {step_index}: reduced S not even")
        if not nb.is_even_integral_form(reduced_g):
            raise AssertionError(f"step {step_index}: reduced G not even")

        shell = root_shell(nb, reduced, 2)
        root_count = shell["counts"].get("2", 0)
        expected = EXPECTED_ROOT_COUNTS[step_index]
        if root_count != expected:
            raise AssertionError(
                f"step {step_index}: roots {root_count} != {expected}"
            )
        root_counts.append(root_count)
        steps.append({
            "step": step_index,
            "support_in_previous_reduced_basis": list(support),
            "neighbor_vector_norm": int(neighbor_norm),
            "parity_pivot": basis["pivot"],
            "half_vector_replacement_column": basis["replacement"],
            "neighbor_basis_P": json_matrix(p),
            "neighbor_basis_P_inverse": json_matrix(p_inverse),
            "det_P": json_scalar(basis["det_P"]),
            "raw_neighbor_gram_sha256": canonical_hash(json_matrix(raw_next)),
            "exact_lll_row_transform_U": lll_rows,
            "exact_lll_stats": lll_stats,
            "reduced_gram_sha256": canonical_hash(reduced_integer),
            "root_shell_through_norm_2": shell,
        })
        current = reduced

    final_integer = imatrix(current)
    final_hash = canonical_hash(final_integer)
    if final_hash != EXPECTED_FINAL_T20_HASH:
        raise AssertionError(f"final T20 hash drifted: {final_hash}")
    if root_counts != list(EXPECTED_ROOT_COUNTS):
        raise AssertionError(f"root chain drifted: {root_counts}")

    final_g = nb.matrix_scale(21, nb.inverse(current))
    final_three_dual = nb.matrix_scale(3, nb.inverse(current))
    if not nb.is_even_integral_form(final_three_dual):
        raise AssertionError("3*T20^-1 is not even integral")
    shell_four = root_shell(nb, current, 4)
    if shell_four["counts"] != {"0": 1, "4": 5076}:
        raise AssertionError(f"T20 norm-four shell drifted: {shell_four}")

    return {
        "starting_form": {
            "description": "K12 orthogonal_sum E8",
            "rank": 20,
            "determinant": 729,
            "root_count": EXPECTED_ROOT_COUNTS[0],
            "K12_gram_sha256": canonical_hash(k12),
            "E8_gram_sha256": canonical_hash(e8),
        },
        "neighbor_chain": steps,
        "root_count_chain": root_counts,
        "T20": {
            "rank": 20,
            "determinant": 729,
            "minimum": 4,
            "norm_two_count": 0,
            "norm_four_count": 5076,
            "gram": final_integer,
            "gram_sha256": final_hash,
            "scaled_dual_21_T20_inverse":
                imatrix(final_g),
            "scaled_dual_gram_sha256":
                canonical_hash(json_matrix(final_g)),
            "three_scaled_dual_is_even_integral": True,
            "three_scaled_dual_gram_sha256":
                canonical_hash(json_matrix(final_three_dual)),
            "shell_through_norm_4": shell_four,
        },
    }


def build_rank44_candidate(nb: Any, t20_data: dict[str, Any]) -> dict[str, Any]:
    t20 = qmatrix(t20_data["T20"]["gram"])
    leech = qmatrix(LEECH)
    if not nb.is_even_integral_form(leech):
        raise AssertionError("embedded Leech Gram is not even integral")
    if nb.determinant(leech) != 1:
        raise AssertionError("embedded Leech determinant is not one")
    leech_g = nb.inverse(leech)
    if not nb.is_even_integral_form(leech_g):
        raise AssertionError("Leech inverse is not even integral")
    leech_roots = root_shell(nb, leech, 2)
    if leech_roots["counts"] != {"0": 1}:
        raise AssertionError("embedded Leech Gram has a root")

    s44 = nb.block_diagonal([t20, leech])
    g44 = nb.matrix_scale(21, nb.inverse(s44))
    three_dual_44 = nb.matrix_scale(3, nb.inverse(s44))
    if len(s44) != 44:
        raise AssertionError("rank-44 assembly changed")
    if not nb.is_even_integral_form(s44):
        raise AssertionError("rank-44 S is not even integral")
    if not nb.is_even_integral_form(g44):
        raise AssertionError("rank-44 G is not even integral")
    if not nb.is_even_integral_form(three_dual_44):
        raise AssertionError("rank-44 3*S^-1 is not even integral")
    if nb.determinant(s44) != 729:
        raise AssertionError("rank-44 determinant changed")
    if nb.matmul(s44, g44) != nb.matrix_scale(21, nb.eye(44)):
        raise AssertionError("S44*G44 is not 21I")

    # Both summands have minimum four, so a norm-two vector of the direct
    # sum would have to be a root in one summand.  The two exact searches
    # above therefore prove rootlessness without a 44-dimensional search.
    return {
        "candidate_id": "W30-H729-T20-L24-001",
        "primary_status": "CANDIDATE",
        "evidence_label": "FINITE_COMPUTATIONAL_EVIDENCE",
        "description": "T20 orthogonal_sum embedded LAMBDA24",
        "rank": 44,
        "determinant": 729,
        "minimum": 4,
        "rootless": True,
        "exact_level": 3,
        "decomposition": [
            {
                "name": "T20",
                "rank": 20,
                "determinant": 729,
                "minimum": 4,
            },
            {
                "name": "LAMBDA24",
                "rank": 24,
                "determinant": 1,
                "minimum": 4,
            },
        ],
        "necessary_frame_row_split_if_realized": {
            "T20_rows": 105,
            "LAMBDA24_rows": 126,
            "derivation": "21*rank/4 in each minimum-four orthogonal block",
        },
        "S": imatrix(s44),
        "S_sha256": canonical_hash(json_matrix(s44)),
        "G_equals_21_S_inverse": imatrix(g44),
        "G_sha256": canonical_hash(json_matrix(g44)),
        "three_scaled_dual_is_even_integral": True,
        "three_scaled_dual_sha256":
            canonical_hash(json_matrix(three_dual_44)),
        "SG_equals_21I": True,
        "Leech": {
            "gram_sha256": canonical_hash(LEECH),
            "inverse_gram_sha256": canonical_hash(json_matrix(leech_g)),
            "determinant": 1,
            "minimum": 4,
            "root_shell_through_norm_2": leech_roots,
        },
        "passes": [
            "S is even integral symmetric positive definite",
            "rank(S)=44",
            "det(S)=729",
            "minimum(S)=4",
            "G=21*S^-1 is even integral symmetric positive definite",
            "S*G=21I",
            "the only surviving decomposable-rootless block ranks 20+24 are instantiated",
            "the rank-20 norm-four shell has 5076 vectors, exceeding the 210 signed-vector availability floor for 105 rows",
        ],
        "not_constructed": [
            "an even determinant-five Q",
            "B=S*Q with trace 60",
            "a 105-row tight frame on T20",
            "a 126-row tight frame on LAMBDA24",
            "the complete 231-row X",
            "M=X*S*X^T with the endpoint alphabet and row data",
            "Q=X^T*(M o M)*X",
            "a graph or Conway-99 configuration",
        ],
    }


def exact_result() -> dict[str, Any]:
    input_hashes = validate_inputs()
    nb = load_helper("wave30_neighbor_helper", NEIGHBOR_HELPER_PATH)
    tv = load_helper("wave30_lll_helper", LLL_HELPER_PATH)
    t20 = construct_t20(nb, tv)
    candidate = build_rank44_candidate(nb, t20)
    return {
        "scope": (
            "Exact five-neighbor construction of a rootless rank-20 "
            "determinant-729 form and a rootless rank-44 bare S/G endpoint "
            "candidate after adjoining an embedded Leech form."
        ),
        "status": "FINITE_COMPUTATIONAL_EVIDENCE",
        "frozen_inputs": input_hashes,
        "attributed_embedded_sources": {
            "K12": {
                **K12_SOURCE,
                "embedded_gram_sha256":
                    t20["starting_form"]["K12_gram_sha256"],
            },
            "LAMBDA24": {
                **LEECH_SOURCE,
                "embedded_gram_sha256":
                    candidate["Leech"]["gram_sha256"],
            },
        },
        "rank20_construction": t20,
        "rank44_candidate": candidate,
        "restrictions": {
            "neighbor_search": (
                "The five displayed supports are a discovered deterministic "
                "route, not a complete enumeration of the 2-neighbor graph."
            ),
            "orthogonal_ansatz": (
                "The rank-44 candidate explicitly assumes the decomposition "
                "T20 orthogonal_sum LAMBDA24."
            ),
            "automorphisms": "No automorphism of a target or candidate is assumed.",
            "frame_status": (
                "Shell size is only an availability check. No subset solving "
                "the tight-frame or pairwise alphabet equations is supplied."
            ),
            "global_status": (
                "The construction neither realizes nor excludes n3=708 and "
                "does not resolve Conway-99."
            ),
        },
    }


def render(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = exact_result()
    args.output.write_text(render(result), encoding="utf-8", newline="\n")
    candidate = result["rank44_candidate"]
    summary = {
        "candidate_id": candidate["candidate_id"],
        "status": result["status"],
        "rank": candidate["rank"],
        "determinant": candidate["determinant"],
        "minimum": candidate["minimum"],
        "root_count_chain":
            result["rank20_construction"]["root_count_chain"],
        "T20_norm_four_count":
            result["rank20_construction"]["T20"]["norm_four_count"],
        "T20_gram_sha256":
            result["rank20_construction"]["T20"]["gram_sha256"],
        "S44_sha256": candidate["S_sha256"],
        "output": str(args.output),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
