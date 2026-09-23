#!/usr/bin/env python3
"""Degree-2 squarefree F2 closure on exact branch-15 coordinate windows.

This is a bounded algebraic scout, not an UNSAT prover.  It imports the exact
Wave 37 branch-15 OPB, the Wave 42 prism delta and closure, and the Wave 43
two-coordinate-triangle prism delta.  For each matched coordinate pair
``(2k, 2k+1)`` it takes the 24 residual labels containing one of the two
coordinates and all 276 residual-edge variables among those labels.

The polynomial system is the following rigorously restricted one.

* Work in the squarefree Boolean quotient
  ``F2[x_1,...,x_m] / <x_i^2-x_i>``.
* Retain every exact coordinate-incidence block from the frozen OPB whose
  complete support is inside the 276-variable window.  After applying the
  SHA-bound Wave 42 closure, insert the complete vector space of degree-at-most
  two polynomials that vanishes on the corresponding exact Hamming slice.
* Retain every frozen OPB clause which, after the same closure, is active, has
  complete residual support inside the window, and has residual width at most
  two.  Insert its usual falsifying-assignment polynomial.
* Close under addition and every multiplication by a window variable that
  stays within degree two.  Equivalently, every derived linear row is
  multiplied by every free window variable until the Macaulay row space
  stabilizes.

Rows outside the window, residual clauses of width at least three, and all
degree-three-or-higher consequences are deliberately omitted.  In particular,
the active Wave 43 cuts have residual width four and cannot enter an unassumed
degree-2 (or degree-3) polynomial-calculus matrix.
"""

from __future__ import annotations

import argparse
import ctypes
import gzip
import hashlib
import itertools
import json
import os
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


HERE = Path(__file__).resolve().parent
REPOSITORY_ROOT = HERE.parents[1]
WAVE42_ROOT = REPOSITORY_ROOT / "attempts" / "wave42-endpoint-certificate"
for import_root in (WAVE42_ROOT,):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

import seventh_triangle_strengthen as wave42  # noqa: E402


BASE_OPB = (
    REPOSITORY_ROOT
    / "attempts"
    / "wave37-proof-producing-endpoint"
    / "branch-15.opb.gz"
)
WAVE42_DELTA = WAVE42_ROOT / "branch-15-seventh-triangle-delta.opb.gz"
WAVE43_DELTA = (
    REPOSITORY_ROOT
    / "attempts"
    / "wave43-branch15-two-triangle"
    / "branch-15-two-coordinate-triangle-delta.opb.gz"
)
CLOSURE = WAVE42_ROOT / "branch-15-combined-propagation-certificate.json"
DEFAULT_OUTPUT = HERE / "degree2-window-result.json"

EXPECTED = {
    BASE_OPB: {
        "gzip": "7683599142bfb51dc2d461d56fc1820bc58c658ed5167b17b5004473b589933e",
        "raw": "4c1607f4aef7e20569592ccb4ac20dfe30c1e1d220a8fbc0a202554bed6d84e5",
        "constraints": 574_615,
    },
    WAVE42_DELTA: {
        "gzip": "0840524515920a59fd3d0f0666b496f9e639476dd887d0d90df5bb58a9e8904e",
        "raw": "348dc5f4bc9ee99511286a8078d0e4ef79786b57ba39ae572c032e42747be77e",
        "constraints": 64_932,
    },
    WAVE43_DELTA: {
        "gzip": "82a13e78e514cf35f27190da665bdedaf4fed28c7a6fa2856e22badf63f32797",
        "raw": "23fc3b22b4b235cc631bfd0b53ed2806394273aa1b4c691c883ebe343788d3f1",
        "constraints": 40_800,
    },
    CLOSURE: {
        "sha256": "ab05feb596c25d0fbb872a0d92978355638218350bdf7606c248ca98ae2469ce"
    },
}

TERM_RE = re.compile(rb"\+1 (~)?x([1-9][0-9]*)")
BOUND_RE = re.compile(rb">= ([0-9]+) ;\n$")
HEADER_RE = re.compile(
    rb"^\* #variable= ([1-9][0-9]*) #constraint= ([1-9][0-9]*)\n$"
)
PRIMARY_VARIABLES = 3_486
MIN_FREE_MEMORY_PERCENT = 20.0

Monomial = tuple[int, ...]


@dataclass(frozen=True)
class Constraint:
    source: str
    row: int
    raw_sha256: str
    literals: tuple[tuple[int, bool], ...]
    bound: int


class SparseReducer:
    """Deterministic sparse Gaussian elimination with Python-int bit rows."""

    def __init__(self, max_linear_column: int) -> None:
        self.pivots: dict[int, int] = {}
        self.max_linear_column = max_linear_column
        self.input_rows = 0
        self.zero_rows = 0
        self.low_pivot_queue: list[int] = []

    def add(self, row: int) -> tuple[bool, int]:
        self.input_rows += 1
        reduced = row
        while reduced:
            pivot = reduced.bit_length() - 1
            old = self.pivots.get(pivot)
            if old is None:
                self.pivots[pivot] = reduced
                if pivot <= self.max_linear_column:
                    self.low_pivot_queue.append(reduced)
                return True, reduced
            reduced ^= old
        self.zero_rows += 1
        return False, 0

    def echelon_sha256(self) -> str:
        digest = hashlib.sha256()
        for pivot in sorted(self.pivots):
            payload = self.pivots[pivot].to_bytes(
                (self.pivots[pivot].bit_length() + 7) // 8,
                "little",
            )
            digest.update(f"{pivot}:{len(payload)}:".encode("ascii"))
            digest.update(payload)
            digest.update(b"\n")
        return digest.hexdigest()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical_payload(data: object) -> bytes:
    return (json.dumps(data, indent=2, sort_keys=True) + "\n").encode("utf-8")


def free_memory_percent() -> float:
    if os.name == "nt":
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

        state = MEMORYSTATUSEX()
        state.dwLength = ctypes.sizeof(state)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(state)):
            raise OSError("GlobalMemoryStatusEx failed")
        return 100.0 * state.ullAvailPhys / state.ullTotalPhys
    page_size = os.sysconf("SC_PAGE_SIZE")
    available = os.sysconf("SC_AVPHYS_PAGES") * page_size
    total = os.sysconf("SC_PHYS_PAGES") * page_size
    return 100.0 * available / total


def memory_guard(stage: str) -> float:
    available = free_memory_percent()
    if available < MIN_FREE_MEMORY_PERCENT:
        raise MemoryError(
            f"free physical memory {available:.2f}% below "
            f"{MIN_FREE_MEMORY_PERCENT:.2f}% guard at {stage}"
        )
    return available


def load_closure() -> tuple[dict[int, bool], bytes]:
    payload = CLOSURE.read_bytes()
    if sha256_bytes(payload) != EXPECTED[CLOSURE]["sha256"]:
        raise ValueError("Wave 42 closure SHA-256 mismatch")
    data = json.loads(payload)
    if data.get("format") != "wave42-branch15-combined-propagation-v1":
        raise ValueError("unsupported Wave 42 closure")
    result = data.get("result")
    if not isinstance(result, dict) or result.get("contradiction") is not None:
        raise ValueError("Wave 42 closure is malformed or contradictory")
    assignments: dict[int, bool] = {}
    for expected_index, item in enumerate(data["derivations"], start=1):
        if item.get("index") != expected_index:
            raise ValueError("closure derivation order changed")
        variable = item.get("variable")
        value = item.get("value")
        if type(variable) is not int or type(value) is not bool:
            raise ValueError("malformed closure assignment")
        if variable in assignments:
            raise ValueError("duplicate closure assignment")
        assignments[variable] = value
    if len(assignments) != 830:
        raise ValueError("closure assignment count changed")
    return assignments, payload


def load_constraints(path: Path) -> tuple[list[Constraint], dict[str, object]]:
    expected = EXPECTED[path]
    compressed = path.read_bytes()
    if sha256_bytes(compressed) != expected["gzip"]:
        raise ValueError(f"{path.name} gzip SHA-256 mismatch")
    raw = gzip.decompress(compressed)
    if sha256_bytes(raw) != expected["raw"]:
        raise ValueError(f"{path.name} raw SHA-256 mismatch")
    lines = raw.splitlines(keepends=True)
    match = HEADER_RE.fullmatch(lines[0])
    if match is None:
        raise ValueError(f"{path.name} header is not canonical")
    if int(match.group(2)) != expected["constraints"]:
        raise ValueError(f"{path.name} declared constraint count changed")
    if len(lines) - 1 != expected["constraints"]:
        raise ValueError(f"{path.name} actual constraint count changed")
    constraints: list[Constraint] = []
    for row, line in enumerate(lines[1:], start=1):
        bound_match = BOUND_RE.search(line)
        if bound_match is None:
            raise ValueError(f"{path.name}:{row} malformed bound")
        literals = tuple(
            (int(variable), not bool(negated))
            for negated, variable in TERM_RE.findall(line)
        )
        if not literals:
            raise ValueError(f"{path.name}:{row} has no literals")
        constraints.append(
            Constraint(
                path.relative_to(REPOSITORY_ROOT).as_posix(),
                row,
                sha256_bytes(line),
                literals,
                int(bound_match.group(1)),
            )
        )
    return constraints, {
        "path": path.relative_to(REPOSITORY_ROOT).as_posix(),
        "gzip_sha256": expected["gzip"],
        "raw_sha256": expected["raw"],
        "constraints": expected["constraints"],
    }


def simplify(
    constraint: Constraint,
    assignments: dict[int, bool],
) -> tuple[str, tuple[tuple[int, bool], ...], int]:
    true_count = 0
    residual: list[tuple[int, bool]] = []
    for variable, positive in constraint.literals:
        value = assignments.get(variable)
        if value is None:
            residual.append((variable, positive))
        elif value == positive:
            true_count += 1
    bound = constraint.bound - true_count
    if bound <= 0:
        return "SATISFIED", (), bound
    if bound > len(residual):
        return "CONTRADICTION", tuple(residual), bound
    return "ACTIVE", tuple(residual), bound


def exact_blocks(
    base: Sequence[Constraint],
    assignments: dict[int, bool],
) -> list[dict[str, object]]:
    grouped: dict[tuple[int, ...], list[Constraint]] = {}
    for constraint in base:
        variables = tuple(variable for variable, _ in constraint.literals)
        if (
            len(variables) not in (11, 12)
            or max(variables) > PRIMARY_VARIABLES
            or len({positive for _, positive in constraint.literals}) != 1
        ):
            continue
        grouped.setdefault(variables, []).append(constraint)
    if len(grouped) != 1_176:
        raise ValueError("exact coordinate-block count changed")
    blocks: list[dict[str, object]] = []
    for variables, rows in sorted(grouped.items()):
        if len(rows) != 2:
            raise ValueError("coordinate block does not have two OPB bounds")
        lower: int | None = None
        upper: int | None = None
        for row in rows:
            positive = row.literals[0][1]
            if positive:
                lower = row.bound
            else:
                upper = len(variables) - row.bound
        if lower is None or upper is None or lower != upper:
            raise ValueError("coordinate block is not an exact count")
        remaining_target = lower
        remaining: list[int] = []
        for variable in variables:
            if variable in assignments:
                remaining_target -= int(assignments[variable])
            else:
                remaining.append(variable)
        if not 0 <= remaining_target <= len(remaining):
            raise ValueError("closure contradicts a coordinate block")
        blocks.append(
            {
                "variables": tuple(variables),
                "remaining": tuple(remaining),
                "target": remaining_target,
                "source_rows": tuple(
                    (row.source, row.row, row.raw_sha256) for row in rows
                ),
            }
        )
    return blocks


def coordinate_windows() -> list[dict[str, object]]:
    labels = wave42.rooted_labels()
    variable_ids = wave42.residual_variable_ids()
    windows: list[dict[str, object]] = []
    for pair in range(7):
        coordinates = (2 * pair, 2 * pair + 1)
        vertices = sorted(
            index
            for index, label in enumerate(labels)
            if coordinates[0] in label or coordinates[1] in label
        )
        if len(vertices) != 24:
            raise AssertionError("mate-coordinate window lost a residual label")
        variables = tuple(
            sorted(
                variable_ids[(first, second)]
                for first, second in itertools.combinations(vertices, 2)
            )
        )
        if len(variables) != 276:
            raise AssertionError("mate-coordinate window variable count changed")
        windows.append(
            {
                "pair_index": pair,
                "coordinates": coordinates,
                "residual_vertices": tuple(vertices),
                "variables": variables,
            }
        )
    return windows


def rref_lowest(rows: Iterable[int]) -> dict[int, int]:
    pivots: dict[int, int] = {}
    for row in rows:
        reduced = row
        while reduced:
            low_bit = reduced & -reduced
            pivot = low_bit.bit_length() - 1
            old = pivots.get(pivot)
            if old is None:
                pivots[pivot] = reduced
                break
            reduced ^= old
    for pivot in sorted(pivots, reverse=True):
        row = pivots[pivot]
        for lower in sorted(key for key in pivots if key < pivot):
            if (pivots[lower] >> pivot) & 1:
                pivots[lower] ^= row
    return pivots


def rref_highest(rows: Iterable[int]) -> dict[int, int]:
    pivots: dict[int, int] = {}
    for row in rows:
        reduced = row
        while reduced:
            pivot = reduced.bit_length() - 1
            old = pivots.get(pivot)
            if old is None:
                pivots[pivot] = reduced
                break
            reduced ^= old
    for pivot in sorted(pivots):
        row = pivots[pivot]
        for higher in sorted(key for key in pivots if key > pivot):
            if (pivots[higher] >> pivot) & 1:
                pivots[higher] ^= row
    return pivots


def slice_relations(
    variables: Sequence[int],
    target: int,
    monomial_column: dict[Monomial, int],
) -> tuple[list[int], int, str]:
    local_monomials: list[Monomial] = [()]
    local_monomials.extend((variable,) for variable in variables)
    local_monomials.extend(itertools.combinations(variables, 2))
    evaluation_rows: list[int] = []
    for chosen in itertools.combinations(variables, target):
        chosen_set = frozenset(chosen)
        row = 0
        for column, monomial in enumerate(local_monomials):
            if all(variable in chosen_set for variable in monomial):
                row |= 1 << column
        evaluation_rows.append(row)
    evaluation_rref = rref_lowest(evaluation_rows)
    pivot_columns = set(evaluation_rref)
    relations: list[int] = []
    relation_digest = hashlib.sha256()
    for free_column in range(len(local_monomials)):
        if free_column in pivot_columns:
            continue
        local_relation = 1 << free_column
        for pivot, row in evaluation_rref.items():
            if (row >> free_column) & 1:
                local_relation |= 1 << pivot
        global_relation = 0
        for column, monomial in enumerate(local_monomials):
            if (local_relation >> column) & 1:
                global_relation ^= 1 << monomial_column[monomial]
        relations.append(global_relation)
        payload = global_relation.to_bytes(
            (global_relation.bit_length() + 7) // 8,
            "little",
        )
        relation_digest.update(f"{len(payload)}:".encode("ascii"))
        relation_digest.update(payload)
        relation_digest.update(b"\n")
    return relations, len(evaluation_rref), relation_digest.hexdigest()


def clause_polynomial(
    literals: Sequence[tuple[int, bool]],
    monomial_column: dict[Monomial, int],
) -> int:
    terms: set[Monomial] = {()}
    for variable, positive in literals:
        if positive:
            # A positive clause literal is false at x=0: factor (1+x).
            extension = {
                tuple(sorted((*monomial, variable)))
                for monomial in terms
            }
            terms ^= extension
        else:
            # A negative clause literal is false at x=1: factor x.
            terms = {
                tuple(sorted(set((*monomial, variable))))
                for monomial in terms
            }
    return sum(1 << monomial_column[monomial] for monomial in terms)


def multiply_linear(
    row: int,
    variable: int,
    column_monomials: Sequence[Monomial],
    monomial_column: dict[Monomial, int],
) -> int:
    product = 0
    remaining = row
    while remaining:
        low_bit = remaining & -remaining
        column = low_bit.bit_length() - 1
        monomial = column_monomials[column]
        if len(monomial) > 1:
            raise ValueError("attempted to multiply a nonlinear row at degree two")
        multiplied = tuple(sorted(set((*monomial, variable))))
        product ^= 1 << monomial_column[multiplied]
        remaining ^= low_bit
    return product


def linear_rref(rows: Iterable[int], max_linear_column: int) -> dict[int, int]:
    low_rows = [
        row for row in rows if row and row.bit_length() - 1 <= max_linear_column
    ]
    return rref_highest(low_rows)


def row_catalog_sha256(rows: Iterable[int]) -> str:
    digest = hashlib.sha256()
    for index, row in enumerate(rows, start=1):
        payload = row.to_bytes((row.bit_length() + 7) // 8, "little")
        digest.update(f"{index}:{len(payload)}:".encode("ascii"))
        digest.update(payload)
        digest.update(b"\n")
    return digest.hexdigest()


def quotient_relations(
    initial_rows: Iterable[int],
    consequence_rows: Iterable[int],
) -> list[int]:
    pivots = dict(rref_highest(initial_rows))
    new_rows: list[int] = []
    for row in sorted(consequence_rows, reverse=True):
        reduced = row
        while reduced:
            pivot = reduced.bit_length() - 1
            old = pivots.get(pivot)
            if old is None:
                pivots[pivot] = reduced
                new_rows.append(reduced)
                break
            reduced ^= old
    return new_rows


def analyze_window(
    window: dict[str, object],
    assignments: dict[int, bool],
    blocks: Sequence[dict[str, object]],
    constraints: Sequence[Constraint],
) -> dict[str, object]:
    pair_index = int(window["pair_index"])
    memory_guard(f"window {pair_index} start")
    window_variables = frozenset(window["variables"])
    labels = wave42.rooted_labels()
    inverse_variable_ids = {
        variable: edge
        for edge, variable in wave42.residual_variable_ids().items()
    }
    free_variables = tuple(
        variable
        for variable in window["variables"]
        if variable not in assignments
    )
    column_monomials: list[Monomial] = [()]
    column_monomials.extend((variable,) for variable in free_variables)
    max_linear_column = len(column_monomials) - 1
    column_monomials.extend(itertools.combinations(free_variables, 2))
    monomial_column = {
        monomial: column for column, monomial in enumerate(column_monomials)
    }

    local_blocks = [
        block
        for block in blocks
        if frozenset(block["variables"]).issubset(window_variables)
    ]
    if len(local_blocks) != 48:
        raise ValueError(
            f"window {pair_index} expected 48 exact blocks, "
            f"found {len(local_blocks)}"
        )

    axiom_rows: list[int] = []
    axiom_types: Counter[str] = Counter()
    slice_ranks: Counter[str] = Counter()
    slice_relation_digest = hashlib.sha256()
    initial_linear_rows: list[int] = []
    for block_index, block in enumerate(local_blocks, start=1):
        remaining = tuple(block["remaining"])
        target = int(block["target"])
        if not frozenset(remaining).issubset(free_variables):
            raise AssertionError("local block contains a nonfree variable")
        relations, evaluation_rank, relation_hash = slice_relations(
            remaining,
            target,
            monomial_column,
        )
        axiom_rows.extend(relations)
        axiom_types["exact_slice_degree2_relations"] += len(relations)
        slice_ranks[f"n={len(remaining)},t={target},rank={evaluation_rank}"] += 1
        slice_relation_digest.update(
            f"{block_index}:{relation_hash}\n".encode("ascii")
        )
        parity_row = (target & 1) << monomial_column[()]
        for variable in remaining:
            parity_row ^= 1 << monomial_column[(variable,)]
        initial_linear_rows.append(parity_row)

    active_clause_widths: Counter[int] = Counter()
    clause_sources: Counter[str] = Counter()
    degree2_clause_rows: list[int] = []
    wave43_active_window_widths: Counter[int] = Counter()
    for constraint in constraints:
        if constraint.bound != 1:
            continue
        state, residual, bound = simplify(constraint, assignments)
        if state == "CONTRADICTION":
            raise ValueError("frozen closure contradicts an imported clause")
        if state != "ACTIVE" or bound != 1:
            continue
        variables = frozenset(variable for variable, _ in residual)
        if not variables.issubset(window_variables):
            continue
        active_clause_widths[len(residual)] += 1
        if "wave43-branch15-two-triangle" in constraint.source:
            wave43_active_window_widths[len(residual)] += 1
        if len(residual) <= 2:
            row = clause_polynomial(residual, monomial_column)
            degree2_clause_rows.append(row)
            clause_sources[constraint.source] += 1
            if len(residual) == 1:
                initial_linear_rows.append(row)
    axiom_rows.extend(degree2_clause_rows)
    axiom_types["active_clause_degree2_relations"] += len(degree2_clause_rows)

    reducer = SparseReducer(max_linear_column)
    for index, row in enumerate(axiom_rows, start=1):
        reducer.add(row)
        if index % 1_000 == 0:
            memory_guard(f"window {pair_index} axiom row {index}")

    initial_linear_basis = rref_lowest(initial_linear_rows)
    initial_linear_rank = len(initial_linear_basis)
    processed_low_rows: set[int] = set()
    saturation_rounds = 0
    multiplied_rows = 0
    while True:
        pending = [
            row
            for row in reducer.low_pivot_queue
            if row not in processed_low_rows
        ]
        if not pending:
            break
        saturation_rounds += 1
        reducer.low_pivot_queue.clear()
        for low_row in pending:
            processed_low_rows.add(low_row)
            if low_row == 1:
                continue
            for variable in free_variables:
                product = multiply_linear(
                    low_row,
                    variable,
                    column_monomials,
                    monomial_column,
                )
                reducer.add(product)
                multiplied_rows += 1
                if multiplied_rows % 5_000 == 0:
                    memory_guard(
                        f"window {pair_index} multiplier row {multiplied_rows}"
                    )

    final_linear_basis = linear_rref(
        reducer.pivots.values(),
        max_linear_column,
    )
    contradiction = 0 in final_linear_basis and final_linear_basis[0] == 1
    new_linear_rows = quotient_relations(
        initial_linear_basis.values(),
        final_linear_basis.values(),
    )
    new_linear_rank = len(new_linear_rows)
    if len(final_linear_basis) - initial_linear_rank != new_linear_rank:
        raise AssertionError("linear quotient rank accounting changed")
    new_linear_relations: list[dict[str, object]] = []
    for row in new_linear_rows:
        variables = [
            column_monomials[column][0]
            for column in range(1, max_linear_column + 1)
            if (row >> column) & 1
        ]
        decoded_edges = []
        common_coordinates: set[int] | None = None
        for variable in variables:
            first, second = inverse_variable_ids[variable]
            edge_coordinates = set(labels[first]).intersection(labels[second])
            if common_coordinates is None:
                common_coordinates = set(edge_coordinates)
            else:
                common_coordinates.intersection_update(edge_coordinates)
            decoded_edges.append(
                {
                    "variable": variable,
                    "residual_vertices": [first, second],
                    "residual_labels": [
                        list(labels[first]),
                        list(labels[second]),
                    ],
                }
            )
        new_linear_relations.append(
            {
                "constant": int(bool(row & 1)),
                "variables": variables,
                "decoded_edges": decoded_edges,
                "support_common_coordinates": sorted(
                    common_coordinates if common_coordinates is not None else ()
                ),
                "term_count": len(variables) + int(bool(row & 1)),
                "row_sha256": sha256_bytes(
                    row.to_bytes((row.bit_length() + 7) // 8, "little")
                ),
            }
        )
    assigned: list[dict[str, object]] = []
    for pivot, row in sorted(final_linear_basis.items()):
        if pivot == 0:
            continue
        nonconstant = row & ~1
        if nonconstant.bit_count() == 1:
            variable = column_monomials[pivot][0]
            assigned.append(
                {
                    "variable": variable,
                    "value": bool(row & 1),
                    "canonical_linear_row": [
                        column_monomials[column]
                        for column in range(max_linear_column + 1)
                        if (row >> column) & 1
                    ],
                }
            )

    degree_pivots = Counter(
        len(column_monomials[pivot]) for pivot in reducer.pivots
    )
    memory_guard(f"window {pair_index} end")
    return {
        "pair_index": pair_index,
        "coordinates": list(window["coordinates"]),
        "residual_vertices": len(window["residual_vertices"]),
        "window_variables": len(window["variables"]),
        "free_variables_after_wave42_closure": len(free_variables),
        "fixed_variables_from_wave42_closure": (
            len(window["variables"]) - len(free_variables)
        ),
        "monomial_columns": len(column_monomials),
        "monomial_columns_by_degree": {
            "0": 1,
            "1": len(free_variables),
            "2": len(column_monomials) - len(free_variables) - 1,
        },
        "exact_blocks": len(local_blocks),
        "exact_block_residual_histogram": {
            key: value for key, value in sorted(slice_ranks.items())
        },
        "active_clause_residual_width_histogram": {
            str(key): value for key, value in sorted(active_clause_widths.items())
        },
        "wave43_active_clause_residual_width_histogram": {
            str(key): value
            for key, value in sorted(wave43_active_window_widths.items())
        },
        "degree2_clause_rows_by_source": {
            key: value for key, value in sorted(clause_sources.items())
        },
        "axiom_rows": len(axiom_rows),
        "axiom_rows_by_type": {
            key: value for key, value in sorted(axiom_types.items())
        },
        "axiom_catalog_sha256": row_catalog_sha256(axiom_rows),
        "slice_relation_catalog_sha256": slice_relation_digest.hexdigest(),
        "saturation_rounds": saturation_rounds,
        "multiplied_linear_rows": multiplied_rows,
        "macaulay_input_rows": reducer.input_rows,
        "macaulay_zero_rows": reducer.zero_rows,
        "macaulay_rank": len(reducer.pivots),
        "pivot_histogram_by_degree": {
            str(key): value for key, value in sorted(degree_pivots.items())
        },
        "echelon_sha256": reducer.echelon_sha256(),
        "initial_linear_rank": initial_linear_rank,
        "final_linear_rank": len(final_linear_basis),
        "final_linear_rref_sha256": row_catalog_sha256(
            final_linear_basis[pivot]
            for pivot in sorted(final_linear_basis)
        ),
        "new_linear_rank": new_linear_rank,
        "new_linear_relations": new_linear_relations,
        "new_linear_relation_catalog_sha256": row_catalog_sha256(
            new_linear_rows
        ),
        "contradiction_derived": contradiction,
        "new_assignments": assigned,
    }


def run() -> dict[str, object]:
    memory_guard("load")
    assignments, closure_payload = load_closure()
    loaded: list[Constraint] = []
    source_records: list[dict[str, object]] = []
    base_constraints: list[Constraint] | None = None
    for path in (BASE_OPB, WAVE42_DELTA, WAVE43_DELTA):
        constraints, record = load_constraints(path)
        if path == BASE_OPB:
            base_constraints = constraints
        loaded.extend(constraints)
        source_records.append(record)
        memory_guard(f"loaded {path.name}")
    if base_constraints is None:
        raise AssertionError("base OPB was not loaded")
    blocks = exact_blocks(base_constraints, assignments)
    windows = coordinate_windows()
    results = []
    for window in windows:
        full = analyze_window(window, assignments, blocks, loaded)
        control = analyze_window(window, assignments, blocks, [])
        same_linear_span = (
            full["final_linear_rank"] == control["final_linear_rank"]
            and full["final_linear_rref_sha256"]
            == control["final_linear_rref_sha256"]
        )
        full["exact_blocks_only_control"] = {
            "axiom_rows": control["axiom_rows"],
            "macaulay_input_rows": control["macaulay_input_rows"],
            "macaulay_rank": control["macaulay_rank"],
            "initial_linear_rank": control["initial_linear_rank"],
            "final_linear_rank": control["final_linear_rank"],
            "new_linear_rank": control["new_linear_rank"],
            "new_assignments": control["new_assignments"],
            "contradiction_derived": control["contradiction_derived"],
            "final_linear_rref_sha256": control[
                "final_linear_rref_sha256"
            ],
            "full_and_control_linear_spaces_equal": same_linear_span,
        }
        results.append(full)
    wave43_degree_barrier = all(
        set(result["wave43_active_clause_residual_width_histogram"]) <= {"4"}
        for result in results
    )
    aggregate = {
        "windows": len(results),
        "windows_deriving_contradiction": sum(
            result["contradiction_derived"] for result in results
        ),
        "windows_deriving_new_linear_rank": sum(
            result["new_linear_rank"] > 0 for result in results
        ),
        "new_linear_rank_total": sum(
            result["new_linear_rank"] for result in results
        ),
        "new_assignments_total": sum(
            len(result["new_assignments"]) for result in results
        ),
        "wave43_active_rows_in_windows": sum(
            sum(result["wave43_active_clause_residual_width_histogram"].values())
            for result in results
        ),
        "wave43_degree_at_least_four_barrier": wave43_degree_barrier,
        "all_new_linear_relations_persist_in_exact_blocks_only_control": all(
            result["exact_blocks_only_control"][
                "full_and_control_linear_spaces_equal"
            ]
            for result in results
        ),
    }
    return {
        "format": "wave47-branch15-degree2-coordinate-windows-v1",
        "role": "proof_b",
        "claim_label": "UNKNOWN",
        "scope": (
            "complete squarefree degree-2 F2 polynomial-calculus closure of "
            "seven exact 276-variable mate-coordinate window subtheories, "
            "after the SHA-bound Wave 42 branch-15 closure"
        ),
        "field": "F2",
        "degree": 2,
        "squarefree_boolean_quotient": True,
        "source_encoding": {
            "exact_count_blocks": (
                "complete degree-at-most-two vanishing space of each exact "
                "local Hamming slice"
            ),
            "clauses": (
                "usual falsifying-assignment polynomial when residual width "
                "is at most two"
            ),
            "closure": (
                "addition plus multiplication of every derived linear row by "
                "every free window variable"
            ),
        },
        "sources": [
            *source_records,
            {
                "path": CLOSURE.relative_to(REPOSITORY_ROOT).as_posix(),
                "sha256": sha256_bytes(closure_payload),
                "forced_variables": len(assignments),
                "forced_primary_variables": sum(
                    variable <= PRIMARY_VARIABLES for variable in assignments
                ),
            },
        ],
        "resource_guard": {
            "minimum_free_physical_memory_percent": MIN_FREE_MEMORY_PERCENT,
            "status": "PASS",
        },
        "aggregate": aggregate,
        "windows": results,
        "interpretation": (
            "A contradiction or new linear relation would be a candidate "
            "consequence only of the stated restricted window subtheory. "
            "A null result does not establish satisfiability.  The active "
            "Wave 43 all-negative width-four monomials cannot enter any "
            "unassumed degree-at-most-three Macaulay matrix."
        ),
        "limitations": [
            "This is seven restricted local window calculations, not the full branch.",
            "Constraints whose complete support leaves a window are omitted.",
            "Residual clauses above degree two are omitted from the degree-two matrix.",
            "No completed-graph automorphism is assumed.",
            "No null result implies SAT, graph existence, or endpoint feasibility.",
            "No contradiction here would count as verified without independent replay.",
            "Branch 15, the endpoint, and Conway-99 remain UNKNOWN.",
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--verify",
        action="store_true",
        help="regenerate and require byte equality with --output",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = run()
    payload = canonical_payload(result)
    if args.verify:
        if not args.output.exists():
            raise FileNotFoundError(args.output)
        if args.output.read_bytes() != payload:
            raise ValueError("stored result differs from exact regeneration")
        print(
            "PASS_EXACT_REPLAY "
            f"sha256={sha256_bytes(payload)} "
            f"windows={result['aggregate']['windows']}"
        )
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(payload)
    print(json.dumps(result["aggregate"], indent=2, sort_keys=True))
    print(f"result_sha256={sha256_bytes(payload)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
