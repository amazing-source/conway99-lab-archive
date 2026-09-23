#!/usr/bin/env python3
"""Bounded exact solver for the canonical mask-51739 joint-incidence problem.

This is a construction search, not a verifier.  It reconstructs the frozen
Wave 41 core, enumerates all Wave 42 mixed-legal six-sets, and asks for sixty
sets satisfying every pair partition and cross-fibre concurrence capacity.

The cardinality model uses one Boolean per retained six-set.  Exact pair
partitions and upper bounds on every positive cross-fibre Gram cell suffice:
each selected block contributes four cells to each cross-fibre block, so the
fixed total of 240 forces every upper bound to be attained.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import itertools
import json
import os
import random
import threading
import time
from collections import Counter
from pathlib import Path
from typing import Sequence

from pysat.card import CardEnc, EncType
from pysat.solvers import Cadical195, Glucose42, Kissat404, Minicard

FORMAT = "wave43-joint-completion-v1"
SOURCE = Path("verification/wave41-allquotient-lifts/independent-results.json")
SOURCE_SHA256 = "062785a47ddb8f85ddec10a76a663c262ec9c60c133b681be5228639b022260b"
CORE_EDGE_SHA256 = "b0a9e7cc75d933597d43c9395e0192268b71ad88b93120a82dc662e64585b664"
CANONICAL_MASK = 51739
FIBRE_SIZE = 12
X_SIZE = 36


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def read_source(path: Path) -> dict[str, object]:
    raw = path.read_bytes()
    if sha256_bytes(raw) != SOURCE_SHA256:
        raise ValueError("frozen Wave 41 source hash changed")
    payload = json.loads(raw)
    witness = payload["rank_identity"]["minimum_witness"]
    if witness["mask"] != CANONICAL_MASK:
        raise ValueError("canonical witness mask changed")
    if witness["core_edges_sha256"] != CORE_EDGE_SHA256:
        raise ValueError("canonical core-edge digest changed")
    return payload


def adjacency_from_edges(edges: Sequence[Sequence[int]]) -> list[list[int]]:
    adjacency = [[0] * X_SIZE for _ in range(X_SIZE)]
    seen: set[tuple[int, int]] = set()
    for raw_edge in edges:
        if len(raw_edge) != 2:
            raise ValueError("malformed core edge")
        left, right = sorted(map(int, raw_edge))
        if not 0 <= left < right < X_SIZE or (left, right) in seen:
            raise ValueError("bad or duplicate core edge")
        seen.add((left, right))
        adjacency[left][right] = adjacency[right][left] = 1
    if len(seen) != 54 or {sum(row) for row in adjacency} != {3}:
        raise ValueError("frozen core is not cubic on 36 vertices")
    return adjacency


def components(adjacency: Sequence[Sequence[int]]) -> list[tuple[int, ...]]:
    unseen = set(range(X_SIZE))
    answer: list[tuple[int, ...]] = []
    while unseen:
        start = min(unseen)
        seen = {start}
        stack = [start]
        while stack:
            vertex = stack.pop()
            for neighbor, value in enumerate(adjacency[vertex]):
                if value and neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
        unseen -= seen
        answer.append(tuple(sorted(seen)))
    return sorted(answer, key=lambda part: (len(part), part))


def forced_gram(adjacency: Sequence[Sequence[int]]) -> list[list[int]]:
    square = [
        [
            sum(adjacency[left][middle] * adjacency[middle][right] for middle in range(X_SIZE))
            for right in range(X_SIZE)
        ]
        for left in range(X_SIZE)
    ]
    gram = [
        [
            (12 if left == right else 0)
            - adjacency[left][right]
            + 2
            - int(left // FIBRE_SIZE == right // FIBRE_SIZE)
            - square[left][right]
            for right in range(X_SIZE)
        ]
        for left in range(X_SIZE)
    ]
    if {gram[index][index] for index in range(X_SIZE)} != {10}:
        raise ValueError("forced Gram diagonal changed")
    if {sum(row) for row in gram} != {60} or min(map(min, gram)) < 0:
        raise ValueError("forced Gram row sums or support changed")
    return gram


def fibre_pairs(fibre: int, gram: Sequence[Sequence[int]]) -> tuple[tuple[int, int], ...]:
    start = fibre * FIBRE_SIZE
    pairs = tuple(
        pair
        for pair in itertools.combinations(range(start, start + FIBRE_SIZE), 2)
        if gram[pair[0]][pair[1]] == 1
    )
    if len(pairs) != 60:
        raise ValueError(f"fibre {fibre} does not have 60 allowed pairs")
    return pairs


def mixed_legal(
    block: Sequence[int],
    adjacency: Sequence[Sequence[int]],
) -> bool:
    selected = set(block)
    if len(selected) != 6:
        return False
    return all(
        sum(adjacency[vertex][neighbor] for neighbor in selected)
        <= (1 if vertex in selected else 2)
        for vertex in range(X_SIZE)
    )


def enumerate_candidates(
    pairs: Sequence[Sequence[tuple[int, int]]],
    gram: Sequence[Sequence[int]],
    adjacency: Sequence[Sequence[int]],
    small: frozenset[int],
) -> list[tuple[int, int, int]]:
    candidates: list[tuple[int, int, int]] = []
    census = Counter()
    for indices in itertools.product(range(60), repeat=3):
        triple = tuple(pairs[fibre][indices[fibre]] for fibre in range(3))
        block = tuple(itertools.chain.from_iterable(triple))
        census["raw"] += 1
        if not all(
            gram[left][right] > 0
            for left, right in itertools.combinations(block, 2)
        ):
            continue
        census["support"] += 1
        if sum(vertex in small for vertex in block) != 2:
            continue
        census["component"] += 1
        if not mixed_legal(block, adjacency):
            continue
        census["mixed"] += 1
        candidates.append(indices)
    expected = Counter(raw=216000, support=118718, component=49736, mixed=45032)
    if census != expected:
        raise ValueError(f"candidate census changed: {census}")
    return candidates


def candidate_digest(candidates: Sequence[Sequence[int]]) -> str:
    return sha256_bytes(canonical_bytes([list(item) for item in candidates]))


def build_solver(
    candidates: Sequence[tuple[int, int, int]],
    pairs: Sequence[Sequence[tuple[int, int]]],
    gram: Sequence[Sequence[int]],
    backend: str,
) -> tuple[Cadical195 | Glucose42 | Kissat404 | Minicard, dict[str, int]]:
    if backend == "minicard":
        solver: Cadical195 | Minicard = Minicard(use_timer=True)
    elif backend == "cadical195":
        solver = Cadical195(use_timer=True)
    elif backend == "kissat404":
        solver = Kissat404(use_timer=True)
    elif backend == "glucose42":
        solver = Glucose42(use_timer=True)
    else:
        raise ValueError(f"unsupported backend {backend}")
    top_id = len(candidates)
    cnf_clauses = 0

    def add_atmost(group: Sequence[int], bound: int) -> None:
        nonlocal top_id, cnf_clauses
        if backend == "minicard":
            solver.add_atmost(group, bound)
            return
        encoded = CardEnc.atmost(
            lits=list(group),
            bound=bound,
            top_id=top_id,
            encoding=EncType.seqcounter,
        )
        top_id = encoded.nv
        cnf_clauses += len(encoded.clauses)
        solver.append_formula(encoded.clauses)

    pair_groups = [[[ ] for _ in range(60)] for _ in range(3)]
    cell_groups: dict[tuple[int, int], list[int]] = {
        (left, right): []
        for first, second in ((0, 1), (0, 2), (1, 2))
        for left in range(first * FIBRE_SIZE, (first + 1) * FIBRE_SIZE)
        for right in range(second * FIBRE_SIZE, (second + 1) * FIBRE_SIZE)
        if gram[left][right] > 0
    }
    for offset, indices in enumerate(candidates, start=1):
        for fibre, pair_index in enumerate(indices):
            pair_groups[fibre][pair_index].append(offset)
        for first, second in ((0, 1), (0, 2), (1, 2)):
            for left in pairs[first][indices[first]]:
                for right in pairs[second][indices[second]]:
                    cell_groups[(left, right)].append(offset)

    # Every named within-fibre pair is used exactly once.
    for fibre in range(3):
        for group in pair_groups[fibre]:
            if not group:
                raise ValueError("empty pair-partition group")
            solver.add_clause(group)
            cnf_clauses += 1
            add_atmost(group, 1)

    # Every positive cross-fibre cell stays below its exact Gram target.
    # Exactness follows from the fixed 60 blocks: each block contributes four
    # incidences per fibre pair, while every target block sums to 240.
    target_sums = Counter()
    for (left, right), group in sorted(cell_groups.items()):
        bound = gram[left][right]
        if bound not in (1, 2):
            raise ValueError("unexpected positive cross-fibre Gram entry")
        add_atmost(group, bound)
        target_sums[(left // FIBRE_SIZE, right // FIBRE_SIZE)] += bound
    if set(target_sums.values()) != {240}:
        raise ValueError(f"cross-fibre target sums changed: {target_sums}")

    if backend != "kissat404":
        solver.set_phases([-variable for variable in range(1, len(candidates) + 1)])
    stats = {
        "candidate_variables": len(candidates),
        "pair_exactly_one_constraints": 180,
        "cross_cell_upper_bound_constraints": len(cell_groups),
        "mathematical_cardinality_constraints": 180 + len(cell_groups),
        "cnf_variables_including_auxiliary": top_id,
        "cnf_clauses": cnf_clauses,
    }
    if len(cell_groups) != 412:
        raise ValueError(f"positive cross-cell census changed: {len(cell_groups)}")
    return solver, stats


def build_pairing_solver(
    candidates: Sequence[tuple[int, int, int]],
    pairs: Sequence[Sequence[tuple[int, int]]],
    gram: Sequence[Sequence[int]],
    backend: str,
    variable_seed: int,
) -> tuple[
    Cadical195 | Glucose42 | Kissat404 | Minicard,
    dict[str, int],
    dict[tuple[int, int, int, int], int],
]:
    """Build an equivalent compact model using three pairwise matchings."""
    if backend == "minicard":
        solver: Cadical195 | Glucose42 | Kissat404 | Minicard = Minicard(use_timer=True)
    elif backend == "cadical195":
        solver = Cadical195(use_timer=True)
    elif backend == "kissat404":
        solver = Kissat404(use_timer=True)
    elif backend == "glucose42":
        solver = Glucose42(use_timer=True)
    else:
        raise ValueError(f"unsupported backend {backend}")

    fibre_pairs_ = ((0, 1), (0, 2), (1, 2))
    combo_sets = {
        fibre_pair: sorted(
            {(item[fibre_pair[0]], item[fibre_pair[1]]) for item in candidates}
        )
        for fibre_pair in fibre_pairs_
    }
    combo_counts = [len(combo_sets[fibre_pair]) for fibre_pair in fibre_pairs_]
    if combo_counts != [2881, 2881, 2694]:
        raise ValueError(f"pair-combination census changed: {combo_counts}")

    variable_of: dict[tuple[int, int, int, int], int] = {}
    next_variable = 1
    generator = random.Random(variable_seed)
    for first, second in fibre_pairs_:
        assignment_order = list(combo_sets[(first, second)])
        generator.shuffle(assignment_order)
        for left_index, right_index in assignment_order:
            variable_of[(first, second, left_index, right_index)] = next_variable
            next_variable += 1
    semantic_variable_count = next_variable - 1
    top_id = semantic_variable_count
    cnf_clauses = 0

    def add_atmost(group: Sequence[int], bound: int) -> None:
        nonlocal top_id, cnf_clauses
        if backend == "minicard":
            solver.add_atmost(group, bound)
            return
        encoded = CardEnc.atmost(
            lits=list(group),
            bound=bound,
            top_id=top_id,
            encoding=EncType.seqcounter,
        )
        top_id = encoded.nv
        cnf_clauses += len(encoded.clauses)
        solver.append_formula(encoded.clauses)

    # Each of the three pairwise relations is a perfect matching.
    perfect_matching_exactly_one = 0
    for first, second in fibre_pairs_:
        combos = combo_sets[(first, second)]
        for side in (0, 1):
            for pair_index in range(60):
                group = [
                    variable_of[(first, second, left_index, right_index)]
                    for left_index, right_index in combos
                    if (left_index, right_index)[side] == pair_index
                ]
                if not group:
                    raise ValueError("empty compact perfect-matching group")
                solver.add_clause(group)
                cnf_clauses += 1
                add_atmost(group, 1)
                perfect_matching_exactly_one += 1
    if perfect_matching_exactly_one != 360:
        raise ValueError("compact perfect-matching constraint count changed")

    # Each pairwise matching realizes its exact cross-fibre Gram block.
    cell_caps = 0
    for first, second in fibre_pairs_:
        combos = combo_sets[(first, second)]
        cell_groups: dict[tuple[int, int], list[int]] = {
            (left, right): []
            for left in range(first * FIBRE_SIZE, (first + 1) * FIBRE_SIZE)
            for right in range(second * FIBRE_SIZE, (second + 1) * FIBRE_SIZE)
            if gram[left][right] > 0
        }
        for left_index, right_index in combos:
            variable = variable_of[(first, second, left_index, right_index)]
            for left in pairs[first][left_index]:
                for right in pairs[second][right_index]:
                    cell_groups[(left, right)].append(variable)
        if sum(gram[left][right] for left, right in cell_groups) != 240:
            raise ValueError("compact cross-fibre Gram target sum changed")
        for (left, right), group in sorted(cell_groups.items()):
            add_atmost(group, gram[left][right])
            cell_caps += 1
    if cell_caps != 412:
        raise ValueError(f"compact cross-cell cap count changed: {cell_caps}")

    # The first two matchings share the fibre-0 pair.  Their choices determine
    # a triple (i,j,k).  Illegal triples are forbidden; a legal triple forces
    # the corresponding selected edge in the fibre-1--fibre-2 matching.
    legal = set(candidates)
    options_01: dict[int, list[int]] = {index: [] for index in range(60)}
    options_02: dict[int, list[int]] = {index: [] for index in range(60)}
    for left_index, middle_index in combo_sets[(0, 1)]:
        options_01[left_index].append(middle_index)
    for left_index, right_index in combo_sets[(0, 2)]:
        options_02[left_index].append(right_index)

    illegal_binary_clauses = 0
    legal_ternary_clauses = 0
    for left_index in range(60):
        for middle_index in options_01[left_index]:
            first_variable = variable_of[(0, 1, left_index, middle_index)]
            for right_index in options_02[left_index]:
                second_variable = variable_of[(0, 2, left_index, right_index)]
                triple = (left_index, middle_index, right_index)
                if triple not in legal:
                    solver.add_clause([-first_variable, -second_variable])
                    cnf_clauses += 1
                    illegal_binary_clauses += 1
                    continue
                third_variable = variable_of[(1, 2, middle_index, right_index)]
                solver.add_clause(
                    [-first_variable, -second_variable, third_variable]
                )
                cnf_clauses += 1
                legal_ternary_clauses += 1
    if legal_ternary_clauses != 45032:
        raise ValueError("one compatibility clause was not emitted per candidate")

    if backend != "kissat404":
        solver.set_phases(
            [-variable for variable in range(1, semantic_variable_count + 1)]
        )
    stats = {
        "pairing_variables_01": combo_counts[0],
        "pairing_variables_02": combo_counts[1],
        "pairing_variables_12": combo_counts[2],
        "semantic_pairing_variables": semantic_variable_count,
        "perfect_matching_exactly_one_constraints": perfect_matching_exactly_one,
        "cross_cell_upper_bound_constraints": cell_caps,
        "illegal_triple_binary_clauses": illegal_binary_clauses,
        "legal_triple_ternary_clauses": legal_ternary_clauses,
        "cnf_variables_including_auxiliary": top_id,
        "cnf_clauses": cnf_clauses,
        "variable_numbering_seed": variable_seed,
    }
    return solver, stats, variable_of


def selected_certificate(
    candidates: Sequence[tuple[int, int, int]],
    model: Sequence[int],
    pairs: Sequence[Sequence[tuple[int, int]]],
) -> dict[str, object]:
    true_variables = {literal for literal in model if literal > 0}
    selected = [
        indices
        for variable, indices in enumerate(candidates, start=1)
        if variable in true_variables
    ]
    if len(selected) != 60:
        raise ValueError(f"model selected {len(selected)} candidates, not 60")
    blocks = [
        [vertex for fibre in range(3) for vertex in pairs[fibre][indices[fibre]]]
        for indices in selected
    ]
    return {
        "selected_pair_indices": [list(item) for item in selected],
        "selected_blocks": blocks,
        "selected_pair_indices_sha256": sha256_bytes(
            canonical_bytes([list(item) for item in selected])
        ),
        "selected_blocks_sha256": sha256_bytes(canonical_bytes(blocks)),
    }


def selected_pairing_certificate(
    candidates: Sequence[tuple[int, int, int]],
    model: Sequence[int],
    pairs: Sequence[Sequence[tuple[int, int]]],
    variable_of: dict[tuple[int, int, int, int], int],
) -> dict[str, object]:
    true_variables = {literal for literal in model if literal > 0}
    selected_relations: dict[tuple[int, int], list[tuple[int, int]]] = {}
    for first, second in ((0, 1), (0, 2), (1, 2)):
        selected = sorted(
            (left_index, right_index)
            for (f0, f1, left_index, right_index), variable in variable_of.items()
            if (f0, f1) == (first, second) and variable in true_variables
        )
        if len(selected) != 60:
            raise ValueError(
                f"compact model selected {len(selected)} edges for {(first, second)}"
            )
        selected_relations[(first, second)] = selected

    map_01 = dict(selected_relations[(0, 1)])
    map_02 = dict(selected_relations[(0, 2)])
    map_12 = dict(selected_relations[(1, 2)])
    triples = [(index, map_01[index], map_02[index]) for index in range(60)]
    if any(map_12[middle] != right for _, middle, right in triples):
        raise ValueError("three selected pairwise matchings are inconsistent")
    if any(triple not in set(candidates) for triple in triples):
        raise ValueError("compact model selected an illegal triple")
    blocks = [
        [vertex for fibre in range(3) for vertex in pairs[fibre][indices[fibre]]]
        for indices in triples
    ]
    relation_payload = {
        f"{first}{second}": [list(item) for item in selected_relations[(first, second)]]
        for first, second in ((0, 1), (0, 2), (1, 2))
    }
    return {
        "selected_pair_indices": [list(item) for item in triples],
        "selected_pairings": relation_payload,
        "selected_blocks": blocks,
        "selected_pair_indices_sha256": sha256_bytes(
            canonical_bytes([list(item) for item in triples])
        ),
        "selected_pairings_sha256": sha256_bytes(canonical_bytes(relation_payload)),
        "selected_blocks_sha256": sha256_bytes(canonical_bytes(blocks)),
    }


class _ProcessMemoryCounters(ctypes.Structure):
    _fields_ = [
        ("cb", ctypes.c_ulong),
        ("PageFaultCount", ctypes.c_ulong),
        ("PeakWorkingSetSize", ctypes.c_size_t),
        ("WorkingSetSize", ctypes.c_size_t),
        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
        ("PagefileUsage", ctypes.c_size_t),
        ("PeakPagefileUsage", ctypes.c_size_t),
    ]


def process_working_set_bytes() -> int:
    counters = _ProcessMemoryCounters()
    counters.cb = ctypes.sizeof(counters)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    psapi = ctypes.WinDLL("psapi", use_last_error=True)
    kernel32.GetCurrentProcess.restype = ctypes.c_void_p
    psapi.GetProcessMemoryInfo.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(_ProcessMemoryCounters),
        ctypes.c_ulong,
    ]
    psapi.GetProcessMemoryInfo.restype = ctypes.c_int
    handle = kernel32.GetCurrentProcess()
    if not psapi.GetProcessMemoryInfo(
        handle, ctypes.byref(counters), counters.cb
    ):
        raise OSError("GetProcessMemoryInfo failed")
    return int(counters.WorkingSetSize)


def physical_free_fraction() -> float:
    class _MemoryStatus(ctypes.Structure):
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

    memory = _MemoryStatus()
    memory.dwLength = ctypes.sizeof(memory)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.GlobalMemoryStatusEx.argtypes = [ctypes.POINTER(_MemoryStatus)]
    kernel32.GlobalMemoryStatusEx.restype = ctypes.c_int
    if not kernel32.GlobalMemoryStatusEx(ctypes.byref(memory)):
        raise OSError("GlobalMemoryStatusEx failed")
    if memory.ullTotalPhys <= 0:
        raise ValueError("physical memory total is zero")
    return float(memory.ullAvailPhys) / float(memory.ullTotalPhys)


def solve_bounded(
    solver: Cadical195 | Glucose42 | Kissat404 | Minicard,
    timeout_seconds: float,
    backend: str,
    conflict_budget: int,
) -> tuple[bool | None, list[int] | None, dict[str, int | float]]:
    if backend in ("cadical195", "kissat404", "glucose42"):
        # CaDiCaL's solve call holds the Python GIL on this Windows build, so
        # a Python timer thread cannot enforce wall time.  A conflict budget
        # is deterministic and is complemented by an external process guard
        # in the recorded run protocol.
        solver.conf_budget(conflict_budget)
        working_set_before = process_working_set_bytes()
        free_fraction_before = physical_free_fraction()
        started = time.monotonic()
        status = solver.solve_limited()
        elapsed = time.monotonic() - started
        model = solver.get_model() if status is True else None
        stats: dict[str, int | float] = dict(solver.accum_stats())
        stats["elapsed_seconds"] = round(elapsed, 6)
        stats["working_set_before_solve_bytes"] = working_set_before
        stats["working_set_after_solve_bytes"] = process_working_set_bytes()
        stats["host_free_fraction_before_solve"] = round(free_fraction_before, 6)
        stats["host_free_fraction_after_solve"] = round(physical_free_fraction(), 6)
        stats["conflict_budget"] = conflict_budget
        stats["interrupt_reason"] = (
            "conflict_budget" if status is None else "solver_terminal"
        )
        return status, model, stats

    stop_monitor = threading.Event()
    monitor_state: dict[str, int | float | str] = {
        "peak_working_set_bytes": process_working_set_bytes(),
        "minimum_host_free_fraction": physical_free_fraction(),
        "interrupt_reason": "none",
    }

    def monitor() -> None:
        deadline = time.monotonic() + timeout_seconds
        while not stop_monitor.wait(0.25):
            working_set = process_working_set_bytes()
            free_fraction = physical_free_fraction()
            monitor_state["peak_working_set_bytes"] = max(
                int(monitor_state["peak_working_set_bytes"]), working_set
            )
            monitor_state["minimum_host_free_fraction"] = min(
                float(monitor_state["minimum_host_free_fraction"]), free_fraction
            )
            if working_set >= int(3.75 * 1024**3):
                monitor_state["interrupt_reason"] = "working_set_guard"
                solver.interrupt()
                return
            if free_fraction <= 0.15:
                monitor_state["interrupt_reason"] = "host_free_memory_guard"
                solver.interrupt()
                return
            if time.monotonic() >= deadline:
                monitor_state["interrupt_reason"] = "wall_clock_guard"
                solver.interrupt()
                return

    monitor_thread = threading.Thread(target=monitor, name="wave43-resource-guard")
    started = time.monotonic()
    monitor_thread.start()
    try:
        status = solver.solve_limited(expect_interrupt=True)
        model = solver.get_model() if status is True else None
    finally:
        stop_monitor.set()
        monitor_thread.join()
    elapsed = time.monotonic() - started
    stats: dict[str, int | float] = dict(solver.accum_stats())
    stats["elapsed_seconds"] = round(elapsed, 6)
    stats["peak_working_set_bytes"] = int(monitor_state["peak_working_set_bytes"])
    stats["minimum_host_free_fraction"] = round(
        float(monitor_state["minimum_host_free_fraction"]), 6
    )
    stats["interrupt_reason"] = str(monitor_state["interrupt_reason"])
    return status, model, stats


def build_result(
    source_path: Path,
    timeout_seconds: float,
    backend: str,
    conflict_budget: int,
    model_kind: str,
    variable_seed: int,
) -> dict[str, object]:
    source = read_source(source_path)
    witness = source["rank_identity"]["minimum_witness"]
    adjacency = adjacency_from_edges(witness["core_edges"])
    gram = forced_gram(adjacency)
    core_components = components(adjacency)
    if [len(part) for part in core_components] != [12, 24]:
        raise ValueError("core component orders changed")
    small = frozenset(core_components[0])
    pairs = tuple(fibre_pairs(fibre, gram) for fibre in range(3))
    candidates = enumerate_candidates(pairs, gram, adjacency, small)
    variable_of: dict[tuple[int, int, int, int], int] | None = None
    if model_kind == "direct":
        solver, encoding_stats = build_solver(candidates, pairs, gram, backend)
    elif model_kind == "pairing":
        solver, encoding_stats, variable_of = build_pairing_solver(
            candidates, pairs, gram, backend, variable_seed
        )
    else:
        raise ValueError(f"unsupported model kind {model_kind}")
    try:
        status, model, solver_stats = solve_bounded(
            solver, timeout_seconds, backend, conflict_budget
        )
    finally:
        solver.delete()

    result: dict[str, object] = {
        "format": FORMAT,
        "claim_label": "CANDIDATE" if status is True else "UNKNOWN",
        "scope": (
            "Conditional on n3=4158, rank_F3(M)=12, every edge having local "
            "type 2+2+2, and occurrence of the canonical rank-33 mask-51739 "
            "core. No automorphism is assumed."
        ),
        "input": {
            str(source_path).replace("\\", "/"): SOURCE_SHA256,
            "canonical_mask": CANONICAL_MASK,
            "canonical_core_edges_sha256": CORE_EDGE_SHA256,
        },
        "candidate_enumeration": {
            "filter_census": [216000, 118718, 49736, 45032],
            "retained_candidate_sha256": candidate_digest(candidates),
        },
        "encoding": {
            **encoding_stats,
            "model_kind": model_kind,
            "logic": (
                "The pairing model uses three perfect matchings of the three "
                "60-pair inventories. The first two determine each triple; "
                "binary clauses forbid illegal triples and ternary clauses "
                "force the third matching. Every matching obeys upper bounds "
                "Q[u,v]. Its sixty pair-pairs contribute 240 cell incidences, "
                "equal to the Gram-block target sum, so all bounds are exact."
                if model_kind == "pairing"
                else (
                    "One Boolean per retained six-set; exactly one selected "
                    "set per named within-fibre pair; at most Q[u,v] selected "
                    "sets per positive cross-fibre cell. Sixty blocks "
                    "contribute 240 cell incidences per fibre pair, equal to "
                    "each Gram-block target sum, so every upper bound is "
                    "attained exactly."
                )
            ),
            "solver": (
                "PySAT Minicard 1.9.dev7 native cardinality"
                if backend == "minicard"
                else (
                    "PySAT CaDiCaL 1.9.5 with sequential-counter CNF"
                    if backend == "cadical195"
                    else (
                        "PySAT Kissat 4.0.4 with sequential-counter CNF"
                        if backend == "kissat404"
                        else "PySAT Glucose 4.2 with sequential-counter CNF"
                    )
                )
            ),
        },
        "bounded_run": {
            "timeout_seconds": timeout_seconds,
            "conflict_budget": conflict_budget,
            "status": {True: "SAT", False: "UNSAT", None: "INTERRUPTED"}[status],
            "solver_stats": solver_stats,
            "unsat_evidence": (
                "NONE: this run did not request or check an UNSAT proof; an "
                "UNSAT solver status alone would remain non-evidence."
            ),
        },
        "status_wall": {
            "full_B": "CANDIDATE_PENDING_INDEPENDENT_VERIFICATION"
            if status is True
            else "NOT_CONSTRUCTED_OR_EXCLUDED",
            "compatible_H": "NOT_CONSTRUCTED_OR_EXCLUDED",
            "endpoint_excluded": False,
            "conway_99_resolved": False,
        },
    }
    if model is not None:
        if model_kind == "pairing":
            if variable_of is None:
                raise AssertionError("compact variable map is absent")
            result["certificate"] = selected_pairing_certificate(
                candidates, model, pairs, variable_of
            )
        else:
            result["certificate"] = selected_certificate(candidates, model, pairs)
    return result


def describe_pairing_reduction(
    source_path: Path,
    variable_seed: int,
) -> dict[str, object]:
    source = read_source(source_path)
    witness = source["rank_identity"]["minimum_witness"]
    adjacency = adjacency_from_edges(witness["core_edges"])
    gram = forced_gram(adjacency)
    core_components = components(adjacency)
    small = frozenset(core_components[0])
    pairs = tuple(fibre_pairs(fibre, gram) for fibre in range(3))
    candidates = enumerate_candidates(pairs, gram, adjacency, small)
    solver, encoding_stats, _ = build_pairing_solver(
        candidates, pairs, gram, "cadical195", variable_seed
    )
    solver.delete()
    fibre_pairs_ = ((0, 1), (0, 2), (1, 2))
    combo_payload = {
        f"{first}{second}": [
            list(item)
            for item in sorted(
                {(candidate[first], candidate[second]) for candidate in candidates}
            )
        ]
        for first, second in fibre_pairs_
    }
    return {
        "format": "wave43-joint-pairing-reduction-v1",
        "claim_label": "DERIVED_PENDING_INDEPENDENT_VERIFICATION",
        "scope": (
            "Conditional on n3=4158, rank_F3(M)=12, every edge having local "
            "type 2+2+2, and occurrence of the canonical rank-33 mask-51739 "
            "core. No automorphism is assumed."
        ),
        "input": {
            str(source_path).replace("\\", "/"): SOURCE_SHA256,
            "canonical_mask": CANONICAL_MASK,
            "canonical_core_edges_sha256": CORE_EDGE_SHA256,
        },
        "candidate_enumeration": {
            "filter_census": [216000, 118718, 49736, 45032],
            "retained_candidate_sha256": candidate_digest(candidates),
        },
        "pairing_projection": {
            "pairing_combo_counts_01_02_12": [2881, 2881, 2694],
            "pairing_combo_sha256": {
                key: sha256_bytes(canonical_bytes(value))
                for key, value in combo_payload.items()
            },
        },
        "canonical_sequential_counter_cnf": encoding_stats,
        "equivalence_argument": [
            (
                "A full B selects sixty legal triples and therefore projects "
                "to three perfect matchings satisfying all encoded clauses."
            ),
            (
                "Conversely, the selected 01 and 02 perfect matchings give "
                "one triple for every fibre-0 pair. Illegal triples are "
                "forbidden and each legal triple forces its 12 edge."
            ),
            (
                "The sixty induced 12 edges are distinct because the 01 and "
                "02 relations are bijections. The independently exact-one "
                "12 matching contains sixty edges, so it equals the induced "
                "relation and the three matchings define exactly sixty legal "
                "six-sets."
            ),
            (
                "Each cross-fibre matching contributes 240 point-pair "
                "incidences. The sum of its Gram-cell upper bounds is also "
                "240, so every upper bound is attained and all 432 "
                "concurrence entries, including zeros excluded by support, "
                "have their exact target."
            ),
        ],
        "bounded_search_boundary": {
            "terminal_model_or_checked_unsat_proof": False,
            "classification": "UNKNOWN",
            "note": (
                "Bounded solver runs are diagnostics only and are summarized "
                "in failed-routes.md; they are not nonexistence evidence."
            ),
        },
        "status_wall": {
            "full_B": "NOT_CONSTRUCTED_OR_EXCLUDED",
            "compatible_H": "NOT_CONSTRUCTED_OR_EXCLUDED",
            "endpoint_excluded": False,
            "conway_99_resolved": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--timeout-seconds", type=float, default=300.0)
    parser.add_argument(
        "--backend",
        choices=("cadical195", "glucose42", "kissat404", "minicard"),
        default="cadical195",
    )
    parser.add_argument("--conflict-budget", type=int, default=50000)
    parser.add_argument(
        "--model",
        choices=("pairing", "direct"),
        default="pairing",
    )
    parser.add_argument("--variable-seed", type=int, default=0)
    parser.add_argument("--describe-only", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not 1 <= args.timeout_seconds <= 1800:
        raise SystemExit("timeout must be between 1 and 1800 seconds")
    if not 1 <= args.conflict_budget <= 10_000_000:
        raise SystemExit("conflict budget must be between 1 and 10000000")
    if not 0 <= args.variable_seed <= 2**31 - 1:
        raise SystemExit("variable seed must be between 0 and 2147483647")
    if args.describe_only:
        if args.model != "pairing":
            raise SystemExit("--describe-only currently requires --model pairing")
        result = describe_pairing_reduction(args.source, args.variable_seed)
    else:
        result = build_result(
            args.source,
            args.timeout_seconds,
            args.backend,
            args.conflict_budget,
            args.model,
            args.variable_seed,
        )
    rendered = canonical_bytes(result)
    if args.output is None:
        print(rendered.decode("utf-8"), end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(rendered)
        print(
            json.dumps(
                {
                    "output": str(args.output),
                    "sha256": sha256_bytes(rendered),
                    "status": (
                        result["bounded_run"]["status"]
                        if "bounded_run" in result
                        else result["claim_label"]
                    ),
                },
                sort_keys=True,
            )
        )


if __name__ == "__main__":
    main()
