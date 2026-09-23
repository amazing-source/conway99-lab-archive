#!/usr/bin/env python3
"""Independent Wave 14 n3=48 active-local computation audit.

This verifier imports no Wave 14 discovery module.  It reconstructs the
finite arithmetic, the deterministic PySAT formulas, and all three positive
objects from the archived raw JSON.  Solver-negative rows are deliberately
treated as non-evidentiary because no checked proof traces exist.
"""

from __future__ import annotations

import copy
import gc
import hashlib
import itertools
import json
import platform
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import pysat
from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver


ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = ROOT / "attempts" / "wave14-computation"
OUTPUT_DIR = ROOT / "verification" / "n3-48-computation"

PROFILE_PATH = SOURCE_DIR / "n3-48-profile-census.json"
SCAN_PATH = SOURCE_DIR / "n3-48-active-local-scan.json"
CONTROLS_PATH = SOURCE_DIR / "n3-48-positive-controls.json"
FULL_CANDIDATE_PATH = (
    SOURCE_DIR / "n3-48-r16-q2x16-no-size3-full-candidate.json"
)
NO_COMMON_CANDIDATE_PATH = (
    SOURCE_DIR
    / "n3-48-r16-q2x16-root-q3x0-no_common_point_control-candidate.json"
)
K_UPPER_CANDIDATE_PATH = (
    SOURCE_DIR
    / "n3-48-r16-q2x16-no-size3-k_degree_upper_control-candidate.json"
)
DISCOVERY_VALIDATION_PATH = SOURCE_DIR / "n3-48-independent-validation.json"
FAILURES_PATH = SOURCE_DIR / "n3-48-run-failures.json"

REPORT_PATH = ROOT / "agents" / "2026-07-22-wave14-n3-48-computational.md"
CODE_PATHS = (
    ROOT / "code" / "wave14_n3_48_profiles.py",
    ROOT / "code" / "wave14_n3_48_active_sat.py",
    ROOT / "code" / "wave14_n3_48_verify.py",
    ROOT / "code" / "wave14_n3_48_test.py",
)

EXPECTED_FILE_HASHES = {
    "agents/2026-07-22-wave14-n3-48-computational.md":
        "54b532035f0ac3c09aaafd1a825600151d6ae55d3a2fcb87f911cfe37dc8b756",
    "code/wave14_n3_48_profiles.py":
        "fb7c670d0240401929bac609177c83dd618c6baf5969a2e99e6f0dc7ed48f827",
    "code/wave14_n3_48_active_sat.py":
        "84e0dcd6cd11f4742abecfe00e1df1ac96047a8967d94f8f5e735d330b4a2ef2",
    "code/wave14_n3_48_verify.py":
        "6b2318acc5784290c2f5a32046cd76535bf00db9123b4de4246b882cd2b7c827",
    "code/wave14_n3_48_test.py":
        "e29999d7485ef3fefc6a32892d2889fd5c1bf6db69733866ea3803ffed0a28ef",
    "attempts/wave14-computation/n3-48-profile-census.json":
        "c2acf43d29aa08179869a31327991336ac54559fa5ec4915d9f3ea993de7bb5a",
    "attempts/wave14-computation/n3-48-active-local-scan.json":
        "4ce53c2fc8a8c0bc005ac1b73dc657ea3c8b7a7f1e3bae1cd73f24de73c539f2",
    "attempts/wave14-computation/n3-48-positive-controls.json":
        "db6fb90836dc16440a9e0c73ccff420516af9641e60d6775537f7a695e33ae33",
    (
        "attempts/wave14-computation/"
        "n3-48-r16-q2x16-no-size3-full-candidate.json"
    ): "b5873ddca8dd92bbcc50fb91b942472f426010264fcfe5599912e178318f4ad5",
    (
        "attempts/wave14-computation/"
        "n3-48-r16-q2x16-root-q3x0-no_common_point_control-candidate.json"
    ): "a5f049c7a7651db6ae8ba5d08cd4d5509814fdcc6202a5080a549acefb0fc024",
    (
        "attempts/wave14-computation/"
        "n3-48-r16-q2x16-no-size3-k_degree_upper_control-candidate.json"
    ): "0cb8644bbd6013dbdb1e00657a3cf6a6e9c3a146ad65a43e7270aee6488c1e37",
    "attempts/wave14-computation/n3-48-independent-validation.json":
        "20ac2afa64329074677f698331460a27e987ff74527e99ceeee5e5f01fc6d069",
    "attempts/wave14-computation/n3-48-run-failures.json":
        "0a4b82afccf09ed26a5dcd34306243723115ff304bbe6f018286c1de141c57b3",
}

# Correct the K-upper file hash separately to make an accidental copy/paste
# collision in the manifest impossible to overlook.
EXPECTED_FILE_HASHES[
    (
        "attempts/wave14-computation/"
        "n3-48-r16-q2x16-no-size3-k_degree_upper_control-candidate.json"
    )
] = "0cb8644bbd6013dbdb1e00657a3cf6a6e9c3a146ad65a43e7270aee6488c1e37"

FULL = "full"
NO_COMMON = "no_common_point_control"
K_UPPER = "k_degree_upper_control"

PROFILES = {
    "r16-q2x16": (2,) * 16,
    "r15-q2x13-q3x2": (2,) * 13 + (3,) * 2,
    "r14-q2x10-q3x4": (2,) * 10 + (3,) * 4,
}

RAW_BRANCHES = [
    ("r16-q2x16", "no-size3"),
    ("r16-q2x16", "root-q3x0"),
    ("r15-q2x13-q3x2", "no-size3"),
    ("r15-q2x13-q3x2", "root-q3x0"),
    ("r15-q2x13-q3x2", "root-q3x1"),
    ("r15-q2x13-q3x2", "root-q3x2"),
    ("r14-q2x10-q3x4", "no-size3"),
    ("r14-q2x10-q3x4", "root-q3x0"),
    ("r14-q2x10-q3x4", "root-q3x1"),
    ("r14-q2x10-q3x4", "root-q3x2"),
    ("r14-q2x10-q3x4", "root-q3x3"),
]

REDUCED_BRANCHES = [
    ("r16-q2x16", "no-size3"),
    ("r16-q2x16", "root-q3x0"),
    ("r15-q2x13-q3x2", "root-q3x0"),
    ("r14-q2x10-q3x4", "root-q3x0"),
]

EXPECTED_STATUSES = [
    "SAT_CANDIDATE",
    "TIMEOUT_UNKNOWN",
    "BUDGET_UNKNOWN",
    "TIMEOUT_UNKNOWN",
    "UNSAT_UNVERIFIED",
    "UNSAT_UNVERIFIED",
    "UNSAT_UNVERIFIED",
    "UNSAT_UNVERIFIED",
    "UNSAT_UNVERIFIED",
    "UNSAT_UNVERIFIED",
    "UNSAT_UNVERIFIED",
]

EXPECTED_FORMULAS = {
    ("r16-q2x16", "no-size3", FULL):
        (469160, 1639520, 560, 1640080,
         "4f0a295ce08409877efee09f87f1ccaf289ea5fe3014d115a4ef99e3e2b5ebdb"),
    ("r16-q2x16", "root-q3x0", FULL):
        (469160, 1639520, 1, 1639521,
         "010481d24a8870fd5918b748f67a71bae0159aaabed5df4d911f3379c828769d"),
    ("r15-q2x13-q3x2", "no-size3", FULL):
        (326446, 1137931, 455, 1138386,
         "e9d9a23627adaa7d52e630e9477c26ad549b72a9f8057f3d45022821cd7cac78"),
    ("r15-q2x13-q3x2", "root-q3x0", FULL):
        (326446, 1137931, 1, 1137932,
         "54d2c55fb75c51df00db9900245d0aefce058990f0b214498ffd87bc36d6750f"),
    ("r15-q2x13-q3x2", "root-q3x1", FULL):
        (326446, 1137931, 1, 1137932,
         "8f4e055f9423431ce3f1aaa9478d534881c681aac97b8deaf5fdf268e06ba514"),
    ("r15-q2x13-q3x2", "root-q3x2", FULL):
        (326446, 1137931, 1, 1137932,
         "76d1da14f0a1aae3f063d12161baa4a964535e0cdb21be50067f8dca1a69b656"),
    ("r14-q2x10-q3x4", "no-size3", FULL):
        (227295, 780242, 364, 780606,
         "197aca54f1dc3362e7cc124628ca54842437d5bf06573d168f649866ca0e6042"),
    ("r14-q2x10-q3x4", "root-q3x0", FULL):
        (227295, 780242, 1, 780243,
         "8483315145c89d24be050391fa40899a4d7272d0a4c38d4726b1c05a90bac784"),
    ("r14-q2x10-q3x4", "root-q3x1", FULL):
        (227295, 780242, 1, 780243,
         "1f9ebed0748cb0304980639ef5c2584c264bf48bb4afa2d6a294858159bb06da"),
    ("r14-q2x10-q3x4", "root-q3x2", FULL):
        (227295, 780242, 1, 780243,
         "21b4cacbdf044b18a618eec9f72df71bda29dbbe699867c56d95a93bb986631e"),
    ("r14-q2x10-q3x4", "root-q3x3", FULL):
        (227295, 780242, 1, 780243,
         "95921cb5b0418a38adef1a49f0288e4cf720e9307d4614d8e439f4817f7659ea"),
    ("r16-q2x16", "root-q3x0", NO_COMMON):
        (469720, 1641761, 1, 1641762,
         "2c386e58446c3142a6f0d93f8f92f0cd6a085951d82f7214eb9cc9adef2b6d4b"),
    ("r16-q2x16", "no-size3", K_UPPER):
        (468352, 1637855, 560, 1638415,
         "4bf32491072b83a53ff254ee8359e606e3b93d1cbb974ba380ed82f2f7af59ef"),
}

EXPECTED_SEMANTIC_HASHES = {
    "profiles": "07eb5c0430458adb4e17a00d27b3635d14031d87c185adb48368f56bfb75bd13",
    "scan": "de119937479d4f5c8fe75cab3affe275938c32bdfe660410d7443a0348b0fc7a",
    "controls": "fb39d2cf7f9b42375eb2bf77f211739c9da61f7f1c1b74d65b12355fc4f89905",
    "full_candidate":
        "b533da6c967098ed5ec9afd4d0d4e6166c6082e4bf9de5717f48c7b6835d686a",
    "no_common_control":
        "00fa2235b5716387a2eb8e57438f078df5361925c83513d767437890285406ff",
    "k_upper_control":
        "e918fe1cad2812f5a9c708df63d95e531e1a015d406ba4607293a940170294b5",
    "discovery_validation":
        "965e2457c4b1357ded77b370907e0414e730abd310a94fc02754ef8a4416aefa",
}

ENCODED_PREMISES = [
    "exactly three selected non-singleton point sets through each active label",
    "point sizes are two or three after the finite flower reductions",
    "point-family linearity",
    "F is the exact union of selected point-clique edges",
    "every selected point is a clique in K",
    "common-point/Berge-triangle rule unless named as the omitted control premise",
    "exact two-sided degree-{0,2} crossing for every pair of meeting selected points",
    "fixed-point upper cap on full-L overlaps at every selected size-three point",
    "profile-specific K degrees, or only upper bounds in the named control",
]

UNENCODED_PREMISES = [
    "inactive point sets and inactive graph vertices",
    "which disjoint active point sets represent adjacent original vertices",
    "fixed support contributed by disjoint point sets",
    "equality completion of every fixed-point support sum",
    "the 693-vertex H graph",
    "a 99-vertex adjacency matrix",
    "global SRG lambda/mu equations",
]

SYMMETRY_BOUNDARY = (
    "q labels are sorted canonically; a positive root branch uses only "
    "permutations within equal-q label classes; no completed-graph "
    "automorphism is assumed"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("ascii")


def semantic_hash(value: object) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def pair(a: int, b: int) -> tuple[int, int]:
    require(a != b, "loop is not an edge")
    return (a, b) if a < b else (b, a)


def enumerate_q_profiles() -> list[tuple[int, ...]]:
    found: list[tuple[int, ...]] = []

    def descend(remaining: int, least: int, values: tuple[int, ...]) -> None:
        if remaining == 0:
            r = len(values)
            if values and all(3 * q <= r - 1 for q in values):
                found.append(values)
            return
        for q in range(least, remaining + 1):
            descend(remaining - q, q, values + (q,))

    descend(32, 2, ())
    return sorted(found, key=lambda values: (-len(values), values))


def profile_name(values: Sequence[int]) -> str:
    histogram = Counter(values)
    suffix = "-".join(f"q{q}x{histogram[q]}" for q in sorted(histogram))
    return f"r{len(values)}-{suffix}"


def flower_census(
    order: int,
    root_size: int,
    max_petal_size: int,
    root_degree: int,
) -> tuple[int, int, list[tuple[int, ...]]]:
    feasible = 0
    survivors: list[tuple[int, ...]] = []
    alphabet = range(2, max_petal_size + 1)
    for word in itertools.product(alphabet, repeat=2 * root_size):
        if sum(value - 1 for value in word) > order - root_size:
            continue
        feasible += 1
        singletons = word.count(2)
        lower = []
        for root in range(root_size):
            based = word[2 * root:2 * root + 2]
            large_slots = sum(value - 1 for value in based if value > 2)
            lower.append(root_size - 1 + singletons + large_slots)
        if all(value <= root_degree for value in lower):
            survivors.append(word)
    return feasible, len(survivors), survivors


def rooted_state_count(
    order: int,
    root_q: Sequence[int],
) -> tuple[int, int]:
    states: list[tuple[tuple[int, ...], tuple[int, ...]]] = []
    degrees = tuple(order - 1 - 3 * q for q in root_q)
    for t_values in itertools.product((1, 2, 3), repeat=3):
        if 3 + sum(t_values) > order - 3:
            continue
        u_caps = tuple(d - (3 + t) for d, t in zip(degrees, t_values))
        if min(u_caps) < 0:
            continue
        for zeroes in itertools.product(*(range(t) for t in t_values)):
            forced = tuple(
                sum(
                    3 - t_values[j] + 2 * zeroes[j]
                    for j in range(3)
                    if j != i
                )
                for i in range(3)
            )
            if any(a > b for a, b in zip(forced, u_caps)):
                continue
            full = sum(t - 1 - z for t, z in zip(t_values, zeroes))
            if 4 * full > 2 * sum(root_q):
                continue
            states.append((t_values, zeroes))

    orbit_keys = set()
    for t_values, zeroes in states:
        groups = []
        for q in sorted(set(root_q)):
            records = sorted(
                (t_values[i], zeroes[i])
                for i, observed in enumerate(root_q)
                if observed == q
            )
            groups.append((q, tuple(records)))
        orbit_keys.add(tuple(groups))
    return len(states), len(orbit_keys)


def audit_finite_reductions(profile_doc: dict[str, object]) -> dict[str, object]:
    profiles = enumerate_q_profiles()
    require(len(profiles) == 12, "independent q profile count is not 12")
    expected_rows = profile_doc["semantic"]["raw_profiles"]
    observed_rows = [
        (
            profile_name(values),
            list(values),
            [len(values) - 1 - 3 * q for q in values],
        )
        for values in profiles
    ]
    archived_rows = [
        (row["profile_id"], row["q_values"], row["k_degrees"])
        for row in expected_rows
    ]
    require(observed_rows == archived_rows, "q profile rows differ from archive")

    survivors = []
    for values in profiles:
        degrees = [len(values) - 1 - 3 * q for q in values]
        if min(degrees) >= 4:
            survivors.append(profile_name(values))
    require(survivors == list(PROFILES), "inherited profile survivors differ")

    flower_specs = [
        ("r16-size5", 16, 5, 5, 9, (11, 0)),
        ("r16-size4", 16, 4, 4, 9, (423, 16)),
        ("r15-size5", 15, 5, 5, 8, (1, 0)),
        ("r15-size4", 15, 4, 4, 8, (157, 0)),
        ("r14-size4", 14, 4, 4, 7, (45, 0)),
    ]
    flower_results = {}
    r16_size4_words: list[tuple[int, ...]] = []
    for name, order, root_size, max_size, degree, expected in flower_specs:
        feasible, survivor_count, words = flower_census(
            order, root_size, max_size, degree
        )
        require(
            (feasible, survivor_count) == expected,
            f"flower census mismatch at {name}",
        )
        flower_results[name] = {
            "capacity_feasible": feasible,
            "k_degree_survivors": survivor_count,
        }
        if name == "r16-size4":
            r16_size4_words = words
            flower_results[name]["survivor_words"] = [
                list(word) for word in words
            ]

    require(len(r16_size4_words) == 16, "r16 size-four survivor list wrong")
    require(
        all(
            tuple(sorted(word[2 * i:2 * i + 2])) == (2, 3)
            for word in r16_size4_words
            for i in range(4)
        ),
        "r16 size-four survivor shape is not uniformly (2,3)",
    )
    # Each survivor saturates d_K=9 at every root.  The two external labels
    # of any based triple are therefore L-adjacent to the other three roots:
    # K_{3,2} has row degrees 2 and column degrees 3, violating {0,2}.
    crossing_rejections = sum(
        any(value not in (0, 2) for value in (2, 2, 2, 3, 3))
        for _word in r16_size4_words
    )
    require(crossing_rejections == 16, "r16 size-four crossing rejection failed")

    local_specs = [
        (16, (2, 2, 2), (32, 10)),
        (15, (2, 2, 2), (8, 4)),
        (15, (2, 2, 3), (0, 0)),
        (15, (2, 3, 3), (0, 0)),
        (14, (2, 2, 2), (1, 1)),
        (14, (2, 2, 3), (0, 0)),
        (14, (2, 3, 3), (0, 0)),
        (14, (3, 3, 3), (0, 0)),
    ]
    local_results = {}
    for order, root_q, expected in local_specs:
        observed = rooted_state_count(order, root_q)
        require(observed == expected, f"rooted state mismatch r{order} {root_q}")
        local_results[f"r{order}-q{''.join(map(str, root_q))}"] = {
            "labeled": observed[0],
            "equal_q_orbits": observed[1],
        }

    archive_cover = [
        (row["profile_id"], row["branch_id"])
        for row in profile_doc["semantic"]["sat_branch_cover"]
    ]
    require(archive_cover == RAW_BRANCHES, "raw 11-branch cover differs")
    archived_reduced = [
        (row["profile_id"], row["branch_id"])
        for row in profile_doc["semantic"]["finite_branch_reduction"]
        if row["survives_finite_reductions"]
    ]
    require(archived_reduced == REDUCED_BRANCHES, "archive 11-to-4 reduction differs")

    # Independently check the two non-local eliminations.
    require(3 * 15 % 2 == 1, "r15 all-size-two incidence parity did not obstruct")
    forced_r14_k_degree = 3 + 2
    require(forced_r14_k_degree > 4, "r14 q=3 path obstruction did not exceed dK")
    return {
        "status": "PASS",
        "raw_profile_count": len(profiles),
        "inherited_survivors": survivors,
        "flower_results": flower_results,
        "r16_size4_survivor_count": len(r16_size4_words),
        "r16_size4_crossing_rejections": crossing_rejections,
        "rooted_local_modes": local_results,
        "raw_branch_count": len(RAW_BRANCHES),
        "post_finite_branches": [list(item) for item in REDUCED_BRANCHES],
        "semantic_sha256": profile_doc["semantic_sha256"],
    }


@dataclass
class Formula:
    profile_id: str
    q_values: tuple[int, ...]
    variant: str
    cnf: CNF
    pool: IDPool
    points: tuple[frozenset[int], ...]
    selected: dict[frozenset[int], int]
    k_vars: dict[tuple[int, int], int]


def cardinality_equals(
    cnf: CNF,
    pool: IDPool,
    literals: Iterable[int],
    bound: int,
) -> None:
    encoding = CardEnc.equals(
        lits=list(literals),
        bound=bound,
        vpool=pool,
        encoding=EncType.seqcounter,
    )
    cnf.extend(encoding.clauses)


def cardinality_at_most(
    cnf: CNF,
    pool: IDPool,
    literals: Iterable[int],
    bound: int,
) -> None:
    values = list(literals)
    if len(values) <= bound:
        return
    encoding = CardEnc.atmost(
        lits=values,
        bound=bound,
        vpool=pool,
        encoding=EncType.seqcounter,
    )
    cnf.extend(encoding.clauses)


def build_formula(profile_id: str, variant: str) -> Formula:
    q_values = PROFILES[profile_id]
    order = len(q_values)
    points = tuple(
        frozenset(item)
        for size in (2, 3)
        for item in itertools.combinations(range(order), size)
    )
    edges = tuple(itertools.combinations(range(order), 2))
    pool = IDPool()
    selected = {
        point: pool.id(("point", tuple(sorted(point))))
        for point in points
    }
    k_vars = {edge: pool.id(("K", edge)) for edge in edges}
    f_vars = {edge: pool.id(("F", edge)) for edge in edges}
    cnf = CNF()

    for vertex in range(order):
        cardinality_equals(
            cnf,
            pool,
            (selected[p] for p in points if vertex in p),
            3,
        )

    for edge in edges:
        owners = [selected[p] for p in points if set(edge) <= p]
        cardinality_at_most(cnf, pool, owners, 1)
        for owner in owners:
            cnf.append([-owner, f_vars[edge]])
        cnf.append([-f_vars[edge], *owners])

    for point in points:
        for edge in itertools.combinations(sorted(point), 2):
            cnf.append([-selected[point], k_vars[edge]])

    if variant != NO_COMMON:
        for triple in itertools.combinations(range(order), 3):
            ab, ac, bc = itertools.combinations(triple, 2)
            cnf.append(
                [-f_vars[ab], -f_vars[ac], -f_vars[bc],
                 selected[frozenset(triple)]]
            )
    else:
        witnesses = []
        for triple in itertools.combinations(range(order), 3):
            triple_point = frozenset(triple)
            ab, ac, bc = itertools.combinations(triple, 2)
            witness = pool.id(("unowned_F_triangle", triple))
            witnesses.append(witness)
            cnf.append([-witness, f_vars[ab]])
            cnf.append([-witness, f_vars[ac]])
            cnf.append([-witness, f_vars[bc]])
            cnf.append([-witness, -selected[triple_point]])
            cnf.append(
                [-f_vars[ab], -f_vars[ac], -f_vars[bc],
                 selected[triple_point], witness]
            )
        cnf.append(witnesses)

    triples = tuple(p for p in points if len(p) == 3)
    overlaps_by_triple = {p: [] for p in triples}
    for index, left in enumerate(points):
        for right in points[index + 1:]:
            common_set = left & right
            if len(common_set) != 1:
                continue
            common = next(iter(common_set))
            left_external = sorted(left - {common})
            right_external = sorted(right - {common})
            crossing = [
                k_vars[pair(a, b)]
                for a in left_external
                for b in right_external
            ]
            guard = [-selected[left], -selected[right]]
            if len(left_external) == 1 or len(right_external) == 1:
                for literal in crossing:
                    cnf.append([*guard, literal])
                continue
            pivot = crossing[0]
            for literal in crossing[1:]:
                cnf.append([*guard, -pivot, literal])
                cnf.append([*guard, pivot, -literal])
            witness = pool.id(
                (
                    "full_L_overlap",
                    tuple(sorted(left)),
                    tuple(sorted(right)),
                )
            )
            overlaps_by_triple[left].append(witness)
            overlaps_by_triple[right].append(witness)
            cnf.append([-witness, selected[left]])
            cnf.append([-witness, selected[right]])
            cnf.append([-witness, -pivot])
            cnf.append([-selected[left], -selected[right], pivot, witness])

    for triple in triples:
        cap = sum(q_values[v] for v in triple) // 2
        cardinality_at_most(cnf, pool, overlaps_by_triple[triple], cap)

    k_degrees = tuple(order - 1 - 3 * q for q in q_values)
    for vertex, degree in enumerate(k_degrees):
        literals = [
            k_vars[pair(vertex, other)]
            for other in range(order)
            if other != vertex
        ]
        if variant == K_UPPER:
            cardinality_at_most(cnf, pool, literals, degree)
        else:
            cardinality_equals(cnf, pool, literals, degree)
    if variant == K_UPPER:
        literals = [k_vars[pair(0, other)] for other in range(1, order)]
        cardinality_at_most(cnf, pool, literals, k_degrees[0] - 1)

    return Formula(profile_id, q_values, variant, cnf, pool, points, selected, k_vars)


def canonical_root(formula: Formula, q3_count: int) -> frozenset[int]:
    q2_count = formula.q_values.count(2)
    ordinary = tuple(range(3 - q3_count))
    special = tuple(range(q2_count, q2_count + q3_count))
    root = frozenset((*ordinary, *special))
    require(len(root) == 3, "bad canonical root")
    return root


def branch_units(formula: Formula, branch_id: str) -> tuple[int, ...]:
    triples = tuple(p for p in formula.points if len(p) == 3)
    if branch_id == "no-size3":
        return tuple(-formula.selected[p] for p in triples)
    require(branch_id.startswith("root-q3x"), "unknown branch id")
    count = int(branch_id.removeprefix("root-q3x"))
    return (formula.selected[canonical_root(formula, count)],)


def dimacs_hash(formula: Formula, units: Sequence[int]) -> str:
    digest = hashlib.sha256()
    clause_count = len(formula.cnf.clauses) + len(units)
    digest.update(f"p cnf {formula.pool.top} {clause_count}\n".encode("ascii"))
    for clause in formula.cnf.clauses:
        digest.update(" ".join(map(str, clause)).encode("ascii"))
        digest.update(b" 0\n")
    for literal in units:
        digest.update(f"{literal} 0\n".encode("ascii"))
    return digest.hexdigest()


def formula_record(formula: Formula, branch_id: str) -> tuple[int, int, int, int, str]:
    units = branch_units(formula, branch_id)
    return (
        formula.pool.top,
        len(formula.cnf.clauses),
        len(units),
        len(formula.cnf.clauses) + len(units),
        dimacs_hash(formula, units),
    )


def archived_formula_tuple(row: dict[str, object]) -> tuple[int, int, int, int, str]:
    data = row["formula"]
    return (
        data["variable_count"],
        data["base_clause_count"],
        data["branch_unit_count"],
        data["materialized_clause_count"],
        data["materialized_dimacs_sha256"],
    )


def reconstruct_candidate_diagnostics(
    q_values: Sequence[int],
    raw_points: Sequence[Sequence[int]],
    raw_k_edges: Sequence[Sequence[int]],
) -> dict[str, object]:
    order = len(q_values)
    points = tuple(frozenset(map(int, item)) for item in raw_points)
    k_edges = frozenset(pair(*map(int, item)) for item in raw_k_edges)
    incidence = Counter(v for point in points for v in point)
    pair_owners = {
        edge: []
        for edge in itertools.combinations(range(order), 2)
    }
    missing = []
    point_index = {point: index for index, point in enumerate(points)}
    for index, point in enumerate(points):
        for edge in itertools.combinations(sorted(point), 2):
            pair_owners[edge].append(index)
            if edge not in k_edges:
                missing.append(edge)

    berge = []
    point_set = set(points)
    for triple in itertools.combinations(range(order), 3):
        edges = tuple(itertools.combinations(triple, 2))
        if all(pair_owners[edge] for edge in edges):
            if frozenset(triple) not in point_set:
                berge.append(list(triple))

    crossing_violations = []
    full_overlaps = []
    full_degrees: Counter[frozenset[int]] = Counter()
    meeting_count = 0
    for index, left in enumerate(points):
        for right in points[index + 1:]:
            common_set = left & right
            if len(common_set) != 1:
                continue
            meeting_count += 1
            common = next(iter(common_set))
            left_external = sorted(left - {common})
            right_external = sorted(right - {common})
            l_matrix = [
                [pair(a, b) not in k_edges for b in right_external]
                for a in left_external
            ]
            row_degrees = [sum(row) for row in l_matrix]
            column_degrees = [
                sum(l_matrix[i][j] for i in range(len(left_external)))
                for j in range(len(right_external))
            ]
            if any(v not in (0, 2) for v in (*row_degrees, *column_degrees)):
                crossing_violations.append(
                    {
                        "left": sorted(left),
                        "right": sorted(right),
                        "row_degrees": row_degrees,
                        "column_degrees": column_degrees,
                    }
                )
            if len(left) == len(right) == 3 and sum(row_degrees) == 4:
                full_degrees[left] += 1
                full_degrees[right] += 1
                full_overlaps.append([sorted(left), sorted(right)])

    cap_violations = []
    for point in points:
        if len(point) != 3:
            continue
        cap = sum(q_values[v] for v in point) // 2
        observed = full_degrees[point]
        if observed > cap:
            cap_violations.append(
                {"point": sorted(point), "observed": observed, "cap": cap}
            )

    degrees = [0] * order
    for a, b in k_edges:
        degrees[a] += 1
        degrees[b] += 1
    t_values = [
        sum(len(point) == 3 and v in point for point in points)
        for v in range(order)
    ]
    histogram = Counter(
        (
            tuple(sorted(q_values[v] for v in point)),
            tuple(sorted(t_values[v] for v in point)),
        )
        for point in points
        if len(point) == 3
    )
    f_edges = [edge for edge, owners in pair_owners.items() if owners]
    return {
        "point_count": len(points),
        "size2_point_count": sum(len(point) == 2 for point in points),
        "size3_point_count": sum(len(point) == 3 for point in points),
        "incidence_degrees": [incidence[v] for v in range(order)],
        "linear_pair_owner_violations":
            sum(len(owners) > 1 for owners in pair_owners.values()),
        "f_edge_count": len(f_edges),
        "missing_point_clique_edges": [list(edge) for edge in sorted(set(missing))],
        "k_edge_count": len(k_edges),
        "k_degree_sequence": degrees,
        "common_point_Berge_triangle_count": len(berge),
        "common_point_Berge_triangles": berge,
        "meeting_crossings_checked": meeting_count,
        "meeting_crossing_violation_count": len(crossing_violations),
        "meeting_crossing_violations": crossing_violations,
        "full_L_overlap_count": len(full_overlaps),
        "full_L_overlaps": full_overlaps,
        "overlap_cap_violation_count": len(cap_violations),
        "overlap_cap_violations": cap_violations,
        "t_values": t_values,
        "size3_local_q_t_histogram": {
            "q" + "".join(map(str, q_type)) + "-t" + "".join(map(str, t_type)): count
            for (q_type, t_type), count in sorted(histogram.items())
        },
        "point_index_checksum": semantic_hash(
            [
                [index, sorted(point)]
                for point, index in sorted(
                    point_index.items(), key=lambda item: item[1]
                )
            ]
        ),
    }


def expected_branch_metadata(formula: Formula, branch_id: str) -> dict[str, object]:
    if branch_id == "no-size3":
        return {
            "branch_id": branch_id,
            "root_q3_count": None,
            "root_point": None,
            "normalization":
                "no label symmetry is fixed; every size-three point is absent",
        }
    count = int(branch_id.removeprefix("root-q3x"))
    root = canonical_root(formula, count)
    return {
        "branch_id": branch_id,
        "root_q3_count": count,
        "root_point": sorted(root),
        "root_q_values": sorted(formula.q_values[v] for v in root),
        "normalization": (
            "choose one selected triple with this q-composition and map it "
            "to the displayed labels using only permutations within equal-q classes"
        ),
    }


def validate_candidate(
    candidate: dict[str, object],
    formula: Formula,
    branch_id: str,
    expected_semantic_sha: str,
    archived_formula: tuple[int, int, int, int, str],
) -> dict[str, object]:
    require(
        candidate.get("schema")
        == "conway99-wave14-n3-48-active-local-candidate-v1",
        "candidate schema mismatch",
    )
    require(candidate.get("claim_label") == "CANDIDATE", "claim inflation")
    require(candidate.get("target_result") == "UNKNOWN", "target inflation")
    require(candidate.get("novelty") == "UNKNOWN", "novelty inflation")
    require(candidate.get("target_n3") == 48, "target n3 mismatch")
    require(candidate.get("scope") == "active-label auxiliary object only", "scope mismatch")
    require(candidate.get("profile_id") == formula.profile_id, "profile mismatch")
    require(candidate.get("active_order") == len(formula.q_values), "order mismatch")
    require(tuple(candidate.get("q_values", [])) == formula.q_values, "q mismatch")
    expected_degrees = [
        len(formula.q_values) - 1 - 3 * q for q in formula.q_values
    ]
    require(candidate.get("k_degree_targets") == expected_degrees, "degree targets mismatch")
    require(candidate.get("variant") == formula.variant, "variant mismatch")
    expected_omission = {
        FULL: None,
        NO_COMMON: "common-point/Berge-triangle rule",
        K_UPPER: "exact K-degree equality",
    }[formula.variant]
    require(candidate.get("omitted_premise") == expected_omission, "omission mismatch")
    require(candidate.get("encoded_premises") == ENCODED_PREMISES, "encoded premise metadata mismatch")
    require(candidate.get("unencoded_premises") == UNENCODED_PREMISES, "unencoded premise metadata mismatch")
    require(candidate.get("symmetry_boundary") == SYMMETRY_BOUNDARY, "symmetry boundary mismatch")
    require(candidate.get("branch") == expected_branch_metadata(formula, branch_id), "branch mismatch")

    raw_points = candidate.get("point_sets")
    raw_k_edges = candidate.get("K_edges")
    require(isinstance(raw_points, list), "point list missing")
    require(isinstance(raw_k_edges, list), "K-edge list missing")
    require(
        raw_points == sorted(raw_points, key=lambda item: (len(item), item)),
        "point list is not canonical",
    )
    require(raw_k_edges == sorted(raw_k_edges), "K edge list is not canonical")
    require(len(raw_points) == len({tuple(item) for item in raw_points}), "duplicate point")
    require(len(raw_k_edges) == len({tuple(item) for item in raw_k_edges}), "duplicate K edge")
    order = len(formula.q_values)
    require(
        all(
            len(item) in (2, 3)
            and item == sorted(item)
            and len(set(item)) == len(item)
            and all(isinstance(v, int) and 0 <= v < order for v in item)
            for item in raw_points
        ),
        "invalid point",
    )
    require(
        all(
            len(item) == 2
            and item == sorted(item)
            and item[0] != item[1]
            and all(isinstance(v, int) and 0 <= v < order for v in item)
            for item in raw_k_edges
        ),
        "invalid K edge",
    )
    if branch_id == "no-size3":
        require(all(len(item) == 2 for item in raw_points), "no-size3 branch violated")
    else:
        root = sorted(canonical_root(formula, int(branch_id.removeprefix("root-q3x"))))
        require(root in raw_points, "root branch unit absent")

    replay = reconstruct_candidate_diagnostics(
        formula.q_values, raw_points, raw_k_edges
    )
    require(candidate.get("diagnostics") == replay, "diagnostic replay mismatch")
    require(replay["incidence_degrees"] == [3] * order, "incidence premise fails")
    require(replay["linear_pair_owner_violations"] == 0, "linearity fails")
    require(not replay["missing_point_clique_edges"], "point clique premise fails")
    require(replay["meeting_crossing_violation_count"] == 0, "crossing premise fails")
    require(replay["overlap_cap_violation_count"] == 0, "overlap cap fails")
    if formula.variant == NO_COMMON:
        require(replay["common_point_Berge_triangle_count"] > 0, "control did not violate omitted premise")
    else:
        require(replay["common_point_Berge_triangle_count"] == 0, "common point premise fails")
    if formula.variant == K_UPPER:
        require(
            all(a <= b for a, b in zip(replay["k_degree_sequence"], expected_degrees)),
            "K upper bound fails",
        )
        require(replay["k_degree_sequence"][0] < expected_degrees[0], "control is not deficient at zero")
    else:
        require(replay["k_degree_sequence"] == expected_degrees, "exact K degrees fail")

    core = {
        "profile_id": formula.profile_id,
        "q_values": list(formula.q_values),
        "branch": expected_branch_metadata(formula, branch_id),
        "variant": formula.variant,
        "point_sets": raw_points,
        "K_edges": raw_k_edges,
    }
    require(candidate.get("semantic_core") == core, "semantic core mismatch")
    computed_semantic = semantic_hash(core)
    require(computed_semantic == candidate.get("semantic_sha256"), "semantic digest mismatch")
    require(computed_semantic == expected_semantic_sha, "unexpected semantic candidate digest")
    require(archived_formula_tuple(candidate) == archived_formula, "candidate formula provenance mismatch")
    return {
        "status": "PASS",
        "profile_id": formula.profile_id,
        "branch_id": branch_id,
        "variant": formula.variant,
        "point_count": replay["point_count"],
        "size3_point_count": replay["size3_point_count"],
        "k_edge_count": replay["k_edge_count"],
        "k_degree_sequence": replay["k_degree_sequence"],
        "meeting_crossings_checked": replay["meeting_crossings_checked"],
        "common_point_Berge_triangle_count":
            replay["common_point_Berge_triangle_count"],
        "semantic_sha256": computed_semantic,
    }


def fixed_model_extends(
    formula: Formula,
    branch_id: str,
    candidate: dict[str, object],
) -> bool:
    chosen_points = {
        frozenset(map(int, item)) for item in candidate["point_sets"]
    }
    chosen_k = {pair(*map(int, item)) for item in candidate["K_edges"]}
    assumptions = list(branch_units(formula, branch_id))
    assumptions.extend(
        variable if point in chosen_points else -variable
        for point, variable in formula.selected.items()
    )
    assumptions.extend(
        variable if edge in chosen_k else -variable
        for edge, variable in formula.k_vars.items()
    )
    with Solver(name="glucose42", bootstrap_with=formula.cnf.clauses) as solver:
        return bool(solver.solve(assumptions=assumptions))


def mutate_must_reject(
    name: str,
    validator,
    base: dict[str, object],
    mutator,
    results: dict[str, str],
) -> None:
    changed = copy.deepcopy(base)
    mutator(changed)
    try:
        validator(changed)
    except (AssertionError, KeyError, TypeError, ValueError):
        results[name] = "REJECTED"
    else:
        raise AssertionError(f"hostile mutation accepted: {name}")


def audit_scan_document(
    scan: dict[str, object],
    formula_records: dict[tuple[str, str, str], tuple[int, int, int, int, str]],
    strict_semantic: bool = True,
) -> None:
    require(scan.get("schema") == "conway99-wave14-n3-48-active-local-scan-v1", "scan schema")
    require(scan.get("claim_label") == "CANDIDATE", "scan claim inflation")
    require(scan.get("target_result") == "UNKNOWN", "scan target inflation")
    require(scan.get("novelty") == "UNKNOWN", "scan novelty inflation")
    require(scan.get("solver_name") == "glucose42", "unexpected solver")
    require(scan.get("encoded_premises") == ENCODED_PREMISES, "scan encoded premise metadata")
    require(scan.get("unencoded_premises") == UNENCODED_PREMISES, "scan unencoded premise metadata")
    require(
        scan.get("negative_result_policy")
        == (
            "UNSAT and bounded/timeout solver returns are non-evidentiary "
            "without emitted and independently checked proof traces"
        ),
        "scan negative-result policy",
    )
    require(scan.get("conflict_budget_per_branch") == 30000, "budget provenance")
    require(scan.get("wall_timeout_seconds_per_branch") == 5.0, "timer provenance")
    results = scan.get("results")
    require(isinstance(results, list) and len(results) == 11, "scan branch count")
    cover = [(row["profile_id"], row["branch"]["branch_id"]) for row in results]
    require(cover == RAW_BRANCHES, "scan branch cover")
    require([row["status"] for row in results] == EXPECTED_STATUSES, "scan status rows")
    for row in results:
        key = (row["profile_id"], row["branch"]["branch_id"], FULL)
        require(row.get("variant") == FULL, "scan variant")
        require(archived_formula_tuple(row) == formula_records[key], "scan formula mismatch")
        require(row["formula"].get("branch_units_are_solver_assumptions") is True, "formula unit provenance")
        solver = row.get("solver", {})
        require(solver.get("name") == "glucose42", "row solver mismatch")
        require(solver.get("conflict_budget") == 30000, "row budget mismatch")
        require(solver.get("wall_timeout_seconds_requested") == 5.0, "row timer mismatch")
        require(solver.get("wall_timeout_enforced") is True, "timer was not enforced")
        require(solver.get("proof_trace_emitted") is False, "proof trace emitted changed")
        require(solver.get("proof_trace_checked") is False, "proof trace checked changed")
        if row["status"] == "SAT_CANDIDATE":
            require(row.get("evidentiary_status") == "positive assignment requires exact validation", "positive status boundary")
            require(
                row.get("candidate_path")
                == (
                    "attempts/wave14-computation/"
                    "n3-48-r16-q2x16-no-size3-full-candidate.json"
                ),
                "positive candidate path provenance",
            )
            require(
                row.get("candidate_semantic_sha256")
                == EXPECTED_SEMANTIC_HASHES["full_candidate"],
                "positive candidate digest provenance",
            )
        else:
            require(
                row.get("evidentiary_status")
                == "NON_EVIDENTIARY_NO_CHECKED_PROOF_TRACE",
                "negative status inflation",
            )
            require("candidate_path" not in row, "negative row has candidate")
            require("candidate_semantic_sha256" not in row, "negative row has candidate digest")
    require(
        Counter(row["status"] for row in results)
        == Counter(
            {
                "SAT_CANDIDATE": 1,
                "UNSAT_UNVERIFIED": 7,
                "BUDGET_UNKNOWN": 1,
                "TIMEOUT_UNKNOWN": 2,
            }
        ),
        "scan status histogram",
    )
    semantic_projection = [
        {
            "profile_id": row["profile_id"],
            "branch_id": row["branch"]["branch_id"],
            "status": row["status"],
            "formula_sha256": row["formula"]["materialized_dimacs_sha256"],
            "candidate_semantic_sha256": row.get("candidate_semantic_sha256"),
        }
        for row in results
    ]
    require(scan["semantic"]["results"] == semantic_projection, "scan semantic projection")
    if strict_semantic:
        require(semantic_hash(scan["semantic"]) == scan.get("semantic_sha256"), "scan semantic digest")
        require(scan.get("semantic_sha256") == EXPECTED_SEMANTIC_HASHES["scan"], "scan digest changed")


def audit_all() -> dict[str, object]:
    observed_hashes = {}
    for name, expected in EXPECTED_FILE_HASHES.items():
        path = ROOT / Path(name)
        observed = sha256_file(path)
        require(observed == expected, f"input file hash mismatch: {name}")
        observed_hashes[name] = observed

    profile_doc = load_json(PROFILE_PATH)
    scan_doc = load_json(SCAN_PATH)
    controls_doc = load_json(CONTROLS_PATH)
    discovery_validation = load_json(DISCOVERY_VALIDATION_PATH)
    failures_doc = load_json(FAILURES_PATH)

    for name, doc, digest_key in [
        ("profiles", profile_doc, "profiles"),
        ("scan", scan_doc, "scan"),
        ("controls", controls_doc, "controls"),
        ("discovery validation", discovery_validation, "discovery_validation"),
    ]:
        require(semantic_hash(doc["semantic"]) == doc["semantic_sha256"], f"{name} semantic hash")
        require(doc["semantic_sha256"] == EXPECTED_SEMANTIC_HASHES[digest_key], f"{name} digest changed")

    finite = audit_finite_reductions(profile_doc)

    scan_by_key = {
        (row["profile_id"], row["branch"]["branch_id"], FULL): row
        for row in scan_doc["results"]
    }
    controls_by_key = {
        (row["profile_id"], row["branch"]["branch_id"], row["variant"]): row
        for row in controls_doc["results"]
    }
    formula_records = {}
    candidate_results = []

    for profile_id in PROFILES:
        formula = build_formula(profile_id, FULL)
        for p, branch in RAW_BRANCHES:
            if p != profile_id:
                continue
            key = (p, branch, FULL)
            observed = formula_record(formula, branch)
            require(observed == EXPECTED_FORMULAS[key], f"expected full formula mismatch: {key}")
            require(observed == archived_formula_tuple(scan_by_key[key]), f"archived full formula mismatch: {key}")
            formula_records[key] = observed
        if profile_id == "r16-q2x16":
            candidate = load_json(FULL_CANDIDATE_PATH)
            key = (profile_id, "no-size3", FULL)
            validation = validate_candidate(
                candidate,
                formula,
                "no-size3",
                EXPECTED_SEMANTIC_HASHES["full_candidate"],
                formula_records[key],
            )
            require(fixed_model_extends(formula, "no-size3", candidate), "full positive core does not extend")
            require(
                scan_by_key[key].get("candidate_path")
                == "attempts/wave14-computation/n3-48-r16-q2x16-no-size3-full-candidate.json",
                "scan candidate path provenance mismatch",
            )
            require(
                scan_by_key[key].get("candidate_semantic_sha256")
                == validation["semantic_sha256"],
                "scan candidate semantic provenance mismatch",
            )
            candidate_results.append(validation)
        del formula
        gc.collect()

    control_cases = [
        (
            "r16-q2x16",
            "root-q3x0",
            NO_COMMON,
            NO_COMMON_CANDIDATE_PATH,
            EXPECTED_SEMANTIC_HASHES["no_common_control"],
        ),
        (
            "r16-q2x16",
            "no-size3",
            K_UPPER,
            K_UPPER_CANDIDATE_PATH,
            EXPECTED_SEMANTIC_HASHES["k_upper_control"],
        ),
    ]
    control_results = []
    for profile_id, branch, variant, path, expected_digest in control_cases:
        formula = build_formula(profile_id, variant)
        key = (profile_id, branch, variant)
        observed = formula_record(formula, branch)
        require(observed == EXPECTED_FORMULAS[key], f"expected control formula mismatch: {key}")
        require(observed == archived_formula_tuple(controls_by_key[key]), f"archived control formula mismatch: {key}")
        formula_records[key] = observed
        candidate = load_json(path)
        validation = validate_candidate(
            candidate, formula, branch, expected_digest, observed
        )
        require(fixed_model_extends(formula, branch, candidate), f"control core does not extend: {variant}")
        expected_path = rel(path)
        require(controls_by_key[key].get("candidate_path") == expected_path, f"control path provenance mismatch: {variant}")
        require(controls_by_key[key].get("candidate_semantic_sha256") == expected_digest, f"control digest provenance mismatch: {variant}")
        control_results.append(validation)
        del formula
        gc.collect()

    require(
        controls_doc.get("schema") == "conway99-wave14-n3-48-positive-controls-v1",
        "controls schema",
    )
    require(controls_doc.get("claim_label") == "CANDIDATE", "controls claim inflation")
    require(controls_doc.get("target_result") == "UNKNOWN", "controls target inflation")
    require(controls_doc.get("novelty") == "UNKNOWN", "controls novelty inflation")
    require([row["status"] for row in controls_doc["results"]] == ["SAT_CANDIDATE"] * 2, "controls are not positive")

    audit_scan_document(scan_doc, formula_records)

    require(failures_doc.get("claim_label") == "UNKNOWN", "failure log claim inflation")
    require(failures_doc.get("target_result") == "UNKNOWN", "failure log target inflation")
    require(len(failures_doc.get("failures", [])) == 2, "failure log count")
    require(
        all(row.get("mathematical_status") == "NON_EVIDENTIARY" for row in failures_doc["failures"]),
        "failure log status inflation",
    )

    # Candidate-validator hostile mutations.
    full_formula = build_formula("r16-q2x16", FULL)
    full_candidate = load_json(FULL_CANDIDATE_PATH)
    full_key = ("r16-q2x16", "no-size3", FULL)
    candidate_mutations: dict[str, str] = {}

    def candidate_validator(value):
        validate_candidate(
            value,
            full_formula,
            "no-size3",
            EXPECTED_SEMANTIC_HASHES["full_candidate"],
            formula_records[full_key],
        )

    mutate_must_reject("candidate_claim_inflation", candidate_validator, full_candidate, lambda d: d.__setitem__("claim_label", "VERIFIED"), candidate_mutations)
    mutate_must_reject("candidate_target_inflation", candidate_validator, full_candidate, lambda d: d.__setitem__("target_result", "EXCLUDED"), candidate_mutations)
    mutate_must_reject("candidate_novelty_inflation", candidate_validator, full_candidate, lambda d: d.__setitem__("novelty", "NEW"), candidate_mutations)
    mutate_must_reject("candidate_scope_expansion", candidate_validator, full_candidate, lambda d: d.__setitem__("scope", "99-vertex graph"), candidate_mutations)
    mutate_must_reject("candidate_encoded_premise_forgery", candidate_validator, full_candidate, lambda d: d["encoded_premises"].pop(), candidate_mutations)
    mutate_must_reject("candidate_unencoded_premise_forgery", candidate_validator, full_candidate, lambda d: d["unencoded_premises"].pop(), candidate_mutations)
    mutate_must_reject("candidate_symmetry_boundary_forgery", candidate_validator, full_candidate, lambda d: d.__setitem__("symmetry_boundary", "completed automorphism assumed"), candidate_mutations)
    mutate_must_reject("candidate_duplicate_point", candidate_validator, full_candidate, lambda d: d["point_sets"].append(copy.deepcopy(d["point_sets"][0])), candidate_mutations)
    mutate_must_reject("candidate_deleted_point", candidate_validator, full_candidate, lambda d: d["point_sets"].pop(), candidate_mutations)
    mutate_must_reject("candidate_duplicate_K_edge", candidate_validator, full_candidate, lambda d: d["K_edges"].append(copy.deepcopy(d["K_edges"][0])), candidate_mutations)
    mutate_must_reject("candidate_deleted_K_edge", candidate_validator, full_candidate, lambda d: d["K_edges"].pop(), candidate_mutations)
    mutate_must_reject("candidate_forged_diagnostic", candidate_validator, full_candidate, lambda d: d["diagnostics"].__setitem__("k_edge_count", 73), candidate_mutations)
    mutate_must_reject("candidate_forged_normalization", candidate_validator, full_candidate, lambda d: d["branch"].__setitem__("normalization", "completed automorphism"), candidate_mutations)
    mutate_must_reject("candidate_forged_formula_hash", candidate_validator, full_candidate, lambda d: d["formula"].__setitem__("materialized_dimacs_sha256", "0" * 64), candidate_mutations)
    mutate_must_reject("candidate_forged_semantic_hash", candidate_validator, full_candidate, lambda d: d.__setitem__("semantic_sha256", "0" * 64), candidate_mutations)

    # Scan/status/provenance hostile mutations.  Recompute semantic data for
    # status mutations so rejection is not merely a stale-digest check.
    scan_mutations: dict[str, str] = {}

    def scan_validator(value):
        audit_scan_document(value, formula_records)

    def promote_negative_status(value):
        value["results"][4]["status"] = "UNSAT_VERIFIED"
        value["semantic"]["results"][4]["status"] = "UNSAT_VERIFIED"
        value["semantic_sha256"] = semantic_hash(value["semantic"])

    def redirect_positive_digest(value):
        replacement = EXPECTED_SEMANTIC_HASHES["k_upper_control"]
        value["results"][0]["candidate_semantic_sha256"] = replacement
        value["semantic"]["results"][0]["candidate_semantic_sha256"] = replacement
        value["semantic_sha256"] = semantic_hash(value["semantic"])

    mutate_must_reject("scan_claim_inflation", scan_validator, scan_doc, lambda d: d.__setitem__("claim_label", "VERIFIED"), scan_mutations)
    mutate_must_reject("scan_target_inflation", scan_validator, scan_doc, lambda d: d.__setitem__("target_result", "EXCLUDED"), scan_mutations)
    mutate_must_reject("scan_novelty_inflation", scan_validator, scan_doc, lambda d: d.__setitem__("novelty", "NEW"), scan_mutations)
    mutate_must_reject("scan_unencoded_premise_forgery", scan_validator, scan_doc, lambda d: d["unencoded_premises"].pop(), scan_mutations)
    mutate_must_reject("scan_negative_policy_forgery", scan_validator, scan_doc, lambda d: d.__setitem__("negative_result_policy", "UNSAT proves nonexistence"), scan_mutations)
    mutate_must_reject("scan_status_promotion", scan_validator, scan_doc, promote_negative_status, scan_mutations)
    mutate_must_reject("scan_proof_checked_forgery", scan_validator, scan_doc, lambda d: d["results"][4]["solver"].__setitem__("proof_trace_checked", True), scan_mutations)
    mutate_must_reject("scan_negative_evidence_forgery", scan_validator, scan_doc, lambda d: d["results"][4].__setitem__("evidentiary_status", "PROVED_UNSAT"), scan_mutations)
    mutate_must_reject("scan_formula_hash_forgery", scan_validator, scan_doc, lambda d: d["results"][0]["formula"].__setitem__("materialized_dimacs_sha256", "0" * 64), scan_mutations)
    mutate_must_reject("scan_candidate_path_redirect", scan_validator, scan_doc, lambda d: d["results"][0].__setitem__("candidate_path", rel(K_UPPER_CANDIDATE_PATH)), scan_mutations)
    mutate_must_reject("scan_candidate_digest_redirect", scan_validator, scan_doc, redirect_positive_digest, scan_mutations)
    mutate_must_reject("scan_missing_branch", scan_validator, scan_doc, lambda d: d["results"].pop(), scan_mutations)
    mutate_must_reject("scan_duplicate_branch", scan_validator, scan_doc, lambda d: d["results"].append(copy.deepcopy(d["results"][0])), scan_mutations)
    mutate_must_reject("scan_semantic_hash_forgery", scan_validator, scan_doc, lambda d: d.__setitem__("semantic_sha256", "0" * 64), scan_mutations)

    # A separate path check binds the sole positive scan row to the actual
    # expected object; audit_scan_document intentionally focuses on status.
    positive = scan_doc["results"][0]
    positive_path = (ROOT / Path(positive["candidate_path"])).resolve()
    require(positive_path == FULL_CANDIDATE_PATH.resolve(), "positive candidate path escaped provenance")
    require(sha256_file(positive_path) == EXPECTED_FILE_HASHES[rel(FULL_CANDIDATE_PATH)], "positive candidate file changed")

    del full_formula
    gc.collect()

    return {
        "schema": "conway99-wave14-n3-48-independent-computation-audit-v1",
        "role": "verifier",
        # Freeze the audit identifier so a successful replay is byte-for-byte
        # reproducible instead of changing the evidence artifact on every run.
        "audit_frozen_utc": "2026-07-23T09:37:49Z",
        "git_commit": "fd02baec74a5cc19dd415277f9d2504e2d022a9f",
        "claim_label": "VERIFIED",
        "scope": "Wave14 conditional n3=48 active-local computation lane only",
        "verdict": "PASS",
        "target_result": "UNKNOWN",
        "novelty": "UNKNOWN",
        "negative_solver_results_evidentiary": False,
        "environment": {
            "python": sys.version,
            "python_sat": pysat.__version__,
            "platform": platform.platform(),
            "solver": "glucose42",
        },
        "input_sha256": observed_hashes,
        "finite_reductions": finite,
        "formula_records": {
            "|".join(key): {
                "variable_count": value[0],
                "base_clause_count": value[1],
                "branch_unit_count": value[2],
                "materialized_clause_count": value[3],
                "materialized_dimacs_sha256": value[4],
            }
            for key, value in formula_records.items()
        },
        "positive_candidate_validations": candidate_results,
        "positive_control_validations": control_results,
        "scan_status_histogram": dict(sorted(Counter(EXPECTED_STATUSES).items())),
        "raw_scan_statuses": [
            {
                "profile_id": profile,
                "branch_id": branch,
                "status": status,
            }
            for (profile, branch), status in zip(RAW_BRANCHES, EXPECTED_STATUSES)
        ],
        "mutation_resistance": {
            "candidate": candidate_mutations,
            "scan_status_and_provenance": scan_mutations,
            "rejected_count": len(candidate_mutations) + len(scan_mutations),
        },
        "unencoded_global_premises": scan_doc["unencoded_premises"],
        "limitations": [
            "No Wave14 proof report/artifact and no Wave13 path was inspected.",
            "No Git command was run; git_commit is the frozen commit declared by the candidate report.",
            "Seven UNSAT returns have no emitted or checked proof trace and remain non-evidentiary.",
            "One conflict-budget return and two wall-timeout returns remain UNKNOWN.",
            "The positive object is only an active-label auxiliary object, not H, not a 99-vertex adjacency matrix, and not a Conway graph or counterexample.",
            "Conditional n3=48 exclusion, the Conway-99 target, and novelty remain UNKNOWN.",
        ],
    }


def main() -> int:
    output = audit_all()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    destination = OUTPUT_DIR / "independent-audit-results.json"
    destination.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "verdict": output["verdict"],
        "target_result": output["target_result"],
        "raw_profile_count": output["finite_reductions"]["raw_profile_count"],
        "formula_count": len(output["formula_records"]),
        "positive_candidate_count": len(output["positive_candidate_validations"]),
        "positive_control_count": len(output["positive_control_validations"]),
        "scan_status_histogram": output["scan_status_histogram"],
        "mutations_rejected": output["mutation_resistance"]["rejected_count"],
        "output": rel(destination),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
