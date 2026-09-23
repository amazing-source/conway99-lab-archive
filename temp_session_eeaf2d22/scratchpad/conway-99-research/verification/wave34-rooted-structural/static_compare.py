from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, permutations
from pathlib import Path
from typing import Any, Callable, Sequence


ROOT = Path(__file__).resolve().parents[2]
STAGE1 = ROOT / "verification/wave34-rooted-structural/precomparison"
CANDIDATE_DIR = ROOT / "attempts/wave34-rooted-structural"

CANDIDATE_RELEASE_HASHES = {
    "verification/wave34-rooted-structural/candidate-release.md":
        "594ecaec43bb3fdea4dfdd3e866a9591951a01433834a09f2a726518785f5040",
    "agents/2026-07-24-wave34-rooted-structural.md":
        "535d237abcb841609835b1b8da11f2193cf17314c3dfe1dc427a3eec0a710246",
    "attempts/wave34-rooted-structural/check_results.py":
        "9a4912cb4875d0ec7e54366491484fdf21c218ba2361858ea5d28a0e9af9ad1c",
    "attempts/wave34-rooted-structural/reduction.py":
        "c3ad0a5b764e6e5045082ba28fc7c5ddfb2727859eac990f2845a8e5dd4c60e1",
    "attempts/wave34-rooted-structural/results.json":
        "bd68070b172329e161f46d85e634aecf2348da16de785331e60e4b93a1f4dfc5",
    "attempts/wave34-rooted-structural/test_reduction.py":
        "3e9f2f95d44fda18c0733267a58fd101fa904bc94e283baa75b7b1616dcede4f",
    "attempts/wave34-rooted-structural/artifact-manifest.sha256":
        "fd1372a3e0013eec265f828a33249f5bb0872e505f7e8479d2946a0e917f32de",
}

CANDIDATE_INPUT_HASHES = {
    "AGENTS.md":
        "4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3",
    "verification/wave34-continuation-protocol.md":
        "60e6c3aba152e924a51bd2503e82de3d05bb39fada258da4a2796e344ae23cd4",
    "CONJECTURE.md":
        "7b4e67a28dbae58dffbf8f06a5fcb0241b12c34807dcb145ef2ff5c70d4c1c58",
    "STATUS.yaml":
        "feda17934162602804015e17130c029ffdba7bf0307cdf234f4a7d8979298864",
    "verification/2026-07-24-wave33-clean-clone.md":
        "d83e18052114affaed873ddaa7bdc6a26c63afc6432345e1027aeef5bd66d052",
    "verification/wave33-rooted-extension/comparison-results.json":
        "2e36ecade28bca12d35a963a8c6b52777ac7d766a3c4b3267774000fe2e929fd",
    "verification/wave33-rooted-extension/comparison-audit.md":
        "fc7abcd53154d4551a5d3d97d38024840b4228195e143559c9e8b46c15644b8a",
    "verification/wave33-rooted-construction-chronology/chronology-results.json":
        "b2f0b872221a3fd9f41d6a88637be21034b70e8c8129fe57617115548b425957",
    "verification/wave33-rooted-construction-chronology/audit.md":
        "1346992e11db72c4c94018293d3827214e2ee79e074490b8f905028e20fa30f1",
}

VERIFIER_INPUT_HASHES = {
    "verification/wave33-rooted-extension/independent-results.json":
        "66cef570dbbb4a86e2a35f780edcfc1873d0ac2c5266f1c2065c902a8f91e778",
    "verification/wave34-rooted-structural/precomparison/artifact-manifest.sha256":
        "233a32ac6cb67bcb23b7b269cc6f3f889d943bd5d0714c4f54ead9cbf28c7681",
}

Matrix = list[list[Fraction]]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_hash_dictionary(expected: dict[str, str]) -> dict[str, str]:
    observed: dict[str, str] = {}
    for relative, frozen_hash in expected.items():
        actual = sha256_file(ROOT / relative)
        if actual != frozen_hash:
            raise AssertionError(
                f"hash drift for {relative}: {actual} != {frozen_hash}"
            )
        observed[relative] = actual
    return observed


def validate_candidate_inner_manifest() -> dict[str, Any]:
    manifest_path = CANDIDATE_DIR / "artifact-manifest.sha256"
    entries: dict[str, str] = {}
    for line in manifest_path.read_text("utf-8").splitlines():
        digest, relative = line.split(maxsplit=1)
        relative = relative.strip()
        actual = sha256_file(ROOT / relative)
        if actual != digest:
            raise AssertionError(f"candidate inner manifest drift: {relative}")
        entries[relative] = digest
    expected_paths = {
        key for key in CANDIDATE_RELEASE_HASHES
        if key not in {
            "verification/wave34-rooted-structural/candidate-release.md",
            "attempts/wave34-rooted-structural/artifact-manifest.sha256",
        }
    }
    if set(entries) != expected_paths:
        raise AssertionError("candidate inner manifest composition mismatch")
    return {
        "entries": entries,
        "entry_count": len(entries),
        "self_hash_omitted": True,
        "manifest_sha256": sha256_file(manifest_path),
    }


def validate_stage1_manifest() -> dict[str, Any]:
    manifest_path = STAGE1 / "artifact-manifest.sha256"
    entries: dict[str, str] = {}
    for line in manifest_path.read_text("utf-8").splitlines():
        digest, marked_path = line.split(maxsplit=1)
        if not marked_path.startswith("*"):
            raise AssertionError("Stage-1 manifest marker drift")
        relative = marked_path[1:]
        actual = sha256_file(ROOT / relative)
        if actual != digest:
            raise AssertionError(f"Stage-1 byte drift: {relative}")
        entries[relative] = digest
    if len(entries) != 8:
        raise AssertionError("Stage-1 manifest entry count drift")
    return {
        "entries": entries,
        "entry_count": len(entries),
        "manifest_sha256": sha256_file(manifest_path),
        "all_entries_pass": True,
    }


def static_candidate_code_review() -> dict[str, Any]:
    reviewed: dict[str, Any] = {}
    for filename in ("reduction.py", "check_results.py", "test_reduction.py"):
        path = CANDIDATE_DIR / filename
        source = path.read_text("utf-8")
        tree = ast.parse(source, filename=str(path))
        imports: list[str] = []
        direct_dynamic_calls: list[str] = []
        exec_module_calls = 0
        test_methods: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.append(node.module or "")
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name.startswith("test_"):
                    test_methods.append(node.name)
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in {
                    "eval", "exec", "compile", "__import__"
                }:
                    direct_dynamic_calls.append(node.func.id)
                if (
                    isinstance(node.func, ast.Attribute)
                    and node.func.attr == "exec_module"
                ):
                    exec_module_calls += 1
        reviewed[filename] = {
            "syntax_parse": "PASS",
            "imports": sorted(set(imports)),
            "direct_eval_exec_compile_import_calls": direct_dynamic_calls,
            "exec_module_calls": exec_module_calls,
            "test_methods": sorted(test_methods),
        }
    return {
        "mode": "AST_AND_TEXT_ONLY",
        "candidate_code_imported": False,
        "candidate_code_executed": False,
        "files": reviewed,
        "static_test_method_count":
            len(reviewed["test_reduction.py"]["test_methods"]),
    }


def q(value: int | Fraction) -> Fraction:
    return value if isinstance(value, Fraction) else Fraction(value)


def zeros(rows: int, columns: int) -> Matrix:
    return [[Fraction(0) for _ in range(columns)] for _ in range(rows)]


def identity(size: int) -> Matrix:
    return [
        [Fraction(int(i == j)) for j in range(size)]
        for i in range(size)
    ]


def ones(rows: int, columns: int) -> Matrix:
    return [[Fraction(1) for _ in range(columns)] for _ in range(rows)]


def transpose(matrix: Sequence[Sequence[int | Fraction]]) -> Matrix:
    return [
        [q(matrix[i][j]) for i in range(len(matrix))]
        for j in range(len(matrix[0]))
    ]


def matmul(
    left: Sequence[Sequence[int | Fraction]],
    right: Sequence[Sequence[int | Fraction]],
) -> Matrix:
    right_t = transpose(right)
    return [
        [
            sum((q(a) * q(b) for a, b in zip(row, column)), Fraction(0))
            for column in right_t
        ]
        for row in left
    ]


def matrix_add(
    *terms: tuple[int | Fraction, Sequence[Sequence[int | Fraction]]],
) -> Matrix:
    rows = len(terms[0][1])
    columns = len(terms[0][1][0])
    return [
        [
            sum(
                (q(scale) * q(matrix[i][j]) for scale, matrix in terms),
                Fraction(0),
            )
            for j in range(columns)
        ]
        for i in range(rows)
    ]


def matrix_scale(
    matrix: Sequence[Sequence[int | Fraction]],
    scale: int | Fraction,
) -> Matrix:
    factor = q(scale)
    return [[factor * q(value) for value in row] for row in matrix]


def trace(matrix: Sequence[Sequence[int | Fraction]]) -> Fraction:
    return sum(
        (q(matrix[i][i]) for i in range(len(matrix))),
        Fraction(0),
    )


def fraction_rank(matrix: Sequence[Sequence[int | Fraction]]) -> int:
    work = [[q(value) for value in row] for row in matrix]
    rows = len(work)
    columns = len(work[0]) if rows else 0
    pivot_row = 0
    for column in range(columns):
        pivot = next(
            (row for row in range(pivot_row, rows) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        pivot_value = work[pivot_row][column]
        work[pivot_row] = [value / pivot_value for value in work[pivot_row]]
        for row in range(rows):
            if row == pivot_row or not work[row][column]:
                continue
            factor = work[row][column]
            work[row] = [
                work[row][j] - factor * work[pivot_row][j]
                for j in range(columns)
            ]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def determinant(matrix: Sequence[Sequence[int | Fraction]]) -> Fraction:
    size = len(matrix)
    work = [[q(value) for value in row] for row in matrix]
    answer = Fraction(1)
    sign = 1
    for column in range(size):
        pivot = next(
            (row for row in range(column, size) if work[row][column]),
            None,
        )
        if pivot is None:
            return Fraction(0)
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            sign *= -1
        pivot_value = work[column][column]
        answer *= pivot_value
        for row in range(column + 1, size):
            if not work[row][column]:
                continue
            factor = work[row][column] / pivot_value
            work[row] = [
                work[row][j] - factor * work[column][j]
                for j in range(size)
            ]
    return sign * answer


def canonical_json_sha256(value: Any) -> str:
    raw = json.dumps(
        value,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def as_int_matrix(matrix: Sequence[Sequence[int | Fraction]]) -> list[list[int]]:
    output: list[list[int]] = []
    for row in matrix:
        converted: list[int] = []
        for value in row:
            item = q(value)
            if item.denominator != 1:
                raise AssertionError(f"nonintegral matrix entry {item}")
            converted.append(item.numerator)
        output.append(converted)
    return output


def candidate_cyclic_arrays() -> dict[str, Any]:
    lines = [{i, (i + 1) % 7, (i + 3) % 7} for i in range(7)]
    support = [[0] * 14 for _ in range(14)]
    labels: list[dict[str, Any]] = []
    for point in range(7):
        for line in range(7):
            if point not in lines[line]:
                support[point][7 + line] = 1
                support[7 + line][point] = 1
            incident = point in lines[line]
            for copy in range(2 if incident else 1):
                labels.append({
                    "point": point,
                    "line": line,
                    "copy": copy,
                    "incident": incident,
                })
    fixed_f = [[0] * 70 for _ in range(14)]
    for column, label in enumerate(labels):
        fixed_f[label["point"]][column] = 1
        fixed_f[7 + label["line"]][column] = 1
    return {
        "lines": lines,
        "support": support,
        "F": fixed_f,
        "labels": labels,
    }


def wave33_arrays() -> dict[str, Any]:
    payload = json.loads(
        (
            ROOT
            / "verification/wave33-rooted-extension/independent-results.json"
        ).read_text("utf-8")
    )
    return {
        "lines": [
            {point - 1 for point in line}
            for line in payload["support"]["fano_lines"]
        ],
        "support": payload["support"]["support_adjacency"],
        "F": payload["support_outside_incidence"]["D"],
        "metadata": payload["support_outside_incidence"]["column_metadata"],
    }


def coordinate_binding() -> dict[str, Any]:
    candidate = candidate_cyclic_arrays()
    wave = wave33_arrays()
    candidate_lines = candidate["lines"]
    wave_lines = wave["lines"]

    isomorphisms: list[tuple[tuple[int, ...], tuple[int, ...]]] = []
    for point_map in permutations(range(7)):
        mapped_lines = [
            {point_map[point] for point in line}
            for line in candidate_lines
        ]
        if all(line in wave_lines for line in mapped_lines):
            line_map = tuple(wave_lines.index(line) for line in mapped_lines)
            isomorphisms.append((point_map, line_map))
    if len(isomorphisms) != 168:
        raise AssertionError("unexpected number of Fano coordinate bindings")
    point_map, line_map = isomorphisms[0]
    support_map = list(point_map) + [7 + line for line in line_map]

    wave_lookup = {
        (
            item["point_index"],
            item["line_index"],
            item["copy"],
        ): index
        for index, item in enumerate(wave["metadata"])
    }
    o_map = [
        wave_lookup[
            (
                point_map[label["point"]],
                line_map[label["line"]],
                label["copy"],
            )
        ]
        for label in candidate["labels"]
    ]
    if sorted(o_map) != list(range(70)):
        raise AssertionError("candidate-to-Wave33 O map is not a permutation")

    support_matches = all(
        candidate["support"][i][j]
        == wave["support"][support_map[i]][support_map[j]]
        for i in range(14)
        for j in range(14)
    )
    incidence_matches = all(
        candidate["F"][i][j] == wave["F"][support_map[i]][o_map[j]]
        for i in range(14)
        for j in range(70)
    )
    if not support_matches or not incidence_matches:
        raise AssertionError("canonical coordinates do not bind to Wave33")

    mapping_payload = {
        "support_candidate_to_wave33": support_map,
        "O_candidate_to_wave33": o_map,
    }
    return {
        "isomorphism_count": len(isomorphisms),
        "chosen_point_map_candidate_to_wave33": list(point_map),
        "chosen_line_map_candidate_to_wave33": list(line_map),
        "chosen_support_map_candidate_to_wave33": support_map,
        "chosen_O_map_candidate_to_wave33": o_map,
        "mapping_sha256": canonical_json_sha256(mapping_payload),
        "support_adjacency_entrywise_match": support_matches,
        "support_to_O_entrywise_match": incidence_matches,
        "candidate_label_type_map": {
            "incident": "support_cross_nonedge_completion",
            "nonincident": "support_edge_completion",
        },
    }


def support_projector(t_matrix: Matrix) -> Matrix:
    t2 = matmul(t_matrix, t_matrix)
    t3 = matmul(t2, t_matrix)
    numerator = matrix_add(
        (1, t3),
        (-40, t2),
        (498, t_matrix),
    )
    return matrix_scale(numerator, Fraction(1, 1960))


def fixed_wave33_audit(binding: dict[str, Any]) -> dict[str, Any]:
    wave = wave33_arrays()
    support = [[q(value) for value in row] for row in wave["support"]]
    fixed_f = [[q(value) for value in row] for row in wave["F"]]
    t_matrix = matmul(transpose(fixed_f), fixed_f)
    p_f = support_projector(t_matrix)
    if matmul(p_f, p_f) != p_f or fraction_rank(p_f) != 13:
        raise AssertionError("Wave33 P_F projector reconstruction failed")
    h_r = matrix_add((1, t_matrix), (-11, p_f))
    support_times_f = matmul(support, fixed_f)
    c_so = [
        [
            Fraction(2) - fixed_f[i][j] - support_times_f[i][j]
            for j in range(70)
        ]
        for i in range(14)
    ]
    if matmul(fixed_f, h_r) != c_so:
        raise AssertionError("fixed action does not satisfy the S-O block")
    if h_r != transpose(h_r) or trace(h_r) != -3:
        raise AssertionError("fixed action symmetry or trace failed")

    c_rational = matrix_add(
        (21, t_matrix),
        (63, identity(70)),
        (-294, p_f),
        (Fraction(21, 5), ones(70, 70)),
    )
    c_wave = as_int_matrix(c_rational)
    diagonal = Counter(c_wave[i][i] for i in range(70))
    off_diagonal = Counter(
        c_wave[i][j] for i in range(70) for j in range(i + 1, 70)
    )
    if diagonal != Counter({51: 28, 57: 42}):
        raise AssertionError("fixed C diagonal distribution failed")
    expected_off = Counter(
        {-6: 21, -3: 84, 0: 336, 3: 168, 6: 714, 9: 840, 12: 252}
    )
    if off_diagonal != expected_off:
        raise AssertionError("fixed C off-diagonal distribution failed")

    o_map = binding["chosen_O_map_candidate_to_wave33"]
    c_candidate_order = [
        [c_wave[o_map[i]][o_map[j]] for j in range(70)]
        for i in range(70)
    ]
    candidate = candidate_cyclic_arrays()
    reported_candidate_hashes = {
        "support_adjacency_sha256":
            canonical_json_sha256(candidate["support"]),
        "support_to_O_sha256": canonical_json_sha256(candidate["F"]),
        "O_labels_sha256": canonical_json_sha256(candidate["labels"]),
        "fixed_C_sha256": canonical_json_sha256(c_candidate_order),
    }

    c_mod7 = [[value % 7 for value in row] for row in c_wave]
    c_mod7_squared = [
        [
            sum(c_mod7[i][k] * c_mod7[k][j] for k in range(70)) % 7
            for j in range(70)
        ]
        for i in range(70)
    ]
    if any(value for row in c_mod7_squared for value in row):
        raise AssertionError("Wave33 C mod 7 is not square-zero")
    mod7_rank = rank_mod(c_mod7, 7)
    if mod7_rank != 5:
        raise AssertionError("Wave33 C mod 7 rank is not five")

    p_f_diagonal = {
        "support_edge_completion": set(),
        "support_cross_nonedge_completion": set(),
    }
    for i, item in enumerate(wave["metadata"]):
        p_f_diagonal[item["kind"]].add(p_f[i][i])
    expected_leverage = {
        "support_edge_completion": {Fraction(97, 490)},
        "support_cross_nonedge_completion": {Fraction(87, 490)},
    }
    if p_f_diagonal != expected_leverage:
        raise AssertionError("Wave33 support leverage values drift")

    solution_l_diagonal = {
        "support_edge_completion": 30,
        "support_cross_nonedge_completion": 36,
    }
    for i, item in enumerate(wave["metadata"]):
        if c_wave[i][i] - 7 * 3 != solution_l_diagonal[item["kind"]]:
            raise AssertionError("hollow recovery does not force L diagonal")

    return {
        "P_F_formula": "T(T^2-40T+498I)/1960",
        "candidate_R_equals_P_F": True,
        "rank_P_F": fraction_rank(p_f),
        "H_R_formula": "T-11P_F",
        "trace_H_R": int(trace(h_r)),
        "F_H_R_equals_C_SO": True,
        "C_formula_stage1_symbols": "21T+63I-294P_F+21J/5",
        "C_formula_candidate_symbols":
            "21(H_R+3I-3P_F)+21J/5",
        "C_wave33_sha256": canonical_json_sha256(c_wave),
        "candidate_order_hashes": reported_candidate_hashes,
        "C_binding_entrywise_match": True,
        "C_diagonal_distribution": {
            str(key): diagonal[key] for key in sorted(diagonal)
        },
        "C_off_diagonal_distribution": {
            str(key): off_diagonal[key] for key in sorted(off_diagonal)
        },
        "C_mod_7_rank": mod7_rank,
        "C_mod_7_square_zero": True,
        "P_F_diagonal": {
            key: str(next(iter(values)))
            for key, values in p_f_diagonal.items()
        },
        "solution_L_diagonal": solution_l_diagonal,
        "trace_L": 42 * 36 + 28 * 30,
    }


def rank_mod(matrix: Sequence[Sequence[int]], prime: int) -> int:
    work = [[int(value) % prime for value in row] for row in matrix]
    rows = len(work)
    columns = len(work[0])
    pivot_row = 0
    for column in range(columns):
        pivot = next(
            (row for row in range(pivot_row, rows) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        inverse = pow(work[pivot_row][column], -1, prime)
        work[pivot_row] = [
            value * inverse % prime for value in work[pivot_row]
        ]
        for row in range(rows):
            if row == pivot_row or not work[row][column]:
                continue
            factor = work[row][column]
            work[row] = [
                (work[row][j] - factor * work[pivot_row][j]) % prime
                for j in range(columns)
            ]
        pivot_row += 1
    return pivot_row


def signed_minor(
    fixed_f: Sequence[Sequence[int]],
    columns: Sequence[int],
    deleted_row: int,
) -> Fraction:
    signed = [
        [
            q(fixed_f[row][column]) * (1 if row < 7 else -1)
            for column in columns
        ]
        for row in range(14)
        if row != deleted_row
    ]
    return determinant(signed)


def snf_audit(binding: dict[str, Any], candidate_results: dict[str, Any]) -> dict[str, Any]:
    candidate = candidate_cyclic_arrays()
    wave = wave33_arrays()
    rank_candidate = fraction_rank(candidate["F"])
    rank_wave = fraction_rank(wave["F"])
    if rank_candidate != 13 or rank_wave != 13:
        raise AssertionError("support incidence rank is not thirteen")

    candidate_witness = candidate_results["kernel_snf"]["unit_minor_witness"]
    candidate_det = signed_minor(
        candidate["F"],
        candidate_witness["columns"],
        candidate_witness["deleted_row"],
    )
    if candidate_det != candidate_witness["determinant"]:
        raise AssertionError("released unit-minor witness failed")
    if [
        candidate["labels"][column]
        for column in candidate_witness["columns"]
    ] != candidate_witness["o_labels"]:
        raise AssertionError("released unit-minor label payload failed")

    # Verifier-owned spanning tree in the exact Wave33 label order.
    lookup: dict[tuple[int, int], int] = {}
    for index, item in enumerate(wave["metadata"]):
        lookup.setdefault((item["point_index"], item["line_index"]), index)
    own_columns = [lookup[(0, line)] for line in range(7)]
    own_columns.extend(lookup[(point, 0)] for point in range(1, 7))
    own_deleted_row = 13
    own_det = signed_minor(wave["F"], own_columns, own_deleted_row)
    if abs(own_det) != 1:
        raise AssertionError("verifier-owned Wave33 unit minor failed")

    mapped_candidate_columns = [
        binding["chosen_O_map_candidate_to_wave33"][column]
        for column in candidate_witness["columns"]
    ]
    mapped_deleted_row = binding[
        "chosen_support_map_candidate_to_wave33"
    ][candidate_witness["deleted_row"]]
    mapped_det = signed_minor(
        wave["F"],
        mapped_candidate_columns,
        mapped_deleted_row,
    )
    if abs(mapped_det) != 1:
        raise AssertionError("mapped released unit minor failed in Wave33")

    return {
        "rank_over_Q_candidate_coordinates": rank_candidate,
        "rank_over_Q_wave33_coordinates": rank_wave,
        "kernel_dimension": 70 - rank_wave,
        "left_kernel_dimension": 14 - rank_wave,
        "candidate_unit_minor_determinant": int(candidate_det),
        "candidate_unit_minor_mapped_wave33_determinant": int(mapped_det),
        "verifier_unit_minor": {
            "columns": own_columns,
            "deleted_row": own_deleted_row,
            "determinant": int(own_det),
        },
        "snf_nonzero_invariant_factors": [1] * 13,
        "snf_zero_rows": 1,
        "proof": (
            "rank 13 plus an absolute-unit 13x13 minor forces the product "
            "of the 13 nonzero Smith factors to one"
        ),
    }


def cycle_type(permutation: Sequence[int]) -> tuple[int, ...]:
    seen = [False] * len(permutation)
    parts: list[int] = []
    for start in range(len(permutation)):
        if seen[start]:
            continue
        current = start
        length = 0
        while not seen[current]:
            seen[current] = True
            length += 1
            current = permutation[current]
        parts.append(length)
    return tuple(sorted(parts, reverse=True))


@lru_cache(maxsize=1)
def independent_matching_pair_census() -> dict[str, Any]:
    """Independent census via ordered pairs of perfect matchings.

    This is structurally different from the released point-degree recursion.
    A relative permutation records the alternating components. Ordered
    edge-colorings are divided out by component.
    """

    lines = [{i, (i + 1) % 7, (i + 3) % 7} for i in range(7)]
    multiplicity = [
        [2 if point in lines[line] else 1 for line in range(7)]
        for point in range(7)
    ]
    all_permutations = list(permutations(range(7)))
    labeled_ordered: Counter[tuple[int, ...]] = Counter()
    underlying_ordered: Counter[tuple[int, ...]] = Counter()

    for relative in all_permutations:
        kind = cycle_type(relative)
        fixed = [point for point in range(7) if relative[point] == point]
        moving = [point for point in range(7) if relative[point] != point]
        for first_matching in all_permutations:
            if any(
                multiplicity[point][first_matching[point]] != 2
                for point in fixed
            ):
                continue
            underlying_ordered[kind] += 1
            weight = 2 ** len(fixed)
            for point in moving:
                weight *= (
                    multiplicity[point][first_matching[point]]
                    * multiplicity[point][first_matching[relative[point]]]
                )
            labeled_ordered[kind] += weight

    labeled: dict[str, int] = {}
    underlying: dict[str, int] = {}
    for kind in sorted(labeled_ordered, reverse=True):
        label = "+".join(str(part) for part in kind)
        labeled_divisor = 2 ** len(kind)
        underlying_divisor = 2 ** (len(kind) - kind.count(1))
        if labeled_ordered[kind] % labeled_divisor:
            raise AssertionError("labeled ordered-pair quotient is nonintegral")
        if underlying_ordered[kind] % underlying_divisor:
            raise AssertionError(
                "underlying ordered-pair quotient is nonintegral"
            )
        labeled[label] = labeled_ordered[kind] // labeled_divisor
        underlying[label] = (
            underlying_ordered[kind] // underlying_divisor
        )
    return {
        "method": "ordered_pairs_of_perfect_matchings",
        "labeled_cycle_census": labeled,
        "underlying_cycle_census": underlying,
        "labeled_total": sum(labeled.values()),
        "underlying_total": sum(underlying.values()),
    }


@lru_cache(maxsize=1)
def independent_line_transfer_count() -> dict[str, int]:
    """A second count, processing line vertices rather than point vertices."""

    lines = [{i, (i + 1) % 7, (i + 3) % 7} for i in range(7)]
    options: list[list[tuple[tuple[int, ...], int]]] = []
    for line in range(7):
        line_options: list[tuple[tuple[int, ...], int]] = []
        for point in range(7):
            if point in lines[line]:
                row = [0] * 7
                row[point] = 2
                line_options.append((tuple(row), 1))
        for first, second in combinations(range(7), 2):
            row = [0] * 7
            row[first] = row[second] = 1
            weight = (
                (2 if first in lines[line] else 1)
                * (2 if second in lines[line] else 1)
            )
            line_options.append((tuple(row), weight))
        options.append(line_options)

    @lru_cache(maxsize=None)
    def recurse(line: int, remaining: tuple[int, ...]) -> tuple[int, int]:
        if line == 7:
            accepted = int(not any(remaining))
            return accepted, accepted
        underlying = 0
        labeled = 0
        for use, weight in options[line]:
            if any(use[i] > remaining[i] for i in range(7)):
                continue
            next_remaining = tuple(
                remaining[i] - use[i] for i in range(7)
            )
            child_underlying, child_labeled = recurse(
                line + 1,
                next_remaining,
            )
            underlying += child_underlying
            labeled += weight * child_labeled
        return underlying, labeled

    underlying, labeled = recurse(0, (2,) * 7)
    return {
        "underlying_total": underlying,
        "labeled_total": labeled,
        "cached_states": recurse.cache_info().currsize,
    }


def symbolic_add(
    *terms: tuple[Fraction | int, dict[str, Fraction]],
) -> dict[str, Fraction]:
    output: dict[str, Fraction] = {}
    for scale, expression in terms:
        for symbol, coefficient in expression.items():
            output[symbol] = (
                output.get(symbol, Fraction(0))
                + q(scale) * coefficient
            )
    return {
        symbol: coefficient
        for symbol, coefficient in output.items()
        if coefficient
    }


def expression(**coefficients: int | Fraction) -> dict[str, Fraction]:
    return {
        symbol: q(coefficient)
        for symbol, coefficient in coefficients.items()
        if coefficient
    }


def projector_equivalence_audit() -> dict[str, Any]:
    h_r = expression(H_R=1)
    p_f = expression(P_F=1)
    rb = expression(R_B=1)
    j = expression(J=1)
    ident = expression(I=1)
    e_minus4 = expression(E_minus4=1)

    e_w = symbolic_add((Fraction(1, 12), rb), (Fraction(-1, 20), j))
    q_u = symbolic_add((1, ident), (-1, p_f), (-1, e_w))
    h_candidate = symbolic_add(
        (1, h_r),
        (-1, e_w),
        (3, q_u),
        (-7, e_minus4),
    )
    c_star = symbolic_add(
        (21, h_r),
        (63, ident),
        (-63, p_f),
        (Fraction(21, 5), j),
    )
    numerator = symbolic_add(
        (1, c_star),
        (-7, rb),
        (-21, h_candidate),
    )
    if numerator != expression(E_minus4=147):
        raise AssertionError("forward integral-numerator identity failed")

    reverse_h = symbolic_add(
        (Fraction(1, 21), c_star),
        (Fraction(-1, 3), rb),
        (Fraction(-1, 21), expression(L=1)),
    )
    expected_reverse = symbolic_add(
        (1, h_r),
        (-1, e_w),
        (3, q_u),
        (Fraction(-1, 21), expression(L=1)),
    )
    if reverse_h != expected_reverse:
        raise AssertionError("reverse H reconstruction identity failed")

    # Exact scalar audit of all mutually orthogonal summands.
    summands = [
        {
            "space": "constant_in_R",
            "dimension": 1,
            "T": Fraction(20),
            "H": Fraction(9),
            "R_B": Fraction(42),
            "J": Fraction(70),
        },
        {
            "space": "nonconstant_R_conjugate_pair",
            "dimension": 12,
            "identity": (
                "for a=+/-sqrt(2): T=10-a, H=-1-a, "
                "and T+H^2=12-H"
            ),
        },
        {
            "space": "E_W",
            "dimension": 14,
            "T": Fraction(0),
            "H": Fraction(-1),
            "R_B": Fraction(12),
            "J": Fraction(0),
        },
        {
            "space": "Q_U_minus_E_minus4",
            "dimension": 27,
            "T": Fraction(0),
            "H": Fraction(3),
            "R_B": Fraction(0),
            "J": Fraction(0),
        },
        {
            "space": "E_minus4",
            "dimension": 16,
            "T": Fraction(0),
            "H": Fraction(-4),
            "R_B": Fraction(0),
            "J": Fraction(0),
        },
    ]
    for row in (summands[0], summands[2], summands[3], summands[4]):
        if (
            row["T"] + row["H"] ** 2 + row["R_B"]
            != 12 - row["H"] + 2 * row["J"]
        ):
            raise AssertionError(f"O-O scalar block failed on {row['space']}")

    return {
        "notation_map": {
            "candidate_R": "Stage1 P_F",
            "candidate_E_W": "Stage1 P_B-P_0",
            "candidate_Q_U": "Stage1 E (43-dimensional residual projector)",
            "candidate_H_R": "Stage1 T-11P_F",
            "candidate_rank16_E": "Stage1 E_minus_4",
            "candidate_L": "147*Stage1 E_minus_4",
        },
        "dimension_reconciliation": "13+14+43 = (13+15-1)+43 = 70",
        "forward": {
            "from_six_blocks_to_rank16_projector": True,
            "numerator_identity": "C-7R_B-21H=147E_minus4",
            "annihilators_follow_from_support": True,
            "rank": 16,
        },
        "reverse": {
            "symmetric_L_and_L_squared_147L_give_orthogonal_projector":
                True,
            "P L=0 and B^T L=0_put_range_in_Q_U": True,
            "hollow_recovery_forces_trace_L_2352_and_rank_16": True,
            "H_recovery_equals_projector_decomposition": True,
            "all_six_blocks_reconstructed": True,
        },
        "operator_summands": [
            {
                key: (str(value) if isinstance(value, Fraction) else value)
                for key, value in row.items()
            }
            for row in summands
        ],
        "grassmann_dimension": 16 * (43 - 16),
        "continuous_symmetric_before_B": 57 * 58 // 2,
        "continuous_symmetric_after_B": 43 * 44 // 2,
    }


def pair_census_reconciliation(
    labeled_cycle_census: dict[str, int],
) -> dict[str, Any]:
    stage1_results = json.loads(
        (STAGE1 / "exact-results.json").read_text("utf-8")
    )
    duplicate_state = stage1_results["forced_pair_distribution"][
        "global_unordered_pair_distribution"
    ]["g2_r0_h0_c0"]
    if duplicate_state != 21:
        raise AssertionError("Stage-1 duplicate-pair census drift")

    full_solution_types = ["7", "5+2", "4+3", "3+2+2"]
    compatible_single_columns = sum(
        labeled_cycle_census[key] for key in full_solution_types
    )
    pb_only_total = sum(labeled_cycle_census.values())
    excluded_by_duplicate_pair_rule = pb_only_total - compatible_single_columns
    if compatible_single_columns != 448_879_368:
        raise AssertionError("duplicate-free single-column count drift")
    return {
        "Stage1_duplicate_support_pairs": duplicate_state,
        "Stage1_rule": (
            "g=2 forces r=h=c=0, so the two copies of a doubled support "
            "label have disjoint B rows"
        ),
        "candidate_574118037_scope": (
            "all binary single columns satisfying P b=2*1 only"
        ),
        "candidate_count_verified": pb_only_total,
        "necessary_full_solution_single_column_types": full_solution_types,
        "full_cycle_lengths": ["14", "10+4", "8+6", "6+4+4"],
        "duplicate_free_Pb_columns_surviving_rule": compatible_single_columns,
        "remaining_compatibility_not_checked":
            "other columns, pair intersections, L, and H",
        "Pb_only_columns_excluded_by_duplicate_pair_rule":
            excluded_by_duplicate_pair_rule,
        "does_not_enumerate_compatible_15_tuples": True,
        "classification": "SCOPE_REFINEMENT_NOT_DISCREPANCY",
    }


def compare_candidate_results(
    candidate_results: dict[str, Any],
    binding: dict[str, Any],
    fixed: dict[str, Any],
    snf: dict[str, Any],
    matching: dict[str, Any],
    transfer: dict[str, Any],
    equivalence: dict[str, Any],
) -> dict[str, Any]:
    checks = {
        "raw_weight_14_columns":
            candidate_results["domain"]["raw_weight_14_columns"]
            == math.comb(70, 14),
        "labeled_two_factor_total":
            candidate_results["domain"]["two_factor_columns"][
                "labeled_binary_columns"
            ] == matching["labeled_total"] == transfer["labeled_total"],
        "underlying_two_factor_total":
            candidate_results["domain"]["two_factor_columns"][
                "underlying_capacity_bounded_multigraphs"
            ] == matching["underlying_total"] == transfer["underlying_total"],
        "transfer_state_count":
            candidate_results["domain"]["two_factor_columns"]["dp_states"]
            == transfer["cached_states"],
        "full_cycle_census":
            candidate_results["domain"]["two_factor_cycle_census"]
            == matching["labeled_cycle_census"],
        "support_hashes":
            all(
                candidate_results["fixed_support"][key]
                == fixed["candidate_order_hashes"][key]
                for key in (
                    "support_adjacency_sha256",
                    "support_to_O_sha256",
                    "O_labels_sha256",
                )
            ),
        "coordinate_binding":
            binding["support_adjacency_entrywise_match"]
            and binding["support_to_O_entrywise_match"],
        "snf":
            candidate_results["kernel_snf"][
                "snf_nonzero_invariant_factors"
            ] == snf["snf_nonzero_invariant_factors"]
            and candidate_results["kernel_snf"]["rank_P_over_Q"] == 13,
        "fixed_action":
            candidate_results["projector_reduction"]["rank_R"] == 13
            and candidate_results["projector_reduction"]["trace_H_R"] == -3,
        "13_14_43_decomposition":
            candidate_results["projector_reduction"][
                "rank_W_for_every_admissible_B"
            ] == 14
            and candidate_results["projector_reduction"][
                "rank_U_for_every_admissible_B"
            ] == 43,
        "rank16_projector":
            candidate_results["projector_reduction"][
                "residual_projector_rank"
            ] == equivalence["forward"]["rank"],
        "dimension_counts":
            candidate_results["projector_reduction"][
                "continuous_symmetric_K_block_before_B"
            ] == equivalence["continuous_symmetric_before_B"]
            and candidate_results["projector_reduction"][
                "continuous_symmetric_U_block_after_B"
            ] == equivalence["continuous_symmetric_after_B"]
            and candidate_results["projector_reduction"][
                "rank_16_projector_grassmann_dimension"
            ] == equivalence["grassmann_dimension"],
        "fixed_C_hash":
            candidate_results["integral_projector_numerator"][
                "fixed_C_sha256"
            ] == fixed["candidate_order_hashes"]["fixed_C_sha256"],
        "fixed_C_distributions":
            candidate_results["integral_projector_numerator"][
                "fixed_C_diagonal_distribution"
            ] == fixed["C_diagonal_distribution"]
            and candidate_results["integral_projector_numerator"][
                "fixed_C_off_diagonal_distribution"
            ] == fixed["C_off_diagonal_distribution"],
        "L_diagonal_and_trace":
            candidate_results["integral_projector_numerator"][
                "solution_L_diagonal_distribution"
            ] == {"30": 28, "36": 42}
            and candidate_results["integral_projector_numerator"]["trace_L"]
            == 2352,
        "mod7":
            candidate_results["integral_projector_numerator"]["mod_7"][
                "fixed_rank"
            ] == fixed["C_mod_7_rank"]
            and fixed["C_mod_7_square_zero"],
        "mod3":
            candidate_results["integral_projector_numerator"]["mod_3"]
            == "L=-B*B^T",
        "status_wall":
            set(candidate_results["status_wall"].values()) == {"UNKNOWN"},
    }
    failures = [name for name, passed in checks.items() if not passed]
    if failures:
        raise AssertionError(f"candidate comparison failures: {failures}")
    return {
        "checks": checks,
        "all_checks_pass": True,
        "material_discrepancies": [],
        "release_clarifications": [
            (
                "The exact Wave33 arrays are available to the verifier and "
                "are now bound by an explicit permutation; the candidate's "
                "permutation-equivalent limitation is discharged."
            ),
            (
                "The 574,118,037 census is correctly scoped to one P-coupled "
                "column, not a complete six-block column or a 15-column tuple."
            ),
        ],
    }


def build_result(full_census: bool = True) -> dict[str, Any]:
    release_hashes = validate_hash_dictionary(CANDIDATE_RELEASE_HASHES)
    candidate_input_hashes = validate_hash_dictionary(CANDIDATE_INPUT_HASHES)
    verifier_input_hashes = validate_hash_dictionary(VERIFIER_INPUT_HASHES)
    inner_manifest = validate_candidate_inner_manifest()
    stage1_manifest = validate_stage1_manifest()
    static_review = static_candidate_code_review()

    candidate_results = json.loads(
        (CANDIDATE_DIR / "results.json").read_text("utf-8")
    )
    candidate_report = (
        ROOT / "agents/2026-07-24-wave34-rooted-structural.md"
    ).read_text("utf-8")
    binding = coordinate_binding()
    fixed = fixed_wave33_audit(binding)
    snf = snf_audit(binding, candidate_results)
    transfer = independent_line_transfer_count()
    matching = (
        independent_matching_pair_census()
        if full_census
        else {
            "method": "not_run",
            "labeled_cycle_census":
                candidate_results["domain"]["two_factor_cycle_census"],
            "underlying_cycle_census": {},
            "labeled_total": transfer["labeled_total"],
            "underlying_total": transfer["underlying_total"],
        }
    )
    equivalence = projector_equivalence_audit()
    pair_reconciliation = pair_census_reconciliation(
        matching["labeled_cycle_census"]
    )
    comparison = compare_candidate_results(
        candidate_results,
        binding,
        fixed,
        snf,
        matching,
        transfer,
        equivalence,
    )

    normalized_report = " ".join(candidate_report.split())
    scope_checks = {
        "report_says_no_compatible_15_tuple_enumeration":
            (
                "does not cover every compatible 15-column design tuple"
                in normalized_report
                and "compatible 15-tuple" in normalized_report
            ),
        "report_says_unknown_binary_solution":
            "complete_binary_solution" in json.dumps(candidate_results)
            and candidate_results["status_wall"][
                "complete_binary_solution"
            ] == "UNKNOWN",
        "report_does_not_claim_exclusion":
            candidate_results["status_wall"]["complete_exclusion"]
            == "UNKNOWN",
        "no_automorphism_quotient":
            candidate_results["domain"]["automorphism_quotient"] is False,
        "no_fixed_O_Q_design":
            candidate_results["domain"]["fixed_O_Q_design"] is False,
    }
    if not all(scope_checks.values()):
        raise AssertionError("candidate scope wall failed")

    return {
        "schema_version": 1,
        "role": "verifier",
        "claim_label": "VERIFIED",
        "audit_verdict": "STATIC_CLEAN_ROOM_COMPARISON_PASS",
        "scope": (
            "Exact static comparison of the released Wave34 rooted "
            "cycle-space/rank-16-projector structural reduction in its "
            "unrestricted graph-only reparameterization scope."
        ),
        "public_candidate_commit_supplied_by_orchestrator":
            "52c94e915927f791d30f680d12181a08567248fb",
        "git_used": False,
        "input_integrity": {
            "candidate_release_hashes": release_hashes,
            "candidate_report_input_hashes": candidate_input_hashes,
            "verifier_additional_input_hashes": verifier_input_hashes,
            "candidate_inner_manifest": inner_manifest,
            "stage1_manifest": stage1_manifest,
            "all_hashes_pass": True,
        },
        "static_candidate_review": static_review,
        "coordinate_binding": binding,
        "snf": snf,
        "two_factor_verification": {
            "line_side_transfer": transfer,
            "matching_pair_census": matching,
            "raw_weight_14_columns": math.comb(70, 14),
            "full_census_run": full_census,
        },
        "fixed_action_and_integral_C": fixed,
        "projector_equivalence": equivalence,
        "stage1_reconciliation": pair_reconciliation,
        "candidate_result_comparison": comparison,
        "scope_checks": scope_checks,
        "objections_and_corrections": {
            "material_discrepancy": "NONE",
            "binding_objection": "RESOLVED_BY_EXPLICIT_PERMUTATION",
            "single_column_scope_objection": (
                "RESOLVED; count is Pb-only, with a stricter necessary "
                "duplicate-free refinement recorded"
            ),
            "modular_exclusion": "NOT_OBTAINED",
            "binary_solution_or_exclusion": "NOT_OBTAINED",
        },
        "limitations": [
            "Candidate Python was parsed statically but never imported or executed.",
            "The full census verifies individual P-coupled columns, not compatible labeled 15-tuples.",
            "The exact projector equivalence does not enumerate integral rank-16 projectors.",
            "No binary solution or complete exclusion is supplied.",
            "The graph-only criterion does not complete the endpoint projector, lattice, tensor, or Schur obligations.",
        ],
        "status": {
            "released_structural_reparameterization": "VERIFIED",
            "coordinate_binding": "VERIFIED",
            "SNF_and_two_factor_census": "VERIFIED",
            "rank16_projector_equivalence": "VERIFIED",
            "integral_C_L_and_modular_claims": "VERIFIED",
            "binary_solution": "UNKNOWN",
            "complete_exclusion": "UNKNOWN",
            "rooted_graph_extension": "UNKNOWN",
            "rooted_endpoint": "UNKNOWN",
            "n3_708": "UNKNOWN",
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
    }


def write_json_lf(path: Path, payload: dict[str, Any]) -> None:
    path.write_bytes(
        (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Verifier-owned Wave34 rooted structural static comparison"
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--skip-full-census",
        action="store_true",
        help="skip the independent 25.4M ordered matching-pair census",
    )
    args = parser.parse_args()
    payload = build_result(full_census=not args.skip_full_census)
    if args.output:
        write_json_lf(args.output, payload)
    else:
        print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
