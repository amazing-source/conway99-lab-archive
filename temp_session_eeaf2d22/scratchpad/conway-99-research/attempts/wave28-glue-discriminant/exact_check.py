#!/usr/bin/env python3
"""Exact Wave 28 discriminant-form and one-root necessary-condition census."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Iterable


PUBLIC_HEAD = "d76d030f6d74e2e1b7ca2b2f0f97536241b3a10b"
H_VALUES = (9, 21, 49, 81, 189, 441, 729, 1029)
INPUT_HASHES = {
    "agents/2026-07-24-wave28-orchestrator-brief.md":
        "6a15446551b78822706a8e005bef49a411b904cf05f9459b6b3350239839ee1e",
    "verification/wave21-lattice-extension/2026-07-23T184926Z-audit.md":
        "45814560f1d5bffb3b00144022a3a1f8d069e71dfe430247a1871822ac08f268",
    "verification/wave24-n3-708-index/2026-07-23T204222Z-audit.md":
        "958b9b2d13d697c281ba490d21b170f453d059bfaa952f8e92a9709b6c8d3cd8",
    "verification/wave25-n3-708-strictness/2026-07-23T215549Z-audit.md":
        "642255098bf424654e1a3a8c926a924ae8bf068cd422f0f367f64f9e402648de",
    "verification/wave27-general-root-tensor/2026-07-24T010548Z-audit.md":
        "68747c2b09a86f10eb58f7bccce6670b4d99856a073a87a3dcae2c0555f37033",
}
NONSQUARE = {3: 2, 7: 3}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_inputs(root: Path | None = None) -> dict[str, str]:
    root = repo_root() if root is None else root
    actual: dict[str, str] = {}
    for relative, expected in INPUT_HASHES.items():
        path = root / relative
        if not path.is_file():
            raise AssertionError(f"missing frozen input: {relative}")
        observed = sha256(path)
        if observed != expected:
            raise AssertionError(
                f"frozen input mismatch for {relative}: "
                f"expected {expected}, observed {observed}"
            )
        actual[relative] = observed
    return actual


def valuation(value: int, prime: int) -> int:
    exponent = 0
    while value % prime == 0:
        value //= prime
        exponent += 1
    return exponent


def exponents(h: int) -> tuple[int, int]:
    u = valuation(h, 3)
    v = valuation(h, 7)
    if 3**u * 7**v != h:
        raise AssertionError(f"determinant is not 3,7-smooth: {h}")
    return u, v


def legendre(value: int, prime: int) -> int:
    residue = value % prime
    if residue == 0:
        raise ValueError("Legendre symbol requires a prime-adic unit")
    power = pow(residue, (prime - 1) // 2, prime)
    if power == 1:
        return 1
    if power == prime - 1:
        return -1
    raise AssertionError("Euler criterion returned an invalid residue")


def radical_level(h: int) -> int:
    u, v = exponents(h)
    return (3 if u else 1) * (7 if v else 1)


def required_delta_product(u: int, v: int) -> int:
    """Milgram sign for q=<2a/3>^u plus <2b/7>^v at signature 44."""
    if (u + v) % 2:
        raise AssertionError("the determinant-one-mod-four rows have even u+v")
    return -1 if ((u + v) // 2 + 1) % 2 else 1


def canonical_coefficients(prime: int, dimension: int, delta: int) -> list[int]:
    """Diagonal coefficients a in q(x)=sum 2*a_i*x_i^2/p."""
    if dimension == 0:
        if delta != 1:
            raise AssertionError("the zero-dimensional form has delta +1")
        return []
    if delta not in (-1, 1):
        raise ValueError("delta must be a Legendre sign")
    coefficients = [1] * dimension
    if delta == -1:
        coefficients[-1] = NONSQUARE[prime]
    observed = 1
    for value in coefficients:
        observed *= legendre(value, prime)
    if observed != delta:
        raise AssertionError("canonical discriminant-form sign mismatch")
    return coefficients


def i_phase(exponent: int, sign: int) -> tuple[int, int]:
    phases = ((1, 0), (0, 1), (-1, 0), (0, -1))
    real, imag = phases[exponent % 4]
    return sign * real, sign * imag


def scaled_dual_delta_ratio(prime: int, u: int, v: int) -> int:
    """Return delta(G,p)/delta(S,p) from the local Jordan blocks."""
    if prime == 3:
        m, other_prime, other_exponent = u, 7, v
        ell = 7
    elif prime == 7:
        m, other_prime, other_exponent = v, 3, u
        ell = 3
    else:
        raise ValueError("only p=3,7 occur")
    return (
        legendre(2, prime) ** 44
        * legendre(ell, prime) ** (44 - m)
        * legendre(other_prime, prime) ** other_exponent
    )


def discriminant_classes() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for h in H_VALUES:
        u, v = exponents(h)
        required = required_delta_product(u, v)
        delta3_values: Iterable[int] = (1,) if u == 0 else (1, -1)
        for delta3 in delta3_values:
            if v == 0:
                delta7 = 1
                if delta3 != required:
                    continue
            else:
                delta7 = required * delta3
            if u == 0 and delta3 != 1:
                continue
            coeff3 = canonical_coefficients(3, u, delta3)
            coeff7 = canonical_coefficients(7, v, delta7)
            phase = i_phase(u + v, delta3 * delta7)
            if phase != (-1, 0):
                raise AssertionError("Milgram phase is not the signature-44 phase")
            ratio3 = scaled_dual_delta_ratio(3, u, v)
            ratio7 = scaled_dual_delta_ratio(7, u, v)
            if ratio3 != 1 or ratio7 != 1:
                raise AssertionError("scaled-dual discriminant signs diverged")
            rows.append(
                {
                    "class_id": (
                        f"h{h}-d3{'p' if delta3 == 1 else 'm'}"
                        f"-d7{'p' if delta7 == 1 else 'm'}"
                    ),
                    "h": h,
                    "v3_h": u,
                    "v7_h": v,
                    "exact_level_S": radical_level(h),
                    "A_S": {
                        "group": f"(Z/3)^{u} direct_sum (Z/7)^{v}",
                        "delta_3": delta3,
                        "delta_7": delta7,
                        "q3_coefficients_for_2a_over_3": coeff3,
                        "q7_coefficients_for_2a_over_7": coeff7,
                    },
                    "A_G": {
                        "group": (
                            f"(Z/3)^{44-u} direct_sum "
                            f"(Z/7)^{44-v}"
                        ),
                        "delta_3": delta3,
                        "delta_7": delta7,
                    },
                    "rank_mod_3_S": 44 - u,
                    "rank_mod_7_S": 44 - v,
                    "rank_mod_3_G": u,
                    "rank_mod_7_G": v,
                    "milgram_phase": {"real": -1, "imaginary": 0},
                }
            )
    return rows


def root_projection_distributions(
    enforce_cubic_projection: bool = True,
) -> list[dict[str, object]]:
    """Enumerate counts of coordinates 2,1,0,-1,-2 for t=XSr."""
    rows: list[dict[str, object]] = []
    for plus_two in range(22):
        for minus_two in range(22):
            plus_one = 21 - 3 * plus_two - minus_two
            minus_one = 21 - plus_two - 3 * minus_two
            if plus_one < 0 or minus_one < 0:
                continue
            zero = 189 + 3 * (plus_two + minus_two)
            cube_sum = 6 * (plus_two - minus_two)
            pure_cubic_energy = Fraction(cube_sum * cube_sum, 8)
            if enforce_cubic_projection and pure_cubic_energy > 60:
                continue
            row = {
                "plus_2": plus_two,
                "plus_1": plus_one,
                "zero": zero,
                "minus_1": minus_one,
                "minus_2": minus_two,
                "coordinate_sum": 0,
                "squared_norm": 42,
                "cube_sum": cube_sum,
                "pure_line_cubic_energy": (
                    f"{pure_cubic_energy.numerator}/"
                    f"{pure_cubic_energy.denominator}"
                ),
            }
            if sum(
                row[key]
                for key in ("plus_2", "plus_1", "zero", "minus_1", "minus_2")
            ) != 231:
                raise AssertionError("root projection does not have 231 entries")
            rows.append(row)
    return rows


def build_results(root: Path | None = None) -> dict[str, object]:
    frozen = verify_inputs(root)
    classes = discriminant_classes()
    moment_rows = root_projection_distributions(False)
    cubic_rows = root_projection_distributions(True)
    if len(classes) != 12:
        raise AssertionError("expected exactly twelve discriminant-form types")
    if len(moment_rows) != 46 or len(cubic_rows) != 32:
        raise AssertionError("unexpected one-root distribution census")
    hostile = next(
        row
        for row in cubic_rows
        if (
            row["plus_2"],
            row["plus_1"],
            row["zero"],
            row["minus_1"],
            row["minus_2"],
        )
        == (0, 21, 189, 21, 0)
    )
    rejected_mutation = {
        "plus_2": 4,
        "plus_1": 9,
        "zero": 201,
        "minus_1": 17,
        "minus_2": 0,
        "coordinate_sum": 0,
        "squared_norm": 42,
        "cube_sum": 24,
        "pure_line_cubic_energy": "72/1",
        "rejected_because": "pure line cubic energy exceeds global tensor norm 60",
    }
    return {
        "schema_version": 1,
        "public_head": PUBLIC_HEAD,
        "claim_label": "DERIVED",
        "frozen_inputs": frozen,
        "discriminant_form_census": {
            "count": len(classes),
            "correction": {
                "rejected_count": 11,
                "reason": (
                    "four pure-prime rows contribute one class each and "
                    "four mixed-prime rows contribute two each: 4+8=12"
                ),
            },
            "rows": classes,
            "theorem": (
                "A_S is elementary at 3 and 7; the normalized Gauss sign "
                "at signature 44 leaves exactly these twelve isometry types."
            ),
        },
        "single_root_glue": {
            "root_is_primitive": True,
            "root_divisibility": 1,
            "orthogonal_A1_summand": False,
            "index_of_A1_plus_complement": 2,
            "complement_rank": 43,
            "complement_determinant_formula": "2*h",
            "complement_2_primary_form": "<-1/2>",
            "odd_discriminant_form": "same as A_S",
        },
        "single_root_projector_image": {
            "map": "r -> t=X*S*r",
            "coordinate_alphabet": [-2, -1, 0, 1, 2],
            "coordinate_sum": 0,
            "squared_norm": 42,
            "inner_product_scale": 21,
            "moment_only_distribution_count": len(moment_rows),
            "tensor_filtered_distribution_count": len(cubic_rows),
            "tensor_filtered_distributions": cubic_rows,
            "surviving_hostile_control": hostile,
            "active_rejected_mutation": rejected_mutation,
        },
        "root_sublattice_reduction": {
            "R": "orthogonal ADE root lattice generated by every norm-two vector",
            "primitive_closure": "Rbar=(R tensor Q) intersect S",
            "H0": "Rbar/R is isotropic in A_R and every nonzero used coset has minimum >=4",
            "K": "Rbar_perp intersect S is rootless",
            "H1": (
                "S/(Rbar direct_sum K) is the graph of an anti-isometry "
                "between discriminant subgroups, with "
                "H1_perp/H1 one of the twelve A_S forms"
            ),
            "prime_to_21_cancellation": (
                "for every prime p other than 3 and 7, "
                "q_K,p is anti-isometric to q_Rbar,p in full; "
                "in particular their p-adic determinant valuations agree"
            ),
            "determinant_formula": (
                "h=det(R)*det(K)/(|H0|^2*|H1|^2)"
            ),
        },
        "scope": {
            "excluded_h_rows": [],
            "finite_lattice_classification": "NOT_OBTAINED",
            "general_even_rank_44_forms": "UNKNOWN",
            "n3_708": "UNKNOWN",
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
    }


def canonical_json(payload: dict[str, object]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rendered = canonical_json(build_results())
    if args.output is None:
        print(rendered, end="")
        return
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
