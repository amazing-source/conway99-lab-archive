"""Hard-bounded integral ordinary MacWilliams feasibility scout.

The parent process enforces a wall-clock timeout on a fresh worker.  UNKNOWN
or a killed worker is telemetry only and proves no infeasibility.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from math import comb
from pathlib import Path


N = 99
K = 54
ORDER = 1 << K
HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE / "integral-scout.json"
WEIGHTS = [0] + list(range(14, 100, 2))
A_LOWER = {
    0: 1,
    14: 99,
    24: 4158,
    26: 693,
    30: 70686,
    32: 41580,
    34: 36036,
    36: 8547,
}
B_BASE_LOWER = {
    0: 1,
    15: 99,
    24: 693,
    26: 4158,
    31: 41580,
    33: 79002,
    35: 8316,
    37: 27720,
    39: 231,
    99: 1,
}


def krawtchouk(degree: int, weight: int) -> int:
    return sum(
        (-1) ** overlap
        * comb(weight, overlap)
        * comb(N - weight, degree - overlap)
        for overlap in range(
            max(0, degree - (N - weight)),
            min(weight, degree) + 1,
        )
    )


def lower_with_complements() -> dict[int, int]:
    lower = dict(B_BASE_LOWER)
    for weight, value in list(lower.items()):
        lower[N - weight] = max(lower.get(N - weight, 0), value)
    return lower


def worker(timeout_ms: int) -> None:
    from z3 import Int, Solver, Sum, sat

    image = {weight: Int(f"A_{weight}") for weight in WEIGHTS}
    dual = {weight: Int(f"B_{weight}") for weight in range(N + 1)}
    dual_lower = lower_with_complements()
    solver = Solver()
    solver.set(timeout=timeout_ms)
    for weight in WEIGHTS:
        solver.add(image[weight] >= A_LOWER.get(weight, 0))
    solver.add(image[0] == 1)
    solver.add(Sum([image[weight] for weight in WEIGHTS]) == ORDER)
    for degree in range(N + 1):
        solver.add(dual[degree] >= dual_lower.get(degree, 0))
        if 1 <= degree <= 14:
            solver.add(dual[degree] == 0)
        solver.add(
            Sum(
                [
                    image[weight] * krawtchouk(degree, weight)
                    for weight in WEIGHTS
                ]
            )
            == ORDER * dual[degree]
        )
    for weight in range(50):
        solver.add(dual[weight] == dual[N - weight])

    status = solver.check()
    result = {
        "solver_status": str(status).upper(),
        "solver_reason_unknown": solver.reason_unknown(),
    }
    if status == sat:
        model = solver.model()
        result["image_coefficients"] = {
            str(weight): model.eval(
                image[weight], model_completion=True
            ).as_long()
            for weight in WEIGHTS
            if model.eval(image[weight], model_completion=True).as_long()
        }
        result["dual_coefficients"] = {
            str(weight): model.eval(
                dual[weight], model_completion=True
            ).as_long()
            for weight in range(N + 1)
            if model.eval(dual[weight], model_completion=True).as_long()
        }
    print(json.dumps(result), flush=True)


def bounded_run(timeout_ms: int, wall_seconds: int) -> dict:
    started = time.monotonic()
    command = [
        sys.executable,
        "-B",
        str(Path(__file__).resolve()),
        "--worker",
        "--timeout-ms",
        str(timeout_ms),
    ]
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=wall_seconds,
            check=False,
        )
        elapsed = time.monotonic() - started
        if completed.returncode != 0:
            return {
                "status": "UNKNOWN_WORKER_ERROR",
                "returncode": completed.returncode,
                "stderr_tail": completed.stderr[-1000:],
                "elapsed_seconds": round(elapsed, 3),
            }
        payload = json.loads(completed.stdout.strip().splitlines()[-1])
        payload["status"] = payload.pop("solver_status")
        payload["elapsed_seconds"] = round(elapsed, 3)
        return payload
    except subprocess.TimeoutExpired:
        elapsed = time.monotonic() - started
        return {
            "status": "UNKNOWN_HARD_TIMEOUT",
            "elapsed_seconds": round(elapsed, 3),
        }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--timeout-ms", type=int, default=10_000)
    parser.add_argument("--wall-seconds", type=int, default=15)
    parser.add_argument("--worker", action="store_true")
    args = parser.parse_args()
    if args.worker:
        worker(args.timeout_ms)
        return
    result = {
        "format": "wave131-integral-scout-v1",
        "claim_label": "UNKNOWN",
        "scope": (
            "Integral A_i and B_j satisfying the full ordinary binary "
            "MacWilliams system, d(image)>=14, d(dual)>=15, all forced "
            "lower bounds, and dual complement symmetry."
        ),
        "solver_timeout_ms": args.timeout_ms,
        "hard_wall_seconds": args.wall_seconds,
        "result": bounded_run(args.timeout_ms, args.wall_seconds),
        "negative_inference_allowed": False,
        "limitations": [
            "UNKNOWN or timeout is not evidence of infeasibility.",
            "An integral formal enumerator would not construct a code.",
            "A realized code would not by itself construct the target graph.",
        ],
    }
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result["result"], sort_keys=True))


if __name__ == "__main__":
    main()
