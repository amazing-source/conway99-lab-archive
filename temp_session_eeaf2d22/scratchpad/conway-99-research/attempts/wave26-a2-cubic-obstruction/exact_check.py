#!/usr/bin/env python3
"""Exact checker for the Wave 26 A2 cubic-tensor obstruction.

This checker deliberately has a narrow scope.  It proves that the explicit
Wave 24

    S = E8^5 direct_sum A2^2,
    Q = (E8^-1)^5 direct_sum A2^2

coordinate-lattice survivor cannot also possess the omitted 231-column
projector/Hadamard origin.  It does not reject every h=9 lattice package and
does not reject n3=708.

Only Python's standard library and exact integer arithmetic are used.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from itertools import product
from pathlib import Path
from typing import Any, Iterable, Sequence


PUBLIC_BASE = "1f22323a2805e3e24f7848d53f2f4813e236fae9"
N_TRIANGLES = 231
RANK = 44
PROJECTOR_SCALE = 21
N3 = 708

A2: tuple[tuple[int, int], tuple[int, int]] = ((2, -1), (-1, 2))
A2_INVERSE_TIMES_21: tuple[tuple[int, int], tuple[int, int]] = (
    (14, 7),
    (7, 14),
)
ROOT_REPRESENTATIVES: tuple[tuple[int, int], ...] = (
    (1, 0),
    (0, 1),
    (1, 1),
)

INPUTS = {
    "verification/2026-07-23-wave20-global-schur-audit.md": (
        "6311a893e1802382bfaaf00f8d366ba7f25ff036cda8032978dc5c6b4fdf35a3"
    ),
    "verification/wave24-n3-708-index/2026-07-23T204222Z-audit.md": (
        "958b9b2d13d697c281ba490d21b170f453d059bfaa952f8e92a9709b6c8d3cd8"
    ),
    "verification/wave24-n3-708-index/survivor-certificate.json": (
        "a217ec7211128f51e684030a7fe8d3c60ac80935f356ba5193dc34d36d4077a2"
    ),
}


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_frozen_inputs(root: Path | None = None) -> list[dict[str, Any]]:
    root = repository_root() if root is None else root
    rows: list[dict[str, Any]] = []
    for relative, expected in INPUTS.items():
        path = root / relative
        if not path.is_file():
            raise AssertionError(f"missing frozen input: {relative}")
        actual = sha256_file(path)
        if actual != expected:
            raise AssertionError(
                f"frozen input hash mismatch for {relative}: "
                f"expected {expected}, got {actual}"
            )
        rows.append(
            {
                "path": relative,
                "sha256": actual,
                "bytes": path.stat().st_size,
            }
        )
    return rows


def matmul(
    left: Sequence[Sequence[int]], right: Sequence[Sequence[int]]
) -> list[list[int]]:
    if not left or not right or len(left[0]) != len(right):
        raise AssertionError("incompatible matrix dimensions")
    return [
        [
            sum(left[i][k] * right[k][j] for k in range(len(right)))
            for j in range(len(right[0]))
        ]
        for i in range(len(left))
    ]


def trace(matrix: Sequence[Sequence[int]]) -> int:
    if any(len(row) != len(matrix) for row in matrix):
        raise AssertionError("trace requires a square matrix")
    return sum(matrix[i][i] for i in range(len(matrix)))


def block(
    matrix: Sequence[Sequence[int]], start: int, stop: int
) -> list[list[int]]:
    return [list(row[start:stop]) for row in matrix[start:stop]]


def validate_square_integer_matrix(
    name: str, matrix: object, size: int
) -> list[list[int]]:
    if not isinstance(matrix, list) or len(matrix) != size:
        raise AssertionError(f"{name} is not a {size}-row matrix")
    checked: list[list[int]] = []
    for row in matrix:
        if not isinstance(row, list) or len(row) != size:
            raise AssertionError(f"{name} is not a {size}-by-{size} matrix")
        if any(type(value) is not int for value in row):
            raise AssertionError(f"{name} contains a non-integer entry")
        checked.append(list(row))
    if any(checked[i][j] != checked[j][i] for i in range(size) for j in range(size)):
        raise AssertionError(f"{name} is not symmetric")
    return checked


def validate_explicit_survivor(root: Path | None = None) -> dict[str, Any]:
    root = repository_root() if root is None else root
    path = root / "verification/wave24-n3-708-index/survivor-certificate.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    matrices = payload.get("matrices")
    if not isinstance(matrices, dict):
        raise AssertionError("survivor certificate has no matrices object")

    a2 = validate_square_integer_matrix("A2", matrices.get("A2"), 2)
    if a2 != [list(row) for row in A2]:
        raise AssertionError(f"certificate A2 block changed: {a2}")

    checked = {
        name: validate_square_integer_matrix(name, matrices.get(name), RANK)
        for name in ("S", "Q", "G", "B")
    }
    expected_a2 = [list(row) for row in A2]
    expected_g = [list(row) for row in A2_INVERSE_TIMES_21]
    expected_b = matmul(expected_a2, expected_a2)

    block_rows: list[dict[str, Any]] = []
    for start in (40, 42):
        stop = start + 2
        if block(checked["S"], start, stop) != expected_a2:
            raise AssertionError(f"S block {start}:{stop} is not A2")
        if block(checked["Q"], start, stop) != expected_a2:
            raise AssertionError(f"Q block {start}:{stop} is not A2")
        if block(checked["G"], start, stop) != expected_g:
            raise AssertionError(f"G block {start}:{stop} is not 21*A2^-1")
        if block(checked["B"], start, stop) != expected_b:
            raise AssertionError(f"B block {start}:{stop} is not A2^2")

        for name in ("S", "Q", "G", "B"):
            matrix = checked[name]
            for i in range(start, stop):
                for j in range(RANK):
                    if not (start <= j < stop) and matrix[i][j] != 0:
                        raise AssertionError(
                            f"{name} block {start}:{stop} is not orthogonal"
                        )

        block_rows.append(
            {
                "coordinates": [start, stop - 1],
                "S": expected_a2,
                "Q": expected_a2,
                "G": expected_g,
                "B": expected_b,
                "trace_SQ": trace(expected_b),
            }
        )

    if any(checked["S"][i][i] % 2 for i in range(RANK)):
        raise AssertionError("S is not even")

    return {
        "certificate_path": (
            "verification/wave24-n3-708-index/survivor-certificate.json"
        ),
        "rank": RANK,
        "orthogonal_A2_blocks": block_rows,
        "all_S_diagonal_entries_even": True,
    }


def a2_inner(
    left: Sequence[int],
    right: Sequence[int],
    gram: Sequence[Sequence[int]] = A2,
) -> int:
    if len(left) != 2 or len(right) != 2:
        raise AssertionError("A2 vectors must have two coordinates")
    return sum(left[i] * gram[i][j] * right[j] for i in range(2) for j in range(2))


def canonical_line(vector: tuple[int, int]) -> tuple[int, int]:
    if vector == (0, 0):
        raise AssertionError("zero has no unoriented line")
    for value in vector:
        if value:
            if value < 0:
                return (-vector[0], -vector[1])
            return vector
    raise AssertionError("unreachable")


def a2_small_vector_classification() -> dict[str, Any]:
    # For f(a,b)=a^2-ab+b^2, reduction modulo three gives only 0 or 1.
    residue_values = sorted(
        {
            (a * a - a * b + b * b) % 3
            for a in range(3)
            for b in range(3)
        }
    )
    if residue_values != [0, 1]:
        raise AssertionError(f"unexpected A2 norm residues: {residue_values}")

    # q(a,b)=2f(a,b).  q=4 would require f=2, impossible modulo three.
    # For q<=4, 4f=(2a-b)^2+3b^2<=8, so |a|,|b|<=2.
    vectors_by_norm: dict[int, list[tuple[int, int]]] = {}
    for target in (0, 2, 4):
        vectors_by_norm[target] = sorted(
            vector
            for vector in product(range(-2, 3), repeat=2)
            if a2_inner(vector, vector) == target
        )

    expected_roots = sorted(
        [
            (-1, -1),
            (-1, 0),
            (0, -1),
            (0, 1),
            (1, 0),
            (1, 1),
        ]
    )
    if vectors_by_norm[0] != [(0, 0)]:
        raise AssertionError("A2 has a nonzero norm-zero vector")
    if vectors_by_norm[2] != expected_roots:
        raise AssertionError(f"unexpected A2 roots: {vectors_by_norm[2]}")
    if vectors_by_norm[4]:
        raise AssertionError(f"A2 unexpectedly represents four: {vectors_by_norm[4]}")

    lines = sorted({canonical_line(vector) for vector in expected_roots})
    if lines != sorted(ROOT_REPRESENTATIVES):
        raise AssertionError(f"unexpected A2 root lines: {lines}")

    return {
        "norm_form": "2*(a^2-a*b+b^2)",
        "residues_of_a2_minus_ab_plus_b2_mod_3": residue_values,
        "norm_2_vectors": [list(vector) for vector in expected_roots],
        "norm_4_vectors": [],
        "unoriented_root_lines": [list(vector) for vector in ROOT_REPRESENTATIVES],
    }


def solve_root_line_counts(
    moment: Sequence[Sequence[int]] = A2_INVERSE_TIMES_21,
) -> tuple[int, int, int]:
    """Solve counts on e1, e2, e1+e2 from their outer-product sum."""

    if len(moment) != 2 or any(len(row) != 2 for row in moment):
        raise AssertionError("moment must be two-by-two")
    if moment[0][1] != moment[1][0]:
        raise AssertionError("moment is not symmetric")
    n_gamma = moment[0][1]
    n_alpha = moment[0][0] - n_gamma
    n_beta = moment[1][1] - n_gamma
    counts = (n_alpha, n_beta, n_gamma)
    if any(value < 0 for value in counts):
        raise AssertionError(f"negative root-line count: {counts}")
    return counts


def cubic_gram(
    roots: Sequence[Sequence[int]] = ROOT_REPRESENTATIVES,
) -> list[list[int]]:
    return [
        [a2_inner(left, right) ** 3 for right in roots]
        for left in roots
    ]


def quadratic_form(
    matrix: Sequence[Sequence[int]], vector: Sequence[int]
) -> int:
    if len(matrix) != len(vector) or any(len(row) != len(vector) for row in matrix):
        raise AssertionError("quadratic-form dimensions disagree")
    return sum(
        vector[i] * matrix[i][j] * vector[j]
        for i in range(len(vector))
        for j in range(len(vector))
    )


def cubic_norm_decomposition(d: Sequence[int]) -> dict[str, int]:
    if len(d) != 3:
        raise AssertionError("three signed line imbalances are required")
    d1, d2, d3 = d
    six_norm = 6 * (d1 * d1 + d2 * d2 + d3 * d3)
    square_remainder = (
        (d1 - d2) ** 2 + (d1 + d3) ** 2 + (d2 + d3) ** 2
    )
    direct = quadratic_form(cubic_gram(), d)
    if direct != six_norm + square_remainder:
        raise AssertionError("cubic norm decomposition failed")
    return {
        "direct": direct,
        "six_times_coordinate_norm": six_norm,
        "sum_of_three_squares": square_remainder,
    }


def signed_imbalances(
    counts: Sequence[int],
    require_zero_sum: bool,
) -> list[tuple[int, tuple[int, int, int]]]:
    if len(counts) != 3:
        raise AssertionError("three line counts are required")
    value_sets = [range(-count, count + 1, 2) for count in counts]
    rows: list[tuple[int, tuple[int, int, int]]] = []
    for raw in product(*value_sets):
        d = (int(raw[0]), int(raw[1]), int(raw[2]))
        if require_zero_sum:
            # d1*e1+d2*e2+d3*(e1+e2)=0.
            if d[0] + d[2] != 0 or d[1] + d[2] != 0:
                continue
        rows.append((quadratic_form(cubic_gram(), d), d))
    return sorted(rows)


def prove_a2_cubic_floor() -> dict[str, Any]:
    classification = a2_small_vector_classification()
    counts = solve_root_line_counts()
    if counts != (7, 7, 7):
        raise AssertionError(f"expected seven vectors on each root line, got {counts}")

    gram = cubic_gram()
    expected_gram = [[8, -1, 1], [-1, 8, 1], [1, 1, 8]]
    if gram != expected_gram:
        raise AssertionError(f"wrong cubic Gram matrix: {gram}")

    # Each signed imbalance has the parity of its line count, hence is odd.
    all_signed = signed_imbalances(counts, require_zero_sum=False)
    minimum_all = all_signed[0][0]
    if minimum_all != 18:
        raise AssertionError(f"wrong odd-imbalance cubic floor: {minimum_all}")

    zero_sum = signed_imbalances(counts, require_zero_sum=True)
    expected_zero_sum = [
        (18 * t * t, (t, t, -t))
        for t in (-7, -5, -3, -1, 1, 3, 5, 7)
    ]
    if sorted(zero_sum) != sorted(expected_zero_sum):
        raise AssertionError(f"wrong zero-sum imbalance list: {zero_sum}")

    equality = cubic_norm_decomposition((1, 1, -1))
    if equality["direct"] != 18 or equality["sum_of_three_squares"] != 0:
        raise AssertionError("cubic floor equality control failed")

    return {
        "small_vectors": classification,
        "frame_block_moment": [list(row) for row in A2_INVERSE_TIMES_21],
        "root_line_counts": list(counts),
        "signed_line_imbalances_are_odd": True,
        "cubic_gram": gram,
        "exact_norm_identity": (
            "d^T H d = 6*(d1^2+d2^2+d3^2)"
            " +(d1-d2)^2+(d1+d3)^2+(d2+d3)^2"
        ),
        "minimum_pure_A2_cubic_norm_squared": minimum_all,
        "zero_sum_signed_imbalances": [
            {"imbalance": list(d), "norm_squared": norm}
            for norm, d in zero_sum
        ],
        "active_premises": [
            "orthogonal even A2 summand of S",
            "231-column row norms x_i^T*S*x_i=4",
            "sum_i x_i*x_i^T=21*S^-1",
        ],
        "not_needed_for_floor_but_checked": "M*1=0",
    }


def endpoint_histogram() -> dict[int, int]:
    two_n3_over_three = 2 * N3 // 3
    if 3 * two_n3_over_three != 2 * N3:
        raise AssertionError("n3 is not divisible by three")
    return {
        4: N_TRIANGLES,
        1: 4620 + two_n3_over_three,
        0: N_TRIANGLES * 18 + (41580 - 2 * N3),
        -1: 2 * N3,
        -2: 2772 - two_n3_over_three,
    }


def histogram_moment(histogram: dict[int, int], power: int) -> int:
    if power < 0:
        raise AssertionError("moment power must be nonnegative")
    return sum(count * (value**power) for value, count in histogram.items())


def validate_endpoint_histogram(
    histogram: dict[int, int] | None = None,
) -> dict[str, Any]:
    histogram = endpoint_histogram() if histogram is None else histogram
    if set(histogram) != {4, 1, 0, -1, -2}:
        raise AssertionError("M entry histogram is incomplete")
    if any(type(count) is not int or count < 0 for count in histogram.values()):
        raise AssertionError("M entry histogram has an invalid count")
    if sum(histogram.values()) != N_TRIANGLES * N_TRIANGLES:
        raise AssertionError("M entry histogram does not contain 231^2 entries")

    moments = {power: histogram_moment(histogram, power) for power in range(1, 5)}
    expected = {
        1: 0,
        2: PROJECTOR_SCALE * (4 * N_TRIANGLES),
        3: 4 * (N3 - 693),
        4: 102444,
    }
    if moments != expected:
        raise AssertionError(f"wrong endpoint moments: {moments}, expected {expected}")

    # W=M o M has row sum 16+a0+a2+4*a3=84 for every q.
    row_sums = {
        q: 16 + (20 + q) + (3 * q) + 4 * (12 - q)
        for q in range(13)
    }
    if set(row_sums.values()) != {84}:
        raise AssertionError(f"W row sum depends on q: {row_sums}")

    return {
        "ordered_entry_histogram": {
            str(value): histogram[value] for value in (4, 1, 0, -1, -2)
        },
        "moments": {str(power): value for power, value in moments.items()},
        "identities": {
            "sum_M_entries": 0,
            "sum_M_squared": "tr(M^2)=21*tr(M)=19404",
            "sum_M_cubed": "||sum_i u_i^(tensor 3)||^2=60",
            "sum_M_fourth": "tr((M o M)^2)=102444",
            "W_row_sum": 84,
        },
    }


def tensor_bridge() -> dict[str, Any]:
    return {
        "hypothetical_integer_basis": "X in Z^(231 x 44), X^T X=G",
        "projector_gram": "M=X*S*X^T, where S=21*G^-1",
        "row_vectors": "u_i=S^(1/2)*x_i",
        "tight_frame": "sum_i u_i*u_i^T=21*I_44",
        "zero_sum": "M*1=0 implies sum_i u_i=0",
        "schur_square": "W=M o M",
        "cubic_tensor": "T=sum_i u_i^(tensor 3)",
        "flattening": "Phi(v)=contraction_v(T)=sum_i <v,u_i>*u_i tensor u_i",
        "coordinate_schur_gram": "Q=X^T*W*X",
        "orthogonal_schur_gram": "K=Phi^*Phi=S^(1/2)*Q*S^(1/2)",
        "trace": "tr(K)=||T||^2=sum_(i,j)<u_i,u_j>^3=60",
        "harmonicity": "trace_2(T)=4*sum_i u_i=0",
        "block_inequality": (
            "For an orthogonal A2 summand A, "
            "tr(K compressed to A)>=||proj_(A tensor A tensor A) T||^2"
        ),
        "integer_cubic_certificate": {
            "P_abc": "sum_i X_ia*X_ib*X_ic in Z",
            "trace_free": "sum_(b,c) S_bc*P_abc=0",
            "Q_factorization": (
                "Q_ab=sum_(c,e,d,f) P_ace*S_cd*S_ef*P_bdf"
            ),
        },
    }


def evaluate_explicit_survivor(root: Path | None = None) -> dict[str, Any]:
    certificate = validate_explicit_survivor(root)
    lemma = prove_a2_cubic_floor()
    lower = lemma["minimum_pure_A2_cubic_norm_squared"]
    blocks = certificate["orthogonal_A2_blocks"]
    if len(blocks) != 2:
        raise AssertionError("expected exactly two audited A2 blocks")

    tested: list[dict[str, Any]] = []
    for row in blocks:
        available_trace = row["trace_SQ"]
        if available_trace >= lower:
            verdict = "NOT_EXCLUDED"
        else:
            verdict = "REFUTED_AS_FULL_SCHUR_ORIGIN"
        tested.append(
            {
                "coordinates": row["coordinates"],
                "trace_of_K_compression": available_trace,
                "required_pure_cubic_norm_squared_floor": lower,
                "gap": lower - available_trace,
                "verdict": verdict,
            }
        )

    if any(row["verdict"] != "REFUTED_AS_FULL_SCHUR_ORIGIN" for row in tested):
        raise AssertionError("explicit survivor was not contradicted")

    return {
        "general_A2_summand_necessary_condition": (
            "tr(A2*Q_AA)>=18 for every orthogonal A2 summand of S"
        ),
        "two_A2_total_compression_floor": 2 * lower,
        "explicit_blocks": tested,
        "explicit_survivor_full_projector_schur_origin": "REFUTED",
        "scope_guard": {
            "explicit_coordinate_lattice_relaxation_still_valid": True,
            "all_h_equals_9_packages_excluded": False,
            "n3_equals_708_excluded": False,
            "conway_99_resolved": False,
        },
    }


def hostile_controls() -> dict[str, Any]:
    # If the scale were 18, each A2 root line would occur six times.  Balanced
    # signs then give zero pure cubic tensor, so the odd scale 21 is active.
    scale_18_moment = ((12, 6), (6, 12))
    scale_18_counts = solve_root_line_counts(scale_18_moment)
    scale_18_zero_sum = signed_imbalances(scale_18_counts, require_zero_sum=True)
    scale_18_minimum = scale_18_zero_sum[0]
    if scale_18_counts != (6, 6, 6) or scale_18_minimum != (0, (0, 0, 0)):
        raise AssertionError("even-line-count hostile control failed")

    doubled_q = [[2 * value for value in row] for row in A2]
    doubled_trace = trace(matmul([list(row) for row in A2], doubled_q))
    if doubled_trace != 20:
        raise AssertionError("doubled-Q hostile control failed")

    wrong_histogram = endpoint_histogram()
    wrong_histogram[-1] -= 2
    wrong_histogram[0] += 2
    histogram_mutation_detected = False
    try:
        validate_endpoint_histogram(wrong_histogram)
    except AssertionError:
        histogram_mutation_detected = True
    if not histogram_mutation_detected:
        raise AssertionError("entry-histogram mutation was missed")

    wrong_gram = ((2, 0), (0, 2))
    fake_norm_four = [
        vector
        for vector in product(range(-2, 3), repeat=2)
        if a2_inner(vector, vector, wrong_gram) == 4
    ]
    if not fake_norm_four:
        raise AssertionError("wrong-Gram hostile control has no norm-four vectors")

    return {
        "scale_18_even_line_counts": {
            "line_counts": list(scale_18_counts),
            "zero_sum_minimum_cubic_norm_squared": scale_18_minimum[0],
            "status": "OBSTRUCTION_CORRECTLY_DISAPPEARS",
        },
        "double_Q_block": {
            "trace_A2_times_2A2": doubled_trace,
            "required_floor": 18,
            "status": "TRACE_CONTRADICTION_CORRECTLY_DISAPPEARS",
        },
        "ordered_histogram_mutation": {
            "status": "DETECTED" if histogram_mutation_detected else "MISSED"
        },
        "replace_A2_by_diagonal_even_gram": {
            "norm_four_vectors_exist": True,
            "example": list(fake_norm_four[0]),
            "status": "A2_ROOT_CLASSIFICATION_CORRECTLY_REJECTED",
        },
    }


def build_results(root: Path | None = None) -> dict[str, Any]:
    root = repository_root() if root is None else root
    return {
        "base_commit": PUBLIC_BASE,
        "claim": {
            "label": "DERIVED",
            "scope": (
                "The explicit Wave 24 E8^5 direct-sum A2^2 coordinate-lattice "
                "survivor cannot have the omitted 231-column projector/"
                "Hadamard-Schur origin."
            ),
            "endpoint_status": "UNKNOWN",
            "novelty_status": "UNKNOWN",
        },
        "frozen_inputs": validate_frozen_inputs(root),
        "n3_708_frame_moments": validate_endpoint_histogram(),
        "tensor_bridge": tensor_bridge(),
        "a2_cubic_floor": prove_a2_cubic_floor(),
        "explicit_survivor_test": evaluate_explicit_survivor(root),
        "hostile_controls": hostile_controls(),
        "limitations": [
            "This rejects the Schur origin of one explicit abstract survivor, "
            "not the abstract coordinate-lattice identities it was designed to satisfy.",
            "It does not exclude every h=9 lattice package or any of the other "
            "seven necessary index values.",
            "It supplies no primitive embedding, projector matrix, graph, "
            "target resolution, or novelty determination.",
        ],
    }


def canonical_json(payload: object) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def write_results(output: Path, payload: object) -> None:
    output.write_text(canonical_json(payload), encoding="utf-8", newline="\n")


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("exact-results.json"),
        help="deterministic JSON output path",
    )
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    payload = build_results()
    write_results(args.output, payload)
    print(canonical_json(payload), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
