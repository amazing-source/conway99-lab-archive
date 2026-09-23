"""Clean-room exact verifier for Wave 128.

This module does not import the discovery checker.  It rebuilds the motif
incidence data, uses an integer Smith reduction (rather than the discovery
package's local DVR routine), and enumerates the finite quadratic modules
directly with exact rational and cyclotomic arithmetic.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from fractions import Fraction
from itertools import combinations, product
from math import isqrt, lcm
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
DISCOVERY = ROOT / "attempts" / "wave128-alternative-spaces"
N_OUTSIDE = 87
N_MOTIF = 12
PRIMES = (2, 3, 5, 7)
EXPECTED_DISCOVERY_MANIFEST_SHA256 = (
    "851df7c40ab2056f6a5f927093707e5e9b578df2b18662e6b95fcf6335033038"
)
EXPECTED_INPUTS = {
    "attempts/wave105-c4boxk3-extension/package-manifest.sha256":
        "b0fd40eda5a3677d4a835788cea20dfcb9bb3c5764719fc04536893f1b5da4a1",
    "verification/wave105-c4boxk3-extension/package-manifest.sha256":
        "2a24e3e5846558a9e93cd2f103e049816cef7f8dd4a200108643e44cc4c300ae",
    "attempts/wave107-c4boxk3-spectrum/package-manifest.sha256":
        "7e899602825d3cdf989affade8a1e5a6256f17ba911f6351ea8bfe4a3b05d2b0",
    "attempts/wave109-c4boxk3-local-projector/package-manifest.sha256":
        "6d54d48dbb6b1ffd3f7da845792fc12ee490471c02cc8137ebd1b03c21f5347e",
    "verification/wave109-c4boxk3-local-projector/package-manifest.sha256":
        "fcbb970eebf0b92cb012f5f2e81ccb8c6315c002c1f228f830cd1b0b082e62cd",
}


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical(data: object) -> str:
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def transpose(a: list[list[int]]) -> list[list[int]]:
    return [list(column) for column in zip(*a)]


def multiply(a: list[list[int]], b: list[list[int]]) -> list[list[int]]:
    ensure(a and b and len(a[0]) == len(b), "matrix dimension mismatch")
    return [
        [
            sum(a[i][t] * b[t][j] for t in range(len(b)))
            for j in range(len(b[0]))
        ]
        for i in range(len(a))
    ]


def horizontal(a: list[list[int]], b: list[list[int]]) -> list[list[int]]:
    ensure(len(a) == len(b), "horizontal concatenation mismatch")
    return [a[i] + b[i] for i in range(len(a))]


def bareiss_det(a: list[list[int]]) -> int:
    work = [row[:] for row in a]
    n = len(work)
    ensure(all(len(row) == n for row in work), "determinant needs square matrix")
    sign = 1
    previous = 1
    for k in range(n - 1):
        if work[k][k] == 0:
            pivot = next((r for r in range(k + 1, n) if work[r][k]), None)
            if pivot is None:
                return 0
            work[k], work[pivot] = work[pivot], work[k]
            sign = -sign
        value = work[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                numerator = work[i][j] * value - work[i][k] * work[k][j]
                ensure(numerator % previous == 0, "nonexact Bareiss step")
                work[i][j] = numerator // previous
            work[i][k] = 0
        previous = value
    return sign * work[-1][-1]


def solve_exact(a: list[list[int]], b: list[list[int]]) -> list[list[Fraction]]:
    n = len(a)
    ensure(all(len(row) == n for row in a) and len(b) == n, "bad exact solve")
    work = [
        [Fraction(value) for value in a[i] + b[i]]
        for i in range(n)
    ]
    width = len(work[0])
    for k in range(n):
        pivot = next((r for r in range(k, n) if work[r][k]), None)
        ensure(pivot is not None, "singular exact system")
        work[k], work[pivot] = work[pivot], work[k]
        divisor = work[k][k]
        work[k] = [value / divisor for value in work[k]]
        for r in range(n):
            if r == k or work[r][k] == 0:
                continue
            factor = work[r][k]
            work[r] = [
                work[r][j] - factor * work[k][j] for j in range(width)
            ]
    return [row[n:] for row in work]


def smith_diagonal_integer(a: list[list[int]]) -> list[int]:
    """Integer Smith diagonal via Euclidean unimodular row/column moves."""

    work = [row[:] for row in a]
    rows = len(work)
    columns = len(work[0]) if work else 0
    ensure(all(len(row) == columns for row in work), "ragged Smith matrix")
    k = 0
    while k < min(rows, columns):
        positions = [
            (abs(work[i][j]), i, j)
            for i in range(k, rows)
            for j in range(k, columns)
            if work[i][j]
        ]
        if not positions:
            break
        _, pivot_row, pivot_column = min(positions)
        work[k], work[pivot_row] = work[pivot_row], work[k]
        for row in work:
            row[k], row[pivot_column] = row[pivot_column], row[k]

        while True:
            restarted = False
            for i in range(k + 1, rows):
                if work[i][k] == 0:
                    continue
                quotient = work[i][k] // work[k][k]
                work[i] = [
                    work[i][j] - quotient * work[k][j]
                    for j in range(columns)
                ]
                if work[i][k]:
                    work[k], work[i] = work[i], work[k]
                restarted = True
                break
            if restarted:
                continue
            for j in range(k + 1, columns):
                if work[k][j] == 0:
                    continue
                quotient = work[k][j] // work[k][k]
                for i in range(rows):
                    work[i][j] -= quotient * work[i][k]
                if work[k][j]:
                    for row in work:
                        row[k], row[j] = row[j], row[k]
                restarted = True
                break
            if restarted:
                continue

            bad = next(
                (
                    (i, j)
                    for i in range(k + 1, rows)
                    for j in range(k + 1, columns)
                    if work[i][j] % work[k][k]
                ),
                None,
            )
            if bad is None:
                break
            bad_row, _ = bad
            work[k] = [
                work[k][j] + work[bad_row][j] for j in range(columns)
            ]

        if work[k][k] < 0:
            work[k] = [-value for value in work[k]]
        k += 1

    diagonal = [abs(work[i][i]) for i in range(min(rows, columns))]
    nonzero = [value for value in diagonal if value]
    ensure(
        all(nonzero[i + 1] % nonzero[i] == 0 for i in range(len(nonzero) - 1)),
        "Smith divisibility chain failed",
    )
    return diagonal


def p_valuations(diagonal: list[int], prime: int) -> list[int]:
    values: list[int] = []
    for entry in diagonal:
        exponent = 0
        while entry and entry % prime == 0:
            entry //= prime
            exponent += 1
        if exponent:
            values.append(exponent)
    return values


def motif_graph() -> list[list[int]]:
    vertices = [(c, t) for c in range(4) for t in range(3)]
    return [
        [
            int(
                (ci == cj and ti != tj)
                or (ti == tj and (ci - cj) % 4 in (1, 3))
            )
            for cj, tj in vertices
        ]
        for ci, ti in vertices
    ]


def outside_patterns() -> tuple[tuple[int, ...], ...]:
    h = motif_graph()
    result: list[tuple[int, ...]] = [()] * 3
    for i in range(N_MOTIF):
        result.extend([(i,)] * 4)
    for i, j in combinations(range(N_MOTIF), 2):
        common = sum(h[i][t] * h[j][t] for t in range(N_MOTIF))
        multiplicity = (1 if h[i][j] else 2) - common
        ensure(multiplicity >= 0, "negative incidence multiplicity")
        result.extend([(i, j)] * multiplicity)
    ensure(len(result) == N_OUTSIDE, "outside order mismatch")
    return tuple(result)


def q_matrix() -> list[list[int]]:
    result: list[list[int]] = []
    for pattern in outside_patterns():
        row = [1] + [0] * N_MOTIF
        for vertex in pattern:
            row[vertex + 1] = 1
        result.append(row)
    return result


def action_on_w() -> list[list[int]]:
    """Return C from BQ=QC, derived from the linear block equations."""

    h = motif_graph()
    c = [[0] * 13 for _ in range(13)]
    c[0][0] = 18
    for i in range(12):
        c[i + 1][0] = -1
    for j in range(12):
        c[0][j + 1] = 2
        for i in range(12):
            c[i + 1][j + 1] = 3 * int(i == j) - h[i][j]
    return c


def linear_solutions_mod_p(
    a: list[list[int]], b: list[int], prime: int
) -> list[tuple[int, ...]]:
    rows = len(a)
    columns = len(a[0])
    work = [
        [value % prime for value in a[i]] + [b[i] % prime]
        for i in range(rows)
    ]
    pivots: list[int] = []
    r = 0
    for column in range(columns):
        pivot = next((i for i in range(r, rows) if work[i][column]), None)
        if pivot is None:
            continue
        work[r], work[pivot] = work[pivot], work[r]
        inverse = pow(work[r][column], -1, prime)
        work[r] = [value * inverse % prime for value in work[r]]
        for i in range(rows):
            if i == r or work[i][column] == 0:
                continue
            factor = work[i][column]
            work[i] = [
                (work[i][j] - factor * work[r][j]) % prime
                for j in range(columns + 1)
            ]
        pivots.append(column)
        r += 1
        if r == rows:
            break
    if any(
        all(work[i][j] == 0 for j in range(columns)) and work[i][-1]
        for i in range(r, rows)
    ):
        return []
    free = [j for j in range(columns) if j not in pivots]
    particular = [0] * columns
    for i, column in enumerate(pivots):
        particular[column] = work[i][-1]
    basis: list[list[int]] = []
    for column in free:
        vector = [0] * columns
        vector[column] = 1
        for i, pivot_column in enumerate(pivots):
            vector[pivot_column] = -work[i][column] % prime
        basis.append(vector)
    coefficient_rows = [()] if not basis else product(range(prime), repeat=len(basis))
    return [
        tuple(
            (
                particular[j]
                + sum(coefficients[i] * basis[i][j] for i in range(len(basis)))
            )
            % prime
            for j in range(columns)
        )
        for coefficients in coefficient_rows
    ]


def kernel_mod_prime_power(
    a: list[list[int]], prime: int, exponent: int
) -> list[tuple[int, ...]]:
    columns = len(a[0])
    vectors = linear_solutions_mod_p(a, [0] * len(a), prime)
    modulus = prime
    for _ in range(1, exponent):
        next_vectors: list[tuple[int, ...]] = []
        for vector in vectors:
            products = [
                sum(row[j] * vector[j] for j in range(columns)) for row in a
            ]
            ensure(all(value % modulus == 0 for value in products), "bad lift")
            rhs = [-(value // modulus) % prime for value in products]
            for correction in linear_solutions_mod_p(a, rhs, prime):
                next_vectors.append(
                    tuple(
                        (vector[j] + modulus * correction[j]) % (modulus * prime)
                        for j in range(columns)
                    )
                )
        vectors = next_vectors
        modulus *= prime
    return vectors


def q_value(
    vector: tuple[int, ...], prime: int, exponent: int, gram: list[list[int]]
) -> Fraction:
    modulus = prime**exponent
    ga = [sum(gram[i][j] * vector[j] for j in range(13)) for i in range(13)]
    ensure(all(value % modulus == 0 for value in ga), "not in dual lattice")
    pairing_with_characteristic = ga[0] // modulus
    norm_numerator = sum(vector[i] * ga[i] for i in range(13))
    value = Fraction(pairing_with_characteristic, 2) - Fraction(
        norm_numerator, 2 * modulus * modulus
    )
    return value - (value.numerator // value.denominator)


def cyclotomic_reduce(coefficients: list[int], prime: int) -> list[int]:
    modulus = len(coefficients)
    base = modulus // prime
    degree = modulus - base
    reduced = coefficients[:degree]
    for offset in range(base):
        tail = coefficients[degree + offset]
        for block in range(prime - 1):
            reduced[offset + block * base] -= tail
    return reduced


def certify_phase(values: list[Fraction], prime: int) -> dict[str, object]:
    order = len(values)
    square_root = isqrt(order)
    ensure(square_root * square_root == order, "nonsquare module order")
    denominator = 1
    for value in values:
        denominator = lcm(denominator, value.denominator)
    counts = [0] * denominator
    for value in values:
        counts[
            (value.numerator * (denominator // value.denominator)) % denominator
        ] += 1
    if denominator == 1:
        reduced = [1]
        phase = "+1"
    else:
        reduced = cyclotomic_reduce(counts, prime)
        targets: dict[str, list[int]] = {}
        for label, coefficient, position in (
            ("+1", square_root, 0),
            ("-1", -square_root, 0),
        ):
            candidate = [0] * denominator
            candidate[position] = coefficient
            targets[label] = cyclotomic_reduce(candidate, prime)
        if denominator % 4 == 0:
            for label, position in (
                ("+i", denominator // 4),
                ("-i", 3 * denominator // 4),
            ):
                candidate = [0] * denominator
                candidate[position] = square_root
                targets[label] = cyclotomic_reduce(candidate, prime)
        matches = [label for label, target in targets.items() if target == reduced]
        ensure(len(matches) == 1, "Gauss phase not uniquely certified")
        phase = matches[0]
    return {
        "order": order,
        "denominator": denominator,
        "distinct_values": len(set(values)),
        "phase": phase,
        "remainder_sha256": hashlib.sha256(
            canonical(reduced).encode("ascii")
        ).hexdigest(),
    }


def preinspect() -> dict[str, object]:
    manifest = DISCOVERY / "package-manifest.sha256"
    ensure(sha256(manifest) == EXPECTED_DISCOVERY_MANIFEST_SHA256,
           "discovery manifest file hash drift")
    checked = 0
    for line in manifest.read_text(encoding="utf-8").splitlines():
        digest, relative = line.split("  ", 1)
        ensure(sha256(ROOT / relative) == digest, f"sealed file drift: {relative}")
        checked += 1
    ensure(checked == 11, "unexpected discovery manifest entry count")
    for relative, expected in EXPECTED_INPUTS.items():
        ensure(sha256(ROOT / relative) == expected, f"input drift: {relative}")
    return {
        "discovery_manifest_sha256": EXPECTED_DISCOVERY_MANIFEST_SHA256,
        "discovery_entries_checked": checked,
        "input_manifests_checked": len(EXPECTED_INPUTS),
    }


def build_results() -> dict[str, object]:
    seal = preinspect()
    q = q_matrix()
    gram = multiply(transpose(q), q)
    determinant = bareiss_det(gram)
    ensure(determinant == 6_191_736_422_400, "Gram determinant drift")
    ensure(Counter(map(len, outside_patterns())) == {0: 3, 1: 48, 2: 36},
           "incidence histogram drift")
    primitive_rows = [0] + [3 + 4 * i for i in range(12)]
    primitive_minor = [[q[i][j] for j in range(13)] for i in primitive_rows]
    ensure(abs(bareiss_det(primitive_minor)) == 1, "Q is not primitive")

    c = action_on_w()
    ct = transpose(c)
    ensure(multiply(gram, c) == multiply(ct, gram), "self-adjointness failed")
    polynomial = [
        [
            multiply(ct, ct)[i][j] - 7 * ct[i][j]
            for j in range(13)
        ]
        for i in range(13)
    ]
    quotient = solve_exact(gram, polynomial)
    ensure(all(x.denominator == 1 for row in quotient for x in row),
           "projector polynomial does not vanish on discriminant group")

    identity = [[int(i == j) for j in range(13)] for i in range(13)]
    seven_minus_ct = [
        [7 * identity[i][j] - ct[i][j] for j in range(13)]
        for i in range(13)
    ]
    smith = {
        "ambient": smith_diagonal_integer(gram),
        "U": smith_diagonal_integer(horizontal(gram, seven_minus_ct)),
        "K": smith_diagonal_integer(horizontal(gram, ct)),
    }
    profiles = {
        str(prime): {
            component: p_valuations(diagonal, prime)
            for component, diagonal in smith.items()
        }
        for prime in PRIMES
    }
    expected_profiles = {
        "2": {
            "ambient": [2, 3, 3, 3, 3, 8],
            "U": [2, 8],
            "K": [3, 3, 3, 3],
        },
        "3": {
            "ambient": [1, 1, 1, 1, 2, 2, 2],
            "U": [1, 1, 2, 2],
            "K": [1, 1, 2],
        },
        "5": {"ambient": [1, 1], "U": [1, 1], "K": []},
        "7": {"ambient": [], "U": [], "K": []},
    }
    ensure(profiles == expected_profiles, "independent Smith profile mismatch")

    gauss: dict[str, dict[str, object]] = {"U": {}, "K": {}}
    for component in ("U", "K"):
        operator = [
            [
                c[i][j] - (7 if component == "U" and i == j else 0)
                for j in range(13)
            ]
            for i in range(13)
        ]
        stacked = gram + operator
        for prime, exponent in ((2, 8), (3, 2), (5, 1)):
            vectors = kernel_mod_prime_power(stacked, prime, exponent)
            values = [q_value(vector, prime, exponent, gram) for vector in vectors]
            gauss[component][str(prime)] = certify_phase(values, prime)
    phases = {
        component: {
            prime: data["phase"] for prime, data in gauss[component].items()
        }
        for component in ("U", "K")
    }
    ensure(
        phases
        == {
            "U": {"2": "-i", "3": "-1", "5": "-1"},
            "K": {"2": "+1", "3": "-1", "5": "+1"},
        },
        "finite Gauss phase mismatch",
    )

    # Milgram: positive even ranks 42 and 32 have total phases i and +1.
    # Dividing by the non-seven products -i and -1 gives -1 at seven.
    seven_phase = {"U": "-1", "K": "-1"}
    rows: list[dict[str, object]] = []
    nonseven_u = 2**10 * 3**6 * 5**2
    nonseven_k = 2**12 * 3**4
    for k in range(16, 31, 2):
        length_ok = k <= 32 and k <= 42
        # For p=7 and even k, phase -1 is precisely the nonsplit type.
        type_exists = True
        rows.append(
            {
                "k": k,
                "global_rank_r": k + 12,
                "det_U": nonseven_u * 7**k,
                "det_K": nonseven_k * 7**k,
                "discriminant_length_bounds_hold": length_ok,
                "O_minus_k_7_exists": type_exists,
                "excluded": not (length_ok and type_exists),
            }
        )
    ensure(not any(row["excluded"] for row in rows), "unexpected row exclusion")

    return {
        "format": "wave128-independent-verification-v1",
        "claim_label": "VERIFIED",
        "scope": (
            "Conditional necessary discriminant and rootlessness consequences "
            "of the frozen Wave 105 motif and verified Wave 109 projector."
        ),
        "preinspection": seal,
        "reconstruction": {
            "pattern_histogram": {"0": 3, "1": 48, "2": 36},
            "Q_rank": 13,
            "primitive_minor_determinant_abs": 1,
            "Lambda_rank": 74,
            "det_Lambda": determinant,
            "det_factorization": "2^22 * 3^10 * 5^2",
            "self_adjointness": True,
            "projector_relation_on_discriminant": True,
        },
        "smith_diagonals": smith,
        "primary_valuations": profiles,
        "gauss_profiles": gauss,
        "nonseven_phases": {"U": "-i", "K": "-1"},
        "milgram_total_phases": {"U": "+i", "K": "+1"},
        "seven_phases": seven_phase,
        "seven_types": {"U": "O^-(k,7)", "K": "O^-(k,7)"},
        "seven_gluing_audit": {
            "anti_isometric_primary_groups": True,
            "equal_orders": "7^k",
            "maps": {
                "U": "B Lambda = 7 U* over Z_7",
                "K": "(7I-B) Lambda = 7 K* over Z_7",
            },
            "exponent": 7,
        },
        "rootlessness_audit": {
            "Lambda_even": True,
            "norm_two_shape": "+/-(e_i-e_j)",
            "chosen_coordinate_values": [0, -1],
            "forbidden_eigenvalues": [3, -4],
            "min_U_at_least": 4,
            "min_K_at_least": 4,
        },
        "rows": rows,
        "comparison": {
            "discovery_claims_matched": True,
            "corrections": [],
            "clarifications": [
                (
                    "O^-(k,7) compatibility is only a local necessary "
                    "condition; it does not construct U, K, D, or a graph."
                ),
                (
                    "Rootlessness uses the ambient coordinate lattice and "
                    "the zero diagonal/0-1 entries of the unknown adjacency D."
                ),
            ],
        },
        "status_wall": {
            "any_rank_row_excluded": False,
            "motif_extension": "UNKNOWN",
            "Conway_99": "UNKNOWN",
            "literature_novelty": "UNKNOWN",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    rendered = canonical(build_results())
    if args.verify:
        ensure(args.verify.read_text(encoding="utf-8") == rendered,
               "independent result file drift")
    if args.output:
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    if not args.output and not args.verify:
        print(rendered, end="")


if __name__ == "__main__":
    main()
