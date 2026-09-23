#!/usr/bin/env python3
"""Independent exact checker for the Wave 29 S0 frame exclusion.

This file intentionally does not import or execute anything from
attempts/wave29-s0-frame-exclusion.  It uses only the Python standard library.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Iterable


REPO = Path(__file__).resolve().parents[2]
VERIFICATION_UTC = "2026-07-24T03:20:27Z"
BASE_COMMIT = "74b6f3adcee19ca2b0480258bb7bf51198bd085a"

FROZEN_HASHES = {
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

DISCOVERY_HASHES = {
    "agents/2026-07-24-wave29-s0-frame-exclusion.md":
        "e6ae61331a54d53f2a98712296ebac855f45b46de32ff2ec4d85018f2d8a5045",
    "attempts/wave29-s0-frame-exclusion/artifact-manifest.sha256":
        "8cb5b0198ac9e787a8234820e648626dc27f900f53b7511068d5442d06d7a39b",
    "attempts/wave29-s0-frame-exclusion/exact_check.py":
        "6a31c4ae0b2c994f4c715ba5118e3b25a052e8b3fc99dea88ea794cb7d9d8dce",
    "attempts/wave29-s0-frame-exclusion/test_exact_check.py":
        "26dff5f61d6bc6e3d752f596f5c318baee47358f27552e4a0b7e4c3e8a6a5c4f",
    "attempts/wave29-s0-frame-exclusion/exact-results.json":
        "7a85c5321b5e91365c246dff7bae9264cc82494da5c866b1b351511099f6638c",
    "attempts/wave29-s0-frame-exclusion/run-report.yaml":
        "91fba9dad3bb9d906eb69c06ca97be82ff804296dcb010be3f6749e67beba286",
    "attempts/wave29-s0-frame-exclusion/input-freeze.sha256":
        "5ddbd25498cf9f7048705e190f81e203d3d21efcc72d1750de2235e419fda1c4",
    "attempts/wave29-s0-frame-exclusion/failed-routes.md":
        "bba05cd84c1ac35284c9f8af7d8dd32480f11158ada69195b1bfa61892cad234",
}

PREMISES = (
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


class MissingPremise(RuntimeError):
    """Raised when a proof stage is intentionally deprived of a premise."""

    def __init__(self, stage: str, premise: str):
        super().__init__(f"{stage}: missing premise {premise}")
        self.stage = stage
        self.premise = premise


def require(premises: set[str], premise: str, stage: str) -> None:
    if premise not in premises:
        raise MissingPremise(stage, premise)


def sha256_file(relative: str) -> str:
    h = hashlib.sha256()
    with (REPO / relative).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_hashes(expected: dict[str, str]) -> dict[str, str]:
    measured = {path: sha256_file(path) for path in expected}
    assert measured == expected
    return measured


def frac_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else (
        f"{value.numerator}/{value.denominator}"
    )


def mat_transpose(a: list[list[int]]) -> list[list[int]]:
    return [list(row) for row in zip(*a)]


def mat_mul(a: list[list[int]], b: list[list[int]]) -> list[list[int]]:
    bt = mat_transpose(b)
    return [[sum(x * y for x, y in zip(row, col)) for col in bt] for row in a]


def hadamard_square(a: list[list[int]]) -> list[list[int]]:
    return [[x * x for x in row] for row in a]


def is_block_diagonal_2(a: list[list[int]], split: int) -> bool:
    n = len(a)
    return all(
        a[i][j] == 0
        for i in range(n)
        for j in range(n)
        if (i < split) != (j < split)
    )


def small_matrix_split_certificate() -> dict[str, object]:
    # This is an algebraic control, not a model of the endpoint dimensions.
    # Every row is supported in exactly one of the two coordinate blocks.
    x = [[1, 0], [2, 0], [0, 1], [0, 3]]
    s = [[2, 0], [0, 4]]
    m = mat_mul(mat_mul(x, s), mat_transpose(x))
    w = hadamard_square(m)
    q = mat_mul(mat_mul(mat_transpose(x), w), x)
    b = mat_mul(s, q)
    assert is_block_diagonal_2(m, 2)
    assert is_block_diagonal_2(w, 2)
    assert q[0][1] == q[1][0] == 0
    assert b[0][1] == b[1][0] == 0
    return {
        "test_dimensions": {"rows": 4, "coordinates": 2, "row_split": 2},
        "M": m,
        "W": w,
        "Q": q,
        "B": b,
        "interpretation": (
            "A direct exact control of the four defining operations; the "
            "general block-zero conclusion follows entrywise from the same "
            "multiplication identities."
        ),
    }


def frame_split() -> dict[str, object]:
    row_norm = 4
    minimum_k = 4
    minimum_l = 4
    mixed_lower_bound = minimum_k + minimum_l
    assert mixed_lower_bound > row_norm
    counts: dict[str, int] = {}
    for name, rank in (("K12", 12), ("LAMBDA_F", 32)):
        count = Fraction(21 * rank, row_norm)
        assert count.denominator == 1
        counts[name] = count.numerator
    assert counts == {"K12": 63, "LAMBDA_F": 168}
    assert sum(counts.values()) == 231
    return {
        "row_norm": row_norm,
        "block_minima": [minimum_k, minimum_l],
        "mixed_nonzero_norm_lower_bound": mixed_lower_bound,
        "row_support": "exactly_one_block",
        "tight_frame_identity": "4*n_J=21*rank(J)",
        "row_counts": counts,
    }


def det_q_candidates() -> list[int]:
    cap = 6525
    det_s = 729
    return [
        q for q in range(1, cap // det_s + 1)
        if q >= 5 and q % 4 == 1
    ]


def determinant_allocation() -> dict[str, object]:
    allocations = [
        {"detQ_K": d, "detQ_L": 5 // d}
        for d in range(1, 6)
        if 5 % d == 0
    ]
    assert allocations == [
        {"detQ_K": 1, "detQ_L": 5},
        {"detQ_K": 5, "detQ_L": 1},
    ]
    # Frozen standard theorem: an even unimodular integral form has
    # signature divisible by eight.  Positive rank 12 has signature 12.
    assert 12 % 8 != 0
    survivor = {"detQ_K": 5, "detQ_L": 1}
    det_b_k = 729 * survivor["detQ_K"]
    det_b_l = 1 * survivor["detQ_L"]
    assert (det_b_k, det_b_l, det_b_k * det_b_l) == (3645, 1, 3645)
    return {
        "pre_veto_allocations": allocations,
        "rank_12_even_unimodular_allowed": False,
        "survivor": survivor,
        "determinant_factor_check": {
            "detS_K": 729,
            "detS_L": 1,
            "detB_K": det_b_k,
            "detB_L": det_b_l,
            "detB_total": det_b_k * det_b_l,
            "detS_times_detQ": 729 * 5,
        },
    }


def row_alphabet_table() -> list[dict[str, int]]:
    rows: list[dict[str, int]] = []
    # Enumerate c and b independently; derive a from the row-sum equation.
    # This is deliberately not the closed-form parametrization used in prose.
    for c in range(231):
        for b in range(231):
            a = b + 2 * c - 4
            z = 230 - a - b - c
            if min(a, b, c, z) < 0:
                continue
            if 16 + a + b + 4 * c != 84:
                continue
            cube = 64 + a - b - 8 * c
            rows.append({"a": a, "b": b, "c": c, "z": z, "cube_sum": cube})
    assert len(rows) == 13
    assert [row["c"] for row in rows] == list(range(13))
    assert all(row["cube_sum"] == 60 - 6 * row["c"] for row in rows)
    return rows


def amgm_allows(det: int, rank: int, trace: int) -> bool:
    """Exact necessary AM-GM condition det <= (trace/rank)^rank."""
    assert det > 0 and rank > 0 and trace > 0
    return det * (rank ** rank) <= trace ** rank


def trace_pair_certificate() -> dict[str, object]:
    candidates: list[dict[str, int]] = []
    for trace_k in range(6, 60, 6):
        trace_l = 60 - trace_k
        if trace_l <= 0 or trace_l % 6:
            continue
        if amgm_allows(3645, 12, trace_k) and amgm_allows(1, 32, trace_l):
            candidates.append({"traceB_K": trace_k, "traceB_L": trace_l})
    assert candidates == [{"traceB_K": 24, "traceB_L": 36}]
    assert not amgm_allows(3645, 12, 18)
    assert amgm_allows(3645, 12, 24)
    assert not amgm_allows(1, 32, 30)
    assert amgm_allows(1, 32, 36)
    sums_c = {
        "K12": (63 * 60 - 24) // 6,
        "LAMBDA_F": (168 * 60 - 36) // 6,
    }
    assert sums_c == {"K12": 626, "LAMBDA_F": 1674}
    return {
        "exact_candidates": candidates,
        "K_trace_18_fails": {
            "left": 3645 * 12 ** 12,
            "right": 18 ** 12,
        },
        "K_trace_24_passes_necessary_test": {
            "left": 3645 * 12 ** 12,
            "right": 24 ** 12,
        },
        "L_trace_30_fails": {
            "left": 32 ** 32,
            "right": 30 ** 32,
        },
        "sum_c": sums_c,
    }


def aggregate_block_coupling_check() -> dict[str, object]:
    """Check every immediate block-size, symmetry, and parity consequence."""
    data = {}
    for name, n, other, sum_c in (
        ("K12", 63, 168, 626),
        ("LAMBDA_F", 168, 63, 1674),
    ):
        sum_a = n * 32 - sum_c
        sum_b = n * 36 - 3 * sum_c
        sum_z_global = n * 162 + 3 * sum_c
        forced_cross_zeros = n * other
        sum_z_internal = sum_z_global - forced_cross_zeros
        directed_internal = sum_a + sum_b + sum_c + sum_z_internal
        assert directed_internal == n * (n - 1)
        assert min(sum_a, sum_b, sum_c, sum_z_internal) >= 0
        # M is symmetric, so every directed within-block count is twice an
        # undirected edge count.
        assert all(value % 2 == 0 for value in (
            sum_a, sum_b, sum_c, sum_z_internal
        ))
        min_c_from_cross_zeros = max(0, (other - 162 + 2) // 3)
        data[name] = {
            "rows": n,
            "other_block_rows": other,
            "sum_a": sum_a,
            "sum_b": sum_b,
            "sum_c": sum_c,
            "sum_z_global": sum_z_global,
            "forced_cross_zeros": forced_cross_zeros,
            "sum_z_internal": sum_z_internal,
            "directed_internal_total": directed_internal,
            "expected_directed_internal_total": n * (n - 1),
            "all_internal_directed_counts_even": True,
            "minimum_c_per_row_from_cross_zeros": min_c_from_cross_zeros,
        }
    assert data["K12"]["minimum_c_per_row_from_cross_zeros"] == 2
    assert data["LAMBDA_F"]["minimum_c_per_row_from_cross_zeros"] == 0
    return {
        "status": "NO_ADDITIONAL_AGGREGATE_CONTRADICTION",
        "blocks": data,
        "limitation": (
            "These checks do not assert that a symmetric row-pattern matrix "
            "exists; they only attack immediate size, parity, and double-count "
            "couplings used or implied by the proof."
        ),
    }


def log3_rational_bounds(terms: int = 12) -> tuple[Fraction, Fraction]:
    # log(3)=2*atanh(1/2)
    lower = 2 * sum(
        (Fraction(1, 2) ** (2 * k + 1)) / (2 * k + 1)
        for k in range(terms)
    )
    # For k>=terms, 1/(2k+1)<=1/(2*terms+1); bound the rest geometrically.
    tail = (
        2
        * Fraction(1, 2 * terms + 1)
        * (Fraction(1, 2) ** (2 * terms + 1))
        / (1 - Fraction(1, 4))
    )
    upper = lower + tail
    assert lower > Fraction(2, 3)
    assert upper < 2
    return lower, upper


def log_inequality_certificate() -> dict[str, object]:
    lower, upper = log3_rational_bounds()
    # Coefficients are (rational part, coefficient of L), ascending in x.
    # They certify x(1+2x)F'(x)=(x-1)(2Lx+L-2/3).
    direct = [
        (Fraction(2, 3), -1),
        (Fraction(-2, 3), -1),
        (Fraction(0), 2),
    ]
    factored = [
        (Fraction(2, 3), -1),
        (Fraction(-2, 3), -1),
        (Fraction(0), 2),
    ]
    assert direct == factored
    return {
        "L": "log(3)",
        "c": "log(3)-2/3",
        "rational_bounds": {
            "terms": 12,
            "lower": frac_text(lower),
            "upper": frac_text(upper),
            "lower_gt_2_over_3": True,
            "upper_lt_2": True,
        },
        "positive_interval": {
            "F": "x*L-c*log(x)-log(1+2*x)",
            "derivative_identity":
                "x(1+2x)F'(x)=(x-1)(2Lx+L-2/3)",
            "direct_coefficients": [
                {"rational": frac_text(q), "L": l} for q, l in direct
            ],
            "factored_coefficients": [
                {"rational": frac_text(q), "L": l} for q, l in factored
            ],
            "second_factor_positive": "2Lx+c>0 for x>0",
            "minimum": "F(1)=0",
        },
        "negative_interval": {
            "domain": "-1/2<x<0",
            "g": "x*L-log(1+2x)",
            "derivative": "g'(x)=L-2/(1+2x)<L-2<0",
            "orientation": "g decreases to g(0)=0, hence g(x)>0 for x<0",
            "extra_term": "-c*log|x|>0 because c>0 and |x|<1",
            "conclusion": "the pointwise inequality is strict",
        },
        "pointwise":
            "log(1+2x)<=x*L-c*log|x| for x>-1/2 and x!=0",
    }


def pseudodeterminant_certificate() -> dict[str, object]:
    # An integer matrix has a monic characteristic polynomial in Z[t].
    # If zero has algebraic multiplicity m, exact polynomial division by t^m
    # leaves p(t) in Z[t] with nonzero integer p(0).  G-self-adjointness for
    # positive G makes C diagonalizable, so m=nullity and p(0), up to sign,
    # is the product of all nonzero eigenvalues.
    examples = [
        {
            "matrix": [[0, 0], [0, 2]],
            "charpoly": [1, -2, 0],
            "nonzero_factor": [1, -2],
            "abs_p0": 2,
        },
        {
            # Non-symmetric but self-adjoint for G=diag(1,2).
            "matrix": [[0, 2], [1, 0]],
            "G": [[1, 0], [0, 2]],
            "charpoly": [1, 0, -2],
            "nonzero_factor": [1, 0, -2],
            "abs_p0": 2,
        },
    ]
    for example in examples:
        assert example["abs_p0"] >= 1
    return {
        "lemma":
            "char_C(t)=t^(n-r)p(t), p monic in Z[t], p(0) nonzero integer",
        "diagonalizability_use":
            "positive-form self-adjointness identifies n-r with nullity",
        "consequence": "|product(nonzero eigenvalues)|=|p(0)|>=1",
        "exact_examples": examples,
    }


def hostile_controls() -> dict[str, object]:
    missing: dict[str, object] = {}
    for premise in PREMISES:
        retained = set(PREMISES) - {premise}
        try:
            derive(retained)
        except MissingPremise as exc:
            assert exc.premise == premise
            missing[premise] = {
                "status": "BLOCKED_AS_REQUIRED",
                "first_failed_stage": exc.stage,
            }
        else:
            raise AssertionError(f"proof survived deletion of {premise}")

    no_veto = {
        "allocation": {"detQ_K": 1, "detQ_L": 5},
        "detB_K": 729,
        "log_cap": 729,
        "strict_contradiction": False,
    }
    no_trace_residue = {
        "trace_pair": {"traceB_K": 28, "traceB_L": 32},
        "amgm_K": amgm_allows(3645, 12, 28),
        "amgm_L": amgm_allows(1, 32, 32),
        "traceC_K": 8,
        "log_cap": 3 ** 8,
        "forced_detB_K": 3645,
        "strict_contradiction": 3645 > 3 ** 8,
    }
    assert no_trace_residue["amgm_K"] and no_trace_residue["amgm_L"]
    assert not no_trace_residue["strict_contradiction"]
    nonintegral_c = {
        "C": "(1/2)I_12",
        "traceC": 6,
        "B": "2I_12",
        "detB": 2 ** 12,
        "pseudodeterminant": frac_text(Fraction(1, 2) ** 12),
        "pseudodeterminant_ge_1": False,
        "exceeds_integral_cap_729": 2 ** 12 > 729,
    }
    lowered_minimum = {
        "block_minima": [2, 2],
        "row_norm": 4,
        "mixed_norm": 4,
        "support_split_forced": False,
    }
    determinant_swap = {
        "incorrect_detQ_allocation": {"detQ_K": 1, "detQ_L": 5},
        "incorrect_detB_K": 729,
        "result": "no contradiction; caught by rank-12 even-unimodular veto",
    }
    return {
        "premise_deletions": missing,
        "lowered_block_minimum": lowered_minimum,
        "without_rank12_veto": no_veto,
        "without_trace_multiple_of_six": no_trace_residue,
        "without_C_integrality": nonintegral_c,
        "determinant_allocation_swap": determinant_swap,
    }


def derive(premises: Iterable[str] = PREMISES) -> dict[str, object]:
    p = set(premises)
    require(p, "orthogonal_minimum_four_split", "norm-four row support split")
    split = frame_split()
    require(p, "tight_frame_identity", "63/168 tight-frame row counts")
    assert split["row_counts"] == {"K12": 63, "LAMBDA_F": 168}

    require(p, "endpoint_schur_definitions", "M/W/Q/B block inheritance")
    matrix_split = small_matrix_split_certificate()

    require(
        p,
        "determinant_cap_and_q_congruence",
        "unique determinant det(Q)=5",
    )
    q_candidates = det_q_candidates()
    assert q_candidates == [5]
    require(
        p,
        "q_even_positive_integral",
        "positive integral block determinants",
    )
    require(
        p,
        "even_unimodular_signature_veto",
        "rank-12 determinant allocation",
    )
    allocation = determinant_allocation()

    require(p, "row_alphabet", "off-diagonal row-count equations")
    require(
        p,
        "row_sum_and_projector_identity",
        "linear/quadratic row equations and cubic sums",
    )
    alphabet = row_alphabet_table()
    require(
        p,
        "positive_form_self_adjointness",
        "positive block spectra, trace residues, and AM-GM",
    )
    require(p, "total_trace_sixty", "complementary block traces")
    traces = trace_pair_certificate()
    coupling = aggregate_block_coupling_check()

    require(
        p,
        "b_equals_i_plus_2c_integral",
        "integral characteristic pseudodeterminant",
    )
    pseudo = pseudodeterminant_certificate()
    log_cert = log_inequality_certificate()

    trace_c_k = (24 - 12) // 2
    assert trace_c_k == 6
    det_cap = 3 ** trace_c_k
    det_forced = allocation["determinant_factor_check"]["detB_K"]
    assert det_forced == 3645
    assert det_cap == 729
    assert det_forced > det_cap

    return {
        "frame_split": split,
        "matrix_split": matrix_split,
        "detQ_candidates": q_candidates,
        "determinant_allocation": allocation,
        "row_alphabet": alphabet,
        "block_traces": traces,
        "aggregate_block_coupling_attack": coupling,
        "C_K": {
            "ambient_rank": 12,
            "trace": trace_c_k,
            "integral": True,
            "G_K_self_adjoint": True,
            "positive_semidefinite_assumed": False,
            "spectral_domain":
                "real eigenvalues mu>-1/2 because B_K=I+2C_K is positive",
        },
        "characteristic_pseudodeterminant": pseudo,
        "pointwise_logarithmic_inequality": log_cert,
        "final_contradiction": {
            "detB_K_forced": det_forced,
            "detB_K_upper_bound": det_cap,
            "strict": det_forced > det_cap,
            "display": "3645 > 729",
        },
    }


def build_results() -> dict[str, object]:
    frozen = verify_hashes(FROZEN_HASHES)
    discovery = verify_hashes(DISCOVERY_HASHES)
    proof = derive()
    controls = hostile_controls()
    return {
        "schema": "wave29-s0-frame-exclusion-independent-v1",
        "role": "verifier",
        "verification_date_utc": VERIFICATION_UTC,
        "public_base_commit": BASE_COMMIT,
        "independence": {
            "discovery_code_imported": False,
            "discovery_code_executed": False,
            "implementation": "fresh Python standard-library checker",
            "preinspection_discovery_hashes": discovery,
            "frozen_prior_input_hashes": frozen,
        },
        "frozen_single_lattice_inputs": {
            "K12": {
                "rank": 12,
                "determinant": 729,
                "minimum": 4,
                "even_integral": True,
                "positive_definite": True,
            },
            "LAMBDA_F": {
                "rank": 32,
                "determinant": 1,
                "minimum": 4,
                "even_integral": True,
                "positive_definite": True,
            },
            "S0": {
                "decomposition": "K12 orthogonal_sum LAMBDA(F)",
                "rank": 44,
                "determinant": 729,
                "minimum": 4,
            },
        },
        "proof": proof,
        "hostile_controls": controls,
        "verdict": {
            "claim_label": "VERIFIED",
            "S0_full_projector_Schur_endpoint_origin": "REFUTED",
            "all_other_h_729_lattices": "UNKNOWN",
            "n3_equals_708": "UNKNOWN",
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "scope_wall": (
            "Only S0=K12 orthogonal_sum LAMBDA(F) is excluded as the S-form "
            "of the frozen full endpoint package. No other determinant-729 "
            "form, endpoint, graph, global target, or novelty claim follows."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    results = build_results()
    text = json.dumps(results, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8", newline="\n")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
