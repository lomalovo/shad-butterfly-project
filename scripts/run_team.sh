#!/bin/bash
set -e
cd "$(dirname "$0")/.."
PY=${PY:-.venv/bin/python}
IMAGES=${IMAGES:-data/images}
for c in ${CONFIGS:-dino_butterfly dino_butterfly_moth dino_neg owlv2 owlv2_neg qwen3vl qwen3vl_neg}; do
  $PY src/infer.py --config configs/$c.yaml --images $IMAGES --out outputs/raw/$c.jsonl
  $PY src/postprocess.py --raw outputs/raw/$c.jsonl --config configs/$c.yaml --out outputs/preds/$c.jsonl
done
$PY src/postprocess.py --raw outputs/raw/dino_butterfly_moth.jsonl --config configs/dino_butterfly_moth.yaml --nms off \
  --out outputs/preds/dino_butterfly_moth__nms_off.jsonl
$PY src/postprocess.py --raw outputs/raw/qwen3vl.jsonl --config configs/qwen3vl.yaml --nms 0.9 \
  --out outputs/preds/qwen3vl__nms_0.9.jsonl
$PY src/postprocess.py --raw outputs/raw/qwen3vl_neg.jsonl --config configs/qwen3vl_neg.yaml --nms 0.9 \
  --out outputs/preds/qwen3vl_neg__nms_0.9.jsonl
$PY src/postprocess.py --raw outputs/raw/qwen3vl_neg.jsonl --config configs/final.yaml --out outputs/preds/final.jsonl
cp outputs/raw/qwen3vl_neg.meta.json outputs/raw/final.meta.json
$PY src/verify.py --config configs/final_verify.yaml --images $IMAGES --raw outputs/raw/qwen3vl_neg.jsonl \
  --out outputs/raw/final_verify.jsonl
$PY src/postprocess.py --raw outputs/raw/final_verify.jsonl --config configs/final_verify.yaml --out outputs/preds/final_verify.jsonl
$PY src/proxy_stats.py --preds outputs/preds/*.jsonl
