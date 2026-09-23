"""Clean-room exact verifier for the Wave 137 binary Arf branches.

This module intentionally does not import or execute discovery code.  It
reconstructs the length-99 binary MacWilliams transform from the defining
binomial sum, the four Wave-132 distinguished-row projections from their
combinatorial meanings, and the six signed Krawtchouk rows from the frozen
Arf/Ising constants.

Only exact integers and fractions are used.  Solver status strings are
reported but never treated as mathematical evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from functools import lru_cache
from math import comb
from pathlib import Path
from typing import Any, Iterable


N = 99
IMAGE_DIMENSION = 54
DUAL_DIMENSION = 45
IMAGE_ORDER = 1 << IMAGE_DIMENSION
DUAL_ORDER = 1 << DUAL_DIMENSION
ARF_MAGNITUDE = 1 << 27

# These are the independently frozen normalized signed Krawtchouk rows
#   S_t = G_R^{-1} sum_w (-1)^(w/2) A_w K_t(w).
SIGNED_NORMALIZED = {
    0: 1,
    1: -99,
    2: 3465,
    3: -56595,
    4: 462924,
    5: -1821204,
}

IMAGE_LOWER = {
    0: 1,
    14: 99,
    24: 4158,
    26: 693,
    30: 70686,
    32: 41580,
    34: 36036,
    36: 8547,
}
DUAL_BASE_LOWER = {
    0: 1,
    15: 99,
    24: 693,
    26: 4158,
    31: 41580,
    33: 79002,
    35: 8316,
    37: 27720,
    39: 231,
    99: 1,
}

EXPECTED_PAIR_TABLES = {
    "image_neighborhood_rows": {
        "14": {"intersection_14": 99},
        "ordered_distinct": {
            "intersection_1": 1386,
            "intersection_2": 8316,
        },
    },
    "dual_closed_neighborhood_rows": {
        "15": {"intersection_15": 99},
        "ordered_distinct": {
            "intersection_3": 1386,
            "intersection_2": 8316,
        },
    },
    "mixed_neighborhood_closed": {
        "ordered_diagonal": {"intersection_14": 99},
        "ordered_off_diagonal": {"intersection_2": 9702},
    },
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_fraction(value: Any) -> Fraction:
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value)
    if isinstance(value, str):
        return Fraction(value)
    if isinstance(value, dict) and set(value) == {"numerator", "denominator"}:
        return Fraction(int(value["numerator"]), int(value["denominator"]))
    raise TypeError(f"unsupported rational encoding: {value!r}")


def encode_fraction(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


@lru_cache(maxsize=None)
def binary_krawtchouk(degree: int, weight: int) -> int:
    """Direct defining binomial sum, independent of discovery recurrences."""
    return sum(
        (-1) ** overlap
        * comb(weight, overlap)
        * comb(N - weight, degree - overlap)
        for overlap in range(
            max(0, degree - (N - weight)),
            min(weight, degree) + 1,
        )
    )


def signed_phase(weight: int) -> int:
    if weight % 2:
        raise ValueError("Arf phase is defined here only on even weights")
    return -1 if (weight // 2) % 2 else 1


def rational_rank(rows: Iterable[Iterable[int | Fraction]]) -> int:
    """Exact row rank by fraction-preserving Gaussian elimination."""
    matrix = [[Fraction(value) for value in row] for row in rows]
    if not matrix:
        return 0
    width = len(matrix[0])
    if any(len(row) != width for row in matrix):
        raise ValueError("ragged rank matrix")
    rank = 0
    for column in range(width):
        pivot = next(
            (
                candidate
                for candidate in range(rank, len(matrix))
                if matrix[candidate][column]
            ),
            None,
        )
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        pivot_value = matrix[rank][column]
        matrix[rank] = [value / pivot_value for value in matrix[rank]]
        for other in range(len(matrix)):
            if other == rank or not matrix[other][column]:
                continue
            multiplier = matrix[other][column]
            matrix[other] = [
                value - multiplier * pivot_entry
                for value, pivot_entry in zip(matrix[other], matrix[rank])
            ]
        rank += 1
        if rank == len(matrix):
            break
    return rank


def independent_constant_derivation() -> dict[str, Any]:
    """Reconstruct S_0,...,S_4 from local SRG counts and freeze S_5.

    If B_uv=(-1)^A_uv off the diagonal, then for a vertex set T

        (-1)^q(A 1_T) = (-1)^(|T|+e(T)).

    Thus the normalized signed Krawtchouk row is the signed-clique sum.
    The first four nontrivial rows follow from the exact one-, two-, and
    three-subset tables.  For t=4, extend every triple by one vertex.  The
    outside correlation for a triple with e induced edges, c common
    neighbors, and i2 internal length-two incidences is

        H = 96 - 2(42-2e) + 4(6-e-i2) - 8c.

    The t=5 value is a frozen target identity in this verifier; it is then
    checked directly against every exact witness rather than inferred from
    discovery metadata.
    """
    edges = 693
    nonedges = comb(N, 2) - edges
    three_types = [
        # name, count, induced edges, outside common neighbors, internal i2
        ("independent_c0", 70686, 0, 0, 0),
        ("independent_c1", 27720, 0, 1, 0),
        ("one_edge_c0", 41580, 1, 0, 0),
        ("one_edge_c1", 8316, 1, 1, 0),
        ("path", 8316, 2, 0, 1),
        ("triangle", 231, 3, 0, 3),
    ]
    if sum(row[1] for row in three_types) != comb(N, 3):
        raise AssertionError("three-subset table does not partition C(99,3)")

    s0 = 1
    s1 = -N
    s2 = nonedges - edges
    unsigned_s3 = sum(count * (-1) ** edge_count for _, count, edge_count, _, _ in three_types)
    s3 = -unsigned_s3
    triple_extension_terms = []
    four_numerator = 0
    for name, count, edge_count, common, internal_i2 in three_types:
        outside_degree_sum = 42 - 2 * edge_count
        outside_pair_sum = 6 - edge_count - internal_i2
        outside_correlation = (
            96
            - 2 * outside_degree_sum
            + 4 * outside_pair_sum
            - 8 * common
        )
        contribution = count * (-1) ** edge_count * outside_correlation
        four_numerator += contribution
        triple_extension_terms.append(
            {
                "type": name,
                "count": count,
                "edge_count": edge_count,
                "outside_correlation": outside_correlation,
                "contribution": contribution,
            }
        )
    if four_numerator % 4:
        raise AssertionError("four-subset extension numerator is nonintegral")
    s4 = four_numerator // 4
    derived = {0: s0, 1: s1, 2: s2, 3: s3, 4: s4}
    if derived != {degree: SIGNED_NORMALIZED[degree] for degree in range(5)}:
        raise AssertionError(f"signed constant derivation drifted: {derived!r}")
    return {
        "identity": (
            "S_t=sum_|T|=t (-1)^(|T|+e(T))="
            "G_R^-1 sum_w (-1)^(w/2) A_w K_t(w)"
        ),
        "derived_constants_t0_t4": {str(k): v for k, v in derived.items()},
        "frozen_exact_t5": SIGNED_NORMALIZED[5],
        "triple_extension_terms_for_t4": triple_extension_terms,
    }


def ordinary_model_ranks() -> dict[str, Any]:
    """Rank the Wave-132 A-only equality system and each signed row.

    Eliminating B by the forward MacWilliams transform leaves the allowed
    image variables A_0,A_14,A_16,...,A_92.  The base equalities are A_0=1,
    sum A=2^54, and transformed dual coefficients B_1,...,B_14=0.
    """
    weights = [0] + list(range(14, 94, 2))
    a0 = [1 if weight == 0 else 0 for weight in weights]
    size = [1 for _ in weights]
    ordinary_rows = [a0, size]
    ordinary_rows.extend(
        [
            binary_krawtchouk(degree, weight)
            for weight in weights
        ]
        for degree in range(1, 15)
    )
    base_rank = rational_rank(ordinary_rows)
    ordinary_rhs = [1, IMAGE_ORDER] + [0] * 14
    cumulative = []
    rows = list(ordinary_rows)
    for degree in range(6):
        rows.append(
            [
                signed_phase(weight)
                * binary_krawtchouk(degree, weight)
                for weight in weights
            ]
        )
        cumulative.append(
            {
                "through_signed_degree": degree,
                "rank": rational_rank(rows),
                "rank_increment": rational_rank(rows) - rational_rank(rows[:-1]),
                "augmented_rank_plus": rational_rank(
                    [
                        row + [rhs]
                        for row, rhs in zip(
                            rows,
                            ordinary_rhs
                            + [
                                ARF_MAGNITUDE * SIGNED_NORMALIZED[index]
                                for index in range(degree + 1)
                            ],
                        )
                    ]
                ),
                "augmented_rank_minus": rational_rank(
                    [
                        row + [rhs]
                        for row, rhs in zip(
                            rows,
                            ordinary_rhs
                            + [
                                -ARF_MAGNITUDE * SIGNED_NORMALIZED[index]
                                for index in range(degree + 1)
                            ],
                        )
                    ]
                ),
            }
        )
    return {
        "eliminated_variable_order": [f"A_{weight}" for weight in weights],
        "variable_count": len(weights),
        "ordinary_equality_row_count": len(ordinary_rows),
        "ordinary_equality_rank": base_rank,
        "cumulative_signed_ranks": cumulative,
    }


def coefficient_arrays(payload: dict[str, Any]) -> tuple[list[Fraction], list[Fraction]]:
    ordinary = payload.get("ordinary", payload)
    image_map = ordinary.get("image_coefficients") or ordinary.get("A")
    dual_map = ordinary.get("dual_coefficients") or ordinary.get("B")
    if not isinstance(image_map, dict) or not isinstance(dual_map, dict):
        raise KeyError("witness lacks ordinary image/dual coefficient maps")
    image = [Fraction(0) for _ in range(N + 1)]
    dual = [Fraction(0) for _ in range(N + 1)]
    for weight, value in image_map.items():
        image[int(weight)] = parse_fraction(value)
    for weight, value in dual_map.items():
        dual[int(weight)] = parse_fraction(value)
    return image, dual


def dual_lower_bounds() -> dict[int, int]:
    result = dict(DUAL_BASE_LOWER)
    for weight, lower in list(result.items()):
        result[N - weight] = max(result.get(N - weight, 0), lower)
    return result


def audit_ordinary(image: list[Fraction], dual: list[Fraction]) -> dict[str, Any]:
    failures: list[str] = []
    if any(value < 0 for value in image + dual):
        failures.append("negative ordinary coefficient")
    if image[0] != 1:
        failures.append("A_0 != 1")
    if dual[0] != 1 or dual[N] != 1:
        failures.append("B_0/B_99 normalization drift")
    if sum(image) != IMAGE_ORDER:
        failures.append("image size drift")
    if sum(dual) != DUAL_ORDER:
        failures.append("dual size drift")
    if any(image[weight] for weight in range(1, 14)):
        failures.append("image minimum-distance drift")
    if any(image[weight] for weight in range(1, N + 1, 2)):
        failures.append("image evenness drift")
    if any(image[weight] for weight in (94, 96, 98)):
        failures.append("Wave132 high-weight cut drift")
    if any(dual[weight] for weight in range(1, 15)):
        failures.append("dual minimum-distance drift")
    if any(dual[weight] != dual[N - weight] for weight in range(N + 1)):
        failures.append("dual complement symmetry drift")
    for weight, lower in IMAGE_LOWER.items():
        if image[weight] < lower:
            failures.append(f"image lower bound failed at {weight}")
    for weight, lower in dual_lower_bounds().items():
        if dual[weight] < lower:
            failures.append(f"dual lower bound failed at {weight}")

    forward_failures = []
    inverse_failures = []
    for degree in range(N + 1):
        transformed = sum(
            image[weight] * binary_krawtchouk(degree, weight)
            for weight in range(N + 1)
        )
        if transformed != IMAGE_ORDER * dual[degree]:
            forward_failures.append(degree)
        inverse = sum(
            dual[weight] * binary_krawtchouk(degree, weight)
            for weight in range(N + 1)
        )
        if inverse != DUAL_ORDER * image[degree]:
            inverse_failures.append(degree)
    if forward_failures:
        failures.append(f"forward MacWilliams rows failed: {forward_failures}")
    if inverse_failures:
        failures.append(f"inverse MacWilliams rows failed: {inverse_failures}")
    return {
        "pass": not failures,
        "failures": failures,
        "forward_rows_passed": (N + 1) - len(forward_failures),
        "inverse_rows_passed": (N + 1) - len(inverse_failures),
        "image_nonintegral_count": sum(v.denominator != 1 for v in image),
        "dual_nonintegral_count": sum(v.denominator != 1 for v in dual),
    }


def audit_signed_rows(
    image: list[Fraction],
    dual: list[Fraction],
    payload: dict[str, Any],
) -> dict[str, Any]:
    gauss = sum(
        signed_phase(weight) * image[weight]
        for weight in range(0, N + 1, 2)
    )
    if gauss not in (Fraction(ARF_MAGNITUDE), Fraction(-ARF_MAGNITUDE)):
        return {
            "pass": False,
            "failures": [
                f"G_R={encode_fraction(gauss)} is not +/-2^27"
            ],
            "G_R": encode_fraction(gauss),
            "epsilon": None,
            "rows": {},
        }
    epsilon = 1 if gauss > 0 else -1
    claimed_sign = payload.get("sign")
    max_moment = int(
        payload.get("max_moment", 1 if payload.get("include_k1") else 0)
    )
    failures = []
    if claimed_sign not in (-1, 1):
        failures.append(f"invalid or absent claimed sign: {claimed_sign!r}")
    elif claimed_sign != epsilon:
        failures.append(
            f"claimed sign {claimed_sign} disagrees with exact Gauss sign {epsilon}"
        )
    if not 0 <= max_moment <= 5:
        failures.append(f"unsupported max_moment {max_moment}")
    rows = {}
    for degree, normalized in SIGNED_NORMALIZED.items():
        observed = sum(
            signed_phase(weight)
            * image[weight]
            * binary_krawtchouk(degree, weight)
            for weight in range(0, N + 1, 2)
        )
        expected = gauss * normalized
        required = degree <= max_moment
        passed = observed == expected
        if required and not passed:
            failures.append(
                f"signed Krawtchouk degree {degree}: "
                f"{encode_fraction(observed)} != {encode_fraction(expected)}"
            )
        rows[str(degree)] = {
            "normalized_constant": normalized,
            "observed": encode_fraction(observed),
            "expected": encode_fraction(expected),
            "pass": passed,
            "required_by_stage": required,
        }
    k1_binomial = sum(
        signed_phase(weight) * (N - weight) * image[weight]
        for weight in range(0, N + 1, 2)
    )
    if max_moment >= 1 and k1_binomial:
        failures.append(
            "claimed K1 binomial equation "
            f"has value {encode_fraction(k1_binomial)}"
        )
    dual_even_gauss = sum(
        signed_phase(weight) * dual[weight]
        for weight in range(0, N + 1, 2)
    )
    expected_dual = -gauss / 32
    if dual_even_gauss != expected_dual:
        failures.append(
            "dual even Gauss sum does not equal -G_R/32"
        )
    shadow_cuts = payload.get(
        "shadow_cuts", {"lower_degrees": [], "upper_degrees": []}
    )
    shadow_rows = {}
    for degree in sorted(
        set(shadow_cuts.get("lower_degrees", []))
        | set(shadow_cuts.get("upper_degrees", []))
    ):
        observed = sum(
            signed_phase(weight)
            * image[weight]
            * binary_krawtchouk(degree, weight)
            for weight in range(0, N + 1, 2)
        )
        absolute_bound = ARF_MAGNITUDE * comb(N, degree)
        lower_pass = (
            degree not in shadow_cuts.get("lower_degrees", [])
            or observed >= -absolute_bound
        )
        upper_pass = (
            degree not in shadow_cuts.get("upper_degrees", [])
            or observed <= absolute_bound
        )
        if not lower_pass:
            failures.append(f"K{degree} shadow lower bound failed")
        if not upper_pass:
            failures.append(f"K{degree} shadow upper bound failed")
        shadow_rows[str(degree)] = {
            "observed": encode_fraction(observed),
            "absolute_bound": str(absolute_bound),
            "lower_required": degree
            in shadow_cuts.get("lower_degrees", []),
            "upper_required": degree
            in shadow_cuts.get("upper_degrees", []),
            "pass": lower_pass and upper_pass,
        }
    all_shadow_violations = []
    all_shadow_checked = bool(
        shadow_cuts.get("lower_degrees")
        or shadow_cuts.get("upper_degrees")
    )
    if all_shadow_checked:
        for degree in range(6, N + 1):
            observed = sum(
                signed_phase(weight)
                * image[weight]
                * binary_krawtchouk(degree, weight)
                for weight in range(0, N + 1, 2)
            )
            absolute_bound = ARF_MAGNITUDE * comb(N, degree)
            if not -absolute_bound <= observed <= absolute_bound:
                all_shadow_violations.append(
                    {
                        "degree": degree,
                        "observed": encode_fraction(observed),
                        "absolute_bound": str(absolute_bound),
                    }
                )
        if all_shadow_violations:
            failures.append(
                "one or more degree-6-through-99 shadow bounds failed"
            )
    return {
        "pass": not failures,
        "failures": failures,
        "G_R": encode_fraction(gauss),
        "epsilon": epsilon,
        "claimed_sign": claimed_sign,
        "max_moment": max_moment,
        "K1_binomial": encode_fraction(k1_binomial),
        "dual_even_G_E": encode_fraction(dual_even_gauss),
        "expected_dual_even_G_E": encode_fraction(expected_dual),
        "rows": rows,
        "shadow_rows": shadow_rows,
        "all_shadow_degrees_6_through_99_checked": all_shadow_checked,
        "all_shadow_violations": all_shadow_violations,
    }


def parse_split_table(raw: dict[str, Any]) -> dict[int, dict[int, Fraction]]:
    return {
        int(weight): {
            int(intersection): parse_fraction(value)
            for intersection, value in row.items()
        }
        for weight, row in raw.items()
    }


def audit_one_split(
    raw: dict[str, Any],
    coefficients: list[Fraction],
    distinguished_weight: int,
    odd_multiplier: int,
    forced_by_weight: dict[int, dict[int, int]],
) -> dict[str, Any]:
    table = parse_split_table(raw)
    failures = []
    checked_shells = 0
    for weight, coefficient in enumerate(coefficients):
        row = table.get(weight, {})
        if coefficient == 0:
            if any(row.values()):
                failures.append(f"nonzero split row at zero shell {weight}")
            continue
        checked_shells += 1
        lower = max(0, weight + distinguished_weight - N)
        upper = min(weight, distinguished_weight)
        if any(level < lower or level > upper for level in row):
            failures.append(f"intersection range failed at shell {weight}")
        if any(value < 0 for value in row.values()):
            failures.append(f"negative split value at shell {weight}")
        if sum(row.values()) != 99 * coefficient:
            failures.append(f"split row sum failed at shell {weight}")
        if (
            sum(level * value for level, value in row.items())
            != distinguished_weight * weight * coefficient
        ):
            failures.append(f"split first moment failed at shell {weight}")
        if (
            sum(value for level, value in row.items() if level % 2)
            != odd_multiplier * weight * coefficient
        ):
            failures.append(f"split odd count failed at shell {weight}")
        for level, lower_count in forced_by_weight.get(weight, {}).items():
            if row.get(level, Fraction(0)) < lower_count:
                failures.append(
                    f"forced split lower bound failed at ({weight},{level})"
                )
    extra_shells = sorted(set(table) - set(range(N + 1)))
    if extra_shells:
        failures.append(f"out-of-range split shells: {extra_shells}")
    return {
        "pass": not failures,
        "failures": failures,
        "checked_nonzero_shells": checked_shells,
        "nonintegral_entry_count": sum(
            value.denominator != 1
            for row in table.values()
            for value in row.values()
        ),
    }


def audit_split_systems(
    payload: dict[str, Any],
    image: list[Fraction],
    dual: list[Fraction],
) -> dict[str, Any]:
    tables = payload.get("split_enumerators")
    if not isinstance(tables, dict):
        return {
            "pass": False,
            "failures": ["witness lacks split_enumerators"],
            "systems": {},
        }
    specifications = {
        "image_vs_neighborhood": (
            image,
            14,
            1,
            {14: {14: 99, 1: 1386, 2: 8316}},
        ),
        "dual_vs_closed": (
            dual,
            15,
            1,
            {15: {15: 99, 3: 1386, 2: 8316}},
        ),
        "image_vs_closed": (
            image,
            15,
            0,
            {14: {14: 99, 2: 9702}},
        ),
        "dual_vs_neighborhood": (
            dual,
            14,
            0,
            {15: {14: 99, 2: 9702}},
        ),
    }
    systems = {}
    failures = []
    for name, (coefficients, root_weight, odd_multiplier, forced) in specifications.items():
        if name not in tables:
            systems[name] = {
                "pass": False,
                "failures": ["missing split system"],
            }
        else:
            systems[name] = audit_one_split(
                tables[name],
                coefficients,
                root_weight,
                odd_multiplier,
                forced,
            )
        if not systems[name]["pass"]:
            failures.append(name)
    return {"pass": not failures, "failures": failures, "systems": systems}


def audit_pair_tables(payload: dict[str, Any]) -> dict[str, Any]:
    observed = payload.get("distinguished_pair_tables")
    return {
        "pass": observed == EXPECTED_PAIR_TABLES,
        "observed": observed,
        "expected": EXPECTED_PAIR_TABLES,
    }


def find_exact_witnesses(discovery_dir: Path) -> list[Path]:
    """Find branch witnesses without trusting discovery status metadata."""
    candidates = []
    for path in sorted(discovery_dir.glob("binary-*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if payload.get("format") != "wave137-binary-arf-branch-v1":
            continue
        if payload.get("classification") != "EXACT_RATIONAL_FEASIBLE":
            continue
        try:
            coefficient_arrays(payload)
        except (KeyError, TypeError, ValueError):
            continue
        candidates.append(path)
    return candidates


def audit_witness(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    image, dual = coefficient_arrays(payload)
    ordinary = audit_ordinary(image, dual)
    signed = audit_signed_rows(image, dual, payload)
    split = audit_split_systems(payload, image, dual)
    pairs = audit_pair_tables(payload)
    passed = ordinary["pass"] and signed["pass"] and split["pass"] and pairs["pass"]
    return {
        "path": str(path),
        "sha256": sha256(path),
        "pass": passed,
        "ordinary": ordinary,
        "signed_krawtchouk": signed,
        "split_systems": split,
        "pair_tables": pairs,
    }


def audit_z4_outputs(discovery_dir: Path) -> dict[str, Any]:
    """Inventory Z4 outputs while refusing numerical status as evidence."""
    artifacts = []
    numerical_statuses = []
    for path in sorted(discovery_dir.glob("*")):
        if not path.is_file():
            continue
        is_z4 = "z4" in path.name.lower()
        payload = None
        if path.suffix.lower() == ".json":
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                payload = None
            is_z4 = is_z4 or (
                isinstance(payload, dict)
                and "z4" in str(payload.get("format", "")).lower()
            )
        if not is_z4:
            continue
        item = {
            "path": str(path),
            "sha256": sha256(path),
            "size": path.stat().st_size,
        }
        artifacts.append(item)
        if isinstance(payload, dict):
            text = json.dumps(payload, sort_keys=True).lower()
            if any(token in text for token in ("optimal", "infeasible", "timeout", "unknown")):
                numerical_statuses.append(
                    {
                        "path": str(path),
                        "treatment": "INVENTORIED_ONLY_NOT_EVIDENCE",
                    }
                )
    return {
        "artifacts": artifacts,
        "numerical_statuses": numerical_statuses,
        "mathematical_inference_from_numerical_status": False,
        "exact_z4_branch_certificate_found": False,
    }


def audit_discovery_manifest(discovery_dir: Path) -> dict[str, Any]:
    manifest = discovery_dir / "package-manifest.sha256"
    failures = []
    entries = []
    for line_number, raw in enumerate(
        manifest.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not raw.strip():
            continue
        try:
            expected, relative = raw.split("  ", 1)
        except ValueError:
            failures.append(f"malformed manifest line {line_number}")
            continue
        path = discovery_dir.parents[1] / relative
        if not path.is_file():
            failures.append(f"missing manifest entry: {relative}")
            continue
        observed = sha256(path)
        if observed != expected:
            failures.append(f"hash mismatch: {relative}")
        entries.append(
            {
                "path": relative,
                "expected_sha256": expected,
                "observed_sha256": observed,
                "pass": observed == expected,
            }
        )
    return {
        "pass": not failures,
        "manifest_path": str(manifest),
        "manifest_sha256": sha256(manifest),
        "entry_count": len(entries),
        "entries": entries,
        "failures": failures,
    }


def audit_cumulative_stages(
    witnesses: list[dict[str, Any]], ranks: dict[str, Any]
) -> dict[str, Any]:
    expected = {
        "binary-global-minus.json": (-1, 0),
        "binary-global-plus.json": (1, 0),
        "binary-k1-minus.json": (-1, 1),
        "binary-k1-plus.json": (1, 1),
        "binary-k2-minus.json": (-1, 2),
        "binary-k2-plus.json": (1, 2),
        "binary-k3-minus.json": (-1, 3),
        "binary-k3-plus.json": (1, 3),
        "binary-k4-minus.json": (-1, 4),
        "binary-k4-plus.json": (1, 4),
        "binary-k5-minus.json": (-1, 5),
        "binary-k5-plus.json": (1, 5),
        "binary-shadow1-minus.json": (-1, 5),
        "binary-shadow1-plus.json": (1, 5),
    }
    observed_by_name = {
        Path(witness["path"]).name: witness for witness in witnesses
    }
    failures = []
    stages = []
    rank_by_degree = {
        row["through_signed_degree"]: row
        for row in ranks["cumulative_signed_ranks"]
    }
    for filename, (sign, degree) in expected.items():
        witness = observed_by_name.get(filename)
        if witness is None:
            failures.append(f"missing cumulative witness {filename}")
            continue
        signed = witness["signed_krawtchouk"]
        if signed["epsilon"] != sign or signed["max_moment"] != degree:
            failures.append(
                f"stage metadata mismatch for {filename}: "
                f"sign={signed['epsilon']}, degree={signed['max_moment']}"
            )
        rank_row = rank_by_degree[degree]
        if (
            rank_row["augmented_rank_plus"] != rank_row["rank"]
            or rank_row["augmented_rank_minus"] != rank_row["rank"]
        ):
            failures.append(f"augmented-rank inconsistency at degree {degree}")
        stages.append(
            {
                "filename": filename,
                "sign": sign,
                "through_signed_degree": degree,
                "coefficient_rank": rank_row["rank"],
                "augmented_rank_for_sign": rank_row[
                    "augmented_rank_plus" if sign > 0 else "augmented_rank_minus"
                ],
                "witness_pass": witness["pass"],
            }
        )
    unexpected = sorted(set(observed_by_name) - set(expected))
    if unexpected:
        failures.append(f"unexpected exact branch witnesses: {unexpected}")
    return {
        "pass": not failures,
        "stages": stages,
        "failures": failures,
        "rank_conclusion": (
            "Each signed row t=0..5 raises the exact equality rank by one; "
            "plus and minus augmented ranks match the coefficient ranks."
        ),
    }


def verify(discovery_dir: Path) -> dict[str, Any]:
    constants = independent_constant_derivation()
    ranks = ordinary_model_ranks()
    witnesses = [audit_witness(path) for path in find_exact_witnesses(discovery_dir)]
    manifest = audit_discovery_manifest(discovery_dir)
    stages = audit_cumulative_stages(witnesses, ranks)
    failures = [
        f"witness failed: {witness['path']}"
        for witness in witnesses
        if not witness["pass"]
    ]
    if not manifest["pass"]:
        failures.extend(manifest["failures"])
    if not stages["pass"]:
        failures.extend(stages["failures"])
    return {
        "format": "wave137-clean-room-verification-v1",
        "claim_label": "VERIFIED" if not failures else "REFUTED",
        "scope": (
            "Exact rational Wave132 ordinary/distinguished projection plus "
            "Arf and signed Krawtchouk rows t=0..5; not code or graph realization."
        ),
        "independent_reconstruction": {
            "signed_constants": constants,
            "ordinary_model_ranks": ranks,
        },
        "discovery_manifest_audit": manifest,
        "cumulative_stage_rank_audit": stages,
        "witnesses": witnesses,
        "z4_audit": audit_z4_outputs(discovery_dir),
        "failures": failures,
        "status": {
            "exact_branch_replay": "PASS" if not failures else "FAIL",
            "binary_code_constructed": False,
            "graph_constructed": False,
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "limitations": [
            "Rational split-enumerator witnesses do not construct a binary code.",
            "The four distinguished systems do not impose full genus-two compatibility.",
            "No Z4 numerical status is accepted as a certificate.",
            "Conway-99 remains UNKNOWN.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--discovery-dir",
        type=Path,
        default=Path("attempts/wave137-z4-arf-branches"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("verification/wave137-arf-krawtchouk/verification.json"),
    )
    args = parser.parse_args()
    result = verify(args.discovery_dir)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "claim_label": result["claim_label"],
        "failures": result["failures"],
        "witness_count": len(result["witnesses"]),
    }, sort_keys=True))
    if result["failures"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
