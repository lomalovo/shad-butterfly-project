#!/bin/bash
set -e
cd "$(dirname "$0")/.."
PY=${PY:-.venv/bin/python}
IMAGES=$1
IDS=${2:-$1}
OUT=${OUT:-outputs/exam}
for c in ${CONFIGS:-final}; do
  $PY src/infer.py --config configs/$c.yaml --images $IMAGES --out $OUT/raw/$c.jsonl --errors $OUT/errors.jsonl
  $PY src/postprocess.py --raw $OUT/raw/$c.jsonl --config configs/$c.yaml --out $OUT/submission_$c.jsonl
  $PY src/validate_submission.py --sub $OUT/submission_$c.jsonl --ids $IDS || true
done
$PY src/verify.py --config configs/final_verify.yaml --images $IMAGES --raw $OUT/raw/final.jsonl --out $OUT/raw/final_verify.jsonl
$PY src/postprocess.py --raw $OUT/raw/final_verify.jsonl --config configs/final_verify.yaml --out $OUT/submission_final_verify.jsonl
$PY src/validate_submission.py --sub $OUT/submission_final_verify.jsonl --ids $IDS
