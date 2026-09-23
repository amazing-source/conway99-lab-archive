"""Exact HNF certificate for the integral Wave143 equality layer."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path

from flint import fmpz_mat

sys.set_int_max_str_digits(0)


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OPTIMIZE_PATH = HERE / "optimize_rational.py"


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODEL = load("wave143_lattice_model", OPTIMIZE_PATH)
BASE = MODEL.BASE
WEIGHTS = tuple(BASE.IMAGE_WEIGHTS)
N_A = len(WEIGHTS)
N_D = BASE.N + 1
UNKNOWN_NAMES = (
    tuple(f"A_{weight}" for weight in WEIGHTS)
    + tuple(f"D_{degree}" for degree in range(N_D))
    + ("k",)
)


def equality_system(sign: int) -> tuple[list[list[int]], list[int], list[str]]:
    width = len(UNKNOWN_NAMES)
    rows: list[list[int]] = []
    rhs: list[int] = []
    labels: list[str] = []

    def blank() -> list[int]:
        return [0] * width

    def add(row: list[int], value: int, label: str) -> None:
        rows.append(row)
        rhs.append(value)
        labels.append(label)

    row = blank()
    row[0] = 1
    add(row, 1, "A0")

    row = blank()
    for index in range(N_A):
        row[index] = 1
    add(row, BASE.ORDER, "image_size")

    for degree in range(N_D):
        row = blank()
        for index, weight in enumerate(WEIGHTS):
            row[index] = BASE.krawtchouk(degree, weight)
        row[N_A + degree] = -BASE.ORDER
        add(row, 0, f"MacWilliams_{degree}")

    for degree, multiplier in MODEL.S_VALUES.items():
        row = blank()
        for index, weight in enumerate(WEIGHTS):
            row[index] = (
                MODEL.signed(weight)
                * BASE.krawtchouk(degree, weight)
            )
        add(
            row,
            sign * MODEL.ARF_MAGNITUDE * multiplier,
            f"signed_M{degree}",
        )

    # Write n3=3k.  The exact target becomes
    # M6 = sign*2^27*(2024484+512k).
    row = blank()
    for index, weight in enumerate(WEIGHTS):
        row[index] = (
            MODEL.signed(weight) * BASE.krawtchouk(6, weight)
        )
    row[-1] = -sign * MODEL.ARF_MAGNITUDE * 512
    add(
        row,
        sign * MODEL.ARF_MAGNITUDE * MODEL.S6_CONSTANT,
        "signed_M6_target",
    )
    return rows, rhs, labels


def canonical_matrix_digest(
    rows: list[list[int]],
    rhs: list[int],
    labels: list[str],
) -> str:
    payload = json.dumps(
        {"rows": rows, "rhs": rhs, "labels": labels},
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def hnf_data(sign: int):
    rows, rhs, labels = equality_system(sign)
    matrix = fmpz_mat(rows)
    hnf, transform = matrix.transpose().hnf(transform=True)
    rank = hnf.rank()
    if rank != len(rows):
        raise AssertionError("equality rows unexpectedly dependent")

    nonzero_hnf = fmpz_mat(
        rank,
        hnf.ncols(),
        [
            hnf[row, column]
            for row in range(rank)
            for column in range(hnf.ncols())
        ],
    )
    rhs_column = fmpz_mat(len(rhs), 1, rhs)
    coefficients = nonzero_hnf.transpose().solve(rhs_column)
    nonzero_transform = fmpz_mat(
        rank,
        transform.ncols(),
        [
            transform[row, column]
            for row in range(rank)
            for column in range(transform.ncols())
        ],
    )
    particular_q = coefficients.transpose() * nonzero_transform
    particular = []
    for column in range(particular_q.ncols()):
        value = particular_q[0, column]
        if value.denominator != 1:
            raise AssertionError("HNF particular solution is not integral")
        particular.append(int(value.numerator))
    if matrix * fmpz_mat(len(particular), 1, particular) != rhs_column:
        raise AssertionError("particular solution replay failed")
    return (
        matrix,
        rhs,
        labels,
        hnf,
        transform,
        rank,
        particular,
    )


def extended_gcd(values: list[int]) -> tuple[int, list[int]]:
    gcd_value = 0
    coefficients: list[int] = []
    for value in values:
        old_gcd = gcd_value
        if not coefficients:
            gcd_value = abs(value)
            coefficients = [0 if value == 0 else (1 if value > 0 else -1)]
            continue
        a, b = old_gcd, value
        old_r, r = a, abs(b)
        old_s, s = 1, 0
        old_t, t = 0, 1
        while r:
            quotient = old_r // r
            old_r, r = r, old_r - quotient * r
            old_s, s = s, old_s - quotient * s
            old_t, t = t, old_t - quotient * t
        sign_b = 1 if b >= 0 else -1
        coefficients = [old_s * item for item in coefficients]
        coefficients.append(old_t * sign_b)
        gcd_value = old_r
    return gcd_value, coefficients


def sparse_vector(vector: list[int]) -> dict[str, str]:
    return {
        name: str(value)
        for name, value in zip(UNKNOWN_NAMES, vector)
        if value
    }


def vector_record(vector: list[int]) -> dict[str, object]:
    encoded = ",".join(str(value) for value in vector).encode("ascii")
    return {
        "sha256": hashlib.sha256(encoded).hexdigest(),
        "nonzero_coordinates": sum(value != 0 for value in vector),
        "maximum_decimal_digits": max(
            len(str(abs(value))) for value in vector
        ),
        "k": str(vector[-1]),
        "stored_in_full": False,
        "exactly_reconstructed_and_replayed_by": "lattice_certificate.py",
    }


def build_certificate() -> dict:
    (
        plus_matrix,
        plus_rhs,
        plus_labels,
        _plus_hnf,
        plus_transform,
        rank,
        plus_particular,
    ) = hnf_data(1)
    (
        minus_matrix,
        minus_rhs,
        minus_labels,
        _minus_hnf,
        _minus_transform,
        minus_rank,
        minus_particular,
    ) = hnf_data(-1)
    if minus_rank != rank or minus_labels != plus_labels:
        raise AssertionError("Arf branch equality rank drift")

    null_rows = list(range(rank, plus_transform.nrows()))
    k_column = plus_transform.ncols() - 1
    k_values = [
        int(plus_transform[row, k_column]) for row in null_rows
    ]
    projection_gcd, bezout = extended_gcd(k_values)
    if projection_gcd != 1:
        raise AssertionError(
            f"unexpected equality-lattice k step: {projection_gcd}"
        )
    delta = [0] * plus_transform.ncols()
    for coefficient, row in zip(bezout, null_rows):
        if not coefficient:
            continue
        for column in range(plus_transform.ncols()):
            delta[column] += coefficient * int(
                plus_transform[row, column]
            )
    if delta[-1] != 1:
        raise AssertionError("Bezout kernel step does not have delta k=1")

    zero_rhs = fmpz_mat(plus_matrix.nrows(), 1)
    if plus_matrix * fmpz_mat(len(delta), 1, delta) != zero_rhs:
        raise AssertionError("plus homogeneous step replay failed")
    minus_delta = [-value for value in delta]
    minus_delta[-1] = 1
    if minus_matrix * fmpz_mat(len(minus_delta), 1, minus_delta) != zero_rhs:
        raise AssertionError("minus homogeneous step replay failed")
    if plus_particular[-1] != 0 or minus_particular[-1] != 0:
        raise AssertionError("particular solutions are not at k=0")

    # The target equation before introducing k is
    # 3 M6 = sign*2^27*(3*2024484+512*n3).  Modulo 3, the coefficient
    # 2^27*512 is 1, so every integral M6 forces n3=0 mod 3.
    modulo_three_coefficient = (
        MODEL.ARF_MAGNITUDE * 512
    ) % 3
    if modulo_three_coefficient != 1:
        raise AssertionError("modulo-three target coefficient drift")

    return {
        "format": "wave143-integral-equality-lattice-v1",
        "claim_label": "VERIFIED_BY_EXACT_REPLAY",
        "scope": (
            "Integral ordinary MacWilliams equality lattice with A_w,D_t,k "
            "integral and n3=3k; inequalities and nonnegativity excluded"
        ),
        "unknown_count": len(UNKNOWN_NAMES),
        "equation_count": plus_matrix.nrows(),
        "rank": rank,
        "nullity": plus_transform.nrows() - rank,
        "matrix_sha256": {
            "plus": canonical_matrix_digest(
                equality_system(1)[0],
                plus_rhs,
                plus_labels,
            ),
            "minus": canonical_matrix_digest(
                equality_system(-1)[0],
                minus_rhs,
                minus_labels,
            ),
        },
        "obstruction": {
            "equation": (
                "3*M6=sign*2^27*(3*2024484+512*n3)"
            ),
            "modulo_3_coefficient_of_n3": modulo_three_coefficient,
            "necessary_residue": "n3 == 0 (mod 3)",
        },
        "projection": {
            "coordinate": "k=n3/3",
            "kernel_projection_gcd": projection_gcd,
            "exact_admissible_residues_at_equality_layer": (
                "all k in Z, equivalently exactly n3 == 0 (mod 3)"
            ),
        },
        "particular_solutions_k0": {
            "plus": vector_record(plus_particular),
            "minus": vector_record(minus_particular),
        },
        "homogeneous_steps_delta_k1": {
            "plus": vector_record(delta),
            "minus": vector_record(minus_delta),
        },
        "limitations": [
            "The certificate permits negative coefficients.",
            "It proves the equality-lattice projection only.",
            "Nonnegativity, lower bounds, and shadow inequalities may remove residues or all points.",
            "It does not construct a code or graph.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=HERE / "lattice-certificate.json",
    )
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    payload = build_certificate()
    encoded = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.verify:
        if args.output.read_text(encoding="utf-8") != encoded:
            raise SystemExit("canonical lattice certificate mismatch")
    else:
        args.output.write_text(
            encoded,
            encoding="utf-8",
            newline="\n",
        )
    print(
        "PASS: equality lattice has exactly n3=0 mod 3; "
        f"rank={payload['rank']}, nullity={payload['nullity']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
