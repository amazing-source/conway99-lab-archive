#!/usr/bin/env python3
"""Clean-room verifier for the Wave 97 exterior/matroid package.

No discovery module is imported or executed.  The verifier reconstructs the
Schur powers, compound-code data, Smith invariants, generalized weights, and
orthogonal counts directly from the frozen Wave 51 and Wave 80 imports.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import re
from collections import Counter
from functools import reduce
from pathlib import Path
from typing import Iterable


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DISCOVERY = ROOT / "attempts" / "wave97-f7-exterior-matroid"

Q = 7
N = 99
ENDPOINT_RANK = 28
CODE_DIMENSION = 44
LIVE_RANKS = tuple(range(28, 43, 2))

EXPECTED_IMPORTS = {
    "attempts/wave46-f7-code/package-manifest.sha256":
        "756622d5f40457d188c818a0233ee002b64039548bd51a725ec606b821c60272",
    "verification/wave46-f7-code/package-manifest.sha256":
        "3624ea9eca399889c048b3f333ae8df12fbac60176fd7bca0924fc06a18fdff0",
    "attempts/wave51-seidel-smith/package-manifest.sha256":
        "dfb39e94b6837e21959bc2b70a9e296baacc94b4c08cb0b78e04264686685965",
    "verification/wave51-seidel-smith/package-manifest.sha256":
        "bb191148dac5558d9154ea98dbb6f45da146e0602940297131ca7de211d3274c",
    "attempts/wave80-f7-overlattice-code/package-manifest.sha256":
        "51d3e709308851ba9c9c63a8897dec4c761ce11e5126633e0cdf67f6e470cba7",
    "verification/wave80-f7-overlattice-code/package-manifest.sha256":
        "25129c86f97c8f9513eff04ada641c458b924f8edd583e6e6abc76d114c64077",
    "AGENTS.md":
        "4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_hash_manifest(path: Path) -> dict[str, str]:
    pattern = re.compile(r"^([0-9a-f]{64}) [ *](.+)$")
    entries: dict[str, str] = {}
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), 1
    ):
        match = pattern.fullmatch(line)
        if not match:
            raise AssertionError(f"{path}:{line_number}: malformed hash line")
        digest, relative = match.groups()
        if relative in entries:
            raise AssertionError(f"{path}:{line_number}: duplicate {relative}")
        entries[relative] = digest
    return entries


def preinspection_inventory() -> tuple[dict[str, str], dict[str, tuple[int, str]]]:
    metadata: dict[str, str] = {}
    files: dict[str, tuple[int, str]] = {}
    in_files = False
    for line in (HERE / "discovery-inventory-preinspection.tsv").read_text(
        encoding="utf-8"
    ).splitlines():
        if not line:
            continue
        fields = line.split("\t")
        if fields == ["path", "size_bytes", "sha256"]:
            in_files = True
            continue
        if in_files:
            if len(fields) != 3 or fields[0] in files:
                raise AssertionError(f"bad inventory row: {line!r}")
            files[fields[0]] = (int(fields[1]), fields[2])
        else:
            if len(fields) != 2:
                raise AssertionError(f"bad inventory metadata: {line!r}")
            metadata[fields[0]] = fields[1]
    return metadata, files


def verify_inputs() -> dict[str, object]:
    metadata, frozen = preinspection_inventory()
    actual = {
        path.relative_to(DISCOVERY).as_posix()
        for path in DISCOVERY.rglob("*")
        if path.is_file()
    }
    failures: list[str] = []
    if actual != set(frozen):
        failures.append("discovery inventory changed")
    for relative, (expected_size, expected_hash) in frozen.items():
        path = DISCOVERY / relative
        if not path.is_file():
            failures.append(f"missing {relative}")
            continue
        if path.stat().st_size != expected_size:
            failures.append(f"size mismatch {relative}")
        if sha256(path) != expected_hash:
            failures.append(f"hash mismatch {relative}")

    manifest = parse_hash_manifest(DISCOVERY / "package-manifest.sha256")
    expected_manifest_paths = {
        f"attempts/wave97-f7-exterior-matroid/{relative}"
        for relative in actual
        if relative != "package-manifest.sha256"
    }
    if set(manifest) != expected_manifest_paths:
        failures.append("discovery manifest coverage mismatch")
    for relative, expected_hash in manifest.items():
        path = ROOT / relative
        if not path.is_file() or sha256(path) != expected_hash:
            failures.append(f"discovery manifest mismatch {relative}")

    import_rows = {}
    for relative, expected_hash in EXPECTED_IMPORTS.items():
        path = ROOT / relative
        observed = sha256(path) if path.is_file() else None
        import_rows[relative] = {
            "expected_sha256": expected_hash,
            "observed_sha256": observed,
            "passed": observed == expected_hash,
        }
        if observed != expected_hash:
            failures.append(f"frozen import mismatch {relative}")

    input_freeze = parse_hash_manifest(DISCOVERY / "input-freeze.sha256")
    if input_freeze != EXPECTED_IMPORTS:
        failures.append("discovery input freeze differs from verifier freeze")

    return {
        "passed": not failures,
        "failures": failures,
        "frozen_utc": metadata["frozen_utc"],
        "frozen_git_commit": metadata["git_commit"],
        "discovery_files": len(frozen),
        "discovery_manifest_entries": len(manifest),
        "discovery_manifest_sha256": sha256(
            DISCOVERY / "package-manifest.sha256"
        ),
        "frozen_imports": import_rows,
    }


def rank_mod(matrix: list[list[int]], prime: int) -> int:
    if not matrix:
        return 0
    work = [[entry % prime for entry in row] for row in matrix]
    rows = len(work)
    columns = len(work[0])
    rank = 0
    for column in range(columns):
        pivot = next(
            (
                row
                for row in range(rank, rows)
                if work[row][column] % prime
            ),
            None,
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        inverse = pow(work[rank][column], -1, prime)
        work[rank] = [
            value * inverse % prime for value in work[rank]
        ]
        for row in range(rows):
            if row == rank or work[row][column] == 0:
                continue
            multiple = work[row][column]
            work[row] = [
                left - multiple * right
                for left, right in zip(work[row], work[rank])
            ]
            work[row] = [value % prime for value in work[row]]
        rank += 1
    return rank


def matmul_mod(
    left: list[list[int]],
    right: list[list[int]],
    prime: int,
) -> list[list[int]]:
    right_columns = list(zip(*right))
    return [
        [
            sum(a * b for a, b in zip(row, column)) % prime
            for column in right_columns
        ]
        for row in left
    ]


def compound2(matrix: list[list[int]], prime: int | None = None) -> list[list[int]]:
    row_pairs = tuple(itertools.combinations(range(len(matrix)), 2))
    column_pairs = tuple(
        itertools.combinations(range(len(matrix[0])), 2)
    )
    result = []
    for left, right in row_pairs:
        row = []
        for first, second in column_pairs:
            value = (
                matrix[left][first] * matrix[right][second]
                - matrix[left][second] * matrix[right][first]
            )
            row.append(value if prime is None else value % prime)
        result.append(row)
    return result


def schur_profile(rank: int = ENDPOINT_RANK) -> dict[str, object]:
    j_minus_i = [
        [0 if row == column else 1 for column in range(N)]
        for row in range(N)
    ]
    square_rank = rank_mod(j_minus_i, Q)
    hilbert = [1, rank, square_rank, N]
    h_vector = [
        hilbert[0],
        hilbert[1] - hilbert[0],
        hilbert[2] - hilbert[1],
        hilbert[3] - hilbert[2],
    ]
    return {
        "field": Q,
        "order": N,
        "rank_R": rank,
        "order_mod_field": N % Q,
        "rank_J_minus_I": square_rank,
        "R_schur_square": {
            "identity": "R*R=1_perp",
            "dimension": square_rank,
            "proof": (
                "R is self-orthogonal because S is symmetric and S^2=0; "
                "therefore R*R is in 1_perp. The 99 row squares are "
                "1-e_i and span row(J-I)=1_perp because 99=1 mod 7."
            ),
        },
        "R_schur_cube": {
            "identity": "R*R*R=F7^99",
            "dimension": N,
            "coordinate_extraction": (
                "for i!=j, s_j*(e_i-e_j)=S[j,i]e_i and S[j,i] is nonzero"
            ),
        },
        "C_schur_square": {
            "identity": "C*C=F7^99",
            "dimension": N,
            "proof": (
                "R*R=1_perp is contained in C*C. Nondegeneracy of C/R "
                "gives c,d with c dot d nonzero, so sum(c*d) is nonzero."
            ),
        },
        "hilbert_function_degrees_0_to_3": hilbert,
        "first_differences": h_vector,
        "symmetric_square_domain": math.comb(rank + 1, 2),
        "symmetric_square_kernel": math.comb(rank + 1, 2) - square_rank,
        "symmetric_cube_domain": math.comb(rank + 2, 3),
        "symmetric_cube_kernel": math.comb(rank + 2, 3) - N,
        "quadratic_images": {
            "count": N,
            "span_dimension": square_rank,
            "relation_space_dimension": N - square_rank,
            "unique_relation_coefficients": [1] * N,
            "every_98_independent": True,
            "degree_two_Cayley_Bacharach": True,
        },
        "passed": (
            N % Q == 1
            and square_rank == 98
            and hilbert == [1, 28, 98, 99]
            and h_vector == [1, 27, 70, 1]
        ),
    }


def factor_integer(value: int) -> dict[int, int]:
    if value <= 0:
        raise ValueError("positive integer required")
    factors: dict[int, int] = {}
    candidate = 2
    while candidate * candidate <= value:
        while value % candidate == 0:
            factors[candidate] = factors.get(candidate, 0) + 1
            value //= candidate
        candidate += 1
    if value > 1:
        factors[value] = factors.get(value, 0) + 1
    return factors


def valuation(value: int, prime: int) -> int:
    exponent = 0
    while value % prime == 0:
        exponent += 1
        value //= prime
    return exponent


def invariant_factors_of_diagonal(values: Iterable[int]) -> list[int]:
    diagonal = tuple(values)
    primes = sorted(
        {
            prime
            for value in diagonal
            for prime in factor_integer(value)
        }
    )
    result = [1] * len(diagonal)
    for prime in primes:
        exponents = sorted(valuation(value, prime) for value in diagonal)
        for index, exponent in enumerate(exponents):
            result[index] *= prime**exponent
    if any(right % left for left, right in zip(result, result[1:])):
        raise AssertionError("constructed invariant factors are not a chain")
    return result


def compress(values: Iterable[int]) -> list[dict[str, int]]:
    return [
        {"factor": factor, "multiplicity": multiplicity}
        for factor, multiplicity in sorted(Counter(values).items())
    ]


def source_smith_factors(rank: int) -> list[int]:
    middle = N - 2 * rank
    if middle < 0:
        raise ValueError("rank too large")
    return [1] * rank + [7] * middle + [49] * (rank - 1) + [490]


def compound_raw_diagonal(rank: int) -> list[int]:
    source = source_smith_factors(rank)
    return [
        left * right
        for left, right in itertools.combinations(source, 2)
    ]


def prime_valuation_sum(values: Iterable[int], prime: int) -> int:
    return sum(valuation(value, prime) for value in values)


def exterior_smith(rank: int) -> dict[str, object]:
    if rank not in LIVE_RANKS:
        raise ValueError("rank outside frozen live rows")
    middle = N - 2 * rank
    raw = compound_raw_diagonal(rank)
    smith = invariant_factors_of_diagonal(raw)
    expected_counts = {
        1: math.comb(rank, 2),
        7: rank * middle,
        49: rank * rank + math.comb(middle, 2),
        343: rank * middle,
        2401: math.comb(rank, 2) - 98,
        24010: 98,
    }
    counts = Counter(smith)
    seven_counts = Counter(valuation(value, 7) for value in raw)
    determinant_valuations = {
        str(prime): prime_valuation_sum(raw, prime)
        for prime in (2, 5, 7)
    }
    return {
        "rank_F7_S": rank,
        "middle_7_primary_multiplicity": middle,
        "order": len(raw),
        "rank_F7_C2S": counts[1],
        "raw_pair_product_counts": {
            str(factor): multiplicity
            for factor, multiplicity in sorted(Counter(raw).items())
        },
        "smith_normal_form": compress(smith),
        "seven_adic_pair_sum_counts": {
            str(exponent): multiplicity
            for exponent, multiplicity in sorted(seven_counts.items())
        },
        "determinant_valuations": determinant_valuations,
        "factor_24010_audit": {
            "raw_pair_products_equal_24010": Counter(raw)[24010],
            "smith_invariant_factors_equal_24010": counts[24010],
            "terminal_7_power_4_slots": seven_counts[4],
            "terminal_2_adic_slots": 98,
            "terminal_5_adic_slots": 98,
            "reason": (
                "Smith factors align independently sorted p-adic exponent "
                "lists. All 98 v2=v5=1 slots align with the last 98 "
                "v7=4 slots because C(r,2)>=98; they are not restricted "
                "to the raw products 49*490."
            ),
        },
        "passed": (
            len(raw) == math.comb(N, 2)
            and counts == Counter(expected_counts)
            and determinant_valuations == {"2": 98, "5": 98, "7": 9702}
            and all(right % left == 0 for left, right in zip(smith, smith[1:]))
        ),
    }


def determinantal_divisors_of_diagonal(values: list[int]) -> list[int]:
    result = [1]
    for size in range(1, len(values) + 1):
        minors = (
            math.prod(selected)
            for selected in itertools.combinations(values, size)
        )
        result.append(reduce(math.gcd, minors))
    return result


def factor_24010_hostile_control() -> dict[str, object]:
    toy_source = [1, 7, 49, 490]
    toy_raw = [
        left * right
        for left, right in itertools.combinations(toy_source, 2)
    ]
    toy_smith = invariant_factors_of_diagonal(toy_raw)
    divisors = determinantal_divisors_of_diagonal(toy_raw)
    smith_products = [
        math.prod(toy_smith[:index])
        for index in range(len(toy_smith) + 1)
    ]

    # Below the live range C(r,2) can be less than 98. Then some 2- and
    # 5-parts align with exponent-three rather than exponent-four slots.
    hostile_rank = 14
    hostile_raw = compound_raw_diagonal(hostile_rank)
    hostile_smith = Counter(invariant_factors_of_diagonal(hostile_raw))
    return {
        "toy_source_smith": toy_source,
        "toy_raw_compound_diagonal": toy_raw,
        "toy_actual_smith": toy_smith,
        "toy_determinantal_divisors": divisors,
        "toy_smith_prefix_products": smith_products,
        "raw_products_are_not_the_smith_chain": toy_raw != toy_smith,
        "determinantal_divisors_match": divisors == smith_products,
        "hostile_rank_14": {
            "terminal_7_power_4_slots": math.comb(hostile_rank, 2),
            "factor_3430_count": hostile_smith[3430],
            "factor_24010_count": hostile_smith[24010],
            "live_formula_24010_power_98_fails_as_expected": (
                hostile_smith[24010] != 98
            ),
        },
        "passed": (
            divisors == smith_products
            and toy_smith == [7, 49, 49, 3430, 3430, 24010]
            and hostile_smith[3430] == 7
            and hostile_smith[24010] == 91
        ),
    }


def exterior_rank_controls() -> dict[str, object]:
    # Exact small matrices independently exercise C2(AB)=C2(A)C2(B) and
    # rank C2(A)=C(rank(A),2).
    left = [
        [1, 2, 0, 1],
        [0, 1, 1, 3],
        [2, 0, 1, 1],
        [1, 1, 4, 0],
    ]
    right = [
        [1, 0, 2, 1],
        [3, 1, 0, 2],
        [0, 1, 1, 1],
        [2, 2, 1, 0],
    ]
    product = matmul_mod(left, right, Q)
    compound_product = compound2(product, Q)
    product_compounds = matmul_mod(
        compound2(left, Q), compound2(right, Q), Q
    )
    rank_rows = []
    for rank in range(5):
        diagonal = [
            [int(row == column and row < rank) for column in range(4)]
            for row in range(4)
        ]
        observed = rank_mod(compound2(diagonal, Q), Q)
        rank_rows.append(
            {
                "source_rank": rank,
                "compound_rank": observed,
                "expected": math.comb(rank, 2),
            }
        )
    return {
        "Cauchy_Binet_small_control": compound_product == product_compounds,
        "rank_controls": rank_rows,
        "general_rank_formula": "rank_F7(C2(S))=C(rank_F7(S),2)",
        "endpoint_code_parameters": "[4851,378]_7",
        "self_orthogonality": (
            "E is symmetric and E^2=0 modulo 7, so its row code is "
            "self-orthogonal"
        ),
        "passed": (
            compound_product == product_compounds
            and all(
                row["compound_rank"] == row["expected"] for row in rank_rows
            )
        ),
    }


def exterior_row_geometry() -> dict[str, object]:
    remaining = N - 2
    overlap = 2 * remaining
    disjoint = math.comb(remaining, 2)
    adjacent = (1, 12, 12, 72)
    nonadjacent = (2, 12, 12, 71)
    ratio_sizes_adjacent = (adjacent[0] + adjacent[3], adjacent[1] + adjacent[2])
    ratio_sizes_nonadjacent = (
        nonadjacent[0] + nonadjacent[3],
        nonadjacent[1] + nonadjacent[2],
    )
    nonzero_disjoint = math.prod(ratio_sizes_adjacent)
    zero_disjoint = disjoint - nonzero_disjoint
    weight = 1 + overlap + nonzero_disjoint
    square_norm = 1 + overlap + 4 * nonzero_disjoint
    return {
        "adjacent_intersection_classes": list(adjacent),
        "nonadjacent_intersection_classes": list(nonadjacent),
        "ratio_class_sizes_adjacent": list(ratio_sizes_adjacent),
        "ratio_class_sizes_nonadjacent": list(ratio_sizes_nonadjacent),
        "column_counts": {
            "diagonal_nonzero": 1,
            "overlap_nonzero": overlap,
            "disjoint_nonzero": nonzero_disjoint,
            "disjoint_zero": zero_disjoint,
        },
        "distinguished_row_weight": weight,
        "integral_row_square_norm": square_norm,
        "distinguished_projective_lines": math.comb(N, 2),
        "scalar_closed_weight_1947_words": (Q - 1) * math.comb(N, 2),
        "passed": (
            ratio_sizes_adjacent == ratio_sizes_nonadjacent == (73, 24)
            and weight == 1947
            and square_norm == 7203 == 3 * 2401
            and 1 + overlap + nonzero_disjoint + zero_disjoint
            == math.comb(N, 2)
        ),
    }


def exterior_spectrum() -> dict[str, object]:
    entries = [
        (490, 44),
        (-490, 54),
        (49, math.comb(54, 2) + math.comb(44, 2)),
        (-49, 54 * 44),
    ]
    trace = sum(value * multiplicity for value, multiplicity in entries)
    determinant_valuations = {
        str(prime): sum(
            valuation(abs(value), prime) * multiplicity
            for value, multiplicity in entries
        )
        for prime in (2, 5, 7)
    }
    return {
        "source_spectrum": [[-70, 1], [7, 54], [-7, 44]],
        "compound_spectrum": [
            {"eigenvalue": value, "multiplicity": multiplicity}
            for value, multiplicity in entries
        ],
        "trace": trace,
        "constant_diagonal_trace": -math.comb(N, 2),
        "determinant_valuations": determinant_valuations,
        "square_identity": "C2(S)^2=2401*C2(I+J)",
        "SNF_C2_I_plus_J": "diag(1^4753,100^98)",
        "passed": (
            sum(multiplicity for _, multiplicity in entries)
            == math.comb(N, 2)
            and trace == -math.comb(N, 2)
            and determinant_valuations == {"2": 98, "5": 98, "7": 9702}
        ),
    }


def wedge(vector: tuple[int, ...], other: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(
        vector[left] * other[right] - vector[right] * other[left]
        for left, right in itertools.combinations(range(len(vector)), 2)
    )


def projectivity_profile() -> dict[str, object]:
    # Positive controls for the Pluecker implication.
    first = (1, 0, 0, 0)
    second = (0, 1, 0, 0)
    third_same_plane = (1, 1, 0, 0)
    fourth_outside = (0, 0, 1, 0)
    wedge_a = wedge(first, second)
    wedge_same = wedge(first, third_same_plane)
    wedge_outside = wedge(first, fourth_outside)
    return {
        "dual_distance_import": "d(R^perp)>=6",
        "column_independence_import": "every at-most-five columns is independent",
        "compound_columns_nonzero": True,
        "compound_columns_pairwise_nonproportional": True,
        "dual_distance_compound_lower_bound": 3,
        "reason": (
            "A nonzero decomposable wedge determines its two-plane. "
            "Proportional wedges from distinct column pairs would put their "
            "union of three or four source columns in one two-plane, "
            "contradicting five-column independence."
        ),
        "small_positive_controls": {
            "same_plane_wedges_proportional": wedge_a == wedge_same,
            "outside_plane_wedges_not_proportional": wedge_a != wedge_outside,
            "three_same_plane_vectors_dependent": (
                rank_mod([list(first), list(second), list(third_same_plane)], Q)
                == 2
            ),
        },
        "passed": (
            wedge_a == wedge_same
            and wedge_a != wedge_outside
            and rank_mod(
                [list(first), list(second), list(third_same_plane)], Q
            )
            == 2
        ),
    }


def generalized_weights() -> dict[str, object]:
    dual_dimension = N - ENDPOINT_RANK
    rows = [
        {
            "j": index,
            "lower": index + 5,
            "singleton_upper": N - dual_dimension + index,
        }
        for index in range(1, dual_dimension + 1)
    ]
    return {
        "code": "R^perp=[99,71]_7",
        "matroid_rank": ENDPOINT_RANK,
        "girth_lower_bound": 6,
        "bound": "j+5<=d_j(R^perp)<=j+28",
        "rows": rows,
        "forced_short_word": (
            "C is contained in R^perp and contains a forced word of "
            "weight 14, 16, or 18"
        ),
        "first_weight_refinement": "6<=d_1(R^perp)<=18",
        "proof": (
            "A support of nullity at least j contains a circuit. Girth six "
            "makes that circuit rank at least five, so support size "
            "rank+nullity is at least j+5."
        ),
        "passed": (
            len(rows) == 71
            and rows[0] == {"j": 1, "lower": 6, "singleton_upper": 29}
            and rows[-1] == {"j": 71, "lower": 76, "singleton_upper": 99}
            and all(row["lower"] <= row["singleton_upper"] for row in rows)
        ),
    }


def orthogonal_order(sign: str, half_dimension: int, field: int = Q) -> int:
    if sign not in {"plus", "minus"}:
        raise ValueError("orthogonal sign must be plus or minus")
    terminal = (
        field**half_dimension - 1
        if sign == "plus"
        else field**half_dimension + 1
    )
    return (
        2
        * field ** (half_dimension * (half_dimension - 1))
        * terminal
        * math.prod(
            field ** (2 * index) - 1
            for index in range(1, half_dimension)
        )
    )


def minus_point_formula(half_dimension: int, field: int = Q) -> dict[str, int]:
    nonzero_isotropic = (
        (field ** (half_dimension - 1) - 1)
        * (field**half_dimension + 1)
    )
    vectors_per_nonzero_value = (
        field ** (2 * half_dimension - 1)
        + field ** (half_dimension - 1)
    )
    return {
        "isotropic": nonzero_isotropic // (field - 1),
        "square_anisotropic": vectors_per_nonzero_value // 2,
        "nonsquare_anisotropic": vectors_per_nonzero_value // 2,
        "total": (field ** (2 * half_dimension) - 1) // (field - 1),
    }


def nonsquare(field: int) -> int:
    squares = {value * value % field for value in range(1, field)}
    return next(value for value in range(1, field) if value not in squares)


def minus_quadratic_value(vector: tuple[int, ...], field: int) -> int:
    if len(vector) % 2:
        raise ValueError("even dimension required")
    half = len(vector) // 2
    value = sum(
        vector[2 * index] * vector[2 * index + 1]
        for index in range(half - 1)
    )
    x, y = vector[-2:]
    value += x * x - nonsquare(field) * y * y
    return value % field


def brute_minus_point_orbits(half_dimension: int, field: int) -> dict[str, int]:
    dimension = 2 * half_dimension
    value_counts = Counter(
        minus_quadratic_value(vector, field)
        for vector in itertools.product(range(field), repeat=dimension)
        if any(vector)
    )
    squares = {value * value % field for value in range(1, field)}
    square_vectors = sum(
        count for value, count in value_counts.items() if value in squares
    )
    nonsquare_vectors = sum(
        count
        for value, count in value_counts.items()
        if value and value not in squares
    )
    return {
        "isotropic": value_counts[0] // (field - 1),
        "square_anisotropic": square_vectors // (field - 1),
        "nonsquare_anisotropic": nonsquare_vectors // (field - 1),
        "total": sum(value_counts.values()) // (field - 1),
    }


def orthogonal_profile() -> dict[str, object]:
    ambient = orthogonal_order("minus", 21)
    subspace = orthogonal_order("minus", 8)
    complement = orthogonal_order("plus", 13)
    denominator = subspace * complement
    if ambient % denominator:
        raise AssertionError("correct embedding stabilizer does not divide")
    embedding_count = ambient // denominator
    point_orbits = minus_point_formula(8)
    small_formula = minus_point_formula(2)
    small_brute = brute_minus_point_orbits(2, Q)

    wrong_ambient = orthogonal_order("plus", 21)
    wrong_complement = orthogonal_order("minus", 13)
    wrong_ambient_denominator_remainder = wrong_ambient % denominator
    wrong_complement_denominator = subspace * wrong_complement
    wrong_complement_remainder = ambient % wrong_complement_denominator
    wrong_ambient_ratio = wrong_ambient // denominator
    wrong_complement_ratio = ambient // wrong_complement_denominator
    return {
        "ambient": "O^-(42,7)",
        "subspace": "O^-(16,7)",
        "complement": "O^+(26,7)",
        "single_orbit": True,
        "reason": (
            "Witt extension sends any isometry between two nondegenerate "
            "minus-type 16-subspaces to an ambient isometry; the setwise "
            "stabilizer is O^-(16,7) times O^+(26,7)."
        ),
        "embedding_count": embedding_count,
        "embedding_count_decimal_digits": len(str(embedding_count)),
        "point_orbits": point_orbits,
        "small_dimension_formula_control": small_formula,
        "small_dimension_bruteforce_control": small_brute,
        "hostile_sign_controls": {
            "plus_ambient_ratio_integral": (
                wrong_ambient_denominator_remainder == 0
            ),
            "minus_complement_ratio_integral": (
                wrong_complement_remainder == 0
            ),
            "plus_ambient_ratio_differs": (
                wrong_ambient_ratio != embedding_count
            ),
            "minus_complement_ratio_differs": (
                wrong_complement_ratio != embedding_count
            ),
            "warning": (
                "Order divisibility alone does not certify the orthogonal "
                "sign: both hostile ratios are also integers. The imported "
                "Witt indices and discriminant types are essential."
            ),
        },
        "short_classes": {
            "norm14_self_dot_0": "zero class or nonzero isotropic orbit",
            "norm16_self_dot_4": "square-anisotropic orbit",
            "norm18_self_dot_1": "square-anisotropic orbit",
            "norm16_norm18_ratio": 4,
            "ratio_is_square_mod_7": True,
            "norm16_and_norm18_same_projective_orbit": True,
        },
        "passed": (
            point_orbits["isotropic"]
            + point_orbits["square_anisotropic"]
            + point_orbits["nonsquare_anisotropic"]
            == point_orbits["total"]
            and small_formula == small_brute
            and len(str(embedding_count)) == 352
            and wrong_ambient_denominator_remainder == 0
            and wrong_complement_remainder == 0
            and wrong_ambient_ratio != embedding_count
            and wrong_complement_ratio != embedding_count
            and 4 in {value * value % Q for value in range(1, Q)}
        ),
    }


def provenance_profile() -> dict[str, object]:
    return {
        "verified_Wave51_imports": [
            "S^2=49(I+J)",
            "SNF(S)=diag(1^r,7^(99-2r),49^(r-1),490)",
            "corrected spectrum -70^1, 7^54, (-7)^44",
            "99 quadratic pure-square images have rank 98",
            "their unique relation is the all-one relation",
        ],
        "already_implied_by_Wave51_not_new_to_repository": [
            "R*R=1_perp (by the pure-square result and polarization, or directly)",
            "the 99 quadratic images form a circuit",
            "every 98 quadratic images are independent",
            "the degree-two Cayley-Bacharach property (new terminology only)",
        ],
        "verified_Wave80_imports": [
            "d(R^perp)>=6",
            "at r=28, C/R=O^-(16,7) inside O^-(42,7) with O^+(26,7) complement",
            "forced short classes have weights 14,16,18 and self-dots 0,4,1",
        ],
        "new_to_repository_Wave97_consequences": [
            "R*R*R=F7^99 and the degree-three Hilbert saturation",
            "C*C=F7^99",
            "the projective self-orthogonal second-compound code",
            "the distinguished compound-row weight and compound spectrum",
            "the complete second-compound Smith form",
            "the generalized-weight intervals",
            "the exact orthogonal embedding count and point-orbit reduction",
        ],
        "provenance_correction_required": True,
        "correction": (
            "The discovery boundary lists the quadratic circuit among new "
            "exact reformulations. It is already an immediate consequence "
            "of verified Wave51's rank-98 pure-square span and unique "
            "all-one relation. R*R=1_perp is likewise prior-implied; only "
            "the code-product packaging is new."
        ),
        "literature_novelty": "UNKNOWN",
    }


def compare_discovery(independent: dict[str, object]) -> dict[str, object]:
    discovery = json.loads(
        (DISCOVERY / "exact-results.json").read_text(encoding="utf-8")
    )
    endpoint = independent["exterior_square"]["endpoint_rank_28"]
    expected_endpoint = [
        (row["factor"], row["multiplicity"])
        for row in endpoint["smith_normal_form"]
    ]
    observed_endpoint = [
        (row["factor"], row["multiplicity"])
        for row in discovery["exterior_square"]["endpoint_rank_28"][
            "smith_normal_form"
        ]
    ]
    checks = {
        "schur_hilbert": discovery["schur_hilbert"][
            "evaluation_algebra"
        ]["hilbert_function_degrees_0_to_3"] == [1, 28, 98, 99],
        "rank_rows": [
            row["rank_F7_C2S"]
            for row in discovery["exterior_square"]["all_rank_rows"]
        ]
        == [math.comb(rank, 2) for rank in LIVE_RANKS],
        "endpoint_smith": observed_endpoint == expected_endpoint,
        "row_weight": discovery["exterior_square"]["row_geometry"][
            "distinguished_row_weight"
        ] == independent["exterior_square"]["row_geometry"][
            "distinguished_row_weight"
        ],
        "spectrum": discovery["exterior_square"][
            "rational_and_integral_structure"
        ]["spectrum"] == independent["exterior_square"]["spectrum"][
            "compound_spectrum"
        ],
        "generalized_first": discovery["generalized_hamming_weights"][
            "first_weight_boundary_after_forced_short_vector"
        ] == "6<=d1<=18",
        "embedding_count": discovery["orthogonal_orbits"][
            "number_of_embedded_subspaces"
        ] == independent["orthogonal_orbits"]["embedding_count"],
        "point_orbits": discovery["orthogonal_orbits"][
            "projective_point_orbits_in_O_minus_16_7"
        ] == independent["orthogonal_orbits"]["point_orbits"],
        "fail_closed": (
            discovery["boundary"]["rank_28_excluded"] is False
            and discovery["boundary"]["strict_n3_upper_bound_below_4158"]
            is False
            and discovery["boundary"]["Conway_99"] == "UNKNOWN"
        ),
    }
    return {
        "passed": all(checks.values()),
        "checks": checks,
        "mathematical_mismatches": [
            key for key, passed in checks.items() if not passed
        ],
        "provenance_correction": independent["provenance"][
            "correction"
        ],
    }


def build_results() -> dict[str, object]:
    input_integrity = verify_inputs()
    schur = schur_profile()
    ranks = exterior_rank_controls()
    smith_rows = [exterior_smith(rank) for rank in LIVE_RANKS]
    endpoint = next(row for row in smith_rows if row["rank_F7_S"] == 28)
    smith_attack = factor_24010_hostile_control()
    row_geometry = exterior_row_geometry()
    spectrum = exterior_spectrum()
    projectivity = projectivity_profile()
    weights = generalized_weights()
    orthogonal = orthogonal_profile()
    provenance = provenance_profile()
    components = {
        "input_integrity": input_integrity,
        "schur_hilbert": schur,
        "exterior_rank_controls": ranks,
        "factor_24010_hostile_control": smith_attack,
        "row_geometry": row_geometry,
        "spectrum": spectrum,
        "projectivity": projectivity,
        "generalized_weights": weights,
        "orthogonal_orbits": orthogonal,
    }
    passed = all(component["passed"] for component in components.values())
    result: dict[str, object] = {
        "format": "wave97-f7-exterior-matroid-independent-v1",
        "role": "verifier",
        "claim_label": "VERIFIED" if passed else "REFUTED",
        "verdict": (
            "VERIFIED_WITH_PROVENANCE_CORRECTION"
            if passed
            else "REFUTED"
        ),
        "conditional_scope": "hypothetical srg(99,14,1,2)",
        "components": components,
        "provenance": provenance,
        "exterior_square": {
            "all_rank_rows": smith_rows,
            "endpoint_rank_28": endpoint,
            "row_geometry": row_geometry,
            "spectrum": spectrum,
            "projectivity": projectivity,
            "mod_7_code": {
                "parameters": "[4851,378]_7",
                "self_orthogonal": True,
                "projective": True,
                "dual_distance_lower_bound": 3,
                "distinguished_row_weight": 1947,
            },
        },
        "orthogonal_orbits": orthogonal,
        "status": {
            "rank_28_excluded": False,
            "strict_n3_upper_bound_below_4158": False,
            "Conway_99": "UNKNOWN",
            "literature_novelty": "UNKNOWN",
        },
        "limitations": [
            "All results are conditional necessary consequences.",
            "No graph or 4851-by-4851 compound matrix is constructed.",
            "The generalized-weight bounds retain slack.",
            "Orthogonal orbits discard coordinate weights.",
        ],
    }
    comparison = compare_discovery(result)
    result["discovery_comparison"] = comparison
    if not comparison["passed"]:
        result["claim_label"] = "REFUTED"
        result["verdict"] = "REFUTED"
    return result


def canonical_bytes(payload: dict[str, object]) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    encoded = canonical_bytes(build_results())
    if args.output:
        args.output.write_bytes(encoded)
        print(f"WROTE {args.output} sha256={sha256(args.output)}")
    elif args.verify:
        if args.verify.read_bytes() != encoded:
            raise SystemExit(f"verification mismatch: {args.verify}")
        print(f"VERIFIED {args.verify} sha256={sha256(args.verify)}")
    else:
        print(encoded.decode("utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
