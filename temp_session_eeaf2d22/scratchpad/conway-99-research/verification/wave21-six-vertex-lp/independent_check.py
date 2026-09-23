#!/usr/bin/env python3
"""Independent Wave 21 verifier.

This checker reads only the two pinned primary-source TeX files.  It does not
import or execute the discovery checker.  It:

* parses the published four-, five-, six-, and Hamiltonian seven-vertex
  formulas with exact rational arithmetic;
* parses the printed 4->5 and 5->6 vertex-deletion equations;
* independently enumerates locally admissible graph isomorphism classes;
* reconstructs deletion decks and source-index alignments;
* preserves the raw printed 5->6 failure separately from the explicit repair;
* exhausts the exact integer/nonnegative feasibility region at
  srg(99,14,1,2).
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import re
import sys
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from pathlib import Path


N = 99
K = 14
SIX_TEX_SHA256 = "823bcaf636a99f6655af453b2a910b9953338db980480572bca81730cfa1b44f"
SEVEN_TEX_SHA256 = "0b06fdc1c2951a344592c6af23abd133c4a8a68d717f199e7a0e2d7ceb909d0a"

# Polynomial keys are (power of n3, power of h11).
Poly = dict[tuple[int, int], Fraction]


def _clean(poly: Poly) -> Poly:
    return {monomial: coefficient for monomial, coefficient in poly.items() if coefficient}


def constant(value: int | Fraction) -> Poly:
    value = Fraction(value)
    return {} if value == 0 else {(0, 0): value}


def variable(which: str) -> Poly:
    if which == "n3":
        return {(1, 0): Fraction(1)}
    if which == "h11":
        return {(0, 1): Fraction(1)}
    raise ValueError(which)


def add(left: Poly, right: Poly) -> Poly:
    out = dict(left)
    for monomial, coefficient in right.items():
        out[monomial] = out.get(monomial, Fraction(0)) + coefficient
    return _clean(out)


def neg(poly: Poly) -> Poly:
    return {monomial: -coefficient for monomial, coefficient in poly.items()}


def sub(left: Poly, right: Poly) -> Poly:
    return add(left, neg(right))


def mul(left: Poly, right: Poly) -> Poly:
    out: Poly = {}
    for (lx, ly), lc in left.items():
        for (rx, ry), rc in right.items():
            monomial = (lx + rx, ly + ry)
            out[monomial] = out.get(monomial, Fraction(0)) + lc * rc
    return _clean(out)


def div(left: Poly, right: Poly) -> Poly:
    if set(right) - {(0, 0)} or right.get((0, 0), Fraction(0)) == 0:
        raise ValueError(f"nonconstant or zero denominator: {right}")
    denominator = right[(0, 0)]
    return {monomial: coefficient / denominator for monomial, coefficient in left.items()}


def power(poly: Poly, exponent: int) -> Poly:
    if exponent < 0:
        raise ValueError("negative powers are unsupported")
    result = constant(1)
    base = poly
    value = exponent
    while value:
        if value & 1:
            result = mul(result, base)
        base = mul(base, base)
        value >>= 1
    return result


def scale(poly: Poly, coefficient: int | Fraction) -> Poly:
    return mul(constant(coefficient), poly)


def affine(poly: Poly) -> tuple[Fraction, Fraction, Fraction]:
    unexpected = set(poly) - {(0, 0), (1, 0), (0, 1)}
    if unexpected:
        raise AssertionError(f"expression is not affine: {poly}")
    return (
        poly.get((0, 0), Fraction(0)),
        poly.get((1, 0), Fraction(0)),
        poly.get((0, 1), Fraction(0)),
    )


def evaluate(poly: Poly, n3: int, h11: int = 0) -> Fraction:
    total = Fraction(0)
    for (x_power, y_power), coefficient in poly.items():
        total += coefficient * n3**x_power * h11**y_power
    return total


def frac_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def affine_json(poly: Poly) -> dict[str, str]:
    c, x, y = affine(poly)
    return {
        "constant": frac_text(c),
        "n3_coefficient": frac_text(x),
        "h11_coefficient": frac_text(y),
    }


class LatexExpressionParser:
    """Small exact parser for the arithmetic subset used by the pinned TeX."""

    def __init__(self, source: str):
        cleaned = source
        for command in (r"\left", r"\right", r"\bigl", r"\bigr", r"\,", r"\!"):
            cleaned = cleaned.replace(command, "")
        cleaned = cleaned.replace(r"\\", " ").replace("&", " ")
        cleaned = cleaned.strip().rstrip(",;. ")
        self.source = cleaned
        self.position = 0

    def parse(self) -> Poly:
        result = self._expression()
        self._space()
        if self.position != len(self.source):
            raise ValueError(
                f"unparsed suffix at {self.position}: {self.source[self.position:]!r}"
            )
        return result

    def _space(self) -> None:
        while self.position < len(self.source) and self.source[self.position].isspace():
            self.position += 1

    def _take(self, token: str) -> bool:
        self._space()
        if self.source.startswith(token, self.position):
            self.position += len(token)
            return True
        return False

    def _expression(self) -> Poly:
        result = self._term()
        while True:
            if self._take("+"):
                result = add(result, self._term())
            elif self._take("-"):
                result = sub(result, self._term())
            else:
                return result

    def _atom_starts(self) -> bool:
        self._space()
        if self.position >= len(self.source):
            return False
        here = self.source[self.position :]
        return (
            here[0].isdigit()
            or here[0] in "({"
            or here.startswith(r"\frac")
            or here.startswith("n_3")
            or here.startswith("n_{3}")
            or here.startswith("h_{11}")
            or here.startswith("h_11")
            or here[0] in "nk"
        )

    def _term(self) -> Poly:
        result = self._unary_power()
        while True:
            if self._take("*") or self._take(r"\cdot"):
                result = mul(result, self._unary_power())
            elif self._take("/"):
                result = div(result, self._unary_power())
            elif self._atom_starts():
                result = mul(result, self._unary_power())
            else:
                return result

    def _unary_power(self) -> Poly:
        if self._take("+"):
            return self._unary_power()
        if self._take("-"):
            return neg(self._unary_power())
        result = self._atom()
        if self._take("^"):
            exponent_poly = self._atom()
            if set(exponent_poly) - {(0, 0)}:
                raise ValueError("symbolic exponent")
            exponent = exponent_poly.get((0, 0), Fraction(0))
            if exponent.denominator != 1:
                raise ValueError("fractional exponent")
            result = power(result, exponent.numerator)
        return result

    def _group(self, opening: str, closing: str) -> Poly:
        if not self._take(opening):
            raise ValueError(f"expected {opening!r} at {self.position}")
        result = self._expression()
        if not self._take(closing):
            raise ValueError(f"expected {closing!r} at {self.position}")
        return result

    def _atom(self) -> Poly:
        self._space()
        if self._take(r"\frac"):
            numerator = self._group("{", "}")
            denominator = self._group("{", "}")
            return div(numerator, denominator)
        if self._take("("):
            self.position -= 1
            return self._group("(", ")")
        if self._take("{"):
            self.position -= 1
            return self._group("{", "}")
        for spelling in ("h_{11}", "h_11"):
            if self._take(spelling):
                return variable("h11")
        for spelling in ("n_{3}", "n_3"):
            if self._take(spelling):
                return variable("n3")
        if self._take("n"):
            return constant(N)
        if self._take("k"):
            return constant(K)
        self._space()
        match = re.match(r"\d+", self.source[self.position :])
        if match:
            self.position += len(match.group(0))
            return constant(int(match.group(0)))
        raise ValueError(
            f"expected atom at {self.position}: {self.source[self.position:]!r}"
        )


def parse_expression(source: str) -> Poly:
    return LatexExpressionParser(source).parse()


INDEXED_ROW = re.compile(
    r"^\s*([lmnh])(?:_\{(\d+)\}|_(\d+))\s*=&(.*)$"
)
DECK_ROW = re.compile(
    r"^\s*([lm])(?:_\{(\d+)\}|_(\d+))\(n-(\d)\)=&(.*)$"
)


def collect_formula_rows(lines: list[str], letter: str, count: int) -> dict[int, Poly]:
    raw: dict[int, str] = {}
    current: int | None = None
    for line in lines:
        if line.lstrip().startswith(r"\end{"):
            break
        match = INDEXED_ROW.match(line)
        if match and match.group(1) == letter:
            current = int(match.group(2) or match.group(3))
            raw[current] = match.group(4)
        elif current is not None:
            raw[current] += " " + line
    expected = set(range(1, count + 1)) if letter != "h" else set(range(count))
    if set(raw) != expected:
        raise AssertionError(
            f"{letter} formula indices: got {sorted(raw)}, expected {sorted(expected)}"
        )
    return {index: parse_expression(expression) for index, expression in raw.items()}


def collect_deck_rows(
    lines: list[str], lhs_letter: str, rhs_letter: str, lhs_count: int, rhs_count: int
) -> list[list[int]]:
    raw: dict[int, str] = {}
    current: int | None = None
    for line in lines:
        if line.lstrip().startswith(r"\end{"):
            break
        match = DECK_ROW.match(line)
        if match and match.group(1) == lhs_letter:
            current = int(match.group(2) or match.group(3))
            raw[current] = match.group(5)
        elif current is not None:
            raw[current] += " " + line
    if set(raw) != set(range(1, lhs_count + 1)):
        raise AssertionError(f"missing {lhs_letter} deck rows: {sorted(raw)}")
    matrix = [[0 for _ in range(rhs_count)] for _ in range(lhs_count)]
    term = re.compile(
        rf"(?<![A-Za-z0-9_])(\d*){rhs_letter}(?:_\{{(\d+)\}}|_(\d+))"
    )
    for lhs_index, expression in raw.items():
        matches = list(term.finditer(expression))
        if not matches:
            raise AssertionError(f"no RHS terms in {lhs_letter}_{lhs_index}")
        for match in matches:
            coefficient = int(match.group(1)) if match.group(1) else 1
            rhs_index = int(match.group(2) or match.group(3))
            if not 1 <= rhs_index <= rhs_count:
                raise AssertionError(rhs_index)
            matrix[lhs_index - 1][rhs_index - 1] += coefficient
    return matrix


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def read_sources(six_path: Path, seven_path: Path) -> tuple[str, str]:
    six_hash = sha256(six_path)
    seven_hash = sha256(seven_path)
    if six_hash != SIX_TEX_SHA256:
        raise AssertionError(f"six TeX hash mismatch: {six_hash}")
    if seven_hash != SEVEN_TEX_SHA256:
        raise AssertionError(f"seven TeX hash mismatch: {seven_hash}")
    return (
        six_path.read_text(encoding="utf-8"),
        seven_path.read_text(encoding="utf-8"),
    )


def source_tables(six_tex: str, seven_tex: str) -> dict[str, object]:
    six_lines = six_tex.splitlines()
    seven_lines = seven_tex.splitlines()
    # Fixed line slices are part of the pinned-source contract and use the
    # paper's one-based line numbering.
    four = collect_formula_rows(six_lines[427:438], "l", 9)
    five = collect_formula_rows(six_lines[455:478], "m", 21)
    six = collect_formula_rows(six_lines[344:408], "n", 62)
    seven = collect_formula_rows(seven_lines[176:196], "h", 19)
    four_to_five = collect_deck_rows(six_lines[439:450], "l", "m", 9, 21)
    five_to_six = collect_deck_rows(six_lines[492:519], "m", "n", 21, 62)
    return {
        "four": four,
        "five": five,
        "six": six,
        "seven": seven,
        "four_to_five": four_to_five,
        "five_to_six_raw": five_to_six,
    }


@lru_cache(maxsize=None)
def edges(order: int) -> tuple[tuple[int, int], ...]:
    return tuple(itertools.combinations(range(order), 2))


@lru_cache(maxsize=None)
def edge_position(order: int) -> dict[tuple[int, int], int]:
    return {edge: index for index, edge in enumerate(edges(order))}


def has_edge(mask: int, order: int, left: int, right: int) -> bool:
    if left > right:
        left, right = right, left
    return bool(mask & (1 << edge_position(order)[(left, right)]))


def relabel(mask: int, order: int, new_to_old: tuple[int, ...]) -> int:
    result = 0
    positions = edge_position(order)
    for new_left, new_right in edges(order):
        old_left = new_to_old[new_left]
        old_right = new_to_old[new_right]
        if old_left > old_right:
            old_left, old_right = old_right, old_left
        if mask & (1 << positions[(old_left, old_right)]):
            result |= 1 << positions[(new_left, new_right)]
    return result


@lru_cache(maxsize=None)
def canonical(mask: int, order: int) -> int:
    degrees = [
        sum(has_edge(mask, order, vertex, other) for other in range(order) if other != vertex)
        for vertex in range(order)
    ]
    groups = [
        tuple(vertex for vertex, degree in enumerate(degrees) if degree == value)
        for value in sorted(set(degrees))
    ]
    best: int | None = None
    for pieces in itertools.product(*(itertools.permutations(group) for group in groups)):
        permutation = tuple(vertex for piece in pieces for vertex in piece)
        candidate = relabel(mask, order, permutation)
        if best is None or candidate < best:
            best = candidate
    assert best is not None
    return best


def locally_admissible(mask: int, order: int) -> bool:
    for left, right in edges(order):
        common = sum(
            has_edge(mask, order, left, vertex)
            and has_edge(mask, order, right, vertex)
            for vertex in range(order)
            if vertex not in (left, right)
        )
        maximum = 1 if has_edge(mask, order, left, right) else 2
        if common > maximum:
            return False
    return True


@lru_cache(maxsize=None)
def local_classes(order: int) -> tuple[int, ...]:
    representatives: set[int] = set()
    for mask in range(1 << len(edges(order))):
        if locally_admissible(mask, order):
            representatives.add(canonical(mask, order))
    return tuple(sorted(representatives))


def hamiltonian_seven_classes() -> tuple[int, ...]:
    order = 7
    cycle_edges = {
        tuple(sorted((vertex, (vertex + 1) % order))) for vertex in range(order)
    }
    cycle_mask = sum(1 << edge_position(order)[edge] for edge in cycle_edges)
    chords = tuple(edge for edge in edges(order) if edge not in cycle_edges)
    representatives: set[int] = set()
    for chord_mask in range(1 << len(chords)):
        mask = cycle_mask
        for index, edge in enumerate(chords):
            if chord_mask & (1 << index):
                mask |= 1 << edge_position(order)[edge]
        if locally_admissible(mask, order):
            representatives.add(canonical(mask, order))
    return tuple(sorted(representatives))


def delete_vertex(mask: int, order: int, removed: int) -> int:
    remaining = [vertex for vertex in range(order) if vertex != removed]
    lower_order = order - 1
    result = 0
    for new_left, new_right in edges(lower_order):
        old_left = remaining[new_left]
        old_right = remaining[new_right]
        if has_edge(mask, order, old_left, old_right):
            result |= 1 << edge_position(lower_order)[(new_left, new_right)]
    return canonical(result, lower_order)


def deletion_matrix(lower: tuple[int, ...], upper: tuple[int, ...]) -> list[list[int]]:
    lower_position = {mask: index for index, mask in enumerate(lower)}
    matrix = [[0 for _ in upper] for _ in lower]
    upper_order = len(edges(0))  # overwritten below; keeps type checkers quiet
    # Solve m = r(r-1)/2 for the vertex order of upper masks.
    edge_count = max((mask.bit_length() for mask in upper), default=0)
    for candidate_order in range(1, 10):
        if len(edges(candidate_order)) >= edge_count:
            upper_order = candidate_order
            break
    # Empty/highly sparse representatives do not expose their order in the
    # mask, so infer it from the requested class cardinalities.
    upper_order = {21: 5, 62: 6}.get(len(upper), upper_order)
    for column, mask in enumerate(upper):
        for removed in range(upper_order):
            card = delete_vertex(mask, upper_order, removed)
            matrix[lower_position[card]][column] += 1
    return matrix


def align_rows_by_unlabeled_signatures(
    source: list[list[int]], local: list[list[int]]
) -> list[int]:
    source_signatures = [tuple(sorted(row)) for row in source]
    local_signatures = [tuple(sorted(row)) for row in local]
    mapping: list[int] = []
    for signature in source_signatures:
        candidates = [
            index for index, local_signature in enumerate(local_signatures)
            if local_signature == signature
        ]
        if len(candidates) != 1:
            raise AssertionError(f"row signature is not unique: {candidates}")
        mapping.append(candidates[0])
    if len(set(mapping)) != len(mapping):
        raise AssertionError("row mapping is not bijective")
    return mapping


def align_columns(
    source: list[list[int]], local: list[list[int]], source_row_to_local: list[int]
) -> list[int]:
    local_vectors = [
        tuple(local[source_row_to_local[row]][column] for row in range(len(source)))
        for column in range(len(local[0]))
    ]
    mapping: list[int] = []
    for source_column in range(len(source[0])):
        vector = tuple(source[row][source_column] for row in range(len(source)))
        candidates = [
            index for index, local_vector in enumerate(local_vectors)
            if local_vector == vector
        ]
        if len(candidates) != 1:
            raise AssertionError(
                f"column {source_column + 1} has {len(candidates)} local matches"
            )
        mapping.append(candidates[0])
    if len(set(mapping)) != len(mapping):
        raise AssertionError("column mapping is not bijective")
    return mapping


def vector_sum(polys: list[Poly], coefficients: list[int]) -> Poly:
    result: Poly = {}
    for poly, coefficient in zip(polys, coefficients):
        result = add(result, scale(poly, coefficient))
    return result


def identity_residuals(
    lower: dict[int, Poly],
    upper: dict[int, Poly],
    matrix: list[list[int]],
    multiplier: int,
) -> list[Poly]:
    upper_vector = [upper[index] for index in sorted(upper)]
    return [
        sub(scale(lower[row + 1], multiplier), vector_sum(upper_vector, matrix[row]))
        for row in range(len(matrix))
    ]


def ceil_fraction(value: Fraction) -> int:
    return -((-value.numerator) // value.denominator)


def floor_fraction(value: Fraction) -> int:
    return value.numerator // value.denominator


def ceil_multiple(value: Fraction, modulus: int) -> int:
    integer = ceil_fraction(value)
    return integer + (-integer) % modulus


def floor_multiple(value: Fraction, modulus: int) -> int:
    integer = floor_fraction(value)
    return integer - integer % modulus


def six_feasibility(six: dict[int, Poly]) -> dict[str, object]:
    coefficients = {index: affine(poly) for index, poly in six.items()}
    if any(y != 0 for _, _, y in coefficients.values()):
        raise AssertionError("six-vertex formula depends on h11")
    upper_bounds: list[tuple[Fraction, int]] = []
    lower_bounds: list[tuple[Fraction, int]] = [(Fraction(0), 3)]
    for index, (intercept, slope, _) in coefficients.items():
        if slope < 0:
            upper_bounds.append((intercept / -slope, index))
        elif slope > 0:
            lower_bounds.append((-intercept / slope, index))
        elif intercept < 0:
            raise AssertionError(f"n_{index} is always negative")
    rational_lower, lower_index = max(lower_bounds)
    rational_upper, upper_index = min(upper_bounds)
    denominator_lcm = math.lcm(
        *(value.denominator for triple in coefficients.values() for value in triple)
    )
    good_residues = [
        residue
        for residue in range(denominator_lcm)
        if all(evaluate(poly, residue).denominator == 1 for poly in six.values())
    ]
    candidates = [
        n3
        for n3 in range(max(0, ceil_fraction(rational_lower)), floor_fraction(rational_upper) + 1)
        if all(
            evaluate(poly, n3).denominator == 1 and evaluate(poly, n3) >= 0
            for poly in six.values()
        )
    ]
    return {
        "rational_lower": frac_text(rational_lower),
        "rational_upper": frac_text(rational_upper),
        "lower_facet_index": lower_index,
        "upper_facet_index": upper_index,
        "integrality_modulus": denominator_lcm,
        "integrality_residues": good_residues,
        "feasible_count": len(candidates),
        "feasible_first": candidates[0],
        "feasible_last": candidates[-1],
        "feasible_step": candidates[1] - candidates[0],
        "values": candidates,
    }


def y_interval(seven: dict[int, Poly], n3: int, modulus: int = 4) -> tuple[int, int]:
    lower = Fraction(-10**30)
    upper = Fraction(10**30)
    for index, poly in seven.items():
        intercept, x_coefficient, y_coefficient = affine(poly)
        fixed = intercept + x_coefficient * n3
        if y_coefficient > 0:
            lower = max(lower, -fixed / y_coefficient)
        elif y_coefficient < 0:
            upper = min(upper, fixed / -y_coefficient)
        elif fixed < 0:
            raise AssertionError(f"h_{index} negative independent of h11 at n3={n3}")
    return ceil_multiple(lower, modulus), floor_multiple(upper, modulus)


def seven_feasibility(
    seven: dict[int, Poly], six_values: list[int]
) -> dict[str, object]:
    denominator_lcm = math.lcm(
        *(value.denominator for poly in seven.values() for value in affine(poly))
    )
    # Check every n3 residue because coefficients in n3 and h11 may interact.
    residue_table: dict[str, list[int]] = {}
    for x_residue in range(denominator_lcm):
        residue_table[str(x_residue)] = [
            y_residue
            for y_residue in range(denominator_lcm)
            if all(
                evaluate(poly, x_residue, y_residue).denominator == 1
                for poly in seven.values()
            )
        ]
    checks: dict[str, dict[str, int]] = {}
    all_feasible = True
    exact_facets = True
    for n3 in six_values:
        lower, upper = y_interval(seven, n3, denominator_lcm)
        expected_lower = ceil_multiple(Fraction(2 * n3), 4)
        expected_upper = floor_multiple(Fraction(4 * n3), 4)
        exact_facets &= lower == expected_lower and upper == expected_upper
        if lower > upper:
            all_feasible = False
            continue
        for endpoint in (lower, upper):
            if not all(
                evaluate(poly, n3, endpoint).denominator == 1
                and evaluate(poly, n3, endpoint) >= 0
                for poly in seven.values()
            ):
                raise AssertionError(f"bad seven-vertex endpoint: n3={n3}, h11={endpoint}")
        if n3 in (0, 3, 705, 4158):
            checks[str(n3)] = {
                "h11_min": lower,
                "h11_max": upper,
                "feasible_h11_count": (upper - lower) // denominator_lcm + 1,
            }
    incumbent = [value for value in six_values if value >= 705]
    return {
        "integrality_modulus": denominator_lcm,
        "integrality_residues_by_n3_residue": residue_table,
        "all_six_feasible_n3_have_h11": all_feasible,
        "interval_equals_ceil4_2n3_to_4n3": exact_facets,
        "checks": checks,
        "incumbent_n3_count": len(incumbent),
        "incumbent_n3_first": incumbent[0],
        "incumbent_n3_last": incumbent[-1],
        "incumbent_n3_step": incumbent[1] - incumbent[0],
    }


def seven_derivation_residuals(
    five: dict[int, Poly], six: dict[int, Poly], seven: dict[int, Poly]
) -> list[Poly]:
    x = variable("n3")
    h = seven
    n = six
    m = five
    return [
        sub(h[10], scale(x, 2)),
        sub(h[17], scale(n[1], 3)),
        sub(h[14], scale(n[4], 2)),
        sub(h[6], scale(n[5], 8)),
        sub(h[4], scale(n[9], 4)),
        sub(scale(n[8], 2), add(add(scale(h[6], 2), scale(h[15], 4)), h[14])),
        sub(scale(n[4], 2), add(h[11], scale(h[18], 4))),
        sub(scale(n[8], 2), add(scale(h[3], 2), h[11])),
        sub(n[4], add(h[16], scale(h[18], 4))),
        sub(scale(n[4], 2), add(scale(h[13], 2), scale(h[18], 4))),
        sub(scale(m[19], 2), add(h[12], h[18])),
        sub(scale(n[9], 4), add(add(h[9], scale(h[16], 2)), scale(h[18], 2))),
        sub(scale(n[8], 2), add(add(h[8], scale(h[16], 2)), scale(h[15], 4))),
        sub(scale(n[9], 2), add(add(h[7], scale(h[16], 2)), scale(h[18], 2))),
        sub(n[17], add(scale(h[5], 2), scale(h[13], 2))),
        sub(
            scale(n[11], 4),
            add(
                add(add(scale(h[2], 2), scale(h[7], 2)), scale(h[5], 2)),
                add(h[8], h[11]),
            ),
        ),
        sub(scale(n[12], 6), add(add(h[1], h[8]), scale(h[12], 2))),
        sub(
            scale(n[35], 2),
            add(
                add(add(scale(h[0], 7), scale(h[1], 2)), scale(h[2], 2)),
                add(add(h[3], h[4]), h[5]),
            ),
        ),
    ]


def graph_and_deck_audit(
    four_to_five: list[list[int]], five_to_six_raw: list[list[int]]
) -> dict[str, object]:
    classes4 = local_classes(4)
    classes5 = local_classes(5)
    classes6 = local_classes(6)
    classes7h = hamiltonian_seven_classes()
    deck45 = deletion_matrix(classes4, classes5)
    deck56 = deletion_matrix(classes5, classes6)

    l_to_local = align_rows_by_unlabeled_signatures(four_to_five, deck45)
    m_to_local = align_columns(four_to_five, deck45, l_to_local)

    raw_column_sums = [
        sum(five_to_six_raw[row][column] for row in range(21)) for column in range(62)
    ]
    corrected = [row[:] for row in five_to_six_raw]
    corrected[6][22] += 1  # Explicitly named proposed repair: +n23 in m7.
    n_to_local = align_columns(corrected, deck56, m_to_local)

    raw_n23 = tuple(five_to_six_raw[row][22] for row in range(21))
    local_vectors = [
        tuple(deck56[m_to_local[row]][column] for row in range(21))
        for column in range(62)
    ]
    repair_rows = []
    for row in range(21):
        repaired = list(raw_n23)
        repaired[row] += 1
        if tuple(repaired) in local_vectors:
            repair_rows.append(row + 1)

    n3_mask = classes6[n_to_local[2]]
    triangles = [
        triple
        for triple in itertools.combinations(range(6), 3)
        if all(has_edge(n3_mask, 6, left, right) for left, right in itertools.combinations(triple, 2))
    ]
    disjoint_triangle_pairs = [
        (left, right)
        for left, right in itertools.combinations(triangles, 2)
        if set(left).isdisjoint(right)
    ]
    if len(disjoint_triangle_pairs) != 1:
        raise AssertionError(f"N3 disjoint triangle pairs: {disjoint_triangle_pairs}")
    left_triangle, right_triangle = disjoint_triangle_pairs[0]
    cross_edges = [
        (left, right)
        for left in left_triangle
        for right in right_triangle
        if has_edge(n3_mask, 6, left, right)
    ]

    edge_distribution = Counter(mask.bit_count() for mask in classes7h)
    return {
        "local_class_counts": {
            "order4": len(classes4),
            "order5": len(classes5),
            "order6": len(classes6),
            "order7_hamiltonian": len(classes7h),
        },
        "hamiltonian7_edge_distribution": {
            str(edge_count): count for edge_count, count in sorted(edge_distribution.items())
        },
        "four_to_five": {
            "all_column_sums": sorted(set(sum(row[column] for row in four_to_five) for column in range(21))),
            "L_source_to_local_zero_based": l_to_local,
            "M_source_to_local_zero_based": m_to_local,
            "mapping_is_bijective": len(set(l_to_local)) == 9 and len(set(m_to_local)) == 21,
        },
        "five_to_six_raw": {
            "column_sum_histogram": {
                str(value): raw_column_sums.count(value) for value in sorted(set(raw_column_sums))
            },
            "N23_column_sum": raw_column_sums[22],
            "N23_exact_local_match_count": sum(raw_n23 == vector for vector in local_vectors),
        },
        "five_to_six_correction": {
            "repair": "add +n23 to printed m7(n-5) RHS",
            "one_card_repair_rows_that_match_a_local_deck": repair_rows,
            "all_corrected_column_sums": sorted(
                set(sum(corrected[row][column] for row in range(21)) for column in range(62))
            ),
            "N_source_to_local_zero_based": n_to_local,
            "mapping_is_bijective": len(set(n_to_local)) == 62,
        },
        "N3_alignment": {
            "source_index": 3,
            "canonical_mask": n3_mask,
            "edge_count": n3_mask.bit_count(),
            "triangles": [list(triangle) for triangle in triangles],
            "cross_edges": [list(edge) for edge in cross_edges],
            "cross_edge_count": len(cross_edges),
            "cross_edges_form_matching": (
                len({edge[0] for edge in cross_edges}) == len(cross_edges)
                and len({edge[1] for edge in cross_edges}) == len(cross_edges)
            ),
        },
    }


def build_audit(six_path: Path, seven_path: Path) -> tuple[dict[str, object], dict[str, object]]:
    six_tex, seven_tex = read_sources(six_path, seven_path)
    tables = source_tables(six_tex, seven_tex)
    four: dict[int, Poly] = tables["four"]  # type: ignore[assignment]
    five: dict[int, Poly] = tables["five"]  # type: ignore[assignment]
    six: dict[int, Poly] = tables["six"]  # type: ignore[assignment]
    seven: dict[int, Poly] = tables["seven"]  # type: ignore[assignment]
    deck45: list[list[int]] = tables["four_to_five"]  # type: ignore[assignment]
    deck56_raw: list[list[int]] = tables["five_to_six_raw"]  # type: ignore[assignment]

    graph_audit = graph_and_deck_audit(deck45, deck56_raw)
    four_five_residuals = identity_residuals(four, five, deck45, N - 4)
    raw_residuals = identity_residuals(five, six, deck56_raw, N - 5)
    corrected_deck = [row[:] for row in deck56_raw]
    corrected_deck[6][22] += 1
    corrected_residuals = identity_residuals(five, six, corrected_deck, N - 5)
    seven_residuals = seven_derivation_residuals(five, six, seven)

    raw_nonzero = [
        {"row": index + 1, "residual": affine_json(residual)}
        for index, residual in enumerate(raw_residuals)
        if residual
    ]
    raw_result: dict[str, object] = {
        "schema_version": 1,
        "verdict": "FAIL_AS_PRINTED",
        "scope": "Raw printed primary-source deck equations, without repair",
        "source_hashes": {
            "six_tex": SIX_TEX_SHA256,
            "seven_tex": SEVEN_TEX_SHA256,
        },
        "four_to_five_zero_residual_count": sum(not residual for residual in four_five_residuals),
        "five_to_six_raw_zero_residual_count": sum(not residual for residual in raw_residuals),
        "five_to_six_raw_nonzero_residuals": raw_nonzero,
        "raw_graph_deck": graph_audit["five_to_six_raw"],
        "status": "REFUTED_PRINTED_SUPPORTING_EQUATION",
    }

    six_feasible = six_feasibility(six)
    seven_feasible = seven_feasibility(seven, six_feasible["values"])  # type: ignore[arg-type]
    six_sum = vector_sum([six[index] for index in range(1, 63)], [1] * 62)
    corrected_result: dict[str, object] = {
        "schema_version": 1,
        "verdict": "PASS_EXPLICIT_CORRECTION",
        "scope": (
            "Pinned formula feasibility and local graph-deck reconstruction after "
            "the explicit +n23 correction"
        ),
        "source_hashes": {
            "six_tex": SIX_TEX_SHA256,
            "seven_tex": SEVEN_TEX_SHA256,
        },
        "formula_counts": {
            "four": len(four),
            "five": len(five),
            "six": len(six),
            "hamiltonian_seven": len(seven),
        },
        "six_specialized": {
            str(index): affine_json(six[index]) for index in range(1, 63)
        },
        "seven_specialized": {
            str(index): affine_json(seven[index]) for index in range(19)
        },
        "aggregate": {
            "sum_six": affine_json(six_sum),
            "binomial_99_6": math.comb(99, 6),
        },
        "identity_checks": {
            "four_to_five_zero_residual_count": sum(not residual for residual in four_five_residuals),
            "five_to_six_corrected_zero_residual_count": sum(
                not residual for residual in corrected_residuals
            ),
            "seven_derivation_zero_residual_count": sum(
                not residual for residual in seven_residuals
            ),
        },
        "graph_and_deck_audit": graph_audit,
        "six_feasibility": {
            key: value for key, value in six_feasible.items() if key != "values"
        },
        "seven_feasibility": seven_feasible,
        "incumbent_intersection": {
            "n3_values": "705,708,...,4158",
            "count": seven_feasible["incumbent_n3_count"],
            "stronger_lower_bound": None,
            "contradiction": None,
        },
        "status": "RIGOROUS_INCONCLUSIVE_FOR_ENCODED_NECESSARY_CONDITIONS",
        "target_resolution": "UNKNOWN",
        "novelty": "NOT_ASSESSED",
    }

    if raw_result["five_to_six_raw_zero_residual_count"] != 20:
        raise AssertionError(raw_result)
    if raw_nonzero != [
        {
            "row": 7,
            "residual": {
                "constant": "1496880",
                "n3_coefficient": "4",
                "h11_coefficient": "0",
            },
        }
    ]:
        raise AssertionError(raw_nonzero)
    if corrected_result["identity_checks"] != {
        "four_to_five_zero_residual_count": 9,
        "five_to_six_corrected_zero_residual_count": 21,
        "seven_derivation_zero_residual_count": 18,
    }:
        raise AssertionError(corrected_result["identity_checks"])
    return raw_result, corrected_result


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--six-tex", type=Path, required=True)
    parser.add_argument("--seven-tex", type=Path, required=True)
    parser.add_argument("--mode", choices=("raw", "corrected"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    raw, corrected = build_audit(args.six_tex, args.seven_tex)
    if args.mode == "raw":
        write_json(args.output, raw)
        print(
            "FAIL_AS_PRINTED: m7(n-5) has residual n23; "
            "raw N23 deletion-column sum is 5, not 6.",
            file=sys.stderr,
        )
        return 1
    write_json(args.output, corrected)
    print(
        "PASS_EXPLICIT_CORRECTION: +n23 in m7 yields 21/21 deck identities; "
        "encoded count feasibility leaves n3=705,708,...,4158."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
