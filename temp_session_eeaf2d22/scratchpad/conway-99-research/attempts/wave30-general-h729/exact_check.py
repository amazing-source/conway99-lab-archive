#!/usr/bin/env python3
"""Exact companion for the Wave 30 decomposable h=729 reduction.

This standard-library-only checker audits finite integer implications in a
conditional theorem.  It does not enumerate lattices, frames, graphs, or
orthogonal decompositions.  In particular, the single surviving decomposition
type is not asserted to be realizable.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[2]
PUBLIC_BASE_COMMIT = "4c4d2cb8dec14c7834984d47a7e5b29991891e60"

FROZEN_INPUTS = {
    "agents/2026-07-24-wave28-orchestrator-brief.md":
        "6a15446551b78822706a8e005bef49a411b904cf05f9459b6b3350239839ee1e",
    "verification/wave24-n3-708-index/2026-07-23T204222Z-audit.md":
        "958b9b2d13d697c281ba490d21b170f453d059bfaa952f8e92a9709b6c8d3cd8",
    "verification/wave25-n3-708-strictness/2026-07-23T215549Z-audit.md":
        "642255098bf424654e1a3a8c926a924ae8bf068cd422f0f367f64f9e402648de",
    "agents/2026-07-24-wave29-s0-frame-exclusion.md":
        "e6ae61331a54d53f2a98712296ebac855f45b46de32ff2ec4d85018f2d8a5045",
    "verification/wave29-s0-frame-exclusion/audit.md":
        "dbdcb88bf309cbfa47a42b9fb63dd7cf483e07cac8b92c475094c96be3723b7d",
}

RANK = 44
ROWS = 231
FRAME_SCALE = 21
ROW_NORM = 4
TRACE_B = 60
DET_S = 729
DET_B_CAP = 6525

ESSENTIAL_PREMISES = (
    "rootless_integral_orthogonal_decomposition",
    "tight_frame_identity",
    "schur_block_inheritance",
    "endpoint_detq_constraints",
    "even_positive_block_forms",
    "even_unimodular_signature_veto",
    "row_alphabet_trace_residue",
    "b_equals_i_plus_2c_integral",
    "positive_form_self_adjointness",
    "characteristic_pseudodeterminant",
    "equality_integral_split",
)


class PremiseError(ValueError):
    """Raised when a hostile premise deletion blocks the derivation."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_frozen_inputs() -> dict[str, str]:
    observed: dict[str, str] = {}
    for relative, expected in FROZEN_INPUTS.items():
        actual = sha256_file(REPO_ROOT / relative)
        if actual != expected:
            raise AssertionError(
                f"frozen input drift for {relative}: {actual} != {expected}"
            )
        observed[relative] = actual
    return observed


def require(enabled: set[str], premise: str, stage: str) -> None:
    if premise not in enabled:
        raise PremiseError(f"{stage}: missing premise {premise}")


def even_odd_determinant_residue(rank: int) -> int:
    """Return the mod-four determinant residue of an even odd-det form.

    The standard congruence is det(H)=(-1)^(rank/2) modulo four.  Odd rank is
    impossible because an alternating matrix of odd size is singular mod two.
    """

    if rank % 2:
        raise ValueError("an even Gram matrix of odd rank has even determinant")
    return 1 if (rank // 2) % 2 == 0 else 3


def unique_endpoint_detq() -> list[int]:
    """Enumerate det(Q) from the exact h=729 endpoint constraints."""

    return [
        q
        for q in range(1, DET_B_CAP // DET_S + 1)
        if q >= 5 and q % 4 == 1
    ]


def frame_row_count(rank: int) -> int:
    numerator = FRAME_SCALE * rank
    if numerator % ROW_NORM:
        raise ValueError("4*n_J=21*rank(J) does not give an integer")
    return numerator // ROW_NORM


def row_alphabet_solutions() -> list[dict[str, int]]:
    """Exhaust the per-row +1,-1,-2,0 endpoint alphabet."""

    solutions: list[dict[str, int]] = []
    for c in range(ROWS):
        a = 32 - c
        b = 36 - 3 * c
        z = 162 + 3 * c
        if min(a, b, c, z) < 0:
            continue
        if a + b + c + z != ROWS - 1:
            continue
        if ROW_NORM + a - b - 2 * c != 0:
            continue
        if ROW_NORM**2 + a + b + 4 * c != FRAME_SCALE * ROW_NORM:
            continue
        solutions.append(
            {
                "a_plus_one": a,
                "b_minus_one": b,
                "c_minus_two": c,
                "z_zero": z,
                "cubic_row_sum": 60 - 6 * c,
            }
        )
    return solutions


def exceptional_block_types() -> list[tuple[int, int]]:
    """Return possible (rank(A), v3(det(S_A))) before trace inequalities.

    All Q-unimodular components have ranks divisible by eight.  The unique
    det(Q)=5 component A therefore has rank 4 mod 8.  Its even odd-determinant
    form has determinant 1 mod 4, so the exponent is even.  Exponent zero is
    prohibited by the even-unimodular signature theorem at rank 4 mod 8.
    """

    ranks = [rank for rank in range(1, RANK) if rank % 8 == 4]
    exponents = [
        exponent
        for exponent in range(0, 7)
        if pow(3, exponent, 4) == 1 and exponent != 0
    ]
    return [(rank, exponent) for rank in ranks for exponent in exponents]


def amgm_allows(rank: int, trace: int, determinant: int) -> bool:
    if rank <= 0 or trace <= 0 or determinant <= 0:
        return False
    return trace**rank >= determinant * rank**rank


def trace_pairs(rank_a: int, exponent_a: int) -> list[tuple[int, int]]:
    rank_r = RANK - rank_a
    det_b_a = 5 * 3**exponent_a
    det_b_r = 3 ** (6 - exponent_a)
    pairs: list[tuple[int, int]] = []
    for trace_a in range(6, TRACE_B, 6):
        trace_r = TRACE_B - trace_a
        if not amgm_allows(rank_a, trace_a, det_b_a):
            continue
        if not amgm_allows(rank_r, trace_r, det_b_r):
            continue
        pairs.append((trace_a, trace_r))
    return pairs


def logarithmic_cap(rank: int, trace_b: int) -> tuple[int, int]:
    """Return (tr(C), 3^tr(C)) for B=I+2C on one block."""

    difference = trace_b - rank
    if difference % 2:
        raise AssertionError("block trace parity is incompatible with B=I+2C")
    trace_c = difference // 2
    if trace_c < 0:
        raise AssertionError("positive determinant cannot use a negative cap")
    return trace_c, 3**trace_c


def classify_type(rank_a: int, exponent_a: int) -> dict[str, object]:
    rank_r = RANK - rank_a
    det_s_a = 3**exponent_a
    det_s_r = 3 ** (6 - exponent_a)
    det_b_a = 5 * det_s_a
    det_b_r = det_s_r
    pairs = trace_pairs(rank_a, exponent_a)

    result: dict[str, object] = {
        "rank_A": rank_a,
        "rank_R": rank_r,
        "v3_detS_A": exponent_a,
        "detS_A": det_s_a,
        "detS_R": det_s_r,
        "detQ_A": 5,
        "detQ_R": 1,
        "detB_A": det_b_a,
        "detB_R": det_b_r,
        "amgm_trace_pairs": [
            {"traceB_A": left, "traceB_R": right}
            for left, right in pairs
        ],
    }

    if not pairs:
        result.update(
            {
                "status": "EXCLUDED",
                "first_obstruction": "blockwise_AM_GM_and_trace_residue",
            }
        )
        return result

    if len(pairs) != 1:
        raise AssertionError(f"expected a unique trace pair, got {pairs!r}")
    trace_a, trace_r = pairs[0]
    trace_c_a, cap_a = logarithmic_cap(rank_a, trace_a)
    trace_c_r, cap_r = logarithmic_cap(rank_r, trace_r)
    result.update(
        {
            "traceC_A": trace_c_a,
            "traceC_R": trace_c_r,
            "log_cap_A": cap_a,
            "log_cap_R": cap_r,
        }
    )

    if det_b_a > cap_a:
        result.update(
            {
                "status": "EXCLUDED",
                "first_obstruction": "exceptional_block_logarithmic_cap",
            }
        )
        return result
    if det_b_r > cap_r:
        result.update(
            {
                "status": "EXCLUDED",
                "first_obstruction": "complement_block_logarithmic_cap",
            }
        )
        return result

    if det_b_r == cap_r:
        image_rank = trace_c_r
        kernel_rank = rank_r - image_rank
        result["complement_log_equality"] = {
            "C_R_idempotent": True,
            "image_rank": image_rank,
            "kernel_rank": kernel_rank,
            "Q_image_even_unimodular": image_rank > 0,
            "Q_kernel_even_unimodular": kernel_rank > 0,
            "both_ranks_divisible_by_8": (
                image_rank % 8 == 0 and kernel_rank % 8 == 0
            ),
        }
        if image_rank % 8 or kernel_rank % 8:
            result.update(
                {
                    "status": "EXCLUDED",
                    "first_obstruction":
                        "log_equality_integral_split_signature_veto",
                }
            )
            return result

    result.update(
        {
            "status": "SURVIVES_THIS_REDUCTION",
            "first_obstruction": None,
        }
    )
    return result


def decomposition_census() -> list[dict[str, object]]:
    return [
        classify_type(rank, exponent)
        for rank, exponent in exceptional_block_types()
    ]


def surviving_boundary() -> dict[str, object]:
    survivors = [
        item
        for item in decomposition_census()
        if item["status"] == "SURVIVES_THIS_REDUCTION"
    ]
    if len(survivors) != 1:
        raise AssertionError(f"expected one surviving type, got {survivors!r}")
    survivor = survivors[0]
    if (survivor["rank_A"], survivor["v3_detS_A"]) != (20, 6):
        raise AssertionError("surviving decomposition type drifted")

    rank_a = int(survivor["rank_A"])
    rank_r = int(survivor["rank_R"])
    rows_a = frame_row_count(rank_a)
    rows_r = frame_row_count(rank_r)

    allowed_c = [
        item["c_minus_two"]
        for item in row_alphabet_solutions()
        if abs(item["cubic_row_sum"]) <= 8
    ]
    profiles = [
        {
            "n_c9": n11 + 4,
            "n_c10": 122 - 2 * n11,
            "n_c11": n11,
        }
        for n11 in range(62)
    ]
    for profile in profiles:
        if sum(profile.values()) != rows_r:
            raise AssertionError("R-row profile has wrong cardinality")
        weighted = (
            9 * profile["n_c9"]
            + 10 * profile["n_c10"]
            + 11 * profile["n_c11"]
        )
        if weighted != 1256:
            raise AssertionError("R-row profile has wrong c sum")

    scalar_c_spectrum = {0: 13, 1: 6, 2: 1}
    scalar_b_spectrum = {1 + 2 * key: value for key, value in scalar_c_spectrum.items()}
    scalar_trace_c = sum(key * value for key, value in scalar_c_spectrum.items())
    scalar_trace_c2 = sum(
        key * key * value for key, value in scalar_c_spectrum.items()
    )
    scalar_trace_b = sum(
        key * value for key, value in scalar_b_spectrum.items()
    )
    scalar_det_b = 1
    for key, value in scalar_b_spectrum.items():
        scalar_det_b *= key**value

    return {
        "decomposition": {
            "S": "A_20 orthogonal_sum U_24",
            "A_20": {
                "rank": rank_a,
                "determinant": 729,
                "minimum_at_least": 4,
            },
            "U_24": {
                "rank": rank_r,
                "determinant": 1,
                "even_unimodular": True,
                "minimum_at_least": 4,
                "classification_as_Leech_used": False,
            },
        },
        "frame": {
            "A_rows": rows_a,
            "U_rows": rows_r,
            "total_rows": rows_a + rows_r,
        },
        "schur_blocks": {
            "A": {
                "detQ": 5,
                "detB": 3645,
                "traceB": 36,
                "traceC": 8,
            },
            "U": {
                "detQ": 1,
                "detB": 1,
                "traceB": 24,
                "traceC": 0,
                "B_equals_identity": True,
                "C_equals_zero": True,
            },
        },
        "U_tensor_isometry": {
            "definition":
                "Phi(v)=sum_i <v,y_i>*(y_i tensor y_i) on the 126 U rows",
            "identity": "Phi^* Phi=I_24",
            "row_norm_squared": 4,
            "Phi_row_norm_squared": 4,
            "rank_one_tensor_norm": 4,
            "cauchy_absolute_cubic_bound": 8,
            "allowed_c_minus_two_counts": allowed_c,
            "sum_c_over_U_rows": 1256,
            "profile_count": len(profiles),
            "profile_endpoints": [profiles[0], profiles[-1]],
            "aggregate_internal_directed_counts": {
                "plus_one": rows_r * 32 - 1256,
                "minus_one": rows_r * 36 - 3 * 1256,
                "minus_two": 1256,
                "zero": rows_r * (rows_r - 1)
                    - (rows_r * 32 - 1256)
                    - (rows_r * 36 - 3 * 1256)
                    - 1256,
            },
            "conclusion": "necessary counts only; no M or frame is constructed",
        },
        "scalar_spectral_control": {
            "scope": "B_A/C_A scalar spectrum only; no lattice realization",
            "C_A_multiplicities": {
                str(key): value for key, value in scalar_c_spectrum.items()
            },
            "B_A_multiplicities": {
                str(key): value for key, value in scalar_b_spectrum.items()
            },
            "traceC_A": scalar_trace_c,
            "traceC_A_squared": scalar_trace_c2,
            "traceB_A": scalar_trace_b,
            "detB_A": scalar_det_b,
        },
    }


def hostile_controls() -> dict[str, object]:
    census = decomposition_census()
    exceptional_only = [
        [int(item["rank_A"]), int(item["v3_detS_A"])]
        for item in census
        if item.get("log_cap_A", -1) >= item["detB_A"]
    ]
    before_equality_veto = [
        [int(item["rank_A"]), int(item["v3_detS_A"])]
        for item in census
        if item.get("log_cap_A", -1) >= item["detB_A"]
        and item.get("log_cap_R", -1) >= item["detB_R"]
    ]
    return {
        "lower_both_block_minima_to_two": {
            "component_norms": [2, 2],
            "mixed_vector_norm": 4,
            "row_support_split_forced": False,
        },
        "omit_trace_multiple_of_six_in_wave29_type": {
            "type": [12, 6],
            "trace_pair": [28, 32],
            "A_log_cap": 3**8,
            "detB_A": 3645,
            "strict_contradiction": False,
        },
        "use_only_exceptional_block_log_cap": {
            "surviving_type_count": len(exceptional_only),
            "surviving_types": exceptional_only,
        },
        "omit_log_equality_integral_split": {
            "surviving_type_count": len(before_equality_veto),
            "surviving_types": before_equality_veto,
        },
        "remaining_scalar_spectrum": surviving_boundary()["scalar_spectral_control"],
    }


def derive(enabled: Iterable[str] = ESSENTIAL_PREMISES) -> dict[str, object]:
    active = set(enabled)
    require(
        active,
        "rootless_integral_orthogonal_decomposition",
        "norm-four row support split",
    )
    require(active, "tight_frame_identity", "block row counts")
    require(active, "schur_block_inheritance", "M/W/Q/B block inheritance")
    require(active, "endpoint_detq_constraints", "unique det(Q)=5")
    require(
        active,
        "even_positive_block_forms",
        "positive integral determinant factors",
    )
    require(
        active,
        "even_unimodular_signature_veto",
        "Q allocation and block-rank restrictions",
    )
    require(
        active,
        "row_alphabet_trace_residue",
        "block traces are positive multiples of six",
    )
    require(
        active,
        "b_equals_i_plus_2c_integral",
        "integral block C and trace exponents",
    )
    require(
        active,
        "positive_form_self_adjointness",
        "block AM-GM and logarithmic spectral domain",
    )
    require(
        active,
        "characteristic_pseudodeterminant",
        "block logarithmic determinant caps",
    )
    require(
        active,
        "equality_integral_split",
        "complement equality-rank veto",
    )

    hashes = verify_frozen_inputs()
    detq_values = unique_endpoint_detq()
    if detq_values != [5]:
        raise AssertionError(f"endpoint det(Q) census drifted: {detq_values!r}")
    alphabet = row_alphabet_solutions()
    if len(alphabet) != 13:
        raise AssertionError("row alphabet must have exactly 13 solutions")
    census = decomposition_census()
    excluded = [item for item in census if item["status"] == "EXCLUDED"]
    survivors = [
        item
        for item in census
        if item["status"] == "SURVIVES_THIS_REDUCTION"
    ]
    if len(census) != 15 or len(excluded) != 14 or len(survivors) != 1:
        raise AssertionError("decomposition census counts drifted")

    return {
        "scope": (
            "Conditional reduction of rootless integrally orthogonally "
            "decomposable h=729 S-forms under the full n3=708 endpoint "
            "package; no endpoint or graph resolution."
        ),
        "status": "DERIVED_REPAIR_PENDING_INDEPENDENT_REVERIFICATION",
        "public_base_commit": PUBLIC_BASE_COMMIT,
        "runtime": {
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
            "platform": platform.platform(),
        },
        "frozen_input_hashes": hashes,
        "endpoint": {
            "rank": RANK,
            "rows": ROWS,
            "frame_scale": FRAME_SCALE,
            "row_norm": ROW_NORM,
            "traceB": TRACE_B,
            "detS": DET_S,
            "detB_cap": DET_B_CAP,
            "detQ_values": detq_values,
        },
        "abstraction": {
            "row_support":
                "minimum-four orthogonal blocks force every norm-four row "
                "into one block",
            "block_rows": "4*n_J=21*rank(J)",
            "block_inheritance": "M,W,Q,B,C split with the row support",
            "Q_allocation":
                "one block has detQ=5; all others have detQ=1",
            "exceptional_rank":
                "the detQ=5 block has rank 4 mod 8",
            "exceptional_detS_exponent": [2, 4, 6],
            "block_trace_residue": "each trace(B_J) is a positive multiple of 6",
            "log_cap": "det(B_J)<=3^trace(C_J)",
            "log_equality":
                "equality makes C_J an integral self-adjoint idempotent",
        },
        "row_alphabet": alphabet,
        "decomposition_census": census,
        "census_summary": {
            "candidate_types": len(census),
            "excluded_types": len(excluded),
            "surviving_types": len(survivors),
            "obstruction_counts": {
                key: sum(
                    item.get("first_obstruction") == key for item in census
                )
                for key in (
                    "blockwise_AM_GM_and_trace_residue",
                    "exceptional_block_logarithmic_cap",
                    "complement_block_logarithmic_cap",
                    "log_equality_integral_split_signature_veto",
                )
            },
        },
        "surviving_boundary": surviving_boundary(),
        "hostile_controls": hostile_controls(),
        "limitations": [
            "Orthogonal decomposability and minimum at least four are essential.",
            "The surviving rank-20 plus rank-24 type is not constructed.",
            "No automorphism, restricted search, or nonexistence inference is used.",
            "General indecomposable or rooted h=729 forms remain untreated.",
            "n3=708, Conway-99, and novelty remain UNKNOWN.",
        ],
    }


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(payload, indent=2, sort_keys=True))
        stream.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    result = derive()
    if arguments.output is None:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        write_json(arguments.output, result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
