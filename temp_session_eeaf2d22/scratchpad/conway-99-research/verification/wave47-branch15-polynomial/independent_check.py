#!/usr/bin/env python3
"""Clean-room verifier for the Wave 47 degree-two window calculation.

This file imports no discovery implementation.  It parses the four frozen
inputs, replays propagation, reconstructs all seven local exact-count
theories, enumerates each Hamming slice, and performs squarefree degree-two
polynomial calculus over F_2 using Python integer bit vectors.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import itertools
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, Sequence


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
BASE = ROOT / "attempts/wave37-proof-producing-endpoint/branch-15.opb.gz"
W42 = ROOT / (
    "attempts/wave42-endpoint-certificate/"
    "branch-15-seventh-triangle-delta.opb.gz"
)
CLOSURE_CERT = ROOT / (
    "attempts/wave42-endpoint-certificate/"
    "branch-15-combined-propagation-certificate.json"
)
W43 = ROOT / (
    "attempts/wave43-branch15-two-triangle/"
    "branch-15-two-coordinate-triangle-delta.opb.gz"
)

FROZEN = {
    BASE: (
        "7683599142bfb51dc2d461d56fc1820bc58c658ed5167b17b5004473b589933e",
        574_615,
    ),
    W42: (
        "0840524515920a59fd3d0f0666b496f9e639476dd887d0d90df5bb58a9e8904e",
        64_932,
    ),
    CLOSURE_CERT: (
        "ab05feb596c25d0fbb872a0d92978355638218350bdf7606c248ca98ae2469ce",
        None,
    ),
    W43: (
        "82a13e78e514cf35f27190da665bdedaf4fed28c7a6fa2856e22badf63f32797",
        40_800,
    ),
}

EXPECTED_RAW_HASHES = {
    BASE: "4c1607f4aef7e20569592ccb4ac20dfe30c1e1d220a8fbc0a202554bed6d84e5",
    W42: "348dc5f4bc9ee99511286a8078d0e4ef79786b57ba39ae572c032e42747be77e",
    W43: "23fc3b22b4b235cc631bfd0b53ed2806394273aa1b4c691c883ebe343788d3f1",
}

HEADER = re.compile(
    rb"^\* #variable= ([1-9][0-9]*) #constraint= ([1-9][0-9]*)\r?\n$"
)
LITERAL = re.compile(r"^(~)?x([1-9][0-9]*)$")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def strict_json(path: Path) -> dict[str, object]:
    def unique(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key {key!r}")
            result[key] = value
        return result

    value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique)
    if not isinstance(value, dict):
        raise ValueError(f"top-level JSON is not an object: {path}")
    return value


def canonical(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def object_hash(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


@dataclass(frozen=True)
class Term:
    coefficient: int
    variable: int
    positive: bool


@dataclass(frozen=True)
class Constraint:
    terms: tuple[Term, ...]
    operator: str
    bound: int


def parse_constraint(raw: bytes) -> Constraint:
    """Parse an OPB row, including signed integer weights and <=, >=, =."""

    try:
        text = raw.decode("ascii").strip()
    except UnicodeDecodeError as error:
        raise ValueError("non-ASCII OPB row") from error
    if not text.endswith(";"):
        raise ValueError("OPB row lacks terminator")
    body = text[:-1].strip()
    match = re.fullmatch(r"(.*?)\s+(>=|<=|=)\s+([+-]?[0-9]+)", body)
    if match is None:
        raise ValueError(f"unsupported OPB row: {text[:120]}")
    lhs, operator, bound_text = match.groups()
    tokens = lhs.split()
    if not tokens or len(tokens) % 2:
        raise ValueError("malformed coefficient/literal sequence")
    terms: list[Term] = []
    seen: dict[int, bool] = {}
    for index in range(0, len(tokens), 2):
        coefficient = int(tokens[index])
        literal_match = LITERAL.fullmatch(tokens[index + 1])
        if literal_match is None:
            raise ValueError("malformed literal")
        variable = int(literal_match.group(2))
        positive = literal_match.group(1) is None
        if variable in seen:
            raise ValueError("repeated variable in OPB row")
        seen[variable] = positive
        terms.append(Term(coefficient, variable, positive))
    return Constraint(tuple(terms), operator, int(bound_text))


def iter_formula(path: Path) -> Iterator[tuple[int, bytes, Constraint]]:
    expected_rows = FROZEN[path][1]
    require(isinstance(expected_rows, int), "formula lacks expected row count")
    with gzip.open(path, "rb") as stream:
        header = stream.readline()
        header_match = HEADER.fullmatch(header)
        if header_match is None:
            raise ValueError(f"bad OPB header: {path}")
        require(int(header_match.group(1)) == 289_338, "variable count changed")
        require(
            int(header_match.group(2)) == expected_rows,
            f"declared row count changed: {path}",
        )
        observed = 0
        for observed, raw in enumerate(stream, 1):
            yield observed, raw, parse_constraint(raw)
        require(observed == expected_rows, f"observed row count changed: {path}")


def decompressed_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with gzip.open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def input_checks() -> dict[str, object]:
    records: dict[str, object] = {}
    for path, (expected, rows) in FROZEN.items():
        actual = sha256_file(path)
        require(actual == expected, f"frozen SHA-256 mismatch: {path}")
        record: dict[str, object] = {"sha256": actual}
        if rows is not None:
            raw_hash = decompressed_hash(path)
            require(
                raw_hash == EXPECTED_RAW_HASHES[path],
                f"decompressed SHA-256 mismatch: {path}",
            )
            record.update({"rows": rows, "decompressed_sha256": raw_hash})
        records[path.relative_to(ROOT).as_posix()] = record
    return records


def feasible_interval(operator: str, bound: int, low: int, high: int) -> bool:
    if operator == ">=":
        return high >= bound
    if operator == "<=":
        return low <= bound
    if operator == "=":
        return low <= bound <= high
    raise ValueError(f"unsupported operator {operator!r}")


def propagate_constraint(
    constraint: Constraint, assignments: dict[int, bool]
) -> tuple[bool, list[tuple[int, bool]]]:
    """Return feasibility and every literal truth value forced by the row."""

    if any(term.coefficient <= 0 for term in constraint.terms):
        raise ValueError("frozen propagation formula has a nonpositive weight")
    fixed = 0
    open_terms: list[Term] = []
    for term in constraint.terms:
        value = assignments.get(term.variable)
        if value is None:
            open_terms.append(term)
        elif value is term.positive:
            fixed += term.coefficient
    remaining = sum(term.coefficient for term in open_terms)
    if not feasible_interval(constraint.operator, constraint.bound, fixed, fixed + remaining):
        return False, []
    forced: list[tuple[int, bool]] = []
    for term in open_terms:
        false_ok = feasible_interval(
            constraint.operator,
            constraint.bound,
            fixed,
            fixed + remaining - term.coefficient,
        )
        true_ok = feasible_interval(
            constraint.operator,
            constraint.bound,
            fixed + term.coefficient,
            fixed + remaining,
        )
        if not false_ok and not true_ok:
            return False, []
        if not false_ok:
            forced.append((term.variable, term.positive))
        elif not true_ok:
            forced.append((term.variable, not term.positive))
    return True, forced


def replay_closure() -> tuple[dict[int, bool], list[dict[str, int]], str]:
    assignments: dict[int, bool] = {}
    passes: list[dict[str, int]] = []
    for pass_number in itertools.count(1):
        before = len(assignments)
        for path in (BASE, W42):
            for row, _raw, constraint in iter_formula(path):
                feasible, forced = propagate_constraint(constraint, assignments)
                if not feasible:
                    raise ValueError(f"propagation contradiction: {path}:{row}")
                for variable, value in forced:
                    prior = assignments.get(variable)
                    if prior is not None and prior is not value:
                        raise ValueError("propagation assignment conflict")
                    assignments.setdefault(variable, value)
        passes.append(
            {
                "pass": pass_number,
                "before": before,
                "after": len(assignments),
                "new": len(assignments) - before,
            }
        )
        if len(assignments) == before:
            break
    require(len(assignments) == 830, "closure cardinality changed")

    certificate = strict_json(CLOSURE_CERT)
    derivations = certificate.get("derivations")
    require(isinstance(derivations, list), "closure derivations missing")
    archived: dict[int, bool] = {}
    for item in derivations:
        require(isinstance(item, dict), "non-object closure derivation")
        variable = item.get("variable")
        value = item.get("value")
        require(type(variable) is int and type(value) is bool, "bad closure entry")
        require(variable not in archived, "duplicate closure variable")
        archived[variable] = value
    require(archived == assignments, "replayed closure != frozen certificate")
    stream = "".join(
        f"{variable}={int(assignments[variable])}\n"
        for variable in sorted(assignments)
    ).encode("ascii")
    return assignments, passes, hashlib.sha256(stream).hexdigest()


def scaffold() -> tuple[
    tuple[tuple[int, int], ...],
    tuple[tuple[int, int], ...],
    dict[tuple[int, int], int],
]:
    labels = tuple(
        pair
        for pair in itertools.combinations(range(14), 2)
        if pair[1] != (pair[0] ^ 1)
    )
    require(len(labels) == 84 and len(set(labels)) == 84, "label map changed")
    edges = tuple(itertools.combinations(range(84), 2))
    variable = {edge: index for index, edge in enumerate(edges, 1)}
    require(len(edges) == 3_486, "primary variable map changed")
    for edge, index in variable.items():
        require(edges[index - 1] == edge, "edge map is not reversible")
        require(edge[0] < edge[1], "loop or reversed primary edge")
    return labels, edges, variable


@dataclass(frozen=True)
class Window:
    index: int
    coordinates: tuple[int, int]
    vertices: tuple[int, ...]
    variables: tuple[int, ...]
    free_variables: tuple[int, ...]


def windows(assignments: dict[int, bool]) -> tuple[Window, ...]:
    labels, edges, _variables = scaffold()
    result: list[Window] = []
    coordinate_coverage: list[int] = []
    label_memberships = Counter()
    for index in range(7):
        coordinates = (2 * index, 2 * index + 1)
        coordinate_coverage.extend(coordinates)
        vertices = tuple(
            label_index
            for label_index, label in enumerate(labels)
            if any(coordinate in label for coordinate in coordinates)
        )
        for vertex in vertices:
            label_memberships[vertex] += 1
        variables = tuple(
            variable
            for variable, edge in enumerate(edges, 1)
            if edge[0] in vertices and edge[1] in vertices
        )
        require(len(vertices) == 24, "window vertex count changed")
        require(len(variables) == 276, "window variable count changed")
        result.append(
            Window(
                index,
                coordinates,
                vertices,
                variables,
                tuple(variable for variable in variables if variable not in assignments),
            )
        )
    require(sorted(coordinate_coverage) == list(range(14)), "mate pairs do not partition coordinates")
    require(set(label_memberships) == set(range(84)), "labels not covered by windows")
    require(set(label_memberships.values()) == {2}, "each residual label must occur in exactly two windows")
    return tuple(result)


def row_signature(constraint: Constraint) -> tuple[tuple[tuple[int, bool], ...], str, int]:
    return (
        tuple((term.variable, term.positive) for term in constraint.terms),
        constraint.operator,
        constraint.bound,
    )


def expected_incidence_rows() -> set[tuple[tuple[tuple[int, bool], ...], str, int]]:
    labels, _edges, variable = scaffold()
    expected = set()
    for label_index, label in enumerate(labels):
        for coordinate in range(14):
            fibre = [
                other
                for other, other_label in enumerate(labels)
                if coordinate in other_label and other != label_index
            ]
            variables = tuple(
                variable[tuple(sorted((label_index, other)))] for other in fibre
            )
            target = (
                2
                - int(coordinate in label)
                - int((coordinate ^ 1) in label)
            )
            expected.add(
                (tuple((item, True) for item in variables), ">=", target)
            )
            expected.add(
                (
                    tuple((item, False) for item in variables),
                    ">=",
                    len(variables) - target,
                )
            )
    require(len(expected) == 2_352, "expected incidence row count changed")
    return expected


def verify_incidence_rows() -> dict[str, object]:
    expected = expected_incidence_rows()
    observed = Counter()
    for _row, _raw, constraint in iter_formula(BASE):
        signature = row_signature(constraint)
        if signature in expected:
            observed[signature] += 1
    missing = expected - set(observed)
    duplicates = sum(count - 1 for count in observed.values())
    require(not missing, f"{len(missing)} incidence rows missing from base OPB")
    require(duplicates == 0, "duplicate complete incidence row")
    require(len(observed) == 2_352, "incidence row coverage changed")
    return {"expected_rows": 2_352, "matched_rows": len(observed), "duplicates": 0}


@dataclass(frozen=True)
class MonomialMap:
    free_variables: tuple[int, ...]
    variable_position: dict[int, int]
    pair_position: dict[tuple[int, int], int]
    column_token: tuple[str, ...]
    column_count: int


def monomial_map(free_variables: tuple[int, ...]) -> MonomialMap:
    positions = {variable: index for index, variable in enumerate(free_variables)}
    pairs: dict[tuple[int, int], int] = {}
    offset = 1 + len(free_variables)
    for pair_index, pair in enumerate(
        itertools.combinations(range(len(free_variables)), 2)
    ):
        pairs[pair] = offset + pair_index
    tokens = ["1"]
    tokens.extend(f"x{variable}" for variable in free_variables)
    tokens.extend(
        f"x{free_variables[left]}*x{free_variables[right]}"
        for left, right in itertools.combinations(range(len(free_variables)), 2)
    )
    return MonomialMap(
        free_variables,
        positions,
        pairs,
        tuple(tokens),
        1 + len(free_variables) + len(pairs),
    )


def local_terms(variable_count: int) -> tuple[tuple[int, ...], ...]:
    return (
        ((),)
        + tuple((index,) for index in range(variable_count))
        + tuple(itertools.combinations(range(variable_count), 2))
    )


def evaluation_row(assignment: frozenset[int], terms: Sequence[tuple[int, ...]]) -> int:
    result = 0
    for column, term in enumerate(terms):
        if all(variable in assignment for variable in term):
            result |= 1 << column
    return result


def nullspace(equations: Sequence[int], column_count: int) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """Return RREF equations and a canonical nullspace basis over F_2."""

    rows = [row for row in equations if row]
    pivot_columns: list[int] = []
    rank = 0
    for column in range(column_count):
        pivot = next(
            (index for index in range(rank, len(rows)) if (rows[index] >> column) & 1),
            None,
        )
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for index in range(len(rows)):
            if index != rank and ((rows[index] >> column) & 1):
                rows[index] ^= rows[rank]
        pivot_columns.append(column)
        rank += 1
        if rank == len(rows):
            break
    rows = rows[:rank]
    pivot_set = set(pivot_columns)
    basis: list[int] = []
    for free in range(column_count):
        if free in pivot_set:
            continue
        vector = 1 << free
        for row_index, pivot_column in enumerate(pivot_columns):
            if (rows[row_index] >> free) & 1:
                vector |= 1 << pivot_column
        basis.append(vector)
    for equation in equations:
        for vector in basis:
            require((equation & vector).bit_count() % 2 == 0, "bad nullspace row")
    require(len(basis) + rank == column_count, "rank-nullity failure")
    return tuple(rows), tuple(basis)


def embed_local_polynomial(
    local_row: int,
    local_variables: Sequence[int],
    terms: Sequence[tuple[int, ...]],
    mapping: MonomialMap,
) -> int:
    result = 0
    for local_column, term in enumerate(terms):
        if not ((local_row >> local_column) & 1):
            continue
        if not term:
            position = 0
        elif len(term) == 1:
            position = 1 + mapping.variable_position[local_variables[term[0]]]
        else:
            left = mapping.variable_position[local_variables[term[0]]]
            right = mapping.variable_position[local_variables[term[1]]]
            position = mapping.pair_position[tuple(sorted((left, right)))]
        result ^= 1 << position
    return result


def polynomial_tokens(row: int, mapping: MonomialMap) -> list[str]:
    tokens: list[str] = []
    while row:
        least = row & -row
        column = least.bit_length() - 1
        tokens.append(mapping.column_token[column])
        row ^= least
    return tokens


def polynomial_catalog_hash(rows: Iterable[int], mapping: MonomialMap) -> str:
    return object_hash([polynomial_tokens(row, mapping) for row in rows])


class XorBasis:
    """Highest-column-pivot echelon basis for Python integer bit rows."""

    def __init__(self, rows: Iterable[int] = ()) -> None:
        self.rows: dict[int, int] = {}
        for row in rows:
            self.add(row)

    def reduce(self, row: int) -> int:
        while row:
            pivot = row.bit_length() - 1
            prior = self.rows.get(pivot)
            if prior is None:
                return row
            row ^= prior
        return 0

    def add(self, row: int) -> bool:
        row = self.reduce(row)
        if not row:
            return False
        self.rows[row.bit_length() - 1] = row
        return True

    def canonical_rows(self) -> tuple[int, ...]:
        rows = dict(self.rows)
        pivots = sorted(rows)
        for pivot in pivots:
            reducer = rows[pivot]
            for higher in pivots:
                if higher > pivot and ((rows[higher] >> pivot) & 1):
                    rows[higher] ^= reducer
        return tuple(rows[pivot] for pivot in sorted(rows, reverse=True))

    def echelon_rows(self) -> tuple[int, ...]:
        return tuple(self.rows[pivot] for pivot in sorted(self.rows, reverse=True))

    def linear_rows(self, linear_maximum_column: int) -> tuple[int, ...]:
        rows = [
            row
            for pivot, row in self.rows.items()
            if pivot <= linear_maximum_column
        ]
        return XorBasis(rows).canonical_rows()

    @property
    def rank(self) -> int:
        return len(self.rows)


def multiply_affine_by_variable(row: int, variable_index: int, mapping: MonomialMap) -> int:
    require(row >> (1 + len(mapping.free_variables)) == 0, "row is not affine")
    result = 0
    if row & 1:
        result ^= 1 << (1 + variable_index)
    for other in range(len(mapping.free_variables)):
        if not ((row >> (1 + other)) & 1):
            continue
        if other == variable_index:
            result ^= 1 << (1 + other)
        else:
            result ^= 1 << mapping.pair_position[tuple(sorted((other, variable_index)))]
    return result


def saturate(rows: Sequence[int], mapping: MonomialMap) -> tuple[XorBasis, list[dict[str, int]]]:
    basis = XorBasis(rows)
    history: list[dict[str, int]] = []
    for iteration in itertools.count(1):
        linear = basis.linear_rows(len(mapping.free_variables))
        before = basis.rank
        attempted = 0
        added = 0
        for row in linear:
            for variable_index in range(len(mapping.free_variables)):
                attempted += 1
                added += int(
                    basis.add(multiply_affine_by_variable(row, variable_index, mapping))
                )
        history.append(
            {
                "iteration": iteration,
                "linear_rank": len(linear),
                "products_attempted": attempted,
                "rows_added": added,
                "rank_before": before,
                "rank_after": basis.rank,
            }
        )
        if not added:
            return basis, history


def clause_polynomial(
    residual: Sequence[tuple[int, bool]], mapping: MonomialMap
) -> int:
    terms: set[tuple[int, ...]] = {()}
    for variable, positive in residual:
        index = mapping.variable_position[variable]
        factor = {(), (index,)} if positive else {(index,)}
        product: set[tuple[int, ...]] = set()
        for left in terms:
            for right in factor:
                combined = tuple(sorted(set(left).union(right)))
                require(len(combined) <= 2, "clause exceeds degree two")
                if combined in product:
                    product.remove(combined)
                else:
                    product.add(combined)
        terms = product
    result = 0
    for term in terms:
        if not term:
            column = 0
        elif len(term) == 1:
            column = 1 + term[0]
        else:
            column = mapping.pair_position[(term[0], term[1])]
        result ^= 1 << column
    return result


def simplify_clause(
    constraint: Constraint, assignments: dict[int, bool]
) -> tuple[str, tuple[tuple[int, bool], ...]]:
    require(
        constraint.operator == ">="
        and constraint.bound == 1
        and all(term.coefficient == 1 for term in constraint.terms),
        "row is not a clause",
    )
    signs: dict[int, bool] = {}
    for term in constraint.terms:
        prior = signs.get(term.variable)
        if prior is not None and prior is not term.positive:
            return "TAUTOLOGY", ()
        signs[term.variable] = term.positive
        value = assignments.get(term.variable)
        if value is term.positive:
            return "SATISFIED", ()
    residual = tuple(
        (term.variable, term.positive)
        for term in constraint.terms
        if term.variable not in assignments
    )
    if not residual:
        return "CONTRADICTION", ()
    return "ACTIVE", residual


def window_memberships(
    variables: Sequence[int], all_windows: Sequence[Window]
) -> list[int]:
    requested = set(variables)
    return [
        window.index
        for window in all_windows
        if requested.issubset(set(window.variables))
    ]


def eligible_clause_catalogues(
    assignments: dict[int, bool], all_windows: Sequence[Window]
) -> tuple[list[list[dict[str, object]]], dict[str, object]]:
    catalogues: list[list[dict[str, object]]] = [[] for _ in all_windows]
    statistics = Counter()
    for source, path in (("base", BASE), ("wave42", W42)):
        for row_number, _raw, constraint in iter_formula(path):
            if not (
                constraint.operator == ">="
                and constraint.bound == 1
                and all(term.coefficient == 1 for term in constraint.terms)
            ):
                continue
            state, residual = simplify_clause(constraint, assignments)
            statistics[f"{source}_{state.lower()}"] += 1
            if state != "ACTIVE":
                continue
            statistics[f"{source}_active_width_{len(residual)}"] += 1
            if len(residual) > 2:
                continue
            variables = [variable for variable, _positive in residual]
            if any(variable > 3_486 for variable in variables):
                statistics["width_le_2_nonprimary"] += 1
                continue
            memberships = window_memberships(variables, all_windows)
            if not memberships:
                statistics["width_le_2_outside_windows"] += 1
                continue
            require(len(memberships) == 1, "eligible clause lies in multiple windows")
            window = memberships[0]
            catalogues[window].append(
                {
                    "source": source,
                    "row": row_number,
                    "literals": [
                        {"variable": variable, "positive": positive}
                        for variable, positive in residual
                    ],
                }
            )
    for catalogue in catalogues:
        catalogue.sort(
            key=lambda item: (
                item["source"],
                item["row"],
                tuple(
                    (literal["variable"], literal["positive"])
                    for literal in item["literals"]
                ),
            )
        )
    return catalogues, dict(sorted(statistics.items()))


def exact_blocks_for_window(
    window: Window,
    assignments: dict[int, bool],
    mapping: MonomialMap,
) -> tuple[list[dict[str, object]], list[int]]:
    labels, _edges, variable = scaffold()
    blocks: list[dict[str, object]] = []
    axiom_rows: list[int] = []
    for label_index in window.vertices:
        for coordinate in window.coordinates:
            fibre = [
                other
                for other, label in enumerate(labels)
                if coordinate in label and other != label_index
            ]
            complete_variables = tuple(
                variable[tuple(sorted((label_index, other)))] for other in fibre
            )
            require(len(complete_variables) in (11, 12), "incomplete incidence block")
            require(len(set(complete_variables)) == len(complete_variables), "repeated block variable")
            full_target = (
                2
                - int(coordinate in labels[label_index])
                - int((coordinate ^ 1) in labels[label_index])
            )
            fixed_true = sum(assignments.get(item) is True for item in complete_variables)
            active_variables = tuple(
                item for item in complete_variables if item not in assignments
            )
            target = full_target - fixed_true
            require(0 <= target <= len(active_variables), "contradictory simplified exact block")
            require(set(active_variables).issubset(mapping.variable_position), "block escapes window")

            terms = local_terms(len(active_variables))
            slices = tuple(
                frozenset(chosen)
                for chosen in itertools.combinations(range(len(active_variables)), target)
            )
            evaluations = tuple(evaluation_row(item, terms) for item in slices)
            evaluation_rref, kernel = nullspace(evaluations, len(terms))
            embedded = tuple(
                embed_local_polynomial(row, active_variables, terms, mapping)
                for row in kernel
            )
            # nullspace() has already evaluated every local kernel row on
            # every point of the complete slice.  Embedding is an injective
            # monomial relabelling, checked here without an O(global_basis)
            # rescan for every row and point.
            require(len(set(embedded)) == len(embedded), "embedding merged local axioms")
            require(all(row for row in embedded), "zero local axiom was emitted")
            axiom_rows.extend(embedded)
            blocks.append(
                {
                    "label_index": label_index,
                    "label": list(labels[label_index]),
                    "coordinate": coordinate,
                    "complete_variables": list(complete_variables),
                    "full_target": full_target,
                    "fixed_true": fixed_true,
                    "active_variables": list(active_variables),
                    "target": target,
                    "slice_count": len(slices),
                    "monomial_count": len(terms),
                    "evaluation_rank": len(evaluation_rref),
                    "kernel_dimension": len(kernel),
                    "kernel_sha256": polynomial_catalog_hash(embedded, mapping),
                }
            )
    require(len(blocks) == 48, "window does not have 48 exact blocks")
    return blocks, axiom_rows


def quotient_rows(
    smaller_rows: Sequence[int], larger_rows: Sequence[int]
) -> tuple[int, ...]:
    smaller = XorBasis(smaller_rows)
    quotient = XorBasis()
    for row in larger_rows:
        residual = smaller.reduce(row)
        if residual:
            quotient.add(residual)
    return quotient.canonical_rows()


def analyze_window(
    window: Window,
    assignments: dict[int, bool],
    clause_catalogue: list[dict[str, object]],
) -> dict[str, object]:
    mapping = monomial_map(window.free_variables)
    blocks, exact_axioms = exact_blocks_for_window(window, assignments, mapping)
    clause_rows: list[int] = []
    for item in clause_catalogue:
        residual = tuple(
            (literal["variable"], literal["positive"])
            for literal in item["literals"]
        )
        row = clause_polynomial(residual, mapping)
        require(row, "tautological clause entered axiom catalogue")
        clause_rows.append(row)

    initial_rows = [*exact_axioms, *clause_rows]
    initial_basis = XorBasis(initial_rows)
    initial_echelon = initial_basis.echelon_rows()
    initial_linear = initial_basis.linear_rows(len(mapping.free_variables))
    saturated, saturation_history = saturate(initial_rows, mapping)
    saturated_echelon = saturated.echelon_rows()
    final_linear = saturated.linear_rows(len(mapping.free_variables))
    new_rows = quotient_rows(initial_linear, final_linear)
    require(len(new_rows) == len(final_linear) - len(initial_linear), "bad quotient rank")
    require(not any(row == 1 for row in final_linear), "constant-one contradiction")

    exact_initial_basis = XorBasis(exact_axioms)
    exact_saturated, exact_history = saturate(exact_axioms, mapping)
    exact_final_linear = exact_saturated.linear_rows(len(mapping.free_variables))
    for row in final_linear:
        require(XorBasis(exact_final_linear).reduce(row) == 0, "clause theory exceeds exact control")
    for row in exact_final_linear:
        require(XorBasis(final_linear).reduce(row) == 0, "exact control exceeds clause theory")

    final_constants = sum(bool(row & 1) for row in final_linear)
    zero_assignment_satisfies = final_constants == 0
    return {
        "window": window.index,
        "coordinates": list(window.coordinates),
        "vertices": list(window.vertices),
        "variables": list(window.variables),
        "free_variables": list(window.free_variables),
        "fixed_variable_count": len(window.variables) - len(window.free_variables),
        "monomial_count": mapping.column_count,
        "block_count": len(blocks),
        "blocks_sha256": object_hash(blocks),
        "blocks": blocks,
        "exact_axiom_catalog_count": len(exact_axioms),
        "exact_axiom_catalog_sha256": polynomial_catalog_hash(exact_axioms, mapping),
        "eligible_clause_count": len(clause_catalogue),
        "eligible_clause_catalog_sha256": object_hash(clause_catalogue),
        "eligible_clause_polynomial_sha256": polynomial_catalog_hash(clause_rows, mapping),
        "initial_rank": initial_basis.rank,
        "initial_echelon_sha256": polynomial_catalog_hash(initial_echelon, mapping),
        "initial_linear_rank": len(initial_linear),
        "initial_linear_rref_sha256": polynomial_catalog_hash(initial_linear, mapping),
        "saturation": saturation_history,
        "saturated_rank": saturated.rank,
        "saturated_echelon_sha256": polynomial_catalog_hash(saturated_echelon, mapping),
        "final_linear_rank": len(final_linear),
        "final_linear_rref": [polynomial_tokens(row, mapping) for row in final_linear],
        "final_linear_rref_sha256": polynomial_catalog_hash(final_linear, mapping),
        "new_linear_rank": len(new_rows),
        "new_linear_rref": [polynomial_tokens(row, mapping) for row in new_rows],
        "new_linear_rref_sha256": polynomial_catalog_hash(new_rows, mapping),
        "contradiction": any(row == 1 for row in final_linear),
        "affine_rows_with_constant_one": final_constants,
        "zero_assignment_satisfies_final_linear_space": zero_assignment_satisfies,
        "exact_only": {
            "initial_rank": exact_initial_basis.rank,
            "saturation": exact_history,
            "saturated_rank": exact_saturated.rank,
            "final_linear_rank": len(exact_final_linear),
            "final_linear_rref_sha256": polynomial_catalog_hash(exact_final_linear, mapping),
            "mutual_rowspace_equality": True,
        },
    }


def wave43_partition(
    assignments: dict[int, bool], all_windows: Sequence[Window]
) -> dict[str, object]:
    active: list[dict[str, object]] = []
    satisfied = 0
    per_window = Counter()
    stream_by_window: list[list[list[int]]] = [[] for _ in all_windows]
    for row_number, _raw, constraint in iter_formula(W43):
        require(
            constraint.operator == ">="
            and constraint.bound == 1
            and all(term.coefficient == 1 for term in constraint.terms),
            "Wave43 row is not a clause",
        )
        require(
            all(not term.positive for term in constraint.terms),
            "Wave43 row has a positive literal",
        )
        state, residual = simplify_clause(constraint, assignments)
        if state == "SATISFIED":
            satisfied += 1
            continue
        require(state == "ACTIVE", "Wave43 row is tautological or contradictory")
        variables = tuple(variable for variable, positive in residual)
        require(not any(positive for _variable, positive in residual), "active polarity flipped")
        require(len(variables) == 4 and len(set(variables)) == 4, "active cut is not width four")
        require(all(variable <= 3_486 for variable in variables), "active cut uses auxiliary variable")
        memberships = window_memberships(variables, all_windows)
        require(len(memberships) == 1, "active cut belongs to zero or multiple windows")
        window = memberships[0]
        per_window[window] += 1
        stream_by_window[window].append(list(variables))
        active.append(
            {"row": row_number, "window": window, "variables": list(variables)}
        )
    require(len(active) == 34_340 and satisfied == 6_460, "Wave43 active partition count changed")
    require(sum(per_window.values()) == len(active), "Wave43 partition is incomplete")
    return {
        "raw_rows": 40_800,
        "closure_satisfied_rows": satisfied,
        "active_rows": len(active),
        "all_negative_width_four": True,
        "degree_of_falsifying_monomial": 4,
        "per_window_counts": [per_window[index] for index in range(7)],
        "active_catalog_sha256": object_hash(active),
        "per_window_catalog_sha256": [
            object_hash(stream) for stream in stream_by_window
        ],
    }


def memory_snapshot() -> dict[str, float] | None:
    """Read Linux procfs when available; Windows RAM is checked by the caller."""

    path = Path("/proc/meminfo")
    if not path.exists():
        return None
    values = {}
    for line in path.read_text().splitlines():
        key, value = line.split(":", 1)
        values[key] = int(value.strip().split()[0])
    total = values["MemTotal"]
    available = values["MemAvailable"]
    return {
        "total_gib": round(total / 1024 / 1024, 3),
        "available_gib": round(available / 1024 / 1024, 3),
        "available_percent": round(100 * available / total, 3),
    }


def compute() -> dict[str, object]:
    inputs = input_checks()
    print("progress: input hashes", file=sys.stderr, flush=True)
    assignments, passes, assignment_hash = replay_closure()
    print("progress: closure replay", file=sys.stderr, flush=True)
    incidence = verify_incidence_rows()
    print("progress: incidence rows", file=sys.stderr, flush=True)
    all_windows = windows(assignments)
    clauses, clause_statistics = eligible_clause_catalogues(assignments, all_windows)
    print("progress: clause catalogues", file=sys.stderr, flush=True)
    analyses = []
    for window in all_windows:
        analyses.append(analyze_window(window, assignments, clauses[window.index]))
        print(f"progress: window {window.index}", file=sys.stderr, flush=True)
    partition = wave43_partition(assignments, all_windows)
    print("progress: Wave43 partition", file=sys.stderr, flush=True)
    new_ranks = [int(item["new_linear_rank"]) for item in analyses]
    new_relations = [
        relation
        for item in analyses
        for relation in item["new_linear_rref"]
    ]
    return {
        "format": "wave47-branch15-polynomial-independent-v1",
        "role": "verifier",
        "claim_label": "CANDIDATE_PRECOMPARISON",
        "scope": (
            "seven labelled mate-coordinate windows in frozen branch 15, "
            "squarefree F2 polynomial calculus truncated at degree two"
        ),
        "inputs": inputs,
        "closure": {
            "passes": passes,
            "forced_variables": len(assignments),
            "forced_primary_variables": sum(variable <= 3_486 for variable in assignments),
            "positive_primary_variables": sum(
                variable <= 3_486 and value
                for variable, value in assignments.items()
            ),
            "negative_primary_variables": sum(
                variable <= 3_486 and not value
                for variable, value in assignments.items()
            ),
            "assignment_stream_sha256": assignment_hash,
            "exactly_matches_certificate": True,
        },
        "incidence_rows": incidence,
        "clause_statistics": clause_statistics,
        "windows": analyses,
        "summary": {
            "window_count": len(analyses),
            "vertex_counts": [len(item["vertices"]) for item in analyses],
            "variable_counts": [len(item["variables"]) for item in analyses],
            "free_variable_counts": [len(item["free_variables"]) for item in analyses],
            "block_counts": [item["block_count"] for item in analyses],
            "eligible_clause_counts": [item["eligible_clause_count"] for item in analyses],
            "new_linear_ranks": new_ranks,
            "new_relation_count": len(new_relations),
            "new_relations": new_relations,
            "contradiction_count": sum(bool(item["contradiction"]) for item in analyses),
            "zero_assignment_window_count": sum(
                bool(item["zero_assignment_satisfies_final_linear_space"])
                for item in analyses
            ),
            "affine_constant_one_row_counts": [
                item["affine_rows_with_constant_one"] for item in analyses
            ],
            "exact_only_equal_window_count": sum(
                bool(item["exact_only"]["mutual_rowspace_equality"])
                for item in analyses
            ),
        },
        "wave43_degree_four_partition": partition,
        "memory_snapshot_if_procfs": memory_snapshot(),
        "limitations": [
            "The calculation is local to seven overlapping labelled vertex windows.",
            "Only active residual clauses of width at most two enter degree two.",
            "All active Wave43 cuts have degree four and are omitted from degree two.",
            "No cross-window multiplication or omitted wider clause is represented.",
            "No automorphism of a completed graph is assumed.",
            "This is not a SAT, UNSAT, endpoint-exclusion, upper-bound, or Conway-99 certificate.",
        ],
    }


def validate(result: dict[str, object]) -> None:
    require(result["format"] == "wave47-branch15-polynomial-independent-v1", "bad format")
    closure = result["closure"]
    require(isinstance(closure, dict), "closure missing")
    require(closure["forced_variables"] == 830, "closure size mismatch")
    require(closure["forced_primary_variables"] == 174, "primary closure size mismatch")
    summary = result["summary"]
    require(isinstance(summary, dict), "summary missing")
    require(summary["window_count"] == 7, "window count mismatch")
    require(summary["vertex_counts"] == [24] * 7, "vertex counts mismatch")
    require(summary["variable_counts"] == [276] * 7, "variable counts mismatch")
    require(summary["block_counts"] == [48] * 7, "block counts mismatch")
    require(summary["contradiction_count"] == 0, "unexpected contradiction")
    require(summary["exact_only_equal_window_count"] == 7, "exact-only control failed")
    partition = result["wave43_degree_four_partition"]
    require(isinstance(partition, dict), "partition missing")
    require(partition["active_rows"] == 34_340, "active Wave43 count mismatch")
    require(
        partition["per_window_counts"] == [4_141, 0, 5_959, 6_060, 6_060, 6_060, 6_060],
        "Wave43 partition profile changed",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--compute", metavar="OUTPUT")
    group.add_argument("--validate", metavar="INPUT")
    args = parser.parse_args()
    if args.compute:
        result = compute()
        validate(result)
        Path(args.compute).write_bytes(canonical(result))
    else:
        result = strict_json(Path(args.validate))
        validate(result)
    print("PASS: clean-room Wave47 degree-two window calculation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
