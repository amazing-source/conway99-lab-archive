"""Clean-room Boolean encoding of the Wave 33 six-block graph criterion.

This module was written before inspecting any Wave 34 discovery artifact.  It
uses only Python's standard library.  Its default action is count-only: it
constructs the deterministic variable/constraint stream and prints a JSON
summary, but it does not invoke a SAT solver.

The optional ``--emit-dimacs`` mode performs two deterministic passes.  The
first obtains the exact header counts; the second streams the DIMACS clauses
and a JSONL variable map.  Stage 1 does not exercise that large-output mode.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter, OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Mapping, Sequence


S_SIZE = 14
O_SIZE = 70
Q_SIZE = 15

FANO_LINES: tuple[tuple[int, int, int], ...] = (
    (0, 1, 2),
    (0, 3, 4),
    (0, 5, 6),
    (1, 3, 5),
    (1, 4, 6),
    (2, 3, 6),
    (2, 4, 5),
)


def canonical_json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        + "\n"
    ).encode("ascii")


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


@dataclass(frozen=True)
class FixedData:
    """The fixed labeled support adjacency U and support-to-O incidence F."""

    cross: tuple[tuple[int, ...], ...]
    support_adjacency: tuple[tuple[int, ...], ...]
    support_to_o: tuple[tuple[int, ...], ...]
    o_labels: tuple[tuple[int, int, int], ...]


def build_fixed_data() -> FixedData:
    """Construct the canonical labeled signed-Fano data without a catalog.

    Support vertices are P_0,...,P_6,R_0,...,R_6.  P_p--R_l is an edge
    exactly when point p is not on Fano line l.  An O label (p,l,c) occurs
    once for a support edge and twice for a support cross-nonedge.
    """

    cross = tuple(
        tuple(0 if p in FANO_LINES[line] else 1 for line in range(7))
        for p in range(7)
    )
    support = [[0 for _ in range(S_SIZE)] for _ in range(S_SIZE)]
    for p in range(7):
        for line in range(7):
            support[p][7 + line] = cross[p][line]
            support[7 + line][p] = cross[p][line]

    labels: list[tuple[int, int, int]] = []
    for p in range(7):
        for line in range(7):
            multiplicity = 1 if cross[p][line] else 2
            for copy in range(multiplicity):
                labels.append((p, line, copy))
    if len(labels) != O_SIZE:
        raise AssertionError(f"expected 70 O labels, got {len(labels)}")

    support_to_o = [[0 for _ in range(O_SIZE)] for _ in range(S_SIZE)]
    for o, (p, line, _copy) in enumerate(labels):
        support_to_o[p][o] = 1
        support_to_o[7 + line][o] = 1

    fixed = FixedData(
        cross=tuple(tuple(row) for row in cross),
        support_adjacency=tuple(tuple(row) for row in support),
        support_to_o=tuple(tuple(row) for row in support_to_o),
        o_labels=tuple(labels),
    )
    validate_fixed_data(fixed)
    return fixed


def matmul(left: Sequence[Sequence[int]], right: Sequence[Sequence[int]]) -> list[list[int]]:
    if not left or not right or len(left[0]) != len(right):
        raise ValueError("matrix dimensions do not conform")
    return [
        [
            sum(left[i][k] * right[k][j] for k in range(len(right)))
            for j in range(len(right[0]))
        ]
        for i in range(len(left))
    ]


def transpose(matrix: Sequence[Sequence[int]]) -> list[list[int]]:
    return [list(column) for column in zip(*matrix)]


def validate_fixed_data(fixed: FixedData) -> None:
    u = fixed.support_adjacency
    f = fixed.support_to_o
    if len(u) != S_SIZE or any(len(row) != S_SIZE for row in u):
        raise AssertionError("support adjacency has the wrong shape")
    if len(f) != S_SIZE or any(len(row) != O_SIZE for row in f):
        raise AssertionError("support-to-O incidence has the wrong shape")
    if any(value not in (0, 1) for row in u for value in row):
        raise AssertionError("support adjacency is not binary")
    if any(value not in (0, 1) for row in f for value in row):
        raise AssertionError("support-to-O incidence is not binary")
    if any(u[i][i] != 0 for i in range(S_SIZE)):
        raise AssertionError("support adjacency is not hollow")
    if any(u[i][j] != u[j][i] for i in range(S_SIZE) for j in range(S_SIZE)):
        raise AssertionError("support adjacency is not symmetric")
    if {sum(row) for row in u} != {4}:
        raise AssertionError("support degrees are not all four")
    if {sum(row) for row in f} != {10}:
        raise AssertionError("support-to-O row sums are not all ten")
    if {sum(f[s][o] for s in range(S_SIZE)) for o in range(O_SIZE)} != {2}:
        raise AssertionError("support-to-O column sums are not all two")

    u2 = matmul(u, u)
    fft = matmul(f, transpose(f))
    for s in range(S_SIZE):
        for t in range(S_SIZE):
            left = u2[s][t] + fft[s][t]
            right = 12 * int(s == t) - u[s][t] + 2
            if left != right:
                raise AssertionError(f"fixed SS block fails at {(s, t)}")


Clause = tuple[int, ...]
ClauseConsumer = Callable[[Clause], None]
MapConsumer = Callable[[Mapping[str, object]], None]


def negate(term: int | bool) -> int | bool:
    if isinstance(term, bool):
        return not term
    return -term


def normalize_clause(terms: Iterable[int | bool]) -> Clause | None:
    """Simplify constants/duplicates; return None for a tautology."""

    result: list[int] = []
    seen: set[int] = set()
    for term in terms:
        if isinstance(term, bool):
            if term:
                return None
            continue
        if term == 0:
            raise ValueError("literal zero is forbidden inside a clause")
        if -term in seen:
            return None
        if term not in seen:
            seen.add(term)
            result.append(term)
    return tuple(result)


class CountingClauseSink:
    def __init__(self, *, hash_body: bool = True) -> None:
        self.count = 0
        self.length_histogram: Counter[int] = Counter()
        self._hasher = hashlib.sha256() if hash_body else None

    def __call__(self, clause: Clause) -> None:
        self.count += 1
        self.length_histogram[len(clause)] += 1
        if self._hasher is not None:
            line = " ".join(str(literal) for literal in clause)
            self._hasher.update(f"{line} 0\n".encode("ascii"))

    @property
    def body_sha256(self) -> str | None:
        return None if self._hasher is None else self._hasher.hexdigest()


class ListClauseSink:
    def __init__(self) -> None:
        self.clauses: list[Clause] = []

    def __call__(self, clause: Clause) -> None:
        self.clauses.append(clause)


class DimacsClauseSink:
    def __init__(self, handle) -> None:
        self.handle = handle
        self.count = 0

    def __call__(self, clause: Clause) -> None:
        self.count += 1
        body = " ".join(str(literal) for literal in clause)
        self.handle.write(f"{body} 0\n")


class JsonlMapSink:
    def __init__(self, handle) -> None:
        self.handle = handle
        self.count = 0

    def __call__(self, record: Mapping[str, object]) -> None:
        self.count += 1
        self.handle.write(
            json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
            + "\n"
        )


class EncodingBuilder:
    """Allocate deterministic variables and emit a concrete CNF stream."""

    def __init__(
        self,
        clause_sink: ClauseConsumer,
        map_sink: MapConsumer | None = None,
    ) -> None:
        self.clause_sink = clause_sink
        self.map_sink = map_sink
        self.next_var = 1
        self.clause_count = 0
        self.groups: OrderedDict[str, dict[str, int | None]] = OrderedDict()
        self._active_group: str | None = None
        self._group_start_var = 0
        self._group_start_clause = 0

    @property
    def variable_count(self) -> int:
        return self.next_var - 1

    def start_group(self, name: str) -> None:
        if self._active_group is not None:
            raise RuntimeError(f"group {self._active_group} is still active")
        if name in self.groups:
            raise RuntimeError(f"duplicate group {name}")
        self._active_group = name
        self._group_start_var = self.variable_count
        self._group_start_clause = self.clause_count

    def end_group(self) -> None:
        if self._active_group is None:
            raise RuntimeError("no active group")
        first = self._group_start_var + 1
        last = self.variable_count
        self.groups[self._active_group] = {
            "variables": self.variable_count - self._group_start_var,
            "clauses": self.clause_count - self._group_start_clause,
            "first_variable": first if first <= last else None,
            "last_variable": last if first <= last else None,
        }
        self._active_group = None

    def alloc(self, kind: str, **fields: object) -> int:
        variable = self.next_var
        self.next_var += 1
        if self.map_sink is not None:
            record: dict[str, object] = {"id": variable, "kind": kind}
            record.update(fields)
            self.map_sink(record)
        return variable

    def add_clause(self, *terms: int | bool) -> None:
        normalized = normalize_clause(terms)
        if normalized is None:
            return
        if any(abs(literal) >= self.next_var for literal in normalized):
            raise AssertionError("clause references an unallocated variable")
        self.clause_sink(normalized)
        self.clause_count += 1

    def add_and_equivalence(self, output: int, left: int, right: int) -> None:
        """Encode output iff (left and right) with exactly three clauses."""

        self.add_clause(-output, left)
        self.add_clause(-output, right)
        self.add_clause(output, -left, -right)

    def add_threshold_recurrence(
        self,
        output: int,
        prior_same: int | bool,
        prior_lower: int | bool,
        literal: int,
    ) -> None:
        """Encode y iff a or (b and x), simplifying boundary constants."""

        self.add_clause(negate(prior_same), output)
        self.add_clause(negate(prior_lower), -literal, output)
        self.add_clause(-output, prior_same, prior_lower)
        self.add_clause(-output, prior_same, literal)

    def add_exact_count(
        self,
        literals: Sequence[int],
        target: int,
        *,
        family: str,
        key: Sequence[int],
    ) -> None:
        """Encode sum(literals) == target by an equivalence prefix counter.

        Targets zero and n use direct unit clauses.  Otherwise T(i,j) means
        "at least j of the first i literals are true", with j truncated at
        target+1.  Both directions of every recurrence are encoded, so all
        auxiliary values are uniquely determined by the primary/product bits.
        """

        n = len(literals)
        if target < 0 or target > n:
            self.add_clause()  # Explicit contradiction.
            return
        if target == 0:
            for literal in literals:
                self.add_clause(-literal)
            return
        if target == n:
            for literal in literals:
                self.add_clause(literal)
            return

        cap = target + 1
        states: dict[tuple[int, int], int] = {}
        for prefix, literal in enumerate(literals, start=1):
            for threshold in range(1, min(prefix, cap) + 1):
                output = self.alloc(
                    "CARD_GE",
                    family=family,
                    key=list(key),
                    prefix=prefix,
                    threshold=threshold,
                )
                states[(prefix, threshold)] = output
                prior_same: int | bool = states.get(
                    (prefix - 1, threshold), False
                )
                prior_lower: int | bool
                if threshold == 1:
                    prior_lower = True
                else:
                    prior_lower = states.get(
                        (prefix - 1, threshold - 1), False
                    )
                self.add_threshold_recurrence(
                    output, prior_same, prior_lower, literal
                )
        self.add_clause(states[(n, target)])
        self.add_clause(-states[(n, target + 1)])


@dataclass
class BuiltEncoding:
    builder: EncodingBuilder
    fixed: FixedData
    d_vars: dict[tuple[int, int], int]
    b_vars: dict[tuple[int, int], int]
    inventory: dict[str, object]


def fixed_common_support(fixed: FixedData, left_o: int, right_o: int) -> int:
    return sum(
        fixed.support_to_o[s][left_o] * fixed.support_to_o[s][right_o]
        for s in range(S_SIZE)
    )


def build_encoding(
    clause_sink: ClauseConsumer,
    map_sink: MapConsumer | None = None,
) -> BuiltEncoding:
    """Build the complete unrestricted labeled CNF in deterministic order."""

    fixed = build_fixed_data()
    u = fixed.support_adjacency
    f = fixed.support_to_o
    builder = EncodingBuilder(clause_sink=clause_sink, map_sink=map_sink)

    d_vars: dict[tuple[int, int], int] = {}
    b_vars: dict[tuple[int, int], int] = {}

    builder.start_group("PRIMARY_D")
    for i in range(O_SIZE):
        for j in range(i + 1, O_SIZE):
            d_vars[(i, j)] = builder.alloc("D", i=i, j=j)
    builder.end_group()

    builder.start_group("PRIMARY_B")
    for i in range(O_SIZE):
        for q in range(Q_SIZE):
            b_vars[(i, q)] = builder.alloc("B", i=i, q=q)
    builder.end_group()

    def d(i: int, j: int) -> int:
        if i == j:
            raise ValueError("D diagonal is the fixed constant zero")
        return d_vars[(i, j) if i < j else (j, i)]

    def b(i: int, q: int) -> int:
        return b_vars[(i, q)]

    oo_d_and: dict[tuple[int, int, int], int] = {}
    builder.start_group("AND_OO_D")
    for i in range(O_SIZE):
        for j in range(i + 1, O_SIZE):
            for k in range(O_SIZE):
                if k in (i, j):
                    continue
                z = builder.alloc("AND_OO_D", i=i, j=j, k=k)
                builder.add_and_equivalence(z, d(i, k), d(j, k))
                oo_d_and[(i, j, k)] = z
    builder.end_group()

    oo_b_and: dict[tuple[int, int, int], int] = {}
    builder.start_group("AND_OO_B")
    for i in range(O_SIZE):
        for j in range(i + 1, O_SIZE):
            for q in range(Q_SIZE):
                z = builder.alloc("AND_OO_B", i=i, j=j, q=q)
                builder.add_and_equivalence(z, b(i, q), b(j, q))
                oo_b_and[(i, j, q)] = z
    builder.end_group()

    oq_db_and: dict[tuple[int, int, int], int] = {}
    builder.start_group("AND_OQ_DB")
    for i in range(O_SIZE):
        for q in range(Q_SIZE):
            for j in range(O_SIZE):
                if i == j:
                    continue
                z = builder.alloc("AND_OQ_DB", i=i, q=q, j=j)
                builder.add_and_equivalence(z, d(i, j), b(j, q))
                oq_db_and[(i, q, j)] = z
    builder.end_group()

    qq_bb_and: dict[tuple[int, int, int], int] = {}
    builder.start_group("AND_QQ_B")
    for q in range(Q_SIZE):
        for r in range(q + 1, Q_SIZE):
            for i in range(O_SIZE):
                z = builder.alloc("AND_QQ_B", q=q, r=r, i=i)
                builder.add_and_equivalence(z, b(i, q), b(i, r))
                qq_bb_and[(q, r, i)] = z
    builder.end_group()

    constraint_counts: Counter[str] = Counter()
    target_distributions: dict[str, Counter[tuple[int, int]]] = {}

    def record(family: str, literals: Sequence[int], target: int) -> None:
        constraint_counts[family] += 1
        target_distributions.setdefault(family, Counter())[
            (len(literals), target)
        ] += 1

    builder.start_group("CARD_D_ROW")
    for i in range(O_SIZE):
        literals = [d(i, j) for j in range(O_SIZE) if j != i]
        record("D_ROW", literals, 9)
        builder.add_exact_count(literals, 9, family="D_ROW", key=(i,))
    builder.end_group()

    builder.start_group("CARD_B_ROW")
    for i in range(O_SIZE):
        literals = [b(i, q) for q in range(Q_SIZE)]
        record("B_ROW", literals, 3)
        builder.add_exact_count(literals, 3, family="B_ROW", key=(i,))
    builder.end_group()

    builder.start_group("CARD_B_COLUMN_QQ_DIAGONAL")
    for q in range(Q_SIZE):
        literals = [b(i, q) for i in range(O_SIZE)]
        record("B_COLUMN_QQ_DIAGONAL", literals, 14)
        builder.add_exact_count(
            literals, 14, family="B_COLUMN_QQ_DIAGONAL", key=(q,)
        )
    builder.end_group()

    builder.start_group("CARD_SO")
    for s in range(S_SIZE):
        for i in range(O_SIZE):
            literals = [
                d(i, j)
                for j in range(O_SIZE)
                if j != i and f[s][j] == 1
            ]
            fixed_term = sum(
                u[s][t] * f[t][i] for t in range(S_SIZE)
            )
            target = 2 - f[s][i] - fixed_term
            record("SO", literals, target)
            builder.add_exact_count(
                literals, target, family="SO", key=(s, i)
            )
    builder.end_group()

    builder.start_group("CARD_SQ")
    for s in range(S_SIZE):
        support_row = [i for i in range(O_SIZE) if f[s][i] == 1]
        for q in range(Q_SIZE):
            literals = [b(i, q) for i in support_row]
            record("SQ", literals, 2)
            builder.add_exact_count(
                literals, 2, family="SQ", key=(s, q)
            )
    builder.end_group()

    builder.start_group("CARD_OO_DIAGONAL")
    for i in range(O_SIZE):
        literals = [d(i, j) for j in range(O_SIZE) if j != i]
        literals.extend(b(i, q) for q in range(Q_SIZE))
        record("OO_DIAGONAL", literals, 12)
        builder.add_exact_count(
            literals, 12, family="OO_DIAGONAL", key=(i,)
        )
    builder.end_group()

    builder.start_group("CARD_OO_OFFDIAGONAL")
    for i in range(O_SIZE):
        for j in range(i + 1, O_SIZE):
            literals = [
                oo_d_and[(i, j, k)]
                for k in range(O_SIZE)
                if k not in (i, j)
            ]
            literals.extend(oo_b_and[(i, j, q)] for q in range(Q_SIZE))
            literals.append(d(i, j))
            target = 2 - fixed_common_support(fixed, i, j)
            record("OO_OFFDIAGONAL", literals, target)
            builder.add_exact_count(
                literals, target, family="OO_OFFDIAGONAL", key=(i, j)
            )
    builder.end_group()

    builder.start_group("CARD_OQ")
    for i in range(O_SIZE):
        for q in range(Q_SIZE):
            literals = [
                oq_db_and[(i, q, j)]
                for j in range(O_SIZE)
                if j != i
            ]
            literals.append(b(i, q))
            record("OQ", literals, 2)
            builder.add_exact_count(
                literals, 2, family="OQ", key=(i, q)
            )
    builder.end_group()

    builder.start_group("CARD_QQ_OFFDIAGONAL")
    for q in range(Q_SIZE):
        for r in range(q + 1, Q_SIZE):
            literals = [qq_bb_and[(q, r, i)] for i in range(O_SIZE)]
            record("QQ_OFFDIAGONAL", literals, 2)
            builder.add_exact_count(
                literals, 2, family="QQ_OFFDIAGONAL", key=(q, r)
            )
    builder.end_group()

    inventory = {
        "constraint_counts": dict(sorted(constraint_counts.items())),
        "constraint_total": sum(constraint_counts.values()),
        "target_distributions": {
            family: [
                {"scope_size": n, "target": target, "count": count}
                for (n, target), count in sorted(distribution.items())
            ]
            for family, distribution in sorted(target_distributions.items())
        },
    }
    return BuiltEncoding(
        builder=builder,
        fixed=fixed,
        d_vars=d_vars,
        b_vars=b_vars,
        inventory=inventory,
    )


def summarize_encoding(*, hash_body: bool = True) -> dict[str, object]:
    sink = CountingClauseSink(hash_body=hash_body)
    built = build_encoding(sink)
    fixed = built.fixed
    primary_count = len(built.d_vars) + len(built.b_vars)
    groups = built.builder.groups
    product_auxiliaries = sum(
        int(groups[name]["variables"])
        for name in ("AND_OO_D", "AND_OO_B", "AND_OQ_DB", "AND_QQ_B")
    )
    cardinality_auxiliaries = sum(
        int(stats["variables"])
        for name, stats in groups.items()
        if name.startswith("CARD_")
    )
    return {
        "schema_version": 1,
        "scope": "unrestricted labeled six-block graph criterion",
        "fixed_data": {
            "support_adjacency_sha256": canonical_sha256(
                fixed.support_adjacency
            ),
            "support_to_o_sha256": canonical_sha256(fixed.support_to_o),
            "o_labels_sha256": canonical_sha256(fixed.o_labels),
            "support_size": S_SIZE,
            "o_size": O_SIZE,
            "q_size": Q_SIZE,
            "ss_fixed_identity": "PASS",
        },
        "primary_variables": {
            "D_unordered_edges": len(built.d_vars),
            "B_ordered_incidences": len(built.b_vars),
            "total": primary_count,
        },
        "auxiliary_variables": {
            "product": product_auxiliaries,
            "cardinality": cardinality_auxiliaries,
            "total": product_auxiliaries + cardinality_auxiliaries,
        },
        "total_variables": built.builder.variable_count,
        "total_clauses": built.builder.clause_count,
        "clause_length_histogram": {
            str(length): count
            for length, count in sorted(sink.length_histogram.items())
        },
        "dimacs_body_sha256": sink.body_sha256,
        "groups": groups,
        "inventory": built.inventory,
    }


def variable_truth(record: Mapping[str, object], d: Sequence[Sequence[int]], bmat: Sequence[Sequence[int]]) -> int:
    """Evaluate a primary mapping record; used by independent model tooling."""

    kind = record["kind"]
    if kind == "D":
        return int(d[int(record["i"])][int(record["j"])])
    if kind == "B":
        return int(bmat[int(record["i"])][int(record["q"])])
    raise ValueError(f"not a primary record: {kind}")


def six_block_mismatch_counts(
    d: Sequence[Sequence[int]],
    bmat: Sequence[Sequence[int]],
    fixed: FixedData | None = None,
) -> dict[str, int | bool]:
    """Directly check decoded primary matrices, without trusting CNF auxiliaries."""

    fixed = build_fixed_data() if fixed is None else fixed
    u = fixed.support_adjacency
    f = fixed.support_to_o
    if len(d) != O_SIZE or any(len(row) != O_SIZE for row in d):
        raise ValueError("D has the wrong shape")
    if len(bmat) != O_SIZE or any(len(row) != Q_SIZE for row in bmat):
        raise ValueError("B has the wrong shape")

    gates = {
        "D_binary": all(value in (0, 1) for row in d for value in row),
        "D_symmetric": all(
            d[i][j] == d[j][i]
            for i in range(O_SIZE)
            for j in range(O_SIZE)
        ),
        "D_hollow": all(d[i][i] == 0 for i in range(O_SIZE)),
        "B_binary": all(value in (0, 1) for row in bmat for value in row),
        "D_row_9": all(sum(row) == 9 for row in d),
        "B_row_3": all(sum(row) == 3 for row in bmat),
        "B_column_14": all(
            sum(bmat[i][q] for i in range(O_SIZE)) == 14
            for q in range(Q_SIZE)
        ),
    }

    ss = 0
    so = 0
    sq = 0
    oo = 0
    oq = 0
    qq = 0
    u2 = matmul(u, u)
    fft = matmul(f, transpose(f))
    for s in range(S_SIZE):
        for t in range(S_SIZE):
            ss += (
                u2[s][t] + fft[s][t]
                != 12 * int(s == t) - u[s][t] + 2
            )
    for s in range(S_SIZE):
        for i in range(O_SIZE):
            left = sum(u[s][t] * f[t][i] for t in range(S_SIZE))
            left += sum(f[s][j] * d[j][i] for j in range(O_SIZE))
            so += left != 2 - f[s][i]
        for q in range(Q_SIZE):
            sq += sum(f[s][i] * bmat[i][q] for i in range(O_SIZE)) != 2
    for i in range(O_SIZE):
        for j in range(O_SIZE):
            left = sum(f[s][i] * f[s][j] for s in range(S_SIZE))
            left += sum(d[i][k] * d[k][j] for k in range(O_SIZE))
            left += sum(bmat[i][q] * bmat[j][q] for q in range(Q_SIZE))
            right = 12 * int(i == j) - d[i][j] + 2
            oo += left != right
        for q in range(Q_SIZE):
            left = sum(d[i][j] * bmat[j][q] for j in range(O_SIZE))
            oq += left != 2 - bmat[i][q]
    for q in range(Q_SIZE):
        for r in range(Q_SIZE):
            left = sum(bmat[i][q] * bmat[i][r] for i in range(O_SIZE))
            right = 12 * int(q == r) + 2
            qq += left != right
    return {
        **gates,
        "SS_mismatches": ss,
        "SO_mismatches": so,
        "SQ_mismatches": sq,
        "OO_mismatches": oo,
        "OQ_mismatches": oq,
        "QQ_mismatches": qq,
        "passes": all(gates.values())
        and all(value == 0 for value in (ss, so, sq, oo, oq, qq)),
    }


def emit_dimacs_and_map(dimacs_path: Path, map_path: Path) -> dict[str, object]:
    summary = summarize_encoding(hash_body=True)
    with dimacs_path.open("w", encoding="ascii", newline="\n") as dimacs_handle:
        dimacs_handle.write(
            f"p cnf {summary['total_variables']} {summary['total_clauses']}\n"
        )
        dimacs_sink = DimacsClauseSink(dimacs_handle)
        with map_path.open("w", encoding="ascii", newline="\n") as map_handle:
            map_handle.write(
                json.dumps(
                    {
                        "record_type": "header",
                        "schema_version": 1,
                        "total_variables": summary["total_variables"],
                        "primary_variables": summary["primary_variables"]["total"],
                        "dimacs_body_sha256": summary["dimacs_body_sha256"],
                    },
                    sort_keys=True,
                    separators=(",", ":"),
                )
                + "\n"
            )
            map_sink = JsonlMapSink(map_handle)
            emitted = build_encoding(dimacs_sink, map_sink)
    if emitted.builder.variable_count != summary["total_variables"]:
        raise AssertionError("second-pass variable count drift")
    if emitted.builder.clause_count != summary["total_clauses"]:
        raise AssertionError("second-pass clause count drift")
    if dimacs_sink.count != summary["total_clauses"]:
        raise AssertionError("DIMACS sink clause count drift")
    if map_sink.count != summary["total_variables"]:
        raise AssertionError("map record count drift")
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--summary",
        action="store_true",
        help="print the deterministic count/fixed-data summary (default)",
    )
    parser.add_argument("--emit-dimacs", type=Path)
    parser.add_argument("--emit-map", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if (args.emit_dimacs is None) != (args.emit_map is None):
        raise SystemExit("--emit-dimacs and --emit-map must be supplied together")
    if args.emit_dimacs is not None:
        summary = emit_dimacs_and_map(args.emit_dimacs, args.emit_map)
    else:
        summary = summarize_encoding(hash_body=True)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
