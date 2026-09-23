#!/usr/bin/env python3
"""Exact Wave 36 modular-reflection arithmetic.

This checker certifies finite-field counts, Smith-form bookkeeping, and the
dimension bounds used in the proof-B report.  It does not construct a
231-by-231 endpoint matrix or certify the prose-to-graph bridge.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from collections import Counter
from pathlib import Path
from typing import Iterable


PUBLIC_HEAD = "697cc02bcbe16b69aaf08822298e03c66329c64c"
N = 231
RANK_Q_M = 44
SCALE = 21
C_DIAGONAL = -13
C_PLUS = 32
C_MINUS = 36
C_ZERO = 162
INPUT_HASHES = {
    "attempts/wave35-n3-upper-spectral/exact-results.json":
        "ca1df07bede11642fb1639a2ae554c1a31ce9a58424d5b3e5031c90ad550a194",
    "verification/wave35-n3-upper-spectral/independent-results.json":
        "c704d8fce8f1d5975204b9a06ada0098c66fbdb9e0de8016a1ff89d86e691305",
    "verification/wave35-n3-upper-spectral/run-report.yaml":
        "40ded0143abe9b0edcec1b87146621dd6ee0fae3483d3d522fec0c83417d6c95",
    "verification/wave23-index-pranks/2026-07-23T192952Z-audit.md":
        "bfd02ebc39515e27e9e2c79d8e286905086f5747a02a310036ce27dd29ff3116",
    "verification/wave24-n3-708-index/2026-07-23T204222Z-audit.md":
        "958b9b2d13d697c281ba490d21b170f453d059bfaa952f8e92a9709b6c8d3cd8",
}


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_frozen_inputs(root: Path | None = None) -> None:
    base = repository_root() if root is None else root
    actual = {
        relative: sha256_file(base / relative)
        for relative in INPUT_HASHES
    }
    if actual != INPUT_HASHES:
        raise AssertionError(
            "frozen input mismatch\n"
            f"expected={INPUT_HASHES!r}\nactual={actual!r}"
        )


def quadratic_value(vector: Iterable[int], diagonal: Iterable[int], p: int) -> int:
    return sum(a * x * x for a, x in zip(diagonal, vector)) % p


def projective_norm_count_bruteforce(
    dimension: int,
    determinant_class: int,
    target: int = 2,
    p: int = 3,
) -> int:
    """Count target-norm projective points in a canonical odd-field form.

    For p=3, every projective line has exactly two nonzero representatives,
    and multiplying by either representative does not change the norm.
    """

    if p != 3:
        raise ValueError("the frozen projective normalization is for p=3")
    if dimension < 1:
        raise ValueError("dimension must be positive")
    if determinant_class not in (1, 2):
        raise ValueError("F_3 determinant class must be 1 or 2")
    diagonal = [1] * (dimension - 1) + [determinant_class]
    vector_count = sum(
        quadratic_value(vector, diagonal, p) == target
        for vector in itertools.product(range(p), repeat=dimension)
    )
    if vector_count % (p - 1):
        raise AssertionError("nonzero norm vectors did not split into lines")
    return vector_count // (p - 1)


def ternary_count_table(max_dimension: int = 7) -> dict[int, tuple[int, int]]:
    return {
        dimension: (
            projective_norm_count_bruteforce(dimension, 1),
            projective_norm_count_bruteforce(dimension, 2),
        )
        for dimension in range(1, max_dimension + 1)
    }


def ternary_rank_lower_bound(
    point_count: int = N,
    orthogonal_companions: int = C_ZERO,
) -> int:
    """Return the certified rank floor from projective and orthogonal counts."""

    counts = ternary_count_table(7)
    # At dimensions <=6 there are too few target-norm projective points.
    if max(max(pair) for dimension, pair in counts.items() if dimension <= 6) >= point_count:
        raise AssertionError("dimension-at-most-six count no longer excludes")
    # In dimension seven, the orthogonal complement of an anisotropic point
    # is a nondegenerate six-space, with at most 126 target-norm points.
    if max(counts[6]) >= orthogonal_companions:
        raise AssertionError("dimension-seven orthogonal count no longer excludes")
    return 8


def symmetric_cube_dimension(rank: int) -> int:
    if rank < 0:
        raise ValueError("rank must be nonnegative")
    return math.comb(rank + 2, 3)


def mod7_cubic_residues() -> dict[int, int]:
    return {value: pow(value % 7, 3, 7) for value in (0, 1, 2, -2)}


def mod7_rank_lower_bound(point_count: int = N) -> int:
    rank = 0
    while symmetric_cube_dimension(rank) < point_count:
        rank += 1
    return rank


def p_exponents(rank_mod_p: int) -> list[int]:
    """p-adic Smith exponents forced by C^2=21^2 I."""

    if not 0 <= rank_mod_p <= N // 2:
        raise ValueError("rank is outside the square-zero range")
    return (
        [0] * rank_mod_p
        + [1] * (N - 2 * rank_mod_p)
        + [2] * rank_mod_p
    )


def smith_factors(r3: int, r7: int) -> list[int]:
    a = p_exponents(r3)
    b = p_exponents(r7)
    factors = [3**x * 7**y for x, y in zip(a, b)]
    if any(left > right or right % left for left, right in zip(factors, factors[1:])):
        raise AssertionError("factors are not an invariant-factor chain")
    if any(factors[i] * factors[N - 1 - i] != SCALE**2 for i in range(N)):
        raise AssertionError("reciprocal Smith pairing failed")
    return factors


def smith_factor_counts(r3: int, r7: int) -> dict[str, int]:
    counts = Counter(smith_factors(r3, r7))
    return {str(factor): counts[factor] for factor in sorted(counts)}


def admissible_rank_pairs() -> list[tuple[int, int]]:
    """Apply the new lower bounds, rational-rank ceilings, and h=1 mod 4."""

    return [
        (r3, r7)
        for r3 in range(ternary_rank_lower_bound(), RANK_Q_M + 1)
        for r7 in range(mod7_rank_lower_bound(), RANK_Q_M + 1)
        if (r3 + r7) % 2 == 0
    ]


def index_data(r3: int, r7: int) -> dict[str, int | str]:
    u = RANK_Q_M - r3
    v = RANK_Q_M - r7
    h = 3**u * 7**v
    return {
        "v3_h": u,
        "v7_h": v,
        "h": str(h),
        "h_mod_4": h % 4,
    }


def build_results() -> dict[str, object]:
    verify_frozen_inputs()
    counts = ternary_count_table()
    pairs = admissible_rank_pairs()
    boundary_shapes = {
        f"r3={r3},r7={r7}": {
            "smith_factor_counts": smith_factor_counts(r3, r7),
            "index": index_data(r3, r7),
        }
        for r3, r7 in ((8, 12), (9, 11), (44, 44))
    }
    return {
        "schema_version": 1,
        "claim_label": "DERIVED_INCONCLUSIVE",
        "scope": "conditional n3=4158 integral-reflection modular consequences",
        "frozen_public_head": PUBLIC_HEAD,
        "endpoint": {
            "n": N,
            "rank_Q_M": RANK_Q_M,
            "C_definition": "C=2M-21I",
            "C_squared": "441I",
            "C_diagonal": C_DIAGONAL,
            "C_off_diagonal_profile": {
                "+2": C_PLUS,
                "-2": C_MINUS,
                "0": C_ZERO,
            },
            "row_sum": C_DIAGONAL + 2 * C_PLUS - 2 * C_MINUS,
            "row_squared_norm": (
                C_DIAGONAL**2 + 4 * (C_PLUS + C_MINUS)
            ),
            "distinct_row_orthogonality_norm": 2 * SCALE**2,
            "proportional_mod3_false_norm": 2 * 15**2,
        },
        "smith_form_C": {
            "all_invariant_factors_divide": SCALE**2,
            "pairing": "d_i*d_(232-i)=441",
            "p_exponent_profile": (
                "for p in {3,7}: 0^r_p,1^(231-2r_p),2^r_p"
            ),
            "formula_if_r3_le_r7": (
                "1^r3,3^(r7-r3),21^(231-2r7),"
                "147^(r7-r3),441^r3"
            ),
            "formula_if_r7_le_r3": (
                "1^r7,7^(r3-r7),21^(231-2r3),"
                "63^(r3-r7),441^r7"
            ),
            "boundary_shapes": boundary_shapes,
        },
        "mod3": {
            "factorization": "C=V H V^T over F3 with H nondegenerate",
            "point_norm": 2,
            "projective_points": N,
            "projective_points_are_distinct": True,
            "orthogonal_companions_per_point": C_ZERO,
            "canonical_projective_norm2_counts": {
                str(dimension): list(pair)
                for dimension, pair in counts.items()
            },
            "dimension_6_max": max(counts[6]),
            "dimension_7_orthogonal_complement_max": max(counts[6]),
            "rank_lower_bound": ternary_rank_lower_bound(),
        },
        "mod7": {
            "factorization": "C=V H V^T over F7 with H nondegenerate",
            "point_norm": 1,
            "off_diagonal_inner_products": [0, 2, -2],
            "cubic_residues": {
                str(key): value for key, value in mod7_cubic_residues().items()
            },
            "cubic_gram_identity": "C^(o3)=4(I+C) mod 7",
            "inverse_identity": "(I+C)^(-1)=I-C because C^2=0 mod 7",
            "independent_symmetric_cubes": N,
            "dimension_at_rank_10": symmetric_cube_dimension(10),
            "dimension_at_rank_11": symmetric_cube_dimension(11),
            "rank_lower_bound": mod7_rank_lower_bound(),
        },
        "combined_index_reduction": {
            "rank_F3_range": [ternary_rank_lower_bound(), RANK_Q_M],
            "rank_F7_range": [mod7_rank_lower_bound(), RANK_Q_M],
            "rank_sum_even": True,
            "h_formula": "3^(44-r3)*7^(44-r7)",
            "v3_h_upper_bound": RANK_Q_M - ternary_rank_lower_bound(),
            "v7_h_upper_bound": RANK_Q_M - mod7_rank_lower_bound(),
            "admissible_rank_pair_count": len(pairs),
            "admissible_rank_pairs": [list(pair) for pair in pairs],
        },
        "conclusion": {
            "endpoint_excluded": False,
            "upper_bound_improved_below_4158": False,
            "target_status": "UNKNOWN",
            "new_exact_reduction": (
                "rank_F3(M)>=8, rank_F7(M)>=11, r3+r7 even; "
                "the full Smith form of C is then fixed by (r3,r7)"
            ),
            "next_target": (
                "couple the finite-field configurations to rooted "
                "incidence constraints strongly enough to raise a rank "
                "floor to 45 or otherwise contradict rank_Q(M)=44"
            ),
        },
        "limitations": [
            "No endpoint matrix, graph, or finite-field configuration is constructed.",
            "The modular rank bounds are necessary conditions, not an endpoint exclusion.",
            "The checker audits exact arithmetic, not the graph-to-reflection bridge.",
            "No literature novelty claim is made.",
        ],
    }


def canonical_json(payload: dict[str, object]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.output is not None and args.verify is not None:
        parser.error("--output and --verify are mutually exclusive")
    rendered = canonical_json(build_results())
    if args.verify is not None:
        if args.verify.read_text(encoding="utf-8") != rendered:
            raise SystemExit(f"verification failed: {args.verify}")
        print(f"verified {args.verify}")
    elif args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
