"""Hard-bounded integral ordinary-enumerator scout for Wave143.

UNKNOWN and timeout are telemetry only.  The parent process enforces a hard
wall around a fresh worker.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
import time
from math import comb
from pathlib import Path


HERE = Path(__file__).resolve().parent
MODEL_PATH = HERE / "optimize_rational.py"


def load_model():
    spec = importlib.util.spec_from_file_location(
        "wave143_integer_model",
        MODEL_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Wave143 model")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def worker(sign: int, mode: str, timeout_ms: int) -> None:
    from z3 import Int, Optimize, Solver, Sum, sat

    model_data = load_model()
    base = model_data.BASE
    image = {
        weight: Int(f"A_{weight}") for weight in base.IMAGE_WEIGHTS
    }
    dual = {
        degree: Int(f"D_{degree}") for degree in range(base.N + 1)
    }
    k = Int("k")
    engine = Optimize() if mode == "maximize" else Solver()
    engine.set(timeout=timeout_ms)

    for weight in base.IMAGE_WEIGHTS:
        engine.add(image[weight] >= base.IMAGE_LOWER.get(weight, 0))
    engine.add(image[0] == 1)
    engine.add(Sum(list(image.values())) == base.ORDER)
    dual_lower = base.dual_lower()
    for degree in range(base.N + 1):
        engine.add(dual[degree] >= dual_lower.get(degree, 0))
        if 1 <= degree <= 14:
            engine.add(dual[degree] == 0)
        engine.add(
            Sum(
                [
                    image[weight] * base.krawtchouk(degree, weight)
                    for weight in base.IMAGE_WEIGHTS
                ]
            )
            == base.ORDER * dual[degree]
        )
    for degree in range(50):
        engine.add(dual[degree] == dual[base.N - degree])

    for degree, multiplier in model_data.S_VALUES.items():
        engine.add(
            model_data.moment(image, degree)
            == sign * model_data.ARF_MAGNITUDE * multiplier
        )
    for degree in range(6, base.N + 1):
        bound = model_data.ARF_MAGNITUDE * comb(base.N, degree)
        value = model_data.moment(image, degree)
        engine.add(value >= -bound, value <= bound)

    engine.add(k >= 0)
    engine.add(
        model_data.moment(image, 6)
        == sign
        * model_data.ARF_MAGNITUDE
        * (model_data.S6_CONSTANT + 512 * k)
    )
    if mode == "target4158":
        engine.add(k == 1386)
        handle = None
    else:
        handle = engine.maximize(k)

    status = engine.check()
    result: dict[str, object] = {
        "solver_status": str(status).upper(),
        "reason_unknown": engine.reason_unknown(),
    }
    if status == sat:
        z3_model = engine.model()
        result["k"] = z3_model.eval(k, model_completion=True).as_long()
        result["n3"] = 3 * result["k"]
        result["image_coefficients"] = {
            str(weight): z3_model.eval(
                variable,
                model_completion=True,
            ).as_long()
            for weight, variable in image.items()
            if z3_model.eval(variable, model_completion=True).as_long()
        }
        result["dual_coefficients"] = {
            str(degree): z3_model.eval(
                variable,
                model_completion=True,
            ).as_long()
            for degree, variable in dual.items()
            if z3_model.eval(variable, model_completion=True).as_long()
        }
        if handle is not None:
            result["optimizer_lower"] = str(handle.lower())
            result["optimizer_upper"] = str(handle.upper())
            result["proved_optimal_by_status_alone"] = False
    print(json.dumps(result), flush=True)


def bounded(
    sign: int,
    mode: str,
    timeout_ms: int,
    wall_seconds: int,
) -> dict:
    command = [
        sys.executable,
        "-B",
        str(Path(__file__).resolve()),
        "--worker",
        "--sign",
        str(sign),
        "--mode",
        mode,
        "--timeout-ms",
        str(timeout_ms),
    ]
    started = time.monotonic()
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=wall_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {
            "status": "UNKNOWN_HARD_TIMEOUT",
            "elapsed_seconds": round(time.monotonic() - started, 3),
        }
    elapsed = time.monotonic() - started
    if completed.returncode:
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--sign", type=int, choices=(-1, 1))
    parser.add_argument(
        "--mode",
        choices=("target4158", "maximize"),
        default="target4158",
    )
    parser.add_argument("--timeout-ms", type=int, default=30_000)
    parser.add_argument("--wall-seconds", type=int, default=40)
    parser.add_argument(
        "--output",
        type=Path,
        default=HERE / "integer-scout.json",
    )
    args = parser.parse_args()
    if args.worker:
        if args.sign is None:
            raise SystemExit("--worker requires --sign")
        worker(args.sign, args.mode, args.timeout_ms)
        return 0

    results = []
    for sign in (1, -1):
        for mode in ("target4158", "maximize"):
            results.append(
                {
                    "sign": sign,
                    "mode": mode,
                    **bounded(
                        sign,
                        mode,
                        args.timeout_ms,
                        args.wall_seconds,
                    ),
                }
            )
    payload = {
        "format": "wave143-integral-scout-v1",
        "claim_label": "UNKNOWN",
        "scope": (
            "Integral image and dual ordinary enumerators with full "
            "MacWilliams divisibility, Wave137 Arf/K0..K5, all shadow "
            "bounds, and n3=3k through the exact S6 equation"
        ),
        "solver_timeout_ms": args.timeout_ms,
        "hard_wall_seconds": args.wall_seconds,
        "results": results,
        "negative_inference_allowed": False,
        "limitations": [
            "UNKNOWN or timeout is not evidence of infeasibility.",
            "A solver exit code is not an exact infeasibility certificate.",
            "An integral formal enumerator would not construct a code or graph.",
        ],
    }
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(results, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
