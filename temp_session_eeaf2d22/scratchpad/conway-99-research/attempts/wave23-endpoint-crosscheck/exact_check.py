#!/usr/bin/env python3
"""Exact arithmetic checker for the independent n3=705 endpoint exclusion.

The mathematical input is the audited Wave-20 Schur-projector construction
and the audited Wave-21 projection-lattice package.  This checker does not
instantiate a Conway graph.  It checks the finite arithmetic synthesis:

* the scaled dual S=21G^{-1} is an even integral rank-44 matrix of determinant h;
* det(B)=h det(Q), with Q even positive definite and det(Q)>=5;
* B=I+2C, rank(B)=44 and tr(B)=48 force tr(B^2)>=60;
* Maclaurin's inequality then gives det(B)<43;
* the remaining 3,7-smooth index possibilities are empty.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent

FROZEN_INPUTS = {
    "verification/2026-07-23-wave20-global-schur-audit.md": {
        "sha256": "6311a893e1802382bfaaf00f8d366ba7f25ff036cda8032978dc5c6b4fdf35a3",
        "bytes": 16979,
    },
    "attempts/wave20-global-obstruction/independent-verifier/independent-results.json": {
        "sha256": "575939f9abe19e5578a2efd1155495877c2080944c75cc0db6702c21a9ce2637",
        "bytes": 7498,
    },
    "verification/wave21-lattice-extension/2026-07-23T184926Z-audit.md": {
        "sha256": "45814560f1d5bffb3b00144022a3a1f8d069e71dfe430247a1871822ac08f268",
        "bytes": 13482,
    },
    "verification/wave21-lattice-extension/independent-results.json": {
        "sha256": "735ff677e7837f14ec2a52cbccd827d30abc5eee68ee5e4f8e2bd6a9e5bd21b1",
        "bytes": 4116,
    },
    "verification/wave21-lattice-extension/theorem-sources.md": {
        "sha256": "7f70a36ad124a94d983771274cb7b925a4f2560d835b0f607563045110107f8f",
        "bytes": 2198,
    },
}

RANK = 44
N3_ENDPOINT = 705
DELTA = 12
TRACE_B = 48
SCALE = 21


class CheckError(AssertionError):
    """A frozen premise or exact endpoint obligation failed."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def check_frozen_inputs() -> dict[str, dict[str, Any]]:
    checked: dict[str, dict[str, Any]] = {}
    for relative, expected in FROZEN_INPUTS.items():
        path = ROOT / relative
        actual_hash = sha256_file(path)
        actual_bytes = path.stat().st_size
        if actual_hash != expected["sha256"] or actual_bytes != expected["bytes"]:
            raise CheckError(
                f"frozen input drift for {relative}: "
                f"{actual_hash}/{actual_bytes} != "
                f"{expected['sha256']}/{expected['bytes']}"
            )
        checked[relative] = {
            "sha256": actual_hash,
            "bytes": actual_bytes,
            "status": "PASS",
        }

    wave20 = json.loads(
        (
            ROOT
            / "attempts/wave20-global-obstruction/independent-verifier/"
            "independent-results.json"
        ).read_text(encoding="utf-8")
    )
    wave21 = json.loads(
        (
            ROOT / "verification/wave21-lattice-extension/independent-results.json"
        ).read_text(encoding="utf-8")
    )
    if wave20["summary"]["conditional_n3_lower_bound"] != 705:
        raise CheckError("Wave-20 frozen lower endpoint is not 705")
    if wave20["summary"]["conway_99"] != "UNKNOWN":
        raise CheckError("Wave-20 target boundary drifted")
    if wave21["endpoint"] != {
        "am_gm_exact": {
            "denominator": 6626407607736641103900260617069258125403649041,
            "numerator": 304771832334069766392840191887919236168953102336,
        },
        "delta": 12,
        "determinant_cap": 45,
        "n3": 705,
        "trace_B": 48,
    }:
        raise CheckError("Wave-21 endpoint record drifted")
    if wave21["additional_even_determinant_congruence"]["possible_h"] != [1, 9]:
        raise CheckError("Wave-21 audited endpoint h-list drifted")
    if wave21["additional_even_determinant_congruence"]["det_Q_mod_4"] != 1:
        raise CheckError("Wave-21 det(Q) residue drifted")
    return checked


def even_odd_determinant_residue(rank: int) -> int:
    """Residue mod 4 of an odd determinant of an even rank-rank Gram matrix."""

    if rank <= 0 or rank % 2:
        raise CheckError("even-determinant congruence requires positive even rank")
    return 1 if (rank // 2) % 2 == 0 else 3


def determinant_bareiss(matrix: Iterable[Iterable[int]]) -> int:
    """Exact determinant for small hostile-test matrices."""

    work = [list(row) for row in matrix]
    size = len(work)
    if any(len(row) != size for row in work):
        raise CheckError("determinant requires a square matrix")
    if size == 0:
        return 1
    sign = 1
    previous = 1
    for pivot_index in range(size - 1):
        pivot_row = next(
            (
                row
                for row in range(pivot_index, size)
                if work[row][pivot_index] != 0
            ),
            None,
        )
        if pivot_row is None:
            return 0
        if pivot_row != pivot_index:
            work[pivot_index], work[pivot_row] = (
                work[pivot_row],
                work[pivot_index],
            )
            sign *= -1
        pivot = work[pivot_index][pivot_index]
        for row in range(pivot_index + 1, size):
            for column in range(pivot_index + 1, size):
                numerator = (
                    work[row][column] * pivot
                    - work[row][pivot_index] * work[pivot_index][column]
                )
                if numerator % previous:
                    raise CheckError("Bareiss exact division failed")
                work[row][column] = numerator // previous
        previous = pivot
    return sign * work[-1][-1]


def scaled_dual_facts(rank: int = RANK, scale: int = SCALE) -> dict[str, Any]:
    """Finite consequences of S=scale*G^{-1} from the audited lattice bridge."""

    if rank != 44:
        raise CheckError("the frozen projection lattice has rank 44")
    if scale != 21 or scale % 2 == 0:
        raise CheckError("the frozen projector scale is the odd integer 21")

    # The prose proof of evenness is recorded in the report.  Computationally
    # we freeze its finite consequences: S is integral, symmetric, positive
    # definite, even, and det(S)=h.  Rank 44 gives determinant 1 mod 4.
    residue = even_odd_determinant_residue(rank)
    if residue != 1:
        raise CheckError("rank-44 scaled dual should have determinant 1 mod 4")
    signature_mod_8 = rank % 8
    if signature_mod_8 == 0:
        raise CheckError("rank 44 must obstruct an even unimodular lattice")
    return {
        "matrix": "S=21*G^{-1}",
        "integral": True,
        "even": True,
        "positive_definite": True,
        "determinant": "h",
        "determinant_mod_4": residue,
        "h_equals_1_status": "IMPOSSIBLE_EVEN_UNIMODULAR_SIGNATURE_44",
        "signature_mod_8": signature_mod_8,
    }


def trace_square_floor(rank: int = RANK, trace: int = TRACE_B) -> dict[str, Any]:
    """Use B=I+2C and Cauchy to find the exact first possible tr(B^2)."""

    if rank <= 0:
        raise CheckError("rank must be positive")
    if (trace - rank) % 2:
        raise CheckError("B congruent I mod 2 requires trace(B)-rank even")
    trace_c = (trace - rank) // 2

    # tr(C^2) == tr(C) mod 2 for every integral C: off-diagonal products
    # occur in pairs, and x^2 == x mod 2 on the diagonal.
    trace_c2_residue = trace_c % 2
    trace_b2_residue = (
        rank + 4 * trace_c + 4 * trace_c2_residue
    ) % 8
    cauchy_lower = Fraction(trace * trace, rank)
    candidate = math.ceil(cauchy_lower)
    while candidate % 8 != trace_b2_residue:
        candidate += 1

    if (rank, trace, trace_c, trace_b2_residue, candidate) != (44, 48, 2, 4, 60):
        raise CheckError("endpoint trace-square arithmetic drifted")
    return {
        "rank": rank,
        "trace_B": trace,
        "trace_C": trace_c,
        "trace_C2_mod_2": trace_c2_residue,
        "trace_B2_mod_8": trace_b2_residue,
        "cauchy_lower": {
            "numerator": cauchy_lower.numerator,
            "denominator": cauchy_lower.denominator,
        },
        "minimum_trace_B2": candidate,
        "minimum_trace_A4_squared": SCALE * SCALE * candidate,
    }


def maclaurin_bound(
    rank: int = RANK,
    trace: int = TRACE_B,
    trace_square_lower: int = 60,
    *,
    require_endpoint_values: bool = True,
) -> dict[str, Any]:
    """Apply the k=2 versus k=rank Maclaurin inequality exactly."""

    if rank <= 0 or rank % 2:
        raise CheckError("this exact exponent calculation requires positive even rank")
    e2_max = Fraction(trace * trace - trace_square_lower, 2)
    pair_count = math.comb(rank, 2)
    normalized_e2 = e2_max / pair_count
    determinant_bound = normalized_e2 ** (rank // 2)
    integer_cap = determinant_bound.numerator // determinant_bound.denominator

    next_integer = integer_cap + 1
    exact_gap = (
        next_integer * determinant_bound.denominator
        - determinant_bound.numerator
    )
    if exact_gap <= 0 or not determinant_bound < next_integer:
        raise CheckError("failed exact comparison with the next integer")
    if require_endpoint_values:
        if e2_max != 1122:
            raise CheckError("e2 endpoint bound is not 1122")
        if normalized_e2 != Fraction(51, 43):
            raise CheckError("normalized e2 is not 51/43")
        if 43**23 - 51**22 <= 0 or not determinant_bound < 43:
            raise CheckError("failed exact comparison (51/43)^22 < 43")
        if integer_cap != 42:
            raise CheckError("Maclaurin integer determinant cap is not 42")

    return {
        "newton_identity": "e2=(trace(B)^2-trace(B^2))/2",
        "e2_upper": e2_max.numerator,
        "pair_count": pair_count,
        "normalized_e2": {
            "numerator": normalized_e2.numerator,
            "denominator": normalized_e2.denominator,
        },
        "maclaurin_form": (
            "det(B)^(1/22) <= e2/C(44,2)"
            + (" = 51/43" if normalized_e2 == Fraction(51, 43) else "")
        ),
        "determinant_bound": {
            "numerator": determinant_bound.numerator,
            "denominator": determinant_bound.denominator,
        },
        "exact_comparison": {
            "statement": (
                "51^22 < 43^23"
                if normalized_e2 == Fraction(51, 43)
                else "determinant bound is below its next integer"
            ),
            "left": determinant_bound.numerator,
            "right": next_integer * determinant_bound.denominator,
            "gap": exact_gap,
        },
        "strict_upper": next_integer,
        "integer_cap": integer_cap,
    }


def smooth_numbers_at_most(limit: int, primes: Iterable[int] = (3, 7)) -> list[int]:
    values = {1}
    for prime in primes:
        if prime <= 1:
            raise CheckError("smoothness primes must exceed one")
        expanded = set()
        for value in values:
            power = 1
            while value * power <= limit:
                expanded.add(value * power)
                power *= prime
        values = expanded
    return sorted(value for value in values if value <= limit)


def factor_pairs(
    det_b_cap: int,
    det_q_minimum: int,
    *,
    require_h_mod_4_one: bool,
    exclude_h_one: bool,
    require_det_q_mod_4_one: bool,
    primes: Iterable[int] = (3, 7),
) -> list[dict[str, int]]:
    h_values = smooth_numbers_at_most(det_b_cap // det_q_minimum, primes)
    if require_h_mod_4_one:
        h_values = [h for h in h_values if h % 4 == 1]
    if exclude_h_one:
        h_values = [h for h in h_values if h != 1]

    pairs: list[dict[str, int]] = []
    for h in h_values:
        for det_q in range(det_q_minimum, det_b_cap // h + 1):
            if require_det_q_mod_4_one and det_q % 4 != 1:
                continue
            pairs.append({"h": h, "det_Q": det_q, "det_B": h * det_q})
    return pairs


def endpoint_factorization(maclaurin: dict[str, Any]) -> dict[str, Any]:
    det_b_cap = maclaurin["integer_cap"]
    det_q_minimum = 5

    if even_odd_determinant_residue(RANK) != 1:
        raise CheckError("det(Q) residue should be 1 mod 4")
    # det(Q)=1 would be an even positive-definite unimodular lattice of
    # signature 44, forbidden by the frozen van der Blij premise.
    if RANK % 8 == 0:
        raise CheckError("rank 44 signature obstruction disappeared")

    candidates_before_scaled_dual_obstruction = factor_pairs(
        det_b_cap,
        det_q_minimum,
        require_h_mod_4_one=True,
        exclude_h_one=False,
        require_det_q_mod_4_one=True,
    )
    candidates_after_all_constraints = factor_pairs(
        det_b_cap,
        det_q_minimum,
        require_h_mod_4_one=True,
        exclude_h_one=True,
        require_det_q_mod_4_one=True,
    )
    if {pair["h"] for pair in candidates_before_scaled_dual_obstruction} != {1}:
        raise CheckError("unexpected index survived before excluding h=1")
    if candidates_after_all_constraints:
        raise CheckError("an endpoint determinant/index pair survived")

    return {
        "det_B_factorization": "det(B)=h*det(Q)",
        "det_Q_even_rank": RANK,
        "det_Q_mod_4": 1,
        "det_Q_equals_1": "IMPOSSIBLE_SIGNATURE_44",
        "det_Q_minimum": det_q_minimum,
        "det_B_cap": det_b_cap,
        "h_upper": det_b_cap // det_q_minimum,
        "h_is_3_7_smooth": True,
        "h_mod_4": 1,
        "h_equals_1": "IMPOSSIBLE_SCALED_DUAL_SIGNATURE_44",
        "pairs_before_h1_obstruction": candidates_before_scaled_dual_obstruction,
        "pairs_after_all_constraints": candidates_after_all_constraints,
    }


def relaxed_route_ledger() -> dict[str, Any]:
    """Show that each strengthened bridge matters to the finite conclusion."""

    # If the B=I mod 2 trace-square congruence is omitted, Cauchy plus parity
    # permits t=54.  Maclaurin then only recovers the old integer cap 45,
    # leaving the h=9, det(Q)=5 endpoint.
    without_mod8 = maclaurin_bound(
        trace_square_lower=54,
        require_endpoint_values=False,
    )
    mod8_omitted_pairs = factor_pairs(
        without_mod8["integer_cap"],
        5,
        require_h_mod_4_one=True,
        exclude_h_one=True,
        require_det_q_mod_4_one=True,
    )
    if {"h": 9, "det_Q": 5, "det_B": 45} not in mod8_omitted_pairs:
        raise CheckError("hostile omission of trace-square mod 8 did not survive")

    # If the signature obstruction det(Q)!=1 is omitted while the mod-four
    # residues remain active, h=9 and det(Q)=1 give the compatible
    # determinant det(B)=9 under the new cap.
    q_signature_omitted_pairs = factor_pairs(
        42,
        1,
        require_h_mod_4_one=True,
        exclude_h_one=True,
        require_det_q_mod_4_one=True,
    )
    if {"h": 9, "det_Q": 1, "det_B": 9} not in q_signature_omitted_pairs:
        raise CheckError("hostile det(Q)=1 signature omission did not survive")

    # If h were not constrained to be 3,7-smooth, h=5 and det(Q)=5 would
    # survive.  This pair is deliberately outside factor_pairs' prime gate.
    nonsmooth_pair = {"h": 5, "det_Q": 5, "det_B": 25}
    if nonsmooth_pair["det_B"] > 42:
        raise CheckError("hostile nonsmooth index pair should fit the cap")

    # If the scaled-dual signature obstruction is omitted, h=1 has many
    # factor pairs under the new cap.
    h1_omitted_pairs = factor_pairs(
        42,
        5,
        require_h_mod_4_one=True,
        exclude_h_one=False,
        require_det_q_mod_4_one=True,
    )
    if not any(pair["h"] == 1 for pair in h1_omitted_pairs):
        raise CheckError("hostile h=1 omission did not leave survivors")

    return {
        "omit_trace_B2_mod_8": {
            "minimum_trace_B2": 54,
            "det_B_cap": without_mod8["integer_cap"],
            "survivor": {"h": 9, "det_Q": 5, "det_B": 45},
            "status": "ENDPOINT_NOT_EXCLUDED",
        },
        "omit_det_Q_one_signature_obstruction": {
            "retained_residues": {
                "det_B_mod_4": 1,
                "det_Q_mod_4": 1,
                "h_mod_4": 1,
            },
            "survivor": {"h": 9, "det_Q": 1, "det_B": 9},
            "status": "ENDPOINT_NOT_EXCLUDED",
        },
        "omit_3_7_smoothness": {
            "survivor": nonsmooth_pair,
            "status": "ENDPOINT_NOT_EXCLUDED",
        },
        "omit_scaled_dual_h1_obstruction": {
            "survivor_count": sum(pair["h"] == 1 for pair in h1_omitted_pairs),
            "status": "ENDPOINT_NOT_EXCLUDED",
        },
    }


def build_results() -> dict[str, Any]:
    frozen = check_frozen_inputs()
    scaled_dual = scaled_dual_facts()
    trace_square = trace_square_floor()
    maclaurin = maclaurin_bound(
        trace_square_lower=trace_square["minimum_trace_B2"]
    )
    factorization = endpoint_factorization(maclaurin)
    relaxed = relaxed_route_ledger()

    next_n3 = N3_ENDPOINT + 3
    return {
        "claim_label": "DERIVED_PENDING_INDEPENDENT_VERIFIER",
        "scope": (
            "Conditional exclusion of n3=705 for a putative "
            "srg(99,14,1,2), using only the audited Wave-20 global-Schur "
            "and Wave-21 projection-lattice premises."
        ),
        "frozen_inputs": frozen,
        "endpoint": {
            "n3": N3_ENDPOINT,
            "delta": DELTA,
            "rank_B": RANK,
            "trace_B": TRACE_B,
            "trace_A4": SCALE * TRACE_B,
        },
        "scaled_dual": scaled_dual,
        "trace_square": trace_square,
        "maclaurin": maclaurin,
        "determinant_index": factorization,
        "hostile_relaxations": relaxed,
        "modular_rank_boundary": {
            "B_mod_2": "identity on L/2L",
            "rank_F2_B": 44,
            "A4_mod_2": "M",
            "rank_F2_A4": 44,
            "odd_determinant_B": True,
            "claim_at_primes_3_5_7": "NONE_FROM_FROZEN_RANK_DATA",
        },
        "conclusion": {
            "n3_705": "EXCLUDED_CONDITIONALLY_ON_AUDITED_PREMISES",
            "conditional_n3_lower_bound": next_n3,
            "conditional_induced_C6_lower_bound": 209286 + next_n3,
            "target_status": "UNKNOWN",
            "graph_construction": False,
            "novelty": "NOT_ASSESSED",
        },
    }


def write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=HERE / "exact-results.json",
    )
    arguments = parser.parse_args()
    results = build_results()
    write_json(arguments.output, results)
    print(json.dumps(results, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
