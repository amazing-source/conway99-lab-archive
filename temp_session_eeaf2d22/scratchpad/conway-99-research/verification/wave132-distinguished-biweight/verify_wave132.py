"""Independent solver-free verifier for sealed Wave132.

This file intentionally does not import or execute any Wave132 discovery or
checking code.  It reconstructs binary Krawtchouk transforms, distinguished
pair tables, split-enumerator moments, parity rules, range rules, and the
high-weight cut from the sealed JSON witness using only the standard library.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from fractions import Fraction as Q
from pathlib import Path


EXPECTED_MANIFEST_SHA256 = (
    "0b99e87b0f39b1c203709d34ffba3f7b5c94f0078c53fe4020dfc3cd03ec510c"
)
LENGTH = 99
IMAGE_DIMENSION = 54
DUAL_DIMENSION = 45


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_manifest(
    repository: Path, package: Path, expected_hash: str
) -> dict[str, object]:
    manifest = package / "package-manifest.sha256"
    actual_hash = sha256(manifest)
    failures: list[str] = []
    entries = 0
    for line in manifest.read_text(encoding="utf-8").splitlines():
        entries += 1
        try:
            expected, relative = line.split("  ", 1)
        except ValueError:
            failures.append(f"malformed:{line}")
            continue
        target = repository / Path(relative)
        if not target.is_file():
            failures.append(f"missing:{relative}")
        elif sha256(target) != expected:
            failures.append(f"hash:{relative}")
    return {
        "expected_sha256": expected_hash,
        "actual_sha256": actual_hash,
        "entries": entries,
        "failures": failures,
        "verified": actual_hash == expected_hash and not failures,
    }


def parse_input_freeze(
    repository: Path, package: Path
) -> dict[str, object]:
    failures: list[str] = []
    entries = 0
    for line in (package / "input-freeze.sha256").read_text(
        encoding="utf-8"
    ).splitlines():
        entries += 1
        try:
            expected, relative = line.split("  ", 1)
        except ValueError:
            failures.append(f"malformed:{line}")
            continue
        target = repository / Path(relative)
        if not target.is_file():
            failures.append(f"missing:{relative}")
        elif sha256(target) != expected:
            failures.append(f"hash:{relative}")
    return {
        "entries": entries,
        "failures": failures,
        "verified": not failures,
    }


def coefficients(source: dict[str, str]) -> list[Q]:
    result = [Q(0)] * (LENGTH + 1)
    for key, value in source.items():
        index = int(key)
        if not 0 <= index <= LENGTH:
            raise ValueError(f"weight outside 0..99: {index}")
        result[index] = Q(value)
    return result


def krawtchouk_table() -> list[list[int]]:
    table: list[list[int]] = []
    for degree in range(LENGTH + 1):
        row = []
        for weight in range(LENGTH + 1):
            value = 0
            for intersection in range(
                max(0, degree - (LENGTH - weight)),
                min(degree, weight) + 1,
            ):
                value += (
                    (-1) ** intersection
                    * math.comb(weight, intersection)
                    * math.comb(
                        LENGTH - weight, degree - intersection
                    )
                )
            row.append(value)
        table.append(row)
    return table


def ordinary_audit(
    image: list[Q], dual: list[Q], table: list[list[int]]
) -> dict[str, object]:
    forward_failures = []
    inverse_failures = []
    image_size = Q(2**IMAGE_DIMENSION)
    dual_size = Q(2**DUAL_DIMENSION)
    for degree in range(LENGTH + 1):
        expected_dual = (
            sum(
                image[weight] * table[degree][weight]
                for weight in range(LENGTH + 1)
            )
            / image_size
        )
        if expected_dual != dual[degree]:
            forward_failures.append(degree)
        expected_image = (
            sum(
                dual[weight] * table[degree][weight]
                for weight in range(LENGTH + 1)
            )
            / dual_size
        )
        if expected_image != image[degree]:
            inverse_failures.append(degree)

    forced_image = {
        14: 99,
        24: 4158,
        26: 693,
        30: 70686,
        32: 41580,
        34: 36036,
        36: 8547,
    }
    forced_dual = {
        15: 99,
        24: 693,
        26: 4158,
        31: 41580,
        33: 79002,
        35: 8316,
        37: 27720,
        39: 231,
    }
    forced_failures = [
        f"A{weight}"
        for weight, lower in forced_image.items()
        if image[weight] < lower
    ]
    forced_failures.extend(
        f"B{weight}"
        for weight, lower in forced_dual.items()
        if dual[weight] < lower
    )
    complement_failures = [
        weight
        for weight in range(LENGTH + 1)
        if dual[weight] != dual[LENGTH - weight]
    ]
    positive_image_weights = [
        weight for weight, value in enumerate(image) if value > 0
    ]
    positive_dual_weights = [
        weight for weight, value in enumerate(dual) if value > 0
    ]
    return {
        "forward_failures": forward_failures,
        "inverse_failures": inverse_failures,
        "forced_lower_bound_failures": forced_failures,
        "complement_symmetry_failures": complement_failures,
        "negative_image_weights": [
            weight for weight, value in enumerate(image) if value < 0
        ],
        "negative_dual_weights": [
            weight for weight, value in enumerate(dual) if value < 0
        ],
        "image_size": str(sum(image)),
        "dual_size": str(sum(dual)),
        "image_minimum_nonzero_weight": min(
            weight for weight in positive_image_weights if weight
        ),
        "dual_minimum_nonzero_weight": min(
            weight for weight in positive_dual_weights if weight
        ),
        "image_nonintegral_coefficient_count": sum(
            value.denominator != 1 for value in image
        ),
        "dual_nonintegral_coefficient_count": sum(
            value.denominator != 1 for value in dual
        ),
        "image_odd_support": [
            weight
            for weight, value in enumerate(image)
            if weight % 2 and value
        ],
        "all_200_rows_verified": (
            not forward_failures and not inverse_failures
        ),
        "verified": (
            not forward_failures
            and not inverse_failures
            and not forced_failures
            and not complement_failures
            and all(value >= 0 for value in image)
            and all(value >= 0 for value in dual)
            and sum(image) == image_size
            and sum(dual) == dual_size
            and image[0] == dual[0] == 1
            and not any(
                image[weight]
                for weight in range(1, 14)
            )
            and not any(
                dual[weight]
                for weight in range(1, 15)
            )
            and not any(
                image[weight]
                for weight in range(1, LENGTH + 1, 2)
            )
        ),
    }


def expected_pair_tables() -> dict[str, object]:
    ordered_edges = LENGTH * 14
    ordered_nonedges = LENGTH * (LENGTH - 1 - 14)
    ordered_off_diagonal = LENGTH * (LENGTH - 1)
    return {
        "counts": {
            "diagonal": LENGTH,
            "ordered_edges": ordered_edges,
            "ordered_nonedges": ordered_nonedges,
            "ordered_off_diagonal": ordered_off_diagonal,
        },
        "witness_shape": {
            "dual_closed_neighborhood_rows": {
                "15": {"intersection_15": 99},
                "ordered_distinct": {
                    "intersection_2": 8316,
                    "intersection_3": 1386,
                },
            },
            "image_neighborhood_rows": {
                "14": {"intersection_14": 99},
                "ordered_distinct": {
                    "intersection_1": 1386,
                    "intersection_2": 8316,
                },
            },
            "mixed_neighborhood_closed": {
                "ordered_diagonal": {"intersection_14": 99},
                "ordered_off_diagonal": {"intersection_2": 9702},
            },
        },
        "compositions": {
            "image_diagonal": [85, 0, 0, 14],
            "image_edge": [72, 13, 13, 1],
            "image_nonedge": [73, 12, 12, 2],
            "dual_diagonal": [84, 0, 0, 15],
            "dual_edge": [72, 12, 12, 3],
            "dual_nonedge": [71, 13, 13, 2],
            "mixed_diagonal": [84, 1, 0, 14],
            "mixed_off_diagonal": [72, 13, 12, 2],
        },
    }


def split_audit(
    split: dict[str, object],
    image: list[Q],
    dual: list[Q],
) -> dict[str, object]:
    specifications = {
        "image_vs_neighborhood": {
            "ordinary": image,
            "root_weight": 14,
            "first_factor": 14,
            "odd_factor": 1,
        },
        "image_vs_closed": {
            "ordinary": image,
            "root_weight": 15,
            "first_factor": 15,
            "odd_factor": 0,
        },
        "dual_vs_closed": {
            "ordinary": dual,
            "root_weight": 15,
            "first_factor": 15,
            "odd_factor": 1,
        },
        "dual_vs_neighborhood": {
            "ordinary": dual,
            "root_weight": 14,
            "first_factor": 14,
            "odd_factor": 0,
        },
    }
    audits: dict[str, object] = {}
    all_failures: list[str] = []
    parsed_rows: dict[str, dict[int, dict[int, Q]]] = {}
    for family, specification in specifications.items():
        source = split[family]
        rows = {
            int(weight): {
                int(intersection): Q(value)
                for intersection, value in entries.items()
            }
            for weight, entries in source.items()
        }
        parsed_rows[family] = rows
        failures: list[str] = []
        nonintegral = 0
        for weight in range(LENGTH + 1):
            entries = rows.get(weight, {})
            coefficient = specification["ordinary"][weight]
            root_weight = specification["root_weight"]
            lower = max(0, weight + root_weight - LENGTH)
            upper = min(weight, root_weight)
            for intersection, value in entries.items():
                nonintegral += value.denominator != 1
                if value < 0:
                    failures.append(
                        f"negative:w{weight}:j{intersection}"
                    )
                if not lower <= intersection <= upper:
                    failures.append(
                        f"range:w{weight}:j{intersection}"
                    )
                if (
                    specification["odd_factor"] == 0
                    and intersection % 2
                    and value
                ):
                    failures.append(
                        f"mixed_odd:w{weight}:j{intersection}"
                    )
            row_sum = sum(entries.values(), Q(0))
            first_moment = sum(
                Q(intersection) * value
                for intersection, value in entries.items()
            )
            odd_sum = sum(
                value
                for intersection, value in entries.items()
                if intersection % 2
            )
            if row_sum != 99 * coefficient:
                failures.append(f"row_sum:w{weight}")
            if (
                first_moment
                != specification["first_factor"]
                * weight
                * coefficient
            ):
                failures.append(f"first_moment:w{weight}")
            if (
                odd_sum
                != specification["odd_factor"]
                * weight
                * coefficient
            ):
                failures.append(f"odd_count:w{weight}")
        audits[family] = {
            "failures": failures,
            "row_count": len(rows),
            "nonintegral_entry_count": nonintegral,
            "verified": not failures,
        }
        all_failures.extend(f"{family}:{value}" for value in failures)

    pair_lower_requirements = {
        "image_vs_neighborhood": {
            (14, 14): Q(99),
            (14, 1): Q(1386),
            (14, 2): Q(8316),
        },
        "dual_vs_closed": {
            (15, 15): Q(99),
            (15, 3): Q(1386),
            (15, 2): Q(8316),
        },
        "image_vs_closed": {
            (14, 14): Q(99),
            (14, 2): Q(9702),
        },
        "dual_vs_neighborhood": {
            (15, 14): Q(99),
            (15, 2): Q(9702),
        },
    }
    pair_lower_failures = []
    for family, requirements in pair_lower_requirements.items():
        for (weight, intersection), lower in requirements.items():
            value = parsed_rows[family].get(weight, {}).get(
                intersection, Q(0)
            )
            if value < lower:
                pair_lower_failures.append(
                    f"{family}:w{weight}:j{intersection}"
                )
    return {
        "families": audits,
        "pair_lower_failures": pair_lower_failures,
        "verified": not all_failures and not pair_lower_failures,
    }


def state_counts() -> dict[str, int]:
    raw = math.comb(LENGTH + 3, 3)
    even_states = 0
    orbits: set[tuple[int, int, int]] = set()
    for n01 in range(LENGTH + 1):
        for n10 in range(LENGTH - n01 + 1):
            for n11 in range(LENGTH - n01 - n10 + 1):
                if (n10 + n11) % 2 or (n01 + n11) % 2:
                    continue
                even_states += 1
                orbits.add(tuple(sorted((n01, n10, n11))))
    return {
        "raw_four_composition_states": raw,
        "C_times_C_even_weight_states": even_states,
        "GL2_orbits_on_C_times_C_states": len(orbits),
    }


def verify_wave131_strictness(
    repository: Path, table: list[list[int]]
) -> dict[str, object]:
    payload = json.loads(
        (
            repository
            / "attempts"
            / "wave131-binary-lcd-enumerator"
            / "rational-witness.json"
        ).read_text(encoding="utf-8")
    )
    image = coefficients(payload["image_coefficients"])
    dual = coefficients(payload["dual_coefficients"])
    ordinary = ordinary_audit(image, dual, table)
    claimed_a98 = Q(
        170562693352378955498780443720005,
        220411100178756488424348352249856,
    )
    return {
        "A98": str(image[98]),
        "A98_matches_published_value": image[98] == claimed_a98,
        "A98_positive": image[98] > 0,
        "ordinary_MacWilliams_200_rows_pass": ordinary[
            "all_200_rows_verified"
        ],
        "fails_wave132_forced_A98_zero": image[98] > 0,
        "verified": (
            image[98] == claimed_a98
            and image[98] > 0
            and ordinary["all_200_rows_verified"]
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", type=Path, default=Path.cwd())
    parser.add_argument(
        "--package",
        type=Path,
        default=Path(
            "attempts/wave132-distinguished-biweight"
        ),
    )
    parser.add_argument(
        "--expected-manifest",
        default=EXPECTED_MANIFEST_SHA256,
    )
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()
    repository = args.repository.resolve()
    package = (
        args.package
        if args.package.is_absolute()
        else repository / args.package
    ).resolve()

    manifest = parse_manifest(
        repository, package, args.expected_manifest
    )
    input_freeze = parse_input_freeze(repository, package)
    witness = json.loads(
        (package / "joint-witness.json").read_text(encoding="utf-8")
    )
    table = krawtchouk_table()
    image = coefficients(
        witness["ordinary"]["image_coefficients"]
    )
    dual = coefficients(
        witness["ordinary"]["dual_coefficients"]
    )
    ordinary = ordinary_audit(image, dual, table)
    pairs = expected_pair_tables()
    pair_table_verified = (
        witness["distinguished_pair_tables"]
        == pairs["witness_shape"]
    )
    splits = split_audit(
        witness["split_enumerators"], image, dual
    )
    high_weight_failures = [
        weight
        for weight, value in enumerate(image)
        if value and weight > 92
    ]
    high_weight = {
        "derived_integer_bound": 1386 // 15,
        "positive_image_weights_above_92": high_weight_failures,
        "A94": str(image[94]),
        "A96": str(image[96]),
        "A98": str(image[98]),
        "verified": (
            1386 // 15 == 92
            and not high_weight_failures
            and image[94] == image[96] == image[98] == 0
        ),
    }
    states = state_counts()
    state_counts_verified = states == {
        "raw_four_composition_states": 171700,
        "C_times_C_even_weight_states": 42925,
        "GL2_orbits_on_C_times_C_states": 7803,
    }
    wave131 = verify_wave131_strictness(repository, table)
    integral_scout = json.loads(
        (package / "integral-scout.json").read_text(encoding="utf-8")
    )
    timeout_safely_unknown = (
        integral_scout.get("claim_label") == "UNKNOWN"
        and integral_scout.get("negative_inference_allowed") is False
        and integral_scout.get("result", {}).get("status")
        == "UNKNOWN_HARD_TIMEOUT"
    )
    verified = all(
        (
            manifest["verified"],
            input_freeze["verified"],
            pair_table_verified,
            ordinary["verified"],
            splits["verified"],
            high_weight["verified"],
            state_counts_verified,
            wave131["verified"],
            timeout_safely_unknown,
        )
    )
    result = {
        "format": "wave132-independent-verification-v1",
        "role": "verifier",
        "classification": (
            "VERIFIED" if verified else "REFUTED_OR_UNVERIFIED"
        ),
        "manifest": manifest,
        "input_freeze": input_freeze,
        "pair_tables": {
            "expected": pairs,
            "verified": pair_table_verified,
        },
        "ordinary_macwilliams": ordinary,
        "split_enumerators": splits,
        "high_weight_cut": high_weight,
        "full_genus_state_counts": {
            **states,
            "verified": state_counts_verified,
        },
        "wave131_strictness": wave131,
        "integral_scout_status_safely_unknown": (
            timeout_safely_unknown
        ),
        "promoted_claims": {
            "distinguished_pair_compositions": (
                "VERIFIED" if pair_table_verified else "REFUTED"
            ),
            "high_weight_image_cut": (
                "VERIFIED"
                if high_weight["verified"]
                else "REFUTED"
            ),
            "rational_low_degree_split_feasibility": (
                "VERIFIED"
                if ordinary["verified"] and splits["verified"]
                else "REFUTED"
            ),
        },
        "unchanged_unknowns": {
            "integral_low_degree_split_feasibility": "UNKNOWN",
            "full_genus_two_MacWilliams_feasibility": "UNKNOWN",
            "binary_code_realization": "UNKNOWN",
            "graph_realization": "UNKNOWN",
            "Conway_99": "UNKNOWN",
        },
        "independence": {
            "discovery_generator_imported": False,
            "discovery_checker_imported": False,
            "solver_used": False,
            "method": (
                "standard-library Fraction replay with independently "
                "implemented Krawtchouk, pair, split, parity, range, "
                "and state-count formulas"
            ),
        },
    }
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.write:
        args.write.write_text(text, encoding="utf-8", newline="\n")
    else:
        print(text, end="")
    return 0 if verified else 1


if __name__ == "__main__":
    raise SystemExit(main())
