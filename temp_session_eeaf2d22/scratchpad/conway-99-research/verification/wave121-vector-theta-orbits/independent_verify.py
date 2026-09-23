"""Clean-room verifier for sealed Wave 121.

The implementation does not import or execute discovery code.  It rebuilds
the q=14 scalar modular parameterization through y_77, the exact-value
orthogonal aggregates, and the secondary scalar C4 Jacobi reduction.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import math
import os
from fractions import Fraction
from pathlib import Path


Q = Fraction
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
DISCOVERY = ROOT / "attempts" / "wave121-vector-theta-orbits"
CANONICAL = HERE / "independent-results.json"
DISCOVERY_MANIFEST_HASH = (
    "ab3ede13ea60315885ac077cd8e0b3e7b124f34329d51e82fa2f4d08434cf803"
)
PREREQUISITES = {
    "verification/wave66-spherical-code-shift/package-manifest.sha256":
        "a6051ebcfccab0fc9b3f9698f0024cc3284549f5148c9a12a4c6bbe08c786486",
    "verification/wave71-modular-theta-extension/package-manifest.sha256":
        "0eede2ebc625534360dda3f8e62456e582f5184fd18d3820dd44748de95a5237",
    "verification/wave80-f7-overlattice-code/package-manifest.sha256":
        "25129c86f97c8f9513eff04ada641c458b924f8edd583e6e6abc76d114c64077",
    "verification/wave86-level7-exact/package-manifest.sha256":
        "cbfafc03db11ad7f103e532e0f5e0b2e85ff6b568ad327b947a2d394a1d1dfa2",
    "verification/wave97-f7-exterior-matroid/package-manifest.sha256":
        "e7cdd56b40a385ffff42dcdf66f0a0f5b54f60af8472d6a9a9718f7209114992",
    "verification/wave101-all-rank-level7-lp/package-manifest.sha256":
        "79fd0331a936761f2394d58f835df80e41ad855cdf88660a2ccfd5841c5d7aba",
    "verification/wave112-c4-short-vector-incidence/package-manifest.sha256":
        "56845bcdf221c16ec46d40c630a8cdb3d63beed1314dd2683e17bf5c929ff024",
    "verification/wave116-c4-jacobi-theta/package-manifest.sha256":
        "e44afa352f51c192d6c5ac8584ccd6334dd69a3d11856f4ac0254283829bbfb8",
}

LEVEL = 7
WEIGHT = 22
RANK = 44
PRECISION = 77
STURM = 14
CHARACTER = (0, 1, 1, -1, 1, -1, -1)
Factor = tuple[int, str]
Product = tuple[Factor, Factor]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def free_memory_percent() -> float:
    if os.name != "nt":
        return 100.0

    class Status(ctypes.Structure):
        _fields_ = [
            ("length", ctypes.c_ulong),
            ("load", ctypes.c_ulong),
            ("total_phys", ctypes.c_ulonglong),
            ("available_phys", ctypes.c_ulonglong),
            ("total_page", ctypes.c_ulonglong),
            ("available_page", ctypes.c_ulonglong),
            ("total_virtual", ctypes.c_ulonglong),
            ("available_virtual", ctypes.c_ulonglong),
            ("available_extended", ctypes.c_ulonglong),
        ]

    state = Status()
    state.length = ctypes.sizeof(state)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(state)):
        raise OSError("GlobalMemoryStatusEx failed")
    return 100.0 * state.available_phys / state.total_phys


def verify_frozen_bytes() -> None:
    if sha256(DISCOVERY / "package-manifest.sha256") != DISCOVERY_MANIFEST_HASH:
        raise ValueError("discovery manifest drift")
    for rel, expected in PREREQUISITES.items():
        if sha256(ROOT / rel) != expected:
            raise ValueError(f"prerequisite drift: {rel}")
    inventory = {}
    lines = (HERE / "discovery-inventory-preinspection.tsv").read_text(
        encoding="utf-8"
    ).splitlines()
    for line in lines[1:]:
        rel, size, digest = line.split("\t")
        inventory[rel] = (int(size), digest)
    for rel, (size, digest) in inventory.items():
        path = ROOT / rel
        if path.stat().st_size != size or sha256(path) != digest:
            raise ValueError(f"discovery inventory drift: {rel}")


def chi(n: int) -> int:
    return CHARACTER[n % LEVEL]


def bernoulli_numbers(limit: int) -> list[Q]:
    values = [Q(0)] * (limit + 1)
    values[0] = Q(1)
    for degree in range(1, limit + 1):
        values[degree] = -sum(
            Q(math.comb(degree + 1, j)) * values[j]
            for j in range(degree)
        ) / Q(degree + 1)
    return values


BERNOULLI = bernoulli_numbers(WEIGHT)


def bernoulli_polynomial(degree: int, value: Q) -> Q:
    return sum(
        Q(math.comb(degree, j))
        * BERNOULLI[j]
        * value ** (degree - j)
        for j in range(degree + 1)
    )


def generalized_bernoulli(degree: int) -> Q:
    return Q(LEVEL ** (degree - 1)) * sum(
        Q(chi(a)) * bernoulli_polynomial(degree, Q(a, LEVEL))
        for a in range(1, LEVEL + 1)
    )


def divisor_sums(weight: int, orientation: str) -> list[Q]:
    series = [Q(0)] * (PRECISION + 1)
    if orientation == "C":
        series[0] = -generalized_bernoulli(weight) / Q(2 * weight)
    elif orientation != "T":
        raise ValueError(orientation)
    for divisor in range(1, PRECISION + 1):
        coefficient = chi(divisor) if orientation == "C" else 1
        power = divisor ** (weight - 1)
        for n in range(divisor, PRECISION + 1, divisor):
            if orientation == "C":
                series[n] += coefficient * power
            else:
                series[n] += Q(chi(n // divisor)) * power
    return series


EISENSTEIN = {
    (weight, orientation): divisor_sums(weight, orientation)
    for weight in range(3, 20, 2)
    for orientation in ("C", "T")
}


def multiply_series(left: list[Q], right: list[Q]) -> list[Q]:
    return [
        sum(left[j] * right[n - j] for j in range(n + 1))
        for n in range(PRECISION + 1)
    ]


def product_series(product: Product) -> list[Q]:
    return multiply_series(EISENSTEIN[product[0]], EISENSTEIN[product[1]])


def rank(matrix: list[list[Q]]) -> int:
    work = [row[:] for row in matrix]
    if not work:
        return 0
    pivot_row = 0
    for column in range(len(work[0])):
        pivot = next(
            (row for row in range(pivot_row, len(work)) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        scale = work[pivot_row][column]
        work[pivot_row] = [entry / scale for entry in work[pivot_row]]
        for row in range(len(work)):
            if row == pivot_row or not work[row][column]:
                continue
            scale = work[row][column]
            work[row] = [
                left - scale * right
                for left, right in zip(work[row], work[pivot_row], strict=True)
            ]
        pivot_row += 1
        if pivot_row == len(work):
            break
    return pivot_row


def inverse(matrix: list[list[Q]]) -> list[list[Q]]:
    size = len(matrix)
    work = [
        row[:] + [Q(r == c) for c in range(size)]
        for r, row in enumerate(matrix)
    ]
    for column in range(size):
        pivot = next(
            (row for row in range(column, size) if work[row][column]),
            None,
        )
        if pivot is None:
            raise ValueError("singular")
        work[column], work[pivot] = work[pivot], work[column]
        scale = work[column][column]
        work[column] = [entry / scale for entry in work[column]]
        for row in range(size):
            if row == column or not work[row][column]:
                continue
            scale = work[row][column]
            work[row] = [
                left - scale * right
                for left, right in zip(work[row], work[column], strict=True)
            ]
    return [row[size:] for row in work]


def matrix_product(left: list[list[Q]], right: list[list[Q]]) -> list[list[Q]]:
    return [
        [
            sum(left[row][k] * right[k][column] for k in range(len(right)))
            for column in range(len(right[0]))
        ]
        for row in range(len(left))
    ]


def solve(matrix: list[list[Q]], right: list[Q]) -> list[Q]:
    inv = inverse(matrix)
    return [
        sum(inv[row][column] * right[column] for column in range(len(right)))
        for row in range(len(inv))
    ]


def basis_candidates() -> list[Product]:
    rows = []
    for left_weight in range(3, 12, 2):
        right_weight = WEIGHT - left_weight
        for left_type in ("C", "T"):
            for right_type in ("C", "T"):
                rows.append(
                    ((left_weight, left_type), (right_weight, right_type))
                )
    return sorted(rows, key=repr, reverse=True)


def coefficient_matrix(products: list[Product]) -> list[list[Q]]:
    return [
        [product_series(product)[n] for product in products]
        for n in range(STURM + 1)
    ]


def select_basis() -> list[Product]:
    selected: list[Product] = []
    old_rank = 0
    for candidate in basis_candidates():
        trial = selected + [candidate]
        new_rank = rank(coefficient_matrix(trial))
        if new_rank > old_rank:
            selected = trial
            old_rank = new_rank
        if old_rank == 15:
            break
    if old_rank != 15:
        raise AssertionError(old_rank)
    return selected


def fricke_product(product: Product) -> tuple[Q, Product]:
    factor = Q(-1)
    mapped = []
    for weight, orientation in product:
        exponent = (
            (weight - 1) // 2
            if orientation == "C"
            else (1 - weight) // 2
        )
        factor *= Q(LEVEL**exponent) if exponent >= 0 else Q(1, LEVEL ** (-exponent))
        mapped.append((weight, "T" if orientation == "C" else "C"))
    return factor, (mapped[0], mapped[1])


def fricke_expansion_matrix(basis: list[Product]) -> list[list[Q]]:
    prefix_inverse = inverse(coefficient_matrix(basis))
    transformed = [
        [
            fricke_product(product)[0]
            * product_series(fricke_product(product)[1])[n]
            for product in basis
        ]
        for n in range(PRECISION + 1)
    ]
    return matrix_product(transformed, prefix_inverse)


def affine_parameterization() -> dict[str, object]:
    basis = select_basis()
    fricke = fricke_expansion_matrix(basis)
    factor = -Q(LEVEL ** (11 - 14 // 2))  # -7^4
    raw_constants = [factor * fricke[n][0] for n in range(PRECISION + 1)]
    raw_rows = [
        [factor * fricke[n][j] for j in range(7, 15)]
        for n in range(PRECISION + 1)
    ]
    pivot = raw_rows[0][7]
    x14_constant = (Q(1) - raw_constants[0]) / pivot
    x14_row = [-raw_rows[0][j] / pivot for j in range(7)]
    y_constants = [
        raw_constants[n] + raw_rows[n][7] * x14_constant
        for n in range(PRECISION + 1)
    ]
    y_rows = [
        [
            raw_rows[n][j] + raw_rows[n][7] * x14_row[j]
            for j in range(7)
        ]
        for n in range(PRECISION + 1)
    ]
    if y_constants[0] != 1 or any(y_rows[0]):
        raise AssertionError("constant elimination")
    return {
        "basis": basis,
        "fricke": fricke,
        "x14_constant": x14_constant,
        "x14_row": x14_row,
        "y_constants": y_constants,
        "y_rows": y_rows,
    }


def evaluate(constant: Q, row: list[Q], point: list[Q]) -> Q:
    return constant + sum(
        coefficient * value
        for coefficient, value in zip(row, point, strict=True)
    )


def qtext(value: Q) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def x_value(n: int, point: list[Q], system: dict[str, object]) -> Q:
    if n == 0:
        return Q(1)
    if 1 <= n <= 6:
        return Q(0)
    if 7 <= n <= 13:
        return point[n - 7]
    if n == 14:
        return evaluate(system["x14_constant"], system["x14_row"], point)
    raise ValueError(n)


def y_value(n: int, point: list[Q], system: dict[str, object]) -> Q:
    return evaluate(system["y_constants"][n], system["y_rows"][n], point)


def cone_audit(point: list[Q], system: dict[str, object]) -> dict[str, object]:
    x = {n: x_value(n, point, system) for n in range(7, 15)}
    y = {n: y_value(n, point, system) for n in range(1, 78)}
    differences = {
        "x7-y1": x[7] - y[1],
        "x14-y2": x[14] - y[2],
    }
    for n in range(1, 12):
        differences[f"y{7*n}-x{n}"] = y[7 * n] - x_value(n, point, system)
    values = list(x.values()) + list(y.values()) + list(differences.values())
    return {
        "all_nonnegative": all(value >= 0 for value in values),
        "minimum": qtext(min(values)),
        "x7_to_x14": [qtext(x[n]) for n in range(7, 15)],
        "y1_to_y77": [qtext(y[n]) for n in range(1, 78)],
        "orbit_differences": {label: qtext(value) for label, value in differences.items()},
        "all_even_integers": all(
            value.denominator == 1 and value.numerator % 2 == 0
            for value in values
        ),
    }


def assert_affine_identity(
    system: dict[str, object],
    left_constant: Q,
    left_row: list[Q],
    terms: list[tuple[Q, int]],
) -> None:
    right_constant = sum(
        multiplier * system["y_constants"][n] for multiplier, n in terms
    )
    right_row = [
        sum(multiplier * system["y_rows"][n][j] for multiplier, n in terms)
        for j in range(7)
    ]
    # Restrict x7=x8=x9=0: compare the constant and coordinates x10..x13.
    if left_constant != right_constant or left_row[3:] != right_row[3:]:
        raise AssertionError("restricted identity mismatch")


def orbit_count(dimension: int) -> dict[str, int]:
    m = dimension // 2
    isotropic_including_zero = 7 ** (2 * m - 1) - 6 * 7 ** (m - 1)
    each_nonzero = 7 ** (2 * m - 1) + 7 ** (m - 1)
    if isotropic_including_zero + 6 * each_nonzero != 7 ** (2 * m):
        raise AssertionError("orbit total")
    return {
        "dimension": dimension,
        "zero_including_zero_vector": isotropic_including_zero,
        "nonzero_isotropic": isotropic_including_zero - 1,
        "each_exact_nonzero_value": each_nonzero,
        "total": 7**dimension,
    }


def scalar_c4_lane() -> dict[str, object]:
    residues = list(range(20))
    even_orbits = sorted({min(s, (-s) % 20) for s in residues})
    if len(even_orbits) != 11:
        raise AssertionError(even_orbits)

    # Exact character orthogonality behind F^2=20*negation.
    square_rows = []
    for t in residues:
        row = []
        for u in residues:
            # This is the exact geometric sum
            # sum_s exp(-2*pi*i*s*(t+u)/20).
            row.append(20 if (t + u) % 20 == 0 else 0)
        square_rows.append(row)
    if any(
        square_rows[t][u] != 20 * int(u == (-t) % 20)
        for t in residues
        for u in residues
    ):
        raise AssertionError("finite Fourier square")

    scalar_total = 2079 * 5868
    target = 52812
    zero = scalar_total - 2 * target
    table = {(0, 0): 2079, (7, -28): target, (7, 0): zero, (7, 28): target}
    if sum(value for (n, _r), value in table.items() if n == 7) != scalar_total:
        raise AssertionError("truncated table scalar specialization")
    if not all(4 * 70 * n - r * r >= 0 for (n, r) in table if n):
        raise AssertionError("Jacobi support")

    return {
        "marking": {
            "d_definition": "sum_Cyclic epsilon_i*u_i",
            "d_membership": "M subset L",
            "d_norm": 20,
            "d_primitive_in_L": True,
            "d_divisibility_in_L": 1,
            "d_divisibility_argument": (
                "div_L(d) divides norm 20, while primitivity makes d/div "
                "an element of exact order div in the 7-elementary L*/L"
            ),
            "b_definition": "sqrt(7)*d",
            "b_membership": "K",
            "b_norm": 140,
            "b_primitive_in_K": True,
            "b_divisibility_in_K": 7,
            "K_index": 70,
            "L_index": 10,
        },
        "selection": {
            "valid_norms_under_frozen_inputs": [14, 16, 18],
            "K_target": [[7, 28], [8, 28], [9, 28]],
            "coefficient_sum_antipodal_lower": 52812,
            "cap25_total": 51975,
            "q10_interpretation": "UNKNOWN_UNDER_FROZEN_INPUTS",
        },
        "rank28_fricke": {
            "raw_factor": "-7^8",
            "normalized_factor": "-7^-3",
            "raw_formula": (
                "Phi_K(-1/(7tau),z/(7tau))=-7^8*tau^22*"
                "exp(20*pi*i*z^2/tau)*Phi_L(tau,z)"
            ),
        },
        "components": {
            "raw_index70_residues": 140,
            "divisibility_reduced_residues": 20,
            "even_independent_components": len(even_orbits),
            "even_representatives": even_orbits,
            "identity": "theta_(70,7s)(tau,z)=theta_(10,s)(7tau,7z)",
            "component_weight": "43/2",
            "finite_fourier_kernel": "exp(-pi*i*s*t/10)",
            "finite_fourier_square": "20 times residue negation",
            "poisson_component_formula": (
                "sqrt(-i*tau/20)*sum_s exp(-pi*i*s*t/10)"
                "*H_s(-1/(7tau))=-7^8*tau^22*G_t(tau)"
            ),
        },
        "support_margins_r28": {
            str(n): 4 * 70 * n - 28 * 28 for n in range(7, 11)
        },
        "truncated_null": {
            "coefficients_n_r": {
                f"{n},{r}": value for (n, r), value in sorted(table.items())
            },
            "q7_scalar_sum": scalar_total,
            "nonnegative_integral_symmetric": True,
            "is_Jacobi_form": False,
            "is_Fricke_compatible_all_orders": False,
        },
    }


def build_results() -> dict[str, object]:
    verify_frozen_bytes()
    system = affine_parameterization()

    prefix10_point = [
        Q(389888, 57),
        Q(0),
        Q(0),
        Q(0),
        Q(1495218928, 57),
        Q(2126104904, 57),
        Q(6854397536, 19),
    ]
    prefix11_point = [
        Q(0),
        Q(1219920912, 9307),
        Q(3455785984, 9307),
        Q(0),
        Q(0),
        Q(1013289561144, 9307),
        Q(3477251342208, 9307),
    ]
    formal_point = [
        Q(0),
        Q(0),
        Q(0),
        Q(2729216),
        Q(9904496),
        Q(64688008),
        Q(374547488),
    ]
    restricted_rational_point = [
        Q(0),
        Q(0),
        Q(0),
        Q(4144144),
        Q(0),
        Q(83082072),
        Q(383037056),
    ]
    prefix10 = cone_audit(prefix10_point, system)
    prefix11 = cone_audit(prefix11_point, system)
    formal = cone_audit(formal_point, system)
    restricted_rational = cone_audit(restricted_rational_point, system)
    if not prefix10["all_nonnegative"] or not prefix11["all_nonnegative"]:
        raise AssertionError("old optimizer cut off")
    if not formal["all_nonnegative"] or not formal["all_even_integers"]:
        raise AssertionError("formal even-integral control")
    if not restricted_rational["all_nonnegative"]:
        raise AssertionError("restricted rational equality control")
    if restricted_rational["all_even_integers"]:
        raise AssertionError("restricted rational control unexpectedly integral")

    row_x10 = [Q(0)] * 7
    row_x10[3] = 1
    assert_affine_identity(
        system,
        Q(-2729216),
        row_x10,
        [(Q(440363), 1), (Q(32536), 2), (Q(1715), 3), (Q(49), 4)],
    )
    row_second = [Q(0)] * 7
    row_second[3] = 1
    row_second[4] = Q(1, 7)
    assert_affine_identity(
        system,
        Q(-4144144),
        row_second,
        [(Q(280574), 1), (Q(13377), 2), (Q(343), 3)],
    )

    code_upper = 7**30 * (7**13 + 7**6)
    return {
        "format": "wave121-independent-verifier-v1",
        "role": "verifier",
        "claim_label": "VERIFIED",
        "conditional_scope": (
            "q=14/r=30 exact-value orbit scalar cone and the disjoint "
            "rank-28 scalar C4 Jacobi reduction"
        ),
        "discovery_manifest_sha256": DISCOVERY_MANIFEST_HASH,
        "orthogonal_spaces": {
            "D_L": "O^-(14,7)",
            "D_K": "O^-(30,7)",
            "D_K_milgram_phase": -1,
            "D_K_determinant_legendre_sign": 1,
            "D_K_split_determinant_legendre_sign": -1,
            "orbit_counts": {
                "dimension14": orbit_count(14),
                "dimension30": orbit_count(30),
            },
            "aggregate_scope": (
                "complete exact quadratic-value sums only; no component "
                "equality and no lifted lattice or graph automorphism"
            ),
        },
        "orbit_dictionary": {
            "D_L_nonzero_isotropic": "x_(7m)-y_m",
            "D_K_nonzero_isotropic": "y_(7n)-x_n",
            "new_inequalities_tested": [
                "x7-y1",
                "x14-y2",
                *[f"y{7*n}-x{n}" for n in range(1, 12)],
            ],
            "anisotropic_exact_values": (
                "ordinary residue dissections; scalar nonnegativity suffices"
            ),
        },
        "extended_scalar_model": {
            "weight": 22,
            "dimension": 15,
            "sturm_bound": 14,
            "theta_L_precision": 77,
            "basis_products": [
                [[weight, orientation] for weight, orientation in product]
                for product in system["basis"]
            ],
            "prefix10": {
                "old_exact_optimum": "389888/57",
                "parity_bound": 6842,
                "optimizer_feasible_in_extended_cone": True,
                "audit": prefix10,
            },
            "prefix11": {
                "old_exact_optimum": "4675706896/9307",
                "parity_bound": 502388,
                "optimizer_feasible_in_extended_cone": True,
                "audit": prefix11,
            },
            "restricted_identities": [
                {
                    "assumption": "x7=x8=x9=0",
                    "identity": (
                        "x10-2729216=440363*y1+32536*y2+1715*y3+49*y4"
                    ),
                    "lower_bound": 2729216,
                },
                {
                    "assumption": "x7=x8=x9=0",
                    "identity": (
                        "x10+x11-4144144=(6/7)*x11+280574*y1+"
                        "13377*y2+343*y3"
                    ),
                    "lower_bound": 4144144,
                    "integer_rounding_claimed": False,
                    "attaining_rational_control": restricted_rational,
                },
            ],
            "formal_even_integral_control": formal,
            "optima_strengthened": False,
        },
        "short_code_upper": {
            "evaluation_injective_through_norm22": True,
            "difference_lower_if_same_word": 686,
            "difference_upper_by_triangle": 88,
            "norm20_self_dot_mod7": 5,
            "norm22_self_dot_mod7": 2,
            "each_anisotropic_value_upper": code_upper,
            "formula": "7^30*(7^13+7^6)",
            "coordinate_compositions": "UNKNOWN_UNDER_FROZEN_INPUTS",
        },
        "scalar_c4_jacobi": scalar_c4_lane(),
        "status": {
            "rank30_excluded": False,
            "rank28_excluded": False,
            "lattice_constructed": False,
            "graph_constructed": False,
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "verdict": "VERIFIED_SCOPED",
    }


def canonical_json(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    free = free_memory_percent()
    if free < 15:
        raise SystemExit(f"refusing to run at {free:.1f}% free memory")
    payload = canonical_json(build_results())
    if args.write is not None:
        args.write.write_text(payload, encoding="utf-8", newline="\n")
    elif args.verify is not None:
        if args.verify.read_text(encoding="utf-8") != payload:
            raise SystemExit("verification mismatch")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
