#!/usr/bin/env python3
"""Exact ordinary weight-enumerator check for the centered Wave 39 code.

This module deliberately checks only the formal MacWilliams constraints.  A
passing distribution is not asserted to be the weight enumerator of a linear
code, much less a Conway graph.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Iterable


LENGTH = 231
DIMENSION = 11
FIELD_SIZE = 3
CODE_SIZE = FIELD_SIZE**DIMENSION

# A_i, including the unique zero word.  Nonzero ternary words occur in
# antipodal pairs, which the displayed even coefficients respect.
PRIMAL_ENUMERATOR = {
    0: 1,
    18: 2,
    144: 53_316,
    153: 19_798,
    159: 98_496,
    162: 5_072,
    198: 462,
}

DUAL_LOWER_BOUNDS = {
    7: 198,
    12: 1_386,
    13: 1_386,
    14: 16_632,
}


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def krawtchouk_table(
    length: int = LENGTH, field_size: int = FIELD_SIZE
) -> list[list[int]]:
    """Return exact q-ary Krawtchouk values K_j(i).

    The three-term recurrence is checked for exact divisibility at every
    entry; no floating-point arithmetic is used.
    """

    table = [[0] * (length + 1) for _ in range(length + 1)]
    for weight in range(length + 1):
        table[0][weight] = 1
        table[1][weight] = (field_size - 1) * length - field_size * weight

    for degree in range(1, length):
        for weight in range(length + 1):
            numerator = (
                (
                    (field_size - 1) * length
                    - (field_size - 2) * degree
                    - field_size * weight
                )
                * table[degree][weight]
                - (field_size - 1)
                * (length - degree + 1)
                * table[degree - 1][weight]
            )
            divisor = degree + 1
            if numerator % divisor:
                raise AssertionError(
                    f"Krawtchouk recurrence failed at ({degree}, {weight})"
                )
            table[degree + 1][weight] = numerator // divisor
    return table


def macwilliams_transform(
    enumerator: dict[int, int],
    *,
    code_size: int = CODE_SIZE,
    table: list[list[int]] | None = None,
) -> tuple[dict[int, int], list[dict[str, int]]]:
    """Compute the exact ordinary MacWilliams transform.

    The second return value records any coefficient whose numerator is not
    divisible by ``code_size``.
    """

    if table is None:
        table = krawtchouk_table()

    transformed: dict[int, int] = {}
    divisibility_failures: list[dict[str, int]] = []
    for degree in range(LENGTH + 1):
        numerator = sum(
            multiplicity * table[degree][weight]
            for weight, multiplicity in enumerator.items()
        )
        quotient, remainder = divmod(numerator, code_size)
        if remainder:
            divisibility_failures.append(
                {
                    "degree": degree,
                    "numerator": numerator,
                    "remainder": remainder,
                }
            )
        transformed[degree] = quotient
    return transformed, divisibility_failures


def nonzero_dict(values: dict[int, int]) -> dict[str, int]:
    return {str(index): value for index, value in values.items() if value}


def moment_sums(enumerator: dict[int, int]) -> dict[str, int]:
    return {
        "word_count": sum(enumerator.values()),
        "weight_sum": sum(weight * count for weight, count in enumerator.items()),
        "weight_square_sum": sum(
            weight * weight * count for weight, count in enumerator.items()
        ),
    }


def build_result(
    enumerator: dict[int, int] | None = None,
) -> dict[str, object]:
    if enumerator is None:
        enumerator = dict(PRIMAL_ENUMERATOR)

    if any(weight < 0 or weight > LENGTH for weight in enumerator):
        raise AssertionError("primal weight outside 0..231")
    if enumerator.get(0) != 1:
        raise AssertionError("formal enumerator must have A_0=1")
    if any(count < 0 for count in enumerator.values()):
        raise AssertionError("negative primal coefficient")

    table = krawtchouk_table()
    dual, divisibility_failures = macwilliams_transform(
        enumerator, table=table
    )

    primal_count = sum(enumerator.values())
    all_primal_weights_divisible_by_three = all(
        weight % 3 == 0 for weight, count in enumerator.items() if count
    )
    all_nonzero_multiplicities_even = all(
        count % 2 == 0
        for weight, count in enumerator.items()
        if weight and count
    )
    all_dual_coefficients_nonnegative = all(value >= 0 for value in dual.values())
    self_orthogonal_dominance = all(
        dual[weight] >= enumerator.get(weight, 0)
        for weight in range(LENGTH + 1)
    )
    dual_lower_bounds_pass = all(
        dual[weight] >= lower
        for weight, lower in DUAL_LOWER_BOUNDS.items()
    )
    dual_count = sum(dual.values())

    checks = {
        "A0_equals_one": enumerator.get(0) == 1,
        "A198_at_least_462": enumerator.get(198, 0) >= 462,
        "all_nonzero_primal_multiplicities_even": (
            all_nonzero_multiplicities_even
        ),
        "all_primal_weights_divisible_by_three": (
            all_primal_weights_divisible_by_three
        ),
        "all_dual_coefficients_integral": not divisibility_failures,
        "all_dual_coefficients_nonnegative": all_dual_coefficients_nonnegative,
        "B0_equals_one": dual[0] == 1,
        "B1_equals_zero": dual[1] == 0,
        "B2_equals_zero": dual[2] == 0,
        "dual_low_weight_lower_bounds_pass": dual_lower_bounds_pass,
        "dual_word_count_equals_3_pow_220": (
            dual_count == FIELD_SIZE ** (LENGTH - DIMENSION)
        ),
        "formal_self_orthogonal_dominance_Bi_ge_Ai": (
            self_orthogonal_dominance
        ),
        "primal_word_count_equals_3_pow_11": primal_count == CODE_SIZE,
    }
    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise AssertionError(f"formal enumerator check failed: {failed}")

    result = {
        "format": "wave54-centered-enumerator-v1",
        "claim_label": "CANDIDATE",
        "scope": (
            "ordinary formal weight enumerator for the conditional centered "
            "projective self-orthogonal ternary [231,11] endpoint code"
        ),
        "frozen_target": {
            "field_size": FIELD_SIZE,
            "length": LENGTH,
            "dimension": DIMENSION,
            "code_size": CODE_SIZE,
            "projective_dual_distance_condition": "B_1=B_2=0",
            "self_orthogonal_enumerator_condition": "B_i>=A_i for every i",
            "distinguished_primal_constraint": "A_198>=462",
            "dual_lower_bounds": {
                str(weight): value
                for weight, value in DUAL_LOWER_BOUNDS.items()
            },
        },
        "primal_enumerator_nonzero": nonzero_dict(enumerator),
        "primal_moments": moment_sums(enumerator),
        "dual_enumerator_nonzero": nonzero_dict(dual),
        "dual_selected_coefficients": {
            str(weight): dual[weight]
            for weight in range(15)
        },
        "dual_word_count": dual_count,
        "checks": checks,
        "exact_replay": {
            "arithmetic": "Python arbitrary-precision integers only",
            "krawtchouk_recurrence": (
                "(j+1)K_(j+1)(i)=((q-1)n-(q-2)j-qi)K_j(i)"
                "-(q-1)(n-j+1)K_(j-1)(i)"
            ),
            "macwilliams_formula": (
                "B_j=3^-11 sum_i A_i K_j(i)"
            ),
            "divisibility_failure_count": len(divisibility_failures),
        },
        "disposition": {
            "ordinary_integral_enumerator_obstruction": "NONE",
            "actual_linear_code": "NOT_CONSTRUCTED",
            "complete_weight_enumerator": "NOT_CONSTRUCTED",
            "endpoint": "UNKNOWN",
            "conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "limitations": [
            "A formal ordinary weight enumerator need not be realized by a linear code.",
            "Ordinary weights forget the separate counts of the two nonzero ternary symbols.",
            "The 99 distinguished weight-seven dual words are represented only by lower bounds.",
            "No generator matrix, centered polar point set, endpoint graph, or Conway graph is constructed.",
            "Discovery cannot verify itself; independent reconstruction is required.",
        ],
    }
    result["candidate_sha256"] = sha256_bytes(
        canonical_bytes(result["primal_enumerator_nonzero"])
    )
    return result


def parse_args(arguments: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--output", type=Path)
    group.add_argument("--verify", type=Path)
    return parser.parse_args(arguments)


def main(arguments: Iterable[str] | None = None) -> int:
    options = parse_args(arguments)
    payload = canonical_bytes(build_result())
    if options.verify:
        if options.verify.read_bytes() != payload:
            raise SystemExit("exact result bytes differ")
        print(f"VERIFIED {options.verify}")
        print(f"sha256={sha256_bytes(payload)}")
        return 0
    if options.output:
        options.output.write_bytes(payload)
        print(f"WROTE {options.output}")
        print(f"sha256={sha256_bytes(payload)}")
        return 0
    print(payload.decode("utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
