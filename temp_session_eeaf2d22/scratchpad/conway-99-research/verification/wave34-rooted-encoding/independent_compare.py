"""Independent Stage-2 audit of the Wave 34 rooted CNF candidate.

This verifier does not import or execute the candidate generator.  It
reconstructs the fixed labels, the complete variable allocation, and every
CNF clause from the frozen mathematical specification, then compares the
89.5 MB candidate DIMACS byte-for-byte while streaming.

Candidate-owned decode/check scripts are exercised only on verifier-created
synthetic controls.  Those executions are supplemental; the semantic formula
audit is verifier-owned.
"""

from __future__ import annotations

import argparse
import ast
import copy
import gzip
import hashlib
import itertools
import json
import subprocess
import sys
import tempfile
from collections import Counter, OrderedDict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CANDIDATE = ROOT / "attempts" / "wave34-rooted-encoding"
PRECOMPARISON = HERE / "precomparison"

S_SIZE = 14
O_SIZE = 70
Q_SIZE = 15

EXPECTED = {
    "candidate_release": "023088f9a1e4e21929a9d1c5666f2ce3ac3b757e93491d67a3b37f9a8338fa80",
    "candidate_report": "120f9709aea2f7010866c2b7d7e2b74cb954bba92c903923c8c81db4a7dcea8c",
    "publication_manifest": "7cba8a082545cbfcbf01785e6e15a0198bd1cf2357ed0a2b3f353b564a1433e7",
    "artifact_manifest": "e96036e97884f0bbc19c30073dbe295852117e9d4d54892cf5e57b20e6f6ec05",
    "raw_cnf": "2362d15f3a20df0a0d7745eb619a94061cee9911c8dda36c191fb6d728c1c3d3",
    "gzip_cnf": "6b6beb5d49c7fe75b9b475162cc4bd97de2793389df150dfab9765ba497305f0",
    "criterion_spec": "3429a093c682877a3a14848620860f8ffb5e4cc0b0ca70f0fc5a2f85697d1d82",
    "primary_map": "d20ae9196012b2bbf512938abd5641b4281c10e05495b19342a3b46e4d9a264c",
    "encoding_audit": "00be08c4da5bccabc54004cd1b70705a6112847f10658fd2fb0976416cbaa826",
    "encoding_preflight": "155f2e310238112d36f8eddac635f4b25fe40f4a417fb3efd59f1fbe5afb970a",
    "dimacs_audit": "da267da5708f50a0eb46f2c511318e99797ef8a6a9c5f4537db91fef5d5ff1ab",
    "compression_audit": "df6bcc6077480ff5348357a51b471862ad82c2d1088a561d1dabd1c96664746c",
    "correction_ledger": "6daaa2c49cda2ca9e254210ebe64e493cf66cc66510ed6a711251e40e507ff0d",
    "gitattributes": "3b5a883d038c4a3377a8b237ed0180e4f1d80423e987d13682dde670c92614bd",
    "precomparison_manifest": "3f1bdcb0ca2d08ee0380cd1435673fddb499db8c3a8273f6676c18f17ad3550c",
}


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        + "\n"
    ).encode("ascii")


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_sha_manifest(path: Path) -> dict[str, object]:
    entries: list[dict[str, object]] = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if len(line) < 67 or line[64:66] != "  ":
            raise AssertionError(f"malformed manifest line {path}:{line_number}")
        expected_hash = line[:64]
        relative = line[66:]
        if len(expected_hash) != 64 or set(expected_hash) - set("0123456789abcdef"):
            raise AssertionError(f"malformed SHA-256 at {path}:{line_number}")
        target = ROOT / Path(relative)
        if not target.is_file():
            raise AssertionError(f"missing manifested file: {relative}")
        actual_hash = sha256_path(target)
        if actual_hash != expected_hash:
            raise AssertionError(
                f"manifest mismatch {relative}: {actual_hash} != {expected_hash}"
            )
        entries.append(
            {
                "path": relative.replace("\\", "/"),
                "sha256": actual_hash,
                "bytes": target.stat().st_size,
            }
        )
    return {
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "sha256": sha256_path(path),
        "entries": entries,
        "entry_count": len(entries),
        "all_entries_pass": True,
    }


@dataclass(frozen=True)
class FixedData:
    lines: tuple[tuple[int, int, int], ...]
    support: tuple[tuple[int, ...], ...]
    labels: tuple[tuple[int, int, int], ...]
    incidence: tuple[tuple[int, ...], ...]


def fixed_from_lines(lines: Sequence[Sequence[int]]) -> FixedData:
    normalized = tuple(tuple(sorted(map(int, line))) for line in lines)
    if len(normalized) != 7 or any(len(set(line)) != 3 for line in normalized):
        raise AssertionError("expected seven distinct triples")
    if len(set(normalized)) != 7:
        raise AssertionError("Fano lines are repeated")
    line_sets = tuple(frozenset(line) for line in normalized)
    pair_counts = Counter(
        tuple(sorted(pair))
        for line in line_sets
        for pair in itertools.combinations(line, 2)
    )
    if set(pair_counts.values()) != {1} or len(pair_counts) != 21:
        raise AssertionError("line system is not a 2-(7,3,1) design")

    support = [[0] * S_SIZE for _ in range(S_SIZE)]
    for point in range(7):
        for line_index, line in enumerate(line_sets):
            edge = int(point not in line)
            support[point][7 + line_index] = edge
            support[7 + line_index][point] = edge

    labels: list[tuple[int, int, int]] = []
    for point in range(7):
        for line_index, line in enumerate(line_sets):
            for copy_index in range(2 if point in line else 1):
                labels.append((point, line_index, copy_index))
    if len(labels) != O_SIZE or len(set(labels)) != O_SIZE:
        raise AssertionError("O label construction did not give 70 labels")

    incidence = [[0] * O_SIZE for _ in range(S_SIZE)]
    for o, (point, line_index, _copy_index) in enumerate(labels):
        incidence[point][o] = 1
        incidence[7 + line_index][o] = 1

    fixed = FixedData(
        lines=normalized,
        support=tuple(tuple(row) for row in support),
        labels=tuple(labels),
        incidence=tuple(tuple(row) for row in incidence),
    )
    validate_fixed(fixed)
    return fixed


def validate_fixed(fixed: FixedData) -> None:
    support = fixed.support
    incidence = fixed.incidence
    checks = {
        "support_binary": all(x in (0, 1) for row in support for x in row),
        "support_symmetric": all(
            support[i][j] == support[j][i]
            for i in range(S_SIZE)
            for j in range(S_SIZE)
        ),
        "support_hollow": all(support[i][i] == 0 for i in range(S_SIZE)),
        "support_degree_4": {sum(row) for row in support} == {4},
        "incidence_binary": all(x in (0, 1) for row in incidence for x in row),
        "incidence_row_10": {sum(row) for row in incidence} == {10},
        "incidence_column_2": {
            sum(incidence[s][o] for s in range(S_SIZE)) for o in range(O_SIZE)
        }
        == {2},
    }
    if not all(checks.values()):
        raise AssertionError(checks)
    for i in range(S_SIZE):
        for j in range(S_SIZE):
            lhs = sum(
                support[i][k] * support[k][j] for k in range(S_SIZE)
            ) + sum(incidence[i][o] * incidence[j][o] for o in range(O_SIZE))
            rhs = 12 * int(i == j) - support[i][j] + 2
            if lhs != rhs:
                raise AssertionError(f"fixed SS identity fails at {(i, j)}")


def candidate_label_binding(
    candidate_spec: Mapping[str, object],
    stage_spec: Mapping[str, object],
) -> dict[str, object]:
    candidate_lines = candidate_spec["fixed"]["Fano_lines"]
    stage_lines = stage_spec["fixed_data"]["fano_lines_zero_based"]
    candidate_fixed = fixed_from_lines(candidate_lines)
    stage_fixed = fixed_from_lines(stage_lines)
    stage_line_index = {
        frozenset(line): index for index, line in enumerate(stage_fixed.lines)
    }

    isomorphisms: list[tuple[tuple[int, ...], tuple[int, ...]]] = []
    for point_permutation in itertools.permutations(range(7)):
        images = [
            frozenset(point_permutation[p] for p in line)
            for line in candidate_fixed.lines
        ]
        if all(image in stage_line_index for image in images):
            line_permutation = tuple(stage_line_index[image] for image in images)
            isomorphisms.append((point_permutation, line_permutation))
    if len(isomorphisms) != 168:
        raise AssertionError(f"expected 168 Fano isomorphisms, got {len(isomorphisms)}")
    point_permutation, line_permutation = min(isomorphisms)

    support_permutation = tuple(point_permutation) + tuple(
        7 + line_permutation[line] for line in range(7)
    )
    stage_o_index = {label: index for index, label in enumerate(stage_fixed.labels)}
    o_permutation = tuple(
        stage_o_index[
            (
                point_permutation[point],
                line_permutation[line],
                copy_index,
            )
        ]
        for point, line, copy_index in candidate_fixed.labels
    )
    if sorted(support_permutation) != list(range(S_SIZE)):
        raise AssertionError("support map is not a permutation")
    if sorted(o_permutation) != list(range(O_SIZE)):
        raise AssertionError("O map is not a permutation")

    for s in range(S_SIZE):
        for t in range(S_SIZE):
            if (
                candidate_fixed.support[s][t]
                != stage_fixed.support[support_permutation[s]][
                    support_permutation[t]
                ]
            ):
                raise AssertionError("support permutation fails")
        for o in range(O_SIZE):
            if (
                candidate_fixed.incidence[s][o]
                != stage_fixed.incidence[support_permutation[s]][o_permutation[o]]
            ):
                raise AssertionError("incidence permutation fails")

    serialized_candidate_labels = tuple(
        (int(item["point"]), int(item["line"]), int(item["copy"]))
        for item in candidate_spec["fixed"]["O_labels"]
    )
    if serialized_candidate_labels != candidate_fixed.labels:
        raise AssertionError("candidate O labels disagree with its Fano construction")
    candidate_support_rows = tuple(
        tuple(int(x) for x in row) for row in candidate_spec["fixed"]["A_S_rows"]
    )
    candidate_incidence_rows = tuple(
        tuple(int(x) for x in row) for row in candidate_spec["fixed"]["F_rows"]
    )
    if candidate_support_rows != candidate_fixed.support:
        raise AssertionError("serialized candidate support matrix disagrees")
    if candidate_incidence_rows != candidate_fixed.incidence:
        raise AssertionError("serialized candidate incidence matrix disagrees")

    return {
        "candidate_fixed": candidate_fixed,
        "stage_fixed": stage_fixed,
        "fano_isomorphism_count": len(isomorphisms),
        "chosen_point_map_candidate_to_wave33": list(point_permutation),
        "chosen_line_map_candidate_to_wave33": list(line_permutation),
        "support_vertex_map_candidate_to_wave33": list(support_permutation),
        "O_vertex_map_candidate_to_wave33": list(o_permutation),
        "O_vertex_map_sha256": hashlib.sha256(
            canonical_bytes(o_permutation)
        ).hexdigest(),
        "support_exact_under_map": True,
        "incidence_exact_under_map": True,
        "candidate_serialized_fixed_data_exact": True,
        "candidate_hashes": {
            "support_adjacency_sha256": hashlib.sha256(
                canonical_bytes(candidate_fixed.support)
            ).hexdigest(),
            "support_to_O_incidence_sha256": hashlib.sha256(
                canonical_bytes(candidate_fixed.incidence)
            ).hexdigest(),
            "O_labels_tuple_sha256": hashlib.sha256(
                canonical_bytes(candidate_fixed.labels)
            ).hexdigest(),
            "O_labels_dict_sha256": hashlib.sha256(
                canonical_bytes(candidate_spec["fixed"]["O_labels"])
            ).hexdigest(),
        },
        "stage_hashes": {
            "support_adjacency_sha256": hashlib.sha256(
                canonical_bytes(stage_fixed.support)
            ).hexdigest(),
            "support_to_O_incidence_sha256": hashlib.sha256(
                canonical_bytes(stage_fixed.incidence)
            ).hexdigest(),
            "O_labels_tuple_sha256": hashlib.sha256(
                canonical_bytes(stage_fixed.labels)
            ).hexdigest(),
        },
    }


def threshold_state_count(n: int, target: int) -> int:
    if target in (0, n):
        return 0
    cap = target + 1
    return cap * n - cap * (cap - 1) // 2


def threshold_clause_count(n: int, target: int) -> int:
    if target in (0, n):
        return n
    cap = target + 1
    return 2 * cap * cap + 2 + (n - cap) * (4 * cap - 1)


@dataclass
class Family:
    semantic_constraints: int = 0
    variables: int = 0
    clauses: int = 0


class ClauseStreamComparator:
    def __init__(
        self,
        raw_path: Path,
        expected_variables: int,
        expected_clauses: int,
    ) -> None:
        self.raw_path = raw_path
        self.expected_variables = expected_variables
        self.expected_clauses = expected_clauses
        self.handle = raw_path.open("rb")
        self.actual_hasher = hashlib.sha256()
        self.expected_hasher = hashlib.sha256()
        self.expected_size = 0
        expected_header = (
            f"p cnf {expected_variables} {expected_clauses}\n".encode("ascii")
        )
        actual_header = self.handle.readline()
        self.actual_hasher.update(actual_header)
        self.expected_hasher.update(expected_header)
        self.expected_size += len(expected_header)
        if actual_header != expected_header:
            raise AssertionError(
                f"DIMACS header differs: {actual_header!r} != {expected_header!r}"
            )
        self.clauses = 0
        self.length_histogram: Counter[int] = Counter()
        self.seen = bytearray(expected_variables + 1)
        self.semantic_hasher = hashlib.sha256()
        self.semantic_records = 0
        self.maximum_variable = 0

    def note_variable(self, variable: int, kind: str, fields: Mapping[str, object]) -> None:
        record = {"id": variable, "kind": kind, **fields}
        self.semantic_hasher.update(canonical_bytes(record))
        self.semantic_records += 1

    def clause(self, literals: Sequence[int]) -> None:
        clause = tuple(int(value) for value in literals)
        if any(value == 0 for value in clause):
            raise AssertionError("expected clause contains literal zero")
        if len(set(clause)) != len(clause):
            raise AssertionError("expected clause repeats a literal")
        if any(-value in clause for value in clause):
            raise AssertionError("expected clause is tautological")
        if any(abs(value) > self.expected_variables for value in clause):
            raise AssertionError("expected clause exceeds variable range")
        if clause:
            expected_line = (
                " ".join(str(value) for value in clause) + " 0\n"
            ).encode("ascii")
        else:
            expected_line = b"0\n"
        actual_line = self.handle.readline()
        self.actual_hasher.update(actual_line)
        self.expected_hasher.update(expected_line)
        self.expected_size += len(expected_line)
        self.clauses += 1
        if actual_line != expected_line:
            raise AssertionError(
                f"clause {self.clauses} differs: "
                f"observed={actual_line[:200]!r}, expected={expected_line[:200]!r}"
            )
        self.length_histogram[len(clause)] += 1
        for literal in clause:
            variable = abs(literal)
            self.seen[variable] = 1
            self.maximum_variable = max(self.maximum_variable, variable)

    def finish(self) -> dict[str, object]:
        extra = self.handle.read(1)
        self.handle.close()
        if extra:
            raise AssertionError("DIMACS has bytes after the expected clause stream")
        if self.clauses != self.expected_clauses:
            raise AssertionError(
                f"expected {self.expected_clauses} clauses, generated {self.clauses}"
            )
        missing = [
            variable
            for variable in range(1, self.expected_variables + 1)
            if not self.seen[variable]
        ]
        if missing:
            raise AssertionError(f"{len(missing)} variables never occur: {missing[:20]}")
        actual_hash = self.actual_hasher.hexdigest()
        expected_hash = self.expected_hasher.hexdigest()
        if actual_hash != expected_hash:
            raise AssertionError("actual and expected stream hashes differ")
        actual_size = self.raw_path.stat().st_size
        if actual_size != self.expected_size:
            raise AssertionError("actual and expected DIMACS sizes differ")
        return {
            "exact_byte_stream_match": True,
            "variables": self.expected_variables,
            "clauses": self.clauses,
            "bytes": actual_size,
            "sha256": actual_hash,
            "expected_sha256": expected_hash,
            "maximum_variable": self.maximum_variable,
            "all_variables_occur": True,
            "clause_length_histogram": {
                str(length): count
                for length, count in sorted(self.length_histogram.items())
            },
            "semantic_variable_records": self.semantic_records,
            "semantic_variable_map_sha256": self.semantic_hasher.hexdigest(),
        }


class IndependentCnfBuilder:
    def __init__(self, stream: ClauseStreamComparator) -> None:
        self.stream = stream
        self.variable_count = 0
        self.clause_count = 0
        self.families: OrderedDict[str, Family] = OrderedDict()
        self.groups: OrderedDict[str, dict[str, int | bool]] = OrderedDict()
        self.target_distributions: dict[str, Counter[tuple[int, int]]] = {}

    def family(self, name: str) -> Family:
        if name not in self.families:
            self.families[name] = Family()
        return self.families[name]

    def allocate(
        self, owner_family: str, group: str, kind: str, **fields: object
    ) -> int:
        self.variable_count += 1
        variable = self.variable_count
        self.family(owner_family).variables += 1
        group_record = self.groups.setdefault(
            group,
            {
                "count": 0,
                "first": variable,
                "last": variable,
                "contiguous": True,
            },
        )
        if group_record["count"] and variable != int(group_record["last"]) + 1:
            group_record["contiguous"] = False
        group_record["count"] = int(group_record["count"]) + 1
        group_record["last"] = variable
        self.stream.note_variable(variable, kind, fields)
        return variable

    def add_clause(self, family: str, *literals: int) -> None:
        self.family(family).clauses += 1
        self.clause_count += 1
        self.stream.clause(literals)

    def note_constraint(
        self, family: str, literals: Sequence[int], target: int
    ) -> None:
        self.family(family).semantic_constraints += 1
        self.target_distributions.setdefault(family, Counter())[
            (len(literals), target)
        ] += 1

    def conjunction(
        self,
        family: str,
        group: str,
        kind: str,
        left: int,
        right: int,
        **fields: object,
    ) -> int:
        output = self.allocate(family, group, kind, **fields)
        self.add_clause(family, -output, left)
        self.add_clause(family, -output, right)
        self.add_clause(family, -left, -right, output)
        return output

    def exact(
        self,
        family: str,
        key: Sequence[int],
        literals: Sequence[int],
        target: int,
    ) -> None:
        self.note_constraint(family, literals, target)
        n = len(literals)
        if target < 0 or target > n:
            self.add_clause(family)
            return
        if target == 0:
            for literal in literals:
                self.add_clause(family, -literal)
            return
        if target == n:
            for literal in literals:
                self.add_clause(family, literal)
            return

        previous: dict[int, int] = {}
        for prefix, literal in enumerate(literals, start=1):
            current: dict[int, int] = {}
            for threshold in range(1, min(prefix, target + 1) + 1):
                output = self.allocate(
                    family,
                    "aux_cardinality",
                    "CARD_GE",
                    family=family,
                    key=list(key),
                    prefix=prefix,
                    threshold=threshold,
                )
                a: int | bool = previous.get(threshold, False)
                b: int | bool = (
                    True
                    if threshold == 1
                    else previous.get(threshold - 1, False)
                )
                self._threshold_equivalence(family, output, a, b, literal)
                current[threshold] = output
            previous = current
        self.add_clause(family, previous[target])
        self.add_clause(family, -previous[target + 1])

    def _threshold_equivalence(
        self,
        family: str,
        output: int,
        prior_same: int | bool,
        prior_lower: int | bool,
        literal: int,
    ) -> None:
        """Encode y iff a OR (b AND x), in the candidate's frozen clause order."""

        if prior_same is True:
            self.add_clause(family, output)
        elif prior_same is False:
            if prior_lower is True:
                self.add_clause(family, -output, literal)
                self.add_clause(family, -literal, output)
            elif prior_lower is False:
                self.add_clause(family, -output)
            else:
                lower = int(prior_lower)
                self.add_clause(family, -output, lower)
                self.add_clause(family, -output, literal)
                self.add_clause(family, -lower, -literal, output)
        elif prior_lower is True:
            same = int(prior_same)
            self.add_clause(family, -output, same, literal)
            self.add_clause(family, -same, output)
            self.add_clause(family, -literal, output)
        elif prior_lower is False:
            same = int(prior_same)
            self.add_clause(family, -output, same)
            self.add_clause(family, -same, output)
        else:
            same = int(prior_same)
            lower = int(prior_lower)
            self.add_clause(family, -output, same, lower)
            self.add_clause(family, -output, same, literal)
            self.add_clause(family, -same, output)
            self.add_clause(family, -lower, -literal, output)


def offdiagonal_overlap(fixed: FixedData, i: int, j: int) -> int:
    return sum(
        fixed.incidence[s][i] * fixed.incidence[s][j] for s in range(S_SIZE)
    )


def independently_reconstruct_formula(
    raw_path: Path,
    fixed: FixedData,
    expected_variables: int = 1_233_001,
    expected_clauses: int = 4_323_943,
) -> dict[str, object]:
    stream = ClauseStreamComparator(raw_path, expected_variables, expected_clauses)
    builder = IndependentCnfBuilder(stream)

    d = [
        [
            builder.allocate(
                "primary_variables", "primary_D", "D", i=i, j=j
            )
            for j in range(O_SIZE)
        ]
        for i in range(O_SIZE)
    ]
    b = [
        [
            builder.allocate(
                "primary_variables", "primary_B", "B", i=i, q=q
            )
            for q in range(Q_SIZE)
        ]
        for i in range(O_SIZE)
    ]
    if d[0][0] != 1 or d[-1][-1] != 4900:
        raise AssertionError("ordered D primary mapping drift")
    if b[0][0] != 4901 or b[-1][-1] != 5950:
        raise AssertionError("B primary mapping drift")

    for i in range(O_SIZE):
        builder.note_constraint("D_hollow", [d[i][i]], 0)
        builder.add_clause("D_hollow", -d[i][i])
    for i in range(O_SIZE):
        for j in range(i + 1, O_SIZE):
            builder.family("D_symmetry").semantic_constraints += 1
            builder.add_clause("D_symmetry", -d[i][j], d[j][i])
            builder.add_clause("D_symmetry", d[i][j], -d[j][i])

    for i in range(O_SIZE):
        builder.exact(
            "D_row_weight_9",
            (i,),
            [d[i][j] for j in range(O_SIZE) if j != i],
            9,
        )
        builder.exact("B_row_weight_3", (i,), list(b[i]), 3)

    for s in range(S_SIZE):
        support_o = [o for o in range(O_SIZE) if fixed.incidence[s][o]]
        for q in range(Q_SIZE):
            builder.exact(
                "SQ_block_FB_equals_2J",
                (s, q),
                [b[o][q] for o in support_o],
                2,
            )

    for s in range(S_SIZE):
        support_o = [o for o in range(O_SIZE) if fixed.incidence[s][o]]
        for o in range(O_SIZE):
            fixed_asf = sum(
                fixed.support[s][t] * fixed.incidence[t][o]
                for t in range(S_SIZE)
            )
            target = 2 - fixed.incidence[s][o] - fixed_asf
            builder.exact(
                "SO_block_ASF_plus_FD",
                (s, o),
                [d[o_prime][o] for o_prime in support_o if o_prime != o],
                target,
            )

    for i in range(O_SIZE):
        builder.exact(
            "OO_block_diagonal",
            (i,),
            [d[i][j] for j in range(O_SIZE) if j != i] + list(b[i]),
            12,
        )

    for i in range(O_SIZE):
        for j in range(i + 1, O_SIZE):
            products: list[int] = []
            for k in range(O_SIZE):
                if k in (i, j):
                    continue
                products.append(
                    builder.conjunction(
                        "OO_block_offdiagonal",
                        "aux_product_DD",
                        "AND_OO_DD",
                        d[i][k],
                        d[k][j],
                        i=i,
                        j=j,
                        k=k,
                    )
                )
            for q in range(Q_SIZE):
                products.append(
                    builder.conjunction(
                        "OO_block_offdiagonal",
                        "aux_product_BB_OO",
                        "AND_OO_BB",
                        b[i][q],
                        b[j][q],
                        i=i,
                        j=j,
                        q=q,
                    )
                )
            builder.exact(
                "OO_block_offdiagonal",
                (i, j),
                products + [d[i][j]],
                2 - offdiagonal_overlap(fixed, i, j),
            )

    for i in range(O_SIZE):
        for q in range(Q_SIZE):
            products = [
                builder.conjunction(
                    "OQ_block_DB",
                    "aux_product_DB",
                    "AND_OQ_DB",
                    d[i][k],
                    b[k][q],
                    i=i,
                    q=q,
                    k=k,
                )
                for k in range(O_SIZE)
                if k != i
            ]
            builder.exact(
                "OQ_block_DB", (i, q), products + [b[i][q]], 2
            )

    for q in range(Q_SIZE):
        builder.exact(
            "QQ_block_column_weight_14",
            (q,),
            [b[o][q] for o in range(O_SIZE)],
            14,
        )
    for q in range(Q_SIZE):
        for r in range(q + 1, Q_SIZE):
            products = [
                builder.conjunction(
                    "QQ_block_pair_intersection_2",
                    "aux_product_BB_QQ",
                    "AND_QQ_BB",
                    b[o][q],
                    b[o][r],
                    q=q,
                    r=r,
                    o=o,
                )
                for o in range(O_SIZE)
            ]
            builder.exact(
                "QQ_block_pair_intersection_2", (q, r), products, 2
            )

    if builder.variable_count != expected_variables:
        raise AssertionError(
            f"independent variable total {builder.variable_count} != {expected_variables}"
        )
    if builder.clause_count != expected_clauses:
        raise AssertionError(
            f"independent clause total {builder.clause_count} != {expected_clauses}"
        )
    stream_result = stream.finish()
    return {
        **stream_result,
        "families": {
            name: asdict(stats) for name, stats in builder.families.items()
        },
        "variable_groups": builder.groups,
        "target_distributions": {
            family: [
                {"scope_size": n, "target": target, "count": count}
                for (n, target), count in sorted(distribution.items())
            ]
            for family, distribution in sorted(
                builder.target_distributions.items()
            )
        },
        "independent_generator_imported_candidate_code": False,
        "candidate_generator_executed": False,
    }


def audit_gzip(raw_path: Path, gzip_path: Path) -> dict[str, object]:
    compressed_hash = sha256_path(gzip_path)
    raw_hash = hashlib.sha256()
    restored_hash = hashlib.sha256()
    raw_size = 0
    restored_size = 0
    exact = True
    with gzip_path.open("rb") as handle:
        header = handle.read(10)
    with raw_path.open("rb") as raw, gzip.open(gzip_path, "rb") as restored:
        while True:
            raw_block = raw.read(1024 * 1024)
            restored_block = restored.read(1024 * 1024)
            if raw_block != restored_block:
                exact = False
            if not raw_block and not restored_block:
                break
            raw_hash.update(raw_block)
            restored_hash.update(restored_block)
            raw_size += len(raw_block)
            restored_size += len(restored_block)
    if not exact:
        raise AssertionError("gzip decompression differs from raw CNF")
    if raw_hash.hexdigest() != restored_hash.hexdigest():
        raise AssertionError("round-trip digests differ")
    header_checks = {
        "magic_deflate": header[:3] == b"\x1f\x8b\x08",
        "flags_zero_empty_filename": len(header) == 10 and header[3] == 0,
        "mtime_zero": len(header) == 10 and header[4:8] == b"\x00\x00\x00\x00",
        "xfl_level9": len(header) == 10 and header[8] == 2,
        "os_unknown_255": len(header) == 10 and header[9] == 255,
    }
    if not all(header_checks.values()):
        raise AssertionError(header_checks)
    return {
        "compressed_sha256": compressed_hash,
        "compressed_bytes": gzip_path.stat().st_size,
        "header_hex": header.hex(),
        "header_checks": header_checks,
        "raw_sha256": raw_hash.hexdigest(),
        "raw_bytes": raw_size,
        "restored_sha256": restored_hash.hexdigest(),
        "restored_bytes": restored_size,
        "exact_chunkwise_round_trip": exact,
        "gzip_crc_and_size_footer_accepted": True,
    }


def expected_adjacency_for_primary_signature(
    fixed: FixedData, bit: int
) -> list[list[int]]:
    adjacency = [[0] * 99 for _ in range(99)]
    for s in range(S_SIZE):
        for t in range(S_SIZE):
            adjacency[s][t] = fixed.support[s][t]
        for o in range(O_SIZE):
            adjacency[s][14 + o] = adjacency[14 + o][s] = fixed.incidence[s][o]
    for i in range(O_SIZE):
        for j in range(O_SIZE):
            variable = 1 + 70 * i + j
            adjacency[14 + i][14 + j] = (variable >> bit) & 1
        for q in range(Q_SIZE):
            variable = 4901 + 15 * i + q
            value = (variable >> bit) & 1
            adjacency[14 + i][84 + q] = value
            adjacency[84 + q][14 + i] = value
    return adjacency


def independent_block_failure_counts(adjacency: Sequence[Sequence[int]]) -> dict[str, int]:
    counts = {"SS": 0, "SQ": 0, "SO": 0, "OO": 0, "OQ": 0, "QQ": 0}
    for i in range(99):
        for j in range(99):
            lhs = sum(adjacency[i][k] * adjacency[k][j] for k in range(99))
            rhs = 12 * int(i == j) - adjacency[i][j] + 2
            if lhs == rhs:
                continue
            if i < 14 and j < 14:
                block = "SS"
            elif (i < 14 and j >= 84) or (j < 14 and i >= 84):
                block = "SQ"
            elif (i < 14 <= j < 84) or (j < 14 <= i < 84):
                block = "SO"
            elif 14 <= i < 84 and 14 <= j < 84:
                block = "OO"
            elif (14 <= i < 84 <= j) or (14 <= j < 84 <= i):
                block = "OQ"
            else:
                block = "QQ"
            counts[block] += 1
    return counts


def audit_model_route(fixed: FixedData) -> dict[str, object]:
    decoder = CANDIDATE / "decode_model.py"
    checker = CANDIDATE / "check_witness.py"
    signature_bits = (5950).bit_length()
    reconstructed_d_ids = [[0] * O_SIZE for _ in range(O_SIZE)]
    reconstructed_b_ids = [[0] * Q_SIZE for _ in range(O_SIZE)]
    checker_result: dict[str, object] | None = None

    with tempfile.TemporaryDirectory() as temporary:
        temp = Path(temporary)
        for bit in range(signature_bits):
            model = temp / f"signature-{bit}.model"
            output = temp / f"signature-{bit}.json"
            literals = [
                str(variable if ((variable >> bit) & 1) else -variable)
                for variable in range(1, 5951)
            ]
            lines = ["s SATISFIABLE"]
            for start in range(0, len(literals), 200):
                lines.append("v " + " ".join(literals[start : start + 200]) + " 0")
            model.write_text("\n".join(lines) + "\n", encoding="ascii")
            decode = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(decoder),
                    "--model",
                    str(model),
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            if decode.returncode != 0:
                raise AssertionError(
                    f"decoder failed on signature bit {bit}: {decode.stderr}"
                )
            payload = load_json(output)
            observed = [
                [int(value) for value in row] for row in payload["adjacency"]
            ]
            expected = expected_adjacency_for_primary_signature(fixed, bit)
            if observed != expected:
                raise AssertionError(f"decoder mapping differs at signature bit {bit}")
            if tuple(
                (item["point"], item["line"], item["copy"])
                for item in payload["O_labels"]
            ) != fixed.labels:
                raise AssertionError("decoder O-label metadata differs")
            for i in range(O_SIZE):
                for j in range(O_SIZE):
                    reconstructed_d_ids[i][j] |= observed[14 + i][14 + j] << bit
                for q in range(Q_SIZE):
                    reconstructed_b_ids[i][q] |= observed[14 + i][84 + q] << bit

            if bit == 0:
                checked = subprocess.run(
                    [
                        sys.executable,
                        "-B",
                        str(checker),
                        "--witness",
                        str(output),
                    ],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if checked.returncode != 1:
                    raise AssertionError("hostile synthetic witness was not rejected")
                checker_result = json.loads(checked.stdout)
                expected_failures = independent_block_failure_counts(expected)
                if (
                    checker_result["checks"]["block_failure_counts"]
                    != expected_failures
                ):
                    raise AssertionError("candidate checker block census differs")

    expected_d_ids = [
        [1 + 70 * i + j for j in range(O_SIZE)] for i in range(O_SIZE)
    ]
    expected_b_ids = [
        [4901 + 15 * i + q for q in range(Q_SIZE)] for i in range(O_SIZE)
    ]
    if reconstructed_d_ids != expected_d_ids:
        raise AssertionError("D model-map signatures fail")
    if reconstructed_b_ids != expected_b_ids:
        raise AssertionError("B model-map signatures fail")
    assert checker_result is not None
    return {
        "signature_models": signature_bits,
        "primary_ids_distinguished": 5950,
        "D_mapping_exact": True,
        "B_mapping_exact": True,
        "fixed_cells_exact": True,
        "O_label_metadata_exact": True,
        "candidate_decoder_executed_on_synthetic_controls": True,
        "candidate_checker_executed_on_hostile_control": True,
        "hostile_control_rejected": checker_result["status"] == "FAIL",
        "checker_block_failure_counts_match_independent": True,
        "decoder_requires_all_primary_variables": True,
        "decoder_requires_all_auxiliary_variables": False,
        "decoder_checks_dimacs_clauses": False,
        "safety_boundary": (
            "decoder output is explicitly unchecked; a positive claim still "
            "requires the independent full adjacency checker"
        ),
    }


def static_python_audit() -> dict[str, object]:
    paths = [
        CANDIDATE / "generate_cnf.py",
        CANDIDATE / "decode_model.py",
        CANDIDATE / "check_witness.py",
        CANDIDATE / "audit_dimacs.py",
        CANDIDATE / "package_cnf.py",
        CANDIDATE / "test_encoding.py",
    ]
    results: dict[str, object] = {}
    for path in paths:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        dynamic_calls = [
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in {"eval", "exec", "compile", "__import__"}
        ]
        results[path.name] = {
            "sha256": sha256_path(path),
            "syntax": "PASS",
            "dynamic_execution_calls": dynamic_calls,
        }
    return results


def line_ending_audit() -> dict[str, object]:
    raw_paths = [
        CANDIDATE / "compression-audit.json",
        CANDIDATE / "dimacs-audit.json",
        CANDIDATE / "test-results.txt",
    ]
    results: dict[str, object] = {}
    for path in raw_paths:
        data = path.read_bytes()
        crlf = data.count(b"\r\n")
        bare_lf = data.count(b"\n") - crlf
        bare_cr = data.count(b"\r") - crlf
        results[path.name] = {
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "crlf_count": crlf,
            "bare_lf_count": bare_lf,
            "bare_cr_count": bare_cr,
            "contains_crlf": crlf > 0,
        }
    attributes = (ROOT / ".gitattributes").read_text(encoding="utf-8")
    expected_rules = [
        f"attempts/wave34-rooted-encoding/{path.name} -text -diff"
        for path in raw_paths
    ]
    return {
        "files": results,
        "gitattributes_sha256": sha256_path(ROOT / ".gitattributes"),
        "expected_rules": expected_rules,
        "all_expected_rules_present": all(rule in attributes for rule in expected_rules),
    }


def preflight_reproducibility_audit() -> dict[str, object]:
    preflight_path = CANDIDATE / "encoding-preflight.json"
    emitted_path = CANDIDATE / "encoding-audit.json"
    preflight = load_json(preflight_path)
    emitted = load_json(emitted_path)
    normalized_emitted = copy.deepcopy(emitted)
    normalized_preflight = copy.deepcopy(preflight)
    normalized_emitted.pop("status", None)
    normalized_preflight.pop("status", None)
    for field in ("path", "sha256", "bytes"):
        normalized_emitted["cnf"].pop(field, None)
    contiguous_values: dict[str, bool] = {}
    for group, record in normalized_emitted["cnf"]["variable_groups"].items():
        contiguous_values[group] = bool(record.pop("contiguous"))
    semantic_counts_equal = normalized_emitted == normalized_preflight

    current_shape = copy.deepcopy(preflight)
    for group, contiguous in contiguous_values.items():
        current_shape["cnf"]["variable_groups"][group]["contiguous"] = contiguous
    current_bytes = (
        json.dumps(current_shape, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    current_hash = hashlib.sha256(current_bytes).hexdigest()
    return {
        "frozen_preflight_sha256": sha256_path(preflight_path),
        "frozen_preflight_bytes": preflight_path.stat().st_size,
        "semantic_counts_equal_to_emitted_audit": semantic_counts_equal,
        "only_normalized_difference": (
            "current emitted audit adds variable-group contiguous metadata"
        ),
        "current_generator_shape_preflight_sha256": current_hash,
        "current_generator_shape_preflight_bytes": len(current_bytes),
        "recorded_preflight_byte_reproducible_by_current_generator": (
            current_hash == sha256_path(preflight_path)
        ),
        "formula_impact": "NONE",
    }


def gadget_audit() -> dict[str, object]:
    and_pass = True
    for left, right, output in itertools.product((False, True), repeat=3):
        clauses = (
            (not output) or left,
            (not output) or right,
            output or (not left) or (not right),
        )
        and_pass &= all(clauses) == (output == (left and right))

    exact_cases = 0
    exact_pass = True
    # This independent semantic recurrence check does not use candidate code.
    for n in range(1, 8):
        for target in range(n + 1):
            for bits in itertools.product((False, True), repeat=n):
                thresholds: dict[tuple[int, int], bool] = {}
                if 0 < target < n:
                    for prefix, bit in enumerate(bits, start=1):
                        for threshold in range(
                            1, min(prefix, target + 1) + 1
                        ):
                            a = thresholds.get((prefix - 1, threshold), False)
                            b = (
                                True
                                if threshold == 1
                                else thresholds.get(
                                    (prefix - 1, threshold - 1), False
                                )
                            )
                            thresholds[(prefix, threshold)] = a or (b and bit)
                    accepted = thresholds[(n, target)] and not thresholds[
                        (n, target + 1)
                    ]
                elif target == 0:
                    accepted = not any(bits)
                else:
                    accepted = all(bits)
                exact_pass &= accepted == (sum(bits) == target)
                exact_cases += 1

    def encoded_exact(n: int, target: int) -> tuple[int, list[tuple[int, ...]]]:
        next_variable = n + 1
        clauses: list[tuple[int, ...]] = []

        def allocate() -> int:
            nonlocal next_variable
            result = next_variable
            next_variable += 1
            return result

        def recurrence(
            output: int,
            prior_same: int | bool,
            prior_lower: int | bool,
            literal: int,
        ) -> None:
            if prior_same is True:
                clauses.append((output,))
            elif prior_same is False:
                if prior_lower is True:
                    clauses.extend(((-output, literal), (-literal, output)))
                elif prior_lower is False:
                    clauses.append((-output,))
                else:
                    lower = int(prior_lower)
                    clauses.extend(
                        (
                            (-output, lower),
                            (-output, literal),
                            (-lower, -literal, output),
                        )
                    )
            elif prior_lower is True:
                same = int(prior_same)
                clauses.extend(
                    (
                        (-output, same, literal),
                        (-same, output),
                        (-literal, output),
                    )
                )
            elif prior_lower is False:
                same = int(prior_same)
                clauses.extend(((-output, same), (-same, output)))
            else:
                same = int(prior_same)
                lower = int(prior_lower)
                clauses.extend(
                    (
                        (-output, same, lower),
                        (-output, same, literal),
                        (-same, output),
                        (-lower, -literal, output),
                    )
                )

        inputs = list(range(1, n + 1))
        if target == 0:
            clauses.extend((-literal,) for literal in inputs)
            return next_variable - 1, clauses
        if target == n:
            clauses.extend((literal,) for literal in inputs)
            return next_variable - 1, clauses
        previous: dict[int, int] = {}
        for prefix, literal in enumerate(inputs, start=1):
            current: dict[int, int] = {}
            for threshold in range(1, min(prefix, target + 1) + 1):
                output = allocate()
                prior_same: int | bool = previous.get(threshold, False)
                prior_lower: int | bool = (
                    True
                    if threshold == 1
                    else previous.get(threshold - 1, False)
                )
                recurrence(output, prior_same, prior_lower, literal)
                current[threshold] = output
            previous = current
        clauses.extend(((previous[target],), (-previous[target + 1],)))
        return next_variable - 1, clauses

    encoded_cases = 0
    encoded_exact_pass = True
    for n in range(1, 5):
        for target in range(n + 1):
            variable_count, clauses = encoded_exact(n, target)
            auxiliary_ids = list(range(n + 1, variable_count + 1))
            if len(auxiliary_ids) != threshold_state_count(n, target):
                encoded_exact_pass = False
            if len(clauses) != threshold_clause_count(n, target):
                encoded_exact_pass = False
            for primary in itertools.product((False, True), repeat=n):
                extendible = False
                for auxiliary in itertools.product(
                    (False, True), repeat=len(auxiliary_ids)
                ):
                    values = {
                        variable: value
                        for variable, value in zip(
                            list(range(1, n + 1)) + auxiliary_ids,
                            primary + auxiliary,
                        )
                    }
                    if all(
                        any(
                            values[abs(literal)] == (literal > 0)
                            for literal in clause
                        )
                        for clause in clauses
                    ):
                        extendible = True
                        break
                encoded_exact_pass &= extendible == (sum(primary) == target)
                encoded_cases += 1
    return {
        "AND_truth_table_assignments": 8,
        "AND_equivalence": and_pass,
        "exact_threshold_cases": exact_cases,
        "exact_threshold_semantics": exact_pass,
        "exact_CNF_primary_assignments": encoded_cases,
        "exact_CNF_existential_equivalence": encoded_exact_pass,
        "threshold_state_formula_checked": True,
        "threshold_clause_formula_checked": True,
    }


def count_comparison(
    formula_result: Mapping[str, object],
    stage_counts: Mapping[str, object],
) -> dict[str, object]:
    candidate_histogram = formula_result["clause_length_histogram"]
    stage_histogram = stage_counts["clause_length_histogram"]
    return {
        "semantic_independent_primary_bits": 3465,
        "stage1_primary_variables": stage_counts["primary_variables"]["total"],
        "candidate_explicit_primary_variables": 5950,
        "primary_variable_difference": 2485,
        "difference_decomposition": {
            "explicit_D_diagonal_variables": 70,
            "mirrored_offdiagonal_D_variables": 2415,
            "total": 2485,
        },
        "candidate_gate_clauses": {
            "hollow_units": 70,
            "symmetry_binary_clauses": 4830,
            "total": 4900,
        },
        "product_auxiliaries_equal": (
            stage_counts["auxiliary_variables"]["product"] == 280245
        ),
        "cardinality_auxiliaries_equal": (
            stage_counts["auxiliary_variables"]["cardinality"] == 946806
        ),
        "total_variable_difference": (
            formula_result["variables"] - stage_counts["total_variables"]
        ),
        "total_clause_difference": (
            formula_result["clauses"] - stage_counts["total_clauses"]
        ),
        "clause_histogram_difference": {
            length: int(candidate_histogram[length])
            - int(stage_histogram.get(length, 0))
            for length in sorted(
                set(candidate_histogram) | set(stage_histogram), key=int
            )
        },
        "ordered_D_projection": (
            "70 diagonal bits are forced false and each of 2415 mirrored pairs "
            "is forced equal; projection to i<j is a bijection"
        ),
        "complete_domain_equivalence": True,
    }


def run() -> dict[str, object]:
    paths = {
        "candidate_release": HERE / "candidate-release.md",
        "candidate_report": ROOT / "agents" / "2026-07-24-wave34-rooted-encoding.md",
        "publication_manifest": CANDIDATE / "publication-manifest.sha256",
        "artifact_manifest": CANDIDATE / "artifact-manifest.sha256",
        "raw_cnf": CANDIDATE / "rooted-complete.cnf",
        "gzip_cnf": CANDIDATE / "rooted-complete.cnf.gz",
        "criterion_spec": CANDIDATE / "criterion-spec.json",
        "primary_map": CANDIDATE / "primary-map.json",
        "encoding_audit": CANDIDATE / "encoding-audit.json",
        "encoding_preflight": CANDIDATE / "encoding-preflight.json",
        "dimacs_audit": CANDIDATE / "dimacs-audit.json",
        "compression_audit": CANDIDATE / "compression-audit.json",
        "correction_ledger": CANDIDATE / "correction-ledger.md",
        "gitattributes": ROOT / ".gitattributes",
        "precomparison_manifest": PRECOMPARISON / "artifact-manifest.sha256",
    }
    for name, path in paths.items():
        actual = sha256_path(path)
        if actual != EXPECTED[name]:
            raise AssertionError(f"input hash drift for {name}: {actual}")

    publication = validate_sha_manifest(paths["publication_manifest"])
    complete = validate_sha_manifest(paths["artifact_manifest"])
    if publication["entry_count"] != 16 or complete["entry_count"] != 18:
        raise AssertionError("candidate manifest composition count drift")
    publication_entries = {
        entry["path"]: entry["sha256"] for entry in publication["entries"]
    }
    complete_entries = {
        entry["path"]: entry["sha256"] for entry in complete["entries"]
    }
    if any(
        complete_entries.get(path) != digest
        for path, digest in publication_entries.items()
    ):
        raise AssertionError("publication manifest is not a consistent subset")
    expected_complete_additions = {
        "attempts/wave34-rooted-encoding/publication-manifest.sha256",
        "attempts/wave34-rooted-encoding/rooted-complete.cnf",
    }
    if set(complete_entries) - set(publication_entries) != expected_complete_additions:
        raise AssertionError("unexpected complete-manifest additions")

    candidate_spec = load_json(paths["criterion_spec"])
    stage_spec = load_json(PRECOMPARISON / "criterion-spec.json")
    binding = candidate_label_binding(candidate_spec, stage_spec)
    candidate_fixed: FixedData = binding.pop("candidate_fixed")
    binding.pop("stage_fixed")

    candidate_map = load_json(paths["primary_map"])
    map_checks = {
        "D_shape": candidate_map["D"]["shape"] == [70, 70],
        "D_range": (
            candidate_map["D"]["first_variable"],
            candidate_map["D"]["last_variable"],
        )
        == (1, 4900),
        "D_formula": candidate_map["D"]["formula"]
        == "var(D[i,j]) = 1 + 70*i + j",
        "B_shape": candidate_map["B"]["shape"] == [70, 15],
        "B_range": (
            candidate_map["B"]["first_variable"],
            candidate_map["B"]["last_variable"],
        )
        == (4901, 5950),
        "B_formula": candidate_map["B"]["formula"]
        == "var(B[i,q]) = 4901 + 15*i + q",
        "O_labels": tuple(
            (item["point"], item["line"], item["copy"])
            for item in candidate_map["vertex_order"]["O_labels"]
        )
        == candidate_fixed.labels,
    }
    if not all(map_checks.values()):
        raise AssertionError(map_checks)

    formula = independently_reconstruct_formula(paths["raw_cnf"], candidate_fixed)
    if formula["sha256"] != EXPECTED["raw_cnf"]:
        raise AssertionError("full independent clause stream hash differs")

    encoding_audit = load_json(paths["encoding_audit"])
    audit_fixed = encoding_audit["fixed_data"]
    binding["candidate_audit_fixed_hashes_match"] = (
        binding["candidate_hashes"]["support_adjacency_sha256"]
        == audit_fixed["support_adjacency_sha256"]
        and binding["candidate_hashes"]["support_to_O_incidence_sha256"]
        == audit_fixed["support_to_O_incidence_sha256"]
        and binding["candidate_hashes"]["O_labels_dict_sha256"]
        == audit_fixed["O_labels_sha256"]
    )
    if not binding["candidate_audit_fixed_hashes_match"]:
        raise AssertionError("candidate fixed-data hashes differ from reconstruction")
    expected_families = encoding_audit["cnf"]["families"]
    if formula["families"] != expected_families:
        raise AssertionError("candidate family audit differs from reconstruction")
    if formula["variable_groups"] != encoding_audit["cnf"]["variable_groups"]:
        raise AssertionError("candidate variable groups differ from reconstruction")
    oo_distribution = {
        str(item["target"]): item["count"]
        for item in formula["target_distributions"]["OO_block_offdiagonal"]
    }
    so_distribution: Counter[str] = Counter()
    for item in formula["target_distributions"]["SO_block_ASF_plus_FD"]:
        so_distribution[str(item["target"])] += item["count"]
    if oo_distribution != audit_fixed["OO_exact_total_target_histogram"]:
        raise AssertionError("OO target histogram differs from candidate audit")
    if dict(sorted(so_distribution.items())) != audit_fixed["SO_target_histogram"]:
        raise AssertionError("SO target histogram differs from candidate audit")

    dimacs_audit = load_json(paths["dimacs_audit"])
    if (
        formula["clause_length_histogram"]
        != dimacs_audit["observed"]["clause_length_histogram"]
        or formula["variables"] != dimacs_audit["header"]["variables"]
        or formula["clauses"] != dimacs_audit["header"]["clauses"]
    ):
        raise AssertionError("candidate DIMACS audit differs from reconstruction")

    stage_counts = load_json(PRECOMPARISON / "count-expectations.json")
    counts = count_comparison(formula, stage_counts)
    gzip_result = audit_gzip(paths["raw_cnf"], paths["gzip_cnf"])
    if gzip_result["compressed_sha256"] != EXPECTED["gzip_cnf"]:
        raise AssertionError("gzip hash differs")
    compression_audit = load_json(paths["compression_audit"])
    if (
        gzip_result["raw_sha256"] != compression_audit["source"]["sha256"]
        or gzip_result["raw_bytes"] != compression_audit["source"]["bytes"]
        or gzip_result["compressed_sha256"]
        != compression_audit["compressed"]["sha256"]
        or gzip_result["compressed_bytes"]
        != compression_audit["compressed"]["bytes"]
        or gzip_result["restored_sha256"]
        != compression_audit["round_trip"]["sha256"]
        or gzip_result["restored_bytes"]
        != compression_audit["round_trip"]["bytes"]
    ):
        raise AssertionError("candidate compression audit differs")
    model_route = audit_model_route(candidate_fixed)

    correction_ledger_covered = (
        "attempts/wave34-rooted-encoding/correction-ledger.md"
        in complete_entries
    )
    manifest_scope_note = {
        "candidate_correction_ledger_sha256": EXPECTED["correction_ledger"],
        "candidate_correction_ledger_in_publication_manifest": (
            "attempts/wave34-rooted-encoding/correction-ledger.md"
            in publication_entries
        ),
        "candidate_correction_ledger_in_complete_manifest": correction_ledger_covered,
        "candidate_artifact_manifest_self_hash_omitted": True,
        "complete_manifest_label_after_correction_is_literal": False,
        "impact": "packaging/provenance only; formula bytes remain covered",
    }

    status = {
        "encoding_exact_scope": "VERIFIED",
        "manifested_formula_bytes": "VERIFIED",
        "gzip_round_trip": "VERIFIED",
        "complete_domain_no_symmetry_mapping": "VERIFIED",
        "SAT": "UNKNOWN",
        "UNSAT": "UNKNOWN",
        "rooted_graph_extension": "UNKNOWN",
        "rooted_endpoint": "UNKNOWN",
        "n3_708": "UNKNOWN",
        "Conway_99": "UNKNOWN",
        "novelty": "UNKNOWN",
    }

    return {
        "schema_version": 1,
        "role": "verifier",
        "claim_label": "VERIFIED",
        "scope": (
            "candidate CNF is exactly a complete unrestricted labeled encoding "
            "of the Wave 33 six-block graph criterion; no satisfiability claim"
        ),
        "input_integrity": {
            "all_named_input_hashes_pass": True,
            "precomparison_manifest_unchanged": True,
            "precomparison_manifest_sha256": EXPECTED[
                "precomparison_manifest"
            ],
            "publication_manifest": publication,
            "complete_local_manifest": complete,
            "publication_is_consistent_subset": True,
            "complete_manifest_additions": sorted(expected_complete_additions),
        },
        "canonical_label_binding": binding,
        "primary_map_checks": map_checks,
        "gadget_audit": gadget_audit(),
        "formula_reconstruction": formula,
        "count_comparison": counts,
        "gzip_audit": gzip_result,
        "model_route_audit": model_route,
        "candidate_python_static_audit": static_python_audit(),
        "line_ending_audit": line_ending_audit(),
        "preflight_reproducibility": preflight_reproducibility_audit(),
        "manifest_scope_note": manifest_scope_note,
        "no_symmetry_scope": {
            "automorphism_or_orbit_clauses": 0,
            "fixed_B_design_selection": False,
            "all_70x15_B_matrices_enter_before_equations": True,
            "ordered_D_gate_projection_bijective": True,
            "exact_stream_has_no_unreconstructed_extra_clauses": True,
        },
        "candidate_code_execution_boundary": {
            "generator_imported": False,
            "generator_executed": False,
            "decoder_executed_only_on_verifier_synthetic_models": True,
            "witness_checker_executed_only_on_hostile_synthetic_graph": True,
            "large_solver_run": False,
            "proof_checker_run": False,
        },
        "corrections": [
            {
                "id": "W34-RC-V-001",
                "severity": "PACKAGING",
                "finding": (
                    "The post-freeze candidate correction-ledger.md is outside "
                    "both candidate manifests, so the 18-entry manifest is not "
                    "literally complete after that ledger was added."
                ),
                "formula_impact": "NONE",
            },
            {
                "id": "W34-RC-V-002",
                "severity": "REPRODUCIBILITY",
                "finding": (
                    "The frozen preflight JSON predates the current generator's "
                    "variable-group contiguous field and is not byte-reproducible "
                    "by the recorded command with the published generator."
                ),
                "formula_impact": "NONE; all normalized counts match",
            },
            {
                "id": "W34-RC-V-003",
                "severity": "DOCUMENTATION",
                "finding": (
                    "decode_model.py enforces complete primary assignments only; "
                    "it neither requires auxiliaries nor evaluates the CNF. Its "
                    "DECODED_UNCHECKED status and mandatory graph checker preserve "
                    "the positive-certificate safety boundary."
                ),
                "formula_impact": "NONE",
            },
        ],
        "limitations": [
            "No SAT or UNSAT solver run was performed.",
            "No model, 99-vertex witness, or proof certificate exists.",
            "The encoding theorem is conditional and graph-scoped.",
            "The candidate checker has no positive target control because no witness is known.",
        ],
        "status": status,
        "verdict": (
            "STATIC_AND_BYTE_EXACT_COMPLETE_DOMAIN_ENCODING_PASS_WITH_NONFORMULA_CORRECTIONS"
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = run()
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "formula_sha256": result["formula_reconstruction"]["sha256"],
                "semantic_map_sha256": result["formula_reconstruction"][
                    "semantic_variable_map_sha256"
                ],
                "variables": result["formula_reconstruction"]["variables"],
                "clauses": result["formula_reconstruction"]["clauses"],
                "gzip_round_trip": result["gzip_audit"][
                    "exact_chunkwise_round_trip"
                ],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
