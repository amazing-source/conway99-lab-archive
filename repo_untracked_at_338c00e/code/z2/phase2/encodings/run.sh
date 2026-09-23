#!/bin/sh
# usage: run.sh <tag> <solver: kissat|cadical> <seconds> <cnf-file-in-cnf/> [extra solver options...]
# Runs ONE native solver in Docker (image satbox, 1 CPU) detached; log -> logs/<tag>.log; statistics on.
TAG=$1; SOLVER=$2; SECS=$3; CNF=$4; shift 4
DIR="C:/home/researcher/Desktop/conway99-involution/code/z2/phase2/encodings"
if [ "$SOLVER" = kissat ]; then CMD="kissat -s -n --time=$SECS $* cnf/$CNF"; else CMD="cadical -n -t $SECS $* cnf/$CNF"; fi
docker run -d --rm --name p2enc_$TAG --cpus 1 -v "$DIR:/work" satbox sh -c "echo CMD: $CMD; date +%s; $CMD > logs/$TAG.log 2>&1; echo EXIT \$? >> logs/$TAG.log; date +%s >> logs/$TAG.log" > /dev/null
echo "started $TAG: $CMD"
