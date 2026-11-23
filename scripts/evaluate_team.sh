#!/bin/bash
set -e
cd "$(dirname "$0")/.."
PY=${PY:-.venv/bin/python}
GOLDEN=${1:-data/golden/candidate_339.jsonl}
OUT=${OUT:-outputs/eval}
mkdir -p $OUT
$PY src/evaluate.py --golden $GOLDEN --preds outputs/preds/*.jsonl --out $OUT
for c in dino_butterfly dino_butterfly_moth dino_neg owlv2 owlv2_neg; do
  $PY src/sweep.py --raw outputs/raw/$c.jsonl --config configs/$c.yaml --golden $GOLDEN --out $OUT/sweep_$c.csv | tail -1
done
for c in qwen3vl qwen3vl_neg; do
  $PY src/sweep.py --raw outputs/raw/$c.jsonl --config configs/$c.yaml --golden $GOLDEN --thresholds 0 --nms off 0.3 0.4 0.5 0.6 0.7 0.8 0.9 \
    --out $OUT/sweep_$c.csv | tail -1
done
$PY src/sweep.py --raw outputs/raw/final_verify.jsonl --config configs/final_verify.yaml --golden $GOLDEN \
  --thresholds 0 0.01 0.02 0.05 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 0.95 0.98 --nms 0.3 --out $OUT/sweep_final_verify.csv | tail -1
$PY src/bootstrap.py --golden $GOLDEN --a outputs/preds/final.jsonl --b outputs/preds/final_verify.jsonl
