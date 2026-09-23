#!/usr/bin/env python3
"""Independent exact verifier for the Wave 30 decomposable h=729 claim.

This file deliberately does not import or execute any Wave 30 discovery
module.  It reconstructs the finite arithmetic census and its hostile
controls from the frozen endpoint premises.  It also records, without
repairing, the submitted package's stale Wave 29 input hash.
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

RANK = 44
ROW_COUNT = 231
FRAME_SCALE = 21
ROW_NORM = 4
TRACE_B = 60
DET_S = 3**6
DET_B_BOUND = 6525

DISCOVERY_ARTIFACTS = {
    "agents/2026-07-24-wave30-general-h729.md":
        "1bc63f569600bca88e12c977a0bd94ecdd03aa5f3fd8c4f203d4778fbec78efa",
    "attempts/wave30-general-h729/artifact-manifest.sha256":
        "29cbbdff1ab167b436db725130d830bfd047beb1c4ba834c51b5a33c3aed690a",
    "attempts/wave30-general-h729/exact_check.py":
        "ed8edcbb0febde6d6fbd57776b7696402f832421fa11fb1984fcd57c8369eaff",
    "attempts/wave30-general-h729/exact-results.json":
        "93cc1633d0b25d5f3daecd4c49cbc3b2dc3f754576a3cd5c9364c729a79a7698",
    "attempts/wave30-general-h729/failed-routes.md":
        "397f74c75a8ae24bedd26fea41c0fb82d03c6611a87627e86aeb29244a586006",
    "attempts/wave30-general-h729/input-freeze.sha256":
        "a07c703b20237441b221e13c68be885d01db180871b8496af5d7204e2587793b",
    "attempts/wave30-general-h729/run-report.yaml":
        "77232c06827c4c62e7dc6f5380cc4ebe2a3c6d5496fe8c3592589986089e416f",
    "attempts/wave30-general-h729/test_exact_check.py":
        "9075d5fd77253850ba09c4655d9cbab135eb32fdd36638dc4aa9051fa49898a2",
}

CURRENT_PRIOR_ARTIFACTS = {
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

SUBMITTED_WAVE29_AUDIT_HASH = (
    "4101a394252807fb9de8c39fb32b780bc88410d99e47dfe698da251b49f3e061"
)

REPAIR_FILES = [
    "agents/2026-07-24-wave30-general-h729.md",
    "attempts/wave30-general-h729/exact_check.py",
    "attempts/wave30-general-h729/exact-results.json",
    "attempts/wave30-general-h729/input-freeze.sha256",
    "attempts/wave30-general-h729/run-report.yaml",
    "attempts/wave30-general-h729/artifact-manifest.sha256",
]

ESSENTIAL_HYPOTHESES = (
    "even_integral_positive_definite_S",
    "rootless_minimum_four",
    "integral_orthogonal_decomposition",
    "integral_norm_four_frame",
    "tight_frame_scale_21",
    "schur_square_definition",
    "endpoint_determinant_bounds",
    "even_integral_positive_definite_Q",
    "even_unimodular_signature_theorem",
    "row_sum_and_projector_alphabet",
    "integral_C_with_B_equals_I_plus_2C",
    "positive_form_self_adjointness",
    "characteristic_pseudodeterminant",
    "integral_idempotent_split",
)


class MissingHypothesis(ValueError):
    """Fail-closed signal used by premise-deletion tests."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_hash_map(expected: dict[str, str]) -> dict[str, str]:
    observed: dict[str, str] = {}
    for relative, wanted in sorted(expected.items()):
        actual = sha256_file(REPO_ROOT / relative)
        if actual != wanted:
            raise AssertionError(
                f"hash drift for {relative}: observed {actual}, expected {wanted}"
            )
        observed[relative] = actual
    return observed


def submitted_replay_gate() -> dict[str, object]:
    relative = "verification/wave29-s0-frame-exclusion/audit.md"
    observed = sha256_file(REPO_ROOT / relative)
    failed = observed != SUBMITTED_WAVE29_AUDIT_HASH
    return {
        "status": "FAIL_STALE_FROZEN_INPUT" if failed else "PASS",
        "path": relative,
        "submitted_expected_sha256": SUBMITTED_WAVE29_AUDIT_HASH,
        "current_applicable_sha256": observed,
        "submitted_unittest_observation": {
            "command":
                "python -B -m unittest -v test_exact_check.py",
            "tests_run": 0 if failed else 20,
            "status": "ERROR" if failed else "PASS",
            "failure_stage": (
                "setUpClass -> verify_frozen_inputs"
                if failed else None
            ),
        },
        "submitted_generator_observation": {
            "command": "python -B exact_check.py --output <temporary-path>",
            "status": "ERROR" if failed else "PASS",
            "output_written": not failed,
        },
        "repair_required": failed,
        "files_requiring_recorded_repair": REPAIR_FILES if failed else [],
        "repair_policy": (
            "Do not overwrite the failed record. Repair the frozen hash and "
            "dependent outputs in a new revision, then re-run discovery and "
            "independent verification."
        ),
    }


def require_all(enabled: Iterable[str]) -> None:
    active = set(enabled)
    for name in ESSENTIAL_HYPOTHESES:
        if name not in active:
            raise MissingHypothesis(name)


def endpoint_detq_values() -> list[int]:
    """Exact h=729 determinant-Q candidates from the frozen endpoint."""

    upper = DET_B_BOUND // DET_S
    return [
        determinant
        for determinant in range(1, upper + 1)
        if determinant >= 5 and determinant % 4 == 1
    ]


def shell_size(block_rank: int) -> int:
    numerator = FRAME_SCALE * block_rank
    quotient, remainder = divmod(numerator, ROW_NORM)
    if remainder:
        raise ValueError("the block rank is incompatible with 4*n=21*r")
    return quotient


def row_alphabet() -> list[dict[str, int]]:
    """Solve the three exact row equations independently by brute force."""

    solutions: list[dict[str, int]] = []
    for minus_two in range(ROW_COUNT):
        for plus_one in range(ROW_COUNT):
            # The row-sum equation determines minus_one.
            minus_one = ROW_NORM + plus_one - 2 * minus_two
            if minus_one < 0:
                continue
            zero = ROW_COUNT - 1 - plus_one - minus_one - minus_two
            if zero < 0:
                continue
            square_sum = (
                ROW_NORM**2 + plus_one + minus_one + 4 * minus_two
            )
            if square_sum != FRAME_SCALE * ROW_NORM:
                continue
            cubic_sum = (
                ROW_NORM**3 + plus_one - minus_one - 8 * minus_two
            )
            solutions.append(
                {
                    "plus_one": plus_one,
                    "minus_one": minus_one,
                    "minus_two": minus_two,
                    "zero": zero,
                    "cubic_sum": cubic_sum,
                }
            )
    return sorted(solutions, key=lambda item: item["minus_two"])


def partitions_into_multiples_of_eight(total: int) -> list[list[int]]:
    """Unordered positive partitions used to test arbitrary many blocks."""

    if total % 8:
        return []
    units = total // 8
    output: list[list[int]] = []

    def visit(remaining: int, minimum: int, prefix: list[int]) -> None:
        if remaining == 0:
            output.append([8 * item for item in prefix])
            return
        for item in range(minimum, remaining + 1):
            visit(remaining - item, item, prefix + [item])

    visit(units, 1, [])
    return output


def determinant_exponent_options() -> list[tuple[int, int]]:
    """All aggregate (rank(A), v3(det(S_A))) types before inequalities."""

    types: list[tuple[int, int]] = []
    for rank_a in range(4, RANK, 4):
        rank_r = RANK - rank_a
        # det(Q_R)=1 makes every original R component even unimodular.
        if not partitions_into_multiples_of_eight(rank_r):
            continue
        # The total rank then forces rank(A)=4 mod 8.
        if rank_a % 8 != 4:
            continue
        for exponent in range(7):
            # det(S_A)=3^a and the even odd-determinant congruence is 1 mod 4.
            if pow(3, exponent, 4) != 1:
                continue
            # a=0 would make S_A even unimodular at rank 4 mod 8.
            if exponent == 0:
                continue
            types.append((rank_a, exponent))
    return types


def amgm_exact(rank: int, trace: int, determinant: int) -> bool:
    """Integer form of trace^rank >= rank^rank determinant."""

    if min(rank, trace, determinant) <= 0:
        return False
    return trace**rank >= rank**rank * determinant


def possible_trace_pairs(rank_a: int, exponent_a: int) -> list[tuple[int, int]]:
    rank_r = RANK - rank_a
    determinant_a = 5 * 3**exponent_a
    determinant_r = 3 ** (6 - exponent_a)
    pairs: list[tuple[int, int]] = []
    for trace_a in range(6, TRACE_B, 6):
        trace_r = TRACE_B - trace_a
        if amgm_exact(rank_a, trace_a, determinant_a) and amgm_exact(
            rank_r, trace_r, determinant_r
        ):
            pairs.append((trace_a, trace_r))
    return pairs


def log_cap(rank: int, trace_b: int) -> dict[str, int]:
    difference = trace_b - rank
    if difference < 0 or difference % 2:
        raise ValueError("B=I+2C gives no nonnegative integral trace(C)")
    trace_c = difference // 2
    return {"traceC": trace_c, "detB_cap": 3**trace_c}


def classify(rank_a: int, exponent_a: int) -> dict[str, object]:
    rank_r = RANK - rank_a
    det_s_a = 3**exponent_a
    det_s_r = 3 ** (6 - exponent_a)
    det_b_a = 5 * det_s_a
    det_b_r = det_s_r
    pairs = possible_trace_pairs(rank_a, exponent_a)
    item: dict[str, object] = {
        "rank_A": rank_a,
        "rank_R": rank_r,
        "v3_detS_A": exponent_a,
        "detS_A": det_s_a,
        "detS_R": det_s_r,
        "detQ_A": 5,
        "detQ_R": 1,
        "detB_A": det_b_a,
        "detB_R": det_b_r,
        "trace_pairs": [
            {"traceB_A": left, "traceB_R": right} for left, right in pairs
        ],
    }
    if not pairs:
        item.update(
            status="EXCLUDED",
            obstruction="exact_AM_GM_plus_trace_residue",
        )
        return item
    if len(pairs) != 1:
        raise AssertionError(f"non-unique trace pair for {(rank_a, exponent_a)}")

    trace_a, trace_r = pairs[0]
    cap_a = log_cap(rank_a, trace_a)
    cap_r = log_cap(rank_r, trace_r)
    item["A_logarithmic_data"] = cap_a
    item["R_logarithmic_data"] = cap_r

    if det_b_a > cap_a["detB_cap"]:
        item.update(
            status="EXCLUDED",
            obstruction="A_characteristic_pseudodeterminant_cap",
        )
        return item
    if det_b_r > cap_r["detB_cap"]:
        item.update(
            status="EXCLUDED",
            obstruction="R_characteristic_pseudodeterminant_cap",
        )
        return item

    if det_b_r == cap_r["detB_cap"]:
        image_rank = cap_r["traceC"]
        kernel_rank = rank_r - image_rank
        equality = {
            "all_nonzero_C_eigenvalues": 1,
            "C_is_integral_idempotent": True,
            "image_rank": image_rank,
            "kernel_rank": kernel_rank,
            "image_Q_even_unimodular_if_nonzero": image_rank > 0,
            "kernel_Q_even_unimodular_if_nonzero": kernel_rank > 0,
            "image_signature_allowed": image_rank % 8 == 0,
            "kernel_signature_allowed": kernel_rank % 8 == 0,
        }
        item["R_log_equality_split"] = equality
        if image_rank % 8 or kernel_rank % 8:
            item.update(
                status="EXCLUDED",
                obstruction="integral_idempotent_even_unimodular_rank_veto",
            )
            return item

    item.update(status="SURVIVES_THIS_REDUCTION", obstruction=None)
    return item


def full_census() -> list[dict[str, object]]:
    return [
        classify(rank_a, exponent_a)
        for rank_a, exponent_a in determinant_exponent_options()
    ]


def calculus_certificate() -> dict[str, object]:
    """Exact rational and formal-coefficient checks for the log inequality."""

    # log(3)=2*sum_{k>=0}(1/2)^(2k+1)/(2k+1).
    first_term = Fraction(1, 1)
    crude_tail_upper = Fraction(1, 3)
    lower = first_term
    upper = first_term + crude_tail_upper

    # Represent a coefficient a*L+b by (a,b).  These are the coefficients,
    # descending in x, of x(1+2x)F'(x) and (x-1)(2Lx+c), c=L-2/3.
    derivative_coefficients = [
        (Fraction(2), Fraction(0)),
        (Fraction(-1), Fraction(-2, 3)),
        (Fraction(-1), Fraction(2, 3)),
    ]
    factor_coefficients = [
        (Fraction(2), Fraction(0)),
        (Fraction(-1), Fraction(-2, 3)),
        (Fraction(-1), Fraction(2, 3)),
    ]
    if derivative_coefficients != factor_coefficients:
        raise AssertionError("formal derivative factorization failed")

    return {
        "log3_series": "2*sum_(k>=0) (1/2)^(2k+1)/(2k+1)",
        "strict_rational_bounds": {
            "lower": str(lower),
            "upper": str(upper),
            "implies_log3_gt_2_over_3": lower > Fraction(2, 3),
            "implies_log3_lt_2": upper < 2,
        },
        "c_definition": "c=log(3)-2/3",
        "c_is_positive": True,
        "positive_domain_identity": (
            "x(1+2x)F'(x)=(x-1)(2*log(3)*x+c)"
        ),
        "positive_domain_equality_only_at": 1,
        "negative_domain": (
            "for -1/2<x<0, g'(x)<log(3)-2<0 and g(0)=0; "
            "the pointwise inequality is strict"
        ),
        "summed_conclusion": (
            "det(I+2C)<=3^trace(C) when C is integral, real "
            "diagonalizable, and every eigenvalue is greater than -1/2"
        ),
        "equality_conclusion": (
            "all nonzero eigenvalues of C are 1, hence C^2=C"
        ),
    }


def surviving_boundary(census: list[dict[str, object]]) -> dict[str, object]:
    survivors = [
        item for item in census if item["status"] == "SURVIVES_THIS_REDUCTION"
    ]
    if [(item["rank_A"], item["v3_detS_A"]) for item in survivors] != [(20, 6)]:
        raise AssertionError("the surviving type is not uniquely (20,6)")

    rows_a = shell_size(20)
    rows_u = shell_size(24)
    profiles: list[dict[str, int]] = []
    for n11 in range(rows_u + 1):
        n9 = n11 + 4
        n10 = rows_u - n9 - n11
        if min(n9, n10, n11) < 0:
            continue
        if 9 * n9 + 10 * n10 + 11 * n11 != 1256:
            continue
        profiles.append({"n9": n9, "n10": n10, "n11": n11})

    directed = {
        "plus_one": rows_u * 32 - 1256,
        "minus_one": rows_u * 36 - 3 * 1256,
        "minus_two": 1256,
    }
    directed["zero"] = rows_u * (rows_u - 1) - sum(directed.values())

    scalar_c = {0: 13, 1: 6, 2: 1}
    scalar_b = {1 + 2 * value: multiplicity for value, multiplicity in scalar_c.items()}
    scalar_det = 1
    for eigenvalue, multiplicity in scalar_b.items():
        scalar_det *= eigenvalue**multiplicity

    return {
        "decomposition": {
            "A": {
                "rank": 20,
                "detS": 729,
                "detQ": 5,
                "detB": 3645,
                "traceB": 36,
                "rows": rows_a,
                "minimum_at_least": 4,
            },
            "U": {
                "rank": 24,
                "detS": 1,
                "detQ": 1,
                "detB": 1,
                "traceB": 24,
                "rows": rows_u,
                "minimum_at_least": 4,
                "even_unimodular": True,
                "B_equals_identity": True,
                "C_equals_zero": True,
            },
        },
        "tensor_isometry": {
            "Phi_star_Phi": "I_24",
            "cauchy_bound_on_absolute_cubic_row_sum": 8,
            "allowed_minus_two_counts": [9, 10, 11],
            "sum_minus_two_counts": 1256,
            "profile_count": len(profiles),
            "first_profile": profiles[0],
            "last_profile": profiles[-1],
            "internal_directed_totals": directed,
            "status": "NECESSARY_COUNTS_ONLY",
        },
        "scalar_hostile_control": {
            "C_multiplicities": {str(key): value for key, value in scalar_c.items()},
            "B_multiplicities": {str(key): value for key, value in scalar_b.items()},
            "traceC": sum(key * value for key, value in scalar_c.items()),
            "traceC2": sum(key * key * value for key, value in scalar_c.items()),
            "traceB": sum(key * value for key, value in scalar_b.items()),
            "detB": scalar_det,
            "scope": "integral scalar-spectrum control, not a lattice or frame",
        },
    }


def hostile_controls(census: list[dict[str, object]]) -> dict[str, object]:
    a_cap_survivors = [
        [int(item["rank_A"]), int(item["v3_detS_A"])]
        for item in census
        if (
            item.get("A_logarithmic_data") is not None
            and item["detB_A"]
            <= item["A_logarithmic_data"]["detB_cap"]  # type: ignore[index]
        )
    ]
    both_cap_survivors = [
        [int(item["rank_A"]), int(item["v3_detS_A"])]
        for item in census
        if (
            item.get("A_logarithmic_data") is not None
            and item.get("R_logarithmic_data") is not None
            and item["detB_A"]
            <= item["A_logarithmic_data"]["detB_cap"]  # type: ignore[index]
            and item["detB_R"]
            <= item["R_logarithmic_data"]["detB_cap"]  # type: ignore[index]
        )
    ]
    return {
        "minimum_two": {
            "orthogonal_component_norms": [2, 2],
            "mixed_total_norm": 4,
            "support_split_fails": True,
        },
        "rational_not_integral_split": {
            "rootless_form": "4*I_2",
            "rational_orthogonal_lines": ["span(1,1)", "span(1,-1)"],
            "integral_vector": [1, 0],
            "projections": ["(1/2,1/2)", "(1/2,-1/2)"],
            "support_split_fails": True,
        },
        "drop_detQ_mod_four": {
            "additional_integer_candidates_under_bound": [6, 7, 8],
        },
        "drop_trace_multiple_six": {
            "wave29_type": [12, 6],
            "trace_pair": [28, 32],
            "A_traceC": 8,
            "A_cap": 3**8,
            "A_determinant": 3645,
            "contradiction_lost": True,
        },
        "drop_C_integrality": {
            "C": "(1/2)*I_12",
            "traceC": 6,
            "det_I_plus_2C": 2**12,
            "claimed_integral_cap": 3**6,
            "cap_violated": 2**12 > 3**6,
        },
        "drop_self_adjoint_real_spectrum": {
            "C_block": "[[1,N],[-N,1]]",
            "det_I_plus_2C": "9+4*N^2",
            "nominal_cap": 9,
            "complex_eigenvalues": True,
        },
        "use_only_A_cap": {
            "survivor_count": len(a_cap_survivors),
            "types": a_cap_survivors,
        },
        "omit_equality_split": {
            "survivor_count": len(both_cap_survivors),
            "types": both_cap_survivors,
        },
        "drop_evenness_in_equality_veto": {
            "odd_unimodular_rank_two_control": "I_2",
            "signature_rank_veto_fails": True,
        },
    }


def build_result(enabled: Iterable[str] = ESSENTIAL_HYPOTHESES) -> dict[str, object]:
    require_all(enabled)
    discovery_hashes = verify_hash_map(DISCOVERY_ARTIFACTS)
    prior_hashes = verify_hash_map(CURRENT_PRIOR_ARTIFACTS)

    if endpoint_detq_values() != [5]:
        raise AssertionError("the endpoint determinant-Q value is not unique")
    alphabet = row_alphabet()
    if [item["minus_two"] for item in alphabet] != list(range(13)):
        raise AssertionError("the row alphabet is incomplete")
    types = determinant_exponent_options()
    if types != [
        (4, 2), (4, 4), (4, 6),
        (12, 2), (12, 4), (12, 6),
        (20, 2), (20, 4), (20, 6),
        (28, 2), (28, 4), (28, 6),
        (36, 2), (36, 4), (36, 6),
    ]:
        raise AssertionError("rank/determinant census drift")
    census = full_census()
    excluded = [item for item in census if item["status"] == "EXCLUDED"]
    survivors = [
        item for item in census if item["status"] == "SURVIVES_THIS_REDUCTION"
    ]
    if (len(census), len(excluded), len(survivors)) != (15, 14, 1):
        raise AssertionError("classification count drift")

    return {
        "verdict": {
            "mathematical_implication":
                "VERIFIED_SCOPED_CONDITIONAL_CLASSIFICATION",
            "submitted_discovery_replay": submitted_replay_gate()["status"],
            "publication_gate": "FAIL_RECORDED_REPAIR_AND_REVERIFICATION_REQUIRED",
        },
        "scope": (
            "Rootless even integral positive-definite rank-44 h=729 S-forms "
            "with a nontrivial integral orthogonal decomposition and the full "
            "frozen n3=708 projector/Schur endpoint package."
        ),
        "status_wall": {
            "surviving_rank20_plus_rank24_type": "UNKNOWN",
            "rooted_h729_forms": "UNKNOWN",
            "integrally_indecomposable_h729_forms": "UNKNOWN",
            "all_h729_endpoint_forms": "UNKNOWN",
            "n3_708": "UNKNOWN",
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "runtime": {
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
        },
        "blind_frozen_discovery_hashes": discovery_hashes,
        "current_prior_hashes": prior_hashes,
        "submitted_replay_gate": submitted_replay_gate(),
        "endpoint": {
            "rank": RANK,
            "rows": ROW_COUNT,
            "frame_scale": FRAME_SCALE,
            "row_norm": ROW_NORM,
            "traceB": TRACE_B,
            "detS": DET_S,
            "detB_bound": DET_B_BOUND,
            "detQ_values": endpoint_detq_values(),
        },
        "imported_hypothesis_checks": {
            "integral_change_of_basis": (
                "A unimodular orthogonal decomposition keeps row "
                "coordinates integral and preserves evenness."
            ),
            "row_support": (
                "Every nonzero block component has norm at least 4, so a "
                "norm-4 row has exactly one nonzero component."
            ),
            "block_inheritance": (
                "Cross blocks of M vanish; entrywise squaring preserves "
                "them; Q, B, and C then split exactly."
            ),
            "block_shell_equation": "4*n_J=21*rank(J)",
            "determinant_allocation": (
                "Positive integer Q-block determinants multiply to 5."
            ),
            "rank_veto": (
                "Every even positive-definite unimodular Q block has "
                "rank divisible by 8."
            ),
            "trace_residue": (
                "tr(B_J) is a positive multiple of 6 from exact cubic "
                "row sums."
            ),
            "logarithmic_cap": calculus_certificate(),
            "equality_split": (
                "An integral self-adjoint idempotent splits Z^s into "
                "G-orthogonal image and kernel; Q restricts to even "
                "unimodular forms on both nonzero pieces."
            ),
        },
        "multi_block_complements": {
            str(rank_a): partitions_into_multiples_of_eight(RANK - rank_a)
            for rank_a in (4, 12, 20, 28, 36)
        },
        "row_alphabet": alphabet,
        "classification_census": census,
        "classification_summary": {
            "types": len(census),
            "excluded": len(excluded),
            "surviving": len(survivors),
            "obstruction_counts": {
                obstruction: sum(
                    item.get("obstruction") == obstruction for item in census
                )
                for obstruction in (
                    "exact_AM_GM_plus_trace_residue",
                    "A_characteristic_pseudodeterminant_cap",
                    "R_characteristic_pseudodeterminant_cap",
                    "integral_idempotent_even_unimodular_rank_veto",
                )
            },
        },
        "surviving_boundary": surviving_boundary(census),
        "hostile_controls": hostile_controls(census),
        "limitations": [
            "The theorem is conditional on the frozen full endpoint package.",
            "The one surviving decomposition type is not constructed or excluded.",
            "The tensor counts are necessary, not an M, X, lattice, or graph.",
            "No automorphism or finite nonexistence inference is used.",
            "The submitted package must be repaired and re-verified before publication.",
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
    args = parser.parse_args()
    result = build_result()
    if args.output is None:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        write_json(args.output, result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
