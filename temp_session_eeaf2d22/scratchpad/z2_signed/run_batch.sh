#!/bin/sh
# Overnight batch: 3 case CNFs x 2 native solvers in Docker, 1 CPU each, wall limit $1 seconds (default 8h).
# Results: batch_<solver>_<case>.log (solver output; look for "s SATISFIABLE" / "s UNSATISFIABLE" / "s UNKNOWN").
LIMIT=${1:-28800}
DIR="C:/home/researcher/AppData/Local/Temp/claude/C--Users-RESEARCHER-Desktop/eeaf2d22-69e1-42a1-97c8-376f05816a6c/scratchpad/z2_signed"
for c in sib one dis; do
  docker run -d --rm --name sat_cadical_$c --cpus 1 -v "$DIR:/work" satbox sh -c "cadical -t $LIMIT -q k14_$c.cnf > batch_cadical_$c.log 2>&1; echo EXIT \$? >> batch_cadical_$c.log"
  docker run -d --rm --name sat_kissat_$c --cpus 1 -v "$DIR:/work" satbox sh -c "kissat --time=$LIMIT -q k14_$c.cnf > batch_kissat_$c.log 2>&1; echo EXIT \$? >> batch_kissat_$c.log"
done
docker ps --format '{{.Names}} {{.Status}}'
