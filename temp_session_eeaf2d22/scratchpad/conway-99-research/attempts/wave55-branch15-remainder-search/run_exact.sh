#!/usr/bin/env bash
set -u

formula="/mnt/c/home/researcher/OneDrive/Documents/math conjecture/attempts/wave53-proof-cover/branch-15-x187-zero.opb"
out="/mnt/c/home/researcher/OneDrive/Documents/math conjecture/attempts/wave55-branch15-remainder-search"
exact="/home/researcher/.cache/conway-tools/exact/build-wave3/Exact"

cd "$out" || exit 70
date -u +"%Y-%m-%dT%H:%M:%SZ" > started-utc.txt
grep -E 'MemTotal|MemAvailable' /proc/meminfo > resource-before.txt
sha256sum "$exact" "$formula" > run-input-hashes.sha256

"$exact" \
  --timeout=120 \
  --proof-assumptions=0 \
  --proof-log=branch15-x187-zero-120s.raw.pbp \
  "$formula" \
  > solver.txt 2>&1
exit_code=$?

printf '%s\n' "$exit_code" > exit-code.txt
grep -E 'MemTotal|MemAvailable' /proc/meminfo > resource-after.txt
date -u +"%Y-%m-%dT%H:%M:%SZ" > finished-utc.txt
exit "$exit_code"
