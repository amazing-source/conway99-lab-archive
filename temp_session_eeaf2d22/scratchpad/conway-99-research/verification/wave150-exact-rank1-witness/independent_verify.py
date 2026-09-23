"""Independent exact verifier for the sealed Wave150 rational witness.

No Wave150 or Wave147 discovery Python is imported or executed.  Wave44 is
reconstructed through its clean-room verifier and Wave148 through the
precommitted clean-room row builder that was subsequently verified.  This
module independently rebuilds every Wave147 rooted coefficient matrix.
"""

from __future__ import annotations

import ctypes
import gzip
import hashlib
import importlib.util
import itertools
import json
import math
import sys
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from types import ModuleType
from typing import Iterable, Sequence


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DISCOVERY = ROOT / "attempts" / "wave150-order8-sdp-scout"
DISCOVERY_MANIFEST = DISCOVERY / "package-manifest.sha256"
WITNESS_PATH = DISCOVERY / "exact-rank1-witness.json"
SELECTION_PATH = DISCOVERY / "rank1-selection.json"
WAVE44_ROWS = ROOT / "attempts" / "wave44-rooted-flags" / "row-system.json"
WAVE147_GZIP = (
    ROOT / "attempts" / "wave147-alternative-lane" / "coefficients.json.gz"
)
WAVE148_GZIP = (
    ROOT / "attempts" / "wave148-marked-order8" / "marked-rows.json.gz"
)
WAVE44_VERIFIER = (
    ROOT / "verification" / "wave44-rooted-flags" / "independent_check.py"
)
WAVE148_CLEAN = (
    ROOT / "verification" / "wave148-marked-order8" / "clean_room_rows.py"
)
WAVE148_MANIFEST = (
    ROOT / "verification" / "wave148-marked-order8" / "package-manifest.sha256"
)
OUTPUT = HERE / "verification-results.json"

EXPECTED_DISCOVERY_MANIFEST_SHA256 = (
    "ae831ec52fbaf65b9ddc66dee77c4c076621d65a059ec3205e02a3b76bfafb1d"
)
EXPECTED_WITNESS_SHA256 = (
    "e63afbe9ca36b4b1571b3dde75309d0cce45f3bc862d6e8c08bfe62f78dc130d"
)
EXPECTED_WAVE44_ROWS_SHA256 = (
    "fb81601a9c97fc6860702403e56da65c2ba8fd69ee6a61007a0da53cade1d722"
)
EXPECTED_WAVE147_GZIP_SHA256 = (
    "a46d8a8b6fd3ae339cdf7c9b633a661d917e3481bed762ae6aa70f1b4886cf1e"
)
EXPECTED_WAVE147_PAYLOAD_SHA256 = (
    "a7402e77048090ea492c435190aadc1d32bd1df99276e612f6d199aec9e14b08"
)
EXPECTED_WAVE148_GZIP_SHA256 = (
    "e7a39699584fe60ff251119063d66d8eed2a14a69d671c183533806cddc92aa1"
)
EXPECTED_WAVE148_VERIFIER_MANIFEST_SHA256 = (
    "1d57ec93abd7cfd586fc5b5f24d669603f89349e7042a802e7425d536a8375a0"
)
EXPECTED_WAVE148_CLEAN_SHA256 = (
    "7af432dbbf0d7c1f727944dcc26b63f0e1a54ff52082819a8ddd0fc5beb4544a"
)

N, K, LAMBDA, MU = 99, 14, 1, 2
N3, H11, Y = 4158, 8316, 2079
MODULUS = 1_000_003
MIN_FREE_MEMORY_PERCENT = 20.0


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode(
        "ascii"
    )


def strict_json_bytes(raw: bytes, label: str) -> object:
    def reject_duplicates(pairs: list[tuple[str, object]]) -> dict:
        result = {}
        for key, value in pairs:
            require(key not in result, f"{label}: duplicate JSON key {key}")
            result[key] = value
        return result

    return json.loads(
        raw.decode("ascii"),
        object_pairs_hook=reject_duplicates,
        parse_constant=lambda token: (_ for _ in ()).throw(
            ValueError(f"{label}: nonfinite JSON number {token}")
        ),
    )


def strict_json(path: Path) -> object:
    return strict_json_bytes(path.read_bytes(), str(path))


def memory_status() -> dict[str, float]:
    class MemoryStatusEx(ctypes.Structure):
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

    status = MemoryStatusEx()
    status.dwLength = ctypes.sizeof(status)
    require(
        bool(ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status))),
        "GlobalMemoryStatusEx failed",
    )
    free_percent = 100.0 * status.ullAvailPhys / status.ullTotalPhys
    require(
        free_percent >= MIN_FREE_MEMORY_PERCENT,
        f"free memory {free_percent:.2f}% below verifier floor",
    )
    return {
        "free_percent": free_percent,
        "free_gib": status.ullAvailPhys / (1 << 30),
        "floor_percent": MIN_FREE_MEMORY_PERCENT,
    }


def verify_manifest(
    manifest: Path,
    expected_manifest_sha256: str,
) -> dict:
    actual_manifest_sha256 = sha256(manifest)
    failures = []
    rows = []
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, relative = line.split(maxsplit=1)
        relative = relative.strip().replace("\\", "/")
        candidate = (ROOT / relative).resolve()
        try:
            candidate.relative_to(ROOT.resolve())
        except ValueError:
            failures.append(f"path escape: {relative}")
            continue
        if not candidate.is_file():
            failures.append(f"missing: {relative}")
            continue
        actual = sha256(candidate)
        rows.append(
            {
                "path": relative,
                "expected_sha256": expected,
                "actual_sha256": actual,
                "pass": actual == expected,
            }
        )
        if actual != expected:
            failures.append(f"hash mismatch: {relative}")
    return {
        "manifest_sha256": actual_manifest_sha256,
        "expected_manifest_sha256": expected_manifest_sha256,
        "manifest_pass": actual_manifest_sha256
        == expected_manifest_sha256,
        "entry_count": len(rows),
        "entries_pass": not failures,
        "failures": failures,
    }


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@lru_cache(maxsize=None)
def edges(order: int) -> tuple[tuple[int, int], ...]:
    return tuple(
        (left, right)
        for left in range(order)
        for right in range(left + 1, order)
    )


@lru_cache(maxsize=None)
def edge_positions(order: int) -> dict[tuple[int, int], int]:
    return {edge: index for index, edge in enumerate(edges(order))}


def adjacency_rows(mask: int, order: int) -> tuple[int, ...]:
    rows = [0] * order
    for position, (left, right) in enumerate(edges(order)):
        if (mask >> position) & 1:
            rows[left] |= 1 << right
            rows[right] |= 1 << left
    return tuple(rows)


def transform_mask(
    mask: int, order: int, permutation: Sequence[int]
) -> int:
    positions = edge_positions(order)
    result = 0
    for position, (left, right) in enumerate(edges(order)):
        if not ((mask >> position) & 1):
            continue
        image = tuple(sorted((permutation[left], permutation[right])))
        result |= 1 << positions[image]
    return result


@lru_cache(maxsize=None)
def canonical_unrooted(mask: int, order: int) -> int:
    rows = adjacency_rows(mask, order)
    cells: dict[int, list[int]] = {}
    for vertex, row in enumerate(rows):
        cells.setdefault(row.bit_count(), []).append(vertex)
    start = 0
    choices = []
    for degree in sorted(cells):
        sources = cells[degree]
        targets = tuple(range(start, start + len(sources)))
        start += len(sources)
        choices.append(
            tuple(
                tuple(zip(sources, images))
                for images in itertools.permutations(targets)
            )
        )
    best = None
    for selected in itertools.product(*choices):
        permutation = [0] * order
        for cell in selected:
            for source, target in cell:
                permutation[source] = target
        candidate = transform_mask(mask, order, permutation)
        if best is None or candidate < best:
            best = candidate
    require(best is not None, "empty canonicalization")
    return best


def delete_vertex(mask: int, order: int, deleted: int) -> int:
    chosen = tuple(vertex for vertex in range(order) if vertex != deleted)
    positions = edge_positions(order)
    result = 0
    target_position = 0
    for left_index, left in enumerate(chosen):
        for right in chosen[left_index + 1 :]:
            if (mask >> positions[(left, right)]) & 1:
                result |= 1 << target_position
            target_position += 1
    return result


def locally_admissible(mask: int, order: int) -> bool:
    rows = adjacency_rows(mask, order)
    for left in range(order):
        if rows[left].bit_count() > K:
            return False
        for right in range(left + 1, order):
            common = (rows[left] & rows[right]).bit_count()
            if (rows[left] >> right) & 1:
                if common > LAMBDA:
                    return False
            elif common > MU:
                return False
    return True


def canonical_flag(mask: int) -> int:
    return min(
        transform_mask(mask, 5, (0, 1) + free)
        for free in itertools.permutations((2, 3, 4))
    )


def flag_basis(root_edge: bool) -> tuple[int, ...]:
    return tuple(
        sorted(
            {
                canonical_flag(mask)
                for mask in range(1 << math.comb(5, 2))
                if bool(mask & 1) == root_edge
                and locally_admissible(mask, 5)
            }
        )
    )


def induced_flag(
    mask: int,
    order: int,
    roots: tuple[int, int],
    free: tuple[int, int, int],
) -> int:
    chosen = roots + free
    positions = edge_positions(order)
    result = 0
    target_position = 0
    for left_index, left in enumerate(chosen):
        for right in chosen[left_index + 1 :]:
            if (mask >> positions[tuple(sorted((left, right)))]) & 1:
                result |= 1 << target_position
            target_position += 1
    return result


def root_embeddings(
    mask: int, order: int, root_edge: bool
) -> Iterable[tuple[int, int]]:
    rows = adjacency_rows(mask, order)
    for left in range(order):
        for right in range(order):
            if left != right and bool((rows[left] >> right) & 1) == root_edge:
                yield left, right


@lru_cache(maxsize=None)
def triple_pair_indices(
    remaining_size: int,
) -> tuple[
    tuple[tuple[int, int, int], ...],
    tuple[tuple[int, int], ...],
]:
    triples = tuple(itertools.combinations(range(remaining_size), 3))
    pairs = tuple(
        (first, second)
        for first, left in enumerate(triples)
        for second, right in enumerate(triples)
        if len(set(left).union(right)) == remaining_size
    )
    return triples, pairs


def coefficient_upper_entries(
    mask: int,
    order: int,
    root_edge: bool,
    flags: Sequence[int],
) -> list[list[int]]:
    index = {flag: position for position, flag in enumerate(flags)}
    matrix = [[0] * len(flags) for _ in flags]
    vertices = set(range(order))
    relative_triples, eligible_pairs = triple_pair_indices(order - 2)
    for roots in root_embeddings(mask, order, root_edge):
        remaining = tuple(sorted(vertices.difference(roots)))
        flag_indices = []
        for triple in relative_triples:
            free = tuple(remaining[position] for position in triple)
            flag = canonical_flag(induced_flag(mask, order, roots, free))
            require(flag in index, "induced flag left independent basis")
            flag_indices.append(index[flag])
        for first, second in eligible_pairs:
            matrix[flag_indices[first]][flag_indices[second]] += 1
    require(
        matrix == [list(row) for row in zip(*matrix)],
        "coefficient matrix is not symmetric",
    )
    return [
        [row, column, matrix[row][column]]
        for row in range(len(flags))
        for column in range(row, len(flags))
        if matrix[row][column]
    ]


def parse_fraction(value: object, label: str) -> Fraction:
    require(type(value) is str, f"{label}: rational must be a string")
    try:
        result = Fraction(value)
    except (ValueError, ZeroDivisionError) as error:
        raise AssertionError(f"{label}: invalid rational") from error
    require(str(result) == value, f"{label}: rational is not canonical")
    return result


def derive_lower_counts(
    counts: dict[int, Fraction],
    upper_order: int,
    lower_classes: Sequence[int],
) -> dict[int, Fraction]:
    translate = {
        canonical_unrooted(mask, upper_order - 1): mask
        for mask in lower_classes
    }
    require(len(translate) == len(lower_classes), "lower class collision")
    totals = {mask: Fraction(0) for mask in lower_classes}
    for mask, count in counts.items():
        if not count:
            continue
        for deleted in range(upper_order):
            card = canonical_unrooted(
                delete_vertex(mask, upper_order, deleted),
                upper_order - 1,
            )
            require(card in translate, "deleted card left class stream")
            totals[translate[card]] += count
    divisor = N - (upper_order - 1)
    return {mask: value / divisor for mask, value in totals.items()}


def wave44_reconstruction(
    witness_x7: dict[int, Fraction],
) -> tuple[dict, tuple[int, ...]]:
    require(sha256(WAVE44_ROWS) == EXPECTED_WAVE44_ROWS_SHA256, "Wave44 rows drift")
    clean = load_module("wave150_wave44_clean", WAVE44_VERIFIER)
    system = clean.assemble_system()
    published = strict_json(WAVE44_ROWS)
    require(published["classes"] == list(system["classes"]), "Wave44 classes")
    expected_families = {
        "base": {
            "rows": [list(row) for row in system["base_rows"]],
            "rhs": list(system["base_rhs"]),
        },
        "vertex": {
            "rows": [list(row) for row in system["vertex_rows"]],
            "rhs": list(system["vertex_rhs"]),
        },
        "edge": {
            "rows": [list(row) for row in system["edge_rows"]],
            "rhs": list(system["edge_rhs"]),
        },
        "nonedge": {
            "rows": [list(row) for row in system["nonedge_rows"]],
            "rhs": list(system["nonedge_rhs"]),
        },
    }
    require(published["families"] == expected_families, "Wave44 row rebuild")
    classes = tuple(int(mask) for mask in system["classes"])
    vector = tuple(
        int(witness_x7.get(mask, Fraction(0))) for mask in classes
    ) + (Y,)
    require(
        all(
            witness_x7.get(mask, Fraction(0)).denominator == 1
            for mask in classes
        ),
        "x7 is not integral",
    )
    residuals = clean.residuals(system["rows"], system["rhs"], vector)
    require(not any(residuals), "witness fails rebuilt Wave44 rows")
    return (
        {
            "classes": len(classes),
            "rows": len(system["rows"]),
            "family_rows": {
                "base": len(system["base_rows"]),
                "vertex": len(system["vertex_rows"]),
                "edge": len(system["edge_rows"]),
                "nonedge": len(system["nonedge_rows"]),
            },
            "all_coefficients_and_rhs_match_published": True,
            "all_witness_rows_pass": True,
            "maximum_absolute_residual": max(map(abs, residuals)),
            "y_h11_over_4": Y,
        },
        classes,
    )


def load_witness(
    classes7: Sequence[int] | None = None,
    classes8: Sequence[int] | None = None,
) -> tuple[dict, dict[int, Fraction], dict[int, Fraction]]:
    require(sha256(WITNESS_PATH) == EXPECTED_WITNESS_SHA256, "witness drift")
    witness = strict_json(WITNESS_PATH)
    require(
        witness["format"] == "wave150-exact-rank1-endpoint-witness-v1",
        "witness format",
    )
    require(
        witness["target"]
        == {"h11": H11, "n3": N3, "srg": [N, K, LAMBDA, MU]},
        "witness target",
    )
    x7 = {}
    for index, record in enumerate(witness["x7_support"]):
        require(
            isinstance(record, dict)
            and set(record) == {"canonical_mask", "count"},
            f"x7[{index}] shape",
        )
        mask, value = record["canonical_mask"], record["count"]
        require(
            type(mask) is int
            and type(value) is int
            and value > 0
            and mask not in x7,
            f"x7[{index}] value",
        )
        x7[mask] = Fraction(value)
    x8 = {}
    for index, record in enumerate(witness["x8_support"]):
        require(
            isinstance(record, dict)
            and set(record) == {"canonical_mask", "count"},
            f"x8[{index}] shape",
        )
        mask = record["canonical_mask"]
        value = parse_fraction(record["count"], f"x8[{index}]")
        require(
            type(mask) is int and value > 0 and mask not in x8,
            f"x8[{index}] value",
        )
        x8[mask] = value
    if classes7 is not None:
        require(set(x7) <= set(classes7), "unknown x7 mask")
        x7 = {mask: x7.get(mask, Fraction(0)) for mask in classes7}
    if classes8 is not None:
        require(set(x8) <= set(classes8), "unknown x8 mask")
        x8 = {mask: x8.get(mask, Fraction(0)) for mask in classes8}
    return witness, x7, x8


def wave147_reconstruction(
    counts_by_order: dict[int, dict[int, Fraction]],
) -> tuple[dict, dict, dict]:
    require(sha256(WAVE147_GZIP) == EXPECTED_WAVE147_GZIP_SHA256, "Wave147 gzip")
    compressed = WAVE147_GZIP.read_bytes()
    raw = gzip.decompress(compressed)
    require(
        hashlib.sha256(raw).hexdigest() == EXPECTED_WAVE147_PAYLOAD_SHA256,
        "Wave147 payload",
    )
    published = strict_json_bytes(raw, "Wave147 payload")
    require(canonical_bytes(published) == raw, "Wave147 noncanonical payload")

    family_records = {}
    streams = None
    flags_by_family = {
        "ordered_edge": flag_basis(True),
        "ordered_nonedge": flag_basis(False),
    }
    require(
        (len(flags_by_family["ordered_edge"]), len(flags_by_family["ordered_nonedge"]))
        == (66, 87),
        "flag basis sizes",
    )
    moment_data = {}
    total_matrix_records = 0
    total_upper_entries = 0
    for family, root_edge in (
        ("ordered_edge", True),
        ("ordered_nonedge", False),
    ):
        payload = published["families"][family]
        flags = flags_by_family[family]
        require(payload["matrix_size"] == len(flags), f"{family} matrix size")
        records = payload["class_coefficients"]
        by_order = {
            order: tuple(
                int(record["canonical_mask"])
                for record in records
                if int(record["order"]) == order
            )
            for order in range(5, 9)
        }
        require(
            tuple(len(by_order[order]) for order in range(5, 9))
            == (21, 62, 208, 916),
            f"{family} class dimensions",
        )
        if streams is None:
            streams = by_order
        else:
            require(streams == by_order, "family class streams differ")

        moment = [
            [Fraction(0) for _ in flags]
            for _ in flags
        ]
        first_moment = [Fraction(0) for _ in flags]
        order8_coefficients = {
            (row, column): {}
            for row in range(len(flags))
            for column in range(row, len(flags))
        }
        record_count = 0
        entry_count = 0
        for record in records:
            order = int(record["order"])
            mask = int(record["canonical_mask"])
            actual_entries = coefficient_upper_entries(
                mask, order, root_edge, flags
            )
            require(
                actual_entries == record["upper_entries"],
                f"Wave147 coefficient mismatch {family}/{order}/{mask}",
            )
            record_count += 1
            entry_count += len(actual_entries)
            count = counts_by_order[order][mask]
            for row, column, coefficient in actual_entries:
                value = count * coefficient
                moment[row][column] += value
                if row != column:
                    moment[column][row] += value
                if order == 5 and row == column:
                    first_moment[row] += value
                if order == 8:
                    order8_coefficients[(row, column)][mask] = coefficient
        family_records[family] = record_count
        total_matrix_records += record_count
        total_upper_entries += entry_count
        moment_data[family] = {
            "flags": flags,
            "moment": moment,
            "first_moment": first_moment,
            "order8_coefficients": order8_coefficients,
            "upper_entry_count": len(flags) * (len(flags) + 1) // 2,
        }
        memory_status()

    require(streams is not None, "missing class streams")
    require(
        (total_matrix_records, total_upper_entries) == (2414, 272054),
        "Wave147 full artifact dimensions",
    )
    return (
        {
            "class_stream_counts": {
                str(order): len(streams[order]) for order in range(5, 9)
            },
            "flag_basis_counts": {
                family: len(flags) for family, flags in flags_by_family.items()
            },
            "full_matrix_records_reconstructed": total_matrix_records,
            "all_matrix_records_exact_match": True,
            "nonzero_upper_entries_reconstructed": total_upper_entries,
            "gzip_sha256": sha256(WAVE147_GZIP),
            "payload_sha256": hashlib.sha256(raw).hexdigest(),
        },
        streams,
        moment_data,
    )


def wave148_reconstruction(
    classes7: Sequence[int],
    classes8: Sequence[int],
) -> tuple[dict, list[dict]]:
    require(
        sha256(WAVE148_MANIFEST)
        == EXPECTED_WAVE148_VERIFIER_MANIFEST_SHA256,
        "Wave148 verifier manifest drift",
    )
    require(sha256(WAVE148_CLEAN) == EXPECTED_WAVE148_CLEAN_SHA256, "Wave148 clean drift")
    clean = load_module("wave150_wave148_clean", WAVE148_CLEAN)
    published7, published8, _ = clean.published_streams()
    require(tuple(classes7) == tuple(published7), "Wave148 class7 stream")
    require(tuple(classes8) == tuple(published8), "Wave148 class8 stream")
    vertex_types, pair_types = clean.rooted_type_tables(classes7)
    vertex_coefficients, pair_coefficients, column_checks = (
        clean.coefficient_rows(classes8, vertex_types, pair_types)
    )

    equations = []
    expected_payload_rows = {"vertex_rows": [], "ordered_pair_rows": []}
    for index, key in enumerate(
        sorted(
            vertex_types,
            key=lambda rooted: (
                int(vertex_types[rooted]["source_mask"]),
                int(rooted),
            ),
        )
    ):
        record = vertex_types[key]
        lhs = int(record["multiplicity"]) * (
            K - int(record["degree"])
        )
        terms = {
            int(mask): int(coefficient)
            for mask, coefficient in vertex_coefficients[key].items()
        }
        label = f"V{index:04d}"
        equations.append(
            {
                "label": label,
                "source_mask": int(record["source_mask"]),
                "lhs_coefficient": lhs,
                "coefficients": terms,
            }
        )
        expected_payload_rows["vertex_rows"].append(
            {
                "row_id": label,
                "rooted_key": key,
                "order7_mask": int(record["source_mask"]),
                "orbit_multiplicity": int(record["multiplicity"]),
                "internal_degree": int(record["degree"]),
                "outside_neighbor_count": K - int(record["degree"]),
                "lhs_coefficient": lhs,
                "terms_order8_mask_coefficient": [
                    [mask, coefficient]
                    for mask, coefficient in sorted(terms.items())
                ],
            }
        )
    for index, key in enumerate(
        sorted(
            pair_types,
            key=lambda rooted: (
                int(pair_types[rooted]["source_mask"]),
                int(rooted),
            ),
        )
    ):
        record = pair_types[key]
        target = LAMBDA if record["adjacent"] else MU
        residual = target - int(record["common_inside"])
        lhs = int(record["multiplicity"]) * residual
        terms = {
            int(mask): int(coefficient)
            for mask, coefficient in pair_coefficients[key].items()
        }
        label = f"P{index:04d}"
        equations.append(
            {
                "label": label,
                "source_mask": int(record["source_mask"]),
                "lhs_coefficient": lhs,
                "coefficients": terms,
            }
        )
        expected_payload_rows["ordered_pair_rows"].append(
            {
                "row_id": label,
                "rooted_key": key,
                "order7_mask": int(record["source_mask"]),
                "orbit_multiplicity": int(record["multiplicity"]),
                "root_relation": "edge" if record["adjacent"] else "nonedge",
                "target_common_neighbors": target,
                "internal_common_neighbors": int(record["common_inside"]),
                "outside_common_neighbor_count": residual,
                "lhs_coefficient": lhs,
                "terms_order8_mask_coefficient": [
                    [mask, coefficient]
                    for mask, coefficient in sorted(terms.items())
                ],
            }
        )

    require(sha256(WAVE148_GZIP) == EXPECTED_WAVE148_GZIP_SHA256, "Wave148 gzip")
    actual = strict_json_bytes(
        gzip.decompress(WAVE148_GZIP.read_bytes()), "Wave148 rows"
    )
    for family in ("vertex_rows", "ordered_pair_rows"):
        require(
            actual[family] == expected_payload_rows[family],
            f"Wave148 full row mismatch: {family}",
        )
    require(
        all(
            row["vertex_total"] == row["expected_vertex_total"]
            and row["pair_total"] == row["expected_pair_total"]
            for row in column_checks.values()
        ),
        "Wave148 column controls",
    )
    return (
        {
            "vertex_rows": len(vertex_types),
            "ordered_pair_rows": len(pair_types),
            "total_rows": len(equations),
            "vertex_nonzero_terms": sum(
                len(row) for row in vertex_coefficients.values()
            ),
            "pair_nonzero_terms": sum(
                len(row) for row in pair_coefficients.values()
            ),
            "zero_rows": sum(
                row["lhs_coefficient"] == 0 and not row["coefficients"]
                for row in equations
            ),
            "all_rows_exact_match_verified_artifact": True,
            "column_classes_checked": len(column_checks),
            "all_column_identities_pass": True,
        },
        equations,
    )


def moment_equations(
    moment_data: dict,
    counts_by_order: dict[int, dict[int, Fraction]],
) -> tuple[dict, list[dict]]:
    equations = []
    summary = {}
    for family, root_count in (
        ("ordered_edge", N * K),
        ("ordered_nonedge", N * (N - 1 - K)),
    ):
        data = moment_data[family]
        first = data["first_moment"]
        moment = data["moment"]
        expected_first_sum = root_count * math.comb(N - 2, 3)
        expected_moment_sum = root_count * math.comb(N - 2, 3) ** 2
        require(sum(first) == expected_first_sum, f"{family} first sum")
        require(
            sum(sum(row) for row in moment) == expected_moment_sum,
            f"{family} moment sum",
        )
        failures = []
        for row in range(len(first)):
            for column in range(row, len(first)):
                residual = root_count * moment[row][column] - first[row] * first[column]
                if residual:
                    failures.append([row, column, str(residual)])
                upper_contribution = sum(
                    coefficient * counts_by_order[8][mask]
                    for mask, coefficient in data[
                        "order8_coefficients"
                    ][(row, column)].items()
                )
                # The full lower-order value is obtained by subtracting the
                # independently rebuilt order-eight contribution from the
                # independently rebuilt complete moment.
                lower = moment[row][column] - upper_contribution
                equations.append(
                    {
                        "label": f"M:{family}:{row}:{column}",
                        "coefficients": {
                            mask: root_count * coefficient
                            for mask, coefficient in data[
                                "order8_coefficients"
                            ][(row, column)].items()
                        },
                        "rhs": first[row] * first[column]
                        - root_count * lower,
                    }
                )
        require(not failures, f"{family} centered covariance nonzero")
        summary[family] = {
            "size": len(first),
            "root_embeddings": root_count,
            "upper_entries": len(first) * (len(first) + 1) // 2,
            "first_moment_nonzero_entries": sum(bool(value) for value in first),
            "first_moment_sum": int(sum(first)),
            "expected_first_moment_sum": expected_first_sum,
            "moment_sum": int(sum(sum(row) for row in moment)),
            "expected_moment_sum": expected_moment_sum,
            "all_centered_entries_exactly_zero": True,
            "maximum_absolute_centered_residual": 0,
        }
    return summary, equations


def deletion_equations(
    classes7: Sequence[int],
    classes8: Sequence[int],
) -> list[dict]:
    translate = {
        canonical_unrooted(mask, 7): mask for mask in classes7
    }
    rows = {mask: {} for mask in classes7}
    for mask8 in classes8:
        for deleted in range(8):
            card = canonical_unrooted(delete_vertex(mask8, 8, deleted), 7)
            require(card in translate, "deletion left class stream")
            mask7 = translate[card]
            rows[mask7][mask8] = rows[mask7].get(mask8, 0) + 1
    require(
        all(
            sum(rows[mask7].get(mask8, 0) for mask7 in classes7) == 8
            for mask8 in classes8
        ),
        "deletion column totals",
    )
    return [
        {
            "label": f"D:{mask7}",
            "coefficients": rows[mask7],
            "source_mask": mask7,
            "lhs_coefficient": N - 7,
        }
        for mask7 in classes7
    ]


def evaluate_equation(
    equation: dict,
    x8: dict[int, Fraction],
) -> Fraction:
    return sum(
        Fraction(coefficient) * x8[mask]
        for mask, coefficient in equation["coefficients"].items()
    ) - Fraction(equation["rhs"])


def modular_rank(
    rows: Sequence[dict],
    support_masks: Sequence[int],
    prime: int,
) -> tuple[int, int, list[int], list[str]]:
    column = {mask: index for index, mask in enumerate(support_masks)}
    basis: dict[int, list[int]] = {}
    selected_indices = []
    selected_labels = []
    scanned = 0
    for row_index, row in enumerate(rows):
        scanned += 1
        vector = [0] * len(support_masks)
        for mask, coefficient in row["coefficients"].items():
            if mask in column:
                vector[column[mask]] = int(coefficient) % prime
        for pivot in sorted(basis):
            if vector[pivot]:
                factor = vector[pivot]
                pivot_row = basis[pivot]
                vector = [
                    (left - factor * right) % prime
                    for left, right in zip(vector, pivot_row)
                ]
        pivot = next(
            (index for index, value in enumerate(vector) if value),
            None,
        )
        if pivot is not None:
            inverse = pow(vector[pivot], -1, prime)
            vector = [(value * inverse) % prime for value in vector]
            basis[pivot] = vector
            selected_indices.append(row_index)
            selected_labels.append(row["label"])
            if len(basis) == len(support_masks):
                break
    return len(basis), scanned, selected_indices, selected_labels


def build_results() -> dict:
    memory_before = memory_status()
    discovery_manifest = verify_manifest(
        DISCOVERY_MANIFEST, EXPECTED_DISCOVERY_MANIFEST_SHA256
    )
    require(
        discovery_manifest["manifest_pass"]
        and discovery_manifest["entries_pass"]
        and discovery_manifest["entry_count"] == 30,
        "Wave150 manifest freeze",
    )

    initial_witness, sparse_x7, sparse_x8 = load_witness()
    wave44, classes7 = wave44_reconstruction(sparse_x7)
    witness, x7, _ = load_witness(classes7=classes7)

    # The Wave147 streams are read only after their frozen hashes are checked.
    compressed = WAVE147_GZIP.read_bytes()
    raw147 = gzip.decompress(compressed)
    require(
        hashlib.sha256(raw147).hexdigest() == EXPECTED_WAVE147_PAYLOAD_SHA256,
        "Wave147 pre-load hash",
    )
    artifact147 = strict_json_bytes(raw147, "Wave147 pre-load")
    records = artifact147["families"]["ordered_edge"]["class_coefficients"]
    provisional_streams = {
        order: tuple(
            int(record["canonical_mask"])
            for record in records
            if int(record["order"]) == order
        )
        for order in range(5, 9)
    }
    require(tuple(classes7) == provisional_streams[7], "Wave44/Wave147 class7")
    witness, x7, x8 = load_witness(
        classes7=classes7, classes8=provisional_streams[8]
    )

    counts_by_order = {
        7: x7,
        8: x8,
    }
    counts_by_order[6] = derive_lower_counts(
        counts_by_order[7], 7, provisional_streams[6]
    )
    counts_by_order[5] = derive_lower_counts(
        counts_by_order[6], 6, provisional_streams[5]
    )
    for order in range(5, 9):
        require(
            sum(counts_by_order[order].values()) == math.comb(N, order),
            f"order-{order} total count",
        )
        require(
            all(value >= 0 for value in counts_by_order[order].values()),
            f"order-{order} nonnegativity",
        )

    wave147, streams, moment_data = wave147_reconstruction(counts_by_order)
    require(streams == provisional_streams, "Wave147 stream rebuild")
    wave148, marked = wave148_reconstruction(classes7, streams[8])
    deletion = deletion_equations(classes7, streams[8])
    centered, moments = moment_equations(moment_data, counts_by_order)

    equations = [
        {
            "label": "sum_x8",
            "coefficients": {mask: 1 for mask in streams[8]},
            "rhs": math.comb(N, 8),
        }
    ]
    for row in deletion:
        equations.append(
            {
                "label": row["label"],
                "coefficients": row["coefficients"],
                "rhs": row["lhs_coefficient"] * x7[row["source_mask"]],
            }
        )
    for row in marked:
        equations.append(
            {
                "label": row["label"],
                "coefficients": row["coefficients"],
                "rhs": row["lhs_coefficient"] * x7[row["source_mask"]],
            }
        )
    equations.extend(moments)
    nontrivial = [
        row
        for row in equations
        if row["coefficients"] or Fraction(row["rhs"]) != 0
    ]
    require(len(nontrivial) == 10310, "full nontrivial row count")
    residuals = [evaluate_equation(row, x8) for row in nontrivial]
    require(not any(residuals), "exact witness row replay failed")

    selection = strict_json(SELECTION_PATH)
    embedded_selection = dict(witness["selection"])
    standalone_selection = dict(selection)
    embedded_elapsed = embedded_selection.pop("elapsed_seconds")
    standalone_elapsed = standalone_selection.pop("elapsed_seconds")
    require(
        embedded_selection == standalone_selection,
        "embedded selection differs in mathematical content",
    )
    require(
        type(embedded_elapsed) is float
        and embedded_elapsed > 0
        and type(standalone_elapsed) is float
        and standalone_elapsed > 0,
        "selection elapsed-time metadata",
    )
    support_indices = selection["support"]
    support_masks = tuple(streams[8][index] for index in support_indices)
    positive_masks = tuple(mask for mask in streams[8] if x8[mask] > 0)
    require(support_masks == positive_masks, "selection/witness support")
    restricted = []
    for row in nontrivial:
        coefficients = {
            mask: coefficient
            for mask, coefficient in row["coefficients"].items()
            if mask in set(support_masks)
        }
        if coefficients or Fraction(row["rhs"]) != 0:
            require(coefficients, f"restricted contradiction: {row['label']}")
            restricted.append(
                {
                    "label": row["label"],
                    "coefficients": coefficients,
                    "rhs": row["rhs"],
                }
            )
    require(len(restricted) == 10259, "restricted row count")
    rank, scanned, selected_indices, selected_labels = modular_rank(
        restricted, support_masks, MODULUS
    )
    require(
        (rank, scanned) == (874, 1931),
        "independent modular scan dimensions",
    )
    require(
        selected_indices == selection["selected_row_indices"],
        "selected modular row indices differ",
    )
    require(
        selected_labels == selection["selected_row_labels"],
        "selected modular row labels differ",
    )
    selected_rows = [restricted[index] for index in selected_indices]
    selected_rank, selected_scanned, _, _ = modular_rank(
        selected_rows, support_masks, MODULUS
    )
    require(
        (selected_rank, selected_scanned) == (874, 874),
        "stored modular subsystem not full rank",
    )

    x8_denominators = Counter(
        value.denominator for value in x8.values() if value
    )
    require(
        x8_denominators == Counter({1: 865, 2: 5, 4: 4}),
        "x8 denominator distribution",
    )
    require(sum(bool(value) for value in x7.values()) == 204, "x7 support")
    require(sum(bool(value) for value in x8.values()) == 874, "x8 support")

    # These two immutable diagnostic logs use Python's nonstandard Infinity
    # token for an unbounded floating objective.  They are chronology records,
    # not exact certificates; exact artifacts above remain strict JSON.
    false_bound = json.loads(
        (DISCOVERY / "marked-rank1-highs.json").read_text(encoding="ascii")
    )
    explicit = json.loads(
        (
            DISCOVERY / "marked-rank1-both-highs-explicit.json"
        ).read_text(encoding="ascii")
    )
    require(
        false_bound["solver"]["status"] == "infeasible"
        and not false_bound["candidate"]["candidate_available"],
        "initial false-infeasibility record",
    )
    require(
        explicit["solver"]["status"] == "optimal"
        and explicit["candidate"]["candidate_available"],
        "explicit-inequality recovery record",
    )
    memory_after = memory_status()
    return {
        "format": "wave150-independent-exact-rank1-witness-v1",
        "claim_label": "VERIFIED",
        "scope": (
            "exact rational feasibility of the frozen Wave44+Wave147+Wave148 "
            "order-eight count relaxation on both zero-centered-covariance faces"
        ),
        "chronology": {
            "sealed_discovery_manifest": discovery_manifest,
            "discovery_code_imported_or_executed": False,
            "false_infeasibility_retained": {
                "initial_bound_encoding_status": "infeasible",
                "explicit_inequality_encoding_status": "optimal",
                "exact_witness_refutes_infeasibility_for_the_exact_system": True,
                "solver_exit_code_used_as_certificate": False,
            },
        },
        "memory": {
            "floor_percent": MIN_FREE_MEMORY_PERCENT,
            "before": memory_before,
            "after": memory_after,
        },
        "witness": {
            "sha256": sha256(WITNESS_PATH),
            "target": witness["target"],
            "x7_support": sum(bool(value) for value in x7.values()),
            "x8_support": sum(bool(value) for value in x8.values()),
            "x7_total": int(sum(x7.values())),
            "x8_total": str(sum(x8.values())),
            "all_counts_nonnegative": True,
            "x7_all_integral": all(
                value.denominator == 1 for value in x7.values()
            ),
            "x8_denominator_distribution": {
                str(key): value for key, value in sorted(x8_denominators.items())
            },
            "x8_maximum_denominator": max(x8_denominators),
        },
        "lower_counts": {
            str(order): {
                "support": sum(
                    bool(value) for value in counts_by_order[order].values()
                ),
                "total": str(sum(counts_by_order[order].values())),
                "all_integral": all(
                    value.denominator == 1
                    for value in counts_by_order[order].values()
                ),
                "all_nonnegative": True,
            }
            for order in (5, 6)
        },
        "wave44": wave44,
        "wave147": wave147,
        "wave148": wave148,
        "centered_covariance": centered,
        "full_equation_replay": {
            "equations_before_trivial_removal": len(equations),
            "nontrivial_equations": len(nontrivial),
            "restricted_nontrivial_equations": len(restricted),
            "ordinary_deletion_rows": len(deletion),
            "marked_rows_seen": len(marked),
            "moment_upper_entries": {
                family: row["upper_entries"]
                for family, row in centered.items()
            },
            "all_10310_rows_pass_exactly": True,
            "maximum_absolute_rational_residual": "0",
        },
        "modular_selection": {
            "modulus": MODULUS,
            "variables": len(support_masks),
            "rank": rank,
            "full_column_rank": True,
            "restricted_rows": len(restricted),
            "rows_scanned_to_full_rank": scanned,
            "selected_rows": len(selected_indices),
            "stored_selected_indices_exact_match": True,
            "stored_selected_labels_exact_match": True,
            "stored_874_by_874_subsystem_rank": selected_rank,
            "embedded_and_standalone_selection_exact_match_except_elapsed_time": True,
        },
        "verdict": {
            "witness_integrity_and_rational_shape": "PASS",
            "Wave44_170_rows": "PASS",
            "Wave147_all_2414_matrices": "PASS",
            "Wave148_all_5384_rows": "PASS",
            "ordinary_and_marked_row_replay": "PASS",
            "both_centered_covariance_blocks": "PASS",
            "all_10310_full_system_rows": "PASS",
            "modular_full_rank_selection": "PASS",
            "finite_relaxation_at_n3_4158": "EXACT_RATIONAL_FEASIBLE",
            "overall": "PASS_WITH_SCOPE",
        },
        "status_wall": {
            "exact_count_vector_is_a_graph": False,
            "higher_order_overlap_consistency": "NOT_REPRESENTED",
            "endpoint_n3_4158_graph_existence": "UNKNOWN",
            "strict_upper_bound_below_4158": "NOT_PROVED",
            "Conway_99": "UNKNOWN",
            "external_novelty": "UNKNOWN",
        },
    }


def main() -> None:
    payload = build_results()
    OUTPUT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print("Wave150 independent exact-witness audit: PASS_WITH_SCOPE")


if __name__ == "__main__":
    main()
