#!/usr/bin/env python3
"""Clean-room exact verifier for the Wave 53 bounded cut loop.

This module deliberately does not import any discovery module.  Exact claim
decisions use integers and fractions.Fraction only.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import itertools
import json
import math
import re
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "attempts" / "wave53-exact-cut-loop"
OUT_DIR = ROOT / "verification" / "wave53-exact-cut-loop"

PATHS = {
    "row_system": ROOT / "attempts/wave44-rooted-flags/row-system.json",
    "wave45_cuts": ROOT
    / "attempts/wave45-flag-moment/checkpoint-v1-seed0-17cuts-15witnesses.json",
    "wave45_coefficients": ROOT
    / "attempts/wave45-flag-moment/checkpoint-v1-moment-coefficients.json",
    "wave45_independent": ROOT
    / "verification/wave45-flag-moment/independent-results.json",
    "wave47_cuts": ROOT / "attempts/wave47-three-root-moment/cuts.json",
    "wave47_coefficients": ROOT
    / "attempts/wave47-three-root-moment/coefficients.json",
    "wave47_verification": ROOT
    / "verification/wave47-three-root-moment/verification-results.json",
    "wave49_coefficients": ROOT
    / "verification/wave49-five-root-moment/independent-coefficients.json",
    "wave49_scout": ROOT
    / "attempts/wave49-five-root-moment/combined-sdp-result.json",
    "wave51": ROOT
    / "verification/wave51-rankone-cut-relaxation/exact-result.json",
    "wave51_independent": ROOT
    / "verification/wave51-rankone-cut-relaxation-independent/verification-result.json",
    "wave53": SOURCE / "exact-result.json",
}

INTEGER_RE = re.compile(r"-?(?:0|[1-9][0-9]*)\Z")
FRACTION_RE = re.compile(r"(-?(?:0|[1-9][0-9]*))/([1-9][0-9]*)\Z")
HASH_RE = re.compile(r"[0-9a-f]{64}\Z")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def parse_fraction(value: Any) -> Fraction:
    """Parse the exact JSON scalar grammar; floats and booleans are forbidden."""
    if isinstance(value, bool):
        raise ValueError("booleans are not exact rational scalars")
    if isinstance(value, int):
        return Fraction(value)
    if not isinstance(value, str):
        raise ValueError(f"unsupported exact rational scalar: {type(value).__name__}")
    if INTEGER_RE.fullmatch(value):
        return Fraction(int(value))
    match = FRACTION_RE.fullmatch(value)
    if match:
        return Fraction(int(match.group(1)), int(match.group(2)))
    raise ValueError(f"noncanonical or approximate rational scalar: {value!r}")


def fraction_text(value: Fraction | int) -> str:
    value = Fraction(value)
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def lcm_many(values: Iterable[int]) -> int:
    result = 1
    for value in values:
        result = math.lcm(result, value)
    return result


def primitive_vector(values: Iterable[int]) -> tuple[int, ...]:
    values = tuple(int(value) for value in values)
    divisor = math.gcd(*(abs(value) for value in values))
    if divisor == 0:
        raise ValueError("zero vector has no primitive normalization")
    values = tuple(value // divisor for value in values)
    first = next(value for value in values if value)
    if first < 0:
        values = tuple(-value for value in values)
    return values


def integerize_vector(values: Iterable[Fraction]) -> tuple[int, ...]:
    values = tuple(Fraction(value) for value in values)
    multiplier = lcm_many(value.denominator for value in values)
    return primitive_vector(value.numerator * (multiplier // value.denominator) for value in values)


def normalize_cut(
    constant: int, coefficients: dict[int, int]
) -> tuple[int, tuple[tuple[int, int], ...], int]:
    coefficients = {int(k): int(v) for k, v in coefficients.items() if int(v)}
    divisor = math.gcd(abs(int(constant)), *(abs(value) for value in coefficients.values()))
    if divisor == 0:
        raise ValueError("identically zero cut")
    # Inequality orientation is semantic.  Divide only by a positive gcd.
    normalized_constant = int(constant) // divisor
    normalized_coefficients = tuple(
        sorted((mask, value // divisor) for mask, value in coefficients.items())
    )
    return normalized_constant, normalized_coefficients, divisor


def cut_key(cut: dict[str, Any]) -> tuple[int, tuple[tuple[int, int], ...]]:
    constant, coefficients, _ = normalize_cut(cut["constant"], cut["coefficients"])
    return constant, coefficients


def cut_key_sha256(
    key: tuple[int, tuple[tuple[int, int], ...]]
) -> str:
    constant, coefficients = key
    return canonical_sha256(
        {"constant": constant, "coefficients": [list(item) for item in coefficients]}
    )


def cut_value(cut: dict[str, Any], witness: dict[int, Fraction]) -> Fraction:
    return Fraction(cut["constant"]) + sum(
        Fraction(coefficient) * witness.get(mask, Fraction())
        for mask, coefficient in cut["coefficients"].items()
    )


def physical_memory() -> dict[str, Any]:
    class MEMORYSTATUSEX(ctypes.Structure):
        _fields_ = [
            ("dwLength", ctypes.c_ulong),
            ("dwMemoryLoad", ctypes.c_ulong),
            ("ullTotalPhys", ctypes.c_ulonglong),
            ("ullAvailPhys", ctypes.c_ulonglong),
            ("ullTotalPageFile", ctypes.c_ulonglong),
            ("ullAvailPageFile", ctypes.c_ulonglong),
            ("ullTotalVirtual", ctypes.c_ulonglong),
            ("ullAvailVirtual", ctypes.c_ulonglong),
            ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
        ]

    status = MEMORYSTATUSEX()
    status.dwLength = ctypes.sizeof(status)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise OSError("GlobalMemoryStatusEx failed")
    percent = 100 * status.ullAvailPhys / status.ullTotalPhys
    return {
        "total_physical_bytes": status.ullTotalPhys,
        "available_physical_bytes": status.ullAvailPhys,
        "free_percent": round(percent, 6),
        "at_least_15_percent_free": percent >= 15.0,
    }


def edge_order(order: int) -> tuple[tuple[int, int], ...]:
    # The project encoding is Python itertools.combinations lexicographic order.
    return tuple(itertools.combinations(range(order), 2))


@lru_cache(maxsize=None)
def permutation_maps(order: int) -> tuple[tuple[int, ...], ...]:
    edges = edge_order(order)
    indices = {edge: index for index, edge in enumerate(edges)}
    maps = []
    for permutation in itertools.permutations(range(order)):
        maps.append(
            tuple(
                indices[tuple(sorted((permutation[left], permutation[right])))]
                for left, right in edges
            )
        )
    return tuple(maps)


@lru_cache(maxsize=None)
def canonical_mask(mask: int, order: int) -> int:
    best: int | None = None
    for mapping in permutation_maps(order):
        image = 0
        remaining = mask
        while remaining:
            low = remaining & -remaining
            source_bit = low.bit_length() - 1
            image |= 1 << mapping[source_bit]
            remaining ^= low
        if best is None or image < best:
            best = image
    assert best is not None
    return best


@lru_cache(maxsize=None)
def induced_canonical_mask(
    order7_mask: int, subset: tuple[int, ...]
) -> int:
    positions = {vertex: index for index, vertex in enumerate(subset)}
    target_edges = edge_order(len(subset))
    target_indices = {edge: index for index, edge in enumerate(target_edges)}
    induced = 0
    for source_bit, (left, right) in enumerate(edge_order(7)):
        if (
            (order7_mask >> source_bit) & 1
            and left in positions
            and right in positions
        ):
            target_edge = tuple(sorted((positions[left], positions[right])))
            induced |= 1 << target_indices[target_edge]
    return canonical_mask(induced, len(subset))


def deck_profiles(
    classes: tuple[int, ...], orders: tuple[int, ...] = (4, 5, 6)
) -> dict[int, dict[int, Counter[int]]]:
    profiles: dict[int, dict[int, Counter[int]]] = {}
    for order in orders:
        profiles[order] = {}
        subsets = tuple(itertools.combinations(range(7), order))
        for graph_mask in classes:
            profiles[order][graph_mask] = Counter(
                induced_canonical_mask(graph_mask, subset) for subset in subsets
            )
    return profiles


def lower_deck(
    witness: dict[int, Fraction],
    classes: tuple[int, ...],
    profiles: dict[int, dict[int, Counter[int]]],
) -> dict[int, dict[int, Fraction]]:
    counts: dict[int, dict[int, Fraction]] = {
        7: {mask: witness.get(mask, Fraction()) for mask in classes}
    }
    for order, graph_profiles in profiles.items():
        denominator = math.comb(99 - order, 7 - order)
        order_counts: dict[int, Fraction] = {}
        for graph_mask, value in counts[7].items():
            if not value:
                continue
            for lower_mask, multiplicity in graph_profiles[graph_mask].items():
                order_counts[lower_mask] = (
                    order_counts.get(lower_mask, Fraction())
                    + value * multiplicity / denominator
                )
        counts[order] = order_counts
    return counts


def empty_matrix(dimension: int) -> list[list[Fraction]]:
    return [
        [Fraction() for _ in range(dimension)] for _ in range(dimension)
    ]


def add_upper_records(
    matrix: list[list[Fraction]],
    records: Iterable[dict[str, Any]],
    counts: dict[int, dict[int, Fraction]],
    entries_key: str = "upper_entries",
) -> None:
    dimension = len(matrix)
    seen_classes: set[tuple[int, int]] = set()
    for record in records:
        order = int(record["order"])
        mask = int(record["canonical_mask"])
        class_key = (order, mask)
        if class_key in seen_classes:
            raise ValueError(f"duplicate coefficient class record {class_key}")
        seen_classes.add(class_key)
        count = counts[order].get(mask, Fraction())
        seen_entries: set[tuple[int, int]] = set()
        for left, right, coefficient in record[entries_key]:
            left, right, coefficient = int(left), int(right), int(coefficient)
            if not (0 <= left <= right < dimension):
                raise ValueError("invalid upper-triangle coordinate")
            if (left, right) in seen_entries:
                raise ValueError("duplicate upper-triangle coordinate")
            seen_entries.add((left, right))
            matrix[left][right] += coefficient * count
            if left != right:
                matrix[right][left] += coefficient * count


def build_matrices(
    counts: dict[int, dict[int, Fraction]],
    wave45: dict[str, Any],
    wave47: dict[str, Any],
    wave49: dict[str, Any],
) -> dict[tuple[str, str], list[list[Fraction]]]:
    result: dict[tuple[str, str], list[list[Fraction]]] = {}
    wave45_names = {
        "ordered_edge": "edge",
        "ordered_nonedge": "nonedge",
        "vertex": "vertex",
    }
    for source_name, report_name in wave45_names.items():
        family = wave45["families"][source_name]
        matrix = empty_matrix(int(family["matrix_size"]))
        add_upper_records(matrix, family["class_coefficients"], counts)
        result[("wave45", report_name)] = matrix
    for name, family in wave47["families"].items():
        matrix = empty_matrix(int(family["matrix_size"]))
        add_upper_records(matrix, family["class_coefficients"], counts)
        result[("wave47", name)] = matrix
    roots_seen: set[int] = set()
    for family in wave49["families"]:
        root = int(family["root_mask"])
        if root in roots_seen:
            raise ValueError(f"duplicate Wave49 root family {root}")
        roots_seen.add(root)
        matrix = empty_matrix(int(family["dimension"]))
        for order in (6, 7):
            records = [
                {**record, "order": order} for record in family[f"order{order}"]
            ]
            add_upper_records(matrix, records, counts)
        result[("wave49", f"root_{root}")] = matrix
    return result


def quadratic(
    matrix: list[list[Fraction]], vector: Iterable[int | Fraction]
) -> Fraction:
    vector = tuple(Fraction(value) for value in vector)
    if len(matrix) != len(vector):
        raise ValueError("quadratic dimension mismatch")
    return sum(
        vector[left] * matrix[left][right] * vector[right]
        for left in range(len(vector))
        for right in range(len(vector))
    )


def matrix_semantic_sha256(matrix: list[list[Fraction]]) -> str:
    upper = [
        [left, right, fraction_text(matrix[left][right])]
        for left in range(len(matrix))
        for right in range(left, len(matrix))
        if matrix[left][right]
    ]
    return canonical_sha256({"dimension": len(matrix), "upper_entries": upper})


def sign_directions(
    matrix: list[list[Fraction]],
) -> tuple[tuple[int, ...] | None, tuple[int, ...] | None]:
    """Return primitive exact positive and negative quadratic directions.

    The congruence elimination operates on a changing rational basis.  Each
    nonzero diagonal pivot records a sign witness.  A zero-diagonal block with
    a nonzero off-diagonal entry immediately supplies both signs.
    """
    order = len(matrix)
    gram = [[Fraction(value) for value in row] for row in matrix]
    basis = [
        [Fraction(int(index == coordinate)) for coordinate in range(order)]
        for index in range(order)
    ]
    positive: tuple[int, ...] | None = None
    negative: tuple[int, ...] | None = None

    while gram and (positive is None or negative is None):
        size = len(gram)
        pivot_index = next(
            (index for index in range(size) if gram[index][index] != 0), None
        )
        if pivot_index is None:
            off = next(
                (
                    (left, right)
                    for left in range(size)
                    for right in range(left + 1, size)
                    if gram[left][right] != 0
                ),
                None,
            )
            if off is None:
                break
            left, right = off
            plus = [basis[left][k] + basis[right][k] for k in range(order)]
            minus = [basis[left][k] - basis[right][k] for k in range(order)]
            q_plus = quadratic(matrix, plus)
            q_minus = quadratic(matrix, minus)
            for candidate, value in ((plus, q_plus), (minus, q_minus)):
                if value > 0 and positive is None:
                    positive = integerize_vector(candidate)
                if value < 0 and negative is None:
                    negative = integerize_vector(candidate)
            break

        if pivot_index != 0:
            gram[0], gram[pivot_index] = gram[pivot_index], gram[0]
            for row in gram:
                row[0], row[pivot_index] = row[pivot_index], row[0]
            basis[0], basis[pivot_index] = basis[pivot_index], basis[0]

        pivot = gram[0][0]
        direction = integerize_vector(basis[0])
        if pivot > 0 and positive is None:
            positive = direction
        if pivot < 0 and negative is None:
            negative = direction

        new_basis = []
        for index in range(1, size):
            coefficient = gram[0][index] / pivot
            new_basis.append(
                [
                    basis[index][coordinate] - coefficient * basis[0][coordinate]
                    for coordinate in range(order)
                ]
            )
        new_gram = [
            [
                gram[left + 1][right + 1]
                - gram[0][left + 1] * gram[0][right + 1] / pivot
                for right in range(size - 1)
            ]
            for left in range(size - 1)
        ]
        gram, basis = new_gram, new_basis

    if positive is not None and quadratic(matrix, positive) <= 0:
        raise AssertionError("invalid positive congruence direction")
    if negative is not None and quadratic(matrix, negative) >= 0:
        raise AssertionError("invalid negative congruence direction")
    return positive, negative


def record_quadratic_coefficients(
    records: Iterable[dict[str, Any]], vector: tuple[int, ...]
) -> dict[tuple[int, int], int]:
    result: dict[tuple[int, int], int] = {}
    for record in records:
        order, mask = int(record["order"]), int(record["canonical_mask"])
        coefficient = 0
        for left, right, entry in record["upper_entries"]:
            factor = 1 if left == right else 2
            coefficient += (
                factor * int(entry) * vector[int(left)] * vector[int(right)]
            )
        if coefficient:
            result[(order, mask)] = coefficient
    return result


def lift_quadratic_to_order7_cut(
    records: Iterable[dict[str, Any]],
    vector: Iterable[int],
    classes: tuple[int, ...],
    profiles: dict[int, dict[int, Counter[int]]],
) -> dict[str, Any]:
    vector = primitive_vector(vector)
    records = tuple(records)
    coefficients_by_class = record_quadratic_coefficients(records, vector)
    rational_row: dict[int, Fraction] = {mask: Fraction() for mask in classes}
    orders = {order for order, _ in coefficients_by_class}
    for graph_mask in classes:
        value = Fraction()
        for (order, lower_mask), coefficient in coefficients_by_class.items():
            if order == 7:
                multiplicity = int(lower_mask == graph_mask)
                denominator = 1
            else:
                multiplicity = profiles[order][graph_mask].get(lower_mask, 0)
                denominator = math.comb(99 - order, 7 - order)
            value += Fraction(coefficient * multiplicity, denominator)
        rational_row[graph_mask] = value
    denominator_lcm = lcm_many(value.denominator for value in rational_row.values())
    integer_row = {
        mask: value.numerator * (denominator_lcm // value.denominator)
        for mask, value in rational_row.items()
        if value
    }
    _, normalized, divisor = normalize_cut(0, integer_row)
    return {
        "constant": 0,
        "coefficients": dict(normalized),
        "direction": vector,
        "lower_deck_denominator_lcm": denominator_lcm,
        "primitive_coefficient_divisor": divisor,
        "linearization_multiplier": Fraction(denominator_lcm, divisor),
    }


def wave45_cut_records(data: dict[str, Any]) -> list[dict[str, Any]]:
    cuts = []
    for source in data["cuts"]:
        cut = {
            "layer": "wave45",
            "id": source["cut_sha256"],
            "constant": int(source["constant"]),
            "coefficients": {
                int(item["canonical_mask"]): int(item["coefficient"])
                for item in source["coefficients"]
            },
        }
        normalized_constant, normalized, _ = normalize_cut(
            cut["constant"], cut["coefficients"]
        )
        cut["constant"] = normalized_constant
        cut["coefficients"] = dict(normalized)
        cuts.append(cut)
    return cuts


def wave47_cut_records(data: dict[str, Any]) -> list[dict[str, Any]]:
    selected = [
        source for source in data["cuts"] if source["source_direction_index"] == 0
    ]
    pairs = {(source["source"], source["family"]) for source in selected}
    if len(selected) != 136 or len(pairs) != 136:
        raise ValueError("Wave47 fixed selection is not 136 source/family pairs")
    cuts = []
    for source in selected:
        cut = {
            "layer": "wave47",
            "id": source["cut_sha256"],
            "constant": int(source["constant"]),
            "coefficients": {
                int(item["canonical_mask"]): int(item["coefficient"])
                for item in source["coefficients"]
            },
        }
        normalized_constant, normalized, _ = normalize_cut(
            cut["constant"], cut["coefficients"]
        )
        cut["constant"] = normalized_constant
        cut["coefficients"] = dict(normalized)
        cuts.append(cut)
    return cuts


def wave49_cut_records(data: dict[str, Any]) -> list[dict[str, Any]]:
    candidates = data["solvers"][0]["candidate"]["wave49_families"]
    roots = [int(candidate["root_mask"]) for candidate in candidates]
    if len(candidates) != 21 or len(set(roots)) != 21:
        raise ValueError("Wave49 fixed selection is not 21 unique root families")
    cuts = []
    for candidate in candidates:
        source = candidate["candidate_minimum_direction_exact_cut"]
        coefficients = {
            int(mask): int(value)
            for mask, value in source["order7_count_coefficients"]
        }
        constant, normalized, _ = normalize_cut(
            int(source["constant_raw_numerator"]), coefficients
        )
        cuts.append(
            {
                "layer": "wave49",
                "id": source["payload_sha256_without_this_field"],
                "constant": constant,
                "coefficients": dict(normalized),
                "root_mask": int(candidate["root_mask"]),
            }
        )
    return cuts


def parse_manifest(path: Path) -> list[dict[str, str]]:
    entries = []
    seen: set[str] = set()
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line.strip():
            continue
        parts = line.split(maxsplit=1)
        if len(parts) != 2 or not HASH_RE.fullmatch(parts[0].lower()):
            raise ValueError(f"{path}:{line_number}: malformed manifest entry")
        relative = parts[1].replace("\\", "/")
        pure = Path(relative)
        if pure.is_absolute() or ".." in pure.parts:
            raise ValueError(f"{path}:{line_number}: unsafe manifest path")
        if relative in seen:
            raise ValueError(f"{path}:{line_number}: duplicate manifest path")
        seen.add(relative)
        entries.append({"path": relative, "expected_sha256": parts[0].lower()})
    return entries


def verify_manifest(path: Path, forbid_self: bool) -> dict[str, Any]:
    checks = []
    for entry in parse_manifest(path):
        target = ROOT / entry["path"]
        if forbid_self and target.resolve() == path.resolve():
            raise ValueError(f"{path}: self-referential manifest")
        actual = sha256_file(target) if target.is_file() else None
        checks.append({**entry, "actual_sha256": actual, "match": actual == entry["expected_sha256"]})
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "entry_count": len(checks),
        "all_match": all(check["match"] for check in checks),
        "checks": checks,
    }


def witness_from_report(
    report: dict[str, Any], classes: tuple[int, ...]
) -> tuple[dict[int, Fraction], Fraction]:
    support = report["support"]
    masks = [int(item["canonical_mask"]) for item in support]
    if masks != sorted(masks) or len(masks) != len(set(masks)):
        raise ValueError("witness support is not sorted and unique")
    if not set(masks) <= set(classes):
        raise ValueError("witness contains a noncanonical or unknown mask")
    witness = {
        int(item["canonical_mask"]): parse_fraction(item["value"])
        for item in support
    }
    return witness, parse_fraction(report["y_h11_over_4"])


def verify_wave44(
    row_system: dict[str, Any],
    witness: dict[int, Fraction],
    y: Fraction,
) -> dict[str, Any]:
    classes = tuple(int(mask) for mask in row_system["classes"])
    vector = [witness.get(mask, Fraction()) for mask in classes] + [y]
    residuals: list[Fraction] = []
    family_counts: dict[str, int] = {}
    for family_name in ("base", "edge", "nonedge", "vertex"):
        family = row_system["families"][family_name]
        family_counts[family_name] = len(family["rows"])
        if len(family["rows"]) != len(family["rhs"]):
            raise ValueError("row/RHS length mismatch")
        for row, rhs in zip(family["rows"], family["rhs"], strict=True):
            if len(row) != 209:
                raise ValueError("Wave44 row does not have 209 coefficients")
            residuals.append(
                sum(Fraction(coefficient) * value for coefficient, value in zip(row, vector, strict=True))
                - Fraction(rhs)
            )
    return {
        "equation_count": len(residuals),
        "family_counts": family_counts,
        "all_residuals_zero": all(residual == 0 for residual in residuals),
        "nonzero_residual_count": sum(residual != 0 for residual in residuals),
        "all_208_counts_nonnegative": all(value >= 0 for value in vector[:-1]),
        "support_size": sum(value != 0 for value in vector[:-1]),
        "zero_coordinates": sum(value == 0 for value in vector[:-1]),
        "y": fraction_text(y),
        "y_bounds_satisfied": Fraction(2079) <= y <= Fraction(4158),
    }


def coefficient_integrity(
    wave45: dict[str, Any],
    wave45_independent: dict[str, Any],
    wave47: dict[str, Any],
    wave49: dict[str, Any],
) -> dict[str, Any]:
    wave45_equal = True
    wave45_mapping = {
        "ordered_edge": "edge",
        "ordered_nonedge": "nonedge",
        "vertex": "vertex",
    }
    for discovery_name, verifier_name in wave45_mapping.items():
        discovery_family = wave45["families"][discovery_name]
        independent_records = wave45_independent["coefficient_streams"][verifier_name]
        expanded = []
        for record in discovery_family["class_coefficients"]:
            entries = []
            for left, right, coefficient in record["upper_entries"]:
                entries.append([left, right, coefficient])
                if left != right:
                    entries.append([right, left, coefficient])
            entries.sort()
            expanded.append(
                {
                    "canonical_mask": record["canonical_mask"],
                    "entries": entries,
                    "order": record["order"],
                }
            )
        wave45_equal &= (
            expanded == independent_records
            and discovery_family["flags"]
            == wave45_independent["flag_sets"][verifier_name]["canonical_masks"]
        )

    wave47_payload = dict(wave47)
    expected_wave47_hash = wave47_payload.pop("payload_sha256_without_this_field")
    wave47_hash = canonical_sha256(wave47_payload)

    wave49_family_hashes = []
    for family in wave49["families"]:
        payload = dict(family)
        expected = payload.pop("payload_sha256")
        actual = canonical_sha256(payload)
        wave49_family_hashes.append(
            {
                "root_mask": family["root_mask"],
                "expected": expected,
                "actual": actual,
                "match": expected == actual,
            }
        )
    wave49_payload = dict(wave49)
    expected_wave49_hash = wave49_payload.pop("payload_sha256_without_this_field")
    wave49_hash = canonical_sha256(wave49_payload)

    return {
        "wave45_independent_streams_exactly_equal": wave45_equal,
        "wave47_payload_self_hash": {
            "expected": expected_wave47_hash,
            "actual": wave47_hash,
            "match": expected_wave47_hash == wave47_hash,
        },
        "wave49_family_self_hashes": wave49_family_hashes,
        "wave49_payload_self_hash": {
            "expected": expected_wave49_hash,
            "actual": wave49_hash,
            "match": expected_wave49_hash == wave49_hash,
        },
    }


def strict_rational_parser_attacks() -> dict[str, Any]:
    accepted = {
        "0": fraction_text(parse_fraction("0")),
        "-7": fraction_text(parse_fraction("-7")),
        "3/4": fraction_text(parse_fraction("3/4")),
        "integer_5": fraction_text(parse_fraction(5)),
    }
    rejected_values: list[Any] = [
        True,
        False,
        1.0,
        float("nan"),
        "1.0",
        "1e-3",
        "1/0",
        "01",
        "+1",
        " 1",
        "1/-2",
    ]
    rejected = []
    for value in rejected_values:
        try:
            parse_fraction(value)
        except (TypeError, ValueError, ZeroDivisionError):
            rejected.append(repr(value))
    return {
        "accepted": accepted,
        "rejection_cases": len(rejected_values),
        "all_nonexact_or_noncanonical_cases_rejected": len(rejected)
        == len(rejected_values),
        "rejected": rejected,
    }


def verify() -> dict[str, Any]:
    memory_start = physical_memory()
    data = {name: load_json(path) for name, path in PATHS.items()}
    row_system = data["row_system"]
    wave53 = data["wave53"]
    classes = tuple(int(mask) for mask in row_system["classes"])
    if len(classes) != 208 or len(set(classes)) != 208:
        raise ValueError("Wave44 class stream is not 208 unique masks")
    if any(canonical_mask(mask, 7) != mask for mask in classes):
        raise ValueError("Wave44 class stream contains a noncanonical mask")

    profiles = deck_profiles(classes)
    baseline_cuts = (
        wave45_cut_records(data["wave45_cuts"])
        + wave47_cut_records(data["wave47_cuts"])
        + wave49_cut_records(data["wave49_scout"])
    )
    baseline_layer_counts = Counter(cut["layer"] for cut in baseline_cuts)
    baseline_keys = [cut_key(cut) for cut in baseline_cuts]
    duplicate_baseline_cuts = len(baseline_keys) - len(set(baseline_keys))
    baseline_duplicate_groups = []
    baseline_key_groups: dict[
        tuple[int, tuple[tuple[int, int], ...]], list[dict[str, Any]]
    ] = {}
    for cut, key in zip(baseline_cuts, baseline_keys, strict=True):
        baseline_key_groups.setdefault(key, []).append(
            {"layer": cut["layer"], "id": cut["id"]}
        )
    for key, group in baseline_key_groups.items():
        if len(group) > 1:
            baseline_duplicate_groups.append(
                {
                    "normalized_cut_sha256": cut_key_sha256(key),
                    "multiplicity": len(group),
                    "members": group,
                }
            )
    baseline_duplicate_groups.sort(key=lambda item: item["normalized_cut_sha256"])

    wave51_support = data["wave51"]["exact_certificate"]["support"]
    wave51_witness = {
        int(item["canonical_mask"]): parse_fraction(item["value"])
        for item in wave51_support
    }

    expected_families = (
        {("wave45", family) for family in ("edge", "nonedge", "vertex")}
        | {("wave47", family) for family in data["wave47_coefficients"]["families"]}
        | {
            ("wave49", f"root_{int(family['root_mask'])}")
            for family in data["wave49_coefficients"]["families"]
        }
    )

    iteration_results = []
    selected_cuts: list[dict[str, Any]] = []
    correction_catalog: list[dict[str, Any]] = []
    all_matrix_checks = 0
    exact_indefinite_checks = 0
    exact_psd_checks = 0
    reported_quadratic_matches = 0
    reported_status_matches = 0

    for iteration in wave53["iterations"]:
        index = int(iteration["iteration"])
        report_witness = iteration["witness"]
        witness, y = witness_from_report(report_witness, classes)
        wave44_check = verify_wave44(row_system, witness, y)
        deck = lower_deck(witness, classes, profiles)
        deck_totals = {
            str(order): fraction_text(sum(order_counts.values()))
            for order, order_counts in deck.items()
        }
        deck_total_checks = {
            str(order): sum(order_counts.values()) == math.comb(99, order)
            for order, order_counts in deck.items()
        }

        cuts = baseline_cuts + selected_cuts
        slacks = [cut_value(cut, witness) for cut in cuts]
        positive_slacks = [slack for slack in slacks if slack > 0]
        cut_check = {
            "cut_count": len(cuts),
            "all_nonnegative": all(slack >= 0 for slack in slacks),
            "tight_count": sum(slack == 0 for slack in slacks),
            "strictly_positive_count": sum(slack > 0 for slack in slacks),
            "minimum_positive_slack": (
                fraction_text(min(positive_slacks)) if positive_slacks else None
            ),
        }

        matrices = build_matrices(
            deck,
            data["wave45_coefficients"],
            data["wave47_coefficients"],
            data["wave49_coefficients"],
        )
        records = iteration["matrix_evaluation"]["records"]
        reported_keys = [
            (str(record["layer"]), str(record["family"])) for record in records
        ]
        coverage = {
            "reported_record_count": len(records),
            "reported_unique_keys": len(set(reported_keys)),
            "expected_key_count": len(expected_families),
            "missing_keys": sorted(expected_families - set(reported_keys)),
            "unexpected_keys": sorted(set(reported_keys) - expected_families),
            "duplicate_keys": sorted(
                key for key, count in Counter(reported_keys).items() if count > 1
            ),
        }
        if set(matrices) != expected_families:
            raise AssertionError("independent matrix family construction is incomplete")

        matrix_results = []
        candidate_cuts: list[dict[str, Any]] = []
        for record in records:
            key = (str(record["layer"]), str(record["family"]))
            matrix = matrices[key]
            direction = tuple(int(value) for value in record["primitive_integer_direction"])
            primitive = primitive_vector(direction)
            direction_is_primitive_canonical = direction == primitive
            exact_q = quadratic(matrix, direction)
            reported_q = parse_fraction(record["exact_quadratic"])
            positive_direction, negative_direction = sign_directions(matrix)
            positive_q = (
                quadratic(matrix, positive_direction)
                if positive_direction is not None
                else None
            )
            negative_q = (
                quadratic(matrix, negative_direction)
                if negative_direction is not None
                else None
            )
            independently_indefinite = (
                positive_q is not None
                and positive_q > 0
                and negative_q is not None
                and negative_q < 0
            )
            independently_psd = positive_q is not None and negative_q is None
            all_matrix_checks += 1
            exact_indefinite_checks += int(independently_indefinite)
            exact_psd_checks += int(independently_psd)
            reported_quadratic_matches += int(exact_q == reported_q)
            status_matches = (
                record["status"] == "EXACTLY_INDEFINITE"
                and independently_indefinite
            )
            reported_status_matches += int(status_matches)

            matrix_result = {
                "layer": key[0],
                "family": key[1],
                "dimension": len(matrix),
                "correct_matrix_semantic_sha256": matrix_semantic_sha256(matrix),
                "reported_matrix_sha256": record["matrix_sha256"],
                "reported_direction_is_primitive_and_canonical": direction_is_primitive_canonical,
                "reported_direction_exact_quadratic_correct_matrix": fraction_text(exact_q),
                "reported_exact_quadratic": fraction_text(reported_q),
                "reported_quadratic_matches_correct_matrix": exact_q == reported_q,
                "independent_positive_direction": (
                    list(positive_direction) if positive_direction is not None else None
                ),
                "independent_positive_quadratic": (
                    fraction_text(positive_q) if positive_q is not None else None
                ),
                "independent_negative_direction": (
                    list(negative_direction) if negative_direction is not None else None
                ),
                "independent_negative_quadratic": (
                    fraction_text(negative_q) if negative_q is not None else None
                ),
                "independent_status": (
                    "EXACTLY_INDEFINITE"
                    if independently_indefinite
                    else "EXACTLY_PSD"
                    if independently_psd
                    else "EXACTLY_NEGATIVE_SEMIDEFINITE_OR_ZERO"
                ),
                "reported_status_matches": status_matches,
            }
            matrix_results.append(matrix_result)
            if exact_q != reported_q or not status_matches:
                correction_catalog.append(
                    {
                        "iteration": index,
                        "layer": key[0],
                        "family": key[1],
                        "reported_exact_quadratic": fraction_text(reported_q),
                        "correct_exact_quadratic_for_reported_direction": fraction_text(exact_q),
                        "reported_status": record["status"],
                        "correct_status": matrix_result["independent_status"],
                    }
                )

            if key[0] == "wave45":
                source_name = {
                    "edge": "ordered_edge",
                    "nonedge": "ordered_nonedge",
                    "vertex": "vertex",
                }[key[1]]
                family = data["wave45_coefficients"]["families"][source_name]
                records_for_cut = family["class_coefficients"]
            elif key[0] == "wave47":
                records_for_cut = data["wave47_coefficients"]["families"][key[1]][
                    "class_coefficients"
                ]
            else:
                root = int(key[1].split("_", 1)[1])
                family = next(
                    item
                    for item in data["wave49_coefficients"]["families"]
                    if int(item["root_mask"]) == root
                )
                records_for_cut = tuple(
                    {**item, "order": order}
                    for order in (6, 7)
                    for item in family[f"order{order}"]
                )
            lifted = lift_quadratic_to_order7_cut(
                records_for_cut, direction, classes, profiles
            )
            lifted.update(
                {
                    "layer": key[0],
                    "family": key[1],
                    "source_value": cut_value(lifted, witness),
                    "exact_q": exact_q,
                    "selection_score": exact_q
                    / (
                        sum(value * value for value in direction)
                        * max(
                            Fraction(1),
                            sum(abs(matrix[i][i]) for i in range(len(matrix))),
                        )
                    ),
                }
            )
            candidate_cuts.append(lifted)

        candidate_keys = [cut_key(cut) for cut in candidate_cuts]
        cumulative_keys = set(cut_key(cut) for cut in cuts)
        duplicate_candidate_pairs = len(candidate_keys) - len(set(candidate_keys))
        duplicate_against_cumulative = sum(key in cumulative_keys for key in candidate_keys)
        candidate_key_groups: dict[
            tuple[int, tuple[tuple[int, int], ...]], list[dict[str, str]]
        ] = {}
        for cut, key in zip(candidate_cuts, candidate_keys, strict=True):
            candidate_key_groups.setdefault(key, []).append(
                {"layer": cut["layer"], "family": cut["family"]}
            )
        candidate_duplicate_groups = [
            {
                "normalized_cut_sha256": cut_key_sha256(key),
                "multiplicity": len(group),
                "members": group,
            }
            for key, group in candidate_key_groups.items()
            if len(group) > 1
        ]
        candidate_duplicate_groups.sort(
            key=lambda item: item["normalized_cut_sha256"]
        )
        eligible = [
            cut
            for cut in candidate_cuts
            if cut["source_value"] < 0 and cut_key(cut) not in cumulative_keys
        ]
        selected_by_exact_rule = (
            min(
                eligible,
                key=lambda cut: (
                    cut["selection_score"],
                    cut["layer"],
                    cut["family"],
                ),
            )
            if eligible
            else None
        )

        added_cut_check = None
        if "added_cut" in iteration:
            source_added = iteration["added_cut"]
            source_coefficients = {
                int(mask): int(value) for mask, value in source_added["coefficients"]
            }
            source_constant, source_normalized, source_divisor = normalize_cut(
                int(source_added["constant"]), source_coefficients
            )
            source_cut = {
                "layer": source_added["layer"],
                "family": source_added["family"],
                "id": source_added["id"],
                "constant": source_constant,
                "coefficients": dict(source_normalized),
            }
            selected_key = (
                str(source_added["layer"]),
                str(source_added["family"]),
            )
            reconstructed = next(
                cut
                for cut in candidate_cuts
                if (cut["layer"], cut["family"]) == selected_key
            )
            source_value = cut_value(source_cut, witness)
            added_cut_check = {
                "selected_layer": selected_key[0],
                "selected_family": selected_key[1],
                "reported_id": source_added["id"],
                "source_coefficients_were_primitive": source_divisor == 1,
                "reconstructed_coefficients_equal": cut_key(source_cut)
                == cut_key(reconstructed),
                "direction_equal": tuple(source_added["direction"])
                == reconstructed["direction"],
                "lower_deck_denominator_lcm_equal": int(
                    source_added["lower_deck_denominator_lcm"]
                )
                == reconstructed["lower_deck_denominator_lcm"],
                "primitive_coefficient_divisor_equal": int(
                    source_added["primitive_coefficient_divisor"]
                )
                == reconstructed["primitive_coefficient_divisor"],
                "linearization_multiplier_equal": parse_fraction(
                    source_added["linearization_multiplier"]
                )
                == reconstructed["linearization_multiplier"],
                "reported_matrix_value_equal": parse_fraction(
                    source_added["exact_matrix_value"]
                )
                == reconstructed["exact_q"],
                "reported_source_value_equal": parse_fraction(
                    source_added["exact_source_value"]
                )
                == source_value,
                "exact_source_value": fraction_text(source_value),
                "exactly_rejects_source": source_value < 0,
                "selected_by_correct_exact_rule": selected_by_exact_rule is not None
                and (
                    selected_by_exact_rule["layer"],
                    selected_by_exact_rule["family"],
                )
                == selected_key,
                "independent_selected_layer": (
                    selected_by_exact_rule["layer"]
                    if selected_by_exact_rule is not None
                    else None
                ),
                "independent_selected_family": (
                    selected_by_exact_rule["family"]
                    if selected_by_exact_rule is not None
                    else None
                ),
                "independent_selected_score": (
                    fraction_text(selected_by_exact_rule["selection_score"])
                    if selected_by_exact_rule is not None
                    else None
                ),
            }
            selected_cuts.append(source_cut)

        wave45_matrix_results = [
            result for result in matrix_results if result["layer"] == "wave45"
        ]
        iteration_results.append(
            {
                "iteration": index,
                "witness": {
                    **wave44_check,
                    "reported_support_size": report_witness["support_size"],
                    "support_size_matches": wave44_check["support_size"]
                    == report_witness["support_size"],
                    "deck_totals": deck_totals,
                    "deck_totals_equal_binomial_99": deck_total_checks,
                    "is_wave51_exact_witness": witness == wave51_witness,
                },
                "cuts": cut_check,
                "matrix_coverage": coverage,
                "matrix_summary": {
                    "checked": len(matrix_results),
                    "reported_quadratics_matching_correct_matrices": sum(
                        item["reported_quadratic_matches_correct_matrix"]
                        for item in matrix_results
                    ),
                    "independently_indefinite": sum(
                        item["independent_status"] == "EXACTLY_INDEFINITE"
                        for item in matrix_results
                    ),
                    "independently_psd": sum(
                        item["independent_status"] == "EXACTLY_PSD"
                        for item in matrix_results
                    ),
                    "wave45": wave45_matrix_results,
                },
                "candidate_normalization_attacks": {
                    "candidate_count": len(candidate_cuts),
                    "candidate_cut_key_duplicates": duplicate_candidate_pairs,
                    "candidate_duplicate_groups": candidate_duplicate_groups,
                    "duplicates_against_cumulative_cuts": duplicate_against_cumulative,
                    "exactly_rejecting_nonduplicate_candidates": len(eligible),
                },
                "added_cut": added_cut_check,
            }
        )

    final_witness_check = iteration_results[-1]["witness"]
    final_cut_check = iteration_results[-1]["cuts"]
    terminal_wave45_vertex = next(
        result
        for result in iteration_results[-1]["matrix_summary"]["wave45"]
        if result["family"] == "vertex"
    )
    terminal_source_record = next(
        record
        for record in wave53["iterations"][-1]["matrix_evaluation"]["records"]
        if record["layer"] == "wave45" and record["family"] == "vertex"
    )
    terminal_deck = lower_deck(
        witness_from_report(wave53["iterations"][-1]["witness"], classes)[0],
        classes,
        profiles,
    )
    terminal_vertex_family = data["wave45_coefficients"]["families"]["vertex"]
    fourth_cut = lift_quadratic_to_order7_cut(
        terminal_vertex_family["class_coefficients"],
        terminal_source_record["primitive_integer_direction"],
        classes,
        profiles,
    )
    terminal_witness = witness_from_report(
        wave53["iterations"][-1]["witness"], classes
    )[0]
    fourth_cut_value = cut_value(fourth_cut, terminal_witness)
    fourth_correct_matrix = build_matrices(
        terminal_deck,
        data["wave45_coefficients"],
        data["wave47_coefficients"],
        data["wave49_coefficients"],
    )[("wave45", "vertex")]
    fourth_correct_q = quadratic(
        fourth_correct_matrix, terminal_source_record["primitive_integer_direction"]
    )

    manifests = [
        verify_manifest(SOURCE / "input-freeze.sha256", forbid_self=False),
        verify_manifest(SOURCE / "package-manifest.sha256", forbid_self=True),
    ]
    input_records = []
    for source in wave53["inputs"]:
        path = ROOT / source["path"]
        actual = sha256_file(path) if path.is_file() else None
        input_records.append(
            {
                "path": source["path"],
                "expected_sha256": source["sha256"],
                "actual_sha256": actual,
                "match": actual == source["sha256"],
            }
        )

    memory_finish = physical_memory()
    exact_feasibility = (
        final_witness_check["all_residuals_zero"]
        and final_witness_check["all_208_counts_nonnegative"]
        and final_witness_check["y_bounds_satisfied"]
        and final_cut_check["cut_count"] == 177
        and final_cut_check["all_nonnegative"]
    )
    return {
        "format": "wave53-exact-cut-loop-independent-verification-v1",
        "role": "verifier",
        "claim_label": "REFUTED_IN_PART",
        "scope": "clean-room exact replay of the fixed Wave53 four witnesses, 174-cut base, three added cuts, and 32 Wave45/Wave47/Wave49 moment families",
        "status_boundary": {
            "fixed_177_cut_rational_relaxation": (
                "VERIFIED_EXACTLY_FEASIBLE" if exact_feasibility else "NOT_VERIFIED"
            ),
            "all_128_reported_matrix_evaluations": (
                "VERIFIED"
                if reported_quadratic_matches == 128
                and exact_indefinite_checks == 128
                else "REFUTED"
            ),
            "endpoint_n3_4158": "UNKNOWN",
            "strict_upper_bound_below_4158": "NOT_PROVED",
            "integer_count_feasibility": "UNKNOWN",
            "graph_constructed": False,
            "Conway_99": "UNKNOWN",
        },
        "input_integrity": {
            "manifests": manifests,
            "all_manifest_entries_match": all(
                manifest["all_match"] for manifest in manifests
            ),
            "result_input_records": input_records,
            "all_result_input_records_match": all(
                record["match"] for record in input_records
            ),
        },
        "coefficient_integrity": coefficient_integrity(
            data["wave45_coefficients"],
            data["wave45_independent"],
            data["wave47_coefficients"],
            data["wave49_coefficients"],
        ),
        "baseline_174_cut_reconstruction": {
            "count": len(baseline_cuts),
            "layer_counts": dict(sorted(baseline_layer_counts.items())),
            "semantic_duplicate_count_after_primitive_normalization": duplicate_baseline_cuts,
            "semantic_duplicate_group_count": len(baseline_duplicate_groups),
            "semantic_duplicate_groups": baseline_duplicate_groups,
            "wave51_witness_support_size": len(wave51_witness),
            "wave51_witness_equals_wave53_iteration_0": iteration_results[0][
                "witness"
            ]["is_wave51_exact_witness"],
            "wave51_exact_substitution": {
                "wave44": {
                    key: iteration_results[0]["witness"][key]
                    for key in (
                        "equation_count",
                        "all_residuals_zero",
                        "all_208_counts_nonnegative",
                        "support_size",
                        "y",
                        "y_bounds_satisfied",
                    )
                },
                "cuts": iteration_results[0]["cuts"],
            },
        },
        "iterations": iteration_results,
        "matrix_totals": {
            "checks": all_matrix_checks,
            "reported_quadratics_matching_correct_matrices": reported_quadratic_matches,
            "reported_statuses_matching": reported_status_matches,
            "independently_indefinite": exact_indefinite_checks,
            "independently_psd": exact_psd_checks,
        },
        "corrections": correction_catalog,
        "excluded_fourth_dense_wave45_cut": {
            "identified_as_terminal_wave45_vertex_direction": True,
            "nonzero_coefficients": len(fourth_cut["coefficients"]),
            "correct_exact_quadratic": fraction_text(fourth_correct_q),
            "correct_exact_cut_value_at_terminal_witness": fraction_text(
                fourth_cut_value
            ),
            "reported_numerical_farkas_residual": "7.431e-10",
            "exact_farkas_multipliers_or_identity_present_in_package": False,
            "is_exact_farkas_certificate": False,
            "reason": "A nonzero floating residual is not exact coefficient cancellation; no exact nonnegative multiplier identity is supplied.  Moreover the correctly expanded Wave45 quadratic/cut is positive at the terminal witness.",
            "terminal_wave45_vertex_status": terminal_wave45_vertex[
                "independent_status"
            ],
        },
        "rational_parser_attacks": strict_rational_parser_attacks(),
        "resource_guard": {
            "required_free_physical_memory_percent": 15.0,
            "start": memory_start,
            "finish": memory_finish,
            "passed": memory_start["at_least_15_percent_free"]
            and memory_finish["at_least_15_percent_free"],
        },
        "limitations": [
            "The verified feasibility claim concerns one fixed finite rational aggregate relaxation only.",
            "The 32 supplied directions are not an exhaustive description of any PSD cone.",
            "No integer count vector or graph is constructed.",
            "The excluded fourth-cut Farkas data are not present as an exact multiplier certificate, so only rejection—not reconstruction of a nonexistent certificate—is possible.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--compact", action="store_true")
    arguments = parser.parse_args()
    result = verify()
    text = json.dumps(
        result,
        indent=None if arguments.compact else 2,
        sort_keys=True,
        separators=(",", ":") if arguments.compact else None,
    )
    if arguments.output:
        arguments.output.write_text(text + "\n", encoding="utf-8", newline="\n")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
