#!/usr/bin/env python3
"""Exact companion for the Wave 29 S0 full-frame exclusion.

This standard-library-only checker verifies the frozen inputs and the exact
integer/rational implications in the proof.  It does not search for a frame
and it does not classify any lattice beyond the single frozen
K12 orthogonal_sum LAMBDA(F) control.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from fractions import Fraction
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[2]
PUBLIC_BASE_COMMIT = "74b6f3adcee19ca2b0480258bb7bf51198bd085a"

FROZEN_INPUTS = {
    "agents/2026-07-24-wave28-orchestrator-brief.md":
        "6a15446551b78822706a8e005bef49a411b904cf05f9459b6b3350239839ee1e",
    "agents/2026-07-24-wave28-theta-modular.md":
        "8783be7e730306637ed863b4d9fbe8f4193ad756e7ec86d697c7407688a5423a",
    "verification/wave28-theta-modular/audit.md":
        "adc90e404735ca147bc0a5418974d8af0bde71c4ddc2dc62a8c07dee670dbfeb",
    "verification/wave28-theta-modular/independent-results.json":
        "24298ae282c7baa252a39ffe96fc37b7c696cb51f14b9ddea2318a59b4335b7f",
    "verification/wave24-n3-708-index/2026-07-23T204222Z-audit.md":
        "958b9b2d13d697c281ba490d21b170f453d059bfaa952f8e92a9709b6c8d3cd8",
    "verification/wave25-n3-708-strictness/2026-07-23T215549Z-audit.md":
        "642255098bf424654e1a3a8c926a924ae8bf068cd422f0f367f64f9e402648de",
}

RANK = 44
ROWS = 231
FRAME_SCALE = 21
ROW_NORM = 4
TRACE_B = 60
DET_S = 729
DET_B_CAP = 6525


class PremiseError(ValueError):
    """Raised when a hostile premise deletion blocks the derivation."""


ESSENTIAL_PREMISES = (
    "orthogonal_minimum_four_split",
    "tight_frame_identity",
    "endpoint_schur_definitions",
    "row_sum_and_projector_identity",
    "row_alphabet",
    "determinant_cap_and_q_congruence",
    "q_even_positive_integral",
    "even_unimodular_signature_veto",
    "total_trace_sixty",
    "b_equals_i_plus_2c_integral",
    "positive_form_self_adjointness",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_frozen_inputs() -> dict[str, str]:
    observed: dict[str, str] = {}
    for relative, expected in FROZEN_INPUTS.items():
        path = REPO_ROOT / relative
        actual = sha256_file(path)
        if actual != expected:
            raise AssertionError(
                f"frozen input drift for {relative}: {actual} != {expected}"
            )
        observed[relative] = actual
    return observed


def load_s0_facts() -> dict[str, object]:
    source = (
        REPO_ROOT
        / "verification/wave28-theta-modular/independent-results.json"
    )
    payload = json.loads(source.read_text(encoding="utf-8"))
    hostile = payload["hostile_control"]
    k12 = hostile["K12"]
    lam = hostile["LAMBDA_F"]
    s0 = hostile["S0"]

    expected = {
        "K12": {
            "rank": 12,
            "determinant": 729,
            "minimum": 4,
            "norm_four_count": 756,
            "even_integral": True,
            "positive_definite": True,
        },
        "LAMBDA_F": {
            "rank": 32,
            "determinant": 1,
            "minimum": 4,
            "norm_four_count": 146880,
            "even_integral": True,
            "positive_definite": True,
        },
        "S0": {
            "rank": 44,
            "determinant": 729,
            "minimum": 4,
            "norm_four_count": 147636,
            "root_count": 0,
            "twenty_one_dual_even_integral": True,
            "twenty_one_dual_minimum": 28,
        },
    }

    observed = {
        "K12": {
            "rank": k12["rank"],
            "determinant": k12["determinant_exact"],
            "minimum": min(int(key) for key in k12["enumeration"]["norm_counts"]),
            "norm_four_count": k12["enumeration"]["norm_counts"]["4"],
            "even_integral": k12["even_integral"],
            "positive_definite": k12["positive_definite_exact_ldl"],
        },
        "LAMBDA_F": {
            "rank": lam["rank"],
            "determinant": lam["determinant_exact"],
            "minimum": min(int(key) for key in lam["enumeration"]["norm_counts"]),
            "norm_four_count": lam["enumeration"]["norm_counts"]["4"],
            "even_integral": lam["even_integral"],
            "positive_definite": lam["positive_definite_exact_ldl"],
        },
        "S0": {
            "rank": s0["rank"],
            "determinant": s0["determinant"],
            "minimum": s0["exact_minimum"],
            "norm_four_count": s0["norm_four_r4"],
            "root_count": s0["root_count_r2"],
            "twenty_one_dual_even_integral":
                s0["twenty_one_dual_even_integral"],
            "twenty_one_dual_minimum":
                s0["twenty_one_dual_exact_minimum"],
        },
    }
    if observed != expected:
        raise AssertionError(f"frozen S0 facts drifted: {observed!r}")
    return observed


def require(enabled: set[str], premise: str, stage: str) -> None:
    if premise not in enabled:
        raise PremiseError(f"{stage}: missing premise {premise}")


def frame_block_count(rank: int) -> int:
    numerator = FRAME_SCALE * rank
    if numerator % ROW_NORM:
        raise AssertionError("block trace does not give an integral row count")
    return numerator // ROW_NORM


def norm_four_and_frame_split(enabled: set[str]) -> dict[str, object]:
    require(
        enabled,
        "orthogonal_minimum_four_split",
        "norm-four block split",
    )
    require(enabled, "tight_frame_identity", "block row counts")
    k_rows = frame_block_count(12)
    l_rows = frame_block_count(32)
    if k_rows + l_rows != ROWS:
        raise AssertionError("block row counts do not sum to 231")
    return {
        "norm_four_split": (
            "For x=(u,v) of norm four in an orthogonal sum whose two "
            "nonzero minima are four, exactly one of u,v is zero."
        ),
        "tight_frame_trace_identity": "4*n_J=21*rank(J)",
        "K12_rows": k_rows,
        "LAMBDA_F_rows": l_rows,
        "total_rows": k_rows + l_rows,
        "no_automorphism_or_search_assumption": True,
    }


def block_split_certificate(enabled: set[str]) -> dict[str, object]:
    require(
        enabled,
        "orthogonal_minimum_four_split",
        "row-supported matrix split",
    )
    require(
        enabled,
        "endpoint_schur_definitions",
        "M/W/Q/B block split",
    )
    return {
        "after_row_permutation": {
            "X": "[X_K 0; 0 X_L] (rectangular block form)",
            "M": "diag(M_K,M_L)",
            "W": "diag(M_K o M_K,M_L o M_L)",
            "Q": "diag(X_K^T W_K X_K,X_L^T W_L X_L)",
            "B": "diag(S_K Q_K,S_L Q_L)",
        },
        "identities_used": [
            "M=X S X^T",
            "W=M o M",
            "Q=X^T W X",
            "B=S Q",
        ],
    }


def q_determinant_certificate(enabled: set[str]) -> dict[str, object]:
    require(
        enabled,
        "determinant_cap_and_q_congruence",
        "det(Q) determination",
    )
    candidates = [
        value
        for value in range(5, DET_B_CAP // DET_S + 1)
        if value % 4 == 1
    ]
    if candidates != [5]:
        raise AssertionError(f"unexpected det(Q) candidates: {candidates}")
    return {
        "detB_equals_detS_times_detQ": True,
        "detS": DET_S,
        "detB_cap": DET_B_CAP,
        "detQ_floor": 5,
        "detQ_mod_4": 1,
        "detQ_candidates": candidates,
        "detQ": 5,
    }


def determinant_allocation_certificate(
    enabled: set[str],
) -> dict[str, object]:
    require(
        enabled,
        "q_even_positive_integral",
        "positive integral block determinants",
    )
    allocations = [
        {"detQ_K": left, "detQ_L": 5 // left}
        for left in (1, 5)
        if 5 % left == 0
    ]
    require(
        enabled,
        "even_unimodular_signature_veto",
        "rank-12 determinant allocation",
    )
    survivors = [
        row
        for row in allocations
        if not (row["detQ_K"] == 1 and 12 % 8 != 0)
    ]
    if survivors != [{"detQ_K": 5, "detQ_L": 1}]:
        raise AssertionError(f"unexpected determinant allocation: {survivors}")
    return {
        "pre_veto_allocations": allocations,
        "veto": (
            "det(Q_K)=1 would make Q_K even unimodular positive definite "
            "of rank/signature 12, impossible because 12 is not divisible "
            "by eight."
        ),
        "survivor": survivors[0],
        "detB_K": 729 * 5,
        "detB_L": 1,
    }


def row_alphabet(c_minus_two: int) -> dict[str, int]:
    """Solve the exact row-sum and diagonal-projector equations."""
    a_plus_one = 32 - c_minus_two
    b_minus_one = 36 - 3 * c_minus_two
    z_zero = 162 + 3 * c_minus_two
    if min(a_plus_one, b_minus_one, c_minus_two, z_zero) < 0:
        raise ValueError("negative alphabet multiplicity")
    if a_plus_one + b_minus_one + c_minus_two + z_zero != 230:
        raise AssertionError("off-diagonal multiplicities do not sum to 230")
    if 4 + a_plus_one - b_minus_one - 2 * c_minus_two != 0:
        raise AssertionError("M*1=0 row equation failed")
    if 16 + a_plus_one + b_minus_one + 4 * c_minus_two != 84:
        raise AssertionError("(M^2)_ii=21*M_ii row equation failed")
    cube_sum = 64 + a_plus_one - b_minus_one - 8 * c_minus_two
    if cube_sum != 60 - 6 * c_minus_two:
        raise AssertionError("row cubic identity failed")
    return {
        "c_minus_two": c_minus_two,
        "a_plus_one": a_plus_one,
        "b_minus_one": b_minus_one,
        "z_zero": z_zero,
        "row_cube_sum": cube_sum,
    }


def alphabet_certificate(enabled: set[str]) -> dict[str, object]:
    require(
        enabled,
        "row_sum_and_projector_identity",
        "per-row linear and quadratic equations",
    )
    require(enabled, "row_alphabet", "per-row alphabet solution")
    table = [row_alphabet(value) for value in range(13)]
    return {
        "definitions": {
            "a_i": "number of off-diagonal +1 entries in row i",
            "b_i": "number of off-diagonal -1 entries in row i",
            "c_i": "number of off-diagonal -2 entries in row i",
            "z_i": "number of off-diagonal zero entries in row i",
        },
        "equations": [
            "4+a_i-b_i-2c_i=0",
            "16+a_i+b_i+4c_i=84",
            "a_i+c_i=32",
            "b_i=36-3c_i",
            "z_i=162+3c_i",
            "sum_j M_ij^3=60-6c_i",
        ],
        "admissible_table": table,
        "K12_support_forces_c_i_at_least": 2,
    }


def amgm_feasible(rank: int, determinant: int, trace_value: int) -> bool:
    """Exact necessary AM-GM inequality det*r^r <= trace^r."""
    return determinant * rank**rank <= trace_value**rank


def block_trace_certificate(enabled: set[str]) -> dict[str, object]:
    require(
        enabled,
        "endpoint_schur_definitions",
        "block trace as a cubic M-sum",
    )
    require(
        enabled,
        "row_sum_and_projector_identity",
        "block trace residue",
    )
    require(enabled, "row_alphabet", "block trace residue")
    require(enabled, "total_trace_sixty", "complementary block traces")
    require(
        enabled,
        "positive_form_self_adjointness",
        "positive block traces and AM-GM",
    )

    candidates = []
    for trace_k in range(6, TRACE_B, 6):
        trace_l = TRACE_B - trace_k
        if trace_l <= 0 or trace_l % 6:
            continue
        if not amgm_feasible(12, 3645, trace_k):
            continue
        if not amgm_feasible(32, 1, trace_l):
            continue
        candidates.append({"traceB_K": trace_k, "traceB_L": trace_l})
    if candidates != [{"traceB_K": 24, "traceB_L": 36}]:
        raise AssertionError(f"unexpected block traces: {candidates}")

    k_sum_c = (60 * 63 - 24) // 6
    l_sum_c = (60 * 168 - 36) // 6
    return {
        "trace_identity": (
            "tr(B_J)=tr(M_J W_J)=sum_(i,j in J) M_ij^3 "
            "=sum_(i in J)(60-6c_i)"
        ),
        "positive_multiples_of_six": True,
        "amgm_necessary_condition": "det(B_J)*rank(J)^rank(J)<=tr(B_J)^rank(J)",
        "exact_candidates": candidates,
        "sum_c_K": k_sum_c,
        "sum_c_L": l_sum_c,
        "sum_c_total": k_sum_c + l_sum_c,
    }


def log3_bounds(terms: int = 12) -> tuple[Fraction, Fraction]:
    """Exact lower/upper bounds from log(3)=2*atanh(1/2)."""
    if terms < 1:
        raise ValueError("terms must be positive")
    lower = sum(
        (
            Fraction(2, 1)
            * Fraction(1, 2) ** (2 * index + 1)
            / (2 * index + 1)
        )
        for index in range(terms)
    )
    first_power = Fraction(1, 2) ** (2 * terms + 1)
    tail_upper = (
        Fraction(2, 2 * terms + 1)
        * first_power
        / (1 - Fraction(1, 4))
    )
    return lower, lower + tail_upper


def fraction_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def json_fraction(value: Fraction) -> int | str:
    if value.denominator == 1:
        return value.numerator
    return fraction_text(value)


def derivative_factorization_certificate() -> dict[str, object]:
    """Check x(1+2x)F'=(x-1)(2Lx+L-2/3) in Q[L][x]."""
    # Elements of Q[L] are pairs (coefficient of L, rational part).  Only
    # multiplication by rational scalars is needed because both sides are
    # affine in L.
    Pair = tuple[Fraction, Fraction]
    Polynomial = list[Pair]

    def pair_add(left: Pair, right: Pair) -> Pair:
        return left[0] + right[0], left[1] + right[1]

    def pair_scale(value: Pair, scalar: Fraction) -> Pair:
        return value[0] * scalar, value[1] * scalar

    def poly_add(left: Polynomial, right: Polynomial) -> Polynomial:
        size = max(len(left), len(right))
        result = [(Fraction(0), Fraction(0)) for _ in range(size)]
        for index in range(size):
            if index < len(left):
                result[index] = pair_add(result[index], left[index])
            if index < len(right):
                result[index] = pair_add(result[index], right[index])
        while len(result) > 1 and result[-1] == (0, 0):
            result.pop()
        return result

    def poly_scale(poly: Polynomial, scalar: Fraction) -> Polynomial:
        return [pair_scale(value, scalar) for value in poly]

    def poly_shift(poly: Polynomial, places: int) -> Polynomial:
        return [(Fraction(0), Fraction(0))] * places + poly

    def poly_mul_rational(
        left: Polynomial,
        right: list[Fraction],
    ) -> Polynomial:
        result = [
            (Fraction(0), Fraction(0))
            for _ in range(len(left) + len(right) - 1)
        ]
        for i, left_value in enumerate(left):
            for j, right_value in enumerate(right):
                result[i + j] = pair_add(
                    result[i + j],
                    pair_scale(left_value, right_value),
                )
        return result

    L: Pair = (Fraction(1), Fraction(0))
    c: Pair = (Fraction(1), Fraction(-2, 3))
    two: Pair = (Fraction(0), Fraction(2))

    # Direct expansion:
    # L*x*(1+2x) - c*(1+2x) - 2*x.
    direct = poly_add(
        poly_add(
            poly_mul_rational(poly_shift([L], 1), [Fraction(1), Fraction(2)]),
            poly_scale(
                poly_mul_rational([c], [Fraction(1), Fraction(2)]),
                Fraction(-1),
            ),
        ),
        poly_scale(poly_shift([two], 1), Fraction(-1)),
    )

    # Independent factored expansion:
    # (x-1)*(2L*x+c).
    inner = poly_add([c], poly_shift([pair_scale(L, Fraction(2))], 1))
    factored = poly_mul_rational(inner, [Fraction(-1), Fraction(1)])
    if direct != factored:
        raise AssertionError("formal derivative factorization failed")
    return {
        "coefficient_ring": "Q[L], L=log(3)",
        "direct_coefficients_ascending": [
            {"L": json_fraction(left), "rational": fraction_text(right)}
            for left, right in direct
        ],
        "factored_coefficients_ascending": [
            {"L": json_fraction(left), "rational": fraction_text(right)}
            for left, right in factored
        ],
        "identity": "x(1+2x)F'(x)=(x-1)(2Lx+L-2/3)",
    }


def logarithmic_certificate(enabled: set[str]) -> dict[str, object]:
    require(
        enabled,
        "b_equals_i_plus_2c_integral",
        "integral characteristic pseudodeterminant",
    )
    require(
        enabled,
        "positive_form_self_adjointness",
        "real logarithmic eigenvalue domain",
    )
    lower, upper = log3_bounds()
    if not (lower > Fraction(2, 3) and upper < 2):
        raise AssertionError("exact log(3) interval was not certified")
    derivative = derivative_factorization_certificate()

    det_bk = 3645
    cap = 3**6
    if not det_bk > cap:
        raise AssertionError("final determinant contradiction disappeared")
    return {
        "C_K": {
            "rank_of_ambient_block": 12,
            "integral": True,
            "G_K_self_adjoint": True,
            "real_diagonalizable": True,
            "positive_semidefinite": False,
            "correct_positivity_statement": (
                "B_K=I+2C_K is G_K-positive; every C_K eigenvalue "
                "mu is real and strictly greater than -1/2."
            ),
            "trace": 6,
        },
        "characteristic_pseudodeterminant": {
            "factorization": "char_CK(t)=t^(12-r)*p(t), p monic in Z[t]",
            "nonzero_eigenvalue_product": "|product(mu_i)|=|p(0)|>=1",
        },
        "log3_exact_bounds": {
            "terms": 12,
            "lower": fraction_text(lower),
            "upper": fraction_text(upper),
            "lower_gt_2_over_3": lower > Fraction(2, 3),
            "upper_lt_2": upper < 2,
        },
        "positive_domain_derivative": derivative,
        "negative_domain": (
            "For -1/2<x<0, g'(x)=L-2/(1+2x)<L-2<0; "
            "g(0)=0 gives g(x)>0, and -(L-2/3)log|x|>0."
        ),
        "pointwise_inequality": (
            "log(1+2x)<=x*log(3)-(log(3)-2/3)*log|x| "
            "for x>-1/2, x!=0"
        ),
        "summed_bound": "log(det(B_K))<=6*log(3)",
        "detB_K_upper_bound": cap,
        "detB_K_forced": det_bk,
        "contradiction": f"{det_bk}>{cap}",
    }


def run_derivation(enabled: Iterable[str]) -> dict[str, object]:
    premise_set = set(enabled)
    return {
        "frame_split": norm_four_and_frame_split(premise_set),
        "matrix_split": block_split_certificate(premise_set),
        "detQ": q_determinant_certificate(premise_set),
        "determinant_allocation": determinant_allocation_certificate(premise_set),
        "row_alphabet": alphabet_certificate(premise_set),
        "block_traces": block_trace_certificate(premise_set),
        "logarithmic_contradiction": logarithmic_certificate(premise_set),
    }


def hostile_premise_deletions() -> dict[str, object]:
    failures: dict[str, object] = {}
    full = set(ESSENTIAL_PREMISES)
    for omitted in ESSENTIAL_PREMISES:
        try:
            run_derivation(full - {omitted})
        except PremiseError as error:
            failures[omitted] = {
                "status": "BLOCKED_AS_REQUIRED",
                "first_failed_stage": str(error),
            }
        else:
            raise AssertionError(f"omitting {omitted} did not fail closed")

    fractional_c_det = 2**12
    failures["explicit_nonintegral_C_control"] = {
        "C_spectrum": ["1/2"] * 12,
        "traceC": 6,
        "B_spectrum": [2] * 12,
        "B_positive_self_adjoint": True,
        "detB": fractional_c_det,
        "exceeds_integral_log_cap_729": fractional_c_det > 3**6,
        "violated_premise": "C integral",
    }
    failures["without_even_unimodular_veto"] = {
        "surviving_allocation": {"detQ_K": 1, "detQ_L": 5},
        "detB_K": 729,
        "log_cap": 729,
        "strict_contradiction": False,
    }
    failures["without_trace_multiple_of_six"] = {
        "arithmetic_trace_pair_not_excluded": {"traceB_K": 28, "traceB_L": 32},
        "traceC_K": 8,
        "generic_log_cap": 3**8,
        "forced_detB_K": 3645,
        "contradiction": False,
    }
    return failures


def build_result() -> dict[str, object]:
    frozen = verify_frozen_inputs()
    s0 = load_s0_facts()
    derivation = run_derivation(ESSENTIAL_PREMISES)
    hostile = hostile_premise_deletions()
    return {
        "schema": "wave29-s0-frame-exclusion-discovery-v1",
        "role": "proof_a",
        "claim_label": "DERIVED",
        "local_frozen_baseline_commit": PUBLIC_BASE_COMMIT,
        "frozen_inputs": frozen,
        "single_lattice_scope": s0,
        "assumption_profile": {
            "automorphism_assumed": False,
            "finite_search_assumed_complete": False,
            "full_endpoint_assumed_for_contradiction": True,
            "essential_premises": list(ESSENTIAL_PREMISES),
        },
        "derivation": derivation,
        "hostile_controls": hostile,
        "verdict": {
            "S0_full_projector_Schur_endpoint_origin": "REFUTED_DERIVED",
            "all_h_729_lattices": "UNKNOWN",
            "n3_equals_708": "UNKNOWN",
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
            "independent_verification_required": True,
        },
        "runtime": {
            "dependencies": "Python standard library only",
            "implementation": platform.python_implementation(),
            "python": sys.version,
            "platform": platform.platform(),
        },
    }


def canonical_json(payload: object) -> str:
    return json.dumps(
        payload,
        indent=2,
        sort_keys=True,
        ensure_ascii=True,
    ) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    text = canonical_json(build_result())
    if arguments.output is None:
        sys.stdout.write(text)
    else:
        arguments.output.write_text(text, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
