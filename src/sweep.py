import argparse

import numpy as np
import pandas as pd
import yaml

from common import parse_id, read_jsonl
from evaluate import load_golden
from metrics import per_image, summarize
from postprocess import process


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--raw', required=True)
    parser.add_argument('--golden', required=True)
    parser.add_argument('--thresholds', nargs='+', type=float, default=list(np.round(np.arange(0.05, 0.61, 0.05), 2)))
    parser.add_argument('--nms', nargs='+', default=['off', '0.3', '0.5', '0.7'])
    parser.add_argument('--out', default=None)
    parser.add_argument('--config', default=None)
    args = parser.parse_args()

    keep_labels = yaml.safe_load(open(args.config)).get('keep_labels') if args.config else None

    golden = load_golden(args.golden)
    raw = read_jsonl(args.raw)
    rows = []
    for nms_value in args.nms:
        nms_iou = None if nms_value == 'off' else float(nms_value)
        for t in args.thresholds:
            preds = {parse_id(str(r['photo_id'])): process(r, t, nms_iou, keep_labels) for r in raw}
            res = summarize(per_image(golden, preds))
            rows.append({'threshold': t, 'nms': nms_value, **res})
    df = pd.DataFrame(rows)
    cols = ['threshold', 'nms', 'f1_50', 'precision_50', 'recall_50', 'f1_75', 'neg_fp_boxes', 'neg_fp_images']
    print(df[cols].to_string(index=False, float_format='%.3f'))
    best = df.sort_values('f1_50', ascending=False).iloc[0]
    print(f'best: threshold={best.threshold} nms={best.nms} f1_50={best.f1_50:.3f}')
    if args.out:
        df.to_csv(args.out, index=False)


if __name__ == '__main__':
    main()
