import argparse
import os

import pandas as pd

from common import read_jsonl


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--preds', nargs='+', required=True)
    parser.add_argument('--meta', default='data/preliminary_annotations.csv')
    parser.add_argument('--out', default='outputs/proxy_stats.md')
    args = parser.parse_args()

    meta = pd.read_csv(args.meta, encoding='utf-8-sig').set_index('photo_id')
    rows = []
    for path in args.preds:
        name = os.path.splitext(os.path.basename(path))[0]
        for r in read_jsonl(path):
            n = None if r['boxes'] is None else len(r['boxes'])
            rows.append({'run': name, 'photo_id': r['photo_id'], 'n': n})
    df = pd.DataFrame(rows).join(meta[['count', 'provisional_group', 'negative_kind']], on='photo_id')
    res = df.groupby(['run', 'count']).agg(
        photos=('n', 'size'),
        errors=('n', lambda s: s.isna().sum()),
        mean_boxes=('n', 'mean'),
        zero_boxes=('n', lambda s: (s == 0).mean()),
        one_box=('n', lambda s: (s == 1).mean()),
        two_plus=('n', lambda s: (s >= 2).mean()),
    ).reset_index()
    neg = df[df['count'] == 'zero'].groupby(['run', 'negative_kind']).agg(
        photos=('n', 'size'),
        with_box=('n', lambda s: (s > 0).mean()),
        mean_boxes=('n', 'mean'),
    ).reset_index()
    text = res.to_markdown(index=False, floatfmt='.3f')
    text += '\n\nPhotos without butterflies (count = zero) by negative_kind:\n\n'
    text += neg.to_markdown(index=False, floatfmt='.3f')
    with open(args.out, 'w') as f:
        f.write(text + '\n')
    print(text)


if __name__ == '__main__':
    main()
